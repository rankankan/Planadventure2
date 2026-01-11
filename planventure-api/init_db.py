#!/usr/bin/env python
"""
Database initialization script
Run this script to create all database tables
"""

import os
import sys
from app import app, db
from models import User

def init_db():
    """Initialize the database by creating all tables"""
    with app.app_context():
        try:
            # Drop existing tables (optional - uncomment if you want fresh start)
            db.drop_all()
            
            # Create all tables
            db.create_all()
            print("✓ Database tables created successfully!")
            print("✓ Created tables: users")
            return True
        except Exception as e:
            print(f"✗ Error initializing database: {e}", file=sys.stderr)
            return False

if __name__ == '__main__':
    success = init_db()
    sys.exit(0 if success else 1)
