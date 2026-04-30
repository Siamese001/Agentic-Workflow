"""Cross-interview ProceduralPattern distillation — Wave 5 phase 5.3.

Reads ledger episodic events (interview_outcome rows) and distills
durable cross-interview patterns into Memory MCP-compatible payloads.

Architecture
------------
The flywheel (W5.2) operates on raw outcome aggregations. This module
goes one layer up: it identifies *patterns* — reusable lessons that
generalize beyond a single interview. Examples:

  - "Hiring-manager personas always probe X" -> ProceduralPattern
  - "Architecture-route success correlates with non-empty
    architecture_content_blocks" -> ProceduralPattern
  - "Cards over the paste-budget cap suppress route X coverage"
    -> ProceduralPattern

Output is a list of ``MemoryEntityDraft`` objects shaped for
``mcp6_create_entities``. The actual Memory MCP write is the OPERATOR's
responsibility (per MCP serialization §25, the helper cannot make the
MCP call as a side-effect of a build run; it produces the payload, and
the operator runs ``apps_qna memory-writeback`` separately).

This keeps apps_qna's spine integration honest:
  - ledger is the durable record (W1.4)
  - episodic capture closes the loop (W5.1)
  - flywheel produces machine-actionable defaults (W5.2)
  - this module produces human-readable cross-session patterns (W5.3)
"""

from __future__ import annotations

import json
import logging
import sqlite3
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_log = logging.getLogger(__name__)

_LEDGER_NAME: str = "apps_qna_pack_lifecycle"
_DEFAULT_MIN_NAMESPACES_FOR_PATTERN: int = 3
_DEFAULT_MIN_OBSERVATIONS_PER_PATTERN: int = 15


@dataclass
class MemoryEntityDraft:
    """Memory MCP create_entities payload draft."""

    name: str
    entityType: str
    """Use ProceduralPattern for cross-interview patterns; ProjectContext for
    project state. Avoid 'general' — protected types survive cleanup."""

    observations: list[str] = field(default_factory=list)


def _ledger_db_path() -> Path | None:
    try:
        from tools.ledgers.schema_registry import get

        return get(_LEDGER_NAME).db_path
    except (ImportError, KeyError):
        return None


def _walk_outcome_rows(db_path: Path) -> list[dict[str, Any]]:
    """Return [{namespace, asked_route, card_id, asked, landed, success}] rows."""
    rows: list[dict[str, Any]] = []
    if not db_path.is_file():
        return rows
    try:
        con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        try:
            for prediction_json, outcome_json in con.execute(
                "SELECT prediction_json, outcome_json FROM events "
                "WHERE event_kind = 'interview_outcome' AND outcome_json IS NOT NULL"
            ):
                if not prediction_json or not outcome_json:
                    continue
                try:
                    pred = json.loads(prediction_json)
                    out = json.loads(outcome_json)
                except json.JSONDecodeError:
                    continue
                rows.append(
                    {
                        "namespace": pred.get("namespace") or "",
                        "interviewer": pred.get("interviewer") or "",
                        "asked_route": pred.get("asked_route") or "",
                        "card_id": pred.get("card_id") or "",
                        "asked": bool(out.get("asked", False)),
                        "landed": bool(out.get("landed", False)),
                        "success": bool(out.get("success", False)),
                    }
                )
        finally:
            con.close()
    except sqlite3.Error as exc:
        _log.debug("memory_writeback walk error: %r", exc)
    return rows


def _route_dominance_pattern(
    rows: list[dict[str, Any]],
    *,
    min_namespaces: int,
    min_observations: int,
) -> MemoryEntityDraft | None:
    """Detect routes that consistently dominate across many namespaces."""
    by_route: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"n": 0, "asked": 0, "landed": 0, "namespaces": set()}
    )
    for row in rows:
        if not row["asked_route"]:
            continue
        b = by_route[row["asked_route"]]
        b["n"] += 1
        if row["asked"]:
            b["asked"] += 1
        if row["landed"]:
            b["landed"] += 1
        b["namespaces"].add(row["namespace"])

    dominant_routes = []
    for route, stats in by_route.items():
        if stats["n"] < min_observations:
            continue
        if len(stats["namespaces"]) < min_namespaces:
            continue
        ask_rate = stats["asked"] / stats["n"] if stats["n"] else 0.0
        landed_rate = stats["landed"] / stats["n"] if stats["n"] else 0.0
        if ask_rate >= 0.55 or landed_rate >= 0.55:
            dominant_routes.append(
                (route, stats["n"], len(stats["namespaces"]), ask_rate, landed_rate)
            )
    if not dominant_routes:
        return None
    dominant_routes.sort(key=lambda r: (r[3] + r[4]) / 2, reverse=True)

    observations = [
        "Cross-interview pattern: certain likely_questions routes dominate "
        "across multiple interviewer namespaces, suggesting they are "
        "structural defaults rather than per-interviewer choices.",
    ]
    for route, n, ns_count, ask_rate, landed_rate in dominant_routes[:5]:
        observations.append(
            f"Route '{route}': observed in {n} interviews across {ns_count} "
            f"namespaces; ask_rate={ask_rate:.1%}, landed_rate={landed_rate:.1%}. "
            f"Treat as a default-ON candidate when the bandit is in cold-start."
        )

    return MemoryEntityDraft(
        name="ProceduralPattern:AppsQnaRouteDominance",
        entityType="ProceduralPattern",
        observations=observations,
    )


def _interviewer_persona_pattern(
    rows: list[dict[str, Any]],
) -> MemoryEntityDraft | None:
    """Detect interviewer-name -> dominant-route correlations (persona patterns)."""
    by_interviewer: dict[str, dict[str, dict[str, int]]] = defaultdict(
        lambda: defaultdict(lambda: {"asked": 0, "landed": 0, "n": 0})
    )
    for row in rows:
        name = row["interviewer"]
        route = row["asked_route"]
        if not name or not route:
            continue
        cell = by_interviewer[name][route]
        cell["n"] += 1
        if row["asked"]:
            cell["asked"] += 1
        if row["landed"]:
            cell["landed"] += 1

    persona_lines: list[str] = []
    for name, route_stats in by_interviewer.items():
        if not route_stats:
            continue
        # Top route by ask_rate.
        top = max(
            route_stats.items(),
            key=lambda kv: kv[1]["asked"] / max(1, kv[1]["n"]),
        )
        route, stats = top
        n = stats["n"]
        if n < 5:
            continue
        ask_rate = stats["asked"] / n if n else 0.0
        if ask_rate >= 0.50:
            persona_lines.append(
                f"Interviewer '{name}': dominant ask_route='{route}' "
                f"(ask_rate={ask_rate:.1%}, n={n}). Suggests persona-level "
                "preference; bias subsequent packs for this interviewer toward "
                "this route."
            )
    if not persona_lines:
        return None

    observations = [
        "Cross-interview pattern: specific interviewer names correlate with "
        "specific route preferences. Use these as priors when seeding "
        "likely_questions for the same interviewer in a new role context.",
    ]
    observations.extend(persona_lines[:8])
    return MemoryEntityDraft(
        name="ProceduralPattern:AppsQnaInterviewerPersonas",
        entityType="ProceduralPattern",
        observations=observations,
    )


def distill_patterns(
    *,
    db_path: Path | None = None,
    min_namespaces: int = _DEFAULT_MIN_NAMESPACES_FOR_PATTERN,
    min_observations: int = _DEFAULT_MIN_OBSERVATIONS_PER_PATTERN,
) -> list[MemoryEntityDraft]:
    """Read the ledger and produce ProceduralPattern entity drafts.

    Returns an empty list when the ledger has insufficient data. The
    operator runs ``apps_qna memory-writeback`` to persist these drafts
    via the Memory MCP (per §25 the actual MCP write happens in an
    isolated response).
    """
    path = db_path or _ledger_db_path()
    if path is None:
        return []
    rows = _walk_outcome_rows(path)
    if not rows:
        return []

    drafts: list[MemoryEntityDraft] = []

    route_pattern = _route_dominance_pattern(
        rows,
        min_namespaces=min_namespaces,
        min_observations=min_observations,
    )
    if route_pattern is not None:
        drafts.append(route_pattern)

    persona_pattern = _interviewer_persona_pattern(rows)
    if persona_pattern is not None:
        drafts.append(persona_pattern)

    _log.info(
        "memory_writeback distillation: %d outcome rows -> %d patterns",
        len(rows),
        len(drafts),
    )
    return drafts


def format_drafts_for_mcp_call(
    drafts: list[MemoryEntityDraft],
) -> list[dict[str, Any]]:
    """Format drafts into the JSON shape mcp6_create_entities expects."""
    return [
        {
            "name": d.name,
            "entityType": d.entityType,
            "observations": list(d.observations),
        }
        for d in drafts
    ]


__all__ = [
    "MemoryEntityDraft",
    "distill_patterns",
    "format_drafts_for_mcp_call",
]
