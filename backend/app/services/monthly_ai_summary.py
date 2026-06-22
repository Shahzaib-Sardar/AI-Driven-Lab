from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib import error as urlerror
from urllib import request as urlrequest

from app.services.store import store, utc_now_iso

PROMPT_PATH = Path(__file__).resolve().parents[2] / "prompts" / "monthly_spending_summary_v1.txt"


def current_month_key() -> str:
    return datetime.utcnow().strftime("%Y-%m")


def normalize_month(value: Any | None) -> str:
    if value is None:
        return current_month_key()
    month = str(value).strip()
    if len(month) >= 7 and month[4] == "-":
        return month[:7]
    return current_month_key()


def transaction_month(transaction: dict[str, Any]) -> str | None:
    date_value = str(transaction.get("transaction_date", "")).strip()
    if len(date_value) >= 7 and date_value[4] == "-":
        return date_value[:7]
    return None


def load_prompt_template() -> str:
    try:
        return PROMPT_PATH.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return (
            "You are a personal finance assistant. Use the provided JSON context to write a short monthly spending summary. "
            "Return valid JSON with keys summary, recommendations, and flags.\n\n<context_json>\n{{context_json}}\n</context_json>"
        )


def build_monthly_summary_context(month: Any | None = None) -> dict[str, Any]:
    target_month = normalize_month(month)
    monthly_transactions = [
        transaction
        for transaction in store["transactions"]
        if transaction_month(transaction) == target_month
    ]

    category_lookup = {
        str(category["id"]): category["name"]
        for category in store["categories"]
    }

    income = sum(float(tx.get("amount", 0) or 0) for tx in monthly_transactions if tx.get("type") == "income")
    expenses = sum(float(tx.get("amount", 0) or 0) for tx in monthly_transactions if tx.get("type") == "expense")
    net = income - expenses

    expense_breakdown: dict[str, dict[str, Any]] = {}
    for transaction in monthly_transactions:
        if transaction.get("type") != "expense":
            continue
        category_id = transaction.get("category_id")
        category_key = str(category_id) if category_id is not None else "uncategorized"
        category_name = category_lookup.get(category_key, "Uncategorized")
        entry = expense_breakdown.setdefault(
            category_key,
            {
                "category_id": category_id,
                "category_name": category_name,
                "amount": 0.0,
            },
        )
        entry["amount"] += float(transaction.get("amount", 0) or 0)

    ranked_expenses = sorted(expense_breakdown.values(), key=lambda item: item["amount"], reverse=True)
    top_expense_category = ranked_expenses[0] if ranked_expenses else None

    budget = store["budgets"].get(target_month, {})
    overall_budget = budget.get("overall")
    budget_usage = None
    if overall_budget not in (None, ""):
        try:
            overall_budget_value = float(overall_budget)
            if overall_budget_value > 0:
                budget_usage = round((expenses / overall_budget_value) * 100, 1)
        except (TypeError, ValueError):
            budget_usage = None

    return {
        "month": target_month,
        "transaction_count": len(monthly_transactions),
        "income": round(income, 2),
        "expenses": round(expenses, 2),
        "net": round(net, 2),
        "budget": {
            "overall": overall_budget,
            "carry_forward": bool(budget.get("carry_forward", False)),
            "usage_percent": budget_usage,
        },
        "top_expense_category": top_expense_category,
        "expense_breakdown": ranked_expenses[:5],
        "has_transactions": bool(monthly_transactions),
    }


def _build_prompt(context: dict[str, Any]) -> str:
    context_json = json.dumps(context, ensure_ascii=False, indent=2)
    return load_prompt_template().replace("{{context_json}}", context_json)


def _coerce_recommendations(recommendations: Any) -> list[str]:
    if not isinstance(recommendations, list):
        return []

    items = [str(item).strip() for item in recommendations if str(item).strip()]
    return items[:3]


def _fallback_recommendations(context: dict[str, Any]) -> list[str]:
    recommendations: list[str] = []

    if context["transaction_count"] == 0:
        recommendations.append("Log a few transactions to unlock a more useful monthly review.")
    elif context["top_expense_category"]:
        recommendations.append(
            f"Review spending in {context['top_expense_category']['category_name']} and look for one recurring cost to reduce."
        )

    budget = context["budget"]
    if budget.get("overall") not in (None, ""):
        usage = budget.get("usage_percent")
        if usage is not None and usage >= 100:
            recommendations.append("Pause non-essential purchases until the next budget cycle begins.")
        elif usage is not None and usage >= 80:
            recommendations.append("Keep discretionary spending tight to stay below your monthly budget.")
        else:
            recommendations.append("You still have room in the budget, so keep tracking before the month ends.")
    else:
        recommendations.append("Set a monthly budget so the assistant can compare planned and actual spending.")

    recommendations.append("Check payment methods and notes to spot subscriptions or repeated charges.")
    return recommendations[:3]


def _fallback_summary(context: dict[str, Any]) -> dict[str, Any]:
    month = context["month"]
    income = context["income"]
    expenses = context["expenses"]
    net = context["net"]
    budget = context["budget"]

    if context["transaction_count"] == 0:
        summary = f"No transactions were recorded for {month}. Add income and expense entries to generate a useful monthly review."
    else:
        if net >= 0:
            balance_sentence = f"You finished {month} with a positive balance of {net:.2f}."
        else:
            balance_sentence = f"You spent {abs(net):.2f} more than you earned in {month}."

        if budget.get("usage_percent") is not None:
            budget_sentence = f"Monthly budget usage is at {budget['usage_percent']:.1f}% of the planned total."
        else:
            budget_sentence = "No overall budget is set for this month yet."

        top_category = context["top_expense_category"]
        category_sentence = (
            f"The largest expense category is {top_category['category_name']} at {top_category['amount']:.2f}."
            if top_category
            else "No expense category stands out yet."
        )

        summary = (
            f"In {month}, you recorded {income:.2f} in income and {expenses:.2f} in expenses. "
            f"{balance_sentence} {budget_sentence} {category_sentence}"
        )

    return {
        "month": context["month"],
        "summary": summary,
        "recommendations": _fallback_recommendations(context),
        "flags": [],
        "source": "fallback",
    }


def _call_openai_summary(context: dict[str, Any]) -> dict[str, Any] | None:
    # Attempt RAG retrieval and inject into prompt when available
    retrieved_snippets: list[dict[str, Any]] = []
    try:
        from app.services.rag import retrieve

        try:
            retrieved = retrieve(json.dumps(context), top_k=3)
            for r in retrieved:
                retrieved_snippets.append({
                    "text": r.get("text"),
                    "source": r.get("metadata", {}).get("source", "unknown"),
                    "title": r.get("title"),
                })
        except Exception:
            retrieved_snippets = []
    except Exception:
        # RAG service not available
        retrieved_snippets = []

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").strip().rstrip("/")
    endpoint = f"{base_url}/chat/completions"

    # build prompt and inject retrieved snippets
    prompt = _build_prompt(context)
    if retrieved_snippets:
        retrieved_section = "\n\n".join([
            f"Source: {s['source']}\nTitle: {s.get('title','')}\nText: {s['text']}"
            for s in retrieved_snippets
        ])
        prompt = prompt.replace("{{retrieved_context}}", retrieved_section)
    else:
        prompt = prompt.replace("{{retrieved_context}}", "")

    payload = {
        "model": model,
        "temperature": 0.3,
        "response_format": {"type": "json_object"},
        "messages": [
            {
                "role": "system",
                "content": "You are a precise personal finance assistant. Follow the prompt and return only valid JSON.",
            },
            {"role": "user", "content": prompt},
        ],
    }

    request_obj = urlrequest.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlrequest.urlopen(request_obj, timeout=20) as response:
            response_payload = json.loads(response.read().decode("utf-8"))
    except (urlerror.URLError, TimeoutError, ValueError, OSError):
        return None

    try:
        content = response_payload["choices"][0]["message"]["content"]
        parsed = json.loads(content)
    except (KeyError, IndexError, TypeError, json.JSONDecodeError):
        return None

    # attach retrieved sources if present
    if retrieved_snippets and isinstance(parsed, dict):
        parsed.setdefault("rag_sources", [])
        parsed["rag_sources"].extend([s.get("source") for s in retrieved_snippets if s.get("source")])
        parsed["rag_snippets"] = [ {"title": s.get("title"), "source": s.get("source"), "text": s.get("text")} for s in retrieved_snippets ]

    return parsed if isinstance(parsed, dict) else None


def generate_monthly_spending_summary(month: Any | None = None) -> dict[str, Any]:
    context = build_monthly_summary_context(month)
    ai_output = _call_openai_summary(context)

    if not ai_output:
        summary_payload = _fallback_summary(context)
    else:
        summary_text = str(ai_output.get("summary", "")).strip() or _fallback_summary(context)["summary"]
        recommendations = _coerce_recommendations(ai_output.get("recommendations")) or _fallback_recommendations(context)
        flags = [str(flag).strip() for flag in ai_output.get("flags", []) if str(flag).strip()]
        summary_payload = {
            "month": context["month"],
            "summary": summary_text,
            "recommendations": recommendations[:3],
            "flags": flags[:3],
            "source": "llm",
        }

    summary_payload["generated_at"] = utc_now_iso()
    summary_payload["metrics"] = {
        "income": context["income"],
        "expenses": context["expenses"],
        "net": context["net"],
        "transaction_count": context["transaction_count"],
        "budget": context["budget"],
        "top_expense_category": context["top_expense_category"],
        "expense_breakdown": context["expense_breakdown"],
    }
    return summary_payload