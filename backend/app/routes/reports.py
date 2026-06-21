import csv
import io

from flask import Blueprint, Response, jsonify, request

from app.middleware.auth import token_required
from app.services.monthly_ai_summary import generate_monthly_spending_summary
from app.services.store import store

reports_bp = Blueprint("reports", __name__)


@reports_bp.get("/monthly")
def monthly_report():
    return jsonify({"message": "monthly report placeholder", "total": len(store["transactions"])})


@reports_bp.post("/ai-summary")
@token_required
def ai_summary():
    data = request.get_json(silent=True) or {}
    month = data.get("month")
    return jsonify(generate_monthly_spending_summary(month=month))


@reports_bp.get("/export/csv")
def export_csv():
    output = io.StringIO()
    fieldnames = ["id", "type", "amount", "category_id", "transaction_date", "note", "payment_method"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    # Filter each transaction to only include the defined fieldnames
    filtered_transactions = [
        {key: tx.get(key, "") for key in fieldnames}
        for tx in store["transactions"]
    ]
    writer.writerows(filtered_transactions)

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=transactions.csv"},
    )
