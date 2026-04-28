import csv
import io

from flask import Blueprint, Response, jsonify

from app.services.store import store

reports_bp = Blueprint("reports", __name__)


@reports_bp.get("/monthly")
def monthly_report():
    return jsonify({"message": "monthly report placeholder", "total": len(store["transactions"])})


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
