"""
Integration test file - should go to tests/integration/
"""

import pytest
from fastapi.testclient import TestClient


class TestExampleIntegration:
    """Integration test class."""

    @pytest.mark.integration
    def test_api_endpoint(self):
        """Test API integration."""
        client = TestClient(app)
        response = client.get("/test")
        assert response.status_code == 200
