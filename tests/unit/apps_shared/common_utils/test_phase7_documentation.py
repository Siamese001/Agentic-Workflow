#!/usr/bin/env python3
from pathlib import Path

"""
Phase 7: Documentation and Deployment Test Suite

Comprehensive tests for:
- User documentation (DASHBOARD_META_LEARNING_GUIDE.md)
- Developer documentation (META_LEARNING_TELEMETRY_API.md)
- Deployment scripts and configuration
- Documentation completeness and accuracy

Usage:
    python scripts/test_phase7_documentation.py
"""

import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Test results tracking
test_results = {"passed": 0, "failed": 0, "skipped": 0, "tests": []}


def record_test(name: str, passed: bool, details: str = "", skipped: bool = False):
    """Record test result."""
    if skipped:
        status = "SKIPPED"
        test_results["skipped"] += 1
        print(f"  ⏭️  {name}: {details}")
    elif passed:
        status = "PASSED"
        test_results["passed"] += 1
        print(f"  ✅ {name}")
    else:
        status = "FAILED"
        test_results["failed"] += 1
        print(f"  ❌ {name}: {details}")

    test_results["tests"].append({"name": name, "status": status, "details": details})


# =============================================================================
# SECTION 1: USER DOCUMENTATION TESTS
# =============================================================================


def test_user_doc_exists():
    """Test 1.1: User documentation file exists."""
    print("\n" + "=" * 70)
    print("Section 1: User Documentation Tests")
    print("=" * 70)
    print("\n--- Test 1.1: User Documentation File ---")

    doc_file = project_root / "docs" / "DASHBOARD_META_LEARNING_GUIDE.md"
    record_test("DASHBOARD_META_LEARNING_GUIDE.md exists", doc_file.exists())

    if doc_file.exists():
        content = doc_file.read_text(encoding="utf-8")
        record_test("File is not empty", len(content) > 1000, f"Size: {len(content)} bytes")
        return content
    return ""


def test_user_doc_structure(content: str):
    """Test 1.2: User documentation has required sections."""
    print("\n--- Test 1.2: User Documentation Structure ---")

    if not content:
        record_test("User doc structure", False, "No content to check")
        return

    required_sections = [
        ("Overview", "# Overview" in content or "## Overview" in content),
        ("Getting Started", "Getting Started" in content),
        ("Meta-Learning Activity", "Meta-Learning" in content),
        ("Redis cache Activity", "Redis" in content),
        ("Pinecone Vector Operations", "Pinecone" in content),
        ("Agent Execution Flow", "Execution" in content),
        ("Troubleshooting", "Troubleshooting" in content),
        ("FAQ", "FAQ" in content),
    ]

    for section_name, found in required_sections:
        record_test(f"Has '{section_name}' section", found)


def test_user_doc_content(content: str):
    """Test 1.3: User documentation has required content."""
    print("\n--- Test 1.3: User Documentation Content ---")

    if not content:
        record_test("User doc content", False, "No content to check")
        return

    required_content = [
        ("Start API command", "start_runtime_api.py" in content),
        ("Dashboard URL", "localhost:8765" in content or "8765" in content),
        ("API port", "8081" in content),
        ("Experience stream explanation", "experience" in content.lower()),
        ("Strategy weights explanation", "strategy" in content.lower()),
        ("Redis hit rate explanation", "hit rate" in content.lower()),
        ("Pinecone similarity explanation", "similarity" in content.lower()),
        ("Layer flow explanation", "layer" in content.lower()),
        ("Code examples", "```" in content),
        ("Tables for reference", "|" in content),
    ]

    for desc, found in required_content:
        record_test(f"Contains {desc}", found)


def test_user_doc_commands(content: str):
    """Test 1.4: User documentation commands are valid."""
    print("\n--- Test 1.4: User Documentation Commands ---")

    if not content:
        record_test("User doc commands", False, "No content to check")
        return

    # Check for valid command patterns
    commands = [
        ("pip install", "pip install" in content),
        ("python scripts/", "python scripts/" in content),
        ("python -m http.server", "python -m http.server" in content),
        ("curl command", "curl" in content),
    ]

    for desc, found in commands:
        record_test(f"Has {desc}", found)


# =============================================================================
# SECTION 2: DEVELOPER DOCUMENTATION TESTS
# =============================================================================


def test_dev_doc_exists():
    """Test 2.1: Developer documentation file exists."""
    print("\n" + "=" * 70)
    print("Section 2: Developer Documentation Tests")
    print("=" * 70)
    print("\n--- Test 2.1: Developer Documentation File ---")

    doc_file = project_root / "docs" / "META_LEARNING_TELEMETRY_API.md"
    record_test("META_LEARNING_TELEMETRY_API.md exists", doc_file.exists())

    if doc_file.exists():
        content = doc_file.read_text(encoding="utf-8")
        record_test("File is not empty", len(content) > 1000, f"Size: {len(content)} bytes")
        return content
    return ""


def test_dev_doc_structure(content: str):
    """Test 2.2: Developer documentation has required sections."""
    print("\n--- Test 2.2: Developer Documentation Structure ---")

    if not content:
        record_test("Dev doc structure", False, "No content to check")
        return

    required_sections = [
        ("Architecture Overview", "Architecture" in content),
        ("Telemetry Callback Interface", "Callback" in content or "callback" in content),
        ("API Endpoints", "API Endpoints" in content or "Endpoints" in content),
        ("Data Schemas", "schema" in content or "schema" in content),
        ("Adding Custom Telemetry", "Custom" in content or "custom" in content),
        ("Extension Points", "Extension" in content),
        ("Best Practices", "Best Practices" in content or "Practices" in content),
    ]

    for section_name, found in required_sections:
        record_test(f"Has '{section_name}' section", found)


def test_dev_doc_api_endpoints(content: str):
    """Test 2.3: Developer documentation covers all API endpoints."""
    print("\n--- Test 2.3: API Endpoint Documentation ---")

    if not content:
        record_test("API endpoint docs", False, "No content to check")
        return

    endpoints = [
        ("/api/health", "Health check endpoint"),
        ("/api/runtime/state", "Runtime state endpoint"),
        ("/api/meta-learning/statistics", "Meta-learning statistics endpoint"),
        ("/api/meta-learning/activity", "Meta-learning activity endpoint"),
        ("/api/meta-learning/experience", "Meta-learning experience POST endpoint"),
        ("/api/redis/stats", "Redis stats endpoint"),
        ("/api/redis/logs", "Redis logs endpoint"),
        ("/api/pinecone/stats", "Pinecone stats endpoint"),
        ("/api/execution/timeline", "Execution timeline endpoint"),
        ("/api/metrics/latency", "Latency metrics endpoint"),
    ]

    for endpoint, _desc in endpoints:
        record_test(f"Documents {endpoint}", endpoint in content)


def test_dev_doc_schemas(content: str):
    """Test 2.4: Developer documentation has data schemas."""
    print("\n--- Test 2.4: Data schema Documentation ---")

    if not content:
        record_test("schema docs", False, "No content to check")
        return

    schemas = [
        ("Runtime state schema", "runtime_state" in content.lower()),
        ("Experience schema", "experience" in content.lower()),
        ("Execution record schema", "execution" in content.lower()),
        ("Strategy weights", "strategy_weights" in content),
        ("Operations tracking", "operations" in content),
    ]

    for desc, found in schemas:
        record_test(f"Has {desc}", found)


def test_dev_doc_code_examples(content: str):
    """Test 2.5: Developer documentation has code examples."""
    print("\n--- Test 2.5: Code Examples ---")

    if not content:
        record_test("Code examples", False, "No content to check")
        return

    # Count code blocks
    code_blocks = content.count("```python")
    record_test("Has Python code examples", code_blocks >= 5, f"Found {code_blocks} Python blocks")

    # Check for specific patterns
    patterns = [
        ("Callback signature example", "def " in content and "callback" in content.lower()),
        ("MetaLearningAgent usage", "MetaLearningAgent" in content),
        ("SovereignRedisClient usage", "SovereignRedisClient" in content),
        ("PineconeTelemetryWrapper usage", "PineconeTelemetryWrapper" in content),
        ("HTTP request examples", "GET " in content or "POST " in content),
        ("JSON response examples", '"status"' in content or '"total_experiences"' in content),
    ]

    for desc, found in patterns:
        record_test(f"Has {desc}", found)


# =============================================================================
# SECTION 3: DEPLOYMENT CONFIGURATION TESTS
# =============================================================================


def test_deployment_scripts():
    """Test 3.1: Deployment scripts exist and are valid."""
    print("\n" + "=" * 70)
    print("Section 3: Deployment configuration Tests")
    print("=" * 70)
    print("\n--- Test 3.1: Deployment Scripts ---")

    # Check start_runtime_api.py
    start_script = project_root / "scripts" / "start_runtime_api.py"
    record_test("start_runtime_api.py exists", start_script.exists())

    if start_script.exists():
        content = start_script.read_text(encoding="utf-8")
        record_test("Script has argparse", "argparse" in content)
        record_test("Script has uvicorn", "uvicorn" in content)
        record_test("Script has main function", "def main()" in content)
        record_test("Script has port configuration", "--port" in content or "port" in content)
        record_test("Script has host configuration", "--host" in content or "host" in content)


def test_api_module():
    """Test 3.2: API module is importable."""
    print("\n--- Test 3.2: API Module ---")

    try:
        record_test("runtime_api.py is importable", True)
        record_test("FastAPI app exists", app is not None)
    except ImportError as e:
        record_test("runtime_api.py is importable", False, str(e))


def test_dashboard_files():
    """Test 3.3: Dashboard files are in place."""
    print("\n--- Test 3.3: Dashboard Files ---")

    dashboard_dir = project_root / "agentic_core" / "L6_observability" / "dashboards"

    required_files = [
        "autonomy_dashboard.html",
        "js/controllers/meta-learning-controller.js",
        "js/components/meta-learning-panel.js",
        "js/components/redis-monitor.js",
        "js/components/pinecone-monitor.js",
        "js/components/execution-flow.js",
        "css/meta-learning.css",
    ]

    for file_path in required_files:
        full_path = dashboard_dir / file_path
        record_test(f"{file_path} exists", full_path.exists())


def test_runtime_state_schema():
    """Test 3.4: Runtime state schema is correct."""
    print("\n--- Test 3.4: Runtime State schema ---")

    try:
        # ARCHIVED: canon_validator import removed # _runtime_state

        required_fields = [
            "status",
            "start_time",
            "end_time",
            "current_agent",
            "current_layer",
            "agents_order",
            "total_agents",
            "completed_agents",
            "events",
            "meta_learning",
            "redis",
            "pinecone",
            "execution_timeline",
        ]

        for field in required_fields:
            record_test(f"Runtime state has '{field}'", field in _runtime_state)

        # Check nested structures
        record_test(
            "meta_learning has strategy_weights",
            "strategy_weights" in _runtime_state.get("meta_learning", {}),
        )
        record_test("redis has operations", "operations" in _runtime_state.get("redis", {}))
        record_test(
            "pinecone has vectors_stored", "vectors_stored" in _runtime_state.get("pinecone", {})
        )

    except ImportError as e:
        record_test("Import runtime state", False, str(e))


# =============================================================================
# SECTION 4: DOCUMENTATION CROSS-REFERENCE TESTS
# =============================================================================


def test_doc_cross_references():
    """Test 4.1: Documentation files reference each other."""
    print("\n" + "=" * 70)
    print("Section 4: Documentation Cross-Reference Tests")
    print("=" * 70)
    print("\n--- Test 4.1: Cross-References ---")

    user_doc = project_root / "docs" / "DASHBOARD_META_LEARNING_GUIDE.md"
    dev_doc = project_root / "docs" / "META_LEARNING_TELEMETRY_API.md"

    if user_doc.exists():
        user_content = user_doc.read_text(encoding="utf-8")
        record_test("User doc references dev doc", "META_LEARNING_TELEMETRY_API" in user_content)
    else:
        record_test("User doc references dev doc", False, "User doc not found")

    if dev_doc.exists():
        dev_content = dev_doc.read_text(encoding="utf-8")
        record_test("Dev doc references user doc", "DASHBOARD_META_LEARNING_GUIDE" in dev_content)
    else:
        record_test("Dev doc references user doc", False, "Dev doc not found")


def test_doc_version_info():
    """Test 4.2: Documentation has version information."""
    print("\n--- Test 4.2: Version Information ---")

    docs = [
        ("User doc", project_root / "docs" / "DASHBOARD_META_LEARNING_GUIDE.md"),
        ("Dev doc", project_root / "docs" / "META_LEARNING_TELEMETRY_API.md"),
    ]

    for name, path in docs:
        if path.exists():
            content = path.read_text(encoding="utf-8")
            has_version = "Version" in content or "version" in content
            has_date = "2026" in content or "Updated" in content
            record_test(f"{name} has version info", has_version)
            record_test(f"{name} has date info", has_date)
        else:
            record_test(f"{name} has version info", False, "File not found")


def test_doc_table_of_contents():
    """Test 4.3: Documentation has table of contents."""
    print("\n--- Test 4.3: Table of Contents ---")

    docs = [
        ("User doc", project_root / "docs" / "DASHBOARD_META_LEARNING_GUIDE.md"),
        ("Dev doc", project_root / "docs" / "META_LEARNING_TELEMETRY_API.md"),
    ]

    for name, path in docs:
        if path.exists():
            content = path.read_text(encoding="utf-8")
            has_toc = "Table of Contents" in content or "## Contents" in content
            has_links = content.count("](#") >= 3  # Internal links
            record_test(f"{name} has table of contents", has_toc)
            record_test(
                f"{name} has internal links", has_links, f"Found {content.count('](#')} links"
            )
        else:
            record_test(f"{name} has table of contents", False, "File not found")


# =============================================================================
# SECTION 5: API DOCUMENTATION ACCURACY TESTS
# =============================================================================


def test_api_doc_accuracy():
    """Test 5.1: API documentation matches actual endpoints."""
    print("\n" + "=" * 70)
    print("Section 5: API Documentation Accuracy Tests")
    print("=" * 70)
    print("\n--- Test 5.1: API Endpoint Accuracy ---")

    try:
        client = TestClient(app)

        # Test documented endpoints actually work
        documented_endpoints = [
            ("/api/health", 200),
            ("/api/runtime/state", 200),
            ("/api/meta-learning/statistics", 200),
            ("/api/meta-learning/activity", 200),
            ("/api/redis/stats", 200),
            ("/api/redis/logs", 200),
            ("/api/pinecone/stats", 200),
            ("/api/execution/timeline", 200),
            ("/api/metrics/latency", 200),
        ]

        for endpoint, expected_status in documented_endpoints:
            response = client.get(endpoint)
            record_test(
                f"{endpoint} returns {expected_status}",
                response.status_code == expected_status,
                f"Got {response.status_code}",
            )

        # Test POST endpoint
        response = client.post(
            "/api/meta-learning/experience",
            json={"thought_type": "cot", "reward": 0.9, "state": {}, "outcome": {}},
        )
        record_test(
            "POST /api/meta-learning/experience works",
            response.status_code == 200,
            f"Got {response.status_code}",
        )

    except ImportError as e:
        record_test("API endpoint accuracy", False, str(e))


def test_response_schema_accuracy():
    """Test 5.2: API response schemas match documentation."""
    print("\n--- Test 5.2: Response schema Accuracy ---")

    try:
        client = TestClient(app)

        # Test meta-learning statistics response
        response = client.get("/api/meta-learning/statistics")
        data = response.json()
        record_test("Statistics has total_experiences", "total_experiences" in data)
        record_test("Statistics has strategy_weights", "strategy_weights" in data)

        # Test Redis stats response
        response = client.get("/api/redis/stats")
        data = response.json()
        record_test("Redis stats has operations", "operations" in data)
        record_test("Redis stats has hit_rate", "hit_rate" in data)

        # Test Pinecone stats response
        response = client.get("/api/pinecone/stats")
        data = response.json()
        record_test("Pinecone stats has vectors_stored", "vectors_stored" in data)
        record_test("Pinecone stats has operations", "operations" in data)

    except ImportError as e:
        record_test("Response schema accuracy", False, str(e))


# =============================================================================
# MAIN
# =============================================================================


def main():
    """Run all Phase 7 documentation tests."""
    print("=" * 70)
    print("PHASE 7: DOCUMENTATION AND DEPLOYMENT")
    print("Dashboard Live Runtime Meta-Learning Implementation")
    print("=" * 70)

    # Section 1: User Documentation
    user_content = test_user_doc_exists()
    test_user_doc_structure(user_content)
    test_user_doc_content(user_content)
    test_user_doc_commands(user_content)

    # Section 2: Developer Documentation
    dev_content = test_dev_doc_exists()
    test_dev_doc_structure(dev_content)
    test_dev_doc_api_endpoints(dev_content)
    test_dev_doc_schemas(dev_content)
    test_dev_doc_code_examples(dev_content)

    # Section 3: Deployment configuration
    test_deployment_scripts()
    test_api_module()
    test_dashboard_files()
    test_runtime_state_schema()

    # Section 4: Documentation Cross-References
    test_doc_cross_references()
    test_doc_version_info()
    test_doc_table_of_contents()

    # Section 5: API Documentation Accuracy
    test_api_doc_accuracy()
    test_response_schema_accuracy()

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    total = test_results["passed"] + test_results["failed"] + test_results["skipped"]
    print(f"  Total Tests: {total}")
    print(f"  Passed: {test_results['passed']}")
    print(f"  Failed: {test_results['failed']}")
    print(f"  Skipped: {test_results['skipped']}")

    if test_results["failed"] == 0:
        print("\n✅ ALL TESTS PASSED - Phase 7 documentation complete!")
        return 0
    else:
        print(f"\n❌ {test_results['failed']} TEST(S) FAILED")
        print("\nFailed tests:")
        for test in test_results["tests"]:
            if test["status"] == "FAILED":
                print(f"  - {test['name']}: {test['details']}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
