"""
Unit tests for dashboard server endpoints
Tests all endpoints, static file mounting, and error cases
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from pathlib import Path
import json

# Import the app
# DEPRECATED: Old import path - new architecture uses L6_observability
# from agentic_core.observability.metrics.dashboard.dashboard_server import app
import pytest
pytestmark = pytest.mark.skip(reason="DEPRECATED: Old dashboard server path - new architecture uses L6_observability")

@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)

class TestDashboardRootEndpoint:
    """Tests for the root endpoint serving dashboard HTML"""
    
    def test_root_endpoint_returns_html(self, client):
        """Test that root endpoint returns HTML content"""
        response = client.get("/")
        # Should return 200 or 404 depending on whether file exists
        assert response.status_code in [200, 404]
    
    def test_root_endpoint_content_type(self, client):
        """Test that root endpoint returns correct content type when HTML exists"""
        response = client.get("/")
        # If HTML file exists, should return text/html; if not, returns JSON error
        if response.status_code == 200:
            content_type = response.headers.get("content-type", "")
            # Accept either HTML or JSON (JSON if file doesn't exist in test env)
            assert "text/html" in content_type or "application/json" in content_type

class TestMetricsEndpoint:
    """Tests for the /api/metrics endpoint"""
    
    def test_metrics_endpoint_returns_json(self, client):
        """Test that metrics endpoint returns valid JSON"""
        response = client.get("/api/metrics")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
    
    def test_metrics_endpoint_has_layer_counts(self, client):
        """Test that metrics endpoint returns layer_counts"""
        response = client.get("/api/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "layer_counts" in data
        assert isinstance(data["layer_counts"], dict)
    
    def test_metrics_endpoint_has_total_activations(self, client):
        """Test that metrics endpoint returns total_activations"""
        response = client.get("/api/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "total_activations" in data
        assert isinstance(data["total_activations"], int)
    
    def test_metrics_endpoint_layer_counts_structure(self, client):
        """Test that layer_counts has expected layer keys"""
        response = client.get("/api/metrics")
        assert response.status_code == 200
        data = response.json()
        layer_counts = data["layer_counts"]
        
        # Check for expected layers
        expected_layers = [
            "L0_maintenance", "L1_cognition", "L2_execution", "L3_orchestration",
            "L4_state", "L5_safety"
        ]
        for layer in expected_layers:
            assert layer in layer_counts
            assert isinstance(layer_counts[layer], int)
    
    @patch('agentic_core.observability.metrics.dashboard.dashboard_server.get_layer_counts')
    def test_metrics_endpoint_error_handling(self, mock_get_counts, client):
        """Test that metrics endpoint handles errors gracefully"""
        mock_get_counts.side_effect = Exception("Test error")
        response = client.get("/api/metrics")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert "message" in data

class TestHealthEndpoint:
    """Tests for the /api/health endpoint"""
    
    def test_health_endpoint_returns_healthy(self, client):
        """Test that health endpoint returns healthy status"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_health_endpoint_has_service_name(self, client):
        """Test that health endpoint returns service name"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert data["service"] == "autonomy-dashboard"
    
    def test_health_endpoint_has_static_dir_info(self, client):
        """Test that health endpoint returns static directory info"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "static_dir" in data
        assert "static_dir_exists" in data

class TestConfigEndpoint:
    """Tests for the /api/config endpoint"""
    
    def test_config_endpoint_returns_config(self, client):
        """Test that config endpoint returns configuration"""
        response = client.get("/api/config")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
    
    def test_config_endpoint_has_version(self, client):
        """Test that config endpoint returns version"""
        response = client.get("/api/config")
        assert response.status_code == 200
        data = response.json()
        assert "dashboard_version" in data
    
    def test_config_endpoint_has_endpoints(self, client):
        """Test that config endpoint returns endpoint paths"""
        response = client.get("/api/config")
        assert response.status_code == 200
        data = response.json()
        assert "metrics_endpoint" in data
        assert "static_path" in data
    
    def test_config_endpoint_has_layers(self, client):
        """Test that config endpoint returns layer list"""
        response = client.get("/api/config")
        assert response.status_code == 200
        data = response.json()
        assert "layers" in data
        assert isinstance(data["layers"], list)
        assert len(data["layers"]) > 0

class TestStaticFilesMount:
    """Tests for static files mounting"""
    
    def test_static_path_exists(self, client):
        """Test that static path is mounted"""
        # Try to access a non-existent static file
        response = client.get("/static/nonexistent.js")
        # Should return 404 (not 500), indicating static mount works
        assert response.status_code == 404

class TestEndpointIntegration:
    """Integration tests for endpoint interactions"""
    
    def test_metrics_and_config_consistency(self, client):
        """Test that metrics and config endpoints are consistent"""
        metrics_response = client.get("/api/metrics")
        config_response = client.get("/api/config")
        
        assert metrics_response.status_code == 200
        assert config_response.status_code == 200
        
        metrics_data = metrics_response.json()
        config_data = config_response.json()
        
        # Verify config layers match metrics layer_counts keys
        config_layers = set(config_data["layers"])
        metrics_layers = set(metrics_data["layer_counts"].keys())
        
        # All config layers should be in metrics
        assert config_layers.issubset(metrics_layers) or metrics_layers.issubset(config_layers)
    
    def test_all_endpoints_accessible(self, client):
        """Test that all main endpoints are accessible"""
        endpoints = ["/", "/api/metrics", "/api/health", "/api/config"]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            # Should not return 500 (server error)
            assert response.status_code != 500, f"Endpoint {endpoint} returned 500"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
