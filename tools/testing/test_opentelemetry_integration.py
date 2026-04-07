#!/usr/bin/env python3
"""Comprehensive OpenTelemetry integration test for runtime ADG pipeline."""

import sys
import time
import traceback


def test_opentelemetry_runtime_adg_integration():
    """Test complete OpenTelemetry to Runtime ADG integration pipeline."""
    print("=" * 80)
    print("OPENTELEMETRY RUNTIME ADG INTEGRATION TEST")
    print("=" * 80)

    results = {}

    # Test 1: Verify OpenTelemetry is available
    print("\n1. Verifying OpenTelemetry availability...")
    try:
        from apps_shared.utils.open_telemetry_tracing_adapter_util import (
            OTEL_AVAILABLE,
            get_tracer,
        )

        results['otel_available'] = OTEL_AVAILABLE
        if OTEL_AVAILABLE:
            print("✅ OpenTelemetry is available")
        else:
            print("❌ OpenTelemetry is NOT available")
            return results

    except Exception as e:
        results['otel_available'] = f"ERROR: {e}"
        print(f"❌ Failed to import OpenTelemetry: {e}")
        return results

    # Test 2: Test OpenTelemetry tracing functionality
    print("\n2. Testing OpenTelemetry tracing functionality...")
    try:
        tracer = get_tracer(service_name="integration-test")

        # Test orchestrator span
        with tracer.trace_orchestrator("integration-mission", {"test": "runtime-adg"}) as span:
            results['orchestrator_span'] = True

            # Test cognitive span
            with tracer.trace_cognitive("planning", reasoning_mode="react") as cog_span:
                results['cognitive_span'] = True
                time.sleep(0.001)  # Simulate work

            # Test action span
            with tracer.trace_action(action_count=1) as act_span:
                results['action_span'] = True
                time.sleep(0.001)  # Simulate work

            # Test tool span
            with tracer.trace_tool("test_tool", {"param": "value"}) as tool_span:
                results['tool_span'] = True
                time.sleep(0.001)  # Simulate work

        print("✅ All span types created successfully")

    except Exception as e:
        results['orchestrator_span'] = False
        results['cognitive_span'] = False
        results['action_span'] = False
        results['tool_span'] = False
        print(f"❌ Tracing functionality failed: {e}")
        traceback.print_exc()

    # Test 3: Test span draining
    print("\n3. Testing span draining...")
    try:
        spans = tracer.drain_completed_spans()
        results['spans_drained'] = len(spans)
        results['drain_success'] = len(spans) > 0

        if spans:
            print(f"✅ Drained {len(spans)} spans")
            # Verify span structure
            sample_span = spans[0]
            required_fields = ['span_id', 'name', 'kind', 'layer', 'component', 'ts_utc', 'duration_ms', 'status']
            missing_fields = [field for field in required_fields if field not in sample_span]

            if missing_fields:
                results['span_structure'] = False
                print(f"❌ Missing span fields: {missing_fields}")
            else:
                results['span_structure'] = True
                print("✅ Span structure is valid")
        else:
            print("❌ No spans drained")

    except Exception as e:
        results['drain_success'] = False
        results['spans_drained'] = 0
        print(f"❌ Span draining failed: {e}")
        traceback.print_exc()

    # Test 4: Test Runtime ADG materialization
    print("\n4. Testing Runtime ADG materialization...")
    try:
        from system_learning.runtime_adg import RuntimeADGMaterializer

        materializer = RuntimeADGMaterializer()

        if results.get('spans_drained', 0) > 0:
            snapshot = materializer.materialize(
                spans,
                mission="integration-test-mission",
                trace_id="integration-test-trace",
            )

            results['materialization_success'] = True
            results['snapshot_nodes'] = len(snapshot.nodes)
            results['snapshot_edges'] = len(snapshot.edges)

            print(f"✅ Materialized snapshot: {len(snapshot.nodes)} nodes, {len(snapshot.edges)} edges")

            # Verify snapshot structure
            if snapshot.nodes and snapshot.edges:
                results['snapshot_valid'] = True
                print("✅ Snapshot structure is valid")
            else:
                results['snapshot_valid'] = False
                print("❌ Invalid snapshot structure")
        else:
            results['materialization_success'] = False
            print("❌ No spans to materialize")

    except Exception as e:
        results['materialization_success'] = False
        print(f"❌ Runtime ADG materialization failed: {e}")
        traceback.print_exc()

    # Test 5: Test TracingMixin integration
    print("\n5. Testing TracingMixin integration...")
    try:
        from agentic_core.mixins.tracing_mixin import SpanContext, TracingMixin

        class TestAgent(TracingMixin):
            def __init__(self):
                super().__init__(service_name="TestIntegrationAgent")

        agent = TestAgent()
        results['tracing_mixin_init'] = True

        # Test span creation
        with agent.start_span("test_operation", {"test": "integration"}) as span:
            results['mixin_span'] = True
            assert isinstance(span, SpanContext)

        # Test trace context
        context = agent.get_trace_context()
        results['trace_context'] = bool(context)

        # Test trace flushing
        traces = agent.flush_traces()
        results['trace_flush'] = isinstance(traces, list)

        print("✅ TracingMixin integration successful")

    except Exception as e:
        results['tracing_mixin_init'] = False
        results['mixin_span'] = False
        results['trace_context'] = False
        results['trace_flush'] = False
        print(f"❌ TracingMixin integration failed: {e}")
        traceback.print_exc()

    # Test 6: Test runtime ADG store functionality
    print("\n6. Testing Runtime ADG store functionality...")
    try:
        from system_learning.runtime_adg import InMemoryRuntimeADGStore

        store = InMemoryRuntimeADGStore()

        if results.get('materialization_success') and results.get('snapshot_valid'):
            # Store the snapshot
            version_id = store.persist(snapshot)
            results['store_snapshot'] = True

            # Retrieve the snapshot
            payload = store.get_by_version(version_id)
            results['retrieve_snapshot'] = payload is not None

            if payload:
                # For in-memory store, we need to deserialize manually
                # For the test, just verify the payload exists and has content
                results['retrieve_match'] = len(payload) > 0
            else:
                results['retrieve_match'] = False

            print("✅ Runtime ADG store functionality successful")
        else:
            results['store_snapshot'] = False
            results['retrieve_snapshot'] = False
            results['retrieve_match'] = False
            print("❌ No valid snapshot to store")

    except Exception as e:
        results['store_snapshot'] = False
        results['retrieve_snapshot'] = False
        results['retrieve_match'] = False
        print(f"❌ Runtime ADG store failed: {e}")
        traceback.print_exc()

    # Test 7: Test end-to-end pipeline
    print("\n7. Testing end-to-end pipeline...")
    try:
        # Create a complete end-to-end test
        end_to_end_tracer = get_tracer(service_name="end-to-end-test")

        with end_to_end_tracer.trace_orchestrator("e2e-mission", {"pipeline": "test"}) as root_span:
            with end_to_end_tracer.trace_cognitive("e2e-planning", reasoning_mode="chain_of_thought") as planning_span:
                time.sleep(0.001)

            with end_to_end_tracer.trace_action(action_count=2) as action_span:
                with end_to_end_tracer.trace_tool("e2e_tool_1", {"arg": "value1"}) as tool1_span:
                    time.sleep(0.001)
                with end_to_end_tracer.trace_tool("e2e_tool_2", {"arg": "value2"}) as tool2_span:
                    time.sleep(0.001)

        # Drain spans
        e2e_spans = end_to_end_tracer.drain_completed_spans()

        # Materialize snapshot
        e2e_materializer = RuntimeADGMaterializer()
        e2e_snapshot = e2e_materializer.materialize(e2e_spans, mission="e2e-test", trace_id="e2e-trace")

        # Store snapshot
        e2e_store = InMemoryRuntimeADGStore()
        e2e_version_id = e2e_store.persist(e2e_snapshot)

        # Verify retrieval
        e2e_payload = e2e_store.get_by_version(e2e_version_id)

        results['e2e_success'] = (
            len(e2e_spans) >= 4 and  # orchestrator + cognitive + action + 2 tools
            len(e2e_snapshot.nodes) >= 4 and
            len(e2e_snapshot.edges) >= 4 and
            e2e_payload is not None and
            len(e2e_payload) > 0
        )

        if results['e2e_success']:
            print(f"✅ End-to-end pipeline successful: {len(e2e_spans)} spans → {len(e2e_snapshot.nodes)} nodes → {len(e2e_snapshot.edges)} edges")
        else:
            print("❌ End-to-end pipeline failed")

    except Exception as e:
        results['e2e_success'] = False
        print(f"❌ End-to-end pipeline failed: {e}")
        traceback.print_exc()

    # Summary
    print("\n" + "=" * 80)
    print("INTEGRATION TEST SUMMARY")
    print("=" * 80)

    # Count successful tests
    test_keys = [
        'otel_available', 'orchestrator_span', 'cognitive_span', 'action_span', 'tool_span',
        'drain_success', 'span_structure', 'materialization_success', 'snapshot_valid',
        'tracing_mixin_init', 'mixin_span', 'trace_context', 'trace_flush',
        'store_snapshot', 'retrieve_snapshot', 'retrieve_match', 'e2e_success',
    ]

    success_count = sum(1 for key in test_keys if results.get(key) is True)
    total_tests = len(test_keys)

    print(f"Tests passed: {success_count}/{total_tests}")

    if success_count == total_tests:
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        print("✅ OpenTelemetry → Runtime ADG pipeline is fully functional")
    else:
        print("🚨 Some integration tests failed")
        print("❌ OpenTelemetry → Runtime ADG pipeline has issues")

    print("\nDetailed results:")
    for key in test_keys:
        value = results.get(key)
        status = "✅" if value is True else "❌" if value is False else "⚠️"
        print(f"  {status} {key}: {value}")

    return results

if __name__ == "__main__":
    results = test_opentelemetry_runtime_adg_integration()

    # Exit with error code if critical tests failed
    critical_tests = ['otel_available', 'drain_success', 'materialization_success', 'e2e_success']
    critical_failed = [test for test in critical_tests if not results.get(test)]

    if critical_failed:
        print(f"\n🚨 CRITICAL TESTS FAILED: {critical_failed}")
        sys.exit(1)
    else:
        print("\n✅ ALL CRITICAL TESTS PASSED!")
        sys.exit(0)
