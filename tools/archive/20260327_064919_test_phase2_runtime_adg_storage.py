#!/usr/bin/env python3
"""Phase 2 Test Suite - Runtime ADG Storage Integration (L4 + L6 + Auto-Persistence)."""

import json
import sys
import time
import traceback
from pathlib import Path


def test_l4_storage_integration():
    """Test L4 storage integration with FileBackedRuntimeADGStore."""
    print("=" * 80)
    print("PHASE 2: L4 STORAGE INTEGRATION TEST")
    print("=" * 80)

    results = {}

    # Test 1: L4 compliance validation
    print("\n1. Testing L4 compliance validation...")
    try:
        from system_learning.runtime_adg import FileBackedRuntimeADGStore

        # Test default L4 location (should be compliant)
        store = FileBackedRuntimeADGStore()
        results["l4_default_compliant"] = True
        print(f"✅ Default L4 store location: {store._base_dir}")

        # Test custom L4-compliant location
        custom_l4_path = Path("agentic_core/L4_state/memory/test_runtime_adg")
        custom_store = FileBackedRuntimeADGStore(custom_l4_path)
        results["l4_custom_compliant"] = True
        print(f"✅ Custom L4 store location: {custom_store._base_dir}")

        # Test non-compliant location (should fail)
        try:
            invalid_store = FileBackedRuntimeADGStore(Path("invalid/location"))
            results["l4_invalid_rejected"] = False
            print("❌ Non-compliant location was not rejected")
        except ValueError as e:
            results["l4_invalid_rejected"] = True
            print(f"✅ Non-compliant location correctly rejected: {e}")

    except Exception as e:
        results["l4_default_compliant"] = False
        results["l4_custom_compliant"] = False
        results["l4_invalid_rejected"] = False
        print(f"❌ L4 compliance test failed: {e}")
        traceback.print_exc()

    # Test 2: L4 storage functionality
    print("\n2. Testing L4 storage functionality...")
    try:
        from system_learning.runtime_adg import RuntimeADGMaterializer

        # Create test snapshot
        materializer = RuntimeADGMaterializer()
        test_spans = [
            {
                "span_id": "test_span_1",
                "parent_span_id": "",
                "name": "test_operation",
                "kind": "test",
                "layer": "L1_Cognition",
                "component": "TestComponent",
                "ts_utc": int(time.time() * 1000),
                "duration_ms": 100.0,
                "status": "ok",
                "attributes": {"test": "l4_storage"},
            },
        ]

        snapshot = materializer.materialize(test_spans, mission="l4-test-mission")
        results["l4_snapshot_created"] = True

        # Store in L4
        version_id = store.persist(snapshot)
        results["l4_persist_success"] = bool(version_id)
        print(f"✅ Snapshot persisted to L4 with version_id: {version_id}")

        # Retrieve from L4
        payload = store.get_by_version(version_id)
        results["l4_retrieve_success"] = payload is not None
        print(f"✅ Snapshot retrieved from L4: {len(payload) if payload else 0} bytes")

        # Verify trace index
        trace_version = store.get_version_id_for_trace(snapshot.trace_id)
        results["l4_trace_index"] = trace_version == version_id
        print(f"✅ Trace index working: {trace_version}")

    except Exception as e:
        results["l4_snapshot_created"] = False
        results["l4_persist_success"] = False
        results["l4_retrieve_success"] = False
        results["l4_trace_index"] = False
        print(f"❌ L4 storage functionality test failed: {e}")
        traceback.print_exc()

    # Test 3: L4 directory structure
    print("\n3. Testing L4 directory structure...")
    try:
        # Verify L4 directory structure
        base_dir = store._base_dir
        index_file = base_dir / "_index.json"
        trace_index_file = base_dir / "_trace_index.json"

        results["l4_base_dir_exists"] = base_dir.exists()
        results["l4_index_file_exists"] = index_file.exists()
        results["l4_trace_index_exists"] = trace_index_file.exists()

        if index_file.exists():
            index_data = json.loads(index_file.read_text())
            results["l4_index_valid"] = isinstance(index_data, dict)
            print(f"✅ Index file valid with {len(index_data)} entries")
        else:
            results["l4_index_valid"] = False

        if trace_index_file.exists():
            trace_data = json.loads(trace_index_file.read_text())
            results["l4_trace_index_valid"] = isinstance(trace_data, dict)
            print(f"✅ Trace index file valid with {len(trace_data)} entries")
        else:
            results["l4_trace_index_valid"] = False

    except Exception as e:
        results["l4_base_dir_exists"] = False
        results["l4_index_file_exists"] = False
        results["l4_trace_index_exists"] = False
        results["l4_index_valid"] = False
        results["l4_trace_index_valid"] = False
        print(f"❌ L4 directory structure test failed: {e}")
        traceback.print_exc()

    # Summary
    print("\n" + "=" * 80)
    print("L4 STORAGE INTEGRATION SUMMARY")
    print("=" * 80)

    test_keys = [
        "l4_default_compliant",
        "l4_custom_compliant",
        "l4_invalid_rejected",
        "l4_snapshot_created",
        "l4_persist_success",
        "l4_retrieve_success",
        "l4_trace_index",
        "l4_base_dir_exists",
        "l4_index_file_exists",
        "l4_trace_index_exists",
        "l4_index_valid",
        "l4_trace_index_valid",
    ]

    success_count = sum(1 for key in test_keys if results.get(key) is True)
    total_tests = len(test_keys)

    print(f"L4 Storage Tests: {success_count}/{total_tests}")

    if success_count == total_tests:
        print("🎉 ALL L4 STORAGE TESTS PASSED!")
    else:
        print("🚨 Some L4 storage tests failed")

    return results


def test_l6_integration():
    """Test L6 meta-learning integration."""
    print("\n" + "=" * 80)
    print("PHASE 2: L6 META-LEARNING INTEGRATION TEST")
    print("=" * 80)

    results = {}

    # Test 1: L6 bridge initialization
    print("\n1. Testing L6 bridge initialization...")
    try:
        from system_learning.runtime_adg import L6MetaLearningBridge

        # Test default L6 bridge
        bridge = L6MetaLearningBridge()
        results["l6_bridge_init"] = True
        print(f"✅ L6 bridge initialized: {bridge._l6_base_dir}")

        # Test custom L6 bridge
        custom_l6_path = Path("system_learning/meta_learning/test_runtime_adg_snapshots")
        custom_bridge = L6MetaLearningBridge(custom_l6_path)
        results["l6_custom_bridge_init"] = True
        print(f"✅ Custom L6 bridge initialized: {custom_bridge._l6_base_dir}")

    except Exception as e:
        results["l6_bridge_init"] = False
        results["l6_custom_bridge_init"] = False
        print(f"❌ L6 bridge initialization failed: {e}")
        traceback.print_exc()

    # Test 2: L6 snapshot storage
    print("\n2. Testing L6 snapshot storage...")
    try:
        from system_learning.runtime_adg import RuntimeADGMaterializer

        # Create test snapshot
        materializer = RuntimeADGMaterializer()
        test_spans = [
            {
                "span_id": "l6_test_span_1",
                "parent_span_id": "",
                "name": "l6_test_operation",
                "kind": "test",
                "layer": "L2_Execution",
                "component": "L6TestComponent",
                "ts_utc": int(time.time() * 1000),
                "duration_ms": 150.0,
                "status": "ok",
                "attributes": {"test": "l6_meta_learning"},
            },
        ]

        snapshot = materializer.materialize(test_spans, mission="l6-test-mission")
        results["l6_snapshot_created"] = True

        # Store in L6
        meta_learning_id = bridge.store_snapshot_for_meta_learning(snapshot)
        results["l6_store_success"] = bool(meta_learning_id)
        print(f"✅ Snapshot stored in L6: {meta_learning_id}")

    except Exception as e:
        results["l6_snapshot_created"] = False
        results["l6_store_success"] = False
        print(f"❌ L6 snapshot storage test failed: {e}")
        traceback.print_exc()

    # Test 3: L6 pattern extraction
    print("\n3. Testing L6 pattern extraction...")
    try:
        # Get patterns for the stored snapshot
        patterns = bridge.get_execution_patterns()
        results["l6_patterns_retrieved"] = isinstance(patterns, dict)

        if patterns:
            results["l6_layer_distribution"] = "layer_distribution" in patterns
            results["l6_component_distribution"] = "component_distribution" in patterns
            results["l6_span_type_distribution"] = "span_type_distribution" in patterns

            print("✅ Pattern extraction working:")
            print(f"   - Layer distribution: {patterns.get('layer_distribution', {})}")
            print(f"   - Component distribution: {patterns.get('component_distribution', {})}")
            print(f"   - Total snapshots: {patterns.get('total_snapshots', 0)}")
        else:
            results["l6_layer_distribution"] = False
            results["l6_component_distribution"] = False
            results["l6_span_type_distribution"] = False

    except Exception as e:
        results["l6_patterns_retrieved"] = False
        results["l6_layer_distribution"] = False
        results["l6_component_distribution"] = False
        results["l6_span_type_distribution"] = False
        print(f"❌ L6 pattern extraction test failed: {e}")
        traceback.print_exc()

    # Test 4: L6 evolution logging
    print("\n4. Testing L6 evolution logging...")
    try:
        # Query evolution log
        evolution_events = bridge.query_evolution_log(limit=10)
        results["l6_evolution_log"] = isinstance(evolution_events, list)

        if evolution_events:
            results["l6_evolution_events"] = len(evolution_events) > 0
            print(f"✅ Evolution log working: {len(evolution_events)} events")

            # Check for runtime_adg_stored events
            runtime_events = bridge.query_evolution_log("runtime_adg_stored", limit=5)
            results["l6_runtime_events"] = isinstance(runtime_events, list) and len(runtime_events) > 0
            print(f"✅ Runtime ADG events: {len(runtime_events)}")
        else:
            results["l6_evolution_events"] = False
            results["l6_runtime_events"] = False

    except Exception as e:
        results["l6_evolution_log"] = False
        results["l6_evolution_events"] = False
        results["l6_runtime_events"] = False
        print(f"❌ L6 evolution logging test failed: {e}")
        traceback.print_exc()

    # Summary
    print("\n" + "=" * 80)
    print("L6 META-LEARNING INTEGRATION SUMMARY")
    print("=" * 80)

    test_keys = [
        "l6_bridge_init",
        "l6_custom_bridge_init",
        "l6_snapshot_created",
        "l6_store_success",
        "l6_patterns_retrieved",
        "l6_layer_distribution",
        "l6_component_distribution",
        "l6_span_type_distribution",
        "l6_evolution_log",
        "l6_evolution_events",
        "l6_runtime_events",
    ]

    success_count = sum(1 for key in test_keys if results.get(key) is True)
    total_tests = len(test_keys)

    print(f"L6 Integration Tests: {success_count}/{total_tests}")

    if success_count == total_tests:
        print("🎉 ALL L6 INTEGRATION TESTS PASSED!")
    else:
        print("🚨 Some L6 integration tests failed")

    return results


def test_auto_persistence():
    """Test automatic snapshot persistence."""
    print("\n" + "=" * 80)
    print("PHASE 2: AUTO-PERSISTENCE INTEGRATION TEST")
    print("=" * 80)

    results = {}

    # Test 1: Auto-persistence adapter initialization
    print("\n1. Testing auto-persistence adapter initialization...")
    try:
        from system_learning.runtime_adg.auto_persistence import (
            AutoPersistenceTracingAdapter,
            get_auto_persistence_tracer,
        )

        # Test adapter initialization
        adapter = AutoPersistenceTracingAdapter(
            service_name="auto-persistence-test",
            enable_auto_persistence=True,
        )
        results["auto_adapter_init"] = True

        # Test factory function
        factory_adapter = get_auto_persistence_tracer(
            service_name="factory-test",
            enable_auto_persistence=True,
        )
        results["auto_factory_init"] = True

        print("✅ Auto-persistence adapters initialized successfully")

    except Exception as e:
        results["auto_adapter_init"] = False
        results["auto_factory_init"] = False
        print(f"❌ Auto-persistence initialization failed: {e}")
        traceback.print_exc()

    # Test 2: Auto-persistence functionality
    print("\n2. Testing auto-persistence functionality...")
    try:
        # Test auto-persistence with orchestrator trace
        with adapter.trace_orchestrator("auto-persistence-mission", {"test": "auto"}) as span:
            results["auto_orchestrator_trace"] = True

            # Add some nested spans
            with adapter.trace_cognitive("auto-planning", reasoning_mode="react") as cog_span:
                results["auto_cognitive_trace"] = True
                time.sleep(0.001)

            with adapter.trace_action(action_count=1) as act_span:
                results["auto_action_trace"] = True
                time.sleep(0.001)

        # Auto-persistence should happen automatically when exiting context
        print("✅ Auto-persistence trace completed")

    except Exception as e:
        results["auto_orchestrator_trace"] = False
        results["auto_cognitive_trace"] = False
        results["auto_action_trace"] = False
        print(f"❌ Auto-persistence trace failed: {e}")
        traceback.print_exc()

    # Test 3: Auto-persistence status
    print("\n3. Testing auto-persistence status...")
    try:
        status = adapter.get_auto_persistence_status()
        results["auto_status_retrieved"] = isinstance(status, dict)

        if status:
            results["auto_enabled"] = status.get("enabled") == True
            results["auto_l4_available"] = status.get("l4_store_available") == True
            results["auto_l6_available"] = status.get("l6_bridge_available") == True

            print("✅ Auto-persistence status:")
            print(f"   - Enabled: {status.get('enabled')}")
            print(f"   - L4 Store: {status.get('l4_store_available')}")
            print(f"   - L6 Bridge: {status.get('l6_bridge_available')}")
            if "l4_snapshot_count" in status:
                print(f"   - L4 Snapshots: {status['l4_snapshot_count']}")
            if "l6_snapshot_count" in status:
                print(f"   - L6 Snapshots: {status['l6_snapshot_count']}")
        else:
            results["auto_enabled"] = False
            results["auto_l4_available"] = False
            results["auto_l6_available"] = False

    except Exception as e:
        results["auto_status_retrieved"] = False
        results["auto_enabled"] = False
        results["auto_l4_available"] = False
        results["auto_l6_available"] = False
        print(f"❌ Auto-persistence status test failed: {e}")
        traceback.print_exc()

    # Test 4: Force persistence
    print("\n4. Testing force persistence...")
    try:
        # Add some spans manually
        with adapter.trace_tool("force_test_tool", {"param": "value"}) as tool_span:
            results["auto_force_tool_trace"] = True
            time.sleep(0.001)

        # Force persistence
        force_result = adapter.force_persist_current_spans("force-test-mission")
        results["auto_force_success"] = isinstance(force_result, dict) and force_result.get("success") == True

        if force_result.get("success"):
            print("✅ Force persistence successful:")
            print(f"   - Mission: {force_result.get('mission')}")
            print(f"   - Span count: {force_result.get('span_count')}")
            print(f"   - Node count: {force_result.get('node_count')}")
            print(f"   - Edge count: {force_result.get('edge_count')}")
        else:
            print(f"❌ Force persistence failed: {force_result}")

    except Exception as e:
        results["auto_force_tool_trace"] = False
        results["auto_force_success"] = False
        print(f"❌ Force persistence test failed: {e}")
        traceback.print_exc()

    # Summary
    print("\n" + "=" * 80)
    print("AUTO-PERSISTENCE INTEGRATION SUMMARY")
    print("=" * 80)

    test_keys = [
        "auto_adapter_init",
        "auto_factory_init",
        "auto_orchestrator_trace",
        "auto_cognitive_trace",
        "auto_action_trace",
        "auto_status_retrieved",
        "auto_enabled",
        "auto_l4_available",
        "auto_l6_available",
        "auto_force_tool_trace",
        "auto_force_success",
    ]

    success_count = sum(1 for key in test_keys if results.get(key) is True)
    total_tests = len(test_keys)

    print(f"Auto-Persistence Tests: {success_count}/{total_tests}")

    if success_count == total_tests:
        print("🎉 ALL AUTO-PERSISTENCE TESTS PASSED!")
    else:
        print("🚨 Some auto-persistence tests failed")

    return results


def main():
    """Run all Phase 2 tests."""
    print("PHASE 2: RUNTIME ADG STORAGE INTEGRATION - COMPREHENSIVE TEST SUITE")
    print("=" * 80)

    # Run all test suites
    l4_results = test_l4_storage_integration()
    l6_results = test_l6_integration()
    auto_results = test_auto_persistence()

    # Combined summary
    print("\n" + "=" * 80)
    print("PHASE 2 COMPREHENSIVE SUMMARY")
    print("=" * 80)

    all_tests = list(l4_results.keys()) + list(l6_results.keys()) + list(auto_results.keys())
    all_passed = sum(
        1
        for key in all_tests
        if (l4_results.get(key) or l6_results.get(key) or auto_results.get(key)) is True
    )
    total_tests = len(all_tests)

    print(f"Overall Results: {all_passed}/{total_tests} tests passed")

    # Component summaries
    l4_passed = sum(1 for key, value in l4_results.items() if value is True)
    l6_passed = sum(1 for key, value in l6_results.items() if value is True)
    auto_passed = sum(1 for key, value in auto_results.items() if value is True)

    print(f"L4 Storage: {l4_passed}/{len(l4_results)} passed")
    print(f"L6 Integration: {l6_passed}/{len(l6_results)} passed")
    print(f"Auto-Persistence: {auto_passed}/{len(auto_results)} passed")

    if all_passed == total_tests:
        print("\n🎉 PHASE 2 COMPLETE - ALL STORAGE INTEGRATION TESTS PASSED!")
        print("✅ Runtime ADG → L4/L6 storage pipeline is fully operational")
        return True
    else:
        print("\n🚨 PHASE 2 INCOMPLETE - Some storage integration tests failed")
        print("❌ Runtime ADG → L4/L6 storage pipeline has issues")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
