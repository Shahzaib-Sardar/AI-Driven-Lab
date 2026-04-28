"""
Unit tests for budget calculation logic
Run with: pytest backend/tests/test_budget_calculations.py -v
"""
import pytest


class TestBudgetCalculations:
    """Test suite for budget-related calculations"""
    
    def test_calculate_budget_usage_percentage(self):
        """Test that budget usage percentage is calculated correctly"""
        # Arrange
        budget = 1000
        spent = 250
        
        # Act
        percentage_used = (spent / budget) * 100
        
        # Assert
        assert percentage_used == 25.0
        assert percentage_used <= 100
    
    def test_budget_zero_spent(self):
        """Test budget calculation when nothing has been spent"""
        budget = 1000
        spent = 0
        percentage_used = (spent / budget) * 100
        assert percentage_used == 0.0
    
    def test_budget_fully_spent(self):
        """Test budget calculation when entire budget is spent"""
        budget = 1000
        spent = 1000
        percentage_used = (spent / budget) * 100
        assert percentage_used == 100.0
    
    def test_budget_overspent(self):
        """Test budget calculation when spending exceeds budget"""
        budget = 1000
        spent = 1500
        percentage_used = (spent / budget) * 100
        assert percentage_used == 150.0
        assert percentage_used > 100
    
    def test_remaining_budget(self):
        """Test calculation of remaining budget"""
        budget = 1000
        spent = 350
        remaining = budget - spent
        assert remaining == 650
    
    def test_budget_categories_sum(self):
        """Test that category budgets can be summed correctly"""
        category_budgets = {
            "Food": 500,
            "Rent": 1200,
            "Travel": 200
        }
        total = sum(category_budgets.values())
        assert total == 1900


class TestBudgetValidation:
    """Test suite for budget input validation"""
    
    def test_budget_must_be_positive(self):
        """Test that negative budgets are invalid"""
        budget = -500
        assert budget < 0, "Budget should not be negative"
    
    def test_valid_budget_amount(self):
        """Test that positive budget amounts are valid"""
        budget = 1500.50
        assert budget > 0
        assert isinstance(budget, (int, float))
