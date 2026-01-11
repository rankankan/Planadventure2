import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# SQLAlchemy Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'sqlite:///planventure.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_SORT_KEYS'] = False

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 86400  # 24 hours in seconds

# Initialize extensions
db = SQLAlchemy(app)
CORS(app)
jwt = JWTManager(app)

# Import models after db initialization
from models import User
from utils.jwt_utils import generate_tokens
from utils.password import hash_password, verify_password
from utils.email_validator import is_valid_email
from middleware.auth import token_required, optional_token_required, setup_jwt_error_handlers

# Setup JWT error handlers
setup_jwt_error_handlers(app)

@app.route('/')
def home():
    return jsonify({"message": "Welcome to PlanVenture API"})

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"})

# Authentication Routes
@app.route('/auth/register', methods=['POST'])
def register():
    """Register a new user with email and password"""
    try:
        data = request.get_json()
        
        # Validate input
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        email = data.get('email').strip().lower()
        password = data.get('password')
        
        # Validate email format
        is_valid, email_message = is_valid_email(email)
        if not is_valid:
            return jsonify({'error': email_message}), 400
        
        # Validate password length
        if len(password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters long'}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 409
        
        # Create new user
        new_user = User(email=email)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        # Generate tokens
        tokens = generate_tokens(new_user.id)
        
        return jsonify({
            'message': 'User registered successfully',
            'user': new_user.to_dict(),
            'tokens': tokens
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Registration failed', 'message': str(e)}), 500


@app.route('/auth/login', methods=['POST'])
def login():
    """Authenticate user and return JWT tokens"""
    try:
        data = request.get_json()
        
        # Validate input
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        email = data.get('email').strip().lower()
        password = data.get('password')
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        # Verify user exists and password is correct
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Generate tokens
        tokens = generate_tokens(user.id)
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'tokens': tokens
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Login failed', 'message': str(e)}), 500


# Protected Routes Example
@app.route('/profile', methods=['GET'])
@token_required
def get_profile():
    """Get current user profile - requires valid JWT token"""
    from flask_jwt_extended import get_jwt_identity
    
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'message': 'Profile retrieved successfully',
        'user': user.to_dict()
    }), 200


@app.route('/profile', methods=['PUT'])
@token_required
def update_profile():
    """Update current user profile - requires valid JWT token"""
    from flask_jwt_extended import get_jwt_identity
    
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    # Example: update email (with validation)
    if 'email' in data:
        new_email = data.get('email').strip().lower()
        is_valid, email_message = is_valid_email(new_email)
        if not is_valid:
            return jsonify({'error': email_message}), 400
        
        # Check if new email is already taken
        existing_user = User.query.filter_by(email=new_email).first()
        if existing_user and existing_user.id != user.id:
            return jsonify({'error': 'Email already in use'}), 409
        
        user.email = new_email
    
    db.session.commit()
    
    return jsonify({
        'message': 'Profile updated successfully',
        'user': user.to_dict()
    }), 200

if __name__ == '__main__':
    app.run(debug=True)
