from flask import Blueprint, jsonify, request

from app.services.store import store

budgets_bp = Blueprint("budgets", __name__)


@budgets_bp.get("")
def get_budgets():
    return jsonify(store["budgets"])


@budgets_bp.post("")
def set_budget():
    data = request.get_json(silent=True) or {}
    month = str(data.get("month", "")).strip()
    overall = data.get("overall")
    by_category = data.get("by_category", {})
    carry_forward = bool(data.get("carry_forward", False))

    if not month:
        return jsonify({"error": "month is required"}), 400

    store["budgets"][month] = {
        "overall": overall,
        "by_category": by_category,
        "carry_forward": carry_forward,
    }
    return jsonify({"month": month, **store["budgets"][month]}), 201
