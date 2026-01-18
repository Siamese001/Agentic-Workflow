#!/usr/bin/env python3
"""
Test Suite for Phase 3 and Phase 4 - Dashboard Frontend Components

Tests:
- Phase 3.1: Meta-Learning Panel JavaScript components
- Phase 3.2: Redis Monitor JavaScript components
- Phase 3.3: Pinecone Monitor JavaScript components
- Phase 3.4: Execution Flow JavaScript components
- Phase 4.1: Meta-Learning Controller (polling)
- Phase 4.2: CSS styles existence and structure
- Integration: All components work together
"""

import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Test results tracking
test_results = {"passed": 0, "failed": 0, "tests": []}

# Dashboard paths
DASHBOARD_DIR = project_root / "agentic_core" / "L6_observability" / "dashboards"
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


def test_phase3_1_meta_learning_panel():
    """Test Phase 3.1: Meta-Learning Panel JavaScript components."""
    print("\n" + "=" * 70)
    print("Phase 3.1: Meta-Learning Panel Tests")
    print("=" * 70)
    
    # Test 1: File exists
    file_path = COMPONENTS_DIR / "meta-learning-panel.js"
    record_test(
        "meta-learning-panel.js exists",
        file_path.exists(),
        f"File not found: {file_path}"
    )
    
    if file_path.exists():
        content = file_path.read_text(encoding='utf-8')
        
        # Test 2: ExperienceStream class exists
        record_test(
            "ExperienceStream class defined",
            "class ExperienceStream" in content,
            "ExperienceStream class not found"
        )
        
        # Test 3: StrategyWeightsChart class exists
        record_test(
            "StrategyWeightsChart class defined",
            "class StrategyWeightsChart" in content,
            "StrategyWeightsChart class not found"
        )
        
        # Test 4: PatternTimeline class exists
        record_test(
            "PatternTimeline class defined",
            "class PatternTimeline" in content,
            "PatternTimeline class not found"
        )
        
        # Test 5: MetaLearningStatsPanel class exists
        record_test(
            "MetaLearningStatsPanel class defined",
            "class MetaLearningStatsPanel" in content,
            "MetaLearningStatsPanel class not found"
        )
        
        # Test 6: Classes are exported globally
        record_test(
            "Classes exported to window",
            "window.ExperienceStream" in content and "window.StrategyWeightsChart" in content,
            "Classes not exported to window"
        )
        
        # Test 7: ExperienceStream has required methods
        record_test(
            "ExperienceStream has addExperience method",
            "addExperience(" in content,
            "addExperience method not found"
        )
        
        record_test(
            "ExperienceStream has render method",
            "render()" in content,
            "render method not found"
        )
        
        # Test 8: StrategyWeightsChart has update method
        record_test(
            "StrategyWeightsChart has update method",
            "update(weights)" in content or "update(" in content,
            "update method not found"
        )
        
        # Test 9: Reward classification exists
        record_test(
            "Reward classification implemented",
            "getRewardClass" in content and "reward-high" in content,
            "Reward classification not found"
        )


def test_phase3_2_redis_monitor():
    """Test Phase 3.2: Redis Monitor JavaScript components."""
    print("\n" + "=" * 70)
    print("Phase 3.2: Redis Monitor Tests")
    print("=" * 70)
    
    # Test 1: File exists
    file_path = COMPONENTS_DIR / "redis-monitor.js"
    record_test(
        "redis-monitor.js exists",
        file_path.exists(),
        f"File not found: {file_path}"
    )
    
    if file_path.exists():
        content = file_path.read_text(encoding='utf-8')
        
        # Test 2: RedisOperationCounter class exists
        record_test(
            "RedisOperationCounter class defined",
            "class RedisOperationCounter" in content,
            "RedisOperationCounter class not found"
        )
        
        # Test 3: RedisOperationLog class exists
        record_test(
            "RedisOperationLog class defined",
            "class RedisOperationLog" in content,
            "RedisOperationLog class not found"
        )
        
        # Test 4: Classes are exported globally
        record_test(
            "Classes exported to window",
            "window.RedisOperationCounter" in content and "window.RedisOperationLog" in content,
            "Classes not exported to window"
        )
        
        # Test 5: Hit rate classification exists
        record_test(
            "Hit rate classification implemented",
            "getHitRateClass" in content and "hit-rate-excellent" in content,
            "Hit rate classification not found"
        )
        
        # Test 6: Operation log has setOperations method
        record_test(
            "RedisOperationLog has setOperations method",
            "setOperations(" in content,
            "setOperations method not found"
        )
        
        # Test 7: Cache hit/miss styling
        record_test(
            "Cache hit/miss styling implemented",
            "cache-hit" in content and "cache-miss" in content,
            "Cache hit/miss styling not found"
        )


def test_phase3_3_pinecone_monitor():
    """Test Phase 3.3: Pinecone Monitor JavaScript components."""
    print("\n" + "=" * 70)
    print("Phase 3.3: Pinecone Monitor Tests")
    print("=" * 70)
    
    # Test 1: File exists
    file_path = COMPONENTS_DIR / "pinecone-monitor.js"
    record_test(
        "pinecone-monitor.js exists",
        file_path.exists(),
        f"File not found: {file_path}"
    )
    
    if file_path.exists():
        content = file_path.read_text(encoding='utf-8')
        
        # Test 2: PineconeOperationsDashboard class exists
        record_test(
            "PineconeOperationsDashboard class defined",
            "class PineconeOperationsDashboard" in content,
            "PineconeOperationsDashboard class not found"
        )
        
        # Test 3: QueryResultsVisualizer class exists
        record_test(
            "QueryResultsVisualizer class defined",
            "class QueryResultsVisualizer" in content,
            "QueryResultsVisualizer class not found"
        )
        
        # Test 4: Classes are exported globally
        record_test(
            "Classes exported to window",
            "window.PineconeOperationsDashboard" in content and "window.QueryResultsVisualizer" in content,
            "Classes not exported to window"
        )
        
        # Test 5: Similarity classification exists
        record_test(
            "Similarity classification implemented",
            "getSimilarityClass" in content,
            "Similarity classification not found"
        )
        
        # Test 6: Query results rendering
        record_test(
            "Query results rendering implemented",
            "renderResults" in content or "query-results-list" in content,
            "Query results rendering not found"
        )


def test_phase3_4_execution_flow():
    """Test Phase 3.4: Execution Flow JavaScript components."""
    print("\n" + "=" * 70)
    print("Phase 3.4: Execution Flow Tests")
    print("=" * 70)
    
    # Test 1: File exists
    file_path = COMPONENTS_DIR / "execution-flow.js"
    record_test(
        "execution-flow.js exists",
        file_path.exists(),
        f"File not found: {file_path}"
    )
    
    if file_path.exists():
        content = file_path.read_text(encoding='utf-8')
        
        # Test 2: AgentExecutionTimeline class exists
        record_test(
            "AgentExecutionTimeline class defined",
            "class AgentExecutionTimeline" in content,
            "AgentExecutionTimeline class not found"
        )
        
        # Test 3: LayerFlowDiagram class exists
        record_test(
            "LayerFlowDiagram class defined",
            "class LayerFlowDiagram" in content,
            "LayerFlowDiagram class not found"
        )
        
        # Test 4: ExecutionSummaryPanel class exists
        record_test(
            "ExecutionSummaryPanel class defined",
            "class ExecutionSummaryPanel" in content,
            "ExecutionSummaryPanel class not found"
        )
        
        # Test 5: Classes are exported globally
        record_test(
            "Classes exported to window",
            "window.AgentExecutionTimeline" in content and "window.LayerFlowDiagram" in content,
            "Classes not exported to window"
        )
        
        # Test 6: Layer progression implemented
        record_test(
            "Layer progression implemented",
            "layer-completed" in content and "layer-active" in content and "layer-pending" in content,
            "Layer progression not found"
        )
        
        # Test 7: Timeline has addExecution method
        record_test(
            "AgentExecutionTimeline has addExecution method",
            "addExecution(" in content,
            "addExecution method not found"
        )


def test_phase4_1_meta_learning_controller():
    """Test Phase 4.1: Meta-Learning Controller."""
    print("\n" + "=" * 70)
    print("Phase 4.1: Meta-Learning Controller Tests")
    print("=" * 70)
    
    # Test 1: File exists
    file_path = CONTROLLERS_DIR / "meta-learning-controller.js"
    record_test(
        "meta-learning-controller.js exists",
        file_path.exists(),
        f"File not found: {file_path}"
    )
    
    if file_path.exists():
        content = file_path.read_text(encoding='utf-8')
        
        # Test 2: MetaLearningController object exists
        record_test(
            "MetaLearningController object defined",
            "MetaLearningController" in content,
            "MetaLearningController not found"
        )
        
        # Test 3: init method exists
        record_test(
            "init method defined",
            "init:" in content or "init(" in content,
            "init method not found"
        )
        
        # Test 4: startPolling method exists
        record_test(
            "startPolling method defined",
            "startPolling" in content,
            "startPolling method not found"
        )
        
        # Test 5: stopPolling method exists
        record_test(
            "stopPolling method defined",
            "stopPolling" in content,
            "stopPolling method not found"
        )
        
        # Test 6: poll method exists
        record_test(
            "poll method defined",
            "poll:" in content or "poll(" in content or "poll:" in content,
            "poll method not found"
        )
        
        # Test 7: API endpoints are called
        api_endpoints = [
            "/api/meta-learning/statistics",
            "/api/redis/stats",
            "/api/pinecone/stats",
            "/api/execution/timeline"
        ]
        for endpoint in api_endpoints:
            record_test(
                f"Polls {endpoint}",
                endpoint in content,
                f"Endpoint {endpoint} not polled"
            )
        
        # Test 8: Component initialization
        record_test(
            "initializeComponents method defined",
            "initializeComponents" in content,
            "initializeComponents method not found"
        )
        
        # Test 9: Update methods exist
        update_methods = ["updateMetaLearning", "updateRedis", "updatePinecone", "updateTimeline"]
        for method in update_methods:
            record_test(
                f"{method} method defined",
                method in content,
                f"{method} method not found"
            )
        
        # Test 10: Exported globally
        record_test(
            "MetaLearningController exported to window",
            "window.MetaLearningController" in content,
            "MetaLearningController not exported to window"
        )


def test_phase4_2_css_styles():
    """Test Phase 4.2: CSS styles."""
    print("\n" + "=" * 70)
    print("Phase 4.2: CSS Styles Tests")
    print("=" * 70)
    
    # Test 1: File exists
    file_path = CSS_DIR / "meta-learning.css"
    record_test(
        "meta-learning.css exists",
        file_path.exists(),
        f"File not found: {file_path}"
    )
    
    if file_path.exists():
        content = file_path.read_text(encoding='utf-8')
        
        # Test 2: Meta-learning styles exist
        record_test(
            "Meta-learning styles defined",
            ".meta-stats-grid" in content,
            "Meta-learning styles not found"
        )
        
        # Test 3: Experience stream styles exist
        record_test(
            "Experience stream styles defined",
            ".experience-item" in content and ".reward-high" in content,
            "Experience stream styles not found"
        )
        
        # Test 4: Strategy weights styles exist
        record_test(
            "Strategy weights styles defined",
            ".strategy-weights-chart" in content or ".strategy-bar" in content,
            "Strategy weights styles not found"
        )
        
        # Test 5: Redis styles exist
        record_test(
            "Redis styles defined",
            ".redis-stats-grid" in content,
            "Redis styles not found"
        )
        
        # Test 6: Operation log styles exist
        record_test(
            "Operation log styles defined",
            ".operation-log" in content and ".log-entry" in content,
            "Operation log styles not found"
        )
        
        # Test 7: Pinecone styles exist
        record_test(
            "Pinecone styles defined",
            ".pinecone-stats-grid" in content,
            "Pinecone styles not found"
        )
        
        # Test 8: Query results styles exist
        record_test(
            "Query results styles defined",
            ".query-results" in content or ".query-item" in content,
            "Query results styles not found"
        )
        
        # Test 9: Execution timeline styles exist
        record_test(
            "Execution timeline styles defined",
            ".execution-timeline" in content or ".timeline-row" in content,
            "Execution timeline styles not found"
        )
        
        # Test 10: Layer flow styles exist
        record_test(
            "Layer flow styles defined",
            ".layer-flow" in content and ".layer-node" in content,
            "Layer flow styles not found"
        )
        
        # Test 11: Status indicator styles exist
        record_test(
            "Status indicator styles defined",
            ".status-idle" in content or ".status-running" in content,
            "Status indicator styles not found"
        )


def test_integration_file_structure():
    """Test integration: All files exist in correct locations."""
    print("\n" + "=" * 70)
    print("Integration: File Structure Tests")
    print("=" * 70)
    
    # Test component files
    component_files = [
        "meta-learning-panel.js",
        "redis-monitor.js",
        "pinecone-monitor.js",
        "execution-flow.js"
    ]
    
    for filename in component_files:
        file_path = COMPONENTS_DIR / filename
        record_test(
            f"Component {filename} exists",
            file_path.exists(),
            f"File not found: {file_path}"
        )
    
    # Test controller files
    controller_files = [
        "meta-learning-controller.js",
        "runtime-controller.js"
    ]
    
    for filename in controller_files:
        file_path = CONTROLLERS_DIR / filename
        record_test(
            f"Controller {filename} exists",
            file_path.exists(),
            f"File not found: {file_path}"
        )
    
    # Test CSS files
    css_files = [
        "meta-learning.css"
    ]
    
    for filename in css_files:
        file_path = CSS_DIR / filename
        record_test(
            f"CSS {filename} exists",
            file_path.exists(),
            f"File not found: {file_path}"
        )


def test_api_integration():
    """Test that API endpoints are available."""
    print("\n" + "=" * 70)
    print("API Integration Tests")
    print("=" * 70)
    
    try:
        from agentic_core.L6_observability.api.runtime_api import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test endpoints that Phase 3/4 components depend on
        endpoints = [
            ("/api/meta-learning/statistics", "meta-learning statistics"),
            ("/api/redis/stats", "Redis stats"),
            ("/api/pinecone/stats", "Pinecone stats"),
            ("/api/execution/timeline", "execution timeline"),
            ("/api/runtime/state", "runtime state")
        ]
        
        for endpoint, name in endpoints:
            response = client.get(endpoint)
            record_test(
                f"API {name} endpoint returns 200",
                response.status_code == 200,
                f"Status: {response.status_code}"
            )
        
    except ImportError as e:
        record_test("Import FastAPI app", False, str(e))
    except Exception as e:
        record_test("API integration tests", False, str(e))


def main():
    """Run all Phase 3 and Phase 4 tests."""
    print("\n" + "=" * 70)
    print("PHASE 3 & PHASE 4 FRONTEND TEST SUITE")
    print("Dashboard Live Runtime Meta-Learning Implementation")
    print("=" * 70)
    
    # Run all test suites
    test_phase3_1_meta_learning_panel()
    test_phase3_2_redis_monitor()
    test_phase3_3_pinecone_monitor()
    test_phase3_4_execution_flow()
    test_phase4_1_meta_learning_controller()
    test_phase4_2_css_styles()
    test_integration_file_structure()
    test_api_integration()
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"  Total Tests: {test_results['passed'] + test_results['failed']}")
    print(f"  Passed: {test_results['passed']}")
    print(f"  Failed: {test_results['failed']}")
    
    if test_results['failed'] == 0:
        print("\n✅ ALL TESTS PASSED - Phase 3 & Phase 4 implementation complete!")
        return 0
    else:
        print(f"\n❌ {test_results['failed']} TEST(S) FAILED")
        print("\nFailed tests:")
        for test in test_results['tests']:
            if test['status'] == 'FAILED':
                print(f"  - {test['name']}: {test['details']}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
