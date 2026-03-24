from flask import Blueprint, jsonify

from app.services.store import store

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("/summary")
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
        "total_income": income,
        "total_expense": expense,
        "net_balance": net,
        "budget_remaining": None,
        "expenses_by_category": by_category,
        "recent_transactions": store["transactions"][-5:],
    })
