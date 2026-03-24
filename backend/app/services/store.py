from datetime import datetime


# In-memory store for bootstrap/demo. Replace with a real database for production.
store = {
    "users": [],
    "transactions": [],
    "categories": [
        {"id": 1, "name": "Food", "type": "expense", "is_default": True},
        {"id": 2, "name": "Transport", "type": "expense", "is_default": True},
        {"id": 3, "name": "Rent", "type": "expense", "is_default": True},
        {"id": 4, "name": "Utilities", "type": "expense", "is_default": True},
        {"id": 5, "name": "Entertainment", "type": "expense", "is_default": True},
        {"id": 6, "name": "Salary", "type": "income", "is_default": True},
        {"id": 7, "name": "Freelance", "type": "income", "is_default": True},
        {"id": 8, "name": "Other", "type": "income", "is_default": True},
    ],
    "budgets": {},
}


def utc_now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def next_id(items: list[dict]) -> int:
    return (max((item["id"] for item in items), default=0) + 1) if items else 1
