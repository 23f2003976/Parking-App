from celery import current_app as celery 
from models import User, ParkingSession, ParkingLot, ExportJob
from extensions import mail, db 
from flask_mail import Message
from datetime import datetime, timedelta
import csv, io, os
from flask import current_app 
from pathlib import Path
from sqlalchemy import not_, func

def send_flask_mail(to_email, subject, body, is_html=False, attachment=None, filename=None):
    import socket
    original_getaddrinfo = socket.getaddrinfo
    def ipv4_getaddrinfo(*args):
        results = original_getaddrinfo(*args)
        return [r for r in results if r[0] == socket.AF_INET]
    socket.getaddrinfo = ipv4_getaddrinfo
    try:
        with current_app.app_context(): 
            msg = Message(subject, recipients=[to_email])
            if is_html:
                msg.html = body
                msg.body = "View in HTML"
            else:
                msg.body = body
            if attachment and filename:
                msg.attach(filename, 'text/csv', attachment.encode('utf-8'))
            try:
                mail.send(msg)
                return True
            except Exception as e:
                print(f"Error: {e}")
                return False
    finally:
        socket.getaddrinfo = original_getaddrinfo

@celery.task
def schedule_monthly_reports():
    users = User.query.filter(User.email != None).all() 
    for user in users:
        generate_monthly_report.delay(user.id)
    return f"Dispatched {len(users)} reports."

@celery.task
def send_daily_reminders():
    cutoff_date = datetime.utcnow() - timedelta(days=1)
    
    recent_parking = db.session.query(ParkingSession).filter(
        ParkingSession.entry_time >= cutoff_date,
        ParkingSession.user_id == User.id
    ).exists()

    users_to_remind = User.query.filter(
        User.role != 'admin',
        not_(recent_parking),
        User.email != None 
    ).all()

    new_lots = ParkingLot.query.filter(
        ParkingLot.created_at >= datetime.utcnow().date()
    ).count()

    for u in users_to_remind:
        subject = "Need a Parking Spot? 🚗"
        if new_lots > 0:
            msg = f"Hello {u.username},\n\nWe noticed you haven't parked with us lately. We have {new_lots} new parking locations available!\nYou can check it out in our app's dashboard!"
        else:
            msg = f"Hello {u.username},\n\nSafe and secure parking is waiting for you. Book a spot today!"
        
        send_flask_mail(u.email, subject, msg)
        
    print(f"Reminders sent to {len(users_to_remind)} users.")

@celery.task
def generate_monthly_report(user_id):
    user = User.query.get(user_id)
    if not user or user.role == 'admin': return

    now = datetime.utcnow()
    first_day_curr = now.replace(day=1, hour=0, minute=0, second=0)
    first_day_prev = (first_day_curr - timedelta(days=1)).replace(day=1)

    sessions = ParkingSession.query.filter(
        ParkingSession.user_id == user.id,
        ParkingSession.entry_time >= first_day_prev,
        ParkingSession.entry_time < first_day_curr
    ).all()

    total_sessions = len(sessions)
    if total_sessions == 0: return

    total_spent = sum([s.amount_paid for s in sessions])
    most_used_lot_data = db.session.query(ParkingLot.name, func.count(ParkingLot.id))\
        .join(ParkingSession).filter(ParkingSession.id.in_([s.id for s in sessions]))\
        .group_by(ParkingLot.name).order_by(func.count(ParkingLot.id).desc()).first()
    
    most_used_lot = most_used_lot_data[0] if most_used_lot_data else "N/A"
    
    html_rows = ""
    for s in sessions:
        html_rows += f"""<tr>
            <td>{s.lot.name}</td>
            <td>{s.spot.spot_number}</td>
            <td>{s.entry_time.strftime('%d-%m %H:%M')}</td>
            <td>${s.amount_paid}</td>
        </tr>"""

    html_content = f"""
    <html><body>
        <h1>Monthly Parking Report: {first_day_prev.strftime('%B %Y')}</h1>
        <p><strong>Total Parkings:</strong> {total_sessions}</p>
        <p><strong>Total Spent:</strong> ${round(total_spent, 2)}</p>
        <p><strong>Favorite Lot:</strong> {most_used_lot}</p>
        <table border="1">
            <thead><tr><th>Lot</th><th>Spot</th><th>Date</th><th>Fee</th></tr></thead>
            <tbody>{html_rows}</tbody>
        </table>
    </body></html>
    """
    send_flask_mail(user.email, "Monthly Parking Report", html_content, is_html=True)

@celery.task(bind=True) 
def export_user_csv(self, user_id):
    job = ExportJob.query.filter_by(celery_task_id=self.request.id).first()
    user = User.query.get(user_id)
    
    if not user:
        if job: job.status = 'FAILURE'; db.session.commit()
        return

    try:
        sessions = ParkingSession.query.filter_by(user_id=user_id).order_by(ParkingSession.entry_time.desc()).all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Session ID', 'Lot Name', 'Spot Number', 'Vehicle', 'Entry Time', 'Exit Time', 'Fee', 'Status'])
        
        for s in sessions:
            writer.writerow([
                s.id, s.lot.name, s.spot.spot_number, s.vehicle_number,
                s.entry_time, s.exit_time, s.amount_paid, s.status
            ])
            
        csv_data = output.getvalue()
        
        store_path = Path(current_app.config.get('FILE_STORAGE_PATH')).expanduser()
        os.makedirs(store_path, exist_ok=True)
        filename = f"parking_history_{user.username}_{datetime.now().strftime('%Y%m%d')}.csv"
        file_path = os.path.join(store_path, filename)
        
        with open(file_path, 'w') as f: f.write(csv_data)
        
        job.status = 'SUCCESS'
        job.file_path = file_path
        job.completed_at = datetime.utcnow()
        db.session.commit()
        
        send_flask_mail(user.email, "Your Parking History CSV", "Download attached.", attachment=csv_data, filename=filename)
        
    except Exception as e:
        if job: job.status = 'FAILURE'; db.session.commit()
        print(e)