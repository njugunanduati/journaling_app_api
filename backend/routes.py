from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User, JournalEntry
from utils import hash_password, verify_password

api = Blueprint('api', __name__)

@api.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        first_name = data.get('firstName') 
        last_name = data.get('lastName')
        email = data.get('email')
        password = data.get('password')
        print('password: %s' % password)
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'User already exists'}), 400

        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email, 
            password=hash_password(password)
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        print('error: %s' % e)
        return jsonify({'error': 'f Error {e}'}), 400

@api.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        user = User.query.filter_by(email=email).first()
        if not user or not verify_password(password, user.password):
            return jsonify({'error': 'Invalid credentials'}), 401

        access_token = create_access_token(identity=user.id)
        return jsonify({'access_token': access_token}), 200
    except Exception as e:
        return jsonify({'error': f'Error: {e}'}), 400

@api.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        return jsonify({
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name
        }), 200
    except Exception as e:
        return jsonify({'error': f'Error: {e}'}), 400

# update profile
@api.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        user = User.query.get_or_404(user_id)
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        db.session.commit()
        return jsonify({'message': 'Profile updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'Error: {e}'}), 400

@api.route('/entries', methods=['POST'])
@jwt_required()
def add_entry():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        entry = JournalEntry(
            title=data.get('title'),
            content=data.get('content'),
            category=data.get('category'),
            user_id=user_id
        )
        db.session.add(entry)
        db.session.commit()
        return jsonify({'message': 'Entry added successfully'}), 201
    except Exception as e:
        return jsonify({'error': f'Error: {e}'}), 400

@api.route('/entries', methods=['GET'])
@jwt_required()
def get_entries():
    user_id = get_jwt_identity()
    entries = JournalEntry.query.filter_by(user_id=user_id).all()
    return jsonify([{
        'id': entry.id,
        'title': entry.title,
        'content': entry.content,
        'category': entry.category,
        'date': entry.date
    } for entry in entries]), 200

# update the user entry
@api.route('/entries/update/<int:entry_id>', methods=['PUT'])
@jwt_required()
def update_entry(entry_id):
    user_id = get_jwt_identity()
    entry = JournalEntry.query.get_or_404(entry_id)
    if entry.user_id == user_id:
        data = request.get_json()
        entry.title = data.get('title', entry.title)
        entry.content = data.get('content', entry.content)
        entry.category = data.get('category', entry.category)
        db.session.commit()
        return jsonify({'message': 'Entry updated successfully'}), 200
    else:
        return jsonify({'error': 'Unauthorized'}), 401

# delete the user entry
@api.route('/entries/delete/<int:entry_id>', methods=['DELETE'])
@jwt_required()
def delete_entry(entry_id):
    user_id = get_jwt_identity()
    entry = JournalEntry.query.get_or_404(entry_id)
    if entry.user_id == user_id:
        db.session.delete(entry)
        db.session.commit()
        return jsonify({'message': 'Entry deleted successfully'}), 200
    else:
        return jsonify({'error': 'Unauthorized'}), 401