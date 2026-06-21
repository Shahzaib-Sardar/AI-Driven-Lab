"""
Unit tests for the monthly AI spending summary helpers.
"""

from app.services.monthly_ai_summary import build_monthly_summary_context, generate_monthly_spending_summary
from app.services.store import store


def _seed_data(monkeypatch):
    monkeypatch.setitem(store, "transactions", [
        {"id": 1, "type": "income", "amount": 2500, "transaction_date": "2026-06-02", "category_id": 6},
        {"id": 2, "type": "expense", "amount": 400, "transaction_date": "2026-06-03", "category_id": 1},
        {"id": 3, "type": "expense", "amount": 250, "transaction_date": "2026-06-10", "category_id": 2},
        {"id": 4, "type": "expense", "amount": 150, "transaction_date": "2026-05-29", "category_id": 1},
    ])
    monkeypatch.setitem(store, "categories", [
        {"id": 1, "name": "Food", "type": "expense", "is_default": True},
        {"id": 2, "name": "Transport", "type": "expense", "is_default": True},
        {"id": 6, "name": "Salary", "type": "income", "is_default": True},
    ])
    monkeypatch.setitem(store, "budgets", {
        "2026-06": {"overall": 1500, "by_category": {"Food": 500}, "carry_forward": False},
    })


def test_build_monthly_summary_context(monkeypatch):
    _seed_data(monkeypatch)

    context = build_monthly_summary_context("2026-06")

    assert context["month"] == "2026-06"
    assert context["transaction_count"] == 3
    assert context["income"] == 2500
    assert context["expenses"] == 650
    assert context["net"] == 1850
    assert context["top_expense_category"]["category_name"] == "Food"
    assert context["budget"]["usage_percent"] == 43.3


def test_generate_monthly_spending_summary_uses_fallback_without_api_key(monkeypatch):
    _seed_data(monkeypatch)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    result = generate_monthly_spending_summary("2026-06")

    assert result["month"] == "2026-06"
    assert result["source"] == "fallback"
    assert result["summary"]
    assert len(result["recommendations"]) == 3
    assert result["metrics"]["expenses"] == 650