import os
import re
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
import logging
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityService:
    def __init__(self):
        self.secret_key = os.getenv('SECRET_KEY')
        self.session_timeout = int(os.getenv('SESSION_TIMEOUT', 3600))
        self.max_login_attempts = int(os.getenv('MAX_LOGIN_ATTEMPTS', 5))
        self.lockout_duration = int(os.getenv('LOCKOUT_DURATION', 900))
        self.password_hash_algorithm = os.getenv('PASSWORD_HASH_ALGORITHM', 'bcrypt')

    def validate_email(self, email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def sanitize_input(self, data: Any) -> Any:
        """Sanitize user input to prevent XSS and SQL injection."""
        if isinstance(data, str):
            # Remove potentially dangerous characters
            data = re.sub(r'[<>"\']', '', data)
        elif isinstance(data, dict):
            return {k: self.sanitize_input(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.sanitize_input(item) for item in data]
        return data

    def hash_password(self, password: str) -> str:
        """Hash password using configured algorithm."""
        return generate_password_hash(password, method=self.password_hash_algorithm)

    def verify_password(self, password_hash: str, password: str) -> bool:
        """Verify password against hash."""
        return check_password_hash(password_hash, password)

    def generate_token(self, user_id: int, role: str) -> str:
        """Generate JWT token for user."""
        payload = {
            'user_id': user_id,
            'role': role,
            'exp': datetime.utcnow() + timedelta(seconds=self.session_timeout)
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')

    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token and return payload if valid."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None

    def require_auth(self, f):
        """Decorator for requiring authentication."""
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({'message': 'Missing token'}), 401
            
            try:
                token = token.split(' ')[1]  # Remove 'Bearer ' prefix
                payload = self.verify_token(token)
                if not payload:
                    return jsonify({'message': 'Invalid token'}), 401
                
                # Add user info to request context
                request.user_id = payload['user_id']
                request.user_role = payload['role']
            except Exception as e:
                logger.error(f"Authentication error: {str(e)}")
                return jsonify({'message': 'Authentication failed'}), 401
            
            return f(*args, **kwargs)
        return decorated

    def require_role(self, roles: list):
        """Decorator for requiring specific role."""
        def decorator(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                if not hasattr(request, 'user_role') or request.user_role not in roles:
                    return jsonify({'message': 'Insufficient permissions'}), 403
                return f(*args, **kwargs)
            return decorated
        return decorator

    def track_login_attempt(self, email: str, success: bool) -> bool:
        """Track login attempts and implement lockout if needed."""
        # Implement login attempt tracking logic
        # Return True if login is allowed, False if locked out
        return True

    def validate_password_strength(self, password: str) -> tuple[bool, str]:
        """Validate password strength."""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        if not re.search(r'[0-9]', password):
            return False, "Password must contain at least one number"
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
        return True, "Password is strong" 