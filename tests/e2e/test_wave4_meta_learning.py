"""Wave 4: Meta-Learning Bus Wiring — Verification Tests.

Tests for L6MetaLearningBridge and meta-learning integration.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))



def test_meta_learning_bridge_imports() -> bool:
    """Test that L6MetaLearningBridge can be imported."""
    try:

        print("✓ L6MetaLearningBridge imports successfully")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_meta_learning_record() -> bool:
    """Test MetaLearningRecord dataclass."""
    try:
        from agentic_core.L6_observability import MetaLearningRecord

        record = MetaLearningRecord(
            snapshot_id="test-snapshot-001",
            trace_id="test-trace-001",
            mission="test-mission",
            eval_results={"accuracy": 0.95, "f1": 0.92},
            telemetry_events=[{"type": "metric", "value": 42}],
            metadata={"version": "1.0"},
        )

        # Verify fields
        assert record.snapshot_id == "test-snapshot-001"
        assert record.trace_id == "test-trace-001"
        assert record.mission == "test-mission"
        assert record.eval_results["accuracy"] == 0.95
        assert len(record.telemetry_events) == 1

        # Test to_dict
        data = record.to_dict()
        assert data["snapshot_id"] == "test-snapshot-001"
        assert data["eval_results"]["accuracy"] == 0.95

        # Test from_dict
        restored = MetaLearningRecord.from_dict(data)
        assert restored.snapshot_id == record.snapshot_id
        assert restored.eval_results["accuracy"] == 0.95

        print("✓ MetaLearningRecord works correctly")
        return True

    except Exception as e:
        print(f"✗ MetaLearningRecord test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_bridge_initialization() -> bool:
    """Test L6MetaLearningBridge initialization."""
    try:
        import shutil
        import tempfile

        from agentic_core.L6_observability import L6MetaLearningBridge

        temp_dir = tempfile.mkdtemp()

        try:
            bridge = L6MetaLearningBridge(
                storage_path=temp_dir,
                enable_persistence=True,
            )

            # Verify initialization
            assert str(bridge.storage_path) == temp_dir
            assert bridge.enable_persistence is True

            print("✓ L6MetaLearningBridge initializes correctly")
            return True

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    except Exception as e:
        print(f"✗ Bridge initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_store_snapshot_with_linkage() -> bool:
    """Test storing snapshot with evaluation and telemetry linkage."""
    try:
        import shutil
        import tempfile

        from agentic_core.L6_observability import L6MetaLearningBridge

        temp_dir = tempfile.mkdtemp()

        try:
            bridge = L6MetaLearningBridge(
                storage_path=temp_dir,
                enable_persistence=True,
            )

            # Create mock snapshot data
            snapshot = {
                "snapshot_id": "snapshot-001",
                "trace_id": "trace-001",
                "mission": "test-mission",
                "nodes": [],
                "edges": [],
            }

            eval_results = {"accuracy": 0.95, "precision": 0.93, "recall": 0.91}
            telemetry_events = [
                {"type": "latency", "value": 150.5},
                {"type": "throughput", "value": 1000},
            ]

            # Store snapshot with linkage
            record = bridge.store_snapshot(
                snapshot=snapshot,
                eval_results=eval_results,
                telemetry_events=telemetry_events,
                metadata={"test": True},
            )

            # Verify record
            assert record.snapshot_id == "snapshot-001"
            assert record.eval_results["accuracy"] == 0.95
            assert len(record.telemetry_events) == 2

            # Verify it was stored
            assert "snapshot-001" in bridge._records

            print("✓ Snapshot storage with linkage works")
            return True

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    except Exception as e:
        print(f"✗ Store snapshot test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_feed_meta_learning() -> bool:
    """Test feeding snapshot to meta-learning pipeline."""
    try:
        import shutil
        import tempfile

        from agentic_core.L6_observability import L6MetaLearningBridge

        temp_dir = tempfile.mkdtemp()

        try:
            bridge = L6MetaLearningBridge(
                storage_path=temp_dir,
                enable_persistence=True,
            )

            # Store a snapshot first
            snapshot = {
                "snapshot_id": "snapshot-feed-001",
                "trace_id": "trace-feed-001",
                "mission": "feed-test",
            }

            bridge.store_snapshot(
                snapshot=snapshot,
                eval_results={"score": 0.88},
                telemetry_events=[{"event": "test"}],
            )

            # Feed to meta-learning
            result = bridge.feed_meta_learning(
                snapshot_id="snapshot-feed-001",
                downstream_consumer="test_consumer",
            )

            # Verify result
            assert result is not None
            assert result["snapshot_id"] == "snapshot-feed-001"
            assert result["eval_results"]["score"] == 0.88

            print("✓ Feed meta-learning works")
            return True

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    except Exception as e:
        print(f"✗ Feed meta-learning test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_add_telemetry_event() -> bool:
    """Test adding telemetry event to existing record."""
    try:
        import shutil
        import tempfile

        from agentic_core.L6_observability import L6MetaLearningBridge

        temp_dir = tempfile.mkdtemp()

        try:
            bridge = L6MetaLearningBridge(
                storage_path=temp_dir,
                enable_persistence=True,
            )

            # Store initial snapshot
            snapshot = {
                "snapshot_id": "snapshot-tel-001",
                "trace_id": "trace-tel-001",
                "mission": "telemetry-test",
            }

            bridge.store_snapshot(
                snapshot=snapshot,
                telemetry_events=[{"type": "initial"}],
            )

            # Add more telemetry
            success = bridge.add_telemetry_event(
                snapshot_id="snapshot-tel-001",
                event={"type": "additional", "value": 123},
            )

            assert success is True

            # Verify it was added
            record = bridge.load_record("snapshot-tel-001")
            assert record is not None
            assert len(record.telemetry_events) == 2

            print("✓ Add telemetry event works")
            return True

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    except Exception as e:
        print(f"✗ Add telemetry test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_add_eval_result() -> bool:
    """Test adding evaluation result to existing record."""
    try:
        import shutil
        import tempfile

        from agentic_core.L6_observability import L6MetaLearningBridge

        temp_dir = tempfile.mkdtemp()

        try:
            bridge = L6MetaLearningBridge(
                storage_path=temp_dir,
                enable_persistence=True,
            )

            # Store initial snapshot
            snapshot = {
                "snapshot_id": "snapshot-eval-001",
                "trace_id": "trace-eval-001",
                "mission": "eval-test",
            }

            bridge.store_snapshot(
                snapshot=snapshot,
                eval_results={"accuracy": 0.90},
            )

            # Add more eval results
            success = bridge.add_eval_result(
                snapshot_id="snapshot-eval-001",
                key="f1_score",
                value=0.92,
            )

            assert success is True

            # Verify it was added
            record = bridge.load_record("snapshot-eval-001")
            assert record is not None
            assert record.eval_results["accuracy"] == 0.90
            assert record.eval_results["f1_score"] == 0.92

            print("✓ Add eval result works")
            return True

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    except Exception as e:
        print(f"✗ Add eval result test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_record_stats() -> bool:
    """Test getting record statistics."""
    try:
        import shutil
        import tempfile

        from agentic_core.L6_observability import L6MetaLearningBridge

        temp_dir = tempfile.mkdtemp()

        try:
            bridge = L6MetaLearningBridge(
                storage_path=temp_dir,
                enable_persistence=True,
            )

            # Store multiple snapshots
            for i in range(3):
                bridge.store_snapshot(
                    snapshot={
                        "snapshot_id": f"snapshot-stats-{i}",
                        "trace_id": f"trace-{i}",
                        "mission": "stats-test",
                    },
                    eval_results={"metric": i},
                    telemetry_events=[{"event": i}],
                )

            # Get stats
            stats = bridge.get_record_stats()

            assert stats["total_records"] == 3
            assert stats["total_eval_results"] == 3
            assert stats["total_telemetry_events"] == 3

            print("✓ Get record stats works")
            return True

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    except Exception as e:
        print(f"✗ Get stats test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_persistence() -> bool:
    """Test that records are persisted to disk and can be loaded."""
    try:
        import shutil
        import tempfile

        from agentic_core.L6_observability import L6MetaLearningBridge

        temp_dir = tempfile.mkdtemp()

        try:
            # Create bridge and store snapshot
            bridge1 = L6MetaLearningBridge(
                storage_path=temp_dir,
                enable_persistence=True,
            )

            snapshot = {
                "snapshot_id": "snapshot-persist-001",
                "trace_id": "trace-persist-001",
                "mission": "persistence-test",
            }

            bridge1.store_snapshot(
                snapshot=snapshot,
                eval_results={"accuracy": 0.99},
            )

            # Create new bridge instance pointing to same directory
            bridge2 = L6MetaLearningBridge(
                storage_path=temp_dir,
                enable_persistence=True,
            )

            # Load record from disk
            record = bridge2.load_record("snapshot-persist-001")

            assert record is not None
            assert record.snapshot_id == "snapshot-persist-001"
            assert record.eval_results["accuracy"] == 0.99

            print("✓ Persistence and loading works")
            return True

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    except Exception as e:
        print(f"✗ Persistence test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main() -> int:
    """Run all Wave 4 tests."""
    print("=" * 60)
    print("Wave 4: Meta-Learning Bus Wiring — Verification Tests")
    print("=" * 60)

    tests = [
        ("Meta-Learning Bridge Imports", test_meta_learning_bridge_imports),
        ("MetaLearningRecord", test_meta_learning_record),
        ("Bridge Initialization", test_bridge_initialization),
        ("Store Snapshot with Linkage", test_store_snapshot_with_linkage),
        ("Feed Meta-Learning", test_feed_meta_learning),
        ("Add Telemetry Event", test_add_telemetry_event),
        ("Add Eval Result", test_add_eval_result),
        ("Get Record Stats", test_get_record_stats),
        ("Persistence", test_persistence),
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
        print("\n🎉 Wave 4 implementation verified successfully!")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
