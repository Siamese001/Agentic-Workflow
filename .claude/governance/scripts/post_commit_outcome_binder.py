#!/usr/bin/env python3
"""
post_commit_outcome_binder.py — Bind executed decisions to their commit outcomes.

Closes the Author-Gate (developer-loop) learning loop by writing decision_outcomes
rows for any surfaced decision whose files_in_scope overlap a recent commit's
touched files. Distinct from runtime HITL (ADR-023, agentic_core/L5_safety/).

INVOCATION MODES
----------------
1. Standalone (default): scan the last N commits on the current branch, match
   each against surfaced decisions, write outcome rows.

       python .claude/governance/scripts/post_commit_outcome_binder.py
       python .claude/governance/scripts/post_commit_outcome_binder.py --lookback 20

2. Git post-commit hook: bind the single HEAD commit. Invoked from
   `.git/hooks/post-commit` with `--head`.

       python .claude/governance/scripts/post_commit_outcome_binder.py --head

3. Dry-run: report what would be bound without writing.

       python .claude/governance/scripts/post_commit_outcome_binder.py --dry-run

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

from tools.refactor_decisions.bind_confidence import (
    BIND_DISPUTED,
    BIND_HIGH,
    BindConfidenceInput,
    classify_bind_confidence,
    default_binding_window_seconds,
    dispute_id_set_from_env,
    parse_ci_receipt,
    refine_outcome_label_with_ci,
    ci_receipt_path_from_env,
)

try:
    from tqdm import tqdm
except ImportError:  # pragma: no cover — tqdm is a project dep but allow degradation

    def tqdm(x, **_kwargs):  # type: ignore[no-redef]
        return x


REPO_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = REPO_ROOT / ".cursor" / "state" / "refactor_decisions" / "refactor_decision_ledger.sqlite"

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
    """Decisions with status in ('surfaced','executed') and no existing outcome row.

    The v2 capture hook writes status='executed' directly when the DECISION_CAPTURED
    marker carries outcome=executed. Prior to this fix the binder only looked at
    status='surfaced', which meant every v2-captured decision was orphaned (no
    decision_outcomes row) — breaking the meta-learning loop. The outcome write is
    idempotent, so accepting both states is safe.
    """
    cur = conn.execute(
        """
        SELECT d.decision_id, d.created_at, d.decision_type, d.normalized_intent,
               d.commit_sha
          FROM decisions d
          LEFT JOIN decision_outcomes o ON o.decision_id = d.decision_id
         WHERE d.status IN ('surfaced', 'executed')
           AND o.outcome_id IS NULL
         ORDER BY d.created_at DESC
         LIMIT 500
        """
    )
    return cur.fetchall()


def _commit_subject(sha: str) -> str:
    """Return the commit subject for a SHA, or '' on any failure."""
    if not sha:
        return ""
    try:
        r = subprocess.run(
            ["git", "show", "-s", "--format=%s", sha],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
            timeout=GIT_TIMEOUT_S,
            check=False,
        )
    except (subprocess.TimeoutExpired, OSError):
        return ""
    return r.stdout.strip() if r.returncode == 0 else ""


def _commit_files(sha: str) -> list[str]:
    if not sha:
        return []
    files_raw = _git(["diff-tree", "--no-commit-id", "--name-only", "-r", sha])
    return [f for f in files_raw.splitlines() if f]


def _commit_iso_date(sha: str) -> str:
    if not sha:
        return ""
    raw = _git(["show", "-s", "--format=%cI", sha])
    return raw.strip() if raw else ""


def _count_overlapping_commits(scope_files: set[str], commits: list[dict], created_at: str) -> int:
    n = 0
    for c in commits:
        if c["ts"] <= created_at:
            continue
        if _overlap(scope_files, c["files"]):
            n += 1
    return n


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
    # "regression tests" / "regression suite" are feature additions, not rework.
    # Only flag when the subject signals an actual regression fix.
    if any(tok in lower for tok in ("fix regression", "regression fix", "bug:", "bugfix:")):
        flags["regression_found"] = 1
        return "rework", flags
    if any(tok in lower for tok in ("fix ", "bugfix")):
        return "rework", flags
    # Default assumption: clean commit, outcome undecided until tests reported
    return "undecided", flags


# --------------------------------------------------------------------- #
# Bind                                                                  #
# --------------------------------------------------------------------- #


def bind(
    conn: sqlite3.Connection,
    commits: list[dict],
    dry_run: bool,
    *,
    ci_receipt_file: str | None = None,
) -> int:
    decisions = unbound_decisions(conn)
    if not decisions:
        _LOG.info("No unbound decisions.")
        return 0

    iterator: Iterable[sqlite3.Row]
    iterator = tqdm(decisions, desc="Binding outcomes", unit="dec") if len(decisions) > 10 else decisions

    bound_count = 0
    now = datetime.now(timezone.utc)
    dispute_ids = dispute_id_set_from_env()
    receipt_path = Path(ci_receipt_file) if ci_receipt_file else ci_receipt_path_from_env()
    ci_status, ci_meta = parse_ci_receipt(receipt_path)
    window_s = default_binding_window_seconds()

    for dec in iterator:
        decision_id = dec["decision_id"]
        created_at = dec["created_at"]
        scope_files = decision_files(conn, decision_id)
        operator_disputed = decision_id in dispute_ids

        direct_sha = dec["commit_sha"] if "commit_sha" in dec.keys() else None
        best: dict | None = None
        used_direct = False
        if direct_sha:
            subject = _commit_subject(direct_sha)
            if subject:
                files = _commit_files(direct_sha)
                cts = _commit_iso_date(direct_sha) or created_at
                best = {"sha": direct_sha, "subject": subject, "files": files, "ts": cts}
                used_direct = True

        overlapping_n = 1
        if best is None:
            if not scope_files:
                continue
            overlapping_n = _count_overlapping_commits(scope_files, commits, created_at)
            for c in commits:
                if c["ts"] <= created_at:
                    continue
                if _overlap(scope_files, c["files"]):
                    best = c
                    break
            if best is None:
                continue
        elif used_direct:
            overlapping_n = 1

        commit_file_set = set(best["files"])
        label, flags = classify_outcome(best["subject"])
        label, flags = refine_outcome_label_with_ci(label, flags, ci_status, ci_meta)

        bc_in = BindConfidenceInput(
            scope_files=frozenset(scope_files),
            commit_files=frozenset(commit_file_set),
            decision_created_at_iso=created_at,
            commit_timestamp_iso=str(best["ts"]),
            binding_window_seconds=window_s,
            ci_receipt_status=ci_status,
            direct_sha_bind=used_direct,
            overlapping_commit_count=overlapping_n,
            operator_disputed=operator_disputed,
        )
        bind_tier, ci_echo = classify_bind_confidence(bc_in)
        _ = ci_echo  # same as ci_status unless classifier echoes

        promotion_eligible = 1 if bind_tier == BIND_HIGH else 0
        bind_disputed = 1 if (bind_tier == BIND_DISPUTED or operator_disputed) else 0
        overlap_paths = sorted(_overlap(scope_files, commit_file_set))

        try:
            dec_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        except ValueError:
            dec_dt = now
        latency_s = int((now - dec_dt).total_seconds())

        _LOG.info(
            "Bind %s ← commit %s (%s) label=%s bind=%s ci=%s latency=%ss",
            decision_id,
            best["sha"][:8],
            best["subject"][:50],
            label,
            bind_tier,
            ci_status,
            latency_s,
        )

        if dry_run:
            bound_count += 1
            continue

        notes = (
            f"auto-bound: {best['subject'][:160]} | bind_confidence={bind_tier} "
            f"ci_receipt={ci_status} direct={used_direct}"
        )

        try:
            conn.execute(
                """
                INSERT INTO decision_outcomes (
                    decision_id,
                    execution_completed, tests_passed, regression_found,
                    rollback_required, promote_to_pattern,
                    commit_shas_json, files_written_json, tests_run_json,
                    latency_to_outcome_s, pattern_promotion_eligible,
                    outcome_label, bound_at, outcome_notes,
                    bind_confidence, ci_receipt_status, bind_disputed
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    decision_id,
                    flags["execution_completed"],
                    flags["tests_passed"],
                    flags["regression_found"],
                    flags["rollback_required"],
                    flags["promote_to_pattern"],
                    json.dumps([best["sha"]]),
                    json.dumps(overlap_paths),
                    json.dumps([]),
                    latency_s,
                    promotion_eligible,
                    label,
                    now.isoformat(timespec="seconds"),
                    notes,
                    bind_tier,
                    ci_status,
                    bind_disputed,
                ),
            )
            conn.execute(
                "UPDATE decisions SET status = 'executed', commit_sha = ? WHERE decision_id = ?",
                (best["sha"], decision_id),
            )
            conn.commit()
            bound_count += 1

            try:
                from tools.ledgers.hook_helpers import emit_ledger_event

                dec_type = dec["decision_type"] if "decision_type" in dec.keys() else "unknown"
                emit_ledger_event(
                    ledger="refactor_outcome",
                    event_kind="wave_outcome",
                    prediction={
                        "decision_id": decision_id,
                        "decision_type": dec_type,
                    },
                    outcome={
                        "commit_sha": best["sha"],
                        "commit_subject": best["subject"][:200],
                        "outcome_label": label,
                        "latency_to_outcome_s": latency_s,
                        "bind_confidence": bind_tier,
                    },
                    score_band=label if label in ("success", "rework", "rollback") else "partial",
                    commit_sha=best["sha"],
                    latency_ms=int(latency_s) * 1000 if latency_s else None,
                    repo_area=".claude/governance/scripts/post_commit_outcome_binder.py",
                )
            except Exception:  # noqa: BLE001
                # guardian: allow-broad-except -- ledger emit fail-soft
                pass
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
    parser.add_argument(
        "--ci-receipt",
        type=str,
        default="",
        help="CI receipt JSON path (overrides AG_BIND_CI_RECEIPT_PATH)",
    )
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
        bound = bind(
            conn,
            commits,
            dry_run=args.dry_run,
            ci_receipt_file=args.ci_receipt.strip() or None,
        )
        verb = "Would bind" if args.dry_run else "Bound"
        _LOG.info("%s %d outcome(s).", verb, bound)
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
