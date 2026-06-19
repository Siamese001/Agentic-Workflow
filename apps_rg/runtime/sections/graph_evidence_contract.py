"""Graph-native evidence contract helpers for apps_rg section lanes.

This module owns generic proof-pool mechanics shared by graph evidence lanes:
metric derivative IDs, selected evidence plan normalization, active proof-pool
reporting, and claim-ledger source ID collection. It deliberately does not load
or resolve SelectedRoleFactSet/SRFS artifacts.
"""

from __future__ import annotations

from collections import Counter
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

from apps_rg.runtime.graph_era_aliases import emit_graph_era_aliases

SECTION_KEYS: tuple[str, ...] = (
    "competencies",
    "unify_bullets",
    "ibm_bullets",
    "insurtech_bullets",
    "ey_bullets",
    "unify_narrative",
    "ibm_narrative",
    "insurtech_narrative",
    "ey_narrative",
    "executive_summary",
    "headline",
)


def sha16(value: str | bytes) -> str:
    data = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(data).hexdigest()[:16]


def metric_derivative_fact_id(candidate_fact_id: str, metric_raw: str) -> str:
    """Metric-bound derivative ID for section proof-pool allowlists."""
    return f"{candidate_fact_id}_metric_{sha16(metric_raw)[:8]}"


def _metric_raw_from_row(row: dict[str, Any]) -> str:
    raw_metrics = row.get("metric_values") or []
    if not isinstance(raw_metrics, list) or not raw_metrics:
        return ""
    return "|".join(str(x) for x in raw_metrics if str(x).strip())


def slice_row_to_plan_fact(
    slice_row: dict[str, Any],
    *,
    section_id: str = "executive_summary",
) -> dict[str, Any]:
    """Map a graph/candidate evidence row to a selected evidence plan fact."""
    _ = section_id
    cid = str(
        slice_row.get("candidate_fact_id")
        or slice_row.get("fact_id")
        or slice_row.get("role_episode_bundle_id")
        or ""
    ).strip()
    if not cid:
        raise ValueError("selected graph evidence row missing candidate_fact_id/fact_id")
    conf = str(slice_row.get("confidence") or slice_row.get("support_level") or "HIGH").strip().upper()
    vstat = str(
        slice_row.get("verification_status")
        or slice_row.get("approval_status")
        or slice_row.get("support_level")
        or "approved_by_graph_presence"
    ).strip()
    mr = _metric_raw_from_row(slice_row)
    technologies = slice_row.get("technologies")
    if not isinstance(technologies, list):
        technologies = []
    row: dict[str, Any] = {
        "fact_id": cid,
        "claim_text": str(slice_row.get("claim_text") or "").strip(),
        "candidate_fact_id": cid,
        "verification_status": vstat,
        "confidence": conf,
        "claim_eligible_medium": bool(slice_row.get("claim_eligible_medium")),
        "source_trace_archive_relpaths": list(slice_row.get("source_trace_archive_relpaths") or ()),
        "metric_values": tuple(slice_row.get("metric_values") or ()),
        "company_lane": slice_row.get("company_lane"),
        "role_families_supported": slice_row.get("role_families_supported") or [],
        "metric_raw": mr,
        "has_metric": bool(mr),
        "technologies": technologies,
        "domain": str(slice_row.get("domain") or slice_row.get("domain_family") or "").strip(),
        "source_employment": str(slice_row.get("source_employment") or "").strip(),
    }
    for key in (
        "role_episode_bundle_id",
        "employer",
        "employer_node_id",
        "graph_skill_node_ids",
        "metric_outcome_ids",
        "selected_metric_ids",
        "allowed_graph_evidence_ids",
        "linked_identity_fact_ids",
        "graph_evidence_type",
    ):
        if key in slice_row:
            row[key] = slice_row[key]
    return row


def build_allowed_fact_ids_for_plan_facts(
    facts: list[dict[str, Any]],
) -> tuple[list[str], set[str]]:
    """Return ordered allowed IDs: base fact IDs plus metric derivatives."""
    ordered: list[str] = []
    seen: set[str] = set()

    def _push(fid: str) -> None:
        if fid and fid not in seen:
            seen.add(fid)
            ordered.append(fid)

    for fact in facts:
        fid = str(fact.get("fact_id") or "").strip()
        _push(fid)
        for gid in fact.get("allowed_graph_evidence_ids") or []:
            _push(str(gid).strip())
        mr = fact.get("metric_raw")
        if mr and fid:
            _push(metric_derivative_fact_id(fid, str(mr)))
    return ordered, set(ordered)


def selection_method_for_section(section_id: str) -> str:
    return f"selected_graph_evidence_plan_{section_id}"


def selected_graph_evidence_plan_from_payload(source: dict[str, Any] | None) -> dict[str, Any]:
    """Extract the selected graph-evidence plan from a runtime payload or proof-pool metadata."""
    if not isinstance(source, dict):
        return {}
    plan = source.get("selected_graph_evidence_plan")
    if isinstance(plan, dict) and plan:
        return plan
    pp_meta = source.get("proof_pool_metadata")
    if isinstance(pp_meta, dict):
        nested = pp_meta.get("selected_graph_evidence_plan")
        if isinstance(nested, dict) and nested:
            return nested
    return {}


def require_selected_graph_evidence_plan(
    source: dict[str, Any] | None,
    *,
    section_id: str,
) -> dict[str, Any]:
    plan = selected_graph_evidence_plan_from_payload(source)
    if not plan:
        raise ValueError(
            f"{section_id}: graph packet is mandatory; missing selected_graph_evidence_plan"
        )
    return plan


def require_section_packet(
    source: dict[str, Any] | None,
    *,
    section_id: str,
    packet_key: str,
) -> dict[str, Any]:
    """Require an attached section packet either top-level or nested in proof_pool_metadata."""
    if not isinstance(source, dict):
        raise ValueError(f"{section_id}: graph packet is mandatory; missing {packet_key}")
    packet = source.get(packet_key)
    if not isinstance(packet, dict) or not packet:
        pp_meta = source.get("proof_pool_metadata")
        if isinstance(pp_meta, dict):
            nested = pp_meta.get(packet_key)
            if isinstance(nested, dict) and nested:
                packet = nested
    if not isinstance(packet, dict) or not packet:
        raise ValueError(f"{section_id}: graph packet is mandatory; missing {packet_key}")
    return packet


def build_selected_graph_evidence_plan(
    *,
    section_id: str,
    selection_method: str,
    facts: list[dict[str, Any]],
    required_fact_ids: list[str] | None = None,
    **extra_fields: Any,
) -> dict[str, Any]:
    """Build a selected graph-evidence plan with optional section-specific metadata."""
    plan: dict[str, Any] = {
        "section_id": section_id,
        "selection_method": selection_method,
        "facts": facts,
    }
    if required_fact_ids is not None:
        plan["required_fact_ids"] = list(required_fact_ids)
    if extra_fields:
        plan.update(extra_fields)
    return plan


def build_graph_evidence_runtime_payload(
    *,
    run_id_prefix: str,
    section_id: str,
    prompt_id: str,
    repo_root: Path,
    base_json_path: Path,
    base_hash: str,
    selected_graph_evidence_plan: dict[str, Any],
    allowed_graph_evidence_ids: Iterable[str],
    target_title: str,
    target_company: str,
    jd_text: str,
    briefing: str,
    writable_context_scope: str,
    extra_fields: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a graph-era runtime payload and backfill fact-era aliases for compatibility."""
    payload: dict[str, Any] = {
        "run_id": datetime.now(timezone.utc).strftime(f"{run_id_prefix}_%Y%m%d_%H%M%S"),
        "section_id": section_id,
        "prompt_id": prompt_id,
        "base_resume_json_ref": str(base_json_path.relative_to(repo_root))
        if base_json_path.is_relative_to(repo_root)
        else str(base_json_path),
        "base_resume_json_hash": base_hash,
        "target_title": target_title,
        "target_company": target_company,
        "jd_text": jd_text,
        "briefing": briefing,
        "selected_graph_evidence_plan": selected_graph_evidence_plan,
        "allowed_graph_evidence_ids": list(allowed_graph_evidence_ids),
        "writable_context_scope": writable_context_scope,
        "full_resume_writable": False,
    }
    if extra_fields:
        payload.update(extra_fields)
    emit_graph_era_aliases(payload)
    return payload


def _nonempty_trimmed_strings(values: Any) -> list[str]:
    raw: list[Any]
    if values is None:
        raw = []
    elif isinstance(values, str):
        raw = [values]
    elif isinstance(values, (list, tuple, set, frozenset)):
        raw = list(values)
    else:
        raw = [values]
    out: list[str] = []
    seen: set[str] = set()
    for item in raw:
        text = str(item).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out


def _graph_evidence_depth_row(
    item: dict[str, Any],
    *,
    section_id: str,
    packet_shape: str,
) -> dict[str, Any]:
    item_id = str(
        item.get("fact_id")
        or item.get("candidate_fact_id")
        or item.get("role_episode_bundle_id")
        or item.get("competency_bundle_id")
        or item.get("headline_positioning_bundle_id")
        or item.get("item_id")
        or ""
    ).strip()
    if packet_shape == "bundles":
        skill_ids = _nonempty_trimmed_strings(item.get("graph_skill_node_ids") or item.get("source_skill_ids"))
        linked_ids = _nonempty_trimmed_strings(
            item.get("linked_source_fact_ids")
            or item.get("source_fact_ids")
            or item.get("source_fact_id")
        )
        target_category_ids = _nonempty_trimmed_strings(item.get("target_taxonomy_category_ids"))
        missing_axes = []
        if not skill_ids:
            missing_axes.append("skills")
        if not linked_ids:
            missing_axes.append("source_facts")
        rich = not missing_axes
        axis_hit_count = int(bool(skill_ids)) + int(bool(linked_ids))
        axis_total = 2
        return {
            "item_id": item_id or f"{section_id}_bundle",
            "category_id": str(item.get("category_id") or (target_category_ids[0] if target_category_ids else "")).strip(),
            "competency_bundle_id": str(item.get("competency_bundle_id") or "").strip(),
            "capability_family": str(item.get("capability_family") or "").strip(),
            "label": str(
                item.get("display_label_candidate")
                or item.get("display_phrase_candidate")
                or item.get("capability_family")
                or item.get("positioning_family")
                or item_id
            ).strip(),
            "packet_shape": packet_shape,
            "rich": rich,
            "missing_axes": missing_axes,
            "axis_hit_count": axis_hit_count,
            "axis_total": axis_total,
            "skill_count": len(skill_ids),
            "linked_fact_count": len(linked_ids),
            "source_fact_ids": linked_ids,
            "linked_fact_ids": linked_ids,
            "skill_ids": skill_ids,
        }

    skill_ids = _nonempty_trimmed_strings(
        item.get("graph_skill_node_ids")
        or item.get("selected_skill_ids")
        or item.get("source_skill_ids")
        or item.get("graph_skill_node_id")
    )
    metric_ids = _nonempty_trimmed_strings(
        item.get("metric_outcome_ids")
        or item.get("selected_metric_ids")
        or item.get("linked_metric_outcome_ids")
    )
    missing_axes = []
    if not skill_ids:
        missing_axes.append("skills")
    if not metric_ids:
        missing_axes.append("metrics")
    rich = not missing_axes
    axis_hit_count = int(bool(skill_ids)) + int(bool(metric_ids))
    axis_total = 2
    return {
        "item_id": item_id or f"{section_id}_fact",
        "category_id": str(item.get("category_id") or "").strip(),
        "competency_bundle_id": str(item.get("competency_bundle_id") or "").strip(),
        "capability_family": str(item.get("capability_family") or "").strip(),
        "label": str(
            item.get("claim_text")
            or item.get("bundle_theme")
            or item.get("claim_text")
            or item_id
        ).strip(),
        "packet_shape": packet_shape,
        "rich": rich,
        "missing_axes": missing_axes,
        "axis_hit_count": axis_hit_count,
        "axis_total": axis_total,
        "skill_count": len(skill_ids),
        "metric_count": len(metric_ids),
        "source_fact_ids": _nonempty_trimmed_strings(item.get("source_fact_ids") or [item_id]),
        "skill_ids": skill_ids,
        "metric_ids": metric_ids,
    }


_VENDOR_TOKENS = frozenset({
    "aws",
    "azure",
    "databricks",
    "gcp",
    "google",
    "ibm",
    "openai",
    "salesforce",
    "snowflake",
})


def _unit_float(value: float) -> float:
    return round(max(0.0, min(float(value), 1.0)), 4)


def _token_overlap_score(text: str, reference: str) -> float:
    text_tokens = {tok for tok in _nonempty_trimmed_strings(str(text or "").lower().replace("/", " ").split())}
    reference_tokens = {
        tok for tok in _nonempty_trimmed_strings(str(reference or "").lower().replace("/", " ").split())
    }
    if not text_tokens or not reference_tokens:
        return 0.0
    return _unit_float(len(text_tokens & reference_tokens) / len(text_tokens))


def _row_detail_ids(row: dict[str, Any], *, packet_shape: str) -> list[str]:
    key = "metric_ids" if packet_shape == "facts" else "linked_fact_ids"
    return [str(x).strip() for x in (row.get(key) or row.get("source_fact_ids") or []) if str(x).strip()]


def _vendor_overfit_penalty(row: dict[str, Any], *, jd_text: str) -> float:
    label_tokens = {tok.lower() for tok in str(row.get("label") or "").replace("/", " ").split()}
    vendors = label_tokens & _VENDOR_TOKENS
    if not vendors:
        return 0.0
    jd_tokens = {tok.lower() for tok in str(jd_text or "").replace("/", " ").split()}
    return 0.0 if vendors & jd_tokens else 1.0


def _rank_depth_row_weakness(
    row: dict[str, Any],
    *,
    packet_shape: str,
    detail_frequency: Counter[str],
    jd_text: str,
    briefing_text: str,
) -> dict[str, Any]:
    detail_ids = _row_detail_ids(row, packet_shape=packet_shape)
    missing_skill_axis = 1.0 if "skills" in (row.get("missing_axes") or []) else 0.0
    missing_fact_or_metric_axis = 1.0 if any(
        axis in (row.get("missing_axes") or []) for axis in ("source_facts", "metrics")
    ) else 0.0
    repeated_detail_penalty = 1.0 if any(detail_frequency.get(detail_id, 0) > 1 for detail_id in detail_ids) else 0.0
    vendor_penalty = _vendor_overfit_penalty(row, jd_text=jd_text)
    jd_overlap = _token_overlap_score(str(row.get("label") or ""), jd_text)
    briefing_overlap = _token_overlap_score(str(row.get("label") or ""), briefing_text)
    jd_only_or_briefing_only_penalty = (
        1.0
        if (jd_overlap or briefing_overlap) and missing_skill_axis and missing_fact_or_metric_axis
        else 0.0
    )
    weakness_score = _unit_float(
        missing_skill_axis * 0.30
        + missing_fact_or_metric_axis * 0.30
        + repeated_detail_penalty * 0.15
        + vendor_penalty * 0.15
        + jd_only_or_briefing_only_penalty * 0.10
    )
    reason = "adequate_support"
    if missing_fact_or_metric_axis:
        reason = "thin_fact_support"
    elif missing_skill_axis:
        reason = "missing_skill_axis"
    elif repeated_detail_penalty:
        reason = "repeated_metric" if packet_shape == "facts" else "repeated_source_fact"
    elif vendor_penalty:
        reason = "vendor_overfit"
    elif jd_only_or_briefing_only_penalty:
        reason = "jd_or_briefing_only"
    confidence = _unit_float(1.0 - weakness_score)
    return {
        "category_id": row.get("category_id") or "",
        "competency_bundle_id": row.get("competency_bundle_id") or "",
        "term": row.get("label") or row.get("item_id") or "",
        "item_id": row.get("item_id") or "",
        "reason": reason,
        "source_fact_ids": row.get("source_fact_ids") or [],
        "graph_skill_node_ids": row.get("skill_ids") or [],
        "confidence": confidence,
        "weakness_score": weakness_score,
        "components": {
            "missing_skill_axis": missing_skill_axis,
            "missing_fact_or_metric_axis": missing_fact_or_metric_axis,
            "repeated_detail_penalty": repeated_detail_penalty,
            "vendor_overfit_penalty": vendor_penalty,
            "jd_only_or_briefing_only_penalty": jd_only_or_briefing_only_penalty,
        },
    }


def build_graph_evidence_depth_report(
    source: dict[str, Any] | None,
    *,
    section_id: str,
    packet_key: str | None = None,
) -> dict[str, Any]:
    """Return a fail-closed depth report for the selected graph evidence packet."""

    if not isinstance(source, dict) or not source:
        return {
            "schema": "graph_evidence_depth_report_v2",
            "section_id": section_id,
            "packet_key": packet_key or "",
            "packet_shape": "missing",
            "item_count": 0,
            "rich_item_count": 0,
            "unique_skill_count": 0,
            "unique_detail_count": 0,
            "item_rich_ratio": 0.0,
            "skill_diversity_ratio": 0.0,
            "detail_diversity_ratio": 0.0,
            "semantic_coverage_pct": 0.0,
            "axis_coverage_pct": 0.0,
            "minimum_coverage_pct": 0.0,
            "status": "missing",
            "thin_item_ids": [],
            "items": [],
            "weakest_link": None,
            "category_graph_confidence": 0.0,
            "claim_ledger_confidence": 0.0,
            "proof_authority_score": 0.0,
            "targeting_fit_score": 0.0,
            "support_ratio": {
                "items_with_fact_support": 0,
                "items_with_skill_support": 0,
                "items_total": 0,
            },
            "penalties": {
                "metric_reuse_penalty": 0.0,
                "vendor_overfit_penalty": 0.0,
                "generic_label_penalty": 0.0,
            },
            "term_confidence_rows": [],
            "summary": "missing graph evidence packet",
        }

    packet: dict[str, Any] | None = None
    selected_key = packet_key or ""
    if selected_key:
        nested = source.get(selected_key)
        if isinstance(nested, dict) and nested:
            packet = nested
        else:
            pp_meta = source.get("proof_pool_metadata")
            if isinstance(pp_meta, dict):
                nested = pp_meta.get(selected_key)
                if isinstance(nested, dict) and nested:
                    packet = nested
    else:
        nested = source.get("selected_graph_evidence_plan")
        if isinstance(nested, dict) and nested:
            packet = nested
        if packet is None:
            nested = source.get("headline_positioning_section_packet")
            if isinstance(nested, dict) and nested:
                packet = nested
        if packet is None:
            nested = source.get("competency_capability_section_packet")
            if isinstance(nested, dict) and nested:
                packet = nested
        if packet is None and (
            source.get("facts")
            or source.get("competency_bundles")
            or source.get("headline_positioning_bundles")
        ):
            packet = source

    if not isinstance(packet, dict) or not packet:
        return {
            "schema": "graph_evidence_depth_report_v2",
            "section_id": section_id,
            "packet_key": selected_key,
            "packet_shape": "missing",
            "item_count": 0,
            "rich_item_count": 0,
            "unique_skill_count": 0,
            "unique_detail_count": 0,
            "item_rich_ratio": 0.0,
            "skill_diversity_ratio": 0.0,
            "detail_diversity_ratio": 0.0,
            "semantic_coverage_pct": 0.0,
            "axis_coverage_pct": 0.0,
            "minimum_coverage_pct": 0.0,
            "status": "missing",
            "thin_item_ids": [],
            "items": [],
            "weakest_link": None,
            "category_graph_confidence": 0.0,
            "claim_ledger_confidence": 0.0,
            "proof_authority_score": 0.0,
            "targeting_fit_score": 0.0,
            "support_ratio": {
                "items_with_fact_support": 0,
                "items_with_skill_support": 0,
                "items_total": 0,
            },
            "penalties": {
                "metric_reuse_penalty": 0.0,
                "vendor_overfit_penalty": 0.0,
                "generic_label_penalty": 0.0,
            },
            "term_confidence_rows": [],
            "summary": "selected graph evidence packet missing",
        }

    if packet.get("facts"):
        packet_shape = "facts"
        raw_items = [row for row in (packet.get("facts") or []) if isinstance(row, dict)]
    elif packet.get("competency_bundles"):
        packet_shape = "bundles"
        raw_items = [row for row in (packet.get("competency_bundles") or []) if isinstance(row, dict)]
    elif packet.get("headline_positioning_bundles"):
        packet_shape = "bundles"
        raw_items = [row for row in (packet.get("headline_positioning_bundles") or []) if isinstance(row, dict)]
    else:
        packet_shape = "unknown"
        raw_items = []

    item_rows = [
        _graph_evidence_depth_row(item, section_id=section_id, packet_shape=packet_shape)
        for item in raw_items
    ]
    minimum_coverage_pct = 0.8
    detail_ids: list[str] = []
    for row in item_rows:
        if packet_shape == "facts":
            detail_ids.extend(str(x) for x in (row.get("metric_ids") or []) if str(x).strip())
        else:
            detail_ids.extend(str(x) for x in (row.get("linked_fact_ids") or []) if str(x).strip())
    detail_frequency = Counter(detail_ids)
    rich_item_count = sum(1 for row in item_rows if row["rich"])
    item_count = len(item_rows)
    unique_skill_ids = sorted({sid for row in item_rows for sid in row.get("skill_ids") or [] if sid})
    if packet_shape == "facts":
        unique_detail_ids = sorted({mid for row in item_rows for mid in row.get("metric_ids") or [] if mid})
        detail_label = "metrics"
    else:
        unique_detail_ids = sorted(
            {fid for row in item_rows for fid in row.get("linked_fact_ids") or row.get("source_fact_ids") or [] if fid}
        )
        detail_label = "linked_facts"
    item_rich_ratio = round(rich_item_count / item_count, 4) if item_count else 0.0
    skill_diversity_ratio = round(min(len(unique_skill_ids) / item_count, 1.0), 4) if item_count else 0.0
    detail_diversity_ratio = round(min(len(unique_detail_ids) / item_count, 1.0), 4) if item_count else 0.0
    detail_occurrence_count = len(detail_ids)
    detail_reuse_count = max(detail_occurrence_count - len(unique_detail_ids), 0)
    detail_reuse_ratio = round(detail_reuse_count / detail_occurrence_count, 4) if detail_occurrence_count else 0.0
    max_detail_frequency = max(detail_frequency.values()) if detail_frequency else 0
    repeated_detail_ids = sorted(
        [detail_id for detail_id, count in detail_frequency.items() if count > 1]
    )
    top_detail_frequencies = [
        {"detail_id": detail_id, "count": count}
        for detail_id, count in sorted(
            detail_frequency.items(),
            key=lambda item: (-item[1], item[0]),
        )[:5]
    ]
    semantic_coverage_pct = round(
        min(item_rich_ratio, skill_diversity_ratio, detail_diversity_ratio) if item_count else 0.0,
        4,
    )
    axis_coverage_pct = round((skill_diversity_ratio + detail_diversity_ratio) / 2, 4) if item_count else 0.0
    jd_text = str(source.get("jd_text") or source.get("target_jd_text") or packet.get("jd_text") or "")
    briefing_text = str(source.get("briefing") or source.get("briefing_text") or packet.get("briefing_text") or "")
    term_confidence_rows = [
        _rank_depth_row_weakness(
            row,
            packet_shape=packet_shape,
            detail_frequency=detail_frequency,
            jd_text=jd_text,
            briefing_text=briefing_text,
        )
        for row in item_rows
    ]
    ranked_weakness_rows = sorted(
        term_confidence_rows,
        key=lambda row: (-float(row.get("weakness_score") or 0.0), str(row.get("item_id") or "")),
    )
    weakest_link = ranked_weakness_rows[0] if ranked_weakness_rows else None
    items_with_skill_support = sum(1 for row in item_rows if row.get("skill_ids"))
    items_with_fact_support = sum(1 for row in item_rows if _row_detail_ids(row, packet_shape=packet_shape))
    support_ratio = {
        "items_with_fact_support": items_with_fact_support,
        "items_with_skill_support": items_with_skill_support,
        "items_total": item_count,
    }
    metric_reuse_penalty = _unit_float(detail_reuse_ratio)
    vendor_overfit_penalty = _unit_float(
        max((row["components"]["vendor_overfit_penalty"] for row in term_confidence_rows), default=0.0)
    )
    generic_label_penalty = _unit_float(1.0 - item_rich_ratio)
    category_graph_confidence = _unit_float(
        (item_rich_ratio * 0.35)
        + (skill_diversity_ratio * 0.25)
        + (detail_diversity_ratio * 0.25)
        - (metric_reuse_penalty * 0.10)
        - (vendor_overfit_penalty * 0.05)
    )
    claim_ledger_confidence = category_graph_confidence
    proof_authority_score = _unit_float(
        (semantic_coverage_pct * 0.60)
        + (axis_coverage_pct * 0.40)
        - (metric_reuse_penalty * 0.20)
        - (vendor_overfit_penalty * 0.10)
    )
    targeting_scores = [
        max(
            _token_overlap_score(str(row.get("label") or ""), jd_text),
            _token_overlap_score(str(row.get("label") or ""), briefing_text),
        )
        for row in item_rows
    ]
    targeting_fit_score = _unit_float(sum(targeting_scores) / len(targeting_scores)) if targeting_scores else 0.0
    thin_rows = [row for row in item_rows if not row["rich"]]
    status = (
        "judge_grade"
        if item_count and not thin_rows and semantic_coverage_pct >= minimum_coverage_pct
        else ("missing" if not item_count else "insufficient_depth")
    )
    summary = (
        f"{section_id}: {rich_item_count}/{item_count} rich items, "
        f"{len(unique_skill_ids)} unique skills, {len(unique_detail_ids)} unique {detail_label}, "
        f"{semantic_coverage_pct:.0%} semantic coverage, {axis_coverage_pct:.0%} axis coverage"
    )
    return {
        "schema": "graph_evidence_depth_report_v2",
        "section_id": section_id,
        "packet_key": selected_key or ("selected_graph_evidence_plan" if packet_shape == "facts" else ""),
        "packet_shape": packet_shape,
        "item_count": item_count,
        "rich_item_count": rich_item_count,
        "unique_skill_count": len(unique_skill_ids),
        "unique_detail_count": len(unique_detail_ids),
        "detail_occurrence_count": detail_occurrence_count,
        "detail_reuse_count": detail_reuse_count,
        "detail_reuse_ratio": detail_reuse_ratio,
        "max_detail_frequency": max_detail_frequency,
        "repeated_detail_ids": repeated_detail_ids,
        "top_detail_frequencies": top_detail_frequencies,
        "item_rich_ratio": item_rich_ratio,
        "skill_diversity_ratio": skill_diversity_ratio,
        "detail_diversity_ratio": detail_diversity_ratio,
        "semantic_coverage_pct": semantic_coverage_pct,
        "axis_coverage_pct": axis_coverage_pct,
        "minimum_coverage_pct": minimum_coverage_pct,
        "status": status,
        "thin_item_ids": [str(row["item_id"]) for row in thin_rows],
        "items": item_rows,
        "weakest_link": weakest_link,
        "category_graph_confidence": category_graph_confidence,
        "claim_ledger_confidence": claim_ledger_confidence,
        "proof_authority_score": proof_authority_score,
        "targeting_fit_score": targeting_fit_score,
        "support_ratio": support_ratio,
        "penalties": {
            "metric_reuse_penalty": metric_reuse_penalty,
            "vendor_overfit_penalty": vendor_overfit_penalty,
            "generic_label_penalty": generic_label_penalty,
        },
        "term_confidence_rows": term_confidence_rows,
        "summary": summary,
    }


def _graph_evidence_depth_snapshot(report: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(report, dict) or not report:
        return {}
    snapshot: dict[str, Any] = {}
    for key in (
        "schema",
        "section_id",
        "packet_key",
        "packet_shape",
        "status",
        "summary",
        "item_count",
        "rich_item_count",
        "unique_skill_count",
        "unique_detail_count",
        "detail_occurrence_count",
        "detail_reuse_count",
        "detail_reuse_ratio",
        "item_rich_ratio",
        "skill_diversity_ratio",
        "detail_diversity_ratio",
        "semantic_coverage_pct",
        "axis_coverage_pct",
        "minimum_coverage_pct",
        "thin_item_ids",
        "weakest_link",
        "max_detail_frequency",
        "repeated_detail_ids",
        "top_detail_frequencies",
        "category_graph_confidence",
        "claim_ledger_confidence",
        "proof_authority_score",
        "targeting_fit_score",
        "support_ratio",
        "penalties",
        "term_confidence_rows",
    ):
        if key in report:
            value = report.get(key)
            snapshot[key] = list(value) if isinstance(value, tuple) else value
    return snapshot


def build_graph_evidence_depth_comparison_report(
    *,
    section_id: str,
    pre_report: dict[str, Any] | None,
    post_report: dict[str, Any] | None,
    fix_label: str = "post_fix",
) -> dict[str, Any]:
    pre_snapshot = _graph_evidence_depth_snapshot(pre_report)
    post_snapshot = _graph_evidence_depth_snapshot(post_report)

    pre_item_count = int(pre_snapshot.get("item_count") or 0)
    post_item_count = int(post_snapshot.get("item_count") or 0)
    pre_rich_item_count = int(pre_snapshot.get("rich_item_count") or 0)
    post_rich_item_count = int(post_snapshot.get("rich_item_count") or 0)
    pre_thin_item_count = len(pre_snapshot.get("thin_item_ids") or [])
    post_thin_item_count = len(post_snapshot.get("thin_item_ids") or [])
    pre_item_rich_ratio = float(pre_snapshot.get("item_rich_ratio") or 0.0)
    post_item_rich_ratio = float(post_snapshot.get("item_rich_ratio") or 0.0)
    pre_semantic_coverage = float(pre_snapshot.get("semantic_coverage_pct") or 0.0)
    post_semantic_coverage = float(post_snapshot.get("semantic_coverage_pct") or 0.0)
    pre_axis_coverage = float(pre_snapshot.get("axis_coverage_pct") or 0.0)
    post_axis_coverage = float(post_snapshot.get("axis_coverage_pct") or 0.0)
    pre_detail_reuse_ratio = float(pre_snapshot.get("detail_reuse_ratio") or 0.0)
    post_detail_reuse_ratio = float(post_snapshot.get("detail_reuse_ratio") or 0.0)

    delta = {
        "item_count": post_item_count - pre_item_count,
        "rich_item_count": post_rich_item_count - pre_rich_item_count,
        "thin_item_count": post_thin_item_count - pre_thin_item_count,
        "unique_skill_count": int(post_snapshot.get("unique_skill_count") or 0)
        - int(pre_snapshot.get("unique_skill_count") or 0),
        "unique_detail_count": int(post_snapshot.get("unique_detail_count") or 0)
        - int(pre_snapshot.get("unique_detail_count") or 0),
        "detail_occurrence_count": int(post_snapshot.get("detail_occurrence_count") or 0)
        - int(pre_snapshot.get("detail_occurrence_count") or 0),
        "detail_reuse_count": int(post_snapshot.get("detail_reuse_count") or 0)
        - int(pre_snapshot.get("detail_reuse_count") or 0),
        "max_detail_frequency": int(post_snapshot.get("max_detail_frequency") or 0)
        - int(pre_snapshot.get("max_detail_frequency") or 0),
        "item_rich_ratio_pp": round((post_item_rich_ratio - pre_item_rich_ratio) * 100, 2),
        "semantic_coverage_pp": round((post_semantic_coverage - pre_semantic_coverage) * 100, 2),
        "axis_coverage_pp": round((post_axis_coverage - pre_axis_coverage) * 100, 2),
        "detail_reuse_ratio_pp": round((post_detail_reuse_ratio - pre_detail_reuse_ratio) * 100, 2),
    }
    summary = (
        f"{section_id}: {pre_rich_item_count}/{pre_item_count} rich items -> "
        f"{post_rich_item_count}/{post_item_count} rich items; "
        f"thin items {pre_thin_item_count} -> {post_thin_item_count}; "
        f"semantic coverage {pre_semantic_coverage:.0%} -> {post_semantic_coverage:.0%}; "
        f"detail reuse {pre_detail_reuse_ratio:.0%} -> {post_detail_reuse_ratio:.0%}"
    )
    return {
        "schema": "graph_evidence_depth_comparison_report_v1",
        "section_id": section_id,
        "fix_label": fix_label,
        "pre_fix_report": pre_snapshot,
        "post_fix_report": post_snapshot,
        "delta": delta,
        "summary": summary,
        "status_transition": f"{pre_snapshot.get('status') or 'unknown'}->{post_snapshot.get('status') or 'unknown'}",
        "improved": (
            post_thin_item_count < pre_thin_item_count
            or post_semantic_coverage > pre_semantic_coverage
            or post_item_rich_ratio > pre_item_rich_ratio
        ),
    }


def require_graph_evidence_depth(
    source: dict[str, Any] | None,
    *,
    section_id: str,
    packet_key: str | None = None,
) -> dict[str, Any]:
    report = build_graph_evidence_depth_report(source, section_id=section_id, packet_key=packet_key)
    minimum = float(report.get("minimum_coverage_pct") or 0.0)
    if report.get("status") != "judge_grade" or float(report.get("semantic_coverage_pct") or 0.0) < minimum:
        thin = ", ".join(report.get("thin_item_ids") or [])
        weakest = report.get("weakest_link") or {}
        raise ValueError(
            f"{section_id}: evidence depth insufficient for SVP level; "
            f"{report.get('summary')} thin_items=[{thin}] weakest_link={weakest!r}"
        )
    return report


def plan_fact_to_employment_bullet_row(plan_fact: dict[str, Any]) -> dict[str, Any]:
    """Map selected evidence plan facts to the section bullet-row shape."""
    fid = str(plan_fact.get("fact_id") or "").strip()
    mr = str(plan_fact.get("metric_raw") or "").strip()
    technologies = plan_fact.get("technologies")
    if not isinstance(technologies, list):
        technologies = []
    source_emp = str(plan_fact.get("source_employment") or plan_fact.get("employer") or "Graph Evidence").strip()
    return {
        "fact_id": fid,
        "claim_text": str(plan_fact.get("claim_text") or ""),
        "source_employment": source_emp,
        "has_metric": bool(mr),
        "metric_raw": mr,
        "domain": str(plan_fact.get("domain") or ""),
        "technologies": technologies,
    }


def graph_only_proof_pool_metadata(
    *,
    section_id: str,
    candidate_fact_pool_count: int,
    allowed_fact_ids_count: int,
    graph_ref: str,
    legacy_ledger_ref: str = "",
) -> dict[str, Any]:
    n = int(allowed_fact_ids_count)
    out: dict[str, Any] = {
        "proof_pool_type": "augmented_skills_graph",
        "selected_role_fact_set_used": False,
        "base_resume_claim_authority": False,
        "graph_only_claim_authority": True,
        "graph_evidence_plan_used": True,
        "section_id": section_id,
        "candidate_fact_pool_count": int(candidate_fact_pool_count),
        "allowed_fact_ids_count": n,
        "fallback_used": False,
        "fallback_reason": "",
        "c03_graphrag_bound_required": True,
    }
    if legacy_ledger_ref:
        out["claim_evidence_substrate_ref"] = legacy_ledger_ref
        out["legacy_skills_ledger_ref"] = legacy_ledger_ref
        out["legacy_skills_ledger_role"] = "deprecated_reference"
    if graph_ref:
        out["graph_ref"] = graph_ref
    return out


def _ledger_root_fact_ids_union(claim_ledger: list[Any] | None) -> set[str]:
    ids: set[str] = set()
    for row in claim_ledger or []:
        if not isinstance(row, dict):
            continue
        for fid in row.get("source_fact_ids") or []:
            ids.add(str(fid).split("_metric_")[0])
    return ids


def compute_claim_ledger_union_matches_required_fact_ids(
    selected_fact_plan: dict[str, Any] | None,
    claim_ledger: list[Any] | None,
) -> bool | None:
    if not isinstance(selected_fact_plan, dict):
        return None
    req = {
        str(x).split("_metric_")[0]
        for x in (selected_fact_plan.get("required_fact_ids") or [])
        if str(x).strip()
    }
    ledger = _ledger_root_fact_ids_union(claim_ledger)
    if not req:
        return False
    return req == ledger


def _out_of_pool_from_active_gate(active_gate: dict[str, Any] | None) -> list[str]:
    if active_gate is None:
        return []
    ov = active_gate.get("observed_value")
    if not isinstance(ov, dict):
        return []
    oos = ov.get("out_of_slice_fact_ids") or ov.get("out_of_pool_fact_ids")
    if not isinstance(oos, list):
        return []
    return [str(x) for x in oos]


def normalized_graph_evidence_reporting_fields(
    *,
    section_id: str,
    runtime_payload: dict[str, Any],
    x2_gates: list[dict[str, Any]],
    selected_fact_plan: dict[str, Any] | None,
    claim_ledger: list[Any] | None,
) -> dict[str, Any]:
    """Flat active graph evidence fields for section_metric_receipt."""
    from apps_rg.runtime.product_evidence_authority import product_authority_reporting_fields

    pp = dict(runtime_payload.get("proof_pool_metadata") or {})
    req_ids = (selected_fact_plan or {}).get("required_fact_ids") if isinstance(selected_fact_plan, dict) else None
    req_count = len(req_ids or []) if isinstance(req_ids, list) else 0
    out = product_authority_reporting_fields(
        section_id=section_id,
        proof_pool_metadata=pp,
        allowed_fact_ids_count=int(pp.get("allowed_fact_ids_count") or 0),
        required_fact_ids_count=req_count,
    )
    out["claim_ledger_union_matches_required_fact_ids"] = compute_claim_ledger_union_matches_required_fact_ids(
        selected_fact_plan if isinstance(selected_fact_plan, dict) else None,
        claim_ledger,
    )
    for key, value in pp.items():
        key_str = str(key)
        if not (key_str.endswith("_report") and "depth" in key_str):
            continue
        if isinstance(value, dict) and value:
            out[key_str] = dict(value)
    active_gate_id = f"x2_{section_id}_active_proof_pool_source_fact_ids"
    active_gate = next((g for g in x2_gates if g.get("gate_id") == active_gate_id), None)
    if active_gate is not None:
        out["x2_active_proof_pool_gate_status"] = "PASS" if active_gate.get("pass") else "FAIL"
        out["out_of_pool_fact_ids"] = _out_of_pool_from_active_gate(active_gate)
    if bool(pp.get("fallback_used")):
        out["fallback_used"] = True
        out["fallback_reason"] = str(pp.get("fallback_reason") or "")
    return out


def merge_graph_evidence_reporting_into_dict(
    receipt: dict[str, Any],
    *,
    section_id: str,
    runtime_payload: dict[str, Any],
    x2_gates: list[dict[str, Any]],
    selected_fact_plan: dict[str, Any] | None,
    claim_ledger: list[Any] | None,
) -> None:
    receipt.update(
        normalized_graph_evidence_reporting_fields(
            section_id=section_id,
            runtime_payload=runtime_payload,
            x2_gates=x2_gates,
            selected_fact_plan=selected_fact_plan,
            claim_ledger=claim_ledger,
        )
    )
    from apps_rg.runtime.bindings.section_lane_c0_metrics import (
        merge_c0_metrics_into_section_metric_receipt,
    )

    merge_c0_metrics_into_section_metric_receipt(receipt, runtime_payload)
    art = runtime_payload.get("artifact_dir")
    if art:
        from apps_rg.runtime.evidence.canonical_evidence_digest_chain import (
            DIGEST_CHAIN_ARTIFACT,
            build_canonical_evidence_digest_chain,
            emit_canonical_evidence_digest_chain,
        )

        ad = Path(str(art))
        if (ad / "x2_gate_outputs.json").is_file():
            if not (ad / DIGEST_CHAIN_ARTIFACT).is_file():
                emit_canonical_evidence_digest_chain(ad, section_id=section_id)
            chain = build_canonical_evidence_digest_chain(ad, section_id=section_id)
            receipt["canonical_evidence_set_digest"] = chain.get("c05_canonical_evidence_digest")
            receipt["fec_allowed_fact_ids_digest"] = chain.get("c06_final_evidence_contract_digest")
            receipt["c07_runtime_bound_evidence_digest"] = chain.get("c07_runtime_bound_evidence_digest")
            receipt["pa_c0_slot_digest"] = chain.get("pa_c0_slot_digest")
            receipt["provider_request_allowed_ids_digest"] = chain.get(
                "provider_request_allowed_ids_digest"
            )
            receipt["claim_ledger_source_fact_ids_digest"] = chain.get(
                "claim_ledger_source_fact_ids_digest"
            )
            receipt["x2_active_pool_digest"] = chain.get("x2_active_pool_digest")
            receipt["section_receipt_digest"] = chain.get("section_receipt_digest")
            receipt["canonical_evidence_digest_chain_ref"] = DIGEST_CHAIN_ARTIFACT
            receipt["canonical_evidence_invariants_pass"] = (chain.get("invariants") or {}).get(
                "all_pass"
            )


def is_disallowed_proof_id(fid: str) -> bool:
    """JD/briefing/target/companion-shaped proof tokens and empty IDs are never proofable."""
    from apps_rg.runtime.section_proof.section_input_usage_ledger import (
        _is_forbidden_proof_source_fact_id,
    )

    s = str(fid).strip()
    if not s:
        return False
    su = s.upper().replace(" ", "_")
    if su in ("JD_ONLY", "BRIEFING_ONLY", "TARGET_ONLY", "JOB_DESCRIPTION_ONLY"):
        return True
    bad, _ = _is_forbidden_proof_source_fact_id(s)
    return bad


def collect_source_fact_ids_from_claim_ledger(claim_ledger: Iterable[Any] | None) -> list[str]:
    ids: list[str] = []
    for row in claim_ledger or []:
        if not isinstance(row, dict):
            continue
        for fid in row.get("source_fact_ids") or []:
            ids.append(str(fid))
        if row.get("source_fact_id") is not None:
            ids.append(str(row["source_fact_id"]))
    return ids


def collect_source_fact_ids_from_bullets_and_ledger(
    parsed_output: dict[str, Any] | None,
    claim_ledger: Iterable[Any] | None,
) -> list[str]:
    ids: list[str] = []
    for bullet in (parsed_output or {}).get("bullets") or []:
        if not isinstance(bullet, dict):
            continue
        for fid in bullet.get("source_fact_ids") or []:
            ids.append(str(fid))
    ids.extend(collect_source_fact_ids_from_claim_ledger(claim_ledger))
    return ids


def collect_source_fact_ids_from_competencies_struct(
    competencies: Iterable[Any] | None,
    claim_ledger: Iterable[Any] | None,
) -> list[str]:
    ids = collect_source_fact_ids_from_claim_ledger(claim_ledger)
    for cat in competencies or []:
        if not isinstance(cat, dict):
            continue
        for fid in cat.get("source_fact_ids") or []:
            ids.append(str(fid))
        for term in cat.get("terms") or []:
            if isinstance(term, dict):
                if term.get("source_fact_id") is not None:
                    ids.append(str(term["source_fact_id"]))
                for x in term.get("source_fact_ids") or []:
                    ids.append(str(x))
    return ids


def collect_source_fact_ids_for_section(
    section_id: str,
    *,
    claim_ledger: Iterable[Any] | None = None,
    parsed_output: dict[str, Any] | None = None,
    competencies: Iterable[Any] | None = None,
) -> list[str]:
    if section_id in ("unify_bullets", "ibm_bullets"):
        return collect_source_fact_ids_from_bullets_and_ledger(parsed_output, claim_ledger)
    if section_id == "competencies":
        return collect_source_fact_ids_from_competencies_struct(competencies, claim_ledger)
    return collect_source_fact_ids_from_claim_ledger(claim_ledger)


def validate_source_fact_ids_within_active_pool(
    *,
    collected_ids: list[str],
    allowed_fact_ids: set[str],
) -> tuple[bool, list[str]]:
    bad: list[str] = []
    seen: set[str] = set()
    for raw in collected_ids:
        s = str(raw).strip()
        if not s or s in seen:
            continue
        seen.add(s)
        if is_disallowed_proof_id(s) or s not in allowed_fact_ids:
            bad.append(s)
    return (len(bad) == 0, sorted(set(bad)))


def evaluate_active_pool_source_fact_gate(
    *,
    section_id: str,
    collected_ids: list[str],
    allowed_fact_ids: set[str],
) -> tuple[bool, dict[str, Any], str | None]:
    ok, out_of_pool = validate_source_fact_ids_within_active_pool(
        collected_ids=collected_ids,
        allowed_fact_ids=allowed_fact_ids,
    )
    env: dict[str, Any] = {
        "x2_active_pool_gate_status": ok,
        "out_of_pool_fact_ids": out_of_pool,
        "allowed_fact_ids_count": len(allowed_fact_ids),
        "graph_evidence_plan_used": True,
        "section_id": section_id,
    }
    fail = None if ok else "source_fact_ids outside active proof pool: " + ", ".join(out_of_pool[:48])
    return ok, env, fail


__all__ = [
    "SECTION_KEYS",
    "build_allowed_fact_ids_for_plan_facts",
    "build_graph_evidence_depth_comparison_report",
    "build_graph_evidence_depth_report",
    "build_graph_evidence_runtime_payload",
    "build_selected_graph_evidence_plan",
    "collect_source_fact_ids_for_section",
    "collect_source_fact_ids_from_bullets_and_ledger",
    "collect_source_fact_ids_from_claim_ledger",
    "collect_source_fact_ids_from_competencies_struct",
    "compute_claim_ledger_union_matches_required_fact_ids",
    "evaluate_active_pool_source_fact_gate",
    "graph_only_proof_pool_metadata",
    "is_disallowed_proof_id",
    "merge_graph_evidence_reporting_into_dict",
    "metric_derivative_fact_id",
    "normalized_graph_evidence_reporting_fields",
    "plan_fact_to_employment_bullet_row",
    "require_section_packet",
    "require_graph_evidence_depth",
    "require_selected_graph_evidence_plan",
    "selection_method_for_section",
    "selected_graph_evidence_plan_from_payload",
    "sha16",
    "slice_row_to_plan_fact",
    "validate_source_fact_ids_within_active_pool",
]
