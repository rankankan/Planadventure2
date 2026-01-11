"""
Email validation utilities
"""
import re
from typing import Tuple


def is_valid_email(email: str) -> Tuple[bool, str]:
    """
    Validate email format using regex pattern.
    
    Args:
        email: Email address to validate
        
    Returns:
        Tuple of (is_valid: bool, message: str)
        - (True, 'Valid') if email format is correct
        - (False, error_message) if email format is invalid
        
    Validates:
        - Email is not empty
        - Proper format: local@domain.extension
        - Local part: alphanumeric, dots, hyphens, underscores
        - Domain: alphanumeric, hyphens, dots
        - TLD: at least 2 characters (com, org, co.uk, etc.)
    """
    if not email or not isinstance(email, str):
        return False, "Email must be a non-empty string"
    
    email = email.strip().lower()
    
    if len(email) > 254:
        return False, "Email must be less than 254 characters"
    
    # RFC 5322 simplified regex pattern for email validation
    pattern = r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return False, "Invalid email format (use: user@example.com)"
    
    # Additional checks
    if email.startswith('.') or email.endswith('.'):
        return False, "Email cannot start or end with a dot"
    
    if '..' in email:
        return False, "Email cannot contain consecutive dots"
    
    local_part = email.split('@')[0]
    domain_part = email.split('@')[1]
    
    if len(local_part) > 64:
        return False, "Email local part must be less than 64 characters"
    
    if domain_part.startswith('-') or domain_part.endswith('-'):
        return False, "Domain cannot start or end with a hyphen"
    
    return True, "Valid"
