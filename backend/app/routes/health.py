from flask import Blueprint, jsonify
from app.services.store import store

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health_check():
    return jsonify({"status": "ok"})


@health_bp.post("/admin/clear-transactions")
def clear_transactions():
    """Admin endpoint to clear all transactions and budgets. Use with caution."""
    transaction_count = len(store["transactions"])
    store["transactions"].clear()
    store["budgets"].clear()
    return jsonify({
        "message": "All transactions and budgets cleared",
        "cleared_transactions": transaction_count
    }), 200
