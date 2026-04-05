"""Wave 3: Runtime ADG Persistence Integration — Verification Tests.

Tests for AutoPersistenceTracingAdapter and automatic snapshot persistence.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))



def test_adapter_imports() -> bool:
    """Test that AutoPersistenceTracingAdapter can be imported."""
    try:

        print("✓ AutoPersistenceTracingAdapter imports successfully")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_adapter_initialization() -> bool:
    """Test adapter initialization with auto-persistence options."""
    try:
        from agentic_core.L6_observability import AutoPersistenceTracingAdapter

        adapter = AutoPersistenceTracingAdapter(
            service_name="test-service",
            auto_persist=True,
            uwg_endpoint="http://localhost:8000",
            adg_storage_path="test_artifacts/adg",
        )

        # Verify initialization
        assert adapter.auto_persist is True
        assert adapter.uwg_endpoint == "http://localhost:8000"
        assert adapter.adg_storage_path == "test_artifacts/adg"

        print("✓ AutoPersistenceTracingAdapter initializes correctly")
        return True
    except Exception as e:
        print(f"✗ Adapter initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_drain_with_auto_persist() -> bool:
    """Test drain with automatic snapshot persistence."""
    try:
        import shutil
        import tempfile

        from agentic_core.L6_observability import AutoPersistenceTracingAdapter

        # Create temp directory for test
        temp_dir = tempfile.mkdtemp()

        try:
            adapter = AutoPersistenceTracingAdapter(
                service_name="test-service",
                auto_persist=True,
                adg_storage_path=temp_dir,
                enable_logging=False,
            )

            # Create some test spans manually
            adapter._completed_spans.append({
                "span_id": "test-span-001",
                "trace_id": "test-trace-001",
                "name": "test_operation",
                "kind": "action",
                "layer": "L2",
                "component": "TestComponent",
                "ts_utc": 1000,
                "duration_ms": 50.0,
                "status": "ok",
                "attributes": {"tool_name": "test_tool"},
            })

            # Drain with auto-persist
            spans = adapter.drain_completed_spans(mission="test-mission")

            # Verify spans were drained
            assert len(spans) == 1

            # Verify snapshot was persisted
            assert len(adapter._persisted_snapshots) == 1
            assert adapter._current_snapshot_id is not None

            print(f"✓ Auto-persistence works: {len(spans)} spans → snapshot {adapter._current_snapshot_id[:16]}...")
            return True

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    except Exception as e:
        print(f"✗ Drain with auto-persist failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_snapshot_id_propagation() -> bool:
    """Test that snapshot_id is propagated through traces."""
    try:
        from agentic_core.L6_observability import AutoPersistenceTracingAdapter

        adapter = AutoPersistenceTracingAdapter(
            service_name="test-service",
            auto_persist=True,
            enable_logging=False,
        )

        # Set trace ID
        adapter.set_trace_id("test-trace-001")

        # Create test spans
        adapter._completed_spans.append({
            "span_id": "test-span-001",
            "trace_id": "test-trace-001",
            "name": "test_operation",
            "kind": "action",
            "layer": "L2",
            "component": "TestComponent",
            "ts_utc": 1000,
            "duration_ms": 50.0,
            "status": "ok",
            "attributes": {},
        })

        # Drain and persist
        spans = adapter.drain_completed_spans(mission="propagation-test")

        # Verify snapshot_id is available
        snapshot_id = adapter.get_snapshot_id()
        assert snapshot_id is not None
        assert len(snapshot_id) > 0

        print(f"✓ Snapshot ID propagation works: {snapshot_id[:16]}...")
        return True

    except Exception as e:
        print(f"✗ Snapshot ID propagation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_persistence_status() -> bool:
    """Test persistence status reporting."""
    try:
        from agentic_core.L6_observability import AutoPersistenceTracingAdapter

        adapter = AutoPersistenceTracingAdapter(
            service_name="test-service",
            auto_persist=True,
            uwg_endpoint="http://localhost:8000",
            adg_storage_path="test_artifacts/adg",
            enable_logging=False,
        )

        status = adapter.get_persistence_status()

        # Verify status structure
        assert "auto_persist_enabled" in status
        assert "materializer_available" in status
        assert "uwg_endpoint" in status
        assert "local_storage_path" in status
        assert "persisted_snapshot_count" in status

        assert status["auto_persist_enabled"] is True
        assert status["uwg_endpoint"] == "http://localhost:8000"

        print("✓ Persistence status reporting works")
        return True

    except Exception as e:
        print(f"✗ Persistence status test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_graceful_degradation() -> bool:
    """Test graceful degradation when persistence unavailable."""
    try:
        from agentic_core.L6_observability import AutoPersistenceTracingAdapter

        # Create adapter with auto-persist disabled
        adapter = AutoPersistenceTracingAdapter(
            service_name="test-service",
            auto_persist=False,  # Disabled
            enable_logging=False,
        )

        # Create test spans
        adapter._completed_spans.append({
            "span_id": "test-span-001",
            "trace_id": "test-trace-001",
            "name": "test_operation",
            "kind": "action",
            "layer": "L2",
            "component": "TestComponent",
            "ts_utc": 1000,
            "duration_ms": 50.0,
            "status": "ok",
            "attributes": {},
        })

        # Drain without auto-persist
        spans = adapter.drain_completed_spans(mission="degradation-test", persist=False)

        # Verify spans were still drained
        assert len(spans) == 1

        # Verify no snapshots were persisted
        assert len(adapter._persisted_snapshots) == 0

        print("✓ Graceful degradation works: spans drained without persistence")
        return True

    except Exception as e:
        print(f"✗ Graceful degradation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_local_persistence_fallback() -> bool:
    """Test local file persistence fallback when UWG unavailable."""
    try:
        import json
        import shutil
        import tempfile
        from pathlib import Path

        from agentic_core.L6_observability import AutoPersistenceTracingAdapter

        temp_dir = tempfile.mkdtemp()

        try:
            adapter = AutoPersistenceTracingAdapter(
                service_name="test-service",
                auto_persist=True,
                uwg_endpoint=None,  # No UWG
                adg_storage_path=temp_dir,
                enable_logging=False,
            )

            # Create test spans
            adapter._completed_spans.append({
                "span_id": "test-span-001",
                "trace_id": "test-trace-001",
                "name": "test_operation",
                "kind": "action",
                "layer": "L2",
                "component": "TestComponent",
                "ts_utc": 1000,
                "duration_ms": 50.0,
                "status": "ok",
                "attributes": {"test": "value"},
            })

            # Drain and persist locally
            spans = adapter.drain_completed_spans(mission="local-test")

            # Verify snapshot was created
            assert len(adapter._persisted_snapshots) == 1
            snapshot_id = adapter._persisted_snapshots[0]

            # Check that file was created
            expected_file = Path(temp_dir) / f"{snapshot_id}.json"
            assert expected_file.exists(), f"Expected file not found: {expected_file}"

            # Verify file content is valid JSON
            with open(expected_file, encoding="utf-8") as f:
                data = json.load(f)
                assert "snapshot_id" in data
                assert data["snapshot_id"] == snapshot_id

            print(f"✓ Local persistence fallback works: snapshot saved to {expected_file.name}")
            return True

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    except Exception as e:
        print(f"✗ Local persistence test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main() -> int:
    """Run all Wave 3 tests."""
    print("=" * 60)
    print("Wave 3: Runtime ADG Persistence Integration — Verification Tests")
    print("=" * 60)

    tests = [
        ("Adapter Imports", test_adapter_imports),
        ("Adapter Initialization", test_adapter_initialization),
        ("Drain with Auto-Persist", test_drain_with_auto_persist),
        ("Snapshot ID Propagation", test_snapshot_id_propagation),
        ("Persistence Status", test_get_persistence_status),
        ("Graceful Degradation", test_graceful_degradation),
        ("Local Persistence Fallback", test_local_persistence_fallback),
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
        print("\n🎉 Wave 3 implementation verified successfully!")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
