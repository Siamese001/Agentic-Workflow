"""Evidence Shaper — dedupe, normalize, reconcile, and compute coverage.

Pipeline steps (applied in order):
    1. Dedupe     — remove duplicate rows/findings across sources
    2. Normalize  — unify field names (source_file vs file_path, etc.)
    3. Reconcile  — cross-check DB counts vs report counts; tag mismatches
    4. Contradiction Retain — if DB says X but report says Y, preserve both
    5. Provenance Preserve — every item carries source artifact, digest, row ref
    6. Coverage/Gap — compute coverage score, identify gaps, flag weak support

The shaper NEVER drops contradictions or gaps. It ADDS flags.
"""

from __future__ import annotations

from typing import Any

from tools.adg.prompt_assembly.contracts import (
    ContradictionFlag,
    EvidenceBundle,
    EvidenceItem,
)


# ---------------------------------------------------------------------------
# Field normalization map
# ---------------------------------------------------------------------------

_FIELD_ALIASES: dict[str, str] = {
    "file_path": "source_file",
    "filepath": "source_file",
    "path": "source_file",
    "lineno": "line_no",
    "line_number": "line_no",
    "line": "line_no",
    "type": "relation_type",
    "edge_type": "relation_type",
    "kind": "identity_kind",
    "node_type": "identity_kind",
}


def _normalize_fields(data: dict[str, Any]) -> dict[str, Any]:
    """Normalize field names using the alias map."""
    normalized: dict[str, Any] = {}
    for key, value in data.items():
        canonical = _FIELD_ALIASES.get(key, key)
        if isinstance(value, dict):
            normalized[canonical] = _normalize_fields(value)
        elif isinstance(value, list):
            normalized[canonical] = [
                _normalize_fields(item) if isinstance(item, dict) else item for item in value
            ]
        else:
            normalized[canonical] = value
    return normalized


def _dedupe_items(items: list[EvidenceItem]) -> list[EvidenceItem]:
    """Remove duplicate evidence items based on (source_artifact, source_type, row_references)."""
    seen: set[str] = set()
    deduped: list[EvidenceItem] = []
    for item in items:
        key = f"{item.source_artifact}:{item.source_type}:{','.join(item.row_references)}"
        if key not in seen:
            seen.add(key)
            deduped.append(item)
    return deduped


def _reconcile_counts(items: list[EvidenceItem]) -> list[ContradictionFlag]:
    """Cross-check node/edge counts between SQLite and JSON report sources.

    Detects mismatches like DB node_count ≠ report modules_total and
    preserves both values as ContradictionFlags.
    """
    contradictions: list[ContradictionFlag] = []

    db_item: EvidenceItem | None = None
    report_item: EvidenceItem | None = None
    for item in items:
        if item.source_type == "sqlite" and "db_node_count" in item.data:
            db_item = item
        if item.source_type == "json_report" and "modules_total" in item.data:
            report_item = item

    if db_item and report_item:
        db_count = db_item.data.get("db_node_count")
        report_count = report_item.data.get("modules_total")
        if db_count is not None and report_count is not None and db_count != report_count:
            contradictions.append(
                ContradictionFlag(
                    field_name="node_count",
                    source_a=db_item.source_artifact,
                    value_a=db_count,
                    source_b=report_item.source_artifact,
                    value_b=report_count,
                    severity="major" if abs(db_count - report_count) > 100 else "minor",
                    description=(
                        f"SQLite DB reports {db_count} nodes but JSON report reports {report_count} modules"
                    ),
                )
            )

    # Check provenance reconciliation fields
    for item in items:
        if item.source_type == "json_report":
            reconciliation = item.data.get("reconciliation", {})
            if reconciliation:
                nodes_match = reconciliation.get("nodes_match")
                if nodes_match is False:
                    db_nodes = reconciliation.get("db_nodes")
                    report_nodes = reconciliation.get("report_nodes")
                    contradictions.append(
                        ContradictionFlag(
                            field_name="provenance_nodes_match",
                            source_a=f"{item.source_artifact}:db_nodes",
                            value_a=db_nodes,
                            source_b=f"{item.source_artifact}:report_nodes",
                            value_b=report_nodes,
                            severity="major",
                            description="Provenance report internal reconciliation: nodes_match=false",
                        )
                    )
                edges_match = reconciliation.get("edges_match")
                if edges_match is False:
                    db_edges = reconciliation.get("db_edges")
                    report_edges = reconciliation.get("report_edges")
                    contradictions.append(
                        ContradictionFlag(
                            field_name="provenance_edges_match",
                            source_a=f"{item.source_artifact}:db_edges",
                            value_a=db_edges,
                            source_b=f"{item.source_artifact}:report_edges",
                            value_b=report_edges,
                            severity="major",
                            description="Provenance report internal reconciliation: edges_match=false",
                        )
                    )

    return contradictions


def _compute_coverage(items: list[EvidenceItem], must_use_sources: list[str]) -> float:
    """Compute evidence coverage score (0.0–1.0) based on must-use source availability."""
    if not must_use_sources:
        return 1.0

    present_sources: set[str] = set()
    for item in items:
        if item.data.get("error"):
            continue
        # Match by source_type or by known artifact name patterns
        present_sources.add(item.source_type)
        artifact = item.source_artifact.lower()
        if "provenance" in artifact:
            present_sources.add("provenance_report")
        if "closure" in artifact:
            present_sources.add("closure_report")
        if "edge_density" in artifact:
            present_sources.add("edge_density_report")
        if "layer_coverage" in artifact:
            present_sources.add("layer_coverage_report")
        if "snapshot" in artifact:
            present_sources.add("snapshot")
        if "burndown" in artifact:
            present_sources.add("burndown")
        if "ratchet" in artifact:
            present_sources.add("ratchet")
        if "sc_ap_config" in artifact:
            present_sources.add("sc_ap_config")
        if "infra" in artifact:
            present_sources.add("infra_view")

    found = sum(1 for src in must_use_sources if src in present_sources)
    return found / len(must_use_sources)


def _identify_gaps(items: list[EvidenceItem], must_use_sources: list[str]) -> list[str]:
    """Identify missing must-use sources."""
    present_sources: set[str] = set()
    for item in items:
        if not item.data.get("error"):
            present_sources.add(item.source_type)
            artifact = item.source_artifact.lower()
            if "provenance" in artifact:
                present_sources.add("provenance_report")
            if "closure" in artifact:
                present_sources.add("closure_report")
            if "edge_density" in artifact:
                present_sources.add("edge_density_report")
            if "layer_coverage" in artifact:
                present_sources.add("layer_coverage_report")
            if "snapshot" in artifact:
                present_sources.add("snapshot")
            if "burndown" in artifact:
                present_sources.add("burndown")
            if "ratchet" in artifact:
                present_sources.add("ratchet")
            if "sc_ap_config" in artifact:
                present_sources.add("sc_ap_config")
            if "infra" in artifact:
                present_sources.add("infra_view")

    gaps: list[str] = []
    for src in must_use_sources:
        if src not in present_sources:
            gaps.append(f"missing_must_use_source:{src}")
    return gaps


def shape_evidence(
    items: list[EvidenceItem],
    must_use_sources: list[str] | None = None,
) -> EvidenceBundle:
    """Run the full shaping pipeline on a list of evidence items.

    Args:
        items: Raw evidence items from retrieval adapters.
        must_use_sources: List of source types/names that must be present.

    Returns:
        A shaped EvidenceBundle with contradictions, gaps, and coverage computed.
    """
    must_use = must_use_sources or []

    # Step 1: Dedupe
    deduped = _dedupe_items(items)

    # Step 2: Normalize field names in each item's data
    for item in deduped:
        item.data = _normalize_fields(item.data)

    # Step 3–4: Reconcile + Contradiction retain
    contradictions = _reconcile_counts(deduped)

    # Step 5: Coverage and gaps
    coverage = _compute_coverage(deduped, must_use)
    gaps = _identify_gaps(deduped, must_use)

    # Determine contradiction severity
    contradiction_status: str = "none"
    if any(c.severity == "major" for c in contradictions):
        contradiction_status = "major"
    elif contradictions:
        contradiction_status = "minor"

    # Determine freshness (latest among items)
    freshness_values = [item.freshness for item in deduped if item.freshness]
    freshness = max(freshness_values) if freshness_values else ""

    return EvidenceBundle(
        items=deduped,
        coverage_score=coverage,
        contradiction_status=contradiction_status,  # type: ignore[arg-type]
        contradictions=contradictions,
        gaps=gaps,
        freshness=freshness,
        weak_support=coverage < 0.5,
    )
