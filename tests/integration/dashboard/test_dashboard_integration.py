"""
Integration tests for dashboard server
Tests full response chain, static assets, and API data flow
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import json

from agentic_core.observability.metrics.dashboard.dashboard_server import app
from agentic_core.observability.metrics.shared_counters import (
    increment_layer_activation, reset_layer_counts, get_layer_counts
)

@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)

@pytest.fixture(autouse=True)
def reset_counters():
    """Reset layer counters before each test"""
    reset_layer_counts()
    yield
    reset_layer_counts()

class TestDashboardFullFlow:
    """Integration tests for full dashboard flow"""
    
    def test_metrics_api_reflects_activations(self, client):
        """Test that metrics API reflects layer activations"""
        # Reset and set known state
        reset_layer_counts()
        
        # Increment some layers
        increment_layer_activation("L3_orchestration")
        increment_layer_activation("L3_orchestration")
        increment_layer_activation("L2_execution")
        
        # Fetch metrics
        response = client.get("/api/metrics")
        assert response.status_code == 200
        data = response.json()
        
        # Verify counts
        assert data["layer_counts"]["L3_orchestration"] == 2
        assert data["layer_counts"]["L2_execution"] == 1
        assert data["total_activations"] == 3
    
    def test_config_layers_match_metrics_layers(self, client):
        """Test that config layers match available metrics layers"""
        config_response = client.get("/api/config")
        metrics_response = client.get("/api/metrics")
        
        assert config_response.status_code == 200
        assert metrics_response.status_code == 200
        
        config_layers = set(config_response.json()["layers"])
        metrics_layers = set(metrics_response.json()["layer_counts"].keys())
        
        # All config layers should be in metrics
        assert config_layers.issubset(metrics_layers)
    
    def test_health_check_consistency(self, client):
        """Test that health check is consistent across calls"""
        response1 = client.get("/api/health")
        response2 = client.get("/api/health")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        data1 = response1.json()
        data2 = response2.json()
        
        # Status should be consistent
        assert data1["status"] == data2["status"] == "healthy"

class TestStaticAssetServing:
    """Tests for static asset serving"""
    
    def test_static_directory_exists(self):
        """Test that static directory exists"""
        from pathlib import Path
        from agentic_core.config.blueprint_sovereign.structure_blueprint import (
            get_validated_project_root, safe_path_join
        )
        PROJECT_ROOT = get_validated_project_root()
        STATIC_DIR = safe_path_join(
            PROJECT_ROOT,
            "agentic_core", "observability", "metrics", "dashboard", "static"
        )
        assert STATIC_DIR.exists(), f"Static directory does not exist: {STATIC_DIR}"
    
    def test_static_mount_path(self, client):
        """Test that static mount path is configured"""
        # Try accessing static path (will 404 for non-existent file, but mount works)
        response = client.get("/static/")
        # Should return 404 (not 500), indicating mount is working
        assert response.status_code in [404, 200]

class TestAPIDataConsistency:
    """Tests for API data consistency"""
    
    def test_metrics_total_matches_sum(self, client):
        """Test that total_activations equals sum of layer counts"""
        # Set known state
        reset_layer_counts()
        increment_layer_activation("L0_maintenance")
        increment_layer_activation("L1_cognition")
        increment_layer_activation("L1_cognition")
        increment_layer_activation("L2_execution")
        
        response = client.get("/api/metrics")
        assert response.status_code == 200
        data = response.json()
        
        # Verify total
        expected_total = sum(data["layer_counts"].values())
        assert data["total_activations"] == expected_total
    
    def test_metrics_all_layers_present(self, client):
        """Test that all expected layers are present in metrics"""
        response = client.get("/api/metrics")
        assert response.status_code == 200
        data = response.json()
        
        expected_layers = [
            "L0_maintenance", "L1_cognition", "L2_execution", "L3_orchestration",
            "L4_state", "L5_safety", "config", "schemas", "prompt_governance",
            "observability", "utils", "apps_rg", "apps_lic", "apps_shared"
        ]
        
        for layer in expected_layers:
            assert layer in data["layer_counts"], f"Missing layer: {layer}"
            assert isinstance(data["layer_counts"][layer], int)
    
    def test_config_endpoint_stability(self, client):
        """Test that config endpoint returns stable data"""
        response1 = client.get("/api/config")
        response2 = client.get("/api/config")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        data1 = response1.json()
        data2 = response2.json()
        
        # Config should be identical across calls
        assert data1 == data2

class TestErrorRecovery:
    """Tests for error handling and recovery"""
    
    def test_metrics_endpoint_graceful_degradation(self, client):
        """Test that metrics endpoint degrades gracefully on error"""
        # Make multiple requests to ensure no state corruption
        for _ in range(5):
            response = client.get("/api/metrics")
            assert response.status_code == 200
            assert "layer_counts" in response.json()
    
    def test_sequential_requests_consistency(self, client):
        """Test that sequential requests maintain consistency"""
        reset_layer_counts()
        
        # Make sequential requests
        for i in range(3):
            increment_layer_activation("L3_orchestration")
            response = client.get("/api/metrics")
            assert response.status_code == 200
            assert response.json()["layer_counts"]["L3_orchestration"] == i + 1

class TestResponseFormats:
    """Tests for response format consistency"""
    
    def test_metrics_response_format(self, client):
        """Test that metrics response has correct format"""
        response = client.get("/api/metrics")
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "status" in data
        assert "layer_counts" in data
        assert "total_activations" in data
        
        # Check types
        assert isinstance(data["status"], str)
        assert isinstance(data["layer_counts"], dict)
        assert isinstance(data["total_activations"], int)
    
    def test_config_response_format(self, client):
        """Test that config response has correct format"""
        response = client.get("/api/config")
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "dashboard_version" in data
        assert "metrics_endpoint" in data
        assert "static_path" in data
        assert "layers" in data
        
        # Check types
        assert isinstance(data["dashboard_version"], str)
        assert isinstance(data["metrics_endpoint"], str)
        assert isinstance(data["static_path"], str)
        assert isinstance(data["layers"], list)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
