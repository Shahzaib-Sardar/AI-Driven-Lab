#!/usr/bin/env python3
"""
Utility script to clear all transactions from the in-memory store.
"""

from app.services.store import store

if __name__ == "__main__":
    transaction_count = len(store["transactions"])
    store["transactions"].clear()
    store["budgets"].clear()
    print(f"✓ Cleared {transaction_count} transactions")
    print(f"✓ Cleared budgets")
    print(f"✓ Store reset. Users and categories preserved.")
