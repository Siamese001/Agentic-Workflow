#!/usr/bin/env python3
"""
Test Suite for Phase 1 and Phase 2 - Dashboard Live Runtime Meta-Learning

Tests:
- Phase 1.1: Runtime state schema in canon_validator_agentic_v2_thin.py
- Phase 1.2: MetaLearningAgent telemetry callbacks
- Phase 1.3: SovereignRedisClient telemetry
- Phase 1.4: PineconeTelemetryWrapper
- Phase 2.1: FastAPI runtime API endpoints
- Phase 2.2: API response formats
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Test results tracking
test_results = {"passed": 0, "failed": 0, "tests": []}


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


def test_phase1_1_runtime_state_schema():
    """Test Phase 1.1: Extended runtime state schema."""
    print("\n" + "=" * 70)
    print("Phase 1.1: Runtime State Schema Tests")
    print("=" * 70)
    
    try:
        # Import the runtime state from canon_validator
        from archives.void_violations.canon_validator_agentic_v2_thin_21 import _runtime_state
        
        # Test 1: Basic fields exist
        basic_fields = ["status", "start_time", "end_time", "current_agent", 
                       "current_layer", "agents_order", "total_agents", 
                       "completed_agents", "events"]
        for field in basic_fields:
            record_test(
                f"Basic field '{field}' exists",
                field in _runtime_state,
                f"Missing field: {field}"
            )
        
        # Test 2: Meta-learning section exists and has correct structure
        record_test(
            "meta_learning section exists",
            "meta_learning" in _runtime_state,
            "Missing meta_learning section"
        )
        
        if "meta_learning" in _runtime_state:
            ml = _runtime_state["meta_learning"]
            ml_fields = ["enabled", "total_experiences", "patterns_extracted", 
                        "strategy_weights", "recent_experiences", "pattern_history"]
            for field in ml_fields:
                record_test(
                    f"meta_learning.{field} exists",
                    field in ml,
                    f"Missing field: meta_learning.{field}"
                )
            
            # Test strategy weights structure
            if "strategy_weights" in ml:
                strategies = ["cot", "tot", "react", "reflection"]
                for s in strategies:
                    record_test(
                        f"strategy_weights.{s} exists",
                        s in ml["strategy_weights"],
                        f"Missing strategy: {s}"
                    )
        
        # Test 3: Redis section exists and has correct structure
        record_test(
            "redis section exists",
            "redis" in _runtime_state,
            "Missing redis section"
        )
        
        if "redis" in _runtime_state:
            redis = _runtime_state["redis"]
            redis_fields = ["connected", "operations", "cache_hits", 
                          "cache_misses", "hit_rate", "recent_operations"]
            for field in redis_fields:
                record_test(
                    f"redis.{field} exists",
                    field in redis,
                    f"Missing field: redis.{field}"
                )
        
        # Test 4: Pinecone section exists and has correct structure
        record_test(
            "pinecone section exists",
            "pinecone" in _runtime_state,
            "Missing pinecone section"
        )
        
        if "pinecone" in _runtime_state:
            pc = _runtime_state["pinecone"]
            pc_fields = ["connected", "operations", "vectors_stored", 
                        "avg_similarity", "recent_queries"]
            for field in pc_fields:
                record_test(
                    f"pinecone.{field} exists",
                    field in pc,
                    f"Missing field: pinecone.{field}"
                )
        
        # Test 5: Execution timeline exists
        record_test(
            "execution_timeline exists",
            "execution_timeline" in _runtime_state,
            "Missing execution_timeline"
        )
        
    except ImportError as e:
        record_test("Import canon_validator_agentic_v2_thin", False, str(e))
    except Exception as e:
        record_test("Phase 1.1 tests", False, str(e))


def test_phase1_2_meta_learning_telemetry():
    """Test Phase 1.2: MetaLearningAgent telemetry callbacks."""
    print("\n" + "=" * 70)
    print("Phase 1.2: MetaLearningAgent Telemetry Tests")
    print("=" * 70)
    
    try:
        from agentic_core.L1_cognition.learning.MetaLearningAgent import MetaLearningAgent
        
        # Test 1: MetaLearningAgent can be instantiated
        agent = MetaLearningAgent()
        record_test("MetaLearningAgent instantiation", True)
        
        # Test 2: Telemetry callback parameter exists
        telemetry_events = []
        def capture_telemetry(event_type: str, data: dict):
            telemetry_events.append({"type": event_type, "data": data})
        
        agent_with_callback = MetaLearningAgent(telemetry_callback=capture_telemetry)
        record_test(
            "MetaLearningAgent accepts telemetry_callback",
            agent_with_callback.telemetry_callback is not None,
            "telemetry_callback not set"
        )
        
        # Test 3: store_experience triggers telemetry
        exp_id = agent_with_callback.store_experience(
            state={"test": "state"},
            thought_type="cot",
            outcome={"result": "success"},
            reward=0.8
        )
        record_test(
            "store_experience returns experience ID",
            exp_id is not None and exp_id.startswith("exp_"),
            f"Invalid exp_id: {exp_id}"
        )
        
        record_test(
            "store_experience triggers telemetry callback",
            len(telemetry_events) > 0 and telemetry_events[-1]["type"] == "experience_stored",
            "No telemetry event captured"
        )
        
        # Test 4: extract_patterns triggers telemetry
        patterns = agent_with_callback.extract_patterns()
        record_test(
            "extract_patterns triggers telemetry callback",
            any(e["type"] == "patterns_extracted" for e in telemetry_events),
            "No patterns_extracted event"
        )
        
        # Test 5: get_live_statistics returns correct structure
        stats = agent_with_callback.get_live_statistics()
        stat_fields = ["total_experiences", "buffer_size", "buffer_capacity", 
                      "patterns_extracted", "strategy_weights", "recent_experiences"]
        for field in stat_fields:
            record_test(
                f"get_live_statistics has {field}",
                field in stats,
                f"Missing field: {field}"
            )
        
        # Test 6: Verify experience count
        record_test(
            "total_experiences incremented",
            stats["total_experiences"] >= 1,
            f"Expected >= 1, got {stats['total_experiences']}"
        )
        
    except ImportError as e:
        record_test("Import MetaLearningAgent", False, str(e))
    except Exception as e:
        record_test("Phase 1.2 tests", False, str(e))


def test_phase1_3_redis_telemetry():
    """Test Phase 1.3: SovereignRedisClient telemetry."""
    print("\n" + "=" * 70)
    print("Phase 1.3: SovereignRedisClient Telemetry Tests")
    print("=" * 70)
    
    try:
        from agentic_core.utils.core_extensions.redis import SovereignRedisClient
        
        # Test 1: SovereignRedisClient can be instantiated
        client = SovereignRedisClient()
        record_test("SovereignRedisClient instantiation", True)
        
        # Test 2: Telemetry callback parameter exists
        telemetry_events = []
        def capture_telemetry(event_type: str, data: dict):
            telemetry_events.append({"type": event_type, "data": data})
        
        client_with_callback = SovereignRedisClient(telemetry_callback=capture_telemetry)
        record_test(
            "SovereignRedisClient accepts telemetry_callback",
            client_with_callback.telemetry_callback is not None,
            "telemetry_callback not set"
        )
        
        # Test 3: operation_stats initialized
        record_test(
            "operation_stats initialized",
            hasattr(client_with_callback, 'operation_stats'),
            "Missing operation_stats"
        )
        
        # Test 4: Execute SET operation
        client_with_callback.execute('set', key='test_key', value='test_value')
        record_test(
            "SET operation tracked",
            client_with_callback.operation_stats['set'] >= 1,
            f"SET count: {client_with_callback.operation_stats.get('set', 0)}"
        )
        
        # Test 5: Execute GET operation
        client_with_callback.execute('get', key='test_key')
        record_test(
            "GET operation tracked",
            client_with_callback.operation_stats['get'] >= 1,
            f"GET count: {client_with_callback.operation_stats.get('get', 0)}"
        )
        
        # Test 6: Telemetry events captured
        record_test(
            "Telemetry events captured for Redis operations",
            len(telemetry_events) >= 2,
            f"Expected >= 2 events, got {len(telemetry_events)}"
        )
        
        # Test 7: get_statistics returns correct structure
        stats = client_with_callback.get_statistics()
        stat_fields = ["connected", "operations", "cache_hits", 
                      "cache_misses", "hit_rate", "recent_operations"]
        for field in stat_fields:
            record_test(
                f"get_statistics has {field}",
                field in stats,
                f"Missing field: {field}"
            )
        
    except ImportError as e:
        record_test("Import SovereignRedisClient", False, str(e))
    except Exception as e:
        record_test("Phase 1.3 tests", False, str(e))


def test_phase1_4_pinecone_telemetry():
    """Test Phase 1.4: PineconeTelemetryWrapper."""
    print("\n" + "=" * 70)
    print("Phase 1.4: PineconeTelemetryWrapper Tests")
    print("=" * 70)
    
    try:
        from agentic_core.L4_state.pinecone_telemetry import PineconeTelemetryWrapper
        
        # Test 1: PineconeTelemetryWrapper can be instantiated
        wrapper = PineconeTelemetryWrapper()
        record_test("PineconeTelemetryWrapper instantiation", True)
        
        # Test 2: Telemetry callback parameter exists
        telemetry_events = []
        def capture_telemetry(event_type: str, data: dict):
            telemetry_events.append({"type": event_type, "data": data})
        
        wrapper_with_callback = PineconeTelemetryWrapper(telemetry_callback=capture_telemetry)
        record_test(
            "PineconeTelemetryWrapper accepts telemetry_callback",
            wrapper_with_callback.telemetry_callback is not None,
            "telemetry_callback not set"
        )
        
        # Test 3: stats initialized
        record_test(
            "stats initialized",
            hasattr(wrapper_with_callback, 'stats'),
            "Missing stats"
        )
        
        # Test 4: Upsert operation (without real client)
        wrapper_with_callback.upsert(vectors=[{"id": "test1", "values": [0.1, 0.2]}])
        record_test(
            "Upsert operation tracked",
            wrapper_with_callback.stats['upsert'] >= 1,
            f"Upsert count: {wrapper_with_callback.stats.get('upsert', 0)}"
        )
        
        # Test 5: Query operation (without real client)
        wrapper_with_callback.query(vector=[0.1, 0.2], top_k=5)
        record_test(
            "Query operation tracked",
            wrapper_with_callback.stats['query'] >= 1,
            f"Query count: {wrapper_with_callback.stats.get('query', 0)}"
        )
        
        # Test 6: Telemetry events captured
        record_test(
            "Telemetry events captured for Pinecone operations",
            len(telemetry_events) >= 2,
            f"Expected >= 2 events, got {len(telemetry_events)}"
        )
        
        # Test 7: get_statistics returns correct structure
        stats = wrapper_with_callback.get_statistics()
        stat_fields = ["connected", "operations", "vectors_stored", 
                      "avg_similarity", "recent_queries"]
        for field in stat_fields:
            record_test(
                f"get_statistics has {field}",
                field in stats,
                f"Missing field: {field}"
            )
        
    except ImportError as e:
        record_test("Import PineconeTelemetryWrapper", False, str(e))
    except Exception as e:
        record_test("Phase 1.4 tests", False, str(e))


def test_phase2_api_endpoints():
    """Test Phase 2: FastAPI runtime API endpoints."""
    print("\n" + "=" * 70)
    print("Phase 2: FastAPI Runtime API Tests")
    print("=" * 70)
    
    try:
        from agentic_core.L6_observability.api.runtime_api import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test 1: Health endpoint
        response = client.get("/api/health")
        record_test(
            "GET /api/health returns 200",
            response.status_code == 200,
            f"Status: {response.status_code}"
        )
        
        # Test 2: Meta-learning activity endpoint
        response = client.get("/api/meta-learning/activity")
        record_test(
            "GET /api/meta-learning/activity returns 200",
            response.status_code == 200,
            f"Status: {response.status_code}"
        )
        
        if response.status_code == 200:
            data = response.json()
            record_test(
                "meta-learning/activity has total_experiences",
                "total_experiences" in data,
                f"Response: {data}"
            )
        
        # Test 3: Meta-learning statistics endpoint
        response = client.get("/api/meta-learning/statistics")
        record_test(
            "GET /api/meta-learning/statistics returns 200",
            response.status_code == 200,
            f"Status: {response.status_code}"
        )
        
        if response.status_code == 200:
            data = response.json()
            record_test(
                "meta-learning/statistics has strategy_weights",
                "strategy_weights" in data,
                f"Response keys: {list(data.keys())}"
            )
        
        # Test 4: Redis stats endpoint
        response = client.get("/api/redis/stats")
        record_test(
            "GET /api/redis/stats returns 200",
            response.status_code == 200,
            f"Status: {response.status_code}"
        )
        
        if response.status_code == 200:
            data = response.json()
            record_test(
                "redis/stats has operations",
                "operations" in data,
                f"Response keys: {list(data.keys())}"
            )
        
        # Test 5: Pinecone stats endpoint
        response = client.get("/api/pinecone/stats")
        record_test(
            "GET /api/pinecone/stats returns 200",
            response.status_code == 200,
            f"Status: {response.status_code}"
        )
        
        if response.status_code == 200:
            data = response.json()
            record_test(
                "pinecone/stats has vectors_stored",
                "vectors_stored" in data,
                f"Response keys: {list(data.keys())}"
            )
        
        # Test 6: Runtime state endpoint
        response = client.get("/api/runtime/state")
        record_test(
            "GET /api/runtime/state returns 200",
            response.status_code == 200,
            f"Status: {response.status_code}"
        )
        
        # Test 7: Execution timeline endpoint
        response = client.get("/api/execution/timeline")
        record_test(
            "GET /api/execution/timeline returns 200",
            response.status_code == 200,
            f"Status: {response.status_code}"
        )
        
        # Test 8: Redis logs endpoint
        response = client.get("/api/redis/logs")
        record_test(
            "GET /api/redis/logs returns 200",
            response.status_code == 200,
            f"Status: {response.status_code}"
        )
        
        # Test 9: Metrics latency endpoint
        response = client.get("/api/metrics/latency")
        record_test(
            "GET /api/metrics/latency returns 200",
            response.status_code == 200,
            f"Status: {response.status_code}"
        )
        
        # Test 10: POST experience endpoint
        response = client.post("/api/meta-learning/experience", json={
            "state": {"test": "data"},
            "thought_type": "cot",
            "outcome": {"result": "success"},
            "reward": 0.9
        })
        record_test(
            "POST /api/meta-learning/experience returns 200",
            response.status_code == 200,
            f"Status: {response.status_code}"
        )
        
    except ImportError as e:
        record_test("Import FastAPI app", False, str(e))
    except Exception as e:
        record_test("Phase 2 tests", False, str(e))


def test_update_functions():
    """Test the telemetry update functions in canon_validator."""
    print("\n" + "=" * 70)
    print("Telemetry Update Functions Tests")
    print("=" * 70)
    
    try:
        from archives.void_violations.canon_validator_agentic_v2_thin_21 import (
            _runtime_state,
            _update_meta_learning_state,
            _update_redis_state,
            _update_pinecone_state,
            _update_agent_execution,
            _add_event
        )
        
        # Test 1: _update_meta_learning_state
        _update_meta_learning_state({
            "total_experiences": 5,
            "patterns_extracted": 2,
            "experience": {"thought_type": "cot", "reward": 0.8, "timestamp": datetime.now().isoformat()}
        })
        record_test(
            "_update_meta_learning_state works",
            _runtime_state["meta_learning"]["total_experiences"] == 5,
            f"total_experiences: {_runtime_state['meta_learning']['total_experiences']}"
        )
        
        # Test 2: _update_redis_state
        _update_redis_state("get", "test_key", hit=True)
        record_test(
            "_update_redis_state works",
            _runtime_state["redis"]["cache_hits"] >= 1,
            f"cache_hits: {_runtime_state['redis']['cache_hits']}"
        )
        
        # Test 3: _update_pinecone_state
        _update_pinecone_state("query", {"similarity": 0.85, "results": [], "top_k": 5})
        record_test(
            "_update_pinecone_state works",
            _runtime_state["pinecone"]["operations"]["query"] >= 1,
            f"query count: {_runtime_state['pinecone']['operations']['query']}"
        )
        
        # Test 4: _update_agent_execution
        import time
        start = time.time()
        time.sleep(0.01)
        end = time.time()
        _update_agent_execution("TestAgent", "L5", start, end, True)
        record_test(
            "_update_agent_execution works",
            len(_runtime_state["execution_timeline"]) >= 1,
            f"timeline length: {len(_runtime_state['execution_timeline'])}"
        )
        
        # Test 5: _add_event
        initial_events = len(_runtime_state["events"])
        _add_event("test", "Test event message")
        record_test(
            "_add_event works",
            len(_runtime_state["events"]) > initial_events,
            f"events count: {len(_runtime_state['events'])}"
        )
        
    except ImportError as e:
        record_test("Import update functions", False, str(e))
    except Exception as e:
        record_test("Update functions tests", False, str(e))


def main():
    """Run all Phase 1 and Phase 2 tests."""
    print("\n" + "=" * 70)
    print("PHASE 1 & PHASE 2 TELEMETRY TEST SUITE")
    print("Dashboard Live Runtime Meta-Learning Implementation")
    print("=" * 70)
    
    # Run all test suites
    test_phase1_1_runtime_state_schema()
    test_phase1_2_meta_learning_telemetry()
    test_phase1_3_redis_telemetry()
    test_phase1_4_pinecone_telemetry()
    test_update_functions()
    test_phase2_api_endpoints()
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"  Total Tests: {test_results['passed'] + test_results['failed']}")
    print(f"  Passed: {test_results['passed']}")
    print(f"  Failed: {test_results['failed']}")
    
    if test_results['failed'] == 0:
        print("\n✅ ALL TESTS PASSED - Phase 1 & Phase 2 implementation complete!")
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
