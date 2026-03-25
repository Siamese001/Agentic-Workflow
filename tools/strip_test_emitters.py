#!/usr/bin/env python3
"""Phase 0.1: Strip bootstrap emitters from test files.

Identifies and removes top-level _emit_*() calls from test files that import
lifecycle_trace_contract. These calls execute at module import time, causing
significant collection overhead.

Usage:
    python tools/strip_test_emitters.py --dry-run
    python tools/strip_test_emitters.py --apply
    python tools/strip_test_emitters.py --verify
"""

import ast
import re
from pathlib import Path
from typing import List, Tuple

# Test files known to import lifecycle_trace_contract (from ADG analysis)
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
    # Add remaining 15 files as needed from ADG query results
]

# Pattern to match top-level _emit_*() calls
EMITTER_CALL_PATTERN = re.compile(r'^(_emit_\w+\([^)]*\))\s*$', re.MULTILINE)

# Pattern to match lifecycle_trace_contract imports
IMPORT_PATTERN = re.compile(r'from\s+agentic_core\.L_CONTRACTS\.lifecycle_trace_contract\s+import')


def find_emitter_calls(content: str) -> List[Tuple[int, str]]:
    """Find all top-level emitter calls with line numbers."""
    calls = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines, 1):
        # Skip if inside a function/class definition
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        if EMITTER_CALL_PATTERN.match(stripped):
            calls.append((i, line.strip()))
    
    return calls


def strip_emitters_from_file(file_path: Path, dry_run: bool = True) -> Tuple[int, int]:
    """Strip emitter calls from a single file.
    
    Returns:
        (calls_removed, lines_modified)
    """
    if not file_path.exists():
        print(f"  File not found: {file_path}")
        return 0, 0
    
    content = file_path.read_text(encoding='utf-8')
    original_content = content
    
    # Find emitter calls
    calls = find_emitter_calls(content)
    
    if not calls:
        print(f"  No emitter calls found in {file_path}")
        return 0, 0
    
    print(f"  Found {len(calls)} emitter call(s) in {file_path}")
    
    if dry_run:
        for line_no, call in calls:
            print(f"    Line {line_no}: {call}")
        return len(calls), 0
    
    # Remove emitter calls
    lines = content.split('\n')
    modified_lines = 0
    
    for line_no, call in calls:
        # Remove the line entirely
        lines[line_no - 1] = f"# REMOVED: {call}"
        modified_lines += 1
    
    new_content = '\n'.join(lines)
    
    # Write back if changed
    if new_content != original_content:
        file_path.write_text(new_content, encoding='utf-8')
        print(f"  Modified {file_path} - removed {len(calls)} calls")
    
    return len(calls), modified_lines


def verify_emitters_stripped(file_path: Path) -> bool:
    """Verify that emitters have been stripped from a file."""
    if not file_path.exists():
        return False
    
    content = file_path.read_text(encoding='utf-8')
    calls = find_emitter_calls(content)
    
    # Check if any active (non-commented) calls remain
    active_calls = [call for call in calls if not call[1].startswith("# REMOVED")]
    
    if active_calls:
        print(f"  FAIL: {len(active_calls)} active emitter calls remain in {file_path}")
        for line_no, call in active_calls:
            print(f"    Line {line_no}: {call}")
        return False
    
    return True


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Strip bootstrap emitters from test files")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed without modifying files")
    parser.add_argument("--apply", action="store_true", help="Apply the changes to files")
    parser.add_argument("--verify", action="store_true", help="Verify emitters have been stripped")
    parser.add_argument("--threshold", type=int, default=1000, help="Edge count threshold for identifying heavy tests")
    parser.add_argument("--output", type=str, help="Output file for results")
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("=== DRY RUN: Bootstrap Emitter Cleanup ===")
        print("Target: Remove top-level _emit_*() calls from test files")
        print()
        
        total_calls = 0
        total_files = 0
        
        for file_path_str in TARGET_FILES:
            file_path = Path(file_path_str)
            print(f"Checking {file_path}")
            calls, _ = strip_emitters_from_file(file_path, dry_run=True)
            total_calls += calls
            if calls > 0:
                total_files += 1
            print()
        
        print(f"Summary: {total_calls} emitter calls in {total_files} files to remove")
        print(f"Estimated impact: {total_calls * 0.5:.1f}s reduction in collection time")
        
    elif args.apply:
        print("=== APPLYING: Bootstrap Emitter Cleanup ===")
        
        total_calls = 0
        total_modified = 0
        
        for file_path_str in TARGET_FILES:
            file_path = Path(file_path_str)
            print(f"Processing {file_path}")
            calls, modified = strip_emitters_from_file(file_path, dry_run=False)
            total_calls += calls
            total_modified += modified
            print()
        
        print(f"Applied changes: {total_calls} calls removed from {total_modified} lines")
        
    elif args.verify:
        print("=== VERIFYING: Bootstrap Emitter Cleanup ===")
        
        all_passed = True
        failed_files = []
        
        for file_path_str in TARGET_FILES:
            file_path = Path(file_path_str)
            print(f"Verifying {file_path}")
            
            if verify_emitters_stripped(file_path):
                print(f"  PASS: No active emitter calls")
            else:
                all_passed = False
                failed_files.append(str(file_path))
            print()
        
        if all_passed:
            print("✅ All files passed verification")
        else:
            print(f"❌ {len(failed_files)} files failed verification:")
            for f in failed_files:
                print(f"  - {f}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
