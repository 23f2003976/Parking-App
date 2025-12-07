from flask import Blueprint, request, jsonify
from utils.auth import admin_required
from models import ParkingLot, ParkingSpot, User, ParkingSession
from extensions import db, cache
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

# ------------------------------------------- Parking Lot Management -------------------------------------------

@admin_bp.route('/lots', methods=['GET'])
@admin_required
def list_lots():
    lots_data = db.session.query(
        ParkingLot.id, 
        ParkingLot.name, 
        ParkingLot.location, 
        ParkingLot.capacity,
        ParkingLot.rate_per_hour,
        func.count(ParkingSpot.id).filter(ParkingSpot.is_occupied == True).label('occupied_count')
    ).outerjoin(ParkingSpot).group_by(ParkingLot.id).all()
    
    lots = [{
        'id': l.id, 
        'name': l.name, 
        'location': l.location,
        'capacity': l.capacity,
        'rate': l.rate_per_hour,
        'occupied': l.occupied_count,
        'available': l.capacity - l.occupied_count
    } for l in lots_data]
    return jsonify(lots)

@admin_bp.route('/users/<int:limit>', methods=['GET'])
@admin_required
def list_top_users(limit):
    users = (
        db.session.query(
            User,
            func.count(ParkingSession.id).label('session_count')
        )
        .outerjoin(ParkingSession)
        .filter(User.role == 'user')
        .group_by(User.id)
        .order_by(func.count(ParkingSession.id).desc())
        .limit(limit)
        .all()
    )

    result = [{
        'id': u.User.id,
        'name': u.User.username,
        'session_count': u.session_count,
        'last_visit': u.User.last_visit.strftime('%Y-%m-%d %H:%M') if u.User.last_visit else 'Never'
    } for u in users]

    return jsonify(result)

@admin_bp.route('/lots', methods=['POST'])
@admin_required
def create_lot():
    data = request.get_json() or {}
    name = data.get('name')
    capacity = int(data.get('capacity', 0))
    
    if not name or capacity <= 0:
        return jsonify({'error': 'Name and valid capacity required'}), 400
    
    lot = ParkingLot(
        name=name, 
        location=data.get('location'),
        capacity=capacity,
        rate_per_hour=data.get('rate_per_hour', 10.0)
    )
    db.session.add(lot)
    db.session.flush()
    
    for i in range(1, capacity + 1):
        spot = ParkingSpot(
            lot_id=lot.id,
            spot_number=f"SPOT-{i}",
            is_occupied=False
        )
        db.session.add(spot)
        
    db.session.commit()
    cache.delete('user_available_lots') 
    return jsonify({'message': 'Parking Lot and Spots created', 'id': lot.id}), 201

@admin_bp.route('/lots/<int:lid>', methods=['PUT'])
@admin_required
def update_lot(lid):
    lot = ParkingLot.query.get_or_404(lid)
    data = request.get_json() or {}
    
    lot.name = data.get('name', lot.name)
    lot.location = data.get('location', lot.location)
    lot.rate_per_hour = data.get('rate_per_hour', lot.rate_per_hour)
    
    db.session.commit()
    cache.delete('user_available_lots')
    return jsonify({'message': 'Lot updated'})

@admin_bp.route('/lots/<int:lid>', methods=['DELETE'])
@admin_required
def delete_lot(lid):
    lot = ParkingLot.query.get_or_404(lid)
    
    occupied_spots = ParkingSpot.query.filter_by(lot_id=lid, is_occupied=True).count()
    if occupied_spots > 0:
        return jsonify({'error': 'Cannot delete lot. Vehicles are currently parked here.'}), 400
        
    db.session.delete(lot)
    db.session.commit()
    cache.delete('user_available_lots')
    return jsonify({'message': 'Lot deleted'})

# ------------------------------------------- Spot Tracking -------------------------------------------

@admin_bp.route('/lots/<int:lid>/spots', methods=['GET'])
@admin_required
def view_lot_spots(lid):
    spots = db.session.query(
        ParkingSpot.id,
        ParkingSpot.spot_number,
        ParkingSpot.is_occupied,
        ParkingSession.vehicle_number,
        ParkingSession.entry_time,
        User.username
    ).outerjoin(ParkingSession, ParkingSpot.current_session_id == ParkingSession.id)\
     .outerjoin(User, ParkingSession.user_id == User.id)\
     .filter(ParkingSpot.lot_id == lid).all()
     
    result = [{
        'id': s.id,
        'spot_number': s.spot_number,
        'status': 'Occupied' if s.is_occupied else 'Free',
        'vehicle': s.vehicle_number if s.is_occupied else None,
        'parked_by': s.username if s.is_occupied else None,
        'since': s.entry_time.strftime('%Y-%m-%d %H:%M') if s.entry_time else None
    } for s in spots]
    
    return jsonify(result)

# ------------------------------------------- Summary ----------------------------------------------

@admin_bp.route('/summary', methods=['GET'])
@admin_required
def get_admin_summary():    
    total_users = User.query.filter_by(role='user').count()
    total_lots = ParkingLot.query.count()
    total_capacity = db.session.query(func.sum(ParkingLot.capacity)).scalar() or 0
    current_occupancy = ParkingSpot.query.filter_by(is_occupied=True).count()
    
    lot_stats = db.session.query(
        ParkingLot.name,
        func.count(ParkingSession.id).label('total_bookings'),
        func.sum(ParkingSession.amount_paid).label('total_revenue')
    ).outerjoin(ParkingSession).group_by(ParkingLot.id).all()
    
    lot_summary = [{
        'name': name,
        'bookings': bookings,
        'revenue': round(revenue or 0, 2)
    } for name, bookings, revenue in lot_stats]

    return jsonify({
        'total_users': total_users,
        'total_lots': total_lots,
        'total_capacity': total_capacity,
        'current_occupancy': current_occupancy,
        'lot_analytics': lot_summary
    })

# ------------------------------------------- Search API -------------------------------------------
@admin_bp.route('/search', methods=['GET'])
@admin_required
def admin_search():
    query_string = request.args.get('q', '').strip().lower()
    if not query_string:
        return jsonify({"message": "Search query parameter 'q' is missing."}), 400

    search_term = f'%{query_string}%'
    
    # 1. Search Users
    users = User.query.filter(
        (func.lower(User.username).like(search_term)) | 
        (func.lower(User.email).like(search_term))
    ).all()
    
    user_results = [{
        'id': user.id, 
        'username': user.username, 
        'email': user.email, 
        'role': user.role
    } for user in users]

    # 2. Search Lots (Name OR Location)
    lots = ParkingLot.query.filter(
        (func.lower(ParkingLot.name).like(search_term)) | 
        (func.lower(ParkingLot.location).like(search_term))
    ).all()
    
    lot_results = [{
        'id': lot.id, 
        'name': lot.name, 
        'location': lot.location, 
        'capacity': lot.capacity
    } for lot in lots]

    # 3. Search Spots
    spots = ParkingSpot.query.filter(func.lower(ParkingSpot.spot_number).like(search_term)).all()
    spot_results = [{
        'id': spot.id, 
        'name': spot.spot_number, 
        'lot_id': spot.lot_id,
        'is_available': not spot.is_occupied
    } for spot in spots]

    return jsonify({
        "message": "Search successful.",
        "query": query_string,
        "results": {
            "users": user_results,
            "lots": lot_results,
            "spots": spot_results
        }
    }), 200