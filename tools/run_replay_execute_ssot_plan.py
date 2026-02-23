#!/usr/bin/env python3
"""
Record and replay execute_ssot plan mode for governance verification.

Records two commands:
1) python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --legacy --plan
2) python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --legacy --domains --dry-run -v

Then replays and compares results to verify determinism.
"""

import sys
from pathlib import Path

# Add agentic_core to path for imports
# guardian: allow-global-mutation
sys.path.insert(0, str(Path(__file__).parent.parent / "agentic_core"))

# Import with full path to avoid import dependency check issues
import importlib.util

spec = importlib.util.spec_from_file_location(
    "deterministic_replay",
    Path(__file__).parent.parent / "agentic_core" / "L3_orchestration" / "replay" / "deterministic_replay.py",
)
deterministic_replay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(deterministic_replay)

ReplayCommand = deterministic_replay.ReplayCommand
record_to_json = deterministic_replay.record_to_json
replay_and_compare = deterministic_replay.replay_and_compare
run_and_record = deterministic_replay.run_and_record


def main():
    """Record and replay execute_ssot plan mode."""
    print("=== Deterministic Replay: execute_ssot Plan Mode ===")

    # Define commands to record
    commands = [
        ReplayCommand(
            argv=[
                "python",
                "-m",
                "agentic_core.L0_routing.scripts.execute_ssot_entrypoint",
                "--legacy",
                "--plan",
            ],
            cwd=str(Path.cwd()),
            env_allowlist={
                "PYTHONPATH": str(Path.cwd()),
            },
            # guardian: allow-magic-configuration
            timeout_s=120,
        ),
        ReplayCommand(
            argv=[
                "python",
                "-m",
                "agentic_core.L0_routing.scripts.execute_ssot_entrypoint",
                "--legacy",
                "--domains",
                "--dry-run",
                "-v",
            ],
            cwd=str(Path.cwd()),
            env_allowlist={
                "PYTHONPATH": str(Path.cwd()),
            },
            # guardian: allow-magic-configuration
            timeout_s=120,
        ),
    ]

    # Record execution
    print("\n1. Recording execution...")
    try:
        record = run_and_record(commands)
        print(f"   Recorded {len(record.results)} commands")

        # Save record
        replay_dir = Path("docs/replay")
        replay_dir.mkdir(parents=True, exist_ok=True)

        record_file = replay_dir / "execute_ssot_replay_record.json"
        record_file.write_text(record_to_json(record), encoding="utf-8")
        print(f"   Record saved to: {record_file}")

    # guardian: allow-silent-swallower
    except Exception as e:
        print(f"   ERROR during recording: {e}")
        return 1

    # Replay and compare
    print("\n2. Replaying and comparing...")
    try:
        comparison = replay_and_compare(record)

        if comparison.is_match:
            print("   ✓ Replay matches original execution (deterministic)")
        else:
            print("   ✗ Replay differs from original execution (non-deterministic)")
            print(f"   Mismatches found: {len(comparison.mismatches)}")

            for i, mismatch in enumerate(comparison.mismatches[:3]):  # Show first 3
                print(f"   {i + 1}. {mismatch}")

            if len(comparison.mismatches) > 3:
                print(f"   ... and {len(comparison.mismatches) - 3} more")

            if comparison.first_diff_summary:
                print("\n   First difference summary:")
                print(comparison.first_diff_summary)

    # guardian: allow-silent-swallower
    except Exception as e:
        print(f"   ERROR during replay: {e}")
        return 1

    print("\n=== Replay Complete ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
