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

    # Store artifacts in persistent storage
    print("\n3. Storing artifacts...")
    try:
        # Import storage modules
        storage_spec = importlib.util.spec_from_file_location(
            "persistent_store",
            Path(__file__).parent.parent / "agentic_core" / "L4_state" / "storage" / "persistent_store.py",
        )
        persistent_store = importlib.util.module_from_spec(storage_spec)
        storage_spec.loader.exec_module(persistent_store)

        filesystem_spec = importlib.util.spec_from_file_location(
            "filesystem_store",
            Path(__file__).parent.parent / "agentic_core" / "L4_state" / "storage" / "filesystem_store.py",
        )
        filesystem_store = importlib.util.module_from_spec(filesystem_spec)
        filesystem_spec.loader.exec_module(filesystem_store)

        # Initialize store
        store = filesystem_store.FileSystemStore(Path.cwd())

        # Store replay record artifact
        import json

        record_dict = json.loads(record_to_json(record))
        record_artifact = persistent_store.create_artifact(
            kind="replay_record",
            logical_id="execute_ssot_plan",
            payload=record_dict,
            metadata={
                "code_commit": "unknown",  # Will be set by evidence runner
                "tool_version": "1.0",
                "record_version": str(record.version),
            },
        )
        record_ref = store.put(record_artifact)
        print(f"   Stored replay record: {record_ref.path} (v{record_ref.version})")

        # Store replay summary artifact
        summary_payload = {
            "is_deterministic": comparison.is_match,
            "mismatch_count": len(comparison.mismatches),
            "command_count": len(record.commands),
            "record_hashes": record.hashes,
        }
        if not comparison.is_match:
            summary_payload["first_mismatches"] = comparison.mismatches[:3]
            if comparison.first_diff_summary:
                summary_payload["first_diff_summary"] = comparison.first_diff_summary

        summary_artifact = persistent_store.create_artifact(
            kind="replay_summary",
            logical_id="execute_ssot_plan",
            payload=summary_payload,
            metadata={
                "tool_version": "1.0",
                "verdict": "deterministic" if comparison.is_match else "non_deterministic",
            },
        )
        summary_ref = store.put(summary_artifact)
        print(f"   Stored replay summary: {summary_ref.path} (v{summary_ref.version})")

    # guardian: allow-silent-swallower
    except Exception as e:
        print(f"   ERROR during artifact storage: {e}")
        return 1

    print("\n=== Replay Complete ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
