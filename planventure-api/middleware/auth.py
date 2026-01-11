"""
Authentication middleware for protecting routes and handling JWT validation
"""
from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import (
    verify_jwt_in_request, 
    get_jwt_identity, 
    get_jwt
)


def token_required(fn):
    """
    Decorator to require JWT token for a route.
    Returns 401 if no valid token is provided.
    
    Usage:
        @app.route('/protected')
        @token_required
        def protected_route():
            user_id = get_jwt_identity()
            return jsonify({'user_id': user_id})
    """
    @wraps(fn)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception as e:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Invalid or missing token'
            }), 401
        return fn(*args, **kwargs)
    return decorated_function


def optional_token_required(fn):
    """
    Decorator to optionally require JWT token for a route.
    Token is validated if provided, but route works without it.
    Use get_jwt_identity() to check if user is authenticated (returns None if not).
    
    Usage:
        @app.route('/public')
        @optional_token_required
        def public_route():
            user_id = get_jwt_identity()
            if user_id:
                return jsonify({'message': f'Hello user {user_id}'})
            return jsonify({'message': 'Hello anonymous'})
    """
    @wraps(fn)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request(optional=True)
        except Exception as e:
            return jsonify({
                'error': 'Invalid token',
                'message': str(e)
            }), 401
        return fn(*args, **kwargs)
    return decorated_function


def admin_required(fn):
    """
    Decorator to require JWT token with admin role.
    Use after adding 'roles' claim to JWT tokens.
    
    Usage:
        @app.route('/admin')
        @admin_required
        def admin_route():
            user_id = get_jwt_identity()
            return jsonify({'message': f'Admin access granted to user {user_id}'})
    """
    @wraps(fn)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            claims = get_jwt()
            if 'roles' not in claims or 'admin' not in claims['roles']:
                return jsonify({
                    'error': 'Forbidden',
                    'message': 'Admin role required'
                }), 403
        except Exception as e:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Invalid or missing token'
            }), 401
        return fn(*args, **kwargs)
    return decorated_function


def setup_jwt_error_handlers(app):
    """
    Register error handlers for JWT exceptions.
    Call this in app.py after initializing the app.
    
    Usage:
        from middleware.auth import setup_jwt_error_handlers
        
        app = Flask(__name__)
        jwt = JWTManager(app)
        setup_jwt_error_handlers(app)
    """
    
    
    @app.errorhandler(401)
    def handle_unauthorized(e):
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Missing or invalid authentication credentials'
        }), 401
    
    @app.errorhandler(403)
    def handle_forbidden(e):
        return jsonify({
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource'
        }), 403
