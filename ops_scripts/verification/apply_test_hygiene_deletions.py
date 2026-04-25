"""Phase 1 — Apply deletions from the test-hygiene audit.

Reads the latest `artifacts/test_audit/test_audit_*.json` report and produces
a deletion plan. Default mode is dry-run. Pass `--apply` to actually delete
via `git rm` (reversible via `git restore`).

Deletion policy:
    mechanical_twin   -> keep 1 representative per exact-hash group, delete rest
    near_twin         -> keep 1 representative per normalized-hash group, delete rest
    broken_assertions -> delete all (they reference symbols that don't exist)
    importorskip_smoke/substantive/unreadable -> never delete

Representative selection heuristic (per twin group):
    1. prefer files WITHOUT `_adg` suffix
    2. prefer shorter path
    3. tie-break alphabetically

Usage:
    python ops_scripts/verification/apply_test_hygiene_deletions.py          # dry run
    python ops_scripts/verification/apply_test_hygiene_deletions.py --apply  # execute
    python ops_scripts/verification/apply_test_hygiene_deletions.py --include-near-twins --apply
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = REPO_ROOT / "artifacts" / "test_audit"


def find_latest_report() -> Path:
    reports = sorted(AUDIT_DIR.glob("test_audit_*.json"))
    if not reports:
        print(f"[error] no audit reports found in {AUDIT_DIR}", file=sys.stderr)
        print("Run: python ops_scripts/verification/audit_test_suite_hygiene.py", file=sys.stderr)
        sys.exit(1)
    return reports[-1]


def _path_score(path: str) -> tuple[int, int, str]:
    """Lower score = preferred representative.

    Prefers paths without `_adg`, then shorter paths, then alphabetic.
    """
    has_adg = 1 if "_adg" in Path(path).stem else 0
    return (has_adg, len(path), path)


def pick_representative(group: list[dict[str, Any]]) -> dict[str, Any]:
    return min(group, key=lambda r: _path_score(r["path"]))


def build_deletion_plan(
    records: list[dict[str, Any]],
    include_near_twins: bool,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, int]]:
    """Return (to_delete, to_keep_representatives, stats)."""
    # Safety: never consider substantive/unreadable for deletion
    forbidden = {"substantive", "unreadable"}

    # Group mechanical twins by exact hash
    mech_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    near_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    broken: list[dict[str, Any]] = []

    for r in records:
        bucket = r.get("bucket")
        if bucket in forbidden:
            continue
        if bucket == "mechanical_twin":
            mech_groups[r["exact_hash"]].append(r)
        elif bucket == "near_twin":
            near_groups[r["normalized_hash"]].append(r)
        elif bucket == "broken_assertions":
            broken.append(r)

    to_delete: list[dict[str, Any]] = []
    representatives: list[dict[str, Any]] = []
    stats: dict[str, int] = defaultdict(int)

    for group in mech_groups.values():
        if len(group) < 2:
            continue  # safety: not a real twin
        rep = pick_representative(group)
        representatives.append(rep)
        stats["mechanical_groups"] += 1
        for r in group:
            if r is rep:
                continue
            to_delete.append({"reason": "mechanical_twin", "path": r["path"], "kept": rep["path"]})
            stats["mechanical_twin_deletions"] += 1

    if include_near_twins:
        for group in near_groups.values():
            if len(group) < 2:
                continue
            rep = pick_representative(group)
            representatives.append(rep)
            stats["near_groups"] += 1
            for r in group:
                if r is rep:
                    continue
                to_delete.append({"reason": "near_twin", "path": r["path"], "kept": rep["path"]})
                stats["near_twin_deletions"] += 1

    for r in broken:
        to_delete.append({"reason": "broken_assertions", "path": r["path"], "kept": None})
        stats["broken_assertions_deletions"] += 1

    return to_delete, representatives, dict(stats)


def verify_safety(to_delete: list[dict[str, Any]], records: list[dict[str, Any]]) -> None:
    """Hard-fail if any path marked for deletion is classified as substantive."""
    substantive = {r["path"] for r in records if r.get("bucket") == "substantive"}
    kept_representatives_in_delete = {d["kept"] for d in to_delete if d.get("kept")}
    # Check no substantive file is in deletion list
    collisions = [d["path"] for d in to_delete if d["path"] in substantive]
    if collisions:
        print(f"[fatal] deletion plan would remove {len(collisions)} substantive file(s):", file=sys.stderr)
        for c in collisions[:10]:
            print(f"  {c}", file=sys.stderr)
        sys.exit(2)
    # Check representatives are not in deletion list
    overlap = {d["path"] for d in to_delete} & kept_representatives_in_delete
    if overlap:
        print(f"[fatal] representative files would be deleted: {overlap}", file=sys.stderr)
        sys.exit(2)


def git_rm(paths: list[str]) -> int:
    """Batch-delete via `git rm --cached -f`-like semantics.

    Uses plain `git rm` so files are tracked as deletions. Runs in chunks
    of 100 to stay under command-line length limits.
    """
    if not paths:
        return 0
    failed = 0
    chunk_size = 100
    for i in range(0, len(paths), chunk_size):
        chunk = paths[i : i + chunk_size]
        args = ["git", "rm", "-q", "-f", *chunk]
        try:
            result = subprocess.run(
                args,
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            print(f"[error] git rm failed: {exc}", file=sys.stderr)
            failed += len(chunk)
            continue
        if result.returncode != 0:
            print(f"[warn] git rm chunk {i // chunk_size} returned {result.returncode}", file=sys.stderr)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            failed += len(chunk)
    return failed


def write_plan_report(
    to_delete: list[dict[str, Any]],
    stats: dict[str, int],
    applied: bool,
) -> Path:
    ts = datetime.now(timezone.utc).strftime("%m%d%Y_%H%M")
    path = AUDIT_DIR / f"deletion_plan_{ts}.md"
    lines: list[str] = []
    lines.append("# Test Hygiene Deletion Plan")
    lines.append("")
    lines.append(f"- **Generated (UTC)**: {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    lines.append(f"- **Mode**: {'APPLIED (git rm)' if applied else 'DRY RUN'}")
    lines.append(f"- **Files to delete**: {len(to_delete)}")
    lines.append("")
    lines.append("## Stats")
    lines.append("")
    lines.append("| Category | Count |")
    lines.append("|---|---:|")
    for k, v in stats.items():
        lines.append(f"| `{k}` | {v} |")
    lines.append("")
    lines.append("## Deletion List (first 50)")
    lines.append("")
    lines.append("| Path | Reason | Kept Representative |")
    lines.append("|---|---|---|")
    for d in to_delete[:50]:
        kept = d["kept"] or "—"
        lines.append(f"| `{d['path']}` | `{d['reason']}` | `{kept}` |")
    if len(to_delete) > 50:
        lines.append("")
        lines.append(f"_...and {len(to_delete) - 50} more._")
    lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="actually delete files (default: dry run)")
    parser.add_argument(
        "--include-near-twins", action="store_true", help="include near_twin bucket in deletion"
    )
    parser.add_argument("--report", type=Path, default=None, help="path to audit JSON (default: latest)")
    args = parser.parse_args()

    report_path = args.report or find_latest_report()
    print(f"[info] reading audit report: {report_path.relative_to(REPO_ROOT)}", file=sys.stderr)
    with report_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    records: list[dict[str, Any]] = data["records"]

    to_delete, representatives, stats = build_deletion_plan(
        records,
        include_near_twins=args.include_near_twins,
    )

    print(f"\n[info] deletion plan:", file=sys.stderr)
    for k, v in stats.items():
        print(f"    {k}: {v}", file=sys.stderr)
    print(f"    TOTAL FILES TO DELETE: {len(to_delete)}", file=sys.stderr)

    verify_safety(to_delete, records)
    print("[info] safety check passed: no substantive files in deletion list", file=sys.stderr)

    plan_path = write_plan_report(to_delete, stats, applied=args.apply)
    print(f"\nWrote: {plan_path}", file=sys.stderr)

    if not args.apply:
        print("\n[dry-run] no files deleted. Re-run with --apply to execute.", file=sys.stderr)
        return 0

    print(f"\n[info] executing git rm for {len(to_delete)} files...", file=sys.stderr)
    failed = git_rm([d["path"] for d in to_delete])
    if failed:
        print(
            f"[warn] {failed} files could not be removed (may have been already deleted or untracked)",
            file=sys.stderr,
        )
    print(f"[done] Phase 1 complete. Review with `git status` and commit.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
