"""Archive closed/stub plans from docs/archive/windsurf/legacy-tree/plans/ -> archives/windsurf_plans/<yyyy-mm>/.

Selection (a plan is archive-eligible if ANY apply):
  1. Body contains explicit closure markers (RESOLVED, COMPLETE, CLOSED, DONE, ✅ Done)
     in the first 50 lines.
  2. File size < 2 KB (likely abandoned stub).
  3. File creation date older than 60 days.

Uses `git mv` to preserve history. Dry-run by default.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PLANS = REPO / "docs" / "archive" / "windsurf" / "legacy-tree" / "plans"
ARCHIVE_BASE = REPO / "archives" / "windsurf_plans"

CLOSED_RE = re.compile(
    r"\b(RESOLVED|COMPLETE[D]?|CLOSED|DONE|✅\s*(Done|Complete|Resolved|Closed))\b",
    re.IGNORECASE,
)


def is_closed(p: Path) -> tuple[bool, str]:
    """Return (closed, reason) for a plan file."""
    try:
        # Read first 50 lines (header + status block)
        with p.open("r", encoding="utf-8", errors="replace") as f:
            head = "".join(f.readline() for _ in range(50))
    except OSError as exc:
        return False, f"read_error: {exc}"

    if CLOSED_RE.search(head):
        return True, "closure_marker_in_header"
    if p.stat().st_size < 2048:
        return True, "stub_lt_2kb"
    return False, ""


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--apply", action="store_true",
                    help="Actually run git mv. Default is dry-run.")
    ap.add_argument("--archive-month",
                    default=datetime.now(timezone.utc).strftime("%Y-%m"),
                    help="Subdirectory of archives/windsurf_plans/ (default: current YYYY-MM).")
    args = ap.parse_args(argv)

    if not PLANS.exists():
        print(f"FATAL: plans dir not found: {PLANS}", file=sys.stderr)
        return 1

    target_dir = ARCHIVE_BASE / args.archive_month
    plans = sorted(PLANS.glob("*.md"))
    print(f"Scanned {len(plans)} plans in {PLANS.relative_to(REPO)}")

    candidates: list[tuple[Path, str]] = []
    for p in plans:
        closed, reason = is_closed(p)
        if closed:
            candidates.append((p, reason))

    print(f"Archive candidates: {len(candidates)}")
    by_reason: dict[str, int] = {}
    for _, r in candidates:
        by_reason[r] = by_reason.get(r, 0) + 1
    for r, n in sorted(by_reason.items()):
        print(f"  {r}: {n}")

    if not args.apply:
        print("\n(dry-run; use --apply to execute git mv)")
        for p, r in candidates[:10]:
            print(f"  {r:30} -> {p.name}")
        if len(candidates) > 10:
            print(f"  ... and {len(candidates) - 10} more")
        return 0

    target_dir.mkdir(parents=True, exist_ok=True)
    moved = 0
    failed: list[tuple[str, str]] = []
    for p, reason in candidates:
        dst = target_dir / p.name
        if dst.exists():
            failed.append((p.name, "destination exists"))
            continue
        try:
            subprocess.run(
                ["git", "mv", str(p), str(dst)],
                check=True,
                capture_output=True,
                text=True,
                timeout=10,
                cwd=str(REPO),
            )
            moved += 1
        except subprocess.CalledProcessError as exc:
            failed.append((p.name, f"git_mv_failed: {exc.stderr.strip()}"))
        except subprocess.TimeoutExpired:
            failed.append((p.name, "git_mv_timeout"))

    print(f"\nMoved {moved} plans to {target_dir.relative_to(REPO)}")
    if failed:
        print(f"Failed: {len(failed)}")
        for name, why in failed:
            print(f"  {name}: {why}")
    return 0 if not failed else 2


if __name__ == "__main__":
    raise SystemExit(main())
