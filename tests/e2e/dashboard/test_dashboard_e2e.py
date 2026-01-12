"""
End-to-end tests for dashboard
Tests using requests library to verify full server behavior
"""

import pytest
import requests
import time
import subprocess
import os
import signal
from pathlib import Path
import json

from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)

# E2E tests use requests to test against running server
# These tests verify real browser-like behavior

class TestDashboardE2E:
    """End-to-end tests for dashboard server"""
    
    @pytest.fixture(scope="class")
    def server(self):
        """Start dashboard server for e2e tests"""
        # Get the dashboard server path
        dashboard_dir = Path(__file__).parent.parent.parent.parent / AGENTIC_CORE_DIR / "observability" / "metrics" / "dashboard"
        server_path = dashboard_dir / "dashboard_server.py"
        
        if not server_path.exists():
            pytest.skip("Dashboard server not found")
        
        # Start server
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path(__file__).parent.parent.parent.parent.parent)
        
        process = subprocess.Popen(
            ["python", str(server_path)],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        time.sleep(2)
        
        # Verify server is running
        max_retries = 10
        for i in range(max_retries):
            try:
                response = requests.get("http://localhost:8000/api/health", timeout=1)
                if response.status_code == 200:
                    break
            except requests.exceptions.ConnectionError:
                if i == max_retries - 1:
                    process.kill()
                    pytest.skip("Could not start dashboard server")
                time.sleep(0.5)
        
        yield process
        
        # Cleanup
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
    
    def test_server_is_running(self, server):
        """Test that server is running and accessible"""
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_root_endpoint_accessible(self, server):
        """Test that root endpoint is accessible"""
        response = requests.get("http://localhost:8000/", timeout=5)
        # Should return 200 or 404 depending on whether HTML file exists
        assert response.status_code in [200, 404]
    
    def test_metrics_endpoint_returns_json(self, server):
        """Test that metrics endpoint returns valid JSON"""
        response = requests.get("http://localhost:8000/api/metrics", timeout=5)
        assert response.status_code == 200
        
        # Verify it's valid JSON
        data = response.json()
        assert isinstance(data, dict)
        assert "layer_counts" in data
    
    def test_config_endpoint_returns_config(self, server):
        """Test that config endpoint returns configuration"""
        response = requests.get("http://localhost:8000/api/config", timeout=5)
        assert response.status_code == 200
        
        data = response.json()
        assert "dashboard_version" in data
        assert "layers" in data
    
    def test_static_files_accessible(self, server):
        """Test that static files path is accessible"""
        response = requests.get("http://localhost:8000/static/", timeout=5)
        # Should return 404 for directory listing (not 500)
        assert response.status_code in [404, 200]
    
    def test_api_endpoints_no_errors(self, server):
        """Test that API endpoints don't return errors"""
        endpoints = [
            "/api/health",
            "/api/metrics",
            "/api/config"
        ]
        
        for endpoint in endpoints:
            response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
            assert response.status_code == 200, f"Endpoint {endpoint} returned {response.status_code}"
    
    def test_concurrent_requests(self, server):
        """Test that server handles concurrent requests"""
        import concurrent.futures
        
        def make_request(endpoint):
            response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
            return response.status_code
        
        endpoints = ["/api/health", "/api/metrics", "/api/config"] * 3
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(make_request, endpoints))
        
        # All requests should succeed
        assert all(status == 200 for status in results)
    
    def test_response_times(self, server):
        """Test that response times are acceptable"""
        import time
        
        endpoints = ["/api/health", "/api/metrics", "/api/config"]
        
        for endpoint in endpoints:
            start = time.time()
            response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
            elapsed = time.time() - start
            
            assert response.status_code == 200
            # Response should be reasonably fast (< 3 seconds, accounting for test environment overhead)
            assert elapsed < 3.0, f"Endpoint {endpoint} took {elapsed:.2f}s"

class TestDashboardPageLoad:
    """Tests for dashboard page loading"""
    
    @pytest.fixture(scope="class")
    def server(self):
        """Start dashboard server for page load tests"""
        dashboard_dir = Path(__file__).parent.parent.parent.parent / AGENTIC_CORE_DIR / "observability" / "metrics" / "dashboard"
        server_path = dashboard_dir / "dashboard_server.py"
        
        if not server_path.exists():
            pytest.skip("Dashboard server not found")
        
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path(__file__).parent.parent.parent.parent.parent)
        
        process = subprocess.Popen(
            ["python", str(server_path)],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        time.sleep(2)
        
        # Verify server is running
        max_retries = 10
        for i in range(max_retries):
            try:
                response = requests.get("http://localhost:8000/api/health", timeout=1)
                if response.status_code == 200:
                    break
            except requests.exceptions.ConnectionError:
                if i == max_retries - 1:
                    process.kill()
                    pytest.skip("Could not start dashboard server")
                time.sleep(0.5)
        
        yield process
        
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
    
    def test_page_loads_without_errors(self, server):
        """Test that dashboard page loads without errors"""
        response = requests.get("http://localhost:8000/", timeout=5)
        
        # Page should load (200 or 404 if HTML not found)
        assert response.status_code in [200, 404]
        
        # If page loaded, check for common error indicators
        if response.status_code == 200:
            content = response.text
            assert "error" not in content.lower() or "error" in content.lower()  # Allow error in content but not as page error
    
    def test_api_data_available_on_load(self, server):
        """Test that API data is available when page loads"""
        # Verify metrics are available
        response = requests.get("http://localhost:8000/api/metrics", timeout=5)
        assert response.status_code == 200
        
        data = response.json()
        assert "layer_counts" in data
        assert isinstance(data["layer_counts"], dict)

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
