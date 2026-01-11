from app import db
from datetime import datetime, timezone
from utils.password import hash_password, verify_password

class User(db.Model):
    """User model for storing user information"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    trips = db.relationship('Trip', back_populates='user', lazy=True, cascade='all, delete-orphan')
    """trips = db.relationship('Trip', back_populates  backref=db.backref('user', lazy=True, cascade='all, delete-orphan'))"""

    def __init__(self, email):
        self.email = email

    def __repr__(self):
        return f'<User {self.email}>'
    
    def set_password(self, password):
        """Hash and set the user's password using bcrypt"""
        self.password_hash = hash_password(password)
    
    def check_password(self, password):
        """Verify the provided password against the stored hash"""
        return verify_password(password, self.password_hash)
    
    def to_dict(self):
        """Convert user object to dictionary (excluding password)"""
        return {
            'id': self.id,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
