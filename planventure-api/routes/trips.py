"""
Trip routes blueprint with CRUD operations
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity
from app import db
from models import Trip, User
from middleware.auth import token_required
from datetime import datetime

# Create blueprint
trips_bp = Blueprint('trips', __name__, url_prefix='/trips')


@trips_bp.route('', methods=['GET'])
@token_required
def get_trips():
    """Get all trips for the current user"""
    user_id = get_jwt_identity()
    
    try:
        # Fetch all trips for the user
        trips = Trip.query.filter_by(user_id=user_id).all()
        
        return jsonify({
            'message': 'Trips retrieved successfully',
            'count': len(trips),
            'trips': [trip.to_dict() for trip in trips]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve trips', 'message': str(e)}), 500


@trips_bp.route('/<int:trip_id>', methods=['GET'])
@token_required
def get_trip(trip_id):
    """Get a specific trip by ID"""
    user_id = get_jwt_identity()
    
    try:
        trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
        
        if not trip:
            return jsonify({'error': 'Trip not found'}), 404
        
        return jsonify({
            'message': 'Trip retrieved successfully',
            'trip': trip.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve trip', 'message': str(e)}), 500


@trips_bp.route('', methods=['POST'])
@token_required
def create_trip():
    """Create a new trip for the current user"""
    user_id = get_jwt_identity()
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['destination', 'start_date', 'end_date']
        if not data or not all(field in data for field in required_fields):
            return jsonify({
                'error': 'Missing required fields',
                'required': required_fields
            }), 400
        
        destination = data.get('destination', '').strip()
        if not destination:
            return jsonify({'error': 'Destination cannot be empty'}), 400
        
        # Parse dates
        try:
            start_date = datetime.fromisoformat(data.get('start_date'))
            end_date = datetime.fromisoformat(data.get('end_date'))
        except (ValueError, TypeError):
            return jsonify({
                'error': 'Invalid date format. Use ISO 8601 (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)'
            }), 400
        
        # Validate dates
        if start_date >= end_date:
            return jsonify({'error': 'Start date must be before end date'}), 400
        
        # Create new trip
        new_trip = Trip()
        new_trip.user_id = user_id
        new_trip.destination = destination
        new_trip.start_date = start_date
        new_trip.end_date = end_date
        new_trip.latitude = data.get('latitude')
        new_trip.longitude = data.get('longitude')
        new_trip.itinerary = data.get('itinerary')
        
        db.session.add(new_trip)
        db.session.commit()
        
        return jsonify({
            'message': 'Trip created successfully',
            'trip': new_trip.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create trip', 'message': str(e)}), 500


@trips_bp.route('/<int:trip_id>', methods=['PUT'])
@token_required
def update_trip(trip_id):
    """Update an existing trip"""
    user_id = get_jwt_identity()
    
    try:
        # Verify trip belongs to current user
        trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
        
        if not trip:
            return jsonify({'error': 'Trip not found'}), 404
        
        data = request.get_json()
        
        # Update destination
        if 'destination' in data:
            destination = data.get('destination', '').strip()
            if not destination:
                return jsonify({'error': 'Destination cannot be empty'}), 400
            trip.destination = destination
        
        # Update dates
        if 'start_date' in data or 'end_date' in data:
            try:
                start_date = datetime.fromisoformat(data.get('start_date', trip.start_date.isoformat()))
                end_date = datetime.fromisoformat(data.get('end_date', trip.end_date.isoformat()))
                
                if start_date >= end_date:
                    return jsonify({'error': 'Start date must be before end date'}), 400
                
                trip.start_date = start_date
                trip.end_date = end_date
            except (ValueError, TypeError):
                return jsonify({
                    'error': 'Invalid date format. Use ISO 8601 (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)'
                }), 400
        
        # Update coordinates
        if 'latitude' in data:
            trip.latitude = data.get('latitude')
        if 'longitude' in data:
            trip.longitude = data.get('longitude')
        
        # Update itinerary
        if 'itinerary' in data:
            trip.itinerary = data.get('itinerary')
        
        db.session.commit()
        
        return jsonify({
            'message': 'Trip updated successfully',
            'trip': trip.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update trip', 'message': str(e)}), 500


@trips_bp.route('/<int:trip_id>', methods=['DELETE'])
@token_required
def delete_trip(trip_id):
    """Delete a trip"""
    user_id = get_jwt_identity()
    
    try:
        # Verify trip belongs to current user
        trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
        
        if not trip:
            return jsonify({'error': 'Trip not found'}), 404
        
        db.session.delete(trip)
        db.session.commit()
        
        return jsonify({
            'message': 'Trip deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete trip', 'message': str(e)}), 500
