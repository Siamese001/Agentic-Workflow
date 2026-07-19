"""First-class ``metric_outcome`` node materialization for the augmented_skills_graph SQLite.

Plan: ``typed-edge-role-facet-guardrails-a6f3d2`` W2.0.

Before W2.0, metric outcomes lived only as side fields on role_episode_bundle JSON
(``linked_metric_outcome_ids`` list + top-level ``metric_outcome_nodes`` dict).
Validators (``ibm_bullets_x2``, ``unify_role_episode_x2``, etc.) read them via
``role_episode_metric_registry`` — fact-era side-field substrate.

This module discovers the per-employer ``*_role_episode_bundles.json`` files,
extracts every ``metric_outcome_nodes`` entry, and emits:

  * a ``metric_outcome`` graph_node row per metric ID (canonical node_type)
  * edges binding each metric_outcome to its role_episode_bundle, sections
    where it is eligible, and the employer it belongs to

The function is invoked from
``augmented_skills_graph_sqlite.materialize_augmented_skills_graph_sqlite``;
no consumer code is changed by W2.0 (that is W2.2's scope — graph-era field
migration + fact_ledger fence). The materialization is **behavior-neutral**:
new rows/edges are net-additive, and no existing edge_type/node_type query
returns these rows.

Resolver: ``resolve_metric_outcome_graph_node(conn, metric_id)`` is the
W2.0 API consumers will adopt in W2.2. It returns the materialized graph_node
row, or ``None`` if the metric ID has no graph row — in which case the caller
MUST fail closed with ``MISSING_GRAPH_PATH`` or
``BLOCKED_METRIC_OUTCOME_UNRESOLVED`` per the plan's No Silent Fallback Rule.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

#: Edge types introduced by W2.0. They do not collide with the canonical
#: ledger taxonomy and are admitted through the projected signature authority.
METRIC_OUTCOME_EDGE_TYPES: frozenset[str] = frozenset(
    {
        "metric_outcome_anchors_bundle",
        "metric_outcome_section_eligible",
        "metric_outcome_bound_to_employer",
    }
)

#: Projected endpoint-type authority for the edges emitted by this module.
#: These signatures are app-owned because the edges derive from role-episode
#: bundle materialization rather than the canonical ledger edge registry.
METRIC_OUTCOME_EDGE_SIGNATURES: dict[str, frozenset[tuple[str, str]]] = {
    "metric_outcome_anchors_bundle": frozenset({("metric_outcome", "graph_ref")}),
    "metric_outcome_section_eligible": frozenset({("metric_outcome", "graph_ref")}),
    "metric_outcome_bound_to_employer": frozenset({("metric_outcome", "employment")}),
}

#: Glob pattern for per-employer role_episode_bundle JSON files.
ROLE_EPISODE_BUNDLE_GLOB: str = "*_role_episode_bundles.json"


def _required_unique_string_list(
    metric: dict[str, Any],
    *,
    field: str,
    locator: str,
) -> list[str]:
    value = metric.get(field)
    if not isinstance(value, list):
        raise ValueError(f"metric_outcome_materializer: {locator}.{field} must be a JSON list")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise ValueError(
            f"metric_outcome_materializer: {locator}.{field} must contain only non-empty strings"
        )
    normalized = [item.strip() for item in value]
    if len(normalized) != len(set(normalized)):
        raise ValueError(f"metric_outcome_materializer: {locator}.{field} contains duplicate IDs")
    return normalized


def discover_role_episode_bundle_files(repo_root: Path) -> list[Path]:
    """Return all ``*_role_episode_bundles.json`` under ``apps_rg/fact_inventory/``."""
    base = (repo_root / "apps_rg/fact_inventory").resolve()
    if not base.is_dir():
        return []
    return sorted(base.glob(ROLE_EPISODE_BUNDLE_GLOB))


def _metric_outcome_to_node_row(metric_id: str, metric: dict[str, Any], *, ts: str) -> dict[str, Any]:
    """Map a metric_outcome dict (from bundle JSON) to a graph_nodes row.

    ``approval_status`` from the bundle ('APPROVED_GRAPH_SSOT', etc.) maps to
    ``activation_status`` on the graph node so existing approval-status queries
    (filtered by node_type) keep their semantics within the metric_outcome surface.
    """
    label = (
        str(metric.get("metric") or "").strip() or str(metric.get("claim_text") or "").strip() or metric_id
    )
    description = str(metric.get("claim_text") or "").strip()
    approval = str(metric.get("approval_status") or "").strip()
    support = str(metric.get("support_level") or "").strip()
    return {
        "node_id": metric_id,
        "node_type": "metric_outcome",
        "label": label,
        "description": description,
        "activation_status": approval,
        "support_level": support,
        "confidence": "",
        "external_eligible": 1 if bool(metric.get("approved")) else 0,
        "source_authority": "augmented_skills_graph",
        "created_at": ts,
        "updated_at": ts,
    }


def _metric_outcome_to_edge_rows(
    metric_id: str,
    metric: dict[str, Any],
    *,
    known_node_ids: set[str],
) -> list[dict[str, Any]]:
    """Emit edges from a metric_outcome to its bundle bindings, sections, employer.

    Bundle and section tokens are emitted as graph references; the caller
    hydrates those endpoints and enforces ``METRIC_OUTCOME_EDGE_SIGNATURES``.
    Employer edges remain conditional on an already-materialized employer.
    """
    edges: list[dict[str, Any]] = []
    employer_node_id = str(metric.get("employer_node_id") or "").strip()
    bundle_bindings = metric.get("bundle_bindings") or []
    section_eligibility = metric.get("section_eligibility") or []

    for bundle_id in bundle_bindings:
        bid = str(bundle_id or "").strip()
        if not bid:
            continue
        # Bundles use reb_* IDs and remain typed graph_ref endpoints because
        # role-episode bundles are not first-class canonical graph nodes.
        edges.append(
            {
                "edge_id": f"edge_metric_outcome_anchors_bundle__{metric_id}__{bid}",
                "source_node_id": metric_id,
                "target_node_id": bid,
                "edge_family": "metric_outcome",
                "edge_type": "metric_outcome_anchors_bundle",
                "weight": 1.0,
                "confidence": "",
                "directional": 1,
                "evidence_status": "approved_graph_ssot"
                if str(metric.get("approval_status") or "") == "APPROVED_GRAPH_SSOT"
                else "",
                "section_fit": "",
                "source_authority": "augmented_skills_graph",
            }
        )

    for section_ref in section_eligibility:
        section_id = str(section_ref or "").strip()
        if not section_id:
            continue
        edges.append(
            {
                "edge_id": f"edge_metric_outcome_section_eligible__{metric_id}__{section_id}",
                "source_node_id": metric_id,
                "target_node_id": section_id,
                "edge_family": "metric_outcome",
                "edge_type": "metric_outcome_section_eligible",
                "weight": 1.0,
                "confidence": "",
                "directional": 1,
                "evidence_status": "",
                "section_fit": section_id,
                "source_authority": "augmented_skills_graph",
            }
        )

    if employer_node_id and employer_node_id in known_node_ids:
        edges.append(
            {
                "edge_id": f"edge_metric_outcome_bound_to_employer__{metric_id}__{employer_node_id}",
                "source_node_id": metric_id,
                "target_node_id": employer_node_id,
                "edge_family": "metric_outcome",
                "edge_type": "metric_outcome_bound_to_employer",
                "weight": 1.0,
                "confidence": "",
                "directional": 1,
                "evidence_status": "",
                "section_fit": "",
                "source_authority": "augmented_skills_graph",
            }
        )

    return edges


def load_metric_outcome_rows_from_bundles(repo_root: Path) -> dict[str, dict[str, Any]]:
    """Discover all role_episode_bundle JSONs and return ``{metric_id: metric_dict}``.

    Bundle file employer is carried onto each metric row as ``employer_node_id``
    so edge materialization can bind metrics to the employer node.

    Later bundle files do not silently overwrite earlier ones — a metric ID
    declared in two bundles raises ``ValueError`` (provenance conflict).
    """
    out: dict[str, dict[str, Any]] = {}
    for path in discover_role_episode_bundle_files(repo_root):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"metric_outcome_materializer: failed to read {path.name}: {exc}") from exc
        if not isinstance(payload, dict):
            raise ValueError(f"metric_outcome_materializer: {path.name} root must be a JSON object")
        raw_employer_node_id = payload.get("employer_node_id")
        if raw_employer_node_id is not None and not isinstance(raw_employer_node_id, str):
            raise ValueError(f"metric_outcome_materializer: {path.name}.employer_node_id must be a string")
        employer_node_id = str(raw_employer_node_id or "").strip()
        nodes = payload.get("metric_outcome_nodes")
        if not isinstance(nodes, dict):
            raise ValueError(
                f"metric_outcome_materializer: {path.name}.metric_outcome_nodes must be a JSON object"
            )
        for metric_id, metric in nodes.items():
            if not isinstance(metric_id, str) or not metric_id.strip():
                raise ValueError(
                    f"metric_outcome_materializer: {path.name} contains a blank or non-string metric ID"
                )
            mid = metric_id.strip()
            if not isinstance(metric, dict):
                raise ValueError(
                    f"metric_outcome_materializer: {path.name}.metric_outcome_nodes[{mid!r}] "
                    "must be a JSON object"
                )
            if mid in out:
                raise ValueError(
                    f"metric_outcome_materializer: duplicate metric_id {mid!r} "
                    f"in {path.name} (already present from earlier bundle); "
                    "metric IDs must be unique across role_episode_bundle files."
                )
            merged = dict(metric)
            declared_metric_id = merged.get("metric_outcome_id")
            if declared_metric_id is not None and declared_metric_id != mid:
                raise ValueError(
                    f"metric_outcome_materializer: {path.name}.metric_outcome_nodes[{mid!r}] "
                    "metric_outcome_id must match its registry key"
                )
            metric_employer_node_id = merged.get("employer_node_id")
            if metric_employer_node_id is not None and not isinstance(metric_employer_node_id, str):
                raise ValueError(
                    f"metric_outcome_materializer: {path.name}.metric_outcome_nodes[{mid!r}] "
                    "employer_node_id must be a string"
                )
            locator = f"{path.name}.metric_outcome_nodes[{mid!r}]"
            merged["bundle_bindings"] = _required_unique_string_list(
                merged,
                field="bundle_bindings",
                locator=locator,
            )
            merged["section_eligibility"] = _required_unique_string_list(
                merged,
                field="section_eligibility",
                locator=locator,
            )
            if employer_node_id and "employer_node_id" not in merged:
                merged["employer_node_id"] = employer_node_id
            out[mid] = merged
    return out


def metric_outcome_node_and_edge_rows(
    repo_root: Path,
    *,
    ts: str,
    known_node_ids: set[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Return ``(node_rows, edge_rows)`` for all metric_outcome materialization.

    ``known_node_ids`` is the set of node IDs already present in the
    materialization (skills, employers, sections, etc.); employer edges are
    skipped if the employer node is not yet known. Section node IDs are
    intentionally permitted as targets even if missing (they are materialized
    by other code paths and may not be in known_node_ids at the time of
    this call).
    """
    rows = load_metric_outcome_rows_from_bundles(repo_root)
    node_rows: list[dict[str, Any]] = []
    edge_rows: list[dict[str, Any]] = []
    for mid, metric in rows.items():
        node_rows.append(_metric_outcome_to_node_row(mid, metric, ts=ts))
        edge_rows.extend(_metric_outcome_to_edge_rows(mid, metric, known_node_ids=known_node_ids))
    return node_rows, edge_rows


def resolve_metric_outcome_graph_node(conn: Any, metric_id: str) -> dict[str, Any] | None:
    """Look up a materialized metric_outcome graph_node row.

    Returns the row dict if present, ``None`` if not materialized. Callers MUST
    treat ``None`` as a fail-closed condition (``MISSING_GRAPH_PATH`` or
    ``BLOCKED_METRIC_OUTCOME_UNRESOLVED``) per the plan's No Silent Fallback Rule.

    This is the W2.0 resolver consumers will adopt in W2.2 — see
    ``role_episode_metric_registry.py`` and ``ibm_bullets_x2.py`` for the
    migration sites.
    """
    mid = str(metric_id or "").strip()
    if not mid:
        return None
    cur = conn.cursor()
    cur.execute(
        "SELECT node_id, node_type, label, description, activation_status, "
        "support_level, confidence, external_eligible, source_authority "
        "FROM graph_nodes WHERE node_id = ? AND node_type = 'metric_outcome'",
        (mid,),
    )
    row = cur.fetchone()
    if row is None:
        return None
    return {
        "node_id": row[0],
        "node_type": row[1],
        "label": row[2],
        "description": row[3],
        "activation_status": row[4],
        "support_level": row[5],
        "confidence": row[6],
        "external_eligible": int(row[7]),
        "source_authority": row[8],
    }


__all__ = [
    "METRIC_OUTCOME_EDGE_SIGNATURES",
    "METRIC_OUTCOME_EDGE_TYPES",
    "ROLE_EPISODE_BUNDLE_GLOB",
    "discover_role_episode_bundle_files",
    "load_metric_outcome_rows_from_bundles",
    "metric_outcome_node_and_edge_rows",
    "resolve_metric_outcome_graph_node",
]
