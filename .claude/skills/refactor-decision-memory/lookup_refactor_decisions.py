#!/usr/bin/env python3
"""
lookup_refactor_decisions.py — Query the refactor decision ledger for precedent.

Invoked by Claude Code when the refactor-decision-memory skill is active.
Reads a JSON query from stdin, searches the SQLite ledger using FTS5,
and returns a structured precedent verdict to stdout.

Input (stdin, JSON):
    {
        "decision_type": str,
        "normalized_intent": str,
        "repo_area": str | null,
        "layer": str | null,          -- W3 optional scope guard
        "degraded_scope": bool,       -- W3 ADG/stale path; never yields strong
        "scope_degraded": bool,       -- alias for degraded_scope
        "exclude_decision_id": str | null,  -- W3 self-match exclusion
        "self_decision_id": str | null,      -- alias for exclude_decision_id
        "exclude_decision_ids": [str],       -- optional additional excludes
        "limit": int
    }

Output (stdout, JSON):
    {
        "verdict": "strong" | "suggestive" | "none",
        "matches": [...],
        "query_echo": {...},
        "reason": str,
        "reason_codes": [str],         -- W3 deterministic taxonomy
        "lookup_policy_version": str
    }

Verdict classification (W3, plan author-gate-learning-harden-f4e8a2):
    strong     — promote_to_pattern, high bind_confidence, not disputed, strict
                 repo_area, layer match, hash_ok is not False, not degraded_scope
    suggestive — FTS + type + looser repo_area + layer + no regression/rollback;
                 legacy promoted rows without high bind drop to suggestive
    none       — no qualifying rows
"""

from __future__ import annotations

import json
import re
import sqlite3
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from tools.refactor_decisions.ledger_paths import REFACTOR_DECISION_LEDGER_DB  # noqa: E402
from tools.refactor_decisions.author_gate_lookup_w3 import (  # noqa: E402
    LOOKUP_W3_POLICY_VERSION,
    human_reason_line,
    normalize_dedup_key,
    sort_reason_codes,
    validate_reason_codes,
)
from tools.refactor_decisions.precedent_scope import (  # noqa: E402
    layer_matches,
    repo_areas_compatible_strong,
    repo_areas_compatible_suggestive,
)

DB_PATH = REFACTOR_DECISION_LEDGER_DB

_DEFAULT_LIMIT = 5
_MAX_LIMIT = 20

_SCRIPTS_DIR = REPO_ROOT / ".claude" / "governance/scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
try:
    from author_gate_ledger_integrity import (  # type: ignore[import-not-found]
        GENESIS_PREV_HASH,
        compute_row_hash,
    )
    _HASH_VERIFY_AVAILABLE = True
except ImportError:
    GENESIS_PREV_HASH = "0" * 64  # type: ignore[assignment]
    compute_row_hash = None  # type: ignore[assignment]
    _HASH_VERIFY_AVAILABLE = False


def _open_db() -> sqlite3.Connection | None:
    if not DB_PATH.exists():
        return None
    try:
        conn = sqlite3.connect(str(DB_PATH), timeout=5)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error:
        return None


def _verify_row_hash(
    conn: sqlite3.Connection,
    decision_id: str,
    stored_prev: str | None,
    stored_hash: str | None,
) -> bool | None:
    if compute_row_hash is None or not stored_hash:
        return None
    try:
        cur = conn.execute("SELECT * FROM decisions WHERE decision_id = ?", (decision_id,))
        row = cur.fetchone()
    except sqlite3.Error:
        return None
    if row is None:
        return None
    prev = stored_prev if stored_prev else GENESIS_PREV_HASH
    try:
        expected = compute_row_hash(dict(row), prev)
    except (ValueError, TypeError):
        return None
    return expected == stored_hash


def _outcome_tier_from_row(d: dict[str, Any]) -> str:
    """Map ledger outcome row to W1 bind tier (legacy bind_confidence fallback)."""
    raw = (d.get("outcome_bind_tier") or "").strip().lower()
    if raw in ("strong_bind", "weak_bind", "disputed_bind", "no_bind", "unknown_bind"):
        return raw
    if bool(d.get("bind_disputed")):
        return "disputed_bind"
    bc = (str(d.get("bind_confidence") or "")).strip().lower()
    if bc == "high":
        return "strong_bind"
    if bc in ("medium", "low"):
        return "weak_bind"
    return "unknown_bind"


def _sanitize_fts_query(text: str) -> str:
    safe = re.sub(r"[^a-zA-Z0-9_ ]", " ", text)
    safe = " ".join(safe.split())
    return safe[:200]


def lookup(query: dict[str, Any]) -> dict[str, Any]:
    decision_type = (query.get("decision_type") or "").strip()
    normalized_intent = (query.get("normalized_intent") or "").strip()
    repo_area = (query.get("repo_area") or "").strip()
    raw_limit = query.get("limit")
    limit = min(int(raw_limit) if isinstance(raw_limit, int) else _DEFAULT_LIMIT, _MAX_LIMIT)
    degraded_scope = bool(query.get("degraded_scope") or query.get("scope_degraded"))
    query_layer = (query.get("layer") or "").strip()

    exclude_one = str(query.get("exclude_decision_id") or query.get("self_decision_id") or "").strip()
    raw_extras = query.get("exclude_decision_ids") or []
    exclude_extra: list[str] = []
    if isinstance(raw_extras, list):
        exclude_extra = [str(x).strip() for x in raw_extras if str(x).strip()]

    query_echo = {
        "decision_type": decision_type,
        "normalized_intent": normalized_intent[:100],
        "repo_area": repo_area,
        "layer": query_layer,
        "degraded_scope": degraded_scope,
        "exclude_decision_id": exclude_one,
        "exclude_decision_ids": exclude_extra,
    }

    if not normalized_intent:
        return {
            "verdict": "none",
            "matches": [],
            "query_echo": query_echo,
            "reason": "normalized_intent is required",
            "reason_codes": [],
            "lookup_policy_version": LOOKUP_W3_POLICY_VERSION,
        }

    conn = _open_db()
    if conn is None:
        return {
            "verdict": "none",
            "matches": [],
            "query_echo": query_echo,
            "reason": "no ledger found — no decisions captured yet",
            "reason_codes": [],
            "lookup_policy_version": LOOKUP_W3_POLICY_VERSION,
        }

    try:
        return _run_query(conn, decision_type, normalized_intent, repo_area, limit, query_echo)
    except sqlite3.Error as exc:
        return {
            "verdict": "none",
            "matches": [],
            "query_echo": query_echo,
            "reason": f"db_error: {exc}",
            "reason_codes": [],
            "lookup_policy_version": LOOKUP_W3_POLICY_VERSION,
        }
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
    degraded_scope = bool(query_echo.get("degraded_scope"))
    query_layer = (query_echo.get("layer") or "").strip()
    exclude_set: set[str] = set()
    ex1 = (query_echo.get("exclude_decision_id") or "").strip()
    if ex1:
        exclude_set.add(ex1)
    for x in query_echo.get("exclude_decision_ids") or []:
        xs = str(x).strip()
        if xs:
            exclude_set.add(xs)

    reason_codes_accum: list[str] = []

    safe_query = _sanitize_fts_query(normalized_intent)
    if not safe_query:
        out_codes = sort_reason_codes(["BELOW_THRESHOLD"])
        validate_reason_codes(out_codes)
        return {
            "verdict": "none",
            "matches": [],
            "query_echo": query_echo,
            "reason": human_reason_line(out_codes),
            "reason_codes": out_codes,
            "lookup_policy_version": LOOKUP_W3_POLICY_VERSION,
        }

    try:
        d_cols = {r[1] for r in conn.execute("PRAGMA table_info(decisions)").fetchall()}
    except sqlite3.Error:
        d_cols = set()
    try:
        o_cols = {r[1] for r in conn.execute("PRAGMA table_info(decision_outcomes)").fetchall()}
    except sqlite3.Error:
        o_cols = set()

    hash_cols_sql = (
        "d.prev_hash, d.row_hash"
        if {"prev_hash", "row_hash"} <= d_cols
        else "NULL AS prev_hash, NULL AS row_hash"
    )
    bind_cols_sql = (
        "o.bind_confidence, o.bind_disputed"
        if "bind_confidence" in o_cols and "bind_disputed" in o_cols
        else "NULL AS bind_confidence, 0 AS bind_disputed"
    )
    tier_sql = (
        "o.outcome_bind_tier" if "outcome_bind_tier" in o_cols else "NULL AS outcome_bind_tier"
    )

    fts_sql = f"""
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
            {hash_cols_sql},
            s.repo_area,
            s.file_path,
            s.layer,
            s.tags,
            o.tests_passed,
            o.regression_found,
            o.rollback_required,
            o.promote_to_pattern,
            {bind_cols_sql},
            {tier_sql},
            decisions_fts.rank
        FROM decisions_fts
        JOIN decisions d ON decisions_fts.decision_id = d.decision_id
        LEFT JOIN decision_scope s ON s.decision_id = d.decision_id
        LEFT JOIN decision_outcomes o ON o.decision_id = d.decision_id
        WHERE decisions_fts MATCH ?
        ORDER BY decisions_fts.rank ASC, d.created_at DESC
        LIMIT ?
    """

    try:
        fts_cap = max(limit * 12, 48)
        raw_rows = conn.execute(fts_sql, (safe_query, fts_cap)).fetchall()
    except sqlite3.OperationalError:
        raw_rows = []

    if not raw_rows:
        reason_codes_accum.append("COLD_CORPUS")
        out_codes = sort_reason_codes(reason_codes_accum)
        validate_reason_codes(out_codes)
        return {
            "verdict": "none",
            "matches": [],
            "query_echo": query_echo,
            "reason": human_reason_line(out_codes),
            "reason_codes": out_codes,
            "lookup_policy_version": LOOKUP_W3_POLICY_VERSION,
        }

    self_excluded_any = False
    layer_pass: list[dict[str, Any]] = []
    ranks_for_boost: list[Any] = []
    seen_join_ids: set[str] = set()

    for row in raw_rows:
        d = dict(row)
        did = str(d.get("decision_id") or "")
        if not did:
            continue
        if did in exclude_set:
            self_excluded_any = True
            continue
        if did in seen_join_ids:
            continue
        seen_join_ids.add(did)
        row_layer = d.get("layer")
        if not layer_matches(query_layer, row_layer):
            continue
        layer_pass.append(d)
        ranks_for_boost.append(d.get("rank"))

    if self_excluded_any:
        reason_codes_accum.append("SELF_MATCH_EXCLUDED")

    if len(ranks_for_boost) > 1:
        from collections import Counter

        rc = Counter(ranks_for_boost)
        if any(c > 1 for c in rc.values()):
            reason_codes_accum.append("RECENCY_BOOST_APPLIED")

    deduped: list[dict[str, Any]] = []
    seen_k: set[tuple[str, str, str]] = set()
    dup_collapsed = False
    for d in layer_pass:
        key = normalize_dedup_key(
            str(d.get("normalized_intent") or ""),
            str(d.get("decision_type") or ""),
            str(d.get("repo_area") or ""),
        )
        if key in seen_k:
            dup_collapsed = True
            continue
        seen_k.add(key)
        deduped.append(d)

    if dup_collapsed:
        reason_codes_accum.append("DUPLICATE_SCOPE_COLLAPSED")

    if not deduped:
        reason_codes_accum.append("BELOW_THRESHOLD")
        out_codes = sort_reason_codes(reason_codes_accum)
        validate_reason_codes(out_codes)
        return {
            "verdict": "none",
            "matches": [],
            "query_echo": query_echo,
            "reason": human_reason_line(out_codes),
            "reason_codes": out_codes,
            "lookup_policy_version": LOOKUP_W3_POLICY_VERSION,
        }

    matches: list[dict[str, Any]] = []
    policy_blocked_any = False
    degraded_blocked_any = False
    tier_boost_any = False

    for d in deduped:
        did = str(d.get("decision_id") or "")
        row_type = d.get("decision_type") or ""
        row_area = d.get("repo_area") or ""
        no_regression = not d.get("regression_found")
        no_rollback = not d.get("rollback_required")
        promoted = bool(d.get("promote_to_pattern"))
        type_matches = (not decision_type) or (row_type == decision_type)
        tier = _outcome_tier_from_row(d)
        status_l = (d.get("status") or "").lower()
        status_ok = status_l in ("resolved", "executed", "surfaced", "")

        policy_strong_body = (
            promoted
            and type_matches
            and no_regression
            and no_rollback
            and repo_areas_compatible_strong(repo_area, row_area)
            and status_ok
        )
        strong_ok_if_not_degraded = policy_strong_body and tier == "strong_bind"
        if degraded_scope and strong_ok_if_not_degraded:
            degraded_blocked_any = True

        strong_ok = strong_ok_if_not_degraded and not degraded_scope

        suggestive_ok = (
            type_matches
            and no_regression
            and no_rollback
            and repo_areas_compatible_suggestive(repo_area, row_area)
        )

        if strong_ok:
            strength = "strong"
        elif suggestive_ok:
            strength = "suggestive"
        else:
            continue

        if (
            policy_strong_body
            and not degraded_scope
            and tier != "strong_bind"
            and strength == "suggestive"
        ):
            tier_boost_any = True

        hash_ok: bool | None = None
        if _HASH_VERIFY_AVAILABLE and d.get("row_hash") and compute_row_hash is not None:
            hash_ok = _verify_row_hash(conn, did, d.get("prev_hash"), d.get("row_hash"))

        if strength == "strong" and hash_ok is False:
            strength = "suggestive"
            policy_blocked_any = True

        if tier == "strong_bind":
            reason_codes_accum.append("MATCHED_STRONG_BIND")
        elif tier == "weak_bind":
            reason_codes_accum.append("MATCHED_WEAK_BIND")
        elif tier == "disputed_bind":
            reason_codes_accum.append("MATCHED_DISPUTED_BIND")
        elif tier == "no_bind":
            reason_codes_accum.append("MATCHED_NO_BIND")
        else:
            reason_codes_accum.append("MATCHED_UNKNOWN_BIND")

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
                "bind_confidence": d.get("bind_confidence"),
                "bind_disputed": bool(d.get("bind_disputed")),
                "outcome_bind_tier": d.get("outcome_bind_tier"),
                "created_at": d.get("created_at"),
                "hash_ok": hash_ok,
            }
        )

        if len(matches) >= limit:
            break

    if policy_blocked_any:
        reason_codes_accum.append("POLICY_BLOCKED_STRONG")
    if degraded_blocked_any:
        reason_codes_accum.append("DEGRADED_SCOPE_NOT_STRONG")
    if tier_boost_any:
        reason_codes_accum.append("OUTCOME_TIER_BOOST_APPLIED")

    if any(m["strength"] == "strong" for m in matches):
        verdict = "strong"
    elif matches:
        verdict = "suggestive"
    else:
        verdict = "none"
        if not any(c == "BELOW_THRESHOLD" for c in reason_codes_accum):
            reason_codes_accum.append("BELOW_THRESHOLD")

    out_codes = sort_reason_codes(reason_codes_accum)
    validate_reason_codes(out_codes)
    return {
        "verdict": verdict,
        "matches": matches,
        "query_echo": query_echo,
        "reason": human_reason_line(out_codes),
        "reason_codes": out_codes,
        "lookup_policy_version": LOOKUP_W3_POLICY_VERSION,
    }


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
