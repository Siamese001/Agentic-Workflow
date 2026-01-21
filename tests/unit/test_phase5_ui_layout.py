#!/usr/bin/env python3
"""
Test Suite for Phase 5 - UI Layout and Styling

Tests:
- Phase 5.1: HTML structure in Runtime Tab
- Phase 5.2: JS/CSS file includes
- Phase 5.3: Initialization on page load
- Phase 5.4: CSS styling completeness
- Phase 5.5: Integration with existing dashboard
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Test results tracking
test_results = {"passed": 0, "failed": 0, "tests": []}

# Dashboard paths
DASHBOARD_DIR = project_root / "agentic_core" / "L6_observability" / "dashboards"
DASHBOARD_HTML = DASHBOARD_DIR / "autonomy_dashboard.html"
JS_DIR = DASHBOARD_DIR / "js"
CSS_DIR = DASHBOARD_DIR / "css"
COMPONENTS_DIR = JS_DIR / "components"
CONTROLLERS_DIR = JS_DIR / "controllers"


def record_test(name: str, passed: bool, details: str = ""):
    """Record test result."""
    status = "PASSED" if passed else "FAILED"
    test_results["tests"].append({"name": name, "status": status, "details": details})
    if passed:
        test_results["passed"] += 1
        print(f"  ✅ {name}")
    else:
        test_results["failed"] += 1
        print(f"  ❌ {name}: {details}")


def test_phase5_1_html_structure():
    """Test Phase 5.1: HTML structure in Runtime Tab."""
    print("\n" + "=" * 70)
    print("Phase 5.1: HTML Structure in Runtime Tab")
    print("=" * 70)

    if not DASHBOARD_HTML.exists():
        record_test("Dashboard HTML exists", False, f"File not found: {DASHBOARD_HTML}")
        return

    html = DASHBOARD_HTML.read_text(encoding="utf-8")

    # Test Meta-Learning section
    meta_learning_elements = [
        ('id="meta-stats"', "Meta-Learning Stats container"),
        ('id="strategy-weights"', "Strategy Weights container"),
        ('id="experience-stream"', "Experience Stream container"),
        ('id="pattern-timeline"', "Pattern Timeline container"),
    ]

    for pattern, desc in meta_learning_elements:
        record_test(f"Meta-Learning: {desc}", pattern in html, f"Missing: {pattern}")

    # Test Redis section
    redis_elements = [
        ('id="redis-stats"', "Redis Stats container"),
        ('id="redis-log"', "Redis Log container"),
    ]

    for pattern, desc in redis_elements:
        record_test(f"Redis: {desc}", pattern in html, f"Missing: {pattern}")

    # Test Pinecone section
    pinecone_elements = [
        ('id="pinecone-stats"', "Pinecone Stats container"),
        ('id="pinecone-queries"', "Pinecone Queries container"),
    ]

    for pattern, desc in pinecone_elements:
        record_test(f"Pinecone: {desc}", pattern in html, f"Missing: {pattern}")

    # Test Execution Flow section
    execution_elements = [
        ('id="execution-timeline"', "Execution Timeline container"),
        ('id="execution-summary"', "Execution Summary container"),
        ('id="layer-flow"', "Layer Flow container"),
    ]

    for pattern, desc in execution_elements:
        record_test(f"Execution: {desc}", pattern in html, f"Missing: {pattern}")

    # Test section headers
    section_headers = [
        ("Meta-Learning Activity", "Meta-Learning section header"),
        ("Redis Cache Activity", "Redis section header"),
        ("Pinecone Vector Operations", "Pinecone section header"),
        ("Agent Execution Flow", "Execution Flow section header"),
    ]

    for header, desc in section_headers:
        record_test(f"Header: {desc}", header in html, f"Missing: {header}")


def test_phase5_2_file_includes():
    """Test Phase 5.2: JS/CSS file includes."""
    print("\n" + "=" * 70)
    print("Phase 5.2: JS/CSS File Includes")
    print("=" * 70)

    if not DASHBOARD_HTML.exists():
        record_test("Dashboard HTML exists", False, f"File not found: {DASHBOARD_HTML}")
        return

    html = DASHBOARD_HTML.read_text(encoding="utf-8")

    # Test JS includes
    js_includes = [
        ("meta-learning-panel.js", "Meta-Learning Panel JS"),
        ("redis-monitor.js", "Redis Monitor JS"),
        ("pinecone-monitor.js", "Pinecone Monitor JS"),
        ("execution-flow.js", "Execution Flow JS"),
        ("meta-learning-controller.js", "Meta-Learning Controller JS"),
    ]

    for filename, desc in js_includes:
        record_test(f"JS include: {desc}", filename in html, f"Missing: {filename}")

    # Test CSS include
    record_test(
        "CSS include: meta-learning.css", "meta-learning.css" in html, "Missing: meta-learning.css"
    )

    # Test that files actually exist
    js_files = [
        (COMPONENTS_DIR / "meta-learning-panel.js", "Meta-Learning Panel JS file"),
        (COMPONENTS_DIR / "redis-monitor.js", "Redis Monitor JS file"),
        (COMPONENTS_DIR / "pinecone-monitor.js", "Pinecone Monitor JS file"),
        (COMPONENTS_DIR / "execution-flow.js", "Execution Flow JS file"),
        (CONTROLLERS_DIR / "meta-learning-controller.js", "Meta-Learning Controller JS file"),
        (CSS_DIR / "meta-learning.css", "Meta-Learning CSS file"),
    ]

    for file_path, desc in js_files:
        record_test(f"File exists: {desc}", file_path.exists(), f"Missing: {file_path}")


def test_phase5_3_initialization():
    """Test Phase 5.3: Initialization on page load."""
    print("\n" + "=" * 70)
    print("Phase 5.3: Initialization on Page Load")
    print("=" * 70)

    # Check main.js for initialization
    main_js = JS_DIR / "main.js"
    if not main_js.exists():
        record_test("main.js exists", False, f"File not found: {main_js}")
        return

    content = main_js.read_text(encoding="utf-8")

    record_test(
        "initializeMetaLearningDashboard called",
        "initializeMetaLearningDashboard" in content,
        "initializeMetaLearningDashboard not found in main.js",
    )

    # Check controller has init function
    controller_js = CONTROLLERS_DIR / "meta-learning-controller.js"
    if controller_js.exists():
        controller_content = controller_js.read_text(encoding="utf-8")

        record_test(
            "MetaLearningController has init method",
            "init:" in controller_content or "init(" in controller_content,
            "init method not found",
        )

        record_test(
            "initializeMetaLearningDashboard function defined",
            "function initializeMetaLearningDashboard" in controller_content,
            "initializeMetaLearningDashboard function not defined",
        )

        record_test(
            "MetaLearningController exported to window",
            "window.MetaLearningController" in controller_content,
            "MetaLearningController not exported",
        )


def test_phase5_4_css_completeness():
    """Test Phase 5.4: CSS styling completeness."""
    print("\n" + "=" * 70)
    print("Phase 5.4: CSS Styling Completeness")
    print("=" * 70)

    css_file = CSS_DIR / "meta-learning.css"
    if not css_file.exists():
        record_test("meta-learning.css exists", False, f"File not found: {css_file}")
        return

    content = css_file.read_text(encoding="utf-8")

    # Check for required CSS classes
    required_classes = [
        (".meta-stats-grid", "Meta stats grid layout"),
        (".experience-item", "Experience item styling"),
        (".reward-high", "High reward styling"),
        (".reward-medium", "Medium reward styling"),
        (".reward-low", "Low reward styling"),
        (".strategy-weights-chart", "Strategy weights chart"),
        (".strategy-bar", "Strategy bar styling"),
        (".pattern-timeline", "Pattern timeline styling"),
        (".redis-stats-grid", "Redis stats grid"),
        (".operation-log", "Operation log styling"),
        (".log-entry", "Log entry styling"),
        (".cache-hit", "Cache hit styling"),
        (".cache-miss", "Cache miss styling"),
        (".pinecone-stats-grid", "Pinecone stats grid"),
        (".query-results", "Query results styling"),
        (".execution-timeline", "Execution timeline styling"),
        (".layer-flow", "Layer flow diagram"),
        (".layer-node", "Layer node styling"),
        (".layer-completed", "Completed layer styling"),
        (".layer-active", "Active layer styling"),
        (".layer-pending", "Pending layer styling"),
        (".scrollable-list", "Scrollable list styling"),
        (".stat-box", "Stat box styling"),
        (".stat-label", "Stat label styling"),
        (".stat-value", "Stat value styling"),
    ]

    for css_class, desc in required_classes:
        record_test(f"CSS: {desc}", css_class in content, f"Missing: {css_class}")

    # Check for animations
    record_test(
        "CSS: Layer pulse animation", "@keyframes pulse" in content, "Missing pulse animation"
    )


def test_phase5_5_integration():
    """Test Phase 5.5: Integration with existing dashboard."""
    print("\n" + "=" * 70)
    print("Phase 5.5: Integration with Existing Dashboard")
    print("=" * 70)

    if not DASHBOARD_HTML.exists():
        record_test("Dashboard HTML exists", False, f"File not found: {DASHBOARD_HTML}")
        return

    html = DASHBOARD_HTML.read_text(encoding="utf-8")

    # Check Phase 5 sections are in runtime-content tab
    record_test(
        "Phase 5 sections in runtime-content tab",
        'id="runtime-content"' in html and "meta-learning-section" in html,
        "Phase 5 sections not in runtime-content tab",
    )

    # Check CSS is loaded before JS
    css_pos = html.find("meta-learning.css")
    js_pos = html.find("meta-learning-panel.js")
    record_test(
        "CSS loaded before JS",
        css_pos < js_pos if css_pos != -1 and js_pos != -1 else False,
        "CSS should be loaded before JS",
    )

    # Check components are loaded before controller
    panel_pos = html.find("meta-learning-panel.js")
    controller_pos = html.find("meta-learning-controller.js")
    record_test(
        "Components loaded before controller",
        panel_pos < controller_pos if panel_pos != -1 and controller_pos != -1 else False,
        "Components should be loaded before controller",
    )

    # Check main.js is loaded last
    main_pos = html.find("main.js")
    record_test(
        "main.js loaded after Phase 5 components",
        controller_pos < main_pos if controller_pos != -1 and main_pos != -1 else False,
        "main.js should be loaded after Phase 5 components",
    )


def test_api_integration():
    """Test API integration for Phase 5."""
    print("\n" + "=" * 70)
    print("API Integration Tests")
    print("=" * 70)

    try:
        from agentic_core.L6_observability.api.runtime_api import app
        from fastapi.testclient import TestClient

        client = TestClient(app)

        endpoints = [
            ("/api/meta-learning/statistics", "Meta-Learning Statistics"),
            ("/api/redis/stats", "Redis Stats"),
            ("/api/pinecone/stats", "Pinecone Stats"),
            ("/api/execution/timeline", "Execution Timeline"),
            ("/api/runtime/state", "Runtime State"),
        ]

        for endpoint, desc in endpoints:
            response = client.get(endpoint)
            record_test(
                f"API: {desc} returns 200",
                response.status_code == 200,
                f"Status: {response.status_code}",
            )

    except ImportError as e:
        record_test("Import FastAPI app", False, str(e))
    except Exception as e:
        record_test("API integration tests", False, str(e))


def main():
    """Run all Phase 5 tests."""
    print("\n" + "=" * 70)
    print("PHASE 5 UI LAYOUT & STYLING TEST SUITE")
    print("Dashboard Live Runtime Meta-Learning Implementation")
    print("=" * 70)

    # Run all test suites
    test_phase5_1_html_structure()
    test_phase5_2_file_includes()
    test_phase5_3_initialization()
    test_phase5_4_css_completeness()
    test_phase5_5_integration()
    test_api_integration()

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"  Total Tests: {test_results['passed'] + test_results['failed']}")
    print(f"  Passed: {test_results['passed']}")
    print(f"  Failed: {test_results['failed']}")

    if test_results["failed"] == 0:
        print("\n✅ ALL TESTS PASSED - Phase 5 implementation complete!")
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
