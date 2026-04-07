from flask import Blueprint, jsonify

from app.services.store import store
from app.middleware.auth import token_required

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("/summary")
@token_required
def summary():
    income = sum(tx["amount"] for tx in store["transactions"] if tx["type"] == "income")
    expense = sum(tx["amount"] for tx in store["transactions"] if tx["type"] == "expense")
    net = income - expense

    by_category = {}
    for tx in store["transactions"]:
        if tx["type"] != "expense":
            continue
        key = tx.get("category_id") or "uncategorized"
        by_category[key] = by_category.get(key, 0) + tx["amount"]

    return jsonify({
        "balance": net,
        "income": income,
        "expenses": expense,
        "expenses_by_category": by_category,
        "recent_transactions": store["transactions"][-5:],
    })
