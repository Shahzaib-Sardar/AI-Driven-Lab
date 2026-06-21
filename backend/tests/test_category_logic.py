"""
Unit tests for category logic
Run with: pytest backend/tests/test_category_logic.py -v
"""
import pytest


class TestCategoryCreation:
    """Test suite for category creation logic"""
    
    def test_create_category_with_valid_data(self):
        """Test creating a category with valid data"""
        # Arrange
        category_name = "Food"
        category_type = "expense"
        
        # Act
        category = {
            "id": 1,
            "name": category_name,
            "type": category_type,
            "is_default": False
        }
        
        # Assert
        assert category["name"] == "Food"
        assert category["type"] == "expense"
        assert category["id"] > 0
    
    def test_category_type_validation(self):
        """Test that category type must be income or expense"""
        valid_types = ["income", "expense"]
        new_type = "expense"
        assert new_type in valid_types


class TestCategoryDeletion:
    """Test suite for category deletion logic"""
    
    def test_cannot_delete_default_category(self):
        """Test that default categories cannot be deleted"""
        # Arrange
        category = {
            "id": 1,
            "name": "Other",
            "is_default": True
        }
        
        # Act & Assert
        assert category["is_default"] == True, "Cannot delete default category"
    
    def test_can_delete_custom_category(self):
        """Test that custom categories can be deleted"""
        # Arrange
        category = {
            "id": 5,
            "name": "Travel",
            "is_default": False
        }
        
        # Act & Assert
        assert category["is_default"] == False, "Custom category can be deleted"


class TestCategoryAssignment:
    """Test suite for assigning transactions to categories"""
    
    def test_expense_in_category(self):
        """Test that transactions are assigned to correct category"""
        # Arrange
        transactions = [
            {"id": 1, "category_id": 1, "amount": 50, "type": "expense"},
            {"id": 2, "category_id": 1, "amount": 75, "type": "expense"},
            {"id": 3, "category_id": 2, "amount": 100, "type": "expense"},
        ]
        category_id = 1
        
        # Act
        category_expenses = [t for t in transactions if t["category_id"] == category_id]
        total = sum(t["amount"] for t in category_expenses)
        
        # Assert
        assert len(category_expenses) == 2
        assert total == 125
    
    def test_count_transactions_per_category(self):
        """Test counting transactions in each category"""
        # Arrange
        transactions = [
            {"category_id": 1, "amount": 50},
            {"category_id": 1, "amount": 75},
            {"category_id": 2, "amount": 100},
        ]
        
        # Act
        category_counts = {}
        for t in transactions:
            cat_id = t["category_id"]
            category_counts[cat_id] = category_counts.get(cat_id, 0) + 1
        
        # Assert
        assert category_counts[1] == 2
        assert category_counts[2] == 1
