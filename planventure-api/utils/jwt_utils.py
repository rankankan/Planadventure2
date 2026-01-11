"""
JWT token generation and validation utilities
"""
from datetime import timedelta, datetime, timezone
from typing import Dict, Optional, Any
from flask_jwt_extended import create_access_token, create_refresh_token
from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt


def generate_tokens(identity: Any, expires_in_hours: int = 24, refresh_expires_in_days: int = 30) -> Dict[str, str]:
    """
    Generate both access and refresh JWT tokens.
    
    Args:
        identity: User identifier (typically user ID or email) to encode in token
        expires_in_hours: Access token expiration time in hours (default 24)
        refresh_expires_in_days: Refresh token expiration time in days (default 30)
        
    Returns:
        Dictionary with 'access_token' and 'refresh_token' keys
        
    Example:
        tokens = generate_tokens(user.id)
        return jsonify(tokens)
    """
    access_token_expires = timedelta(hours=expires_in_hours)
    refresh_token_expires = timedelta(days=refresh_expires_in_days)
    
    access_token = create_access_token(
        identity=identity,
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        identity=identity,
        expires_delta=refresh_token_expires
    )
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer'
    }


def get_current_user_id() -> Any:
    """
    Get the current authenticated user's identity from JWT token.
    
    Returns:
        User identity from token (typically user ID)
        
    Raises:
        Exception: If no valid JWT is provided (401 Unauthorized)
        
    Note:
        Call this only inside a route protected by @jwt_required()
        
    Example:
        @app.route('/profile')
        @jwt_required()
        def get_profile():
            user_id = get_current_user_id()
            user = User.query.get(user_id)
            return jsonify(user.to_dict())
    """
    return get_jwt_identity()


def get_jwt_claims() -> Dict:
    """
    Get all claims from the current JWT token.
    
    Returns:
        Dictionary of JWT claims (includes 'sub' for identity, 'iat', 'exp', etc.)
        
    Note:
        Call this only inside a route protected by @jwt_required()
    """
    return get_jwt()


def token_required(f):
    """
    Decorator to require JWT token for a route.
    Returns 401 if no valid token or 403 if token is invalid.
    
    Usage:
        @app.route('/protected')
        @token_required
        def protected_route():
            user_id = get_current_user_id()
            return jsonify({'user_id': user_id})
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception as e:
            return jsonify({'error': 'Invalid or missing token', 'message': str(e)}), 401
        return f(*args, **kwargs)
    return decorated


def optional_token_required(f):
    """
    Decorator to optionally require JWT token for a route.
    Token is validated if provided, but route works without it.
    
    Usage:
        @app.route('/public')
        @optional_token_required
        def public_route():
            user_id = get_current_user_id()  # Returns None if no token
            return jsonify({'user_id': user_id})
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request(optional=True)
        except Exception as e:
            return jsonify({'error': 'Invalid token', 'message': str(e)}), 401
        return f(*args, **kwargs)
    return decorated
