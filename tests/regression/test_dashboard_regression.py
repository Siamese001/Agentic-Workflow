"""
Regression tests for dashboard API
Ensures /api/metrics response format never regresses
"""

import pytest
import json
from pathlib import Path
from fastapi.testclient import TestClient

from agentic_core.observability.metrics.dashboard.dashboard_server import app
from agentic_core.observability.metrics.shared_counters import reset_layer_counts

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

@pytest.fixture(scope="session")
def baseline():
    """Load regression baseline"""
    baseline_path = Path(__file__).parent / "regression_baseline.json"
    if not baseline_path.exists():
        raise FileNotFoundError(f"Baseline file not found: {baseline_path}")
    with open(baseline_path, "r") as f:
        data = json.load(f)
    return data

class TestMetricsRegressionBaseline:
    """Regression tests against golden baseline"""
    
    def test_metrics_response_structure(self, client, baseline):
        """Test that metrics response structure matches baseline"""
        response = client.get("/api/metrics")
        assert response.status_code == 200
        data = response.json()
        
        # Check all required fields are present
        for field in baseline["required_fields"]:
            assert field in data, f"Missing required field: {field}"
    
    def test_metrics_layer_counts_structure(self, client, baseline):
        """Test that layer_counts has all required layers"""
        response = client.get("/api/metrics")
        assert response.status_code == 200
        data = response.json()
        
        layer_counts = data["layer_counts"]
        
        # Check all required layers are present
        for layer in baseline["required_layers"]:
            assert layer in layer_counts, f"Missing layer: {layer}"
    
    def test_metrics_response_types(self, client, baseline):
        """Test that response types match baseline constraints"""
        response = client.get("/api/metrics")
        assert response.status_code == 200
        data = response.json()
        
        # Check status type
        assert isinstance(data["status"], str)
        
        # Check layer_counts type
        assert isinstance(data["layer_counts"], dict)
        
        # Check total_activations type
        assert isinstance(data["total_activations"], int)
        
        # Check all layer values are integers
        for layer, count in data["layer_counts"].items():
            assert isinstance(count, int), f"Layer {layer} count is not integer: {type(count)}"
    
    def test_metrics_total_consistency(self, client):
        """Test that total_activations equals sum of layer counts"""
        response = client.get("/api/metrics")
        assert response.status_code == 200
        data = response.json()
        
        calculated_total = sum(data["layer_counts"].values())
        assert data["total_activations"] == calculated_total
    
    def test_metrics_status_value(self, client):
        """Test that status has expected value"""
        response = client.get("/api/metrics")
        assert response.status_code == 200
        data = response.json()
        
        # Status should be "success" or "error"
        assert data["status"] in ["success", "error"]
    
    def test_metrics_layer_counts_non_negative(self, client):
        """Test that all layer counts are non-negative"""
        response = client.get("/api/metrics")
        assert response.status_code == 200
        data = response.json()
        
        for layer, count in data["layer_counts"].items():
            assert count >= 0, f"Layer {layer} has negative count: {count}"
    
    def test_metrics_response_stability(self, client):
        """Test that multiple calls return consistent structure"""
        responses = [client.get("/api/metrics") for _ in range(3)]
        
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            
            # All responses should have same structure
            assert "status" in data
            assert "layer_counts" in data
            assert "total_activations" in data
    
    def test_metrics_no_extra_fields(self, client, baseline):
        """Test that response doesn't have unexpected extra fields"""
        response = client.get("/api/metrics")
        assert response.status_code == 200
        data = response.json()
        
        # Check no unexpected top-level fields (allow for error message)
        allowed_fields = set(baseline["required_fields"]) | {"message"}
        actual_fields = set(data.keys())
        
        unexpected = actual_fields - allowed_fields
        assert not unexpected, f"Unexpected fields in response: {unexpected}"
    
    def test_metrics_layer_counts_completeness(self, client, baseline):
        """Test that layer_counts has exactly the expected layers"""
        response = client.get("/api/metrics")
        assert response.status_code == 200
        data = response.json()
        
        layer_counts = data["layer_counts"]
        expected_layers = set(baseline["required_layers"])
        actual_layers = set(layer_counts.keys())
        
        # All expected layers should be present
        missing = expected_layers - actual_layers
        assert not missing, f"Missing layers: {missing}"
        
        # No unexpected layers should be present
        extra = actual_layers - expected_layers
        assert not extra, f"Unexpected layers: {extra}"

class TestRegressionTolerance:
    """Tests with configurable tolerance for regression detection"""
    
    def test_metrics_response_within_tolerance(self, client, baseline):
        """Test that response structure is within acceptable tolerance"""
        response = client.get("/api/metrics")
        assert response.status_code == 200
        data = response.json()
        
        # Tolerance: all required fields must be present
        tolerance_threshold = 0.95  # 95% of fields must be present
        
        required_count = len(baseline["required_fields"])
        present_count = sum(1 for field in baseline["required_fields"] if field in data)
        
        coverage = present_count / required_count
        assert coverage >= tolerance_threshold, f"Field coverage {coverage:.1%} below threshold {tolerance_threshold:.1%}"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
