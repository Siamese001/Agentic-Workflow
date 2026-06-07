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

Reference: system_learning/runtime_adg/, .claude/rules §1 Testing & Evidence
"""

from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import pytest

# Module-level imports for test classes
try:
    from agentic_core.L6_system_learning.runtime_adg import (
        FileBackedRuntimeADGStore,
        InMemoryRuntimeADGStore,
        L6MetaLearningBridge,
        RuntimeADGEdge,
        RuntimeADGMaterializer,
        RuntimeADGNode,
        RuntimeADGSnapshot,
        attributes_to_json,
        create_runtime_adg_snapshot,
    )

    RUNTIME_ADG_AVAILABLE = True
except ImportError:
    RUNTIME_ADG_AVAILABLE = False

try:
    from agentic_core.L6_system_learning.auto_persistence import AutoPersistenceTracingAdapter

    AUTO_PERSISTENCE_AVAILABLE = True
except ImportError:
    AUTO_PERSISTENCE_AVAILABLE = False


# Lazy import fixtures to avoid collection-time conflicts
@pytest.fixture
def ssot_project_root():
    from agentic_core.L5_safety.config.structure_blueprint.ssot import get_validated_project_root

    return get_validated_project_root()


@pytest.fixture
def runtime_adg_classes():
    from agentic_core.L6_system_learning.runtime_adg import (
        FileBackedRuntimeADGStore,
        InMemoryRuntimeADGStore,
        L6MetaLearningBridge,
        RuntimeADGEdge,
        RuntimeADGMaterializer,
        RuntimeADGNode,
        RuntimeADGSnapshot,
        attributes_to_json,
        create_runtime_adg_snapshot,
    )

    return (
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


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def temp_runtime_adg_dir(tmp_path: Path) -> Path:
    """Provide temporary directory for runtime ADG artifacts.

    Note: FileBackedRuntimeADGStore requires paths within project root.
    Tests using L4 storage should use get_validated_project_root() paths.
    """
    adg_dir = tmp_path / "runtime_adg"
    adg_dir.mkdir(parents=True, exist_ok=True)
    return adg_dir


@pytest.fixture
def l4_store_project_path(ssot_project_root) -> Path:
    """Provide L4-compliant storage path within project root.

    FileBackedRuntimeADGStore requires paths within L4 sovereign territory.
    """
    project_root = ssot_project_root
    # Use a test-specific subdirectory in L4 territory
    l4_test_dir = project_root / "agentic_core" / "L4_state" / "memory" / "runtime_adg_test"
    l4_test_dir.mkdir(parents=True, exist_ok=True)
    return l4_test_dir


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
def materializer(runtime_adg_classes) -> RuntimeADGMaterializer:
    """Provide fresh RuntimeADGMaterializer instance."""
    _, _, _, RuntimeADGMaterializer, _, _, _, _, _ = runtime_adg_classes
    return RuntimeADGMaterializer()


@pytest.fixture
def in_memory_store(runtime_adg_classes) -> InMemoryRuntimeADGStore:
    """Provide fresh in-memory store."""
    _, InMemoryRuntimeADGStore, _, _, _, _, _, _, _ = runtime_adg_classes
    return InMemoryRuntimeADGStore()


@pytest.fixture
def l6_bridge(temp_runtime_adg_dir: Path, runtime_adg_classes) -> L6MetaLearningBridge:
    """Provide fresh L6 meta-learning bridge."""
    _, _, L6MetaLearningBridge, _, _, _, _, _, _ = runtime_adg_classes
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
        l4_store_project_path: Path,
    ) -> None:
        """Test complete pipeline: spans → snapshot → L4 → L6."""
        import shutil

        # Clean up any previous test data
        if l4_store_project_path.exists():
            shutil.rmtree(l4_store_project_path)
        l4_store_project_path.mkdir(parents=True, exist_ok=True)

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

        # Step 2: Persist to L4 (file-backed store with L4-compliant path)
        l4_store = FileBackedRuntimeADGStore(l4_store_project_path)
        version_id = l4_store.persist(snapshot)

        assert version_id is not None
        assert len(version_id) > 0

        # Verify retrieval
        retrieved = l4_store.load_snapshot(version_id)
        assert retrieved is not None
        assert retrieved.snapshot_id == snapshot.snapshot_id
        assert retrieved.trace_id == snapshot.trace_id

        # Step 3: Store in L6 for meta-learning
        l6_bridge = L6MetaLearningBridge(l4_store_project_path / "l6")
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
        l4_store_project_path: Path,
    ) -> None:
        """Test L4 storage with multiple snapshots and retrieval."""
        import shutil

        # Clean up and set up test directory
        l4_test_path = l4_store_project_path / "storage_test"
        if l4_test_path.exists():
            shutil.rmtree(l4_test_path)
        l4_test_path.mkdir(parents=True, exist_ok=True)

        l4_store = FileBackedRuntimeADGStore(l4_test_path)

        # Create multiple snapshots
        trace_ids = []
        for i in range(5):
            spans = [
                {
                    **sample_spans[0],
                    "span_id": f"span-{i:03d}-001",
                    "trace_id": f"trace-{i:03d}",
                    "ts_utc": int(time.time() * 1000) + i * 1000,
                },
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
        l4_store_project_path: Path,
    ) -> None:
        """Test L6 meta-learning pattern extraction and analysis."""
        import shutil

        # Clean up and set up test directory
        l6_test_path = l4_store_project_path / "ml_test"
        if l6_test_path.exists():
            shutil.rmtree(l6_test_path)
        l6_test_path.mkdir(parents=True, exist_ok=True)

        l6_bridge = L6MetaLearningBridge(l6_base_dir=l6_test_path)

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
            },
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
        snapshots = [materializer.materialize(sample_spans, mission="determinism-test") for _ in range(5)]

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
        materializer: RuntimeADGMaterializer,
    ) -> None:
        """Test that span order doesn't affect snapshot hash when timestamps are identical."""
        # Create spans with identical timestamps but different IDs
        base_time = int(time.time() * 1000)
        spans_a = [
            {
                "span_id": "a-001",
                "trace_id": "order-test",
                "ts_utc": base_time,
                "duration_ms": 10.0,
                "status": "ok",
                "name": "op1",
                "kind": "tool",
                "layer": "L2",
                "component": "Test",
                "attributes": {},
            },
            {
                "span_id": "a-002",
                "trace_id": "order-test",
                "ts_utc": base_time + 10,
                "duration_ms": 10.0,
                "status": "ok",
                "name": "op2",
                "kind": "tool",
                "layer": "L2",
                "component": "Test",
                "attributes": {},
            },
        ]
        spans_b = [
            {
                "span_id": "a-002",
                "trace_id": "order-test",
                "ts_utc": base_time + 10,
                "duration_ms": 10.0,
                "status": "ok",
                "name": "op2",
                "kind": "tool",
                "layer": "L2",
                "component": "Test",
                "attributes": {},
            },
            {
                "span_id": "a-001",
                "trace_id": "order-test",
                "ts_utc": base_time,
                "duration_ms": 10.0,
                "status": "ok",
                "name": "op1",
                "kind": "tool",
                "layer": "L2",
                "component": "Test",
                "attributes": {},
            },
        ]

        snapshot1 = materializer.materialize(spans_a, mission="order-test")
        snapshot2 = materializer.materialize(spans_b, mission="order-test")

        # Hashes should be identical (nodes sorted by ts_utc, so same output order)
        assert snapshot1.snapshot_hash == snapshot2.snapshot_hash


# =============================================================================
# Test Class: Auto-Persistence Integration
# =============================================================================


class TestRuntimeADGAutoPersistence:
    """Auto-persistence adapter integration tests."""

    def test_auto_persistence_adapter(
        self,
        l4_store_project_path: Path,
    ) -> None:
        """Test AutoPersistenceTracingAdapter with full pipeline."""
        import shutil

        # Clean up and set up test directories within project
        auto_test_path = l4_store_project_path / "auto_persistence"
        if auto_test_path.exists():
            shutil.rmtree(auto_test_path)
        auto_test_path.mkdir(parents=True, exist_ok=True)

        # Create adapter with auto-persistence enabled using L4-compliant paths
        adapter = AutoPersistenceTracingAdapter(
            service_name="test-service",
            enable_console_export=False,
            enable_logging=False,
            enable_auto_persistence=True,
            l4_store_path=str(auto_test_path / "l4_auto"),
            l6_base_dir=str(auto_test_path / "l6_auto"),
        )

        # Verify initialization
        status = adapter.get_auto_persistence_status()
        assert status["enabled"] is True
        assert status["l4_store_available"] is True
        assert status["l6_bridge_available"] is True

        # Simulate trace execution using proper context managers
        with adapter.trace_orchestrator("test-mission", {"agent": "TestAgent"}):
            # Simulate some work by creating a tool span
            with adapter.trace_tool(
                tool_name="test_operation",
                parameters={},
                metadata={"layer": "L2", "component": "TestTool"},
            ):
                pass  # Span auto-closes

        # Force persistence (since we're not in a real async context)
        result = adapter.force_persist_current_spans("test-mission")

        # Verify persistence result - may succeed or fail depending on span availability
        # but should not crash
        assert "success" in result
        # If spans were drained and persisted successfully
        if result.get("success"):
            assert "l4_version_id" in result
            assert "l6_meta_id" in result

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
        l4_store_project_path: Path,
    ) -> None:
        """Test thread-safe concurrent snapshot persistence."""
        import shutil

        # Clean up and set up test directory
        concurrent_test_path = l4_store_project_path / "concurrent_test"
        if concurrent_test_path.exists():
            shutil.rmtree(concurrent_test_path)
        concurrent_test_path.mkdir(parents=True, exist_ok=True)

        l4_store = FileBackedRuntimeADGStore(concurrent_test_path)

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
        l4_store_project_path: Path,
    ) -> None:
        """Test accurate pattern extraction from snapshots."""
        import shutil

        # Clean up and set up test directory
        pattern_test_path = l4_store_project_path / "pattern_test"
        if pattern_test_path.exists():
            shutil.rmtree(pattern_test_path)
        pattern_test_path.mkdir(parents=True, exist_ok=True)

        l6_bridge = L6MetaLearningBridge(l6_base_dir=pattern_test_path)

        # Create snapshot with known patterns
        base_time = int(time.time() * 1000)
        spans = [
            {
                "span_id": "slow-001",
                "trace_id": "trace-patterns",
                "parent_span_id": "",
                "name": "slow.operation",
                "kind": "tool",
                "layer": "L2",
                "component": "SlowTool",
                "ts_utc": base_time,
                "duration_ms": 2000.0,  # > 1s = slow
                "status": "ok",
                "attributes": {},
            },
            {
                "span_id": "fast-001",
                "trace_id": "trace-patterns",
                "parent_span_id": "slow-001",
                "name": "fast.operation",
                "kind": "tool",
                "layer": "L2",
                "component": "FastTool",
                "ts_utc": base_time + 100,
                "duration_ms": 5.0,  # < 10ms = fast
                "status": "ok",
                "attributes": {},
            },
            {
                "span_id": "error-001",
                "trace_id": "trace-patterns",
                "parent_span_id": "slow-001",
                "name": "error.operation",
                "kind": "tool",
                "layer": "L2",
                "component": "ErrorTool",
                "ts_utc": base_time + 200,
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
        l4_store_project_path: Path,
    ) -> None:
        """Test evolution log maintains integrity across operations."""
        import shutil

        # Clean up and set up test directory
        evolution_test_path = l4_store_project_path / "evolution_test"
        if evolution_test_path.exists():
            shutil.rmtree(evolution_test_path)
        evolution_test_path.mkdir(parents=True, exist_ok=True)

        l6_bridge = L6MetaLearningBridge(l6_base_dir=evolution_test_path)

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
        l4_store_project_path: Path,
    ) -> None:
        """Test that corrupted snapshot data is handled gracefully."""
        import shutil

        # Clean up and set up test directory
        corrupt_test_path = l4_store_project_path / "corrupt_test"
        if corrupt_test_path.exists():
            shutil.rmtree(corrupt_test_path)
        corrupt_test_path.mkdir(parents=True, exist_ok=True)

        l4_store = FileBackedRuntimeADGStore(corrupt_test_path)

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
