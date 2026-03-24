from flask import Blueprint, jsonify, request

from app.services.store import next_id, store

categories_bp = Blueprint("categories", __name__)


@categories_bp.get("")
def list_categories():
    return jsonify({"items": store["categories"]})


@categories_bp.post("")
def create_category():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    cat_type = data.get("type")

    if not name or cat_type not in {"income", "expense"}:
        return jsonify({"error": "valid name and type are required"}), 400

    category = {"id": next_id(store["categories"]), "name": name, "type": cat_type, "is_default": False}
    store["categories"].append(category)
    return jsonify(category), 201


@categories_bp.put("/<int:category_id>")
def update_category(category_id: int):
    category = next((item for item in store["categories"] if item["id"] == category_id), None)
    if not category:
        return jsonify({"error": "category not found"}), 404

    data = request.get_json(silent=True) or {}
    if "name" in data:
        category["name"] = str(data["name"]).strip()
    if "type" in data and data["type"] in {"income", "expense"}:
        category["type"] = data["type"]

    return jsonify(category)


@categories_bp.delete("/<int:category_id>")
def delete_category(category_id: int):
    in_use = any(tx.get("category_id") == category_id for tx in store["transactions"])
    if in_use:
        return jsonify({"error": "category is currently in use"}), 409

    idx = next((i for i, item in enumerate(store["categories"]) if item["id"] == category_id), None)
    if idx is None:
        return jsonify({"error": "category not found"}), 404

    deleted = store["categories"].pop(idx)
    return jsonify({"message": "deleted", "id": deleted["id"]})
