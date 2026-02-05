"""
Integration test example - should be routed to tests/integration/
"""

import pytest
from fastapi.testclient import TestClient


class TestApiIntegration:
    """Integration test for API endpoints."""

    @pytest.mark.integration
    def test_user_api_endpoint(self):
        """Test user API with real database connection."""
        client = TestClient(app)
        response = client.get("/users/1")
        assert response.status_code == 200
