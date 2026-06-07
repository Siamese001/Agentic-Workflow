#!/usr/bin/env python3
"""
promote_author_gate_patterns.py — Weekly pattern promotion for Author-Gate meta-learning.

Flips ``decision_outcomes.promote_to_pattern = 1`` on decisions that qualify as
reusable patterns, and backfills ``decision_outcomes.outcome_label`` on rows that
were bound before the label column existed.

PROMOTION CRITERIA (W3)
-----------------------
    - Outcome bound, clean, **high** bind confidence (or legacy NULL unless
      ``--strict-bind-promotion``), not **bind_disputed**
    - Semantically similar **sibling** decision (FTS) with clean outcome
    - **Recency** window (default 365d) for both candidate and sibling
    - **Quarantine** (default 7d) after eligibility before ``promote_to_pattern``
      unless ``--skip-quarantine`` (column ``promotion_quarantine_started_at``)

LABEL BACKFILL
--------------
    For ``outcome_label IS NULL`` on bound rows, infer from git subject.

USAGE
-----
    python .claude/governance/scripts/promote_author_gate_patterns.py
    python .claude/governance/scripts/promote_author_gate_patterns.py --dry-run
    python .claude/governance/scripts/promote_author_gate_patterns.py --skip-quarantine

CONSTITUTIONAL
    - No shell, no subprocess (except git via helper)
    - Specific exceptions: sqlite3.Error, OSError
    - UTF-8 stdio
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from tools.refactor_decisions.ledger_paths import REFACTOR_DECISION_LEDGER_DB  # noqa: E402

DB_PATH = REFACTOR_DECISION_LEDGER_DB

_FTS_SAFE_RE = re.compile(r"[^a-zA-Z0-9_ ]")


def _sanitize_fts(text: str) -> str:
    safe = _FTS_SAFE_RE.sub(" ", text)
    safe = " ".join(safe.split())
    return safe[:200]


def _classify_outcome(subject: str) -> str:
    lower = (subject or "").lower()
    if any(tok in lower for tok in ("revert ", "rollback", "hotfix revert")):
        return "rollback"
    if any(tok in lower for tok in ("regression", "bug:", "fix regression")):
        return "rework"
    if any(tok in lower for tok in ("fix ", "bugfix")):
        return "rework"
    return "success"


def _git_subject(sha: str) -> str:
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
            timeout=10,
            check=False,
        )
    except (subprocess.TimeoutExpired, OSError):
        return ""
    return r.stdout.strip() if r.returncode == 0 else ""


@dataclass
class Report:
    labels_backfilled: int = 0
    patterns_promoted: int = 0
    candidates_considered: int = 0
    skipped_no_sibling: int = 0
    quarantine_started: int = 0
    awaiting_quarantine: int = 0
    skipped_recency: int = 0


def _open_db() -> sqlite3.Connection | None:
    if not DB_PATH.exists():
        return None
    try:
        conn = sqlite3.connect(str(DB_PATH), timeout=10)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error:
        return None


def _outcome_columns(conn: sqlite3.Connection) -> set[str]:
    try:
        return {r[1] for r in conn.execute("PRAGMA table_info(decision_outcomes)").fetchall()}
    except sqlite3.Error:
        return set()


def _within_recency(created_at: str | None, max_days: int) -> bool:
    if max_days <= 0 or not created_at:
        return True
    try:
        dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    except ValueError:
        return True
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) - dt <= timedelta(days=max_days)


def _quarantine_elapsed(started_at: str | None, days: int) -> bool:
    if not started_at or days <= 0:
        return True
    try:
        dt = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
    except ValueError:
        return True
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) - dt >= timedelta(days=days)


def backfill_labels(conn: sqlite3.Connection, dry_run: bool) -> int:
    rows = conn.execute(
        """
        SELECT o.outcome_id, o.decision_id, o.commit_shas_json, d.commit_sha
          FROM decision_outcomes o
          JOIN decisions d ON d.decision_id = o.decision_id
         WHERE o.outcome_label IS NULL
           AND o.execution_completed = 1
        """
    ).fetchall()
    updated = 0
    for row in rows:
        shas: list[str] = []
        raw = row["commit_shas_json"]
        if raw:
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    shas = [s for s in parsed if isinstance(s, str)]
            except json.JSONDecodeError:
                pass
        if not shas and row["commit_sha"]:
            shas = [row["commit_sha"]]
        if not shas:
            continue
        subject = _git_subject(shas[0])
        label = _classify_outcome(subject)
        if dry_run:
            print(f"[dry-run] would label outcome_id={row['outcome_id']} decision={row['decision_id']} -> {label!r}")
            updated += 1
            continue
        conn.execute(
            "UPDATE decision_outcomes SET outcome_label = ? WHERE outcome_id = ?",
            (label, row["outcome_id"]),
        )
        updated += 1
    if not dry_run:
        conn.commit()
    return updated


def promote_patterns(
    conn: sqlite3.Connection,
    dry_run: bool,
    *,
    strict_bind_promotion: bool = False,
    quarantine_days: int = 7,
    skip_quarantine: bool = False,
    recency_days: int = 365,
) -> Report:
    rep = Report()
    o_cols = _outcome_columns(conn)
    bind_clause = "o.bind_confidence = 'high'"
    if not strict_bind_promotion:
        bind_clause = "(o.bind_confidence = 'high' OR o.bind_confidence IS NULL)"
    quarantine_col = "promotion_quarantine_started_at" in o_cols
    q_sel = (
        "o.promotion_quarantine_started_at"
        if quarantine_col
        else "NULL AS promotion_quarantine_started_at"
    )

    recency_sql = ""
    if recency_days > 0:
        recency_sql = f"AND datetime(d.created_at) >= datetime('now', '-{int(recency_days)} days')"

    candidates = conn.execute(
        f"""
        SELECT d.decision_id, d.decision_type, d.normalized_intent, d.created_at,
               o.outcome_id, o.outcome_label, o.regression_found, o.rollback_required,
               {q_sel}
          FROM decisions d
          JOIN decision_outcomes o ON o.decision_id = d.decision_id
         WHERE o.execution_completed = 1
           AND COALESCE(o.regression_found, 0) = 0
           AND COALESCE(o.rollback_required, 0) = 0
           AND COALESCE(o.promote_to_pattern, 0) = 0
           AND COALESCE(o.bind_disputed, 0) = 0
           AND COALESCE(o.outcome_label, 'success') NOT IN ('rollback', 'rework')
           AND ({bind_clause})
           {recency_sql}
        """
    ).fetchall()
    rep.candidates_considered = len(candidates)

    sibling_recency_sql = ""
    if recency_days > 0:
        sibling_recency_sql = (
            f"AND datetime(d2.created_at) >= datetime('now', '-{int(recency_days)} days')"
        )

    iso_now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    for cand in candidates:
        if not _within_recency(cand["created_at"], recency_days):
            rep.skipped_recency += 1
            continue
        intent = cand["normalized_intent"] or ""
        safe = _sanitize_fts(intent)
        if not safe:
            rep.skipped_no_sibling += 1
            continue
        try:
            sibling = conn.execute(
                f"""
                SELECT d2.decision_id, d2.created_at
                  FROM decisions_fts fts
                  JOIN decisions d2 ON d2.decision_id = fts.decision_id
                  LEFT JOIN decision_outcomes o2 ON o2.decision_id = d2.decision_id
                 WHERE fts MATCH ?
                   AND d2.decision_id != ?
                   AND d2.decision_type = ?
                   AND COALESCE(o2.regression_found, 0) = 0
                   AND COALESCE(o2.rollback_required, 0) = 0
                   {sibling_recency_sql}
                 ORDER BY fts.rank
                 LIMIT 1
                """,
                (safe, cand["decision_id"], cand["decision_type"]),
            ).fetchone()
        except sqlite3.Error:
            sibling = None
        if sibling is None:
            rep.skipped_no_sibling += 1
            continue
        if not _within_recency(sibling["created_at"], recency_days):
            rep.skipped_recency += 1
            continue

        use_quarantine = quarantine_col and not skip_quarantine and quarantine_days > 0
        q_start = cand["promotion_quarantine_started_at"] if quarantine_col else None

        if use_quarantine:
            if not q_start:
                rep.quarantine_started += 1
                if dry_run:
                    print(
                        f"[dry-run] would start quarantine decision={cand['decision_id']} "
                        f"sibling={sibling['decision_id']}"
                    )
                else:
                    conn.execute(
                        "UPDATE decision_outcomes SET promotion_quarantine_started_at = ? "
                        "WHERE outcome_id = ?",
                        (iso_now, cand["outcome_id"]),
                    )
                continue
            if not _quarantine_elapsed(q_start, quarantine_days):
                rep.awaiting_quarantine += 1
                continue

        if dry_run:
            print(
                f"[dry-run] would promote decision={cand['decision_id']} type={cand['decision_type']} "
                f"sibling={sibling['decision_id']}"
            )
        else:
            conn.execute(
                """UPDATE decision_outcomes
                      SET promote_to_pattern = 1, pattern_promotion_eligible = 1
                    WHERE outcome_id = ?""",
                (cand["outcome_id"],),
            )
        rep.patterns_promoted += 1

    if not dry_run:
        conn.commit()
    return rep


def main() -> int:
    parser = argparse.ArgumentParser(description="Author-Gate pattern promotion + label backfill.")
    parser.add_argument("--dry-run", action="store_true", help="Report without writing")
    parser.add_argument("--backfill-only", action="store_true", help="Skip promotion step")
    parser.add_argument("--promote-only", action="store_true", help="Skip label backfill")
    parser.add_argument(
        "--strict-bind-promotion",
        action="store_true",
        help="Require bind_confidence=high (exclude legacy NULL_BIND rows)",
    )
    parser.add_argument(
        "--quarantine-days",
        type=int,
        default=7,
        help="W3: days a candidate waits before promote_to_pattern (0=immediate if skip not set)",
    )
    parser.add_argument(
        "--skip-quarantine",
        action="store_true",
        help="W3: bypass quarantine (set promote_to_pattern on first eligible pass)",
    )
    parser.add_argument(
        "--recency-days",
        type=int,
        default=365,
        help="W3: max age (days) for candidate and sibling decisions (0=unlimited)",
    )
    args = parser.parse_args()

    conn = _open_db()
    if conn is None:
        print(f"[promote_author_gate_patterns] ledger absent: {DB_PATH}", file=sys.stderr)
        return 0

    try:
        backfilled = 0
        if not args.promote_only:
            backfilled = backfill_labels(conn, dry_run=args.dry_run)
        rep = Report()
        if not args.backfill_only:
            rep = promote_patterns(
                conn,
                dry_run=args.dry_run,
                strict_bind_promotion=args.strict_bind_promotion,
                quarantine_days=max(0, args.quarantine_days),
                skip_quarantine=bool(args.skip_quarantine),
                recency_days=max(0, args.recency_days),
            )

        verb = "would-" if args.dry_run else ""
        print(
            f"[promote_author_gate_patterns] {verb}backfilled={backfilled} "
            f"{verb}promoted={rep.patterns_promoted} "
            f"candidates={rep.candidates_considered} "
            f"skipped_no_sibling={rep.skipped_no_sibling} "
            f"quarantine_started={rep.quarantine_started} "
            f"awaiting_quarantine={rep.awaiting_quarantine} "
            f"skipped_recency={rep.skipped_recency}"
        )
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
