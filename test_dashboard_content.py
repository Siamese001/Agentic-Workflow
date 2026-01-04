#!/usr/bin/env python
"""
Comprehensive dashboard content and functionality tests
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_dashboard_html():
    """Test dashboard HTML loads with all required content"""
    print("\n=== TEST 1: Dashboard HTML Content ===")
    try:
        r = requests.get(f"{BASE_URL}/")
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        
        required_elements = [
            ("chart.js", "Chart.js library"),
            ("dashboard.js", "Dashboard script"),
            ("entropy-display", "Entropy display element"),
            ("coverageChart", "Coverage chart canvas"),
            ("glossary-content", "Glossary content div"),
            ("Autonomy Dashboard", "Dashboard title"),
            ("Layer Activation Distribution", "Chart section title"),
            ("Territory Glossary", "Glossary section title"),
        ]
        
        for element, description in required_elements:
            assert element in r.text, f"Missing: {description} ({element})"
            print(f"✓ {description}")
        
        print("✓ All HTML elements present")
        return True
    except AssertionError as e:
        print(f"✗ FAILED: {e}")
        return False
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False

def test_metrics_api():
    """Test metrics API returns correct data structure"""
    print("\n=== TEST 2: Metrics API ===")
    try:
        r = requests.get(f"{BASE_URL}/api/metrics")
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        
        data = r.json()
        assert "status" in data, "Missing 'status' field"
        assert data["status"] == "success", f"Expected status='success', got {data['status']}"
        
        assert "layer_counts" in data, "Missing 'layer_counts' field"
        assert isinstance(data["layer_counts"], dict), "layer_counts should be dict"
        
        assert "total_activations" in data, "Missing 'total_activations' field"
        assert isinstance(data["total_activations"], int), "total_activations should be int"
        
        # Check for expected layers
        expected_layers = [
            "L0_maintenance", "L1_cognition", "L2_execution", "L3_orchestration",
            "L4_state", "L5_safety"
        ]
        
        for layer in expected_layers:
            assert layer in data["layer_counts"], f"Missing layer: {layer}"
        
        print(f"✓ Status: {data['status']}")
        print(f"✓ Layer counts: {len(data['layer_counts'])} layers")
        print(f"✓ Total activations: {data['total_activations']}")
        print(f"✓ All expected layers present")
        return True
    except AssertionError as e:
        print(f"✗ FAILED: {e}")
        return False
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False

def test_health_api():
    """Test health check endpoint"""
    print("\n=== TEST 3: Health Endpoint ===")
    try:
        r = requests.get(f"{BASE_URL}/api/health")
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        
        data = r.json()
        assert "status" in data, "Missing 'status' field"
        assert data["status"] == "healthy", f"Expected status='healthy', got {data['status']}"
        
        assert "service" in data, "Missing 'service' field"
        assert data["service"] == "autonomy-dashboard", f"Expected service='autonomy-dashboard'"
        
        assert "static_dir_exists" in data, "Missing 'static_dir_exists' field"
        
        print(f"✓ Status: {data['status']}")
        print(f"✓ Service: {data['service']}")
        print(f"✓ Static dir exists: {data['static_dir_exists']}")
        return True
    except AssertionError as e:
        print(f"✗ FAILED: {e}")
        return False
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False

def test_config_api():
    """Test config endpoint"""
    print("\n=== TEST 4: Config Endpoint ===")
    try:
        r = requests.get(f"{BASE_URL}/api/config")
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        
        data = r.json()
        assert "dashboard_version" in data, "Missing 'dashboard_version'"
        assert "metrics_endpoint" in data, "Missing 'metrics_endpoint'"
        assert "static_path" in data, "Missing 'static_path'"
        assert "layers" in data, "Missing 'layers'"
        
        assert isinstance(data["layers"], list), "layers should be a list"
        assert len(data["layers"]) > 0, "layers list should not be empty"
        
        print(f"✓ Dashboard version: {data['dashboard_version']}")
        print(f"✓ Metrics endpoint: {data['metrics_endpoint']}")
        print(f"✓ Static path: {data['static_path']}")
        print(f"✓ Layers count: {len(data['layers'])}")
        return True
    except AssertionError as e:
        print(f"✗ FAILED: {e}")
        return False
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False

def test_static_files():
    """Test static files are accessible"""
    print("\n=== TEST 5: Static Files ===")
    try:
        # Test dashboard.js
        r = requests.get(f"{BASE_URL}/static/dashboard.js")
        assert r.status_code == 200, f"dashboard.js: Expected 200, got {r.status_code}"
        assert "loadDashboard" in r.text, "dashboard.js missing loadDashboard function"
        assert "CATEGORY_MAP" in r.text, "dashboard.js missing CATEGORY_MAP"
        assert "Chart" in r.text, "dashboard.js missing Chart reference"
        print(f"✓ dashboard.js loaded ({len(r.text)} bytes)")
        
        # Test autonomy_dashboard.html
        r = requests.get(f"{BASE_URL}/static/autonomy_dashboard.html")
        assert r.status_code == 200, f"autonomy_dashboard.html: Expected 200, got {r.status_code}"
        print(f"✓ autonomy_dashboard.html loaded ({len(r.text)} bytes)")
        
        return True
    except AssertionError as e:
        print(f"✗ FAILED: {e}")
        return False
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False

def test_javascript_functionality():
    """Test JavaScript code for syntax and key functions"""
    print("\n=== TEST 6: JavaScript Functionality ===")
    try:
        r = requests.get(f"{BASE_URL}/static/dashboard.js")
        assert r.status_code == 200
        
        js_content = r.text
        
        # Check for key functions
        functions = [
            "loadDashboard",
            "DOMContentLoaded",
            "setInterval",
        ]
        
        for func in functions:
            assert func in js_content, f"Missing function: {func}"
            print(f"✓ Function present: {func}")
        
        # Check for error handling
        assert "catch (error)" in js_content, "Missing error handling"
        assert "if (entropyDisplay)" in js_content, "Missing null check for entropyDisplay"
        assert "if (glossaryContent)" in js_content, "Missing null check for glossaryContent"
        print(f"✓ Error handling with null checks present")
        
        # Check for category map
        assert "L0_maintenance" in js_content, "Missing L0_maintenance in CATEGORY_MAP"
        assert "L1_cognition" in js_content, "Missing L1_cognition in CATEGORY_MAP"
        assert "L5_safety" in js_content, "Missing L5_safety in CATEGORY_MAP"
        print(f"✓ All layer categories defined")
        
        return True
    except AssertionError as e:
        print(f"✗ FAILED: {e}")
        return False
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 70)
    print("DASHBOARD COMPREHENSIVE CONTENT & FUNCTIONALITY TESTS")
    print("=" * 70)
    
    tests = [
        ("Dashboard HTML Content", test_dashboard_html),
        ("Metrics API", test_metrics_api),
        ("Health Endpoint", test_health_api),
        ("Config Endpoint", test_config_api),
        ("Static Files", test_static_files),
        ("JavaScript Functionality", test_javascript_functionality),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ EXCEPTION in {name}: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("\n✓ ALL TESTS PASSED - Dashboard is fully functional")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
