from flask import Blueprint, jsonify, request

from app.services.store import next_id, store, utc_now_iso

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    name = str(data.get("name", "")).strip()

    if not email or not password or not name:
        return jsonify({"error": "name, email, and password are required"}), 400

    if any(user["email"] == email for user in store["users"]):
        return jsonify({"error": "email already exists"}), 409

    user = {
        "id": next_id(store["users"]),
        "name": name,
        "email": email,
        "password_hash": "TODO_HASH_PASSWORD",
        "created_at": utc_now_iso(),
        "updated_at": utc_now_iso(),
    }
    store["users"].append(user)

    return jsonify({"message": "registered", "user": {"id": user["id"], "name": name, "email": email}}), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    user = next((u for u in store["users"] if u["email"] == email), None)
    if not user or not password:
        return jsonify({"error": "invalid credentials"}), 401

    return jsonify({"message": "logged_in", "token": "demo-token", "user": {"id": user["id"], "name": user["name"], "email": user["email"]}})


@auth_bp.post("/logout")
def logout():
    return jsonify({"message": "logged_out"})


@auth_bp.post("/reset-password")
def reset_password():
    return jsonify({"message": "password reset flow placeholder"})
