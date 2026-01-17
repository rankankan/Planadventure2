"""
Tests for utility functions (email_validator, password, jwt_utils)
"""
import pytest
from utils.email_validator import is_valid_email
from utils.password import hash_password, verify_password, generate_salt
from utils.jwt_utils import generate_tokens, decode_token
from app import create_app



@pytest.fixture
def app_context():
    """Create application context for testing"""
    app = create_app()
    with app.app_context():
        yield


class TestEmailValidator:
    """Test email validation functionality"""
    
    def test_valid_email(self):
        """Test that valid emails pass validation"""
        valid_emails = [
            'user@example.com',
            'test.user@example.co.uk',
            'john_doe@company.org',
            'first-last@domain.info'
        ]
        for email in valid_emails:
            is_valid, message = is_valid_email(email)
            assert is_valid, f"Email {email} should be valid, but got: {message}"
    
    def test_invalid_email_format(self):
        """Test that invalid email formats are rejected"""
        invalid_emails = [
            'user@',
            '@example.com',
            'user..name@example.com',
            'user@.com',
            'user name@example.com',
            'user@example',
            'user@example.',
            '.user@example.com',
            'user.@example.com'
        ]
        for email in invalid_emails:
            is_valid, message = is_valid_email(email)
            assert not is_valid, f"Email {email} should be invalid"
    
    @pytest.mark.parametrize("email", ['', None])
    def test_empty_or_null_email(self, email):
        """Test that empty or None email is rejected"""
        is_valid, message = is_valid_email(email)  # type: ignore
        assert not is_valid
    
    def test_email_too_long(self):
        """Test that email exceeding max length is rejected"""
        long_email = 'a' * 250 + '@example.com'
        is_valid, message = is_valid_email(long_email)
        assert not is_valid
    
    def test_consecutive_dots(self):
        """Test that consecutive dots in email are rejected"""
        is_valid, message = is_valid_email('user..name@example.com')
        assert not is_valid
    
    def test_case_insensitive(self):
        """Test that email validation is case insensitive"""
        is_valid, _ = is_valid_email('User@Example.COM')
        assert is_valid


class TestPasswordUtils:
    """Test password hashing and verification functionality"""
    
    def test_hash_password(self):
        """Test that password is properly hashed"""
        password = 'testpassword123'
        hashed = hash_password(password)
        
        # Hash should be a string
        assert isinstance(hashed, str)
        # Hash should not equal original password
        assert hashed != password
        # Hash should be long (bcrypt hashes are ~60 chars       )
        assert len(hashed) > 50
    
    def test_verify_correct_password(self):
        """Test that correct password verifies successfully"""
        password = 'correctpassword'
        hashed = hash_password(password)
        
        assert verify_password(password, hashed)
    
    def test_verify_incorrect_password(self):
        """Test that incorrect password fails verification"""
        password = 'correctpassword'
        wrong_password = 'wrongpassword'
        hashed = hash_password(password)
        
        assert not verify_password(wrong_password, hashed)
    
    def test_different_hashes_same_password(self):
        """Test that same password produces different hashes"""
        password = 'test&password$'
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        # Hashes should be different (bcrypt uses random salt)
        assert hash1 != hash2
        # Both should verify correctly
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)
    
    @pytest.mark.parametrize("invalid_input", ['', None])
    def test_hash_invalid_password_raises_error(self, invalid_input):
        """Test that empty or None password raises ValueError"""
        with pytest.raises(ValueError):
            hash_password(invalid_input)  # type: ignore
    
    def test_generate_salt(self):
        """Test salt generation"""
        salt = generate_salt()
        assert isinstance(salt, bytes)
        
        # Salt should be different each time
        salt2 = generate_salt()
        assert salt != salt2
    
    def test_hash_with_custom_rounds(self):
        """Test hashing with custom salt rounds"""
        password = 'testpass2'
        salt = generate_salt(rounds=10)
        hashed = hash_password(password, salt)
        
        assert verify_password(password, hashed)


class TestJWTUtils:
    """Test JWT token generation and decoding functionality"""
    
    def test_generate_tokens(self, app_context):
        """Test JWT token generation"""
        user_id = 1
        tokens = generate_tokens(user_id)
        
        assert 'access_token' in tokens
        assert 'refresh_token' in tokens
        assert isinstance(tokens['access_token'], str)
        assert isinstance(tokens['refresh_token'], str)
    
    @pytest.mark.parametrize("user_id", [1, 42, 100, 9999])
    def test_decode_valid_token(self, app_context, user_id):
        """Test decoding a valid JWT token contains correct user ID"""
        tokens = generate_tokens(user_id)
        
        decoded = decode_token(tokens['access_token'])
        assert decoded['sub'] == user_id
    
    def test_decode_invalid_token(self, app_context):
        """Test that invalid token raises exception"""
        with pytest.raises(Exception):
            decode_token('invalid.token.here')
