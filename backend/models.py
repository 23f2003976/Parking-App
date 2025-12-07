from datetime import datetime
from extensions import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(200))
    role = db.Column(db.String(20), default='user')
    last_visit = db.Column(db.DateTime)
    
    sessions = db.relationship('ParkingSession', backref='user', lazy=True)
    exports = db.relationship('ExportJob', backref='user', lazy=True)

class ParkingLot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    location = db.Column(db.Text)
    capacity = db.Column(db.Integer, nullable=False)
    rate_per_hour = db.Column(db.Float, default=10.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    spots = db.relationship(
        'ParkingSpot', 
        backref='lot',
        lazy=True, 
        cascade="all, delete-orphan"
    )

class ParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    spot_number = db.Column(db.String(50), nullable=False)
    is_occupied = db.Column(db.Boolean, default=False)
    
    current_session_id = db.Column(db.Integer, db.ForeignKey('parking_session.id'), nullable=True)

class ParkingSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=False)
    vehicle_number = db.Column(db.String(50), nullable=False)
    
    entry_time = db.Column(db.DateTime, default=datetime.utcnow)
    exit_time = db.Column(db.DateTime, nullable=True)
    
    amount_paid = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='ACTIVE')
    spot = db.relationship('ParkingSpot', foreign_keys=[spot_id], backref='all_sessions')
    lot = db.relationship('ParkingLot', backref='sessions')

class ExportJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    celery_task_id = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.String(20), default='PENDING', nullable=False)
    file_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)