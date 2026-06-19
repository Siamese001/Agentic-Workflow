"""Graph-native role episode selection for apps_rg section proof pools."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from apps_rg.runtime.sections.graph_evidence_contract import (
    build_allowed_fact_ids_for_plan_facts,
    build_graph_evidence_depth_comparison_report,
    build_graph_evidence_depth_report,
    selection_method_for_section,
)
from apps_rg.runtime.sections.executive_summary_briefing import (
    briefing_signal_bonus,
    extract_briefing_signal_packet,
)
from apps_rg.runtime.graph.graph_skill_concentration_policy import (
    build_graph_skill_concentration_policy,
)

_BUNDLE_FILES: tuple[tuple[str, str], ...] = (
    ("unify", "unify_role_episode_bundles.json"),
    ("ibm", "ibm_role_episode_bundles.json"),
    ("insurtech", "insurtech_role_episode_bundles.json"),
    ("ey", "ey_role_episode_bundles.json"),
)

_EMPLOYER_SECTION_LIMITS: dict[str, int] = {
    "unify_bullets": 8,
    "unify_narrative": 8,
    "ibm_bullets": 10,
    "ibm_narrative": 10,
    "insurtech_bullets": 12,
    "insurtech_narrative": 12,
    "ey_bullets": 5,
    "ey_narrative": 5,
}

_SHARED_SECTION_LIMITS: dict[str, int] = {
    "executive_summary": 10,
    "headline": 4,
    "competencies": 8,
}

_SHARED_CROSS_EMPLOYER_ELIGIBILITY: tuple[str, ...] = (
    "executive_summary",
    "headline",
    "competencies",
    "unify_bullets",
    "unify_narrative",
    "ibm_bullets",
    "ibm_narrative",
    "insurtech_bullets",
    "insurtech_narrative",
    "ey_bullets",
    "ey_narrative",
)

_SHARED_SECTION_ELIGIBILITY: dict[str, tuple[str, ...]] = {
    "executive_summary": _SHARED_CROSS_EMPLOYER_ELIGIBILITY,
    "headline": _SHARED_CROSS_EMPLOYER_ELIGIBILITY,
    "competencies": _SHARED_CROSS_EMPLOYER_ELIGIBILITY,
}

_ROLE_EMPLOYER_WEIGHTS: dict[str, dict[str, float]] = {
    "svp_agentic_engineering": {
        "unify": 1.00,
        "ibm": 0.65,
        "insurtech": 0.35,
        "ey": 0.20,
    },
    "ai_partnerships_gtm": {
        "unify": 0.95,
        "ibm": 0.90,
        "insurtech": 0.35,
        "ey": 0.10,
    },
    "insurance_it_strategy": {
        "insurtech": 1.00,
        "ey": 0.70,
        "ibm": 0.55,
        "unify": 0.30,
    },
    "balanced_enterprise_ai": {
        "unify": 0.75,
        "ibm": 0.70,
        "insurtech": 0.55,
        "ey": 0.45,
    },
}

_CAPS_BY_BAND: dict[str, dict[str, tuple[int, int]]] = {
    "executive_summary": {
        "primary": (5, 3),
        "secondary": (3, 2),
        "tertiary": (2, 1),
        "context": (1, 0),
    },
    "headline": {
        "primary": (4, 2),
        "secondary": (3, 1),
        "tertiary": (1, 0),
        "context": (0, 0),
    },
    "competencies": {
        "primary": (5, 2),
        "secondary": (3, 1),
        "tertiary": (2, 1),
        "context": (1, 0),
    },
}

_HEADLINE_FAMILIES_BY_PROFILE: dict[str, tuple[str, ...]] = {
    "svp_agentic_engineering": (
        "svp_engineering_leadership",
        "agentic_ai_platforms",
        "runtime_governance",
        "enterprise_ai_architecture",
    ),
    "ai_partnerships_gtm": (
        "svp_engineering_leadership",
        "platform_productization",
        "distributed_ai_infrastructure",
        "enterprise_ai_architecture",
    ),
    "insurance_it_strategy": (
        "svp_engineering_leadership",
        "regulated_ai_systems",
        "enterprise_ai_architecture",
        "runtime_governance",
    ),
    "balanced_enterprise_ai": (
        "svp_engineering_leadership",
        "enterprise_ai_architecture",
        "distributed_ai_infrastructure",
        "runtime_governance",
    ),
}

_COMPETENCY_FAMILIES_BY_PROFILE: dict[str, tuple[str, ...]] = {
    "svp_agentic_engineering": (
        "agentic_platforms",
        "runtime_governance",
        "retrieval_context_engineering",
        "llmops_reliability",
        "distributed_systems_engineering",
        "platform_productization",
        "partnerships_ecosystem_execution",
        "engineering_leadership",
    ),
    "ai_partnerships_gtm": (
        "platform_productization",
        "partnerships_ecosystem_execution",
        "distributed_systems_engineering",
        "engineering_leadership",
        "cloud_hpc_modernization",
        "data_governance_security",
        "agentic_platforms",
        "runtime_governance",
    ),
    "insurance_it_strategy": (
        "insurance_domain_modernization",
        "data_governance_security",
        "cloud_hpc_modernization",
        "devsecops_delivery_governance",
        "engineering_leadership",
        "distributed_systems_engineering",
        "platform_productization",
        "runtime_governance",
    ),
    "balanced_enterprise_ai": (
        "distributed_systems_engineering",
        "runtime_governance",
        "platform_productization",
        "engineering_leadership",
        "data_governance_security",
        "cloud_hpc_modernization",
        "agentic_platforms",
        "retrieval_context_engineering",
    ),
}


def _load_bundle_doc(repo_root: Path, filename: str) -> dict[str, Any]:
    path = repo_root / "apps_rg" / "fact_inventory" / filename
    return json.loads(path.read_text(encoding="utf-8"))


def _bundle_metric_nodes(doc: dict[str, Any]) -> dict[str, dict[str, Any]]:
    raw = doc.get("metric_outcome_nodes") or {}
    if isinstance(raw, dict):
        return {str(k): v for k, v in raw.items() if isinstance(v, dict)}
    if isinstance(raw, list):
        out: dict[str, dict[str, Any]] = {}
        for row in raw:
            if isinstance(row, dict) and row.get("metric_outcome_id"):
                out[str(row["metric_outcome_id"])] = row
        return out
    return {}


def _infer_target_role_profile(*, target_role: str, jd_text: str, briefing_text: str) -> str:
    blob = f"{target_role}\n{jd_text}\n{briefing_text}".lower()
    insurance_hits = sum(
        1
        for token in (
            "brown & brown",
            "insurance brokerage",
            "insurance",
            "carrier",
            "underwriting",
            "claims",
            "policy administration",
            "guidewire",
            "it strategy",
            "enterprise architecture",
            "innovation incubation",
        )
        if token in blob
    )
    if insurance_hits >= 3:
        return "insurance_it_strategy"

    gtm_hits = sum(
        1
        for token in (
            "partnership",
            "partner",
            "alliance",
            "gtm",
            "go-to-market",
            "co-sell",
            "cosell",
            "hyperscaler",
            "aws partner",
            "revenue",
            "quota",
        )
        if token in blob
    )
    agentic_hits = sum(
        1
        for token in (
            "agentic",
            "multi-agent",
            "graphrag",
            "llm",
            "runtime",
            "orchestration",
            "control plane",
            "svp engineering",
        )
        if token in blob
    )
    if gtm_hits >= 3 and gtm_hits >= agentic_hits:
        return "ai_partnerships_gtm"
    if agentic_hits >= 2:
        return "svp_agentic_engineering"
    if gtm_hits >= 2:
        return "ai_partnerships_gtm"
    return "balanced_enterprise_ai"


def _weight_band(weight: float) -> str:
    if weight >= 0.80:
        return "primary"
    if weight >= 0.55:
        return "secondary"
    if weight >= 0.30:
        return "tertiary"
    return "context"


def _caps_for(*, section_id: str, weight: float) -> tuple[int, int, str]:
    band = _weight_band(weight)
    caps = _CAPS_BY_BAND.get(section_id) or _CAPS_BY_BAND["executive_summary"]
    skill_cap, metric_cap = caps[band]
    return skill_cap, metric_cap, band


def _metric_floor_for_section(section_id: str) -> int:
    if section_id == "competencies":
        return 2
    return 0


def _prefer_novel_metric_ids(
    raw_metric_ids: list[str],
    seen_metric_ids: set[str],
    cap: int,
) -> list[str]:
    if cap <= 0:
        return []
    ordered: list[str] = []
    seen: set[str] = set()
    for metric_id in raw_metric_ids:
        metric_id = str(metric_id).strip()
        if not metric_id or metric_id in seen or metric_id in seen_metric_ids:
            continue
        ordered.append(metric_id)
        seen.add(metric_id)
        if len(ordered) >= cap:
            return ordered
    for metric_id in raw_metric_ids:
        metric_id = str(metric_id).strip()
        if not metric_id or metric_id in seen:
            continue
        ordered.append(metric_id)
        seen.add(metric_id)
        if len(ordered) >= cap:
            break
    return ordered[:cap]


def _allocate_employer_root_budgets(
    *,
    candidates_by_employer: dict[str, list[tuple[float, str, dict[str, Any], dict[str, dict[str, Any]]]]],
    employer_weights: dict[str, float],
    max_items: int,
) -> dict[str, int]:
    active = {
        emp: employer_weights.get(emp, 0.0)
        for emp in candidates_by_employer
        if candidates_by_employer.get(emp) and employer_weights.get(emp, 0.0) > 0.0
    }
    if not active:
        return {}
    total = sum(active.values())
    exact = {emp: (w / total) * max_items for emp, w in active.items()}
    budgets: dict[str, int] = {}
    for emp, value in exact.items():
        floor = int(math.floor(value))
        if floor == 0 and active[emp] >= 0.30 and max_items >= len(active):
            floor = 1
        budgets[emp] = min(floor, len(candidates_by_employer.get(emp) or []))
    remaining = max_items - sum(budgets.values())
    if remaining > 0:
        ranked = sorted(
            active,
            key=lambda emp: (
                -(exact[emp] - math.floor(exact[emp])),
                -active[emp],
                emp,
            ),
        )
        while remaining > 0:
            changed = False
            for emp in ranked:
                if remaining <= 0:
                    break
                available = len(candidates_by_employer.get(emp) or [])
                if budgets.get(emp, 0) >= available:
                    continue
                budgets[emp] = budgets.get(emp, 0) + 1
                remaining -= 1
                changed = True
            if not changed:
                break
    return {emp: n for emp, n in budgets.items() if n > 0}


def _token_score(
    bundle: dict[str, Any],
    *,
    target_role: str,
    jd_text: str,
    briefing_text: str,
    briefing_signal_packet: dict[str, Any] | None = None,
) -> float:
    target_blob = f"{target_role}\n{jd_text}\n{briefing_text}".lower()
    bundle_blob = " ".join(
        [
            str(bundle.get("role_episode_bundle_id") or ""),
            str(bundle.get("bundle_theme") or ""),
            str(bundle.get("claim_text") or ""),
            " ".join(str(x) for x in (bundle.get("executive_scope_signals") or [])),
            " ".join(str(x) for x in (bundle.get("architecture_scope_signals") or [])),
            " ".join(str(x) for x in (bundle.get("graph_skill_node_ids") or [])),
            " ".join(str(x) for x in (bundle.get("linked_metric_outcome_ids") or [])),
            str(bundle.get("operating_context") or ""),
        ]
    ).lower()
    score = 0.0
    for token in (
        "agentic",
        "graphrag",
        "multi-agent",
        "ai",
        "aws",
        "cloud",
        "insurance",
        "policy",
        "underwriting",
        "claims",
        "data",
        "platform",
        "gtm",
        "partnership",
        "modernization",
        "governance",
        "risk",
        "regulatory",
    ):
        if token in target_blob and token in bundle_blob:
            score += 1.0
    score += min(len(bundle.get("linked_metric_outcome_ids") or []), 4) * 0.05
    packet = briefing_signal_packet or extract_briefing_signal_packet(briefing_text)
    score += briefing_signal_bonus(
        packet,
        bundle_blob=bundle_blob,
        target_blob=target_blob,
    )
    return score


def _eligible_bundle(
    bundle: dict[str, Any],
    *,
    section_id: str,
) -> bool:
    eligibility = tuple(str(x) for x in (bundle.get("section_eligibility") or []))
    if section_id in _SHARED_SECTION_ELIGIBILITY:
        allowed = set(_SHARED_SECTION_ELIGIBILITY[section_id])
        return bool(allowed.intersection(eligibility))
    return section_id in eligibility


def _claim_text(bundle: dict[str, Any]) -> str:
    claim = str(bundle.get("claim_text") or "").strip()
    if claim:
        return claim
    signals = [str(x).strip() for x in (bundle.get("executive_scope_signals") or []) if str(x).strip()]
    if signals:
        return signals[0]
    return str(bundle.get("bundle_theme") or bundle.get("role_episode_bundle_id") or "").strip()


def _metric_values(metric_ids: list[str], metric_nodes: dict[str, dict[str, Any]]) -> list[str]:
    values: list[str] = []
    for metric_id in metric_ids:
        node = metric_nodes.get(metric_id) or {}
        label = str(node.get("metric") or node.get("claim_text") or metric_id).strip()
        if label:
            values.append(label)
    return values


def _bundle_to_fact(
    bundle: dict[str, Any],
    *,
    employer_lane: str,
    metric_nodes: dict[str, dict[str, Any]],
    selected_skill_ids: list[str],
    selected_metric_ids: list[str],
) -> dict[str, Any]:
    bundle_id = str(bundle.get("role_episode_bundle_id") or "").strip()
    allowed_graph_ids = [bundle_id, *selected_skill_ids, *selected_metric_ids]
    return {
        "fact_id": bundle_id,
        "candidate_fact_id": bundle_id,
        "claim_text": _claim_text(bundle),
        "role_episode_bundle_id": bundle_id,
        "graph_evidence_type": "role_episode_bundle",
        "employer": str(bundle.get("employer") or ""),
        "employer_lane": employer_lane,
        "employer_node_id": str(bundle.get("employer_node_id") or ""),
        "source_employment": str(bundle.get("employer") or ""),
        "graph_skill_node_ids": selected_skill_ids,
        "metric_outcome_ids": selected_metric_ids,
        "selected_metric_ids": selected_metric_ids,
        "allowed_graph_evidence_ids": allowed_graph_ids,
        "linked_identity_fact_ids": [str(x) for x in (bundle.get("linked_source_fact_ids") or [])],
        "source_fact_ids": [bundle_id],
        "confidence": str(bundle.get("support_level") or "HIGH"),
        "support_level": str(bundle.get("support_level") or "approved_by_graph_presence"),
        "verification_status": "approved_by_graph_presence",
        "metric_values": _metric_values(selected_metric_ids, metric_nodes),
        "technologies": selected_skill_ids,
        "domain": str(bundle.get("bundle_theme") or ""),
    }


def build_selected_graph_evidence_plan_for_section(
    *,
    repo_root: Path,
    section_id: str,
    target_role: str = "",
    jd_text: str = "",
    briefing_text: str = "",
    limit: int | None = None,
) -> tuple[dict[str, Any], list[str], set[str]]:
    """Select graph role episode evidence and return a selected evidence plan."""
    candidates: list[tuple[float, str, dict[str, Any], dict[str, dict[str, Any]]]] = []
    raw_skill_counts_by_employer: dict[str, int] = {}
    raw_metric_counts_by_employer: dict[str, int] = {}
    briefing_signal_packet = extract_briefing_signal_packet(briefing_text)
    for employer_lane, filename in _BUNDLE_FILES:
        doc = _load_bundle_doc(repo_root, filename)
        metric_nodes = _bundle_metric_nodes(doc)
        for bundle in doc.get("bundles") or []:
            if not isinstance(bundle, dict):
                continue
            bundle_id = str(bundle.get("role_episode_bundle_id") or "").strip()
            if not bundle_id or not _eligible_bundle(bundle, section_id=section_id):
                continue
            score = _token_score(
                bundle,
                target_role=target_role,
                jd_text=jd_text,
                briefing_text=briefing_text,
                briefing_signal_packet=briefing_signal_packet,
            )
            candidates.append((score, employer_lane, bundle, metric_nodes))
            raw_skill_counts_by_employer[employer_lane] = raw_skill_counts_by_employer.get(employer_lane, 0) + len(
                bundle.get("graph_skill_node_ids") or []
            )
            raw_metric_counts_by_employer[employer_lane] = raw_metric_counts_by_employer.get(employer_lane, 0) + len(
                bundle.get("linked_metric_outcome_ids") or []
            )

    if not candidates:
        raise ValueError(f"selected graph evidence plan produced empty bundle set for {section_id!r}")

    target_role_profile = _infer_target_role_profile(
        target_role=target_role,
        jd_text=jd_text,
        briefing_text=briefing_text,
    )
    briefing_signal_packet = {
        **briefing_signal_packet,
        "role_family_key": target_role_profile,
    }
    employer_weights = dict(_ROLE_EMPLOYER_WEIGHTS[target_role_profile])

    candidates_by_employer: dict[str, list[tuple[float, str, dict[str, Any], dict[str, dict[str, Any]]]]] = {}
    for row in candidates:
        candidates_by_employer.setdefault(row[1], []).append(row)
    for rows in candidates_by_employer.values():
        rows.sort(
            key=lambda row: (
                -row[0],
                str(row[2].get("role_episode_bundle_id") or ""),
            )
        )
    max_items = int(limit or _EMPLOYER_SECTION_LIMITS.get(section_id) or _SHARED_SECTION_LIMITS.get(section_id) or 8)
    if section_id in _SHARED_SECTION_LIMITS:
        budgets = _allocate_employer_root_budgets(
            candidates_by_employer=candidates_by_employer,
            employer_weights=employer_weights,
            max_items=max_items,
        )
        selected: list[tuple[float, str, dict[str, Any], dict[str, dict[str, Any]]]] = []
        for employer_lane in sorted(budgets, key=lambda emp: (-employer_weights.get(emp, 0.0), emp)):
            selected.extend(candidates_by_employer.get(employer_lane, [])[: budgets[employer_lane]])
        selected.sort(
            key=lambda row: (
                -employer_weights.get(row[1], 0.0),
                -row[0],
                row[1],
                str(row[2].get("role_episode_bundle_id") or ""),
            )
        )
    else:
        budgets = {}
        candidates.sort(
            key=lambda row: (
                -row[0],
                row[1],
                str(row[2].get("role_episode_bundle_id") or ""),
            )
        )
        selected = candidates[:max_items]

    facts: list[dict[str, Any]] = []
    pre_facts: list[dict[str, Any]] = []
    skill_caps_by_root: dict[str, int] = {}
    metric_caps_by_root: dict[str, int] = {}
    metric_caps_by_root_before_floor: dict[str, int] = {}
    root_weight_bands: dict[str, str] = {}
    employer_root_weights: dict[str, float] = {}
    selected_skills: list[dict[str, Any]] = []
    selected_metrics_detail: list[dict[str, Any]] = []
    selected_skill_counts_by_employer: dict[str, int] = {}
    selected_metric_counts_by_employer: dict[str, int] = {}
    selected_metric_counts_by_employer_before_floor: dict[str, int] = {}
    excluded_due_to_root_cap: list[dict[str, Any]] = []
    excluded_due_to_metric_cap: list[dict[str, Any]] = []
    selected_metric_ids_seen: set[str] = set()

    for score, employer_lane, bundle, metric_nodes in selected:
        bundle_id = str(bundle.get("role_episode_bundle_id") or "").strip()
        weight = employer_weights.get(employer_lane, 0.0)
        skill_cap, metric_cap, band = _caps_for(section_id=section_id, weight=weight)
        raw_skill_ids = [str(x).strip() for x in (bundle.get("graph_skill_node_ids") or []) if str(x).strip()]
        raw_metric_ids = [str(x).strip() for x in (bundle.get("linked_metric_outcome_ids") or []) if str(x).strip()]
        metric_floor = _metric_floor_for_section(section_id)
        effective_metric_cap = min(len(raw_metric_ids), max(metric_cap, metric_floor)) if raw_metric_ids else 0
        selected_skill_ids = raw_skill_ids[:skill_cap] if skill_cap > 0 else []
        selected_metric_ids_before_floor = raw_metric_ids[:metric_cap] if metric_cap > 0 else []
        selected_metric_ids = _prefer_novel_metric_ids(
            raw_metric_ids,
            selected_metric_ids_seen,
            effective_metric_cap,
        )
        skill_caps_by_root[bundle_id] = skill_cap
        metric_caps_by_root_before_floor[bundle_id] = metric_cap
        metric_caps_by_root[bundle_id] = effective_metric_cap
        root_weight_bands[bundle_id] = band
        employer_root_weights[bundle_id] = weight
        selected_skill_counts_by_employer[employer_lane] = (
            selected_skill_counts_by_employer.get(employer_lane, 0) + len(selected_skill_ids)
        )
        selected_metric_counts_by_employer_before_floor[employer_lane] = (
            selected_metric_counts_by_employer_before_floor.get(employer_lane, 0)
            + len(selected_metric_ids_before_floor)
        )
        selected_metric_counts_by_employer[employer_lane] = (
            selected_metric_counts_by_employer.get(employer_lane, 0) + len(selected_metric_ids)
        )
        for sid in selected_skill_ids:
            selected_skills.append(
                {
                    "skill_id": sid,
                    "role_episode_bundle_id": bundle_id,
                    "employer_lane": employer_lane,
                    "root_weight": weight,
                    "root_weight_band": band,
                }
            )
        for mid in selected_metric_ids:
            selected_metric_ids_seen.add(mid)
        for mid in selected_metric_ids:
            node = metric_nodes.get(mid) or {}
            selected_metrics_detail.append(
                {
                    "metric_outcome_id": mid,
                    "role_episode_bundle_id": bundle_id,
                    "employer_lane": employer_lane,
                    "root_weight": weight,
                    "root_weight_band": band,
                    "metric": str(node.get("metric") or node.get("claim_text") or mid),
                }
            )
        pre_facts.append(
            _bundle_to_fact(
                bundle,
                employer_lane=employer_lane,
                metric_nodes=metric_nodes,
                selected_skill_ids=selected_skill_ids,
                selected_metric_ids=selected_metric_ids_before_floor,
            )
        )
        for sid in raw_skill_ids[skill_cap:]:
            excluded_due_to_root_cap.append(
                {
                    "graph_evidence_id": sid,
                    "role_episode_bundle_id": bundle_id,
                    "employer_lane": employer_lane,
                    "cap": skill_cap,
                    "reason": "skill_root_cap",
                }
            )
        for mid in raw_metric_ids[metric_cap:]:
            excluded_due_to_metric_cap.append(
                {
                    "graph_evidence_id": mid,
                    "role_episode_bundle_id": bundle_id,
                    "employer_lane": employer_lane,
                    "cap": metric_cap,
                    "reason": "metric_root_cap",
                }
            )
        facts.append(
            _bundle_to_fact(
                bundle,
                employer_lane=employer_lane,
                metric_nodes=metric_nodes,
                selected_skill_ids=selected_skill_ids,
                selected_metric_ids=selected_metric_ids,
            )
        )

    ordered, allowed = build_allowed_fact_ids_for_plan_facts(facts)
    selected_nodes = [str(f["role_episode_bundle_id"]) for f in facts]
    selected_metrics: list[str] = []
    selected_employers: list[str] = []
    selected_employer_roots: dict[str, list[str]] = {}
    for fact in facts:
        for metric_id in fact.get("metric_outcome_ids") or []:
            if metric_id not in selected_metrics:
                selected_metrics.append(metric_id)
        employer_lane = str(fact.get("employer_lane") or "")
        selected_employer_roots.setdefault(employer_lane, []).append(str(fact["role_episode_bundle_id"]))
        employer = str(fact.get("employer") or "")
        if employer and employer not in selected_employers:
            selected_employers.append(employer)
    selected_skill_ids_all = [str(s["skill_id"]) for s in selected_skills]
    concentration_policy = build_graph_skill_concentration_policy(
        counts=selected_skill_counts_by_employer,
        distribution_kind="employer_lane",
        bucket_ids=tuple(employer_weights.keys()),
        context={
            "section_id": section_id,
            "target_role_profile": target_role_profile,
            "target_role": target_role,
        },
    )
    selected_edges = [
        {
            "edge_type": "role_episode_contains_skill",
            "source": str(item["role_episode_bundle_id"]),
            "target": str(item["skill_id"]),
        }
        for item in selected_skills
    ] + [
        {
            "edge_type": "role_episode_has_metric_outcome",
            "source": str(item["role_episode_bundle_id"]),
            "target": str(item["metric_outcome_id"]),
        }
        for item in selected_metrics_detail
    ]
    pre_depth_report = build_graph_evidence_depth_report({"facts": pre_facts}, section_id=section_id)
    post_depth_report = build_graph_evidence_depth_report({"facts": facts}, section_id=section_id)
    depth_comparison_report = build_graph_evidence_depth_comparison_report(
        section_id=section_id,
        pre_report=pre_depth_report,
        post_report=post_depth_report,
        fix_label="competencies_metric_floor_v1" if section_id == "competencies" else "shared_lane_metric_floor_v1",
    )
    raw_max_emp = max(raw_skill_counts_by_employer, key=raw_skill_counts_by_employer.get)
    selected_max_emp = (
        max(selected_skill_counts_by_employer, key=selected_skill_counts_by_employer.get)
        if selected_skill_counts_by_employer
        else ""
    )
    plan = {
        "section_id": section_id,
        "selection_method": selection_method_for_section(section_id),
        "target_role_profile": target_role_profile,
        "role_family_key": target_role_profile,
        "graph_weight_profile": {
            "profile": target_role_profile,
            "employer_weights": employer_weights,
            "selection_model": "role_weighted_employer_budget_plus_root_caps_v1",
        },
        "selected_employer_roots": selected_employer_roots,
        "employer_root_weights": employer_root_weights,
        "root_weight_bands": root_weight_bands,
        "skill_caps_by_root": skill_caps_by_root,
        "metric_caps_by_root": metric_caps_by_root,
        "selected_nodes": selected_nodes,
        "selected_edges": selected_edges,
        "selected_skills": selected_skills,
        "selected_skill_ids": selected_skill_ids_all,
        "selected_metrics": selected_metrics,
        "selected_metrics_detail": selected_metrics_detail,
        "selected_employer_lanes": selected_employers,
        "selected_employer_lane_ids": [str(f.get("employer_lane") or "") for f in facts],
        "selected_headline_positioning_families": list(
            _HEADLINE_FAMILIES_BY_PROFILE.get(target_role_profile, ())
        ),
        "selected_competency_families": list(
            _COMPETENCY_FAMILIES_BY_PROFILE.get(target_role_profile, ())
        ),
        "briefing_signal_packet": briefing_signal_packet,
        "concentration_policy": concentration_policy,
        "excluded_due_to_root_cap": excluded_due_to_root_cap,
        "excluded_due_to_metric_cap": excluded_due_to_metric_cap,
        "allowed_graph_evidence_ids": ordered,
        "selection_rationale": (
            "Selected graph role episode bundles by section eligibility, target-role profile, "
            "employer/root budgets, and per-root skill/metric caps. JD/briefing steer weighting "
            "only and do not create evidence. Briefing signal packet keeps strategy, operating-model, "
            "leadership, platform, forward-looking, and urgency sections visible to the scorer."
        ),
        "skew_diagnostics": {
            "raw_skill_counts_by_employer": raw_skill_counts_by_employer,
            "raw_metric_counts_by_employer": raw_metric_counts_by_employer,
            "selected_skill_counts_by_employer": selected_skill_counts_by_employer,
            "selected_metric_counts_by_employer_before_floor": selected_metric_counts_by_employer_before_floor,
            "selected_metric_counts_by_employer": selected_metric_counts_by_employer,
            "employer_root_budgets": budgets,
            "max_raw_skill_count_employer": raw_max_emp,
            "max_selected_skill_count_employer": selected_max_emp,
            "selection_normalized_by_employer_root_cap": section_id in _SHARED_SECTION_LIMITS,
            "metric_caps_by_root_before_floor": metric_caps_by_root_before_floor,
            "metric_caps_by_root_after_floor": metric_caps_by_root,
            "thin_item_ids_before_floor": pre_depth_report.get("thin_item_ids") or [],
            "thin_item_ids_after_floor": post_depth_report.get("thin_item_ids") or [],
            "raw_density_dominance_detected": bool((pre_depth_report.get("detail_reuse_ratio") or 0.0) > 0.35),
        },
        "facts": facts,
        "required_fact_ids": [str(f["fact_id"]) for f in facts],
    }
    plan["graph_evidence_depth_pre_report"] = pre_depth_report
    plan["graph_evidence_depth_report"] = post_depth_report
    plan["graph_evidence_depth_post_report"] = post_depth_report
    plan["graph_evidence_depth_comparison_report"] = depth_comparison_report
    plan["graph_evidence_depth_status"] = post_depth_report.get("status")
    plan["graph_evidence_semantic_coverage_pct"] = post_depth_report.get("semantic_coverage_pct")
    return plan, ordered, allowed


__all__ = [
    "build_selected_graph_evidence_plan_for_section",
]
