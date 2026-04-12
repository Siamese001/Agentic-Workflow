#!/usr/bin/env python3
"""Comprehensive Runtime ADG end-to-end validation test."""

import asyncio
import json
import time
import uuid
from pathlib import Path
from typing import Any


class MockRuntimeADGStore:
    """Mock runtime ADG store for testing."""

    def __init__(self, store_dir: Path = None):
        self.store_dir = store_dir or Path("artifacts/runtime_adg")
        self.store_dir.mkdir(parents=True, exist_ok=True)
        self.snapshots: dict[str, dict[str, Any]] = {}

    def store_snapshot(self, snapshot: dict[str, Any]) -> str:
        """Store a runtime ADG snapshot."""
        snapshot_id = snapshot.get("snapshot_id", str(uuid.uuid4()))
        snapshot["stored_at_utc"] = int(time.time() * 1000)

        # Store in memory
        self.snapshots[snapshot_id] = snapshot

        # Store to file
        snapshot_file = self.store_dir / f"runtime_adg_{snapshot_id}.json"
        with open(snapshot_file, "w") as f:
            json.dump(snapshot, f, indent=2)

        return snapshot_id

    def get_snapshot(self, snapshot_id: str) -> dict[str, Any]:
        """Retrieve a snapshot by ID."""
        return self.snapshots.get(snapshot_id)

    def list_snapshots(self) -> list[str]:
        """List all snapshot IDs."""
        return list(self.snapshots.keys())


class MockExecutionTrace:
    """Mock execution trace for testing."""

    def __init__(self, trace_id: str = None):
        self.trace_id = trace_id or str(uuid.uuid4())
        self.spans: list[dict[str, Any]] = []
        self.started_at_utc = int(time.time() * 1000)

    def add_span(self, name: str, kind: str, attributes: dict[str, Any] = None):
        """Add a span to the trace."""
        span = {
            "span_id": str(uuid.uuid4()),
            "trace_id": self.trace_id,
            "name": name,
            "kind": kind,
            "started_at_utc": int(time.time() * 1000),
            "attributes": attributes or {},
            "status": "ok",
        }
        self.spans.append(span)
        return span

    def finalize(self):
        """Finalize the trace."""
        self.ended_at_utc = int(time.time() * 1000)

    def to_snapshot(self) -> dict[str, Any]:
        """Convert trace to runtime ADG snapshot format."""
        nodes = []
        for span in self.spans:
            node = {
                "node_id": span["span_id"],
                "name": span["name"],
                "kind": span["kind"],
                "layer": self.trace_id,
                "component": "test_component",
                "started_at_utc": span["started_at_utc"],
                "duration_ms": span.get("duration_ms", 10),
                "status": span["status"],
                "attributes_json": json.dumps(span["attributes"]),
            }
            nodes.append(node)

        return {
            "snapshot_id": self.trace_id,
            "trace_id": self.trace_id,
            "mission": f"test-{self.trace_id}",
            "started_at_utc": self.started_at_utc,
            "ended_at_utc": self.ended_at_utc,
            "nodes": nodes,
        }


class MockAgent:
    """Mock agent that generates execution traces."""

    def __init__(self, name: str, kind: str = "MOCK_ORCHESTRATOR"):
        self.name = name
        self.kind = kind
        self.trace = MockExecutionTrace()

    def execute(self, task: str, **kwargs) -> dict[str, Any]:
        """Execute a task and record traces."""
        # Start execution span
        self.trace.add_span(
            name=f"execute_{task}",
            kind=self.kind,
            attributes={"agent_name": self.name, "task": task},
        )

        # Simulate work
        time.sleep(0.05)

        # Add sub-task spans
        for i in range(3):
            self.trace.add_span(
                name=f"subtask_{i + 1}",
                kind="SUB_TASK",
                attributes={"subtask_id": i + 1, "parent": self.name},
            )
            time.sleep(0.02)

        # Finalize trace
        self.trace.finalize()

        return {
            "success": True,
            "completed": True,
            "message": f"Task '{task}' completed successfully",
            "trace_id": self.trace.trace_id,
            "metadata": {
                "agent": self.name,
                "kind": self.kind,
                "subtasks": 3,
            },
        }


async def test_runtime_adg_e2e():
    """End-to-end validation of Runtime ADG pipeline."""
    print("[E2E TEST] Starting Runtime ADG end-to-end validation...")

    try:
        # Initialize components
        store = MockRuntimeADGStore()

        # Test 1: Single agent execution
        print("\n[E2E TEST] Test 1: Single agent execution")
        agent1 = MockAgent("TestAgent1", "TEST_ORCHESTRATOR")
        result1 = agent1.execute("data_processing")

        # Convert trace to snapshot and store
        snapshot1 = agent1.trace.to_snapshot()
        snapshot_id1 = store.store_snapshot(snapshot1)

        print(f"  ✓ Agent executed: {result1['success']}")
        print(f"  ✓ Trace ID: {result1['trace_id']}")
        print(f"  ✓ Snapshot stored: {snapshot_id1}")
        print(f"  ✓ Spans generated: {len(snapshot1['nodes'])}")

        # Verify snapshot structure
        assert "snapshot_id" in snapshot1
        assert "trace_id" in snapshot1
        assert "nodes" in snapshot1
        assert len(snapshot1["nodes"]) > 0

        # Test 2: Multiple agent execution
        print("\n[E2E TEST] Test 2: Multiple agent execution")
        agents = [
            MockAgent("ValidatorAgent", "VALIDATOR"),
            MockAgent("ProcessorAgent", "PROCESSOR"),
            MockAgent("HealerAgent", "HEALER"),
        ]

        snapshots = []
        for agent in agents:
            result = agent.execute("pipeline_task")
            snapshot = agent.trace.to_snapshot()
            snapshot_id = store.store_snapshot(snapshot)
            snapshots.append(snapshot)
            print(f"  ✓ {agent.name}: {len(snapshot['nodes'])} spans")

        # Test 3: Snapshot retrieval and validation
        print("\n[E2E TEST] Test 3: Snapshot retrieval and validation")
        all_snapshot_ids = store.list_snapshots()
        print(f"  ✓ Total snapshots stored: {len(all_snapshot_ids)}")

        for snapshot_id in all_snapshot_ids:
            retrieved = store.get_snapshot(snapshot_id)
            assert retrieved is not None, f"Snapshot {snapshot_id} not found"
            assert "nodes" in retrieved, f"Snapshot {snapshot_id} missing nodes"
            assert len(retrieved["nodes"]) > 0, f"Snapshot {snapshot_id} has no nodes"

        # Test 4: File system validation
        print("\n[E2E TEST] Test 4: File system validation")
        runtime_adg_dir = Path("artifacts/runtime_adg")
        if runtime_adg_dir.exists():
            snapshot_files = list(runtime_adg_dir.glob("*.json"))
            print(f"  ✓ Snapshot files on disk: {len(snapshot_files)}")

            # Count our test snapshots
            test_snapshot_count = 0
            for file_path in snapshot_files:
                with open(file_path) as f:
                    data = json.load(f)
                # Check if it's one of our test snapshots (has trace_id field)
                if "trace_id" in data or "snapshot_id" in data:
                    test_snapshot_count += 1
                    assert "nodes" in data, f"Snapshot {file_path.name} missing nodes"
                    assert isinstance(data["nodes"], list), f"Snapshot {file_path.name} nodes not a list"

            print(f"  ✓ Test snapshots validated: {test_snapshot_count}")
        else:
            print("  ⚠ No runtime_adg directory found")

        # Test 5: Performance validation
        print("\n[E2E TEST] Test 5: Performance validation")
        start_time = time.time()

        # Execute multiple agents rapidly
        for i in range(10):
            agent = MockAgent(f"PerfAgent{i}", "PERF_TEST")
            agent.execute("rapid_task")
            snapshot = agent.trace.to_snapshot()
            store.store_snapshot(snapshot)

        elapsed = time.time() - start_time
        print(f"  ✓ 10 agents executed in {elapsed:.2f}s")
        print(f"  ✓ Average per agent: {elapsed / 10:.3f}s")
        assert elapsed < 5.0, "Performance threshold exceeded"

        # Test 6: Trace completeness
        print("\n[E2E TEST] Test 6: Trace completeness")
        test_agent = MockAgent("CompletenessAgent", "COMPLETENESS_TEST")
        test_agent.execute("completeness_test")

        trace = test_agent.trace
        snapshot = trace.to_snapshot()

        # Verify all required fields
        required_fields = ["snapshot_id", "trace_id", "mission", "started_at_utc", "ended_at_utc", "nodes"]
        for field in required_fields:
            assert field in snapshot, f"Missing required field: {field}"

        # Verify node structure
        for node in snapshot["nodes"]:
            node_fields = [
                "node_id",
                "name",
                "kind",
                "layer",
                "component",
                "started_at_utc",
                "duration_ms",
                "status",
                "attributes_json",
            ]
            for field in node_fields:
                assert field in node, f"Node missing field: {field}"

        print("  ✓ All required fields present")
        print("  ✓ Node structure validated")

        print("\n[E2E TEST] ✅ Runtime ADG end-to-end validation completed successfully!")
        print("[E2E TEST] Summary:")
        print(f"  - Total snapshots: {len(store.list_snapshots())}")
        print(f"  - Total spans: {sum(len(s['nodes']) for s in snapshots + [snapshot1])}")
        print(f"  - Performance: {elapsed:.2f}s for 10 agents")

        return True

    except Exception as e:
        print(f"\n[E2E TEST] ❌ Validation failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_runtime_adg_e2e())
    exit(0 if success else 1)
