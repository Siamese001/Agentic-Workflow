#!/usr/bin/env python3
"""
post_commit_outcome_binder.py — Bind executed decisions to their commit outcomes.

Closes the harness HITL learning loop by writing decision_outcomes rows for any
surfaced decision whose files_in_scope overlap a recent commit's touched files.

INVOCATION MODES
----------------
1. Standalone (default): scan the last N commits on the current branch, match
   each against surfaced decisions, write outcome rows.

       python .windsurf/scripts/post_commit_outcome_binder.py
       python .windsurf/scripts/post_commit_outcome_binder.py --lookback 20

2. Git post-commit hook: bind the single HEAD commit. Invoked from
   `.git/hooks/post-commit` with `--head`.

       python .windsurf/scripts/post_commit_outcome_binder.py --head

3. Dry-run: report what would be bound without writing.

       python .windsurf/scripts/post_commit_outcome_binder.py --dry-run

MATCH RULE
----------
A decision is considered "executed by" a commit when:
    - decision.status == 'surfaced', AND
    - the intersection of decision_scope.file_path (JSON coerced) and the
      commit's touched files is non-empty, AND
    - the commit timestamp is AFTER decision.created_at, AND
    - no prior outcome row exists for (decision_id).

OUTCOME LABELS
--------------
    - success   : tests_passed=1 AND regression_found=0 AND rollback_required=0
    - rework    : regression_found=1 OR tests_passed=0
    - rollback  : rollback_required=1 (commit message contains 'Revert' or 'ROLLBACK')
    - undecided : no test signal available at bind time

CONSTITUTIONAL COMPLIANCE
-------------------------
    - No PowerShell; subprocess.run with argv + shell=False + timeout=30
    - UTF-8 explicit encoding on all file/stdio ops
    - Specific exceptions (sqlite3.Error, subprocess.TimeoutExpired, OSError, ValueError)
    - Progress bar when lookback > 10 (tqdm)
"""

from __future__ import annotations

import argparse
import json
import logging
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

try:
    from tqdm import tqdm
except ImportError:  # pragma: no cover — tqdm is a project dep but allow degradation

    def tqdm(x, **_kwargs):  # type: ignore[no-redef]
        return x


REPO_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = REPO_ROOT / ".windsurf" / "state" / "refactor_decisions" / "refactor_decision_ledger.sqlite"

DEFAULT_LOOKBACK = 5
GIT_TIMEOUT_S = 15

_LOG = logging.getLogger("post_commit_outcome_binder")


# --------------------------------------------------------------------- #
# Git helpers                                                           #
# --------------------------------------------------------------------- #


def _git(argv: list[str]) -> str:
    """Run git with shell=False + timeout; return stdout stripped."""
    try:
        result = subprocess.run(
            ["git", *argv],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
            timeout=GIT_TIMEOUT_S,
            check=False,
        )
    except subprocess.TimeoutExpired:
        _LOG.error("git %s timed out after %ss", " ".join(argv), GIT_TIMEOUT_S)
        return ""
    except OSError as exc:
        _LOG.error("git %s failed: %s", " ".join(argv), exc)
        return ""
    if result.returncode != 0:
        _LOG.warning("git %s exit %s: %s", " ".join(argv), result.returncode, result.stderr.strip())
        return ""
    return result.stdout.strip()


def recent_commits(lookback: int) -> list[dict]:
    """Return list of recent commits: [{sha, ts, subject, files: [...]}, ...]."""
    if lookback <= 0:
        return []
    # Format: SHA\x1ftimestamp\x1fsubject
    raw = _git(["log", f"-n{lookback}", "--pretty=format:%H%x1f%cI%x1f%s"])
    if not raw:
        return []
    out: list[dict] = []
    for line in raw.splitlines():
        parts = line.split("\x1f")
        if len(parts) != 3:
            continue
        sha, ts, subject = parts
        files_raw = _git(["diff-tree", "--no-commit-id", "--name-only", "-r", sha])
        files = [f for f in files_raw.splitlines() if f]
        out.append({"sha": sha, "ts": ts, "subject": subject, "files": files})
    return out


def head_commit() -> list[dict]:
    return recent_commits(1)


# --------------------------------------------------------------------- #
# Ledger helpers                                                        #
# --------------------------------------------------------------------- #


def open_db() -> sqlite3.Connection | None:
    if not DB_PATH.exists():
        _LOG.info("Ledger DB absent: %s — nothing to bind.", DB_PATH)
        return None
    try:
        conn = sqlite3.connect(str(DB_PATH), timeout=10)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as exc:
        _LOG.error("Cannot open ledger: %s", exc)
        return None


def unbound_decisions(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    """Decisions with status='surfaced' and no existing outcome row."""
    cur = conn.execute(
        """
        SELECT d.decision_id, d.created_at, d.decision_type, d.normalized_intent
          FROM decisions d
          LEFT JOIN decision_outcomes o ON o.decision_id = d.decision_id
         WHERE d.status = 'surfaced'
           AND o.outcome_id IS NULL
         ORDER BY d.created_at DESC
         LIMIT 500
        """
    )
    return cur.fetchall()


def decision_files(conn: sqlite3.Connection, decision_id: str) -> set[str]:
    cur = conn.execute(
        "SELECT file_path FROM decision_scope WHERE decision_id = ? AND file_path IS NOT NULL",
        (decision_id,),
    )
    return {row[0] for row in cur.fetchall() if row[0]}


# --------------------------------------------------------------------- #
# Matching + outcome classification                                     #
# --------------------------------------------------------------------- #


def _overlap(a: Iterable[str], b: Iterable[str]) -> set[str]:
    sa = {p.replace("\\", "/") for p in a}
    sb = {p.replace("\\", "/") for p in b}
    return sa & sb


def classify_outcome(subject: str) -> tuple[str, dict[str, int]]:
    """Infer outcome label from commit subject line alone.

    In W2 we do not run tests automatically; test signal comes from either
    an explicit `--tests-passed` invocation or a CI hook writing back later.
    """
    lower = subject.lower()
    flags = {
        "execution_completed": 1,
        "tests_passed": 0,
        "regression_found": 0,
        "rollback_required": 0,
        "promote_to_pattern": 0,
        "pattern_promotion_eligible": 0,
    }
    if any(tok in lower for tok in ("revert ", "rollback", "hotfix revert")):
        flags["rollback_required"] = 1
        return "rollback", flags
    if any(tok in lower for tok in ("regression", "bug:", "fix regression")):
        flags["regression_found"] = 1
        return "rework", flags
    if any(tok in lower for tok in ("fix ", "bugfix")):
        return "rework", flags
    # Default assumption: clean commit, outcome undecided until tests reported
    return "undecided", flags


# --------------------------------------------------------------------- #
# Bind                                                                  #
# --------------------------------------------------------------------- #


def bind(conn: sqlite3.Connection, commits: list[dict], dry_run: bool) -> int:
    decisions = unbound_decisions(conn)
    if not decisions:
        _LOG.info("No unbound decisions.")
        return 0

    iterator: Iterable[sqlite3.Row]
    iterator = tqdm(decisions, desc="Binding outcomes", unit="dec") if len(decisions) > 10 else decisions

    bound_count = 0
    now = datetime.now(timezone.utc)

    for dec in iterator:
        decision_id = dec["decision_id"]
        created_at = dec["created_at"]
        scope_files = decision_files(conn, decision_id)
        if not scope_files:
            continue

        # Find the first commit AFTER decision.created_at that touches a scope file
        best = None
        for c in commits:
            if c["ts"] <= created_at:
                continue
            if _overlap(scope_files, c["files"]):
                best = c
                break
        if best is None:
            continue

        label, flags = classify_outcome(best["subject"])
        try:
            dec_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        except ValueError:
            dec_dt = now
        latency_s = int((now - dec_dt).total_seconds())

        _LOG.info(
            "Bind %s ← commit %s (%s) label=%s latency=%ss",
            decision_id,
            best["sha"][:8],
            best["subject"][:50],
            label,
            latency_s,
        )

        if dry_run:
            bound_count += 1
            continue

        try:
            conn.execute(
                """
                INSERT INTO decision_outcomes (
                    decision_id,
                    execution_completed, tests_passed, regression_found,
                    rollback_required, promote_to_pattern,
                    commit_shas_json, files_written_json, tests_run_json,
                    latency_to_outcome_s, pattern_promotion_eligible,
                    outcome_label, bound_at, outcome_notes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    decision_id,
                    flags["execution_completed"],
                    flags["tests_passed"],
                    flags["regression_found"],
                    flags["rollback_required"],
                    flags["promote_to_pattern"],
                    json.dumps([best["sha"]]),
                    json.dumps(sorted(_overlap(scope_files, best["files"]))),
                    json.dumps([]),
                    latency_s,
                    flags["pattern_promotion_eligible"],
                    label,
                    now.isoformat(timespec="seconds"),
                    f"auto-bound from commit subject: {best['subject'][:200]}",
                ),
            )
            conn.execute(
                "UPDATE decisions SET status = 'executed', commit_sha = ? WHERE decision_id = ?",
                (best["sha"], decision_id),
            )
            conn.commit()
            bound_count += 1
        except sqlite3.Error as exc:
            _LOG.error("Failed to bind %s: %s", decision_id, exc)
            conn.rollback()

    return bound_count


# --------------------------------------------------------------------- #
# CLI                                                                   #
# --------------------------------------------------------------------- #


def main() -> int:
    parser = argparse.ArgumentParser(description="Bind decision outcomes from recent commits.")
    parser.add_argument(
        "--lookback", type=int, default=DEFAULT_LOOKBACK, help=f"Commits to scan (default {DEFAULT_LOOKBACK})"
    )
    parser.add_argument(
        "--head", action="store_true", help="Bind only the HEAD commit (git post-commit hook mode)"
    )
    parser.add_argument("--dry-run", action="store_true", help="Report without writing")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    conn = open_db()
    if conn is None:
        return 0  # absent DB is not an error — first run scenario

    try:
        commits = head_commit() if args.head else recent_commits(args.lookback)
        if not commits:
            _LOG.info("No commits returned from git log.")
            return 0
        _LOG.info("Scanning %d commit(s)…", len(commits))
        bound = bind(conn, commits, dry_run=args.dry_run)
        verb = "Would bind" if args.dry_run else "Bound"
        _LOG.info("%s %d outcome(s).", verb, bound)
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
