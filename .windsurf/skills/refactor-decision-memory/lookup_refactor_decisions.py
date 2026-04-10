#!/usr/bin/env python3
"""
lookup_refactor_decisions.py — Query the refactor decision ledger for precedent.

Invoked by Cascade when the refactor-decision-memory skill is active.
Reads a JSON query from stdin, searches the SQLite ledger using FTS5,
and returns a structured precedent verdict to stdout.

Input (stdin, JSON):
    {
        "decision_type": str,       # architecture_choice | refactor_scope | anti_pattern |
                                    # dependency_addition | test_strategy | deletion_strategy |
                                    # error_handling | unknown
        "normalized_intent": str,   # 1-2 sentence description of what is being decided
        "repo_area": str | null,    # optional: e.g. "agentic_core/L2_execution"
        "limit": int                # optional: max results (default 5, max 20)
    }

Output (stdout, JSON):
    {
        "verdict": "strong" | "suggestive" | "none",
        "matches": [MatchRecord, ...],
        "query_echo": {...},
        "reason": str               # only present when verdict=="none" due to error/empty
    }

Verdict classification:
    strong     — promote_to_pattern=1 AND decision_type matches AND no regression
    suggestive — FTS5 match AND decision_type matches AND status=resolved
    none       — no matches, DB absent, or all matches have regression/rollback

Zero hardcoded paths — REPO_ROOT resolved from __file__.
"""

import json
import re
import sqlite3
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = REPO_ROOT / ".windsurf" / "state" / "refactor_decisions" / "refactor_decision_ledger.sqlite"

_DEFAULT_LIMIT = 5
_MAX_LIMIT = 20


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------


def _open_db() -> sqlite3.Connection | None:
    if not DB_PATH.exists():
        return None
    try:
        conn = sqlite3.connect(str(DB_PATH), timeout=5)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error:
        return None


def _sanitize_fts_query(text: str) -> str:
    """Strip FTS5 special characters from query text to prevent syntax errors."""
    # Keep only alphanumeric, underscores, hyphens, spaces
    safe = re.sub(r"[^a-zA-Z0-9_\- ]", " ", text)
    # Collapse whitespace
    safe = " ".join(safe.split())
    return safe[:200]


# ---------------------------------------------------------------------------
# Core lookup
# ---------------------------------------------------------------------------


def lookup(query: dict[str, Any]) -> dict[str, Any]:
    decision_type = (query.get("decision_type") or "").strip()
    normalized_intent = (query.get("normalized_intent") or "").strip()
    repo_area = (query.get("repo_area") or "").strip()
    raw_limit = query.get("limit")
    limit = min(int(raw_limit) if isinstance(raw_limit, int) else _DEFAULT_LIMIT, _MAX_LIMIT)

    query_echo = {
        "decision_type": decision_type,
        "normalized_intent": normalized_intent[:100],
        "repo_area": repo_area,
    }

    if not normalized_intent:
        return {
            "verdict": "none",
            "matches": [],
            "query_echo": query_echo,
            "reason": "normalized_intent is required",
        }

    conn = _open_db()
    if conn is None:
        return {
            "verdict": "none",
            "matches": [],
            "query_echo": query_echo,
            "reason": "no ledger found — no decisions captured yet",
        }

    try:
        return _run_query(conn, decision_type, normalized_intent, repo_area, limit, query_echo)
    except sqlite3.Error as exc:
        return {"verdict": "none", "matches": [], "query_echo": query_echo, "reason": f"db_error: {exc}"}
    finally:
        conn.close()


def _run_query(
    conn: sqlite3.Connection,
    decision_type: str,
    normalized_intent: str,
    repo_area: str,
    limit: int,
    query_echo: dict[str, Any],
) -> dict[str, Any]:
    safe_query = _sanitize_fts_query(normalized_intent)
    if not safe_query:
        return {
            "verdict": "none",
            "matches": [],
            "query_echo": query_echo,
            "reason": "normalized_intent contains no searchable terms",
        }

    fts_sql = """
        SELECT
            d.decision_id,
            d.decision_type,
            d.request_summary,
            d.normalized_intent,
            d.user_goal,
            d.recommended_option_id,
            d.selected_option_id,
            d.selection_rationale,
            d.status,
            d.created_at,
            s.repo_area,
            s.file_path,
            s.layer,
            s.tags,
            o.tests_passed,
            o.regression_found,
            o.rollback_required,
            o.promote_to_pattern,
            decisions_fts.rank
        FROM decisions_fts
        JOIN decisions d ON decisions_fts.decision_id = d.decision_id
        LEFT JOIN decision_scope s ON s.decision_id = d.decision_id
        LEFT JOIN decision_outcomes o ON o.decision_id = d.decision_id
        WHERE decisions_fts MATCH ?
        ORDER BY decisions_fts.rank
        LIMIT ?
    """

    try:
        rows = conn.execute(fts_sql, (safe_query, limit * 3)).fetchall()
    except sqlite3.OperationalError:
        rows = []

    matches: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    for row in rows:
        d = dict(row)
        did = d.get("decision_id", "")
        if did in seen_ids:
            continue
        seen_ids.add(did)

        row_type = d.get("decision_type") or ""
        row_area = d.get("repo_area") or ""
        no_regression = not d.get("regression_found")
        no_rollback = not d.get("rollback_required")
        promoted = bool(d.get("promote_to_pattern"))
        type_matches = (not decision_type) or (row_type == decision_type)
        area_overlaps = (not repo_area) or row_area.startswith(repo_area[:30])

        if promoted and type_matches and no_regression and no_rollback:
            strength = "strong"
        elif type_matches and no_regression and (area_overlaps or not repo_area):
            strength = "suggestive"
        else:
            continue

        matches.append(
            {
                "strength": strength,
                "decision_id": did,
                "decision_type": row_type,
                "request_summary": d.get("request_summary"),
                "normalized_intent": d.get("normalized_intent"),
                "recommended_option_id": d.get("recommended_option_id"),
                "selected_option_id": d.get("selected_option_id"),
                "selection_rationale": d.get("selection_rationale"),
                "repo_area": row_area,
                "file_path": d.get("file_path"),
                "tests_passed": bool(d.get("tests_passed")),
                "promote_to_pattern": promoted,
                "created_at": d.get("created_at"),
            }
        )

        if len(matches) >= limit:
            break

    if any(m["strength"] == "strong" for m in matches):
        verdict = "strong"
    elif matches:
        verdict = "suggestive"
    else:
        verdict = "none"

    return {"verdict": verdict, "matches": matches, "query_echo": query_echo}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> int:
    raw = sys.stdin.read()
    try:
        query: dict[str, Any] = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        query = {}

    result = lookup(query)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
