"""ADG Skip-File Ratchet — count ratchet for # adg-grep-ban: skip-file directives.

The # adg-grep-ban: skip-file escape hatch is legitimate for test fixture files
that contain banned patterns as string literals.  But the count must never grow
beyond the committed baseline — otherwise the escape hatch becomes an easy path
to silently erode grep-ban enforcement.

This gate:
  1. Counts all # adg-grep-ban: skip-file directives in tracked Python files.
  2. Compares against the baseline in ops_scripts/hooks/skip_file_budget.json.
  3. FAILS if count > baseline (new skip-file added without updating the baseline).
  4. Prints a WARNING (non-blocking) if count < baseline (budget shrank — tighten it).

To legitimately add a new skip-file directive:
  1. Add the directive to your file.
  2. Run this script with --update to lock in the new baseline.
  3. Commit both the file AND the updated skip_file_budget.json together.

Exit codes:
  0 — count <= baseline (clean or shrank)
  1 — count > baseline (new skip-file added without updating ratchet)
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)

_emit_writes_through("p1", "adg_skip_file_ratchet", "uwg_governed_write")
_emit_writes_through("p1", "adg_skip_file_ratchet", "uwg_governed_write_2")
_emit_pulls_context("p1", "adg_skip_file_ratchet", "context_retrieval")
_emit_pulls_context("p1", "adg_skip_file_ratchet", "context_retrieval_2")
emit_determinism_digest("trace_adg_skip_file_ratchet", "adg_skip_file_ratchet_dispatch")
emit_determinism_digest("trace_adg_skip_file_ratchet", "adg_skip_file_ratchet_complete")
_emit_validated_by_safety_plane("p1", "adg_skip_file_ratchet", "safety_validation")

ROOT = Path(__file__).resolve().parents[2]
BUDGET_FILE = ROOT / "ops_scripts" / "hooks" / "skip_file_budget.json"

_DIRECTIVE = "adg-grep-ban: skip-file"


def _count_skip_files(root: Path) -> list[str]:
    """Return sorted list of tracked Python files containing # adg-grep-ban: skip-file."""
    r = subprocess.run(
        ["git", "ls-files"],
        cwd=str(root),
        capture_output=True,
        encoding="utf-8",
        timeout=60,
    )
    hits: list[str] = []
    for rel in r.stdout.splitlines():
        if not rel.endswith(".py"):
            continue
        try:
            lines = (root / rel).read_text(encoding="utf-8", errors="replace").splitlines()
            for line in lines[:10]:
                if _DIRECTIVE in line.lower():
                    hits.append(rel)
                    break
        except OSError:    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging
            pass
    return sorted(hits)


def _load_baseline() -> int:
    """Load the committed baseline count from skip_file_budget.json."""
    if not BUDGET_FILE.exists():
        return 0
    try:
        data = json.loads(BUDGET_FILE.read_text(encoding="utf-8"))
        return int(data.get("baseline", 0))
    except (json.JSONDecodeError, ValueError, TypeError):
        return 0


def _save_baseline(count: int, files: list[str]) -> None:
    """Write a new baseline to skip_file_budget.json."""
    BUDGET_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "baseline": count,
        "note": (
            "Number of tracked Python files allowed to carry '# adg-grep-ban: skip-file'. "
            "Increment only for files that legitimately contain banned patterns as string "
            "literals (test fixtures). Run with --update to tighten after removal."
        ),
        "files": files,
    }
    BUDGET_FILE.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main(update: bool = False) -> int:
    files = _count_skip_files(ROOT)
    count = len(files)
    baseline = _load_baseline()

    if update:
        _save_baseline(count, files)
        print(f"OK: skip-file ratchet updated to baseline={count}.")
        for f in files:
            print(f"  {f}")
        return 0

    if count > baseline:
        print(
            f"\nFAIL: skip-file ratchet exceeded — {count} files have "
            f"'# adg-grep-ban: skip-file' (baseline={baseline}).\n",
            file=sys.stderr,
        )
        print("New file(s) with skip-file directive:", file=sys.stderr)
        for f in files:
            print(f"  {f}", file=sys.stderr)
        print(
            "\nTo legitimately add a skip-file directive:\n"
            "  1. Confirm the file truly needs it (test fixture with banned patterns as literals).\n"
            "  2. Run:  python ops_scripts/ci/adg_skip_file_ratchet.py --update\n"
            "  3. Commit both the file AND ops_scripts/hooks/skip_file_budget.json.\n",
            file=sys.stderr,
        )
        return 1

    if count < baseline:
        print(
            f"[adg-skip-file-ratchet] NOTE: count ({count}) < baseline ({baseline}). "
            f"Run with --update to tighten the ratchet.",
            file=sys.stderr,
        )

    print(f"OK: skip-file ratchet OK ({count}/{baseline}).")
    return 0


def _cli() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        prog="adg_skip_file_ratchet",
        description="Ratchet gate: count # adg-grep-ban: skip-file directives vs baseline.",
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Write current count as the new baseline (use when legitimately adding skip-file)",
    )
    args = parser.parse_args()
    sys.exit(main(update=args.update))


if __name__ == "__main__":
    _cli()
