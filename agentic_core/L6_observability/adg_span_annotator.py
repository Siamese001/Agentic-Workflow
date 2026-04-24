"""L6 span annotator — enrich OTel span attributes with ADG semantic edges.

This module answers one runtime question: *"Given that the span at
`file:line:symbol` just ran, which writes / side-effects / state changes
would the static ADG predict?"*

The annotator reads the static ADG's semantic edges (``writes_to``,
``emits_side_effect``, ``reads_from``, ``controls_flow``) for the resolved
node and attaches them as structured attributes to the span. Downstream
analysis (anomaly detection, healing chain) can compare:

    expected_writes_to     (from static ADG — what *should* have been touched)
    observed_writes        (from the live span attributes / child spans)

A divergence is a drift signal worth investigating (silent write bypass,
missed guardrail, unexpected state mutation).

Design:
- Pure read; safe for the observer hot path.
- No MCP hops (direct SQLite via RuntimeADGQuery).
- Fail-soft — if ADG is unavailable, returns the input span unchanged.
- Thread-safe via the library's per-call connection pattern.
"""

from __future__ import annotations

import logging
import sqlite3
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT_FOR_IMPORT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT_FOR_IMPORT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT_FOR_IMPORT))

try:
    from tools.adg.runtime_query import (  # noqa: E402
        RuntimeADGQuery,
        _open_readonly,
        get_default_query,
    )
except ImportError as exc:  # pragma: no cover
    logging.getLogger(__name__).warning("ADG runtime_query unavailable: %s", exc)
    RuntimeADGQuery = None  # type: ignore[assignment,misc]
    _open_readonly = None  # type: ignore[assignment]
    get_default_query = lambda: None  # type: ignore[assignment]

logger = logging.getLogger(__name__)

# Semantic edges relevant to span-vs-static comparison.
SEMANTIC_RELATIONS: tuple[str, ...] = (
    "writes_to",
    "reads_from",
    "emits_side_effect",
    "controls_flow",
    "resolves_callsite",
)

# Attribute namespace for the span annotations.
ADG_ATTR_PREFIX: str = "adg.static."

# Cap per relation to keep span payloads bounded.
MAX_ROWS_PER_RELATION: int = 10


def _static_edges_for_node(
    sqlite_path: Path, node_id: str, relations: tuple[str, ...]
) -> dict[str, list[dict[str, Any]]]:
    """Return semantic edges originating at ``node_id``, grouped by relation."""
    out: dict[str, list[dict[str, Any]]] = {rel: [] for rel in relations}
    if _open_readonly is None:
        return out
    try:
        with _open_readonly(sqlite_path) as conn:
            placeholders = ",".join("?" * len(relations))
            rows = conn.execute(
                f"SELECT e.relation_type, n.id AS tgt_id, n.adg_name, n.resolved_path, n.layer "
                f"FROM edges e JOIN nodes n ON n.id = e.tgt_id "
                f"WHERE e.src_id = ? AND e.relation_type IN ({placeholders}) "
                f"LIMIT ?",
                (node_id, *relations, MAX_ROWS_PER_RELATION * len(relations)),
            ).fetchall()
            for r in rows:
                rel = r["relation_type"]
                bucket = out.setdefault(rel, [])
                if len(bucket) < MAX_ROWS_PER_RELATION:
                    bucket.append(
                        {
                            "tgt_id": r["tgt_id"],
                            "adg_name": r["adg_name"],
                            "file_path": r["resolved_path"],
                            "layer": r["layer"],
                        }
                    )
    except sqlite3.Error as exc:
        logger.debug("_static_edges_for_node(%s) failed: %s", node_id, exc)
    return out


def annotate_span(
    span_attributes: dict[str, Any],
    *,
    target_identifier: str | None = None,
    query: RuntimeADGQuery | None = None,
    relations: tuple[str, ...] = SEMANTIC_RELATIONS,
) -> dict[str, Any]:
    """Return ``span_attributes`` with ``adg.static.*`` keys attached.

    If ``target_identifier`` is not provided, the function will look for
    a ``code.adg_name`` or ``code.function`` attribute in ``span_attributes``.

    Never mutates the input. Returns a shallow copy with the new keys.
    """
    out: dict[str, Any] = dict(span_attributes)
    ident = target_identifier or span_attributes.get("code.adg_name") or span_attributes.get("code.function")
    if not ident:
        return out
    q = query if query is not None else get_default_query()
    if q is None:
        return out
    env = q.blast_radius(str(ident))
    out[ADG_ATTR_PREFIX + "snapshot_id"] = env.snapshot_id
    out[ADG_ATTR_PREFIX + "archetype"] = env.archetype
    out[ADG_ATTR_PREFIX + "risk_band"] = env.risk_band
    out[ADG_ATTR_PREFIX + "layer"] = env.layer
    if env.node_id is None:
        out[ADG_ATTR_PREFIX + "node_resolved"] = False
        return out
    out[ADG_ATTR_PREFIX + "node_resolved"] = True
    out[ADG_ATTR_PREFIX + "node_id"] = env.node_id
    # Pull semantic edges.
    edges = _static_edges_for_node(Path(q.snapshot_path), env.node_id, relations)
    for rel, entries in edges.items():
        if not entries:
            continue
        # Flatten to a comma-joined list of adg_names for quick inspection;
        # full structured list is also kept under ``:details`` for richer
        # downstream processing.
        names = [e["adg_name"] for e in entries if e.get("adg_name")]
        out[f"{ADG_ATTR_PREFIX}{rel}"] = ",".join(names)
        out[f"{ADG_ATTR_PREFIX}{rel}:count"] = len(entries)
    return out


def drift_report(
    span_attributes: dict[str, Any],
    *,
    target_identifier: str | None = None,
    observed_writes_key: str = "observed.writes",
    observed_reads_key: str = "observed.reads",
) -> dict[str, Any]:
    """Compare observed span effects against the static-ADG prediction.

    Callers pass a span that already has (a) static ``adg.static.*`` keys
    from ``annotate_span`` AND (b) observed effect lists under
    ``observed_writes_key`` / ``observed_reads_key``.

    Returns a drift summary: expected-but-not-observed and
    observed-but-not-expected, for each of writes and reads.
    """
    enriched = annotate_span(span_attributes, target_identifier=target_identifier)
    expected_writes = _split_csv(enriched.get(f"{ADG_ATTR_PREFIX}writes_to", ""))
    expected_reads = _split_csv(enriched.get(f"{ADG_ATTR_PREFIX}reads_from", ""))
    observed_writes = set(span_attributes.get(observed_writes_key, []) or [])
    observed_reads = set(span_attributes.get(observed_reads_key, []) or [])

    return {
        "snapshot_id": enriched.get(f"{ADG_ATTR_PREFIX}snapshot_id"),
        "target": target_identifier or span_attributes.get("code.function"),
        "writes": {
            "expected": sorted(expected_writes),
            "observed": sorted(observed_writes),
            "missing": sorted(expected_writes - observed_writes),
            "unexpected": sorted(observed_writes - expected_writes),
        },
        "reads": {
            "expected": sorted(expected_reads),
            "observed": sorted(observed_reads),
            "missing": sorted(expected_reads - observed_reads),
            "unexpected": sorted(observed_reads - expected_reads),
        },
    }


def _split_csv(value: Any) -> set[str]:
    if not value:
        return set()
    if isinstance(value, (list, tuple, set)):
        return {str(v) for v in value if v}
    return {s for s in str(value).split(",") if s}


__all__ = ["annotate_span", "drift_report", "SEMANTIC_RELATIONS", "ADG_ATTR_PREFIX"]
