from flask import Blueprint, jsonify, request

from app.services.store import next_id, store, utc_now_iso

transactions_bp = Blueprint("transactions", __name__)


@transactions_bp.get("")
def list_transactions():
    txs = store["transactions"]
    tx_type = request.args.get("type")
    q = request.args.get("q", "").strip().lower()

    filtered = txs
    if tx_type in {"income", "expense"}:
        filtered = [tx for tx in filtered if tx["type"] == tx_type]
    if q:
        filtered = [tx for tx in filtered if q in tx.get("note", "").lower()]

    return jsonify({"items": filtered, "total": len(filtered)})


@transactions_bp.post("")
def create_transaction():
    data = request.get_json(silent=True) or {}
    tx_type = data.get("type")
    amount = data.get("amount")

    if tx_type not in {"income", "expense"}:
        return jsonify({"error": "type must be income or expense"}), 400

    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return jsonify({"error": "amount must be numeric"}), 400

    if amount <= 0:
        return jsonify({"error": "amount must be positive"}), 400

    tx = {
        "id": next_id(store["transactions"]),
        "type": tx_type,
        "amount": amount,
        "category_id": data.get("category_id"),
        "transaction_date": data.get("transaction_date"),
        "note": str(data.get("note", "")).strip(),
        "payment_method": data.get("payment_method"),
        "created_at": utc_now_iso(),
        "updated_at": utc_now_iso(),
    }

    store["transactions"].append(tx)
    return jsonify(tx), 201


@transactions_bp.put("/<int:transaction_id>")
def update_transaction(transaction_id: int):
    tx = next((item for item in store["transactions"] if item["id"] == transaction_id), None)
    if not tx:
        return jsonify({"error": "transaction not found"}), 404

    data = request.get_json(silent=True) or {}
    for key in ["type", "amount", "category_id", "transaction_date", "note", "payment_method"]:
        if key in data:
            tx[key] = data[key]
    tx["updated_at"] = utc_now_iso()

    return jsonify(tx)


@transactions_bp.delete("/<int:transaction_id>")
def delete_transaction(transaction_id: int):
    idx = next((i for i, item in enumerate(store["transactions"]) if item["id"] == transaction_id), None)
    if idx is None:
        return jsonify({"error": "transaction not found"}), 404

    deleted = store["transactions"].pop(idx)
    return jsonify({"message": "deleted", "id": deleted["id"]})
