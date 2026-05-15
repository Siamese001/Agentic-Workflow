#!/usr/bin/env python3
"""
promote_author_gate_patterns.py — Weekly pattern promotion for Author-Gate meta-learning.

Flips ``decision_outcomes.promote_to_pattern = 1`` on decisions that qualify as
reusable patterns, and backfills ``decision_outcomes.outcome_label`` on rows that
were bound before the label column existed.

PROMOTION CRITERIA
------------------
A decision is promoted when ALL hold:

    - Its outcome is bound (``execution_completed = 1``)
    - No regression (``regression_found = 0`` AND ``rollback_required = 0``)
    - ``outcome_label`` is not ``"rollback"`` and not ``"rework"``
    - At least one OTHER decision exists with the same ``decision_type`` AND an
      FTS match on ``normalized_intent`` (≥1 shared token, rank > threshold)
    - The sibling's outcome is also clean (or unbound but recent)

Intuition: two independent successful decisions on semantically similar intents
within the same decision_type constitute a reusable precedent, so the injector
can upgrade the verdict to "strong".

LABEL BACKFILL
--------------
For decisions with ``execution_completed = 1`` but ``outcome_label IS NULL``,
re-run ``classify_outcome`` against the bound commit subject and write the
inferred label (``success`` / ``rework`` / ``rollback`` / ``undecided``).

USAGE
-----
    python .cursor/scripts/promote_author_gate_patterns.py            # promote + backfill
    python .cursor/scripts/promote_author_gate_patterns.py --dry-run  # report only
    python .cursor/scripts/promote_author_gate_patterns.py --backfill-only
    python .cursor/scripts/promote_author_gate_patterns.py --promote-only

CONSTITUTIONAL
    - No shell, no subprocess (except git via helper)
    - Specific exceptions: sqlite3.Error, OSError
    - UTF-8 stdio
    - Idempotent — safe to run repeatedly
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = REPO_ROOT / ".cursor" / "state" / "refactor_decisions" / "refactor_decision_ledger.sqlite"

# Hyphens are intentionally excluded from the keep-set: FTS5 parses ``foo-bar``
# as the column filter ``foo NOT bar`` which raises OperationalError unless
# ``foo`` names an indexed column. Tokenizing hyphens as whitespace makes
# hyphenated intents (meta-learning, anti-pattern, multi-file) match as
# bag-of-words tokens. Mirrors the fix in
# .cursor/skills/refactor-decision-memory/lookup_refactor_decisions.py.
_FTS_SAFE_RE = re.compile(r"[^a-zA-Z0-9_ ]")


def _sanitize_fts(text: str) -> str:
    safe = _FTS_SAFE_RE.sub(" ", text)
    safe = " ".join(safe.split())
    return safe[:200]


def _classify_outcome(subject: str) -> str:
    """Mirror of post_commit_outcome_binder.classify_outcome, label-only."""
    lower = (subject or "").lower()
    if any(tok in lower for tok in ("revert ", "rollback", "hotfix revert")):
        return "rollback"
    if any(tok in lower for tok in ("regression", "bug:", "fix regression")):
        return "rework"
    if any(tok in lower for tok in ("fix ", "bugfix")):
        return "rework"
    # Default: no evidence of regression → treat as success (was "undecided" pre-W4).
    # Reasoning: outcome_binder sets execution_completed=1 only on clean commits, so
    # the default for bound-without-regression-signal rows is success, not undecided.
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


def _open_db() -> sqlite3.Connection | None:
    if not DB_PATH.exists():
        return None
    try:
        conn = sqlite3.connect(str(DB_PATH), timeout=10)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error:
        return None


def backfill_labels(conn: sqlite3.Connection, dry_run: bool) -> int:
    """Populate decision_outcomes.outcome_label where it is NULL."""
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


def promote_patterns(conn: sqlite3.Connection, dry_run: bool) -> Report:
    """Flip promote_to_pattern=1 for decisions meeting the pattern criteria."""
    rep = Report()
    # Candidate set: clean, executed, not already promoted
    candidates = conn.execute(
        """
        SELECT d.decision_id, d.decision_type, d.normalized_intent,
               o.outcome_id, o.outcome_label, o.regression_found, o.rollback_required
          FROM decisions d
          JOIN decision_outcomes o ON o.decision_id = d.decision_id
         WHERE o.execution_completed = 1
           AND COALESCE(o.regression_found, 0) = 0
           AND COALESCE(o.rollback_required, 0) = 0
           AND COALESCE(o.promote_to_pattern, 0) = 0
           AND COALESCE(o.outcome_label, 'success') NOT IN ('rollback', 'rework')
        """
    ).fetchall()
    rep.candidates_considered = len(candidates)

    for cand in candidates:
        intent = cand["normalized_intent"] or ""
        safe = _sanitize_fts(intent)
        if not safe:
            rep.skipped_no_sibling += 1
            continue
        sibling = conn.execute(
            """
            SELECT d2.decision_id
              FROM decisions_fts fts
              JOIN decisions d2 ON d2.decision_id = fts.decision_id
              LEFT JOIN decision_outcomes o2 ON o2.decision_id = d2.decision_id
             WHERE decisions_fts MATCH ?
               AND d2.decision_id != ?
               AND d2.decision_type = ?
               AND COALESCE(o2.regression_found, 0) = 0
               AND COALESCE(o2.rollback_required, 0) = 0
             LIMIT 1
            """,
            (safe, cand["decision_id"], cand["decision_type"]),
        ).fetchone()
        if sibling is None:
            rep.skipped_no_sibling += 1
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
    parser.add_argument("--verbose", "-v", action="store_true")
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
            rep = promote_patterns(conn, dry_run=args.dry_run)

        verb = "would-" if args.dry_run else ""
        print(
            f"[promote_author_gate_patterns] {verb}backfilled={backfilled} "
            f"{verb}promoted={rep.patterns_promoted} "
            f"candidates={rep.candidates_considered} "
            f"skipped_no_sibling={rep.skipped_no_sibling}"
        )
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
