"""Graph-era ↔ fact-era field name alias layer (W2.2).

Plan: ``typed-edge-role-facet-guardrails-a6f3d2`` W2.2.

The W2 migration renames runtime/section/validator/proof-pool field names from
the legacy fact-era taxonomy to graph-era taxonomy:

    selected_fact_plan         → selected_graph_evidence_plan
    allowed_fact_ids           → allowed_graph_evidence_ids
    source_fact_ids            → graph_evidence_ids
    fact_id                    → graph_evidence_id

Per the W2.2 implementation strategy (operator-amended 2026-06-13, plan
``typed-edge-role-facet-guardrails-a6f3d2`` §W2.2), the full migration across
the 158 fact-era consumer files is deferred. The alias layer in THIS module is
the foundational compatibility surface that lets producers emit BOTH names and
consumers read EITHER name with graph-era preferred. Subsequent waves migrate
consumers progressively without churning every producer in one pass.

W2.2 forbids `fact_ledger` as a runtime authority for skill or metric eligibility
— see ``apps_rg/runtime/section_spec.py`` and the ``BLOCKED_FACT_LEDGER_AUTHORITY``
canonical verdict. The alias layer is a NAME-SPACE compatibility shim only and
does NOT re-admit ``fact_ledger`` as an authority surface. ``legacy_candidate_fact_id``
remains a lineage-only field per P0.

Usage
-----

Producers (emit both names so any consumer reads correctly)::

    from apps_rg.runtime.graph_era_aliases import emit_graph_era_aliases

    record = {"source_fact_ids": ["fact_abc"], "fact_id": "fact_abc"}
    emit_graph_era_aliases(record)
    # record now also has "graph_evidence_ids": ["fact_abc"], "graph_evidence_id": "fact_abc"

Consumers (read graph-era, fall back to fact-era)::

    from apps_rg.runtime.graph_era_aliases import read_graph_evidence_ids

    ids = read_graph_evidence_ids(record)  # prefers graph_evidence_ids, falls back to source_fact_ids
"""
from __future__ import annotations

from typing import Any, Mapping, MutableMapping

#: Canonical alias map: graph-era name → fact-era name. Both names carry the SAME
#: payload; producers using ``emit_graph_era_aliases`` ensure consumers reading
#: either name see the same value.
GRAPH_ERA_FIELD_ALIASES: dict[str, str] = {
    "selected_graph_evidence_plan": "selected_fact_plan",
    "allowed_graph_evidence_ids": "allowed_fact_ids",
    "graph_evidence_ids": "source_fact_ids",
    "graph_evidence_id": "fact_id",
}

#: Reverse map: fact-era name → graph-era name (for migration tooling, not runtime).
FACT_ERA_TO_GRAPH_ERA: dict[str, str] = {v: k for k, v in GRAPH_ERA_FIELD_ALIASES.items()}


def emit_graph_era_aliases(record: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
    """Mutate ``record`` in place so every fact-era key has a graph-era twin.

    For each alias pair (``graph_evidence_ids`` ↔ ``source_fact_ids`` etc.):

    * If only the fact-era key is present, copy the value to the graph-era key.
    * If only the graph-era key is present, copy the value to the fact-era key
      (back-compat — keeps fact-era readers working until they migrate).
    * If both are present and equal, no change.
    * If both are present and unequal, raise ``ValueError`` — this means an upstream
      producer set both with divergent values, which is a bug (the alias layer
      cannot disambiguate).

    Returns the same ``record`` for chaining.
    """
    for graph_key, fact_key in GRAPH_ERA_FIELD_ALIASES.items():
        graph_present = graph_key in record
        fact_present = fact_key in record
        if graph_present and fact_present:
            if record[graph_key] != record[fact_key]:
                raise ValueError(
                    f"graph_era_aliases: divergent values for alias pair "
                    f"{graph_key!r} / {fact_key!r} — producer set both with "
                    f"different payloads, alias layer cannot disambiguate."
                )
            continue
        if fact_present and not graph_present:
            record[graph_key] = record[fact_key]
        elif graph_present and not fact_present:
            record[fact_key] = record[graph_key]
    return record


def read_graph_evidence_ids(record: Mapping[str, Any]) -> list[str]:
    """Read ``graph_evidence_ids`` from a record (graph-era preferred, fact-era fallback).

    Returns ``[]`` when neither key is present. Stripped, deduplicated, preserves
    first-seen order. The returned list is a fresh copy; mutating it does not
    affect ``record``.
    """
    raw = record.get("graph_evidence_ids")
    if raw is None:
        raw = record.get("source_fact_ids")
    if raw is None:
        return []
    if isinstance(raw, str):
        raw = [raw]
    out: list[str] = []
    seen: set[str] = set()
    for item in raw:
        s = str(item or "").strip()
        if not s or s in seen:
            continue
        seen.add(s)
        out.append(s)
    return out


def read_graph_evidence_id(record: Mapping[str, Any]) -> str:
    """Read ``graph_evidence_id`` (graph-era preferred, ``fact_id`` fallback).

    Returns ``""`` when neither key is present.
    """
    raw = record.get("graph_evidence_id")
    if raw is None:
        raw = record.get("fact_id")
    return str(raw or "").strip()


def read_allowed_graph_evidence_ids(record: Mapping[str, Any]) -> list[str]:
    """Read ``allowed_graph_evidence_ids`` (preferred) or ``allowed_fact_ids`` (fallback)."""
    raw = record.get("allowed_graph_evidence_ids")
    if raw is None:
        raw = record.get("allowed_fact_ids")
    if raw is None:
        return []
    if isinstance(raw, str):
        raw = [raw]
    out: list[str] = []
    seen: set[str] = set()
    for item in raw:
        s = str(item or "").strip()
        if not s or s in seen:
            continue
        seen.add(s)
        out.append(s)
    return out


def read_selected_graph_evidence_plan(record: Mapping[str, Any]) -> Any:
    """Read ``selected_graph_evidence_plan`` (preferred) or ``selected_fact_plan`` (fallback)."""
    raw = record.get("selected_graph_evidence_plan")
    if raw is None:
        raw = record.get("selected_fact_plan")
    return raw


__all__ = [
    "FACT_ERA_TO_GRAPH_ERA",
    "GRAPH_ERA_FIELD_ALIASES",
    "emit_graph_era_aliases",
    "read_allowed_graph_evidence_ids",
    "read_graph_evidence_id",
    "read_graph_evidence_ids",
    "read_selected_graph_evidence_plan",
]
