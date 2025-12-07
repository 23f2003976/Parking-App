from flask import Blueprint, request, jsonify
from tasks import export_user_csv
from utils.auth import token_required
from models import ParkingLot, ParkingSpot, ParkingSession, ExportJob
from extensions import db, cache
from datetime import datetime
from sqlalchemy import func, desc

user_bp = Blueprint('user', __name__)


@user_bp.route('/lots', methods=['GET'])
@token_required
def list_available_lots():
    lots = ParkingLot.query.all()
    result = []
    for lot in lots:
        occupied = ParkingSpot.query.filter_by(lot_id=lot.id, is_occupied=True).count()
        if occupied < lot.capacity:
            result.append({
                'id': lot.id,
                'name': lot.name,
                'location': lot.location,
                'rate': lot.rate_per_hour,
                'available_spots': lot.capacity - occupied
            })
    return jsonify(result)

@user_bp.route('/park', methods=['POST'])
@token_required
def park_vehicle():
    user = request.current_user
    data = request.get_json() or {}
    lot_id = data.get('lot_id')
    vehicle_number = data.get('vehicle_number')
    
    if not lot_id or not vehicle_number:
        return jsonify({'error': 'Lot ID and Vehicle Number required'}), 400
        
    active_session = ParkingSession.query.filter_by(user_id=user.id, status='ACTIVE').first()
    if active_session:
        return jsonify({'error': 'You already have a vehicle parked. Please unpark first.'}), 400

    spot = ParkingSpot.query.filter_by(lot_id=lot_id, is_occupied=False).with_for_update().first()
    
    if not spot:
        return jsonify({'error': 'Parking Lot is full'}), 400
        
    try:
        session = ParkingSession(
            user_id=user.id,
            lot_id=lot_id,
            spot_id=spot.id,
            vehicle_number=vehicle_number,
            entry_time=datetime.utcnow(),
            status='ACTIVE'
        )
        db.session.add(session)
        db.session.flush() 
        
        spot.is_occupied = True
        spot.current_session_id = session.id
        
        db.session.commit()
        return jsonify({
            'message': 'Parking successful',
            'session_id': session.id,
            'spot_number': spot.spot_number,
            'vehicle': vehicle_number
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/unpark', methods=['POST'])
@token_required
def unpark_vehicle():
    user = request.current_user
    session = ParkingSession.query.filter_by(user_id=user.id, status='ACTIVE').first()
    if not session:
        return jsonify({'error': 'No active parking session found'}), 404
        
    spot = ParkingSpot.query.get(session.spot_id)
    lot = ParkingLot.query.get(session.lot_id)
    
    now = datetime.utcnow()
    duration_hours = (now - session.entry_time).total_seconds() / 3600
    chargeable_hours = max(1, round(duration_hours, 2))
    amount = round(chargeable_hours * lot.rate_per_hour, 2)
    
    session.exit_time = now
    session.amount_paid = amount
    session.status = 'COMPLETED'
    
    spot.is_occupied = False
    spot.current_session_id = None
    
    db.session.commit()
    
    return jsonify({
        'message': 'Vehicle unparked successfully',
        'duration_hours': round(duration_hours, 2),
        'amount_paid': amount,
        'spot_released': spot.spot_number
    })

@user_bp.route('/history', methods=['GET'])
@token_required
def parking_history():
    user = request.current_user
    sessions = ParkingSession.query.filter_by(user_id=user.id).order_by(ParkingSession.entry_time.desc()).all()
    
    result = [{
        'id': s.id,
        'lot_name': s.lot.name,
        'spot': s.spot.spot_number,
        'vehicle': s.vehicle_number,
        'entry': s.entry_time.isoformat() + 'Z', 
        'exit': (s.exit_time.isoformat() + 'Z') if s.exit_time else 'Active',
        'amount': s.amount_paid,
        'status': s.status
    } for s in sessions]
    
    return jsonify(result)

# ----------------- REVISED SEARCH WITH LOWER() -----------------
@user_bp.route('/search', methods=['GET'])
@token_required
def search_user_data():
    user = request.current_user
    query_string = request.args.get('q', '').strip().lower()
    
    if not query_string:
        return jsonify({'lots': [], 'history': []})
        
    search_term = f'%{query_string}%'

    found_lots = ParkingLot.query.filter(
        (func.lower(ParkingLot.name).like(search_term)) | 
        (func.lower(ParkingLot.location).like(search_term))
    ).all()
    
    lots_result = []
    for lot in found_lots:
        occupied = ParkingSpot.query.filter_by(lot_id=lot.id, is_occupied=True).count()
        lots_result.append({
            'id': lot.id,
            'name': lot.name,
            'location': lot.location,
            'rate': lot.rate_per_hour,
            'available_spots': lot.capacity - occupied
        })

    found_history = ParkingSession.query.join(ParkingLot).filter(
        ParkingSession.user_id == user.id,
        (func.lower(ParkingLot.name).like(search_term)) | 
        (func.lower(ParkingSession.vehicle_number).like(search_term))
    ).order_by(ParkingSession.entry_time.desc()).all()
    
    history_result = [{
        'id': s.id,
        'lot_name': s.lot.name,
        'entry_time': s.entry_time.strftime('%Y-%m-%d %H:%M'),
        'amount': s.amount_paid,
        'vehicle': s.vehicle_number
    } for s in found_history]

    return jsonify({
        'lots': lots_result,
        'history': history_result
    })

# ----------------- REVISED SUMMARY WITH NEW CHART DATA -----------------
@user_bp.route('/summary', methods=['GET'])
@token_required
def user_summary():
    user = request.current_user
    
    # Chart 1: Visits per Lot
    fav_lots = db.session.query(
        ParkingLot.name, 
        func.count(ParkingSession.id)
    ).join(ParkingSession).filter(
        ParkingSession.user_id == user.id
    ).group_by(ParkingLot.name).all()
    
    # Chart 2: Monthly Spending
    spending = db.session.query(
        func.strftime('%Y-%m', ParkingSession.entry_time).label('month'),
        func.sum(ParkingSession.amount_paid)
    ).filter(
        ParkingSession.user_id == user.id,
        ParkingSession.status == 'COMPLETED'
    ).group_by('month').all()

    # Chart 3 (NEW): Total Spend per Lot
    spend_by_lot = db.session.query(
        ParkingLot.name,
        func.sum(ParkingSession.amount_paid)
    ).join(ParkingSession).filter(
        ParkingSession.user_id == user.id,
        ParkingSession.status == 'COMPLETED'
    ).group_by(ParkingLot.name).all()
    
    return jsonify({
        'usage_by_lot': [{'lot': l, 'count': c} for l, c in fav_lots],
        'monthly_spend': [{'month': m, 'amount': round(a or 0, 2)} for m, a in spending],
        'spend_by_lot': [{'lot': l, 'amount': round(a or 0, 2)} for l, a in spend_by_lot]
    })

@user_bp.route('/export/trigger', methods=['POST'])
@token_required
def trigger_export():
    user = request.current_user
    task = export_user_csv.delay(user.id)
    new_job = ExportJob(user_id=user.id, celery_task_id=task.id, status='STARTED')
    db.session.add(new_job)
    db.session.commit()
    return jsonify({'job_id': new_job.id})

@user_bp.route('/export/status/<int:job_id>', methods=['GET'])
@token_required
def check_export_status(job_id):
    user = request.current_user
    job = ExportJob.query.filter_by(id=job_id, user_id=user.id).first_or_404()
    return jsonify({'status': job.status, 'file_link': job.file_path if job.status == 'SUCCESS' else None})