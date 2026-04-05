#!/usr/bin/env python3
# RELOCATED: Moved from apps_shared/reasoning/ to ops_scripts/general/ (P1-B, 2026-03-11).
"""
restore_app_agents.py - Restore incorrectly archived app agents

Restores 60 app agents from archives/hierarchy_violations/apps_depth/
back to their original locations in apps_lic/ and apps_rg/.

These agents were archived due to a depth-4 violation rule, but depth-4
is valid for app-specific agents.

Usage:
    python scripts/restore_app_agents.py --dry-run
    python scripts/restore_app_agents.py
"""

import argparse
import re
import shutil
import sys
from pathlib import Path

from agentic_core.L0_routing.config import (
    ARCHIVES_DIR,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)

_emit_writes_through("p1", "restore_app_agents", "uwg_governed_write")
_emit_writes_through("p1", "restore_app_agents", "uwg_governed_write_2")
_emit_pulls_context("p1", "restore_app_agents", "context_retrieval")
_emit_pulls_context("p1", "restore_app_agents", "context_retrieval_2")
emit_determinism_digest("trace_restore_app_agents", "restore_app_agents_dispatch")
emit_determinism_digest("trace_restore_app_agents", "restore_app_agents_complete")
_emit_validated_by_safety_plane("p1", "restore_app_agents", "safety_validation")

PROJECT_ROOT = Path(__file__).parent.parent
ARCHIVE_DIR = PROJECT_ROOT / ARCHIVES_DIR / "hierarchy_violations" / "apps_depth"


def extract_original_path(file_path: Path) -> str:
    """
    Extract original path from the violation comment in the file.

    Files have a header like:
    # APPS DEPTH VIOLATION — 2026-01-18 05:20:53
    # apps_lic\\domain\validators\\ASCIIEnforcerAgent.py was depth 4, MUST be 3.
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read(500)  # Read first 500 chars

        # Look for the path pattern
        match = re.search(r"# (apps_(?:lic|rg)[^\s]+\.py) was depth", content)
        if match:
            return match.group(1).replace("\\", "/")
    # guardian: allow-silent-swallow
    except Exception:
        pass

    # Fallback: reconstruct from archive path
    rel_path = file_path.relative_to(ARCHIVE_DIR)
    return str(rel_path).replace("\\", "/")


def get_agents_to_restore() -> list[tuple[Path, Path]]:
    """
    Get list of (source, destination) pairs for restoration.

    Returns:
        List of (archived_path, original_path) tuples
    """
    agents = []

    for archived_file in ARCHIVE_DIR.rglob("*Agent.py"):
        # Skip test files
        if archived_file.name.startswith("Test"):
            continue

        original_rel = extract_original_path(archived_file)
        original_path = PROJECT_ROOT / original_rel

        agents.append((archived_file, original_path))

    return agents


def remove_violation_header(file_path: Path) -> None:
    """Remove the APPS DEPTH VIOLATION header from the file."""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Remove the violation header (first 2-3 lines if they contain APPS DEPTH VIOLATION)
    lines = content.split("\n")
    clean_lines = []
    skip_header = True

    for line in lines:
        if skip_header and ("APPS DEPTH VIOLATION" in line or "was depth" in line):
            continue
        if skip_header and line.strip() == "":
            continue
        skip_header = False
        clean_lines.append(line)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(clean_lines))


def main():
    parser = argparse.ArgumentParser(description="Restore incorrectly archived app agents")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without moving files",
    )
    args = parser.parse_args()

    print("=" * 70)
    print("App Agent Restoration Script")
    print("=" * 70)

    if args.dry_run:
        print("\n[DRY RUN MODE - No files will be moved]\n")

    agents = get_agents_to_restore()
    print(f"Found {len(agents)} agents to restore\n")

    restored = 0
    skipped = 0
    errors = 0

    for archived_path, original_path in sorted(agents, key=lambda x: str(x[1])):
        rel_original = original_path.relative_to(PROJECT_ROOT)

        # Check if destination already exists
        if original_path.exists():
            print(f"  ⊘ SKIP (exists): {rel_original}")
            skipped += 1
            continue

        if args.dry_run:
            print(f"  ○ Would restore: {rel_original}")
            restored += 1
            continue

        try:
            # Create parent directories
            original_path.parent.mkdir(parents=True, exist_ok=True)

            # Move the file
            shutil.move(str(archived_path), str(original_path))

            # Remove violation header
            remove_violation_header(original_path)

            print(f"  ✓ Restored: {rel_original}")
            restored += 1

        # guardian: allow-silent-swallow
        except Exception as e:
            print(f"  ✗ ERROR: {rel_original} - {e}")
            errors += 1

    # Summary
    print(f"\n{'=' * 70}")
    print("Summary:")
    print(f"  Restored: {restored}")
    print(f"  Skipped:  {skipped}")
    print(f"  Errors:   {errors}")

    if args.dry_run:
        print("\n[DRY RUN COMPLETE - Run without --dry-run to execute]")
    else:
        print("\n✓ RESTORATION COMPLETE")
        print("\nNext step: Regenerate agent_discovery_full.json")
        print("  python scripts/full_agent_discovery.py")

    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
