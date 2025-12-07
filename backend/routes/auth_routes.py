from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from models import User
from extensions import db
from utils.auth import generate_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    email = data.get('email') 
    
    if not username or not password or not email:
        return jsonify({'error': 'username, password, and email required'}), 400
        
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'User exists'}), 400
        
    user = User(
        username=username,
        password=generate_password_hash(password),
        full_name=data.get('full_name'),
        role='user',
        email=email 
    )
    db.session.add(user)
    db.session.commit()
    token = generate_token(user)
    return jsonify({'message': 'registered', 'token': token}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'username and password required'}), 400
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'error': 'invalid credentials'}), 401
    
    token = generate_token(user)
    user.last_visit = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'login successful', 'token': token, 'role': user.role}), 200