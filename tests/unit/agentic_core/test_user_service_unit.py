"""
Unit test example - should be routed to tests/unit/
"""
import unittest
from unittest.mock import MagicMock, patch
import pytest

class TestUserServiceUnit:
    """Unit test for user service logic."""
    
    @patch('user_service.database')
    def test_create_user_with_mock(self, mock_db):
        """Test user creation with mocked database."""
        mock_db.return_value = {"id": 1, "name": "test"}
        result = create_user("test")
        assert result["name"] == "test"
