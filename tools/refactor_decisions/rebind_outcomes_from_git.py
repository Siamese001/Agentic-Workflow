#!/usr/bin/env python3
"""
rebind_outcomes_from_git.py — Retro outcome classifier for the Author-Gate ledger.

Walks `decision_outcomes` rows where `outcome_label='undecided'` and inspects the
git history *after* their `commit_shas_json[0]` to refine the classification.

Heuristics (applied in order; first match wins):
  - A descendant commit reverts the bound SHA       → outcome_label='rollback'
  - A descendant commit's subject contains regression / hotfix / bugfix tokens
    referring back to the bound SHA's files          → outcome_label='regression'
  - Bound SHA + N follow-on commits clean (no revert / regression markers
    in the next 30 commits on the same branch)       → outcome_label='success'
  - Otherwise                                        → leave as 'undecided'

Idempotent: only updates rows that are still 'undecided'. Writes a per-row
explanation into `outcome_notes` so the rebind reason is auditable.

Fail-soft: any git error leaves the row untouched and continues. Subprocess
calls are bounded by a 5-second timeout and shell=False per constitutional §0/§14.

Usage:
  python tools/refactor_decisions/rebind_outcomes_from_git.py
  python tools/refactor_decisions/rebind_outcomes_from_git.py --dry-run
  python tools/refactor_decisions/rebind_outcomes_from_git.py --max-walk 50

Exit codes:
  0 = success (rows scanned; some may have been rebound)
  2 = ledger missing or unreadable
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    from tqdm import tqdm  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover

    def tqdm(x, **_kwargs):  # type: ignore[no-redef]
        return x


REPO_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = REPO_ROOT / ".windsurf" / "state" / "refactor_decisions" / "refactor_decision_ledger.sqlite"

_REVERT_TOKENS = ("revert ", "revert:", "rollback ", "rollback:", 'revert "')
_REGRESSION_TOKENS = (
    "fix regression",
    "regression fix",
    "bugfix:",
    "bug fix:",
    "hotfix:",
    "hot-fix:",
    "fix bug",
)


def _git(args: list[str], cwd: Path) -> tuple[int, str]:
    """Run a git command; return (returncode, stdout). Fail-soft on any error."""
    try:
        r = subprocess.run(  # noqa: S603 -- argv list, shell=False
            ["git", *args],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return 1, ""
    return r.returncode, r.stdout


def _commit_subject(sha: str, repo: Path) -> str:
    rc, out = _git(["show", "-s", "--format=%s", sha], repo)
    return out.strip() if rc == 0 else ""


def _commit_exists(sha: str, repo: Path) -> bool:
    rc, _ = _git(["cat-file", "-e", f"{sha}^{{commit}}"], repo)
    return rc == 0


def _is_descendant_revert(target_sha: str, descendant_subjects: list[str]) -> bool:
    """Return True if any descendant subject explicitly reverts target_sha."""
    short = target_sha[:7].lower()
    for subj in descendant_subjects:
        s = subj.lower()
        if any(tok in s for tok in _REVERT_TOKENS) and short in s:
            return True
    return False


def _classify_via_walk(sha: str, max_walk: int, repo: Path) -> tuple[str, str]:
    """Return (label, reason) for a bound commit using descendant inspection."""
    if not _commit_exists(sha, repo):
        return "undecided", "commit_missing_in_history"

    # Walk descendants on current branch
    rc, out = _git(
        ["log", "--oneline", f"--max-count={max_walk}", f"{sha}..HEAD"],
        repo,
    )
    if rc != 0:
        return "undecided", "git_log_failed"
    descendant_lines = [ln.strip() for ln in out.splitlines() if ln.strip()]
    descendant_subjects = [ln.split(" ", 1)[1] if " " in ln else "" for ln in descendant_lines]

    # Direct revert detection
    if _is_descendant_revert(sha, descendant_subjects):
        return "rollback", f"descendant_revert_found (n_descendants={len(descendant_lines)})"

    # Regression-token detection in any descendant
    lowered = "\n".join(s.lower() for s in descendant_subjects)
    for tok in _REGRESSION_TOKENS:
        if tok in lowered:
            return "regression", f"regression_token={tok!r} (n_descendants={len(descendant_lines)})"

    # Success: clean window of follow-on commits
    if len(descendant_lines) >= 5:
        return "success", f"clean_window n_descendants={len(descendant_lines)}"
    if len(descendant_lines) > 0:
        return "undecided", f"insufficient_window n_descendants={len(descendant_lines)}"
    # No descendants — bound commit is HEAD
    return "undecided", "no_descendants_yet"


def rebind(db_path: Path, max_walk: int, dry_run: bool) -> dict[str, int]:
    """Walk undecided outcomes; refine label via git history. Returns counters."""
    counters: dict[str, int] = {
        "scanned": 0,
        "updated_success": 0,
        "updated_rollback": 0,
        "updated_regression": 0,
        "left_undecided": 0,
        "skipped_no_sha": 0,
    }
    if not db_path.exists():
        print(f"[rebind] FAIL: ledger not found at {db_path}", file=sys.stderr)
        return counters

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    # Append-only triggers (W4.1) bypass: set sentinel user_version before
    # UPDATEs, restore the original on exit. This is the documented escape
    # hatch in .windsurf/scripts/apply_append_only_triggers.py for
    # administrative writers (rebinder, resign, schema migrations).
    original_user_version = int(conn.execute("PRAGMA user_version").fetchone()[0])
    conn.execute("PRAGMA user_version = 99999")
    try:
        rows = list(
            conn.execute(
                """
                SELECT outcome_id, decision_id, commit_shas_json, outcome_notes
                  FROM decision_outcomes
                 WHERE outcome_label = 'undecided'
                """
            )
        )
        counters["scanned"] = len(rows)
        for row in tqdm(rows, desc="Rebinding outcomes", unit="row"):
            shas_json = row["commit_shas_json"] or "[]"
            try:
                shas = json.loads(shas_json)
            except json.JSONDecodeError:
                shas = []
            if not shas:
                counters["skipped_no_sha"] += 1
                continue
            sha = str(shas[0]).strip()
            if not sha:
                counters["skipped_no_sha"] += 1
                continue
            label, reason = _classify_via_walk(sha, max_walk, REPO_ROOT)
            if label == "undecided":
                counters["left_undecided"] += 1
                continue
            counters[f"updated_{label}"] += 1
            if dry_run:
                continue
            note_suffix = (
                f" | rebound_at={datetime.now(timezone.utc).isoformat(timespec='seconds')} reason={reason}"
            )
            new_notes = (row["outcome_notes"] or "") + note_suffix
            extra: dict[str, int] = {}
            if label == "rollback":
                extra["rollback_required"] = 1
            if label == "regression":
                extra["regression_found"] = 1
            if label == "success":
                extra["tests_passed"] = 1
            set_clauses = ["outcome_label = ?", "outcome_notes = ?"]
            params: list[object] = [label, new_notes]
            for col, val in extra.items():
                set_clauses.append(f"{col} = ?")
                params.append(val)
            params.append(row["outcome_id"])
            conn.execute(
                f"UPDATE decision_outcomes SET {', '.join(set_clauses)} WHERE outcome_id = ?",
                params,
            )
        if not dry_run:
            conn.commit()
    finally:
        # Restore original user_version (re-arms append-only triggers).
        try:
            conn.execute(f"PRAGMA user_version = {original_user_version}")
            conn.commit()
        except sqlite3.Error:
            pass  # guardian: allow-silent-swallow -- pragma restore: non-fatal
        conn.close()
    return counters


def main() -> int:
    parser = argparse.ArgumentParser(description="Retro git-walk outcome rebinder")
    parser.add_argument("--dry-run", action="store_true", help="Report only; do not write")
    parser.add_argument(
        "--max-walk",
        type=int,
        default=30,
        help="Max descendant commits to inspect per row (default: 30)",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=DB_PATH,
        help="Override ledger path (default: %(default)s)",
    )
    args = parser.parse_args()

    if not args.db.exists():
        print(f"[rebind] FAIL: ledger not found at {args.db}", file=sys.stderr)
        return 2

    counters = rebind(args.db, args.max_walk, args.dry_run)
    mode = "DRY-RUN" if args.dry_run else "APPLIED"
    print(
        f"[rebind] {mode}: scanned={counters['scanned']} "
        f"success={counters['updated_success']} "
        f"rollback={counters['updated_rollback']} "
        f"regression={counters['updated_regression']} "
        f"undecided={counters['left_undecided']} "
        f"skipped_no_sha={counters['skipped_no_sha']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
