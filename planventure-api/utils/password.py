"""
Password hashing utilities for secure password management
"""
import bcrypt
from typing import Tuple, Optional


def generate_salt(rounds: int = 12) -> bytes:
    """
    Generate a bcrypt salt for password hashing.
    
    Args:
        rounds: Cost factor for bcrypt (higher = slower, more secure). Default 12.
        
    Returns:
        bcrypt salt as bytes
    """
    return bcrypt.gensalt(rounds=rounds)


def hash_password(password: str, salt: Optional[bytes] = None) -> str:
    """
    Hash a plaintext password using bcrypt.
    
    Args:
        password: Plaintext password to hash
        salt: Optional bcrypt salt; generates new one if not provided
        
    Returns:
        Hashed password as string suitable for storage in database
        
    Raises:
        ValueError: If password is empty or None
    """
    if not password or not isinstance(password, str):
        raise ValueError("Password must be a non-empty string")
    
    if salt is None:
        salt = generate_salt()
    
    password_bytes = password.encode('utf-8')
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a plaintext password against a stored bcrypt hash.
    
    Args:
        password: Plaintext password to verify
        password_hash: Stored bcrypt hash from database
        
    Returns:
        True if password matches hash, False otherwise
        
    Raises:
        ValueError: If password or hash is empty/invalid
    """
    if not password or not isinstance(password, str):
        raise ValueError("Password must be a non-empty string")
    
    if not password_hash or not isinstance(password_hash, str):
        raise ValueError("Password hash must be a non-empty string")
    
    try:
        password_bytes = password.encode('utf-8')
        hash_bytes = password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except (ValueError, TypeError):
        # Invalid hash format
        return False
