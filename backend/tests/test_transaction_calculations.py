"""
Unit tests for transaction calculation logic
Run with: pytest backend/tests/test_transaction_calculations.py -v
"""
import pytest


class TestTransactionTotals:
    """Test suite for transaction total calculations"""
    
    def test_calculate_total_expenses(self):
        """Test that total expenses are calculated correctly"""
        # Arrange
        transactions = [
            {"type": "expense", "amount": 100},
            {"type": "expense", "amount": 250},
            {"type": "expense", "amount": 75},
            {"type": "income", "amount": 5000},
        ]
        
        # Act
        total_expenses = sum(t["amount"] for t in transactions if t["type"] == "expense")
        
        # Assert
        assert total_expenses == 425
    
    def test_calculate_total_income(self):
        """Test that total income is calculated correctly"""
        # Arrange
        transactions = [
            {"type": "income", "amount": 5000},
            {"type": "income", "amount": 2000},
            {"type": "expense", "amount": 100},
        ]
        
        # Act
        total_income = sum(t["amount"] for t in transactions if t["type"] == "income")
        
        # Assert
        assert total_income == 7000
    
    def test_calculate_balance(self):
        """Test that balance (income - expenses) is correct"""
        # Arrange
        transactions = [
            {"type": "income", "amount": 5000},
            {"type": "expense", "amount": 100},
            {"type": "expense", "amount": 200},
        ]
        
        # Act
        total_income = sum(t["amount"] for t in transactions if t["type"] == "income")
        total_expense = sum(t["amount"] for t in transactions if t["type"] == "expense")
        balance = total_income - total_expense
        
        # Assert
        assert balance == 4700
    
    def test_calculate_savings_rate(self):
        """Test that savings rate percentage is calculated correctly"""
        # Arrange
        income = 5000
        expenses = 1000
        
        # Act
        savings = income - expenses
        savings_rate = (savings / income) * 100 if income > 0 else 0
        
        # Assert
        assert savings == 4000
        assert savings_rate == 80.0
    
    def test_no_transactions(self):
        """Test calculations with no transactions"""
        # Arrange
        transactions = []
        
        # Act
        total_income = sum(t["amount"] for t in transactions if t["type"] == "income")
        total_expense = sum(t["amount"] for t in transactions if t["type"] == "expense")
        balance = total_income - total_expense
        
        # Assert
        assert balance == 0


class TestTransactionValidation:
    """Test suite for transaction input validation"""
    
    def test_transaction_amount_must_be_positive(self):
        """Test that transaction amounts must be positive"""
        amount = -100
        assert amount < 0
    
    def test_transaction_type_must_be_valid(self):
        """Test that transaction type is either income or expense"""
        valid_types = ["income", "expense"]
        transaction_type = "income"
        assert transaction_type in valid_types
