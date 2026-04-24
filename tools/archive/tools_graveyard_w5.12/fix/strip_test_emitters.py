#!/usr/bin/env python3
"""Strip lifecycle_trace_contract bootstrap emitters from test files.

Phase 0.1: Remove top-level _emit_*() calls that execute at import time.
These emitter calls exist solely for ADG coverage tracking and add
~76 function calls per test file during pytest collection.
"""

import re
from pathlib import Path

# Emitter patterns to strip (top-level calls only)
EMITTER_PATTERNS = [
    r"^_emit_.*\(.*\)$",
    r"^emit_.*\(.*\)$",
]

# Files known to import lifecycle_trace_contract (from ADG analysis)
TARGET_FILES = [
    "tests/unit/agentic_core/L2_execution/enforcement/test_transcript_freezer_adg.py",
    "tests/unit_min_deps/test_vllm_replay.py",
    "tests/unit_min_deps/test_version_store.py",
    "tests/unit_min_deps/test_time_shifted_consumption.py",
    "tests/unit_min_deps/test_three_tier_convergence.py",
    "tests/unit_min_deps/test_telemetry_consumer.py",
    "tests/unit_min_deps/test_spine_cross_app_contract.py",
    "tests/unit_min_deps/test_sovereignty_interfaces.py",
    "tests/unit_min_deps/test_shadow_evaluator.py",
    "tests/unit_min_deps/test_seed_embedding_pack_b0.py",
    "tests/unit_min_deps/test_rlhf_optimizer.py",
    "tests/unit_min_deps/test_replay_validator_b3.py",
    "tests/unit_min_deps/test_replay_validator.py",
    "tests/unit_min_deps/test_replay_harness_contracts.py",
    "tests/unit_min_deps/test_rca_types.py",
    # Additional files will be discovered via pattern matching
]


def find_emitter_calls(file_path: Path) -> list[tuple[int, str]]:
    """Find top-level emitter calls in a Python file."""
    emitter_calls = []

    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
        print(f"Error reading {file_path}: {e}")
        return emitter_calls

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # Skip comments and docstrings
        if stripped.startswith("#") or not stripped:
            continue

        # Check for emitter patterns
        for pattern in EMITTER_PATTERNS:
            if re.match(pattern, stripped):
                emitter_calls.append((i, line.rstrip()))
                break

    return emitter_calls


def strip_emitters_from_file(file_path: Path, dry_run: bool = True) -> tuple[int, list[str]]:
    """Strip emitter calls from a file. Return (lines_changed, changed_lines)."""
    if not file_path.exists():
        return 0, []

    with open(file_path, encoding="utf-8") as f:
        lines = f.readlines()

    changed_lines = []
    lines_changed = 0

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Skip if not an emitter call
        is_emitter = False
        for pattern in EMITTER_PATTERNS:
            if re.match(pattern, stripped):
                is_emitter = True
                break

        if is_emitter:
            # Replace with comment
            new_line = f"# REMOVED: {line.rstrip()}\n"
            if dry_run:
                changed_lines.append(f"  Line {i + 1}: {line.rstrip()} -> {new_line.strip()}")
            else:
                lines[i] = new_line
                changed_lines.append(f"  Line {i + 1}: REMOVED {line.rstrip()}")
            lines_changed += 1

    if not dry_run and lines_changed > 0:
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

    return lines_changed, changed_lines


def find_all_test_files_with_emitters() -> list[Path]:
    """Find all test files that contain emitter calls."""
    test_files = []
    tests_dir = Path("tests")

    if not tests_dir.exists():
        print("tests/ directory not found")
        return test_files

    for py_file in tests_dir.rglob("*.py"):
        emitter_calls = find_emitter_calls(py_file)
        if emitter_calls:
            test_files.append(py_file)

    return test_files


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Strip bootstrap emitters from test files")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed without applying")
    parser.add_argument("--apply", action="store_true", help="Apply the changes")
    parser.add_argument("--file", help="Process specific file")
    parser.add_argument("--threshold", type=int, default=1, help="Minimum emitter calls to process")

    args = parser.parse_args()

    if args.apply and args.dry_run:
        print("ERROR: Cannot use both --apply and --dry-run")
        return

    if not args.apply and not args.dry_run:
        args.dry_run = True  # Default to dry-run for safety

    print("=== Phase 0.1: Bootstrap Emitter Cleanup ===")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'APPLY'}")
    print()

    # Find target files
    if args.file:
        target_files = [Path(args.file)]
    else:
        target_files = find_all_test_files_with_emitters()

    if not target_files:
        print("No test files with emitter calls found")
        return

    print(f"Found {len(target_files)} test files with emitter calls")
    print()

    total_emitters = 0
    total_files_changed = 0

    for file_path in sorted(target_files):
        emitter_calls = find_emitter_calls(file_path)

        if len(emitter_calls) < args.threshold:
            continue

        print(f"File: {file_path}")
        print(f"  Emitter calls: {len(emitter_calls)}")

        for line_num, call in emitter_calls[:5]:  # Show first 5
            print(f"    Line {line_num}: {call}")
        if len(emitter_calls) > 5:
            print(f"    ... and {len(emitter_calls) - 5} more")

        # Strip emitters
        lines_changed, changes = strip_emitters_from_file(file_path, dry_run=args.dry_run)

        if lines_changed > 0:
            total_files_changed += 1
            total_emitters += lines_changed

            print(f"  Changes: {lines_changed} lines")
            for change in changes[:3]:  # Show first 3 changes
                print(f"    {change}")
            if len(changes) > 3:
                print(f"    ... and {len(changes) - 3} more changes")

        print()

    print("=== Summary ===")
    print(f"Files processed: {len(target_files)}")
    print(f"Files with changes: {total_files_changed}")
    print(f"Total emitter calls removed: {total_emitters}")

    if args.dry_run:
        print()
        print("DRY RUN COMPLETE - No files were modified")
        print("Run with --apply to make changes")
    else:
        print()
        print("CHANGES APPLIED")
        print("Run pytest --collect-only to verify performance improvement")


if __name__ == "__main__":
    main()
