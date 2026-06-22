from functools import wraps
from flask import request, jsonify
from app.services.auth import verify_token


def token_required(f):
    """Decorator to require JWT token for protected routes."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Check for token in headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({"error": "Invalid authorization header"}), 401

        if not token:
            return jsonify({"error": "Token is missing"}), 401

        # Verify token
        payload = verify_token(token)
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401

        # Add user info to request context
        request.user_id = payload.get('user_id')
        request.user_email = payload.get('email')

        return f(*args, **kwargs)

    return decorated
