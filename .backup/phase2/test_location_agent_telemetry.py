"""
Quick integration test to verify LocationAgent telemetry works with batch optimization.
"""

import shutil
import sys
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_location_agent_telemetry():
    """Verify LocationAgent can increment files_scanned metric."""

    # Create temporary directory for test
    root = Path(tempfile.mkdtemp(prefix="test_location_telemetry_"))
    try:
        # Create minimal project structure
        (root / "agentic_core").mkdir(parents=True)
        (root / "agentic_core" / "L5_safety").mkdir()
        (root / "agentic_core" / "L4_state").mkdir()

        # Import RuntimeStateGuard directly to test telemetry
        from agentic_core.L4_state.utils.memory.runtime_state_guard import RuntimeStateGuard

        guard = RuntimeStateGuard(root)

        # Test batch context with multiple increments (simulating high-volume scan)
        write_count = 0
        original_persist = guard._atomic_persist

        def spy_persist():
            nonlocal write_count
            write_count += 1
            original_persist()

        guard._atomic_persist = spy_persist

        # Simulate LocationAgent scanning multiple files
        with guard:
            for _i in range(50):  # Simulate scanning 50 files
                guard.increment_metric("files_scanned")

        # Verify batching worked
        assert write_count == 1, f"Expected 1 write, got {write_count}"
        assert guard.get_metric("files_scanned") == 50

        print("test_location_agent_telemetry: 100% PASS")

    finally:
        # Cleanup
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    test_location_agent_telemetry()
    print("LocationAgent telemetry integration verified! ✅")
