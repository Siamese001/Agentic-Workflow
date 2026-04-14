"""
Test script to verify batch performance optimization in RuntimeStateGuard.
Ensures that increment_metric does NOT write to disk when inside a with block.
"""

import shutil
import tempfile
from pathlib import Path


def test_batch_performance_optimization():
    """
    Verifies that batch mode prevents disk thrashing.
    100 increments should result in 1 disk write, not 100.
    """
    # Import after ensuring path
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent))

    from agentic_core.L4_state.utils.memory.runtime_state_guard import RuntimeStateGuard

    # Create temporary directory for test
    root = Path(tempfile.mkdtemp(prefix="test_batch_"))
    try:
        guard = RuntimeStateGuard(root)

        # Spy on the persist method
        write_count = 0
        original_persist = guard._atomic_persist

        def spy_persist():
            nonlocal write_count
            write_count += 1
            original_persist()

        guard._atomic_persist = spy_persist

        # EXECUTION: 100 increments inside batch
        with guard:
            for _ in range(100):
                guard.increment_metric("files_scanned")

        # VERIFICATION
        # Should write exactly ONCE (at exit), not 100 times
        assert write_count == 1, f"Batching failed! Disk written {write_count} times."
        assert guard.get_metric("files_scanned") == 100

        print("test_batch_performance_optimization: 100% PASS")

    finally:
        # Cleanup
        shutil.rmtree(root, ignore_errors=True)


def test_nested_batch_context():
    """
    Verifies that nested batch contexts work correctly.
    Only the outermost exit should trigger the write.
    """
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent))

    from agentic_core.L4_state.utils.memory.runtime_state_guard import RuntimeStateGuard

    # Create temporary directory for test
    root = Path(tempfile.mkdtemp(prefix="test_nested_"))
    try:
        guard = RuntimeStateGuard(root)

        # Spy on the persist method
        write_count = 0
        original_persist = guard._atomic_persist

        def spy_persist():
            nonlocal write_count
            write_count += 1
            original_persist()

        guard._atomic_persist = spy_persist

        # EXECUTION: Nested batch contexts
        with guard:
            guard.increment_metric("test_metric")

            with guard:  # Nested context
                guard.increment_metric("test_metric")
                guard.increment_metric("test_metric")

            # Still in outer context - no write yet
            assert write_count == 0

            guard.increment_metric("test_metric")

        # VERIFICATION: Only one write at outermost exit
        assert write_count == 1, f"Nested batching failed! Disk written {write_count} times."
        assert guard.get_metric("test_metric") == 4

        print("test_nested_batch_context: 100% PASS")

    finally:
        # Cleanup
        shutil.rmtree(root, ignore_errors=True)


def test_immediate_write_outside_batch():
    """
    Verifies that writes happen immediately when NOT in batch mode.
    """
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent))

    from agentic_core.L4_state.utils.memory.runtime_state_guard import RuntimeStateGuard

    # Create temporary directory for test
    root = Path(tempfile.mkdtemp(prefix="test_immediate_"))
    try:
        guard = RuntimeStateGuard(root)

        # Spy on the persist method
        write_count = 0
        original_persist = guard._atomic_persist

        def spy_persist():
            nonlocal write_count
            write_count += 1
            original_persist()

        guard._atomic_persist = spy_persist

        # EXECUTION: Direct increments without batch
        guard.increment_metric("test_metric")
        guard.increment_metric("test_metric")

        # VERIFICATION: Each increment should write immediately
        assert write_count == 2, f"Immediate write failed! Disk written {write_count} times."
        assert guard.get_metric("test_metric") == 2

        print("test_immediate_write_outside_batch: 100% PASS")

    finally:
        # Cleanup
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    print("Running batch performance optimization tests...")
    test_batch_performance_optimization()
    test_nested_batch_context()
    test_immediate_write_outside_batch()
    print("All tests PASSED! ✅")
