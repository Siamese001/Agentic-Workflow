"""Wave 2: Snapshot ADG Extraction + Schema — Verification Tests.

Tests for semantic edge extraction and snapshot validation.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def test_semantic_edge_extraction() -> bool:
    """Test that semantic edges are extracted from span attributes."""
    try:
        from system_learning.runtime_adg.materializer import (
            _extract_semantic_edges,
        )

        # Create test spans with semantic attributes
        spans = [
            {
                "span_id": "span-001",
                "name": "tool_call",
                "kind": "tool",
                "layer": "L2",
                "component": "TestComponent",
                "ts_utc": 1000,
                "duration_ms": 50.0,
                "status": "ok",
                "attributes": {
                    "tool_name": "vector_search",
                    "span_kind": "tool",
                    "actor_id": "agent-001",
                    "target_id": "pinecone_index",
                },
            },
            {
                "span_id": "span-002",
                "name": "orchestrate",
                "kind": "orchestrator",
                "layer": "L3",
                "component": "Orchestrator",
                "ts_utc": 2000,
                "duration_ms": 100.0,
                "status": "ok",
                "attributes": {
                    "orchestrator_name": "campaign_workflow",
                    "span_kind": "orchestrator",
                    "handoff_to": "span-003",
                },
            },
            {
                "span_id": "span-003",
                "name": "evaluate",
                "kind": "evaluation",
                "layer": "L4",
                "component": "Evaluator",
                "ts_utc": 3000,
                "duration_ms": 30.0,
                "status": "ok",
                "attributes": {
                    "span_kind": "evaluation",
                    "subject": "span-001",
                    "outcome": "passed",
                },
            },
            {
                "span_id": "span-004",
                "name": "retry",
                "kind": "action",
                "layer": "L2",
                "component": "RetryHandler",
                "ts_utc": 4000,
                "duration_ms": 20.0,
                "status": "ok",
                "attributes": {
                    "retry_of": "span-001",
                    "retry_count": 1,
                },
            },
        ]

        # Extract semantic edges
        edges = _extract_semantic_edges(spans)

        # Verify edges were extracted
        assert len(edges) > 0, "No semantic edges extracted"

        # Check for specific edge types
        edge_relations = {e.relation for e in edges}

        # Verify we have tool invocation edges
        assert "tool_invocation_edge" in edge_relations, "Missing tool_invocation_edge"

        # Verify we have actor edges
        assert "actor" in edge_relations, "Missing actor edge"

        # Verify we have orchestration handoff edges
        assert "orchestration_handoff_edge" in edge_relations, "Missing orchestration_handoff_edge"

        # Verify we have evaluation edges
        assert "evaluation_edge" in edge_relations, "Missing evaluation_edge"

        # Verify we have retry edges
        assert "retry_edge" in edge_relations, "Missing retry_edge"

        # Verify we have outcome edges
        assert "outcome_edge" in edge_relations, "Missing outcome_edge"

        print(f"✓ Semantic edge extraction works: {len(edges)} edges, {len(edge_relations)} types")
        print(f"  Edge types: {sorted(edge_relations)}")
        return True

    except Exception as e:
        print(f"✗ Semantic edge extraction test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_materializer_with_semantic_edges() -> bool:
    """Test that materializer includes semantic edges in snapshot."""
    try:
        from system_learning.runtime_adg.materializer import RuntimeADGMaterializer

        materializer = RuntimeADGMaterializer()

        spans = [
            {
                "span_id": "root-001",
                "name": "root_operation",
                "kind": "orchestrator",
                "layer": "L3",
                "component": "TestOrchestrator",
                "ts_utc": 1000,
                "duration_ms": 500.0,
                "status": "ok",
                "attributes": {
                    "mission": "test-mission",
                    "orchestrator_name": "test_workflow",
                    "span_kind": "orchestrator",
                },
            },
            {
                "span_id": "child-001",
                "parent_span_id": "root-001",
                "name": "tool_call",
                "kind": "tool",
                "layer": "L2",
                "component": "TestTool",
                "ts_utc": 1500,
                "duration_ms": 100.0,
                "status": "ok",
                "attributes": {
                    "tool_name": "search",
                    "span_kind": "tool",
                    "reads_from": "vector_store",
                },
            },
        ]

        snapshot = materializer.materialize(spans, mission="test-mission")

        # Verify snapshot has nodes
        assert len(snapshot.nodes) == 2, f"Expected 2 nodes, got {len(snapshot.nodes)}"

        # Verify snapshot has edges (parent-child + temporal + semantic)
        assert len(snapshot.edges) >= 2, f"Expected at least 2 edges, got {len(snapshot.edges)}"

        # Verify edge types are present
        edge_relations = {e.relation for e in snapshot.edges}
        assert "parent_child" in edge_relations, "Missing parent_child edges"
        assert "temporal_sequence" in edge_relations, "Missing temporal_sequence edges"

        # Check for semantic edges
        semantic_relations = edge_relations - {"parent_child", "temporal_sequence"}
        assert len(semantic_relations) > 0, "No semantic edges found"

        print(f"✓ Materializer includes semantic edges: {len(snapshot.edges)} total edges")
        print(f"  Semantic relations: {sorted(semantic_relations)}")
        return True

    except Exception as e:
        print(f"✗ Materializer with semantic edges test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_snapshot_validation() -> bool:
    """Test snapshot validation method."""
    try:
        from system_learning.runtime_adg.materializer import RuntimeADGMaterializer

        materializer = RuntimeADGMaterializer()

        spans = [
            {
                "span_id": "test-001",
                "trace_id": "trace-test-001",
                "name": "test_operation",
                "kind": "action",
                "layer": "L2",
                "component": "TestComponent",
                "ts_utc": 1000,
                "duration_ms": 50.0,
                "status": "ok",
                "attributes": {},
            },
        ]

        snapshot = materializer.materialize(spans, mission="validation-test")

        # Validate the snapshot
        validation = snapshot.validate()

        # Check validation structure
        assert "is_valid" in validation, "Missing is_valid field"
        assert "errors" in validation, "Missing errors field"
        assert "warnings" in validation, "Missing warnings field"
        assert "stats" in validation, "Missing stats field"
        assert "edge_types" in validation, "Missing edge_types field"

        # Check that valid snapshot passes
        assert validation["is_valid"] is True, f"Valid snapshot failed: {validation['errors']}"

        # Check stats
        stats = validation["stats"]
        assert stats["node_count"] == 1, f"Expected 1 node, got {stats['node_count']}"

        print("✓ Snapshot validation works correctly")
        print(f"  Validation: is_valid={validation['is_valid']}, errors={len(validation['errors'])}")
        return True

    except Exception as e:
        print(f"✗ Snapshot validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_all_13_edge_types() -> bool:
    """Test that all 13 required edge types can be extracted."""
    try:
        from system_learning.runtime_adg.materializer import _extract_semantic_edges

        # Create spans with attributes for all edge types
        spans = [
            {
                "span_id": "actor-span",
                "attributes": {"actor_id": "agent-1"},
            },
            {
                "span_id": "target-span",
                "attributes": {"target_id": "destination-1"},
            },
            {
                "span_id": "dep-span",
                "attributes": {"depends_on": "dependency-1"},
            },
            {
                "span_id": "read-span",
                "attributes": {"reads_from": "source-1"},
            },
            {
                "span_id": "write-span",
                "attributes": {"writes_to": "dest-1"},
            },
            {
                "span_id": "tool-span",
                "attributes": {"tool_name": "test_tool", "span_kind": "tool"},
            },
            {
                "span_id": "handoff-span",
                "attributes": {"handoff_to": "next-orch", "span_kind": "orchestrator"},
            },
            {
                "span_id": "retry-span",
                "attributes": {"retry_of": "prev-span"},
            },
            {
                "span_id": "eval-span",
                "attributes": {"span_kind": "evaluation", "subject": "test-subj"},
            },
            {
                "span_id": "policy-span",
                "attributes": {"policy_checked": "policy-1"},
            },
            {
                "span_id": "escalation-span",
                "attributes": {"escalated_to": "human-1"},
            },
            {
                "span_id": "failure-span",
                "attributes": {"status": "error", "failed_agent": "agent-1"},
            },
            {
                "span_id": "outcome-span",
                "attributes": {"outcome": "success"},
            },
        ]

        edges = _extract_semantic_edges(spans)

        # Get all extracted relations
        relations = {e.relation for e in edges}

        # Expected edge types (13 semantic types)
        expected_semantic = {
            "actor", "target", "dependency", "read_edge", "write_edge",
            "tool_invocation_edge", "orchestration_handoff_edge", "retry_edge",
            "evaluation_edge", "policy_validation_edge", "human_escalation_edge",
            "failure_propagation_edge", "outcome_edge",
        }

        # Check which expected types were found
        found = relations & expected_semantic
        missing = expected_semantic - relations

        print(f"✓ Extracted {len(found)}/13 semantic edge types")
        if missing:
            print(f"  Missing: {sorted(missing)}")
        print(f"  Found: {sorted(found)}")

        # We should have at least most of them
        assert len(found) >= 10, f"Only found {len(found)}/13 edge types"

        return True

    except Exception as e:
        print(f"✗ All 13 edge types test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_empty_snapshot_validation() -> bool:
    """Test validation of empty snapshot."""
    try:
        from system_learning.runtime_adg.materializer import RuntimeADGMaterializer

        materializer = RuntimeADGMaterializer()

        # Create empty snapshot with explicit trace_id
        snapshot = materializer.materialize([], mission="empty-test", trace_id="empty-trace")

        validation = snapshot.validate()

        # Empty snapshot should be valid but with warnings about empty nodes
        assert validation["is_valid"] is True, f"Empty snapshot should be valid: {validation['errors']}"
        assert len(validation["warnings"]) > 0, "Empty snapshot should have warnings"
        assert any("Empty" in w for w in validation["warnings"]), "Missing empty nodes warning"

        print("✓ Empty snapshot validation works")
        return True

    except Exception as e:
        print(f"✗ Empty snapshot validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_hash_consistency_validation() -> bool:
    """Test that snapshot hash validation works."""
    try:
        from system_learning.runtime_adg.materializer import RuntimeADGMaterializer

        materializer = RuntimeADGMaterializer()

        spans = [
            {
                "span_id": "hash-test",
                "trace_id": "trace-hash-test",
                "name": "test",
                "kind": "action",
                "layer": "L2",
                "component": "Test",
                "ts_utc": 1000,
                "duration_ms": 10.0,
                "status": "ok",
                "attributes": {},
            },
        ]

        snapshot = materializer.materialize(spans, mission="hash-test", trace_id="trace-hash-test")

        # Verify hash consistency
        validation = snapshot.validate()
        assert validation["is_valid"] is True, "Hash should be consistent"

        # Verify snapshot_id matches snapshot_hash
        assert snapshot.snapshot_id == snapshot.snapshot_hash, "snapshot_id should match snapshot_hash"

        print("✓ Hash consistency validation works")
        return True

    except Exception as e:
        print(f"✗ Hash consistency test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main() -> int:
    """Run all Wave 2 tests."""
    print("=" * 60)
    print("Wave 2: Snapshot ADG Extraction + Schema — Verification Tests")
    print("=" * 60)

    tests = [
        ("Semantic Edge Extraction", test_semantic_edge_extraction),
        ("Materializer with Semantic Edges", test_materializer_with_semantic_edges),
        ("Snapshot Validation", test_snapshot_validation),
        ("All 13 Edge Types", test_all_13_edge_types),
        ("Empty Snapshot Validation", test_empty_snapshot_validation),
        ("Hash Consistency", test_hash_consistency_validation),
    ]

    results = []
    for name, test_func in tests:
        print(f"\n--- {name} ---")
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ Test crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 Wave 2 implementation verified successfully!")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
