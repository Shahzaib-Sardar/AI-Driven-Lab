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
    writer = csv.DictWriter(
        output,
        fieldnames=["id", "type", "amount", "category_id", "transaction_date", "note", "payment_method"],
    )
    writer.writeheader()
    writer.writerows(store["transactions"])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=transactions.csv"},
    )
