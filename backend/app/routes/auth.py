from flask import Blueprint, jsonify, request

from app.services.store import next_id, store, utc_now_iso
from app.services.auth import hash_password, verify_password, generate_token
from app.middleware.auth import token_required

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/signup")
def signup():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    full_name = str(data.get("full_name", "")).strip()

    # Validation
    if not email or not password or not full_name:
        return jsonify({"error": "email, password, and full_name are required"}), 400

    if len(password) < 6:
        return jsonify({"error": "password must be at least 6 characters"}), 400

    # Check if user already exists
    if any(user["email"] == email for user in store["users"]):
        return jsonify({"error": "email already exists"}), 409

    # Create new user
    user_id = next_id(store["users"])
    user = {
        "id": user_id,
        "full_name": full_name,
        "email": email,
        "password_hash": hash_password(password),
        # default user preference
        "currency": "USD",
        "created_at": utc_now_iso(),
        "updated_at": utc_now_iso(),
    }
    store["users"].append(user)

    # Generate token
    token = generate_token(user_id, email)

    return jsonify({
        "message": "User registered successfully",
        "token": token,
        "user": {
            "id": user["id"],
            "full_name": user["full_name"],
            "email": user["email"],
            "currency": user.get("currency", "USD")
        }
    }), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    # Validation
    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    # Find user
    user = next((u for u in store["users"] if u["email"] == email), None)
    if not user:
        return jsonify({"error": "invalid credentials"}), 401

    # Verify password
    if not verify_password(password, user["password_hash"]):
        return jsonify({"error": "invalid credentials"}), 401

    # Generate token
    token = generate_token(user["id"], user["email"])

    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": {
            "id": user["id"],
            "full_name": user["full_name"],
            "email": user["email"],
            "currency": user.get("currency", "USD")
        }
    }), 200


@auth_bp.post("/logout")
def logout():
    return jsonify({"message": "logged_out"}), 200


@auth_bp.post("/reset-password")
def reset_password():
    return jsonify({"message": "password reset flow placeholder"}), 200


@auth_bp.get('/preferences')
@token_required
def get_preferences():
    user = next((u for u in store['users'] if u['id'] == request.user_id), None)
    if not user:
        return jsonify({"error": "user not found"}), 404

    return jsonify({"currency": user.get('currency', 'USD')})


@auth_bp.post('/preferences')
@token_required
def set_preferences():
    data = request.get_json(silent=True) or {}
    currency = str(data.get('currency', '')).strip().upper()
    if not currency:
        return jsonify({"error": "currency is required"}), 400

    user = next((u for u in store['users'] if u['id'] == request.user_id), None)
    if not user:
        return jsonify({"error": "user not found"}), 404

    user['currency'] = currency
    user['updated_at'] = utc_now_iso()

    return jsonify({"currency": user['currency']})

