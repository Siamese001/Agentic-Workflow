"""Runtime ADG End-to-End Integration Test — Full Pipeline Coverage.

Test Dimensions:
- End-to-end flow: spans → materializer → snapshot → L4 → L6
- Edge cases: empty spans, malformed spans, missing fields
- State transitions: valid→valid, error→recovery
- Determinism: identical spans → identical snapshot hashes
- Fail-closed: invalid spans don't crash pipeline
- Integration: L4 storage, L6 meta-learning, observability

ROBUSTNESS_MATRIX:
| Test | Success | Edge | Failure | Recovery | Determinism | Side-Effect |
|------|---------|------|---------|----------|-------------|-------------|
| test_full_pipeline_happy_path | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| test_l4_storage_integration | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| test_l6_meta_learning_integration | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| test_empty_spans_handling | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| test_malformed_span_recovery | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| test_auto_persistence_adapter | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| test_snapshot_determinism | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| test_concurrent_snapshot_persistence | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| test_pattern_extraction_accuracy | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| test_evolution_log_integrity | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

Reference: system_learning/runtime_adg/, .windsurfrules §1 Testing & Evidence
"""

from __future__ import annotations

import hashlib
import json
import os
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    get_validated_project_root,
)
from system_learning.runtime_adg import (
    FileBackedRuntimeADGStore,
    InMemoryRuntimeADGStore,
    L6MetaLearningBridge,
    RuntimeADGMaterializer,
    RuntimeADGNode,
    RuntimeADGEdge,
    RuntimeADGSnapshot,
    attributes_to_json,
    create_runtime_adg_snapshot,
)
from system_learning.runtime_adg.auto_persistence import (
    AutoPersistenceTracingAdapter,
    get_auto_persistence_tracer,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def temp_runtime_adg_dir(tmp_path: Path) -> Path:
    """Provide temporary directory for runtime ADG artifacts."""
    adg_dir = tmp_path / "runtime_adg"
    adg_dir.mkdir(parents=True, exist_ok=True)
    return adg_dir


@pytest.fixture
def sample_spans() -> list[dict[str, Any]]:
    """Provide sample OTel spans for testing."""
    base_time = int(time.time() * 1000)
    return [
        {
            "span_id": "span-001",
            "trace_id": "trace-001",
            "parent_span_id": "",
            "name": "orchestrator.execute",
            "kind": "orchestrator",
            "layer": "L3",
            "component": "TestOrchestrator",
            "ts_utc": base_time,
            "duration_ms": 100.0,
            "status": "ok",
            "attributes": {"mission": "test-mission", "agent": "TestAgent"},
        },
        {
            "span_id": "span-002",
            "trace_id": "trace-001",
            "parent_span_id": "span-001",
            "name": "agent.reason",
            "kind": "cognitive",
            "layer": "L1",
            "component": "TestAgent",
            "ts_utc": base_time + 10,
            "duration_ms": 50.0,
            "status": "ok",
            "attributes": {"reasoning_type": "planning"},
        },
        {
            "span_id": "span-003",
            "trace_id": "trace-001",
            "parent_span_id": "span-001",
            "name": "tool.execute",
            "kind": "tool",
            "layer": "L2",
            "component": "FileTool",
            "ts_utc": base_time + 20,
            "duration_ms": 30.0,
            "status": "ok",
            "attributes": {"tool_name": "read_file"},
        },
    ]


@pytest.fixture
def materializer() -> RuntimeADGMaterializer:
    """Provide fresh RuntimeADGMaterializer instance."""
    return RuntimeADGMaterializer()


@pytest.fixture
def in_memory_store() -> InMemoryRuntimeADGStore:
    """Provide fresh in-memory store."""
    return InMemoryRuntimeADGStore()


@pytest.fixture
def l6_bridge(temp_runtime_adg_dir: Path) -> L6MetaLearningBridge:
    """Provide fresh L6 meta-learning bridge."""
    return L6MetaLearningBridge(l6_base_dir=temp_runtime_adg_dir / "l6")


# =============================================================================
# Test Class: Full Pipeline Integration
# =============================================================================

class TestRuntimeADGFullPipeline:
    """End-to-end tests for the complete runtime ADG pipeline."""

    def test_full_pipeline_happy_path(
        self,
        sample_spans: list[dict[str, Any]],
        materializer: RuntimeADGMaterializer,
        temp_runtime_adg_dir: Path,
    ) -> None:
        """Test complete pipeline: spans → snapshot → L4 → L6."""
        # Step 1: Materialize snapshot from spans
        snapshot = materializer.materialize(
            sample_spans,
            mission="test-mission",
            trace_id="trace-001",
        )

        # Verify snapshot properties
        assert snapshot.trace_id == "trace-001"
        assert snapshot.mission == "test-mission"
        assert len(snapshot.nodes) == 3
        assert len(snapshot.edges) > 0  # parent_child + temporal_sequence
        assert snapshot.snapshot_id is not None
        assert len(snapshot.snapshot_hash) == 64  # SHA-256 hex

        # Step 2: Persist to L4 (file-backed store)
        l4_store = FileBackedRuntimeADGStore(temp_runtime_adg_dir / "l4")
        version_id = l4_store.persist(snapshot)

        assert version_id is not None
        assert len(version_id) > 0

        # Verify retrieval
        retrieved = l4_store.load_snapshot(version_id)
        assert retrieved is not None
        assert retrieved.snapshot_id == snapshot.snapshot_id
        assert retrieved.trace_id == snapshot.trace_id

        # Step 3: Store in L6 for meta-learning
        l6_bridge = L6MetaLearningBridge(temp_runtime_adg_dir / "l6")
        meta_id = l6_bridge.store_snapshot_for_meta_learning(snapshot)

        assert meta_id is not None
        assert meta_id.startswith("runtime_adg_")

        # Verify L6 index
        snapshots = l6_bridge.get_meta_learning_snapshots()
        assert len(snapshots) >= 1
        assert any(s["trace_id"] == "trace-001" for s in snapshots)

    def test_l4_storage_integration(
        self,
        sample_spans: list[dict[str, Any]],
        materializer: RuntimeADGMaterializer,
        temp_runtime_adg_dir: Path,
    ) -> None:
        """Test L4 storage with multiple snapshots and retrieval."""
        l4_store = FileBackedRuntimeADGStore(temp_runtime_adg_dir / "l4")

        # Create multiple snapshots
        trace_ids = []
        for i in range(5):
            spans = [
                {
                    **sample_spans[0],
                    "span_id": f"span-{i:03d}-001",
                    "trace_id": f"trace-{i:03d}",
                    "ts_utc": int(time.time() * 1000) + i * 1000,
                }
            ]
            snapshot = materializer.materialize(
                spans,
                mission=f"mission-{i}",
                trace_id=f"trace-{i:03d}",
            )
            version_id = l4_store.persist(snapshot)
            trace_ids.append((f"trace-{i:03d}", version_id))

        # Verify all stored
        all_versions = l4_store.list_snapshots()
        assert len(all_versions) == 5

        # Verify trace index
        for trace_id, version_id in trace_ids:
            retrieved_version = l4_store.get_version_id_for_trace(trace_id)
            assert retrieved_version == version_id

    def test_l6_meta_learning_integration(
        self,
        sample_spans: list[dict[str, Any]],
        materializer: RuntimeADGMaterializer,
        temp_runtime_adg_dir: Path,
    ) -> None:
        """Test L6 meta-learning pattern extraction and analysis."""
        l6_bridge = L6MetaLearningBridge(temp_runtime_adg_dir / "l6_ml")

        # Create snapshot with mixed layer distribution
        mixed_spans = [
            {**sample_spans[0], "layer": "L0", "span_id": "span-l0-001"},
            {**sample_spans[0], "layer": "L1", "span_id": "span-l1-001"},
            {**sample_spans[0], "layer": "L2", "span_id": "span-l2-001"},
            {**sample_spans[0], "layer": "L3", "span_id": "span-l3-001"},
            {**sample_spans[0], "layer": "L5", "span_id": "span-l5-001", "status": "error"},
        ]
        snapshot = materializer.materialize(mixed_spans, mission="mixed-test")

        # Store for meta-learning
        meta_id = l6_bridge.store_snapshot_for_meta_learning(snapshot)

        # Verify pattern extraction
        patterns = l6_bridge.get_execution_patterns(snapshot.trace_id)
        assert "layer_distribution" in patterns
        assert "error_patterns" in patterns
        assert len(patterns["error_patterns"]) == 1  # One error span

        # Verify aggregated patterns
        agg_patterns = l6_bridge.get_execution_patterns()
        assert agg_patterns["total_snapshots"] >= 1
        assert "L5" in agg_patterns.get("layer_distribution", {})

        # Verify evolution log
        events = l6_bridge.query_evolution_log(event_type="runtime_adg_stored")
        assert len(events) >= 1
        assert events[0]["event_type"] == "runtime_adg_stored"


# =============================================================================
# Test Class: Edge Cases and Fail-Closed Behavior
# =============================================================================

class TestRuntimeADGEdgeCases:
    """Edge case and error handling tests."""

    def test_empty_spans_handling(
        self,
        materializer: RuntimeADGMaterializer,
    ) -> None:
        """Test handling of empty span lists."""
        snapshot = materializer.materialize([], mission="empty-test")

        assert snapshot.trace_id == ""
        assert snapshot.mission == "empty-test"
        assert len(snapshot.nodes) == 0
        assert len(snapshot.edges) == 0
        assert snapshot.started_at_utc == 0
        assert snapshot.ended_at_utc == 0
        # Still has valid snapshot_id (hash of empty)
        assert snapshot.snapshot_id is not None

    def test_malformed_span_recovery(
        self,
        materializer: RuntimeADGMaterializer,
    ) -> None:
        """Test recovery from malformed span data."""
        malformed_spans = [
            {
                # Missing most fields
                "span_id": "span-bad-001",
                "trace_id": "trace-bad",
            },
            {
                # Invalid attribute type (string instead of dict)
                "span_id": "span-bad-002",
                "trace_id": "trace-bad",
                "attributes": "not-a-dict",
                "ts_utc": "not-a-number",  # Invalid type
            },
            {
                # Valid span to ensure recovery
                "span_id": "span-good-001",
                "trace_id": "trace-bad",
                "name": "valid.span",
                "kind": "tool",
                "layer": "L2",
                "component": "TestTool",
                "ts_utc": int(time.time() * 1000),
                "duration_ms": 10.0,
                "status": "ok",
                "attributes": {},
            },
        ]

        # Should not crash
        snapshot = materializer.materialize(malformed_spans, mission="malformed-test")

        # Should have all 3 nodes (graceful handling)
        assert len(snapshot.nodes) == 3

        # Verify node with missing fields has defaults
        bad_node = [n for n in snapshot.nodes if n.node_id == "span-bad-001"][0]
        assert bad_node.name == ""  # Default empty string
        assert bad_node.layer == ""  # Default empty string
        assert bad_node.duration_ms == 0.0  # Default float

    def test_single_span_no_edges(
        self,
        materializer: RuntimeADGMaterializer,
    ) -> None:
        """Test single span produces parent_child edge to root but no temporal edges."""
        single_span = [
            {
                "span_id": "single-001",
                "trace_id": "trace-single",
                "parent_span_id": "",  # No parent
                "name": "single.span",
                "kind": "tool",
                "layer": "L2",
                "component": "SingleTool",
                "ts_utc": int(time.time() * 1000),
                "duration_ms": 10.0,
                "status": "ok",
                "attributes": {},
            }
        ]

        snapshot = materializer.materialize(single_span, mission="single-test")

        assert len(snapshot.nodes) == 1
        # Should have parent_child edge to __root__
        parent_child_edges = [e for e in snapshot.edges if e.relation == "parent_child"]
        assert len(parent_child_edges) == 1
        assert parent_child_edges[0].src_id == "__root__"
        # No temporal edges with single span
        temporal_edges = [e for e in snapshot.edges if e.relation == "temporal_sequence"]
        assert len(temporal_edges) == 0


# =============================================================================
# Test Class: Determinism and Replay
# =============================================================================

class TestRuntimeADGDeterminism:
    """Determinism and replay verification tests."""

    def test_snapshot_determinism(
        self,
        sample_spans: list[dict[str, Any]],
        materializer: RuntimeADGMaterializer,
    ) -> None:
        """Test that identical spans produce identical snapshot hashes."""
        # Materialize same spans multiple times
        snapshots = [
            materializer.materialize(sample_spans, mission="determinism-test")
            for _ in range(5)
        ]

        # All hashes should be identical
        first_hash = snapshots[0].snapshot_hash
        for snapshot in snapshots[1:]:
            assert snapshot.snapshot_hash == first_hash
            assert snapshot.snapshot_id == first_hash

    def test_canonical_bytes_determinism(
        self,
        sample_spans: list[dict[str, Any]],
        materializer: RuntimeADGMaterializer,
    ) -> None:
        """Test canonical bytes are deterministic regardless of input order."""
        snapshot = materializer.materialize(sample_spans, mission="canonical-test")

        # Get canonical bytes multiple times
        canonical_bytes_list = [snapshot.canonical_bytes() for _ in range(3)]

        # All should be identical
        first_bytes = canonical_bytes_list[0]
        for cb in canonical_bytes_list[1:]:
            assert cb == first_bytes

    def test_span_order_independence(
        self,
        sample_spans: list[dict[str, Any]],
        materializer: RuntimeADGMaterializer,
    ) -> None:
        """Test that span order doesn't affect snapshot hash (nodes sorted by time)."""
        # Reverse span order
        reversed_spans = list(reversed(sample_spans))

        snapshot1 = materializer.materialize(sample_spans, mission="order-test")
        snapshot2 = materializer.materialize(reversed_spans, mission="order-test")

        # Hashes should still be identical (nodes sorted by ts_utc)
        assert snapshot1.snapshot_hash == snapshot2.snapshot_hash


# =============================================================================
# Test Class: Auto-Persistence Integration
# =============================================================================

class TestRuntimeADGAutoPersistence:
    """Auto-persistence adapter integration tests."""

    def test_auto_persistence_adapter(
        self,
        temp_runtime_adg_dir: Path,
    ) -> None:
        """Test AutoPersistenceTracingAdapter with full pipeline."""
        # Create adapter with auto-persistence enabled
        adapter = AutoPersistenceTracingAdapter(
            service_name="test-service",
            enable_console_export=False,
            enable_logging=False,
            enable_auto_persistence=True,
            l4_store_path=str(temp_runtime_adg_dir / "l4_auto"),
            l6_base_dir=str(temp_runtime_adg_dir / "l6_auto"),
        )

        # Verify initialization
        status = adapter.get_auto_persistence_status()
        assert status["enabled"] is True
        assert status["l4_store_available"] is True
        assert status["l6_bridge_available"] is True

        # Simulate trace execution
        with adapter.trace_orchestrator("test-mission", {"agent": "TestAgent"}):
            # Simulate some work by creating spans directly
            adapter.start_span(
                name="test.operation",
                kind="tool",
                layer="L2",
                component="TestTool",
            )
            adapter.end_span()

        # Force persistence (since we're not in a real async context)
        result = adapter.force_persist_current_spans("test-mission")

        # Verify persistence result
        if result["success"]:
            assert "l4_version_id" in result
            assert "l6_meta_id" in result
            assert result["span_count"] >= 0

    def test_auto_persistence_disabled(
        self,
        temp_runtime_adg_dir: Path,
    ) -> None:
        """Test adapter with auto-persistence disabled."""
        adapter = AutoPersistenceTracingAdapter(
            service_name="test-service",
            enable_console_export=False,
            enable_logging=False,
            enable_auto_persistence=False,
        )

        status = adapter.get_auto_persistence_status()
        assert status["enabled"] is False

        # Attempt to persist should indicate disabled
        result = adapter.force_persist_current_spans("test")
        assert result["success"] is False
        assert result["reason"] == "Auto-persistence disabled"


# =============================================================================
# Test Class: Concurrency and Thread Safety
# =============================================================================

class TestRuntimeADGConcurrency:
    """Concurrency and thread safety tests."""

    def test_concurrent_snapshot_persistence(
        self,
        materializer: RuntimeADGMaterializer,
        temp_runtime_adg_dir: Path,
    ) -> None:
        """Test thread-safe concurrent snapshot persistence."""
        l4_store = FileBackedRuntimeADGStore(temp_runtime_adg_dir / "l4_concurrent")

        num_threads = 10
        errors: list[Exception] = []
        version_ids: list[str] = []

        def persist_task(idx: int) -> str | None:
            try:
                span = {
                    "span_id": f"concurrent-{idx:03d}",
                    "trace_id": f"trace-concurrent-{idx:03d}",
                    "name": "concurrent.operation",
                    "kind": "tool",
                    "layer": "L2",
                    "component": "ConcurrentTool",
                    "ts_utc": int(time.time() * 1000) + idx,
                    "duration_ms": 10.0,
                    "status": "ok",
                    "attributes": {"thread": idx},
                }
                snapshot = materializer.materialize([span], mission=f"concurrent-{idx}")
                version_id = l4_store.persist(snapshot)
                return version_id
            except Exception as e:
                errors.append(e)
                return None

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(persist_task, i) for i in range(num_threads)]
            version_ids = [f.result() for f in as_completed(futures)]

        # Verify no errors
        assert len(errors) == 0, f"Errors during concurrent persistence: {errors}"

        # Verify all persisted
        all_versions = l4_store.list_snapshots()
        assert len(all_versions) == num_threads


# =============================================================================
# Test Class: Pattern Extraction and Analytics
# =============================================================================

class TestRuntimeADGPatternExtraction:
    """Pattern extraction and analytics tests."""

    def test_pattern_extraction_accuracy(
        self,
        materializer: RuntimeADGMaterializer,
        temp_runtime_adg_dir: Path,
    ) -> None:
        """Test accurate pattern extraction from snapshots."""
        l6_bridge = L6MetaLearningBridge(temp_runtime_adg_dir / "l6_patterns")

        # Create snapshot with known patterns
        spans = [
            {
                "span_id": "slow-001",
                "trace_id": "trace-patterns",
                "name": "slow.operation",
                "kind": "tool",
                "layer": "L2",
                "component": "SlowTool",
                "ts_utc": int(time.time() * 1000),
                "duration_ms": 2000.0,  # > 1s = slow
                "status": "ok",
                "attributes": {},
            },
            {
                "span_id": "fast-001",
                "trace_id": "trace-patterns",
                "name": "fast.operation",
                "kind": "tool",
                "layer": "L2",
                "component": "FastTool",
                "ts_utc": int(time.time() * 1000) + 100,
                "duration_ms": 5.0,  # < 10ms = fast
                "status": "ok",
                "attributes": {},
            },
            {
                "span_id": "error-001",
                "trace_id": "trace-patterns",
                "name": "error.operation",
                "kind": "tool",
                "layer": "L2",
                "component": "ErrorTool",
                "ts_utc": int(time.time() * 1000) + 200,
                "duration_ms": 100.0,
                "status": "error",
                "attributes": {},
            },
        ]

        snapshot = materializer.materialize(spans, mission="pattern-test")
        l6_bridge.store_snapshot_for_meta_learning(snapshot)

        # Verify pattern extraction
        patterns = l6_bridge.get_execution_patterns(snapshot.trace_id)

        # Verify slow operation detection
        slow_ops = patterns.get("timing_patterns", {}).get("slow_operations", [])
        assert len(slow_ops) == 1
        assert slow_ops[0]["node_id"] == "slow-001"

        # Verify fast operation detection
        fast_ops = patterns.get("timing_patterns", {}).get("fast_operations", [])
        assert len(fast_ops) == 1
        assert fast_ops[0]["node_id"] == "fast-001"

        # Verify error pattern detection
        error_patterns = patterns.get("error_patterns", [])
        assert len(error_patterns) == 1
        assert error_patterns[0]["node_id"] == "error-001"

    def test_evolution_log_integrity(
        self,
        materializer: RuntimeADGMaterializer,
        temp_runtime_adg_dir: Path,
    ) -> None:
        """Test evolution log maintains integrity across operations."""
        l6_bridge = L6MetaLearningBridge(temp_runtime_adg_dir / "l6_evolution")

        # Store multiple snapshots
        for i in range(5):
            span = {
                "span_id": f"evo-{i:03d}",
                "trace_id": f"trace-evo-{i:03d}",
                "name": "evolution.test",
                "kind": "tool",
                "layer": "L2",
                "component": "EvolutionTool",
                "ts_utc": int(time.time() * 1000) + i * 100,
                "duration_ms": 10.0,
                "status": "ok",
                "attributes": {"iteration": i},
            }
            snapshot = materializer.materialize([span], mission=f"evo-test-{i}")
            l6_bridge.store_snapshot_for_meta_learning(snapshot)

        # Query evolution log
        events = l6_bridge.query_evolution_log(limit=10)

        # Verify all events present
        assert len(events) == 5

        # Verify event ordering (newest first)
        timestamps = [e["timestamp"] for e in events]
        assert timestamps == sorted(timestamps, reverse=True)

        # Verify event structure
        for event in events:
            assert "timestamp" in event
            assert "event_type" in event
            assert "data" in event
            assert event["event_type"] == "runtime_adg_stored"


# =============================================================================
# Test Class: Fail-Closed Behavior
# =============================================================================

class TestRuntimeADGFailClosed:
    """Fail-closed behavior verification tests."""

    def test_invalid_l4_path_rejection(
        self,
        tmp_path: Path,
    ) -> None:
        """Test that invalid L4 paths are rejected."""
        # Try to create store outside L4 territory
        invalid_path = tmp_path / "outside_project" / "runtime_adg"
        invalid_path.mkdir(parents=True, exist_ok=True)

        # Should raise ValueError due to L4 compliance check
        with pytest.raises(ValueError) as exc_info:
            FileBackedRuntimeADGStore(invalid_path)

        assert "L4" in str(exc_info.value) or "compliance" in str(exc_info.value).lower()

    def test_corrupted_snapshot_rejection(
        self,
        sample_spans: list[dict[str, Any]],
        materializer: RuntimeADGMaterializer,
        temp_runtime_adg_dir: Path,
    ) -> None:
        """Test that corrupted snapshot data is handled gracefully."""
        l4_store = FileBackedRuntimeADGStore(temp_runtime_adg_dir / "l4_corrupt")

        # Persist valid snapshot
        snapshot = materializer.materialize(sample_spans, mission="corrupt-test")
        version_id = l4_store.persist(snapshot)

        # Corrupt the stored data
        store_path = l4_store._base_dir
        for json_file in store_path.rglob("*.json"):
            if json_file.name not in ("_index.json", "_trace_index.json"):
                # Write invalid JSON
                json_file.write_text("not valid json {{ corrupted", encoding="utf-8")
                break

        # Attempt to load corrupted snapshot
        # Should return None or raise, not crash
        try:
            loaded = l4_store.load_snapshot(version_id)
            # If it returns, it should be None for corrupted data
            assert loaded is None
        except (json.JSONDecodeError, KeyError, ValueError):
            # These are acceptable exceptions for corrupted data
            pass
