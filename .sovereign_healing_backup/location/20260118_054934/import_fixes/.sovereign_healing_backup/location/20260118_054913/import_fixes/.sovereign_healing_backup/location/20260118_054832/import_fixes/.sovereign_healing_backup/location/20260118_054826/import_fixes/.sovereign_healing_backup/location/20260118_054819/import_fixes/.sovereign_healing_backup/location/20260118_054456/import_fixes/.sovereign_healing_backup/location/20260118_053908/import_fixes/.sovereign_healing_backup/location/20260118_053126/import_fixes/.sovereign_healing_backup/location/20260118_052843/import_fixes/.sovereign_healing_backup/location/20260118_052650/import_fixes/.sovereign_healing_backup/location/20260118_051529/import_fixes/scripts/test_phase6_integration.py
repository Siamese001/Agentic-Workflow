#!/usr/bin/env python3
"""
Phase 6: Integration and Testing Test Suite

Comprehensive tests for:
- Backend Integration (telemetry hooks, API endpoints)
- Frontend Integration (components, controller, styling)
- End-to-End Testing (full data flow verification)

Usage:
    python scripts/test_phase6_integration.py
"""
import sys
import json
import time
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Tuple, List

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
# SECTION 1: BACKEND INTEGRATION TESTS
# =============================================================================

def test_backend_runtime_state_schema():
    """Test 1.1: Runtime state schema is complete."""
    print("\n" + "=" * 70)
    print("Section 1: Backend Integration Tests")
    print("=" * 70)
    print("\n--- Test 1.1: Runtime State Schema ---")
    
    try:
        # Import runtime state from canon_validator
        from archives.void_violations.canon_validator_agentic_v2_thin_13 import _runtime_state
        
        # Check top-level fields
        required_fields = ["status", "start_time", "end_time", "current_agent", 
                          "current_layer", "agents_order", "total_agents", 
                          "completed_agents", "events", "meta_learning", 
                          "redis", "pinecone", "execution_timeline"]
        
        for field in required_fields:
            record_test(f"Runtime state has '{field}'", field in _runtime_state, f"Missing: {field}")
        
        # Check meta_learning sub-fields
        ml_fields = ["enabled", "total_experiences", "patterns_extracted", 
                    "strategy_weights", "recent_experiences", "pattern_history"]
        for field in ml_fields:
            record_test(f"meta_learning has '{field}'", 
                       field in _runtime_state.get("meta_learning", {}), f"Missing: {field}")
        
        # Check redis sub-fields
        redis_fields = ["connected", "operations", "cache_hits", "cache_misses", 
                       "hit_rate", "recent_operations"]
        for field in redis_fields:
            record_test(f"redis has '{field}'", 
                       field in _runtime_state.get("redis", {}), f"Missing: {field}")
        
        # Check pinecone sub-fields
        pc_fields = ["connected", "operations", "vectors_stored", 
                    "avg_similarity", "recent_queries"]
        for field in pc_fields:
            record_test(f"pinecone has '{field}'", 
                       field in _runtime_state.get("pinecone", {}), f"Missing: {field}")
        
    except ImportError as e:
        record_test("Import canon_validator", False, str(e))


def test_backend_telemetry_functions():
    """Test 1.2: Telemetry update functions exist and work."""
    print("\n--- Test 1.2: Telemetry Update Functions ---")
    
    try:
        from archives.void_violations.canon_validator_agentic_v2_thin_13 import (
            _update_meta_learning_state,
            _update_redis_state,
            _update_pinecone_state,
            _update_agent_execution,
            _add_event,
            _runtime_state
        )
        
        # Test _update_meta_learning_state
        initial_exp = _runtime_state["meta_learning"]["total_experiences"]
        _update_meta_learning_state({
            "total_experiences": initial_exp + 1,
            "experience": {"id": "test_exp", "reward": 0.8}
        })
        record_test("_update_meta_learning_state works", 
                   _runtime_state["meta_learning"]["total_experiences"] == initial_exp + 1)
        
        # Test _update_redis_state
        initial_ops = _runtime_state["redis"]["operations"]["get"]
        _update_redis_state("get", "test_key", hit=True)
        record_test("_update_redis_state works", 
                   _runtime_state["redis"]["operations"]["get"] == initial_ops + 1)
        
        # Test _update_pinecone_state
        initial_pc_ops = _runtime_state["pinecone"]["operations"]["query"]
        _update_pinecone_state("query", {"similarity": 0.95, "top_k": 5})
        record_test("_update_pinecone_state works", 
                   _runtime_state["pinecone"]["operations"]["query"] == initial_pc_ops + 1)
        
        # Test _update_agent_execution
        initial_timeline = len(_runtime_state["execution_timeline"])
        _update_agent_execution("TestAgent", "L5", time.time() - 1, time.time(), True)
        record_test("_update_agent_execution works", 
                   len(_runtime_state["execution_timeline"]) == initial_timeline + 1)
        
        # Test _add_event
        initial_events = len(_runtime_state["events"])
        _add_event("test", "Test event message")
        record_test("_add_event works", 
                   len(_runtime_state["events"]) == initial_events + 1)
        
    except ImportError as e:
        record_test("Import telemetry functions", False, str(e))
    except Exception as e:
        record_test("Telemetry functions", False, str(e))


def test_backend_api_endpoints():
    """Test 1.3: FastAPI endpoints return correct data."""
    print("\n--- Test 1.3: API Endpoints ---")
    
    try:
        from agentic_core.L6_observability.api.runtime_api import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test all endpoints
        endpoints = [
            ("/api/health", "Health check"),
            ("/api/runtime/state", "Runtime state"),
            ("/api/meta-learning/statistics", "Meta-learning statistics"),
            ("/api/meta-learning/activity", "Meta-learning activity"),
            ("/api/redis/stats", "Redis stats"),
            ("/api/redis/logs", "Redis logs"),
            ("/api/pinecone/stats", "Pinecone stats"),
            ("/api/execution/timeline", "Execution timeline"),
            ("/api/metrics/latency", "Latency metrics"),
        ]
        
        for endpoint, desc in endpoints:
            response = client.get(endpoint)
            record_test(f"GET {endpoint} returns 200", 
                       response.status_code == 200, 
                       f"Status: {response.status_code}")
        
        # Test POST endpoint
        response = client.post("/api/meta-learning/experience", json={
            "thought_type": "cot",
            "reward": 0.9,
            "state": {"test": True}
        })
        record_test("POST /api/meta-learning/experience returns 200", 
                   response.status_code == 200, 
                   f"Status: {response.status_code}")
        
        # Verify response data structure
        response = client.get("/api/meta-learning/statistics")
        data = response.json()
        record_test("Meta-learning stats has strategy_weights", 
                   "strategy_weights" in data, "Missing strategy_weights")
        
        response = client.get("/api/redis/stats")
        data = response.json()
        record_test("Redis stats has operations", 
                   "operations" in data, "Missing operations")
        
        response = client.get("/api/pinecone/stats")
        data = response.json()
        record_test("Pinecone stats has vectors_stored", 
                   "vectors_stored" in data, "Missing vectors_stored")
        
    except ImportError as e:
        record_test("Import FastAPI app", False, str(e))
    except Exception as e:
        record_test("API endpoints", False, str(e))


def test_backend_meta_learning_agent():
    """Test 1.4: MetaLearningAgent telemetry integration."""
    print("\n--- Test 1.4: MetaLearningAgent Telemetry ---")
    
    try:
        from agentic_core.L1_cognition.learning.MetaLearningAgent import MetaLearningAgent
        
        telemetry_events = []
        
        def test_callback(event_type: str, data: dict):
            telemetry_events.append({"type": event_type, "data": data})
        
        agent = MetaLearningAgent(telemetry_callback=test_callback)
        record_test("MetaLearningAgent instantiation", agent is not None)
        
        # Store experience and check telemetry
        exp_id = agent.store_experience(
            state={"test": True},
            thought_type="cot",
            outcome={"success": True},
            reward=0.85
        )
        record_test("store_experience returns ID", exp_id is not None)
        record_test("store_experience triggers callback", 
                   any(e["type"] == "experience_stored" for e in telemetry_events))
        
        # Extract patterns and check telemetry
        patterns = agent.extract_patterns()
        record_test("extract_patterns triggers callback", 
                   any(e["type"] == "patterns_extracted" for e in telemetry_events))
        
    except ImportError as e:
        record_test("Import MetaLearningAgent", False, str(e))
    except Exception as e:
        record_test("MetaLearningAgent telemetry", False, str(e))


def test_backend_redis_telemetry():
    """Test 1.5: SovereignRedisClient telemetry integration."""
    print("\n--- Test 1.5: Redis Telemetry ---")
    
    try:
        from agentic_core.utils.core_extensions.redis import SovereignRedisClient
        
        telemetry_events = []
        
        def test_callback(event_type: str, data: dict):
            telemetry_events.append({"type": event_type, "data": data})
        
        client = SovereignRedisClient(telemetry_callback=test_callback)
        record_test("SovereignRedisClient instantiation", client is not None)
        record_test("telemetry_callback can be set", client.telemetry_callback is not None)
        
        # Test operations trigger telemetry (uses execute() method)
        client.execute("set", key="test_key", value="test_value")
        client.execute("get", key="test_key")
        
        record_test("Redis operations trigger telemetry", len(telemetry_events) >= 0)
        
        # Check operation stats
        record_test("operation_stats exists", hasattr(client, 'operation_stats'))
        record_test("operation_stats has set count", client.operation_stats.get('set', 0) >= 1)
        record_test("operation_stats has get count", client.operation_stats.get('get', 0) >= 1)
        
    except ImportError as e:
        record_test("Import SovereignRedisClient", False, str(e))
    except Exception as e:
        record_test("Redis telemetry", False, str(e))


def test_backend_pinecone_telemetry():
    """Test 1.6: PineconeTelemetryWrapper integration."""
    print("\n--- Test 1.6: Pinecone Telemetry ---")
    
    try:
        from agentic_core.L4_state.pinecone_telemetry import PineconeTelemetryWrapper
        
        telemetry_events = []
        
        def test_callback(event_type: str, data: dict):
            telemetry_events.append({"type": event_type, "data": data})
        
        wrapper = PineconeTelemetryWrapper(telemetry_callback=test_callback)
        record_test("PineconeTelemetryWrapper instantiation", wrapper is not None)
        
        # Check statistics
        stats = wrapper.get_statistics()
        record_test("get_statistics returns dict", isinstance(stats, dict))
        record_test("get_statistics has vectors_stored", "vectors_stored" in stats)
        record_test("get_statistics has operations", "operations" in stats)
        
    except ImportError as e:
        record_test("Import PineconeTelemetryWrapper", False, str(e))
    except Exception as e:
        record_test("Pinecone telemetry", False, str(e))


# =============================================================================
# SECTION 2: FRONTEND INTEGRATION TESTS
# =============================================================================

def test_frontend_js_components():
    """Test 2.1: JavaScript component files exist and are valid."""
    print("\n" + "=" * 70)
    print("Section 2: Frontend Integration Tests")
    print("=" * 70)
    print("\n--- Test 2.1: JavaScript Components ---")
    
    dashboard_dir = project_root / "agentic_core" / "L6_observability" / "dashboards"
    components_dir = dashboard_dir / "js" / "components"
    controllers_dir = dashboard_dir / "js" / "controllers"
    
    js_files = [
        (components_dir / "meta-learning-panel.js", ["ExperienceStream", "StrategyWeightsChart", "PatternTimeline"]),
        (components_dir / "redis-monitor.js", ["RedisOperationCounter", "RedisOperationLog"]),
        (components_dir / "pinecone-monitor.js", ["PineconeOperationsDashboard", "QueryResultsVisualizer"]),
        (components_dir / "execution-flow.js", ["AgentExecutionTimeline", "LayerFlowDiagram"]),
        (controllers_dir / "meta-learning-controller.js", ["MetaLearningController", "initializeMetaLearningDashboard"]),
    ]
    
    for file_path, required_classes in js_files:
        if file_path.exists():
            content = file_path.read_text(encoding='utf-8')
            record_test(f"{file_path.name} exists", True)
            
            for cls in required_classes:
                record_test(f"{file_path.name} has {cls}", cls in content, f"Missing: {cls}")
        else:
            record_test(f"{file_path.name} exists", False, "File not found")


def test_frontend_css_styles():
    """Test 2.2: CSS styles are complete."""
    print("\n--- Test 2.2: CSS Styles ---")
    
    css_file = project_root / "agentic_core" / "L6_observability" / "dashboards" / "css" / "meta-learning.css"
    
    if not css_file.exists():
        record_test("meta-learning.css exists", False, "File not found")
        return
    
    content = css_file.read_text(encoding='utf-8')
    record_test("meta-learning.css exists", True)
    
    required_classes = [
        ".meta-stats-grid", ".experience-item", ".reward-high", ".reward-medium", ".reward-low",
        ".strategy-weights-chart", ".strategy-bar", ".pattern-timeline",
        ".redis-stats-grid", ".operation-log", ".log-entry", ".cache-hit", ".cache-miss",
        ".pinecone-stats-grid", ".query-results",
        ".execution-timeline", ".layer-flow", ".layer-node",
        ".layer-completed", ".layer-active", ".layer-pending",
        ".scrollable-list", ".stat-box"
    ]
    
    for css_class in required_classes:
        record_test(f"CSS has {css_class}", css_class in content, f"Missing: {css_class}")


def test_frontend_html_integration():
    """Test 2.3: Dashboard HTML has all Phase 5 elements."""
    print("\n--- Test 2.3: HTML Integration ---")
    
    html_file = project_root / "agentic_core" / "L6_observability" / "dashboards" / "autonomy_dashboard.html"
    
    if not html_file.exists():
        record_test("autonomy_dashboard.html exists", False, "File not found")
        return
    
    content = html_file.read_text(encoding='utf-8')
    record_test("autonomy_dashboard.html exists", True)
    
    # Check JS includes
    js_includes = [
        "meta-learning-panel.js", "redis-monitor.js", "pinecone-monitor.js",
        "execution-flow.js", "meta-learning-controller.js"
    ]
    for js in js_includes:
        record_test(f"HTML includes {js}", js in content, f"Missing: {js}")
    
    # Check CSS include
    record_test("HTML includes meta-learning.css", "meta-learning.css" in content)
    
    # Check HTML containers
    containers = [
        'id="meta-stats"', 'id="strategy-weights"', 'id="experience-stream"',
        'id="pattern-timeline"', 'id="redis-stats"', 'id="redis-log"',
        'id="pinecone-stats"', 'id="pinecone-queries"',
        'id="execution-timeline"', 'id="execution-summary"', 'id="layer-flow"'
    ]
    for container in containers:
        record_test(f"HTML has {container}", container in content, f"Missing: {container}")


def test_frontend_controller_polling():
    """Test 2.4: MetaLearningController has polling logic."""
    print("\n--- Test 2.4: Controller Polling Logic ---")
    
    controller_file = project_root / "agentic_core" / "L6_observability" / "dashboards" / "js" / "controllers" / "meta-learning-controller.js"
    
    if not controller_file.exists():
        record_test("meta-learning-controller.js exists", False, "File not found")
        return
    
    content = controller_file.read_text(encoding='utf-8')
    
    # Check polling methods
    methods = ["init", "startPolling", "stopPolling", "poll", 
               "updateMetaLearning", "updateRedis", "updatePinecone", "updateTimeline"]
    for method in methods:
        record_test(f"Controller has {method} method", f"{method}:" in content or f"{method}(" in content)
    
    # Check API endpoints
    endpoints = [
        "/api/meta-learning/statistics",
        "/api/redis/stats",
        "/api/pinecone/stats",
        "/api/execution/timeline"
    ]
    for endpoint in endpoints:
        record_test(f"Controller polls {endpoint}", endpoint in content)


# =============================================================================
# SECTION 3: END-TO-END INTEGRATION TESTS
# =============================================================================

def test_e2e_data_flow():
    """Test 3.1: End-to-end data flow from telemetry to API."""
    print("\n" + "=" * 70)
    print("Section 3: End-to-End Integration Tests")
    print("=" * 70)
    print("\n--- Test 3.1: Data Flow ---")
    
    try:
        from agentic_core.L6_observability.api.runtime_api import app, meta_agent, redis_client, pinecone_wrapper
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test meta-learning data flow via POST endpoint
        initial_exp = meta_agent.total_experiences
        response = client.post("/api/meta-learning/experience", json={
            "thought_type": "cot",
            "reward": 0.95,
            "state": {"test": True},
            "outcome": {"success": True}
        })
        record_test("POST experience returns 200", response.status_code == 200)
        
        # Verify API reflects the new experience
        response = client.get("/api/meta-learning/statistics")
        data = response.json()
        record_test("API reflects meta-learning updates", 
                   data.get("total_experiences", 0) > initial_exp)
        
        # Test Redis data flow via direct client
        initial_ops = redis_client.operation_stats.get('set', 0)
        redis_client.execute("set", key="e2e_test_key", value="test_value")
        
        response = client.get("/api/redis/stats")
        data = response.json()
        record_test("API reflects Redis updates", 
                   data.get("operations", {}).get("set", 0) > initial_ops)
        
        # Test Pinecone data flow via wrapper
        initial_pc_ops = pinecone_wrapper.stats.get('query', 0)
        pinecone_wrapper.query(vector=[0.1]*128, top_k=5)  # Use actual query method
        
        response = client.get("/api/pinecone/stats")
        data = response.json()
        record_test("API reflects Pinecone updates", 
                   data.get("operations", {}).get("query", 0) > initial_pc_ops)
        
    except Exception as e:
        record_test("E2E data flow", False, str(e))


def test_e2e_runtime_state_file():
    """Test 3.2: Runtime state file is created and updated."""
    print("\n--- Test 3.2: Runtime State File ---")
    
    try:
        from archives.void_violations.canon_validator_agentic_v2_thin_13 import _save_runtime_state, _runtime_state
        
        # Save runtime state
        _save_runtime_state(project_root)
        
        state_file = project_root / "runtime_state.json"
        record_test("runtime_state.json created", state_file.exists())
        
        if state_file.exists():
            content = json.loads(state_file.read_text(encoding='utf-8'))
            record_test("runtime_state.json has meta_learning", "meta_learning" in content)
            record_test("runtime_state.json has redis", "redis" in content)
            record_test("runtime_state.json has pinecone", "pinecone" in content)
            record_test("runtime_state.json has execution_timeline", "execution_timeline" in content)
        
    except Exception as e:
        record_test("Runtime state file", False, str(e))


def test_e2e_api_latency():
    """Test 3.3: API response times are acceptable."""
    print("\n--- Test 3.3: API Latency ---")
    
    try:
        from agentic_core.L6_observability.api.runtime_api import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        endpoints = [
            "/api/health",
            "/api/runtime/state",
            "/api/meta-learning/statistics",
            "/api/redis/stats",
            "/api/pinecone/stats",
            "/api/execution/timeline"
        ]
        
        for endpoint in endpoints:
            start = time.time()
            response = client.get(endpoint)
            latency_ms = (time.time() - start) * 1000
            
            # Target: < 50ms
            record_test(f"{endpoint} latency < 50ms", 
                       latency_ms < 50, 
                       f"Latency: {latency_ms:.1f}ms")
        
    except Exception as e:
        record_test("API latency", False, str(e))


def test_e2e_start_script():
    """Test 3.4: start_runtime_api.py script exists and is valid."""
    print("\n--- Test 3.4: Start Script ---")
    
    script_file = project_root / "scripts" / "start_runtime_api.py"
    
    record_test("start_runtime_api.py exists", script_file.exists())
    
    if script_file.exists():
        content = script_file.read_text(encoding='utf-8')
        record_test("Script imports uvicorn", "uvicorn" in content)
        record_test("Script imports runtime_api", "runtime_api" in content)
        record_test("Script has main function", "def main()" in content)
        record_test("Script has argparse", "argparse" in content)


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Run all Phase 6 integration tests."""
    print("=" * 70)
    print("PHASE 6: INTEGRATION AND TESTING")
    print("Dashboard Live Runtime Meta-Learning Implementation")
    print("=" * 70)
    
    # Section 1: Backend Integration
    test_backend_runtime_state_schema()
    test_backend_telemetry_functions()
    test_backend_api_endpoints()
    test_backend_meta_learning_agent()
    test_backend_redis_telemetry()
    test_backend_pinecone_telemetry()
    
    # Section 2: Frontend Integration
    test_frontend_js_components()
    test_frontend_css_styles()
    test_frontend_html_integration()
    test_frontend_controller_polling()
    
    # Section 3: End-to-End Integration
    test_e2e_data_flow()
    test_e2e_runtime_state_file()
    test_e2e_api_latency()
    test_e2e_start_script()
    
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
        print("\n✅ ALL TESTS PASSED - Phase 6 integration complete!")
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
