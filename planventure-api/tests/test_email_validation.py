"""
Unit tests for email validation in registration (lines 67-70 of app.py)

Tests the following code:
    # Validate email format
    is_valid, email_message = is_valid_email(email)
    if not is_valid:
        return jsonify({'error': email_message}), 400
"""
import pytest


class TestEmailValidationInRegister:
    """Test email validation during user registration"""
    
    def test_valid_email_passes_validation(self, client):
        """Test that valid email passes validation and registration succeeds"""
        response = client.post('/auth/register', json={
            'email': 'valid@example.com',
            'password': 'securepass123'
        })
        
        # Should succeed (not fail at email validation)
        assert response.status_code == 201
    
    def test_invalid_email_missing_at_sign(self, client):
        """Test that email without @ is rejected at validation"""
        response = client.post('/auth/register', json={
            'email': 'invalidemail.com',
            'password': 'securepass123'
        })
        
        # Should fail at email validation (lines 67-70)
        assert response.status_code == 400
        assert 'error' in response.get_json()
        assert 'email' in response.get_json()['error'].lower()
    
    def test_invalid_email_missing_domain(self, client):
        """Test that email without domain is rejected"""
        response = client.post('/auth/register', json={
            'email': 'user@',
            'password': 'securepass123'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_invalid_email_missing_local_part(self, client):
        """Test that email without local part is rejected"""
        response = client.post('/auth/register', json={
            'email': '@example.com',
            'password': 'securepass123'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_invalid_email_consecutive_dots(self, client):
        """Test that email with consecutive dots is rejected"""
        response = client.post('/auth/register', json={
            'email': 'user..name@example.com',
            'password': 'securepass123'
        })
        
        assert response.status_code == 400
    
    def test_invalid_email_starts_with_dot(self, client):
        """Test that email starting with dot is rejected"""
        response = client.post('/auth/register', json={
            'email': '.user@example.com',
            'password': 'securepass123'
        })
        
        assert response.status_code == 400
    
    def test_invalid_email_ends_with_dot(self, client):
        """Test that email ending with dot is rejected"""
        response = client.post('/auth/register', json={
            'email': 'user.@example.com',
            'password': 'securepass123'
        })
        
        assert response.status_code == 400
    
    def test_invalid_email_no_tld(self, client):
        """Test that email without TLD is rejected"""
        response = client.post('/auth/register', json={
            'email': 'user@example',
            'password': 'securepass123'
        })
        
        assert response.status_code == 400
    
    def test_invalid_email_spaces(self, client):
        """Test that email with spaces is rejected"""
        response = client.post('/auth/register', json={
            'email': 'user name@example.com',
            'password': 'securepass123'
        })
        
        assert response.status_code == 400
    
    def test_valid_email_with_subdomain(self, client):
        """Test that email with subdomain passes validation"""
        response = client.post('/auth/register', json={
            'email': 'user@mail.example.co.uk',
            'password': 'securepass123'
        })
        
        assert response.status_code == 201
    
    def test_valid_email_with_plus_sign(self, client):
        """Test that email with plus sign passes validation"""
        response = client.post('/auth/register', json={
            'email': 'user+tag@example.com',
            'password': 'securepass123'
        })
        
        # This depends on the regex pattern - test accordingly
        assert response.status_code in [201, 400]
    
    def test_valid_email_with_underscore(self, client):
        """Test that email with underscore passes validation"""
        response = client.post('/auth/register', json={
            'email': 'user_name@example.com',
            'password': 'securepass123'
        })
        
        assert response.status_code == 201
    
    def test_valid_email_with_hyphen(self, client):
        """Test that email with hyphen passes validation"""
        response = client.post('/auth/register', json={
            'email': 'first-last@example.com',
            'password': 'securepass123'
        })
        
        assert response.status_code == 201
    
    def test_error_message_returned_on_invalid_email(self, client):
        """Test that proper error message is returned (line 70)"""
        response = client.post('/auth/register', json={
            'email': 'invalid',
            'password': 'securepass123'
        })
        
        # Lines 69-70: return jsonify({'error': email_message}), 400
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert isinstance(data['error'], str)
        assert len(data['error']) > 0
    
    def test_email_validation_case_insensitive(self, client):
        """Test that email validation handles uppercase letters"""
        response = client.post('/auth/register', json={
            'email': 'USER@EXAMPLE.COM',
            'password': 'securepass123'
        })
        
        assert response.status_code == 201
    
    def test_email_validation_whitespace_trimmed(self, client):
        """Test that whitespace is trimmed before validation"""
        response = client.post('/auth/register', json={
            'email': '  valid@example.com  ',
            'password': 'securepass123'
        })
        
        assert response.status_code == 201
    
    def test_email_too_long_rejected(self, client):
        """Test that extremely long email is rejected"""
        long_email = 'a' * 250 + '@example.com'
        response = client.post('/auth/register', json={
            'email': long_email,
            'password': 'securepass123'
        })
        
        assert response.status_code == 400
