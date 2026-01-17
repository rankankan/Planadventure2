"""
pytest configuration and shared fixtures for testing
"""
import pytest
from app import app, db
from models import User, Trip
from datetime import datetime, timezone, timedelta


@pytest.fixture
def client():
    """Create test client with temporary SQLite database"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


@pytest.fixture
def app_context():
    """Provide application context for database operations"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    
    with app.app_context():
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()


@pytest.fixture
def test_user(app_context):
    """Create a test user"""
    user = User(email='test@example.com')
    user.set_password('testpassword123')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def test_user_2(app_context):
    """Create a second test user"""
    user = User(email='test2@example.com')
    user.set_password('testpassword456')
    db.session.add(user)
    db.session.commit()
    return user





@pytest.fixture
def auth_headers(client):
    """Helper to register and login a user, returning auth headers"""
    # Register
    register_response = client.post('/auth/register', json={
        'email': 'auth_test@example.com',
        'password': 'securepass123'
    })
    assert register_response.status_code == 201
    
    tokens = register_response.get_json()['tokens']
    return {
        'Authorization': f"Bearer {tokens['access_token']}"
    }


@pytest.fixture
def auth_headers_second_user(client):
    """Helper to register and login a second user"""
    register_response = client.post('/auth/register', json={
        'email': 'auth_test2@example.com',
        'password': 'securepass456'
    })
    assert register_response.status_code == 201
    
    tokens = register_response.get_json()['tokens']
    return {
        'Authorization': f"Bearer {tokens['access_token']}"
    }
