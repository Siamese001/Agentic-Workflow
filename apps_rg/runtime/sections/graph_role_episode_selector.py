"""Graph-native role-episode selection with pre-target authority and real traversal receipts."""
from __future__ import annotations

import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.augmented_skills_graph import (
    graph_payload_digest,
    graph_version_from_payload,
    load_augmented_skills_graph,
)
from apps_rg.fact_inventory.master_skills_arsenal_ledger import (
    skill_row_eligible_for_external_claim,
)
from apps_rg.runtime.c0.c03_resume_graph_contracts import (
    TraversalRecorder,
    build_candidate_decision,
    build_candidate_receipt,
    evaluate_pretarget_authority,
    finalize_canonical_section_plan,
    stable_digest,
)
from apps_rg.runtime.graph.graph_skill_concentration_policy import (
    build_graph_skill_concentration_policy,
)
from apps_rg.runtime.sections.executive_summary_briefing import (
    briefing_signal_bonus,
    extract_briefing_signal_packet,
)
from apps_rg.runtime.sections.graph_evidence_contract import (
    build_allowed_fact_ids_for_plan_facts,
    build_graph_evidence_depth_comparison_report,
    build_graph_evidence_depth_report,
    selection_method_for_section,
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
_SHARED_SECTION_ELIGIBILITY = {
    "executive_summary": _SHARED_CROSS_EMPLOYER_ELIGIBILITY,
    "headline": _SHARED_CROSS_EMPLOYER_ELIGIBILITY,
    "competencies": _SHARED_CROSS_EMPLOYER_ELIGIBILITY,
}

_ROLE_EMPLOYER_WEIGHTS: dict[str, dict[str, float]] = {
    "svp_agentic_engineering": {"unify": 1.00, "ibm": 0.65, "insurtech": 0.35, "ey": 0.20},
    "ai_partnerships_gtm": {"unify": 0.95, "ibm": 0.90, "insurtech": 0.35, "ey": 0.10},
    "insurance_it_strategy": {"insurtech": 1.00, "ey": 0.70, "ibm": 0.55, "unify": 0.30},
    "balanced_enterprise_ai": {"unify": 0.75, "ibm": 0.70, "insurtech": 0.55, "ey": 0.45},
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
        "partner_applied_ai_architecture",
        "platform_productization",
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
        "partner_applied_ai_architecture",
        "platform_productization",
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

_TARGET_TERMS = (
    "agentic",
    "graphrag",
    "multi agent",
    "llm",
    "runtime",
    "orchestration",
    "control plane",
    "ai",
    "aws",
    "cloud",
    "insurance",
    "brokerage",
    "policy",
    "underwriting",
    "claims",
    "guidewire",
    "data",
    "platform",
    "gtm",
    "partnership",
    "alliance",
    "co sell",
    "modernization",
    "governance",
    "risk",
    "regulatory",
    "revenue",
    "engineering leadership",
)
_WORD_RE = re.compile(r"[a-z0-9]+")


def _load_bundle_doc(repo_root: Path, filename: str) -> dict[str, Any]:
    path = repo_root / "apps_rg" / "fact_inventory" / filename
    import json

    return json.loads(path.read_text(encoding="utf-8"))


def _bundle_metric_nodes(doc: dict[str, Any]) -> dict[str, dict[str, Any]]:
    raw = doc.get("metric_outcome_nodes") or {}
    if isinstance(raw, dict):
        return {str(key): value for key, value in raw.items() if isinstance(value, dict)}
    if isinstance(raw, list):
        return {
            str(row["metric_outcome_id"]): row
            for row in raw
            if isinstance(row, dict) and row.get("metric_outcome_id")
        }
    return {}


def _infer_target_role_profile(*, target_role: str, jd_text: str, briefing_text: str) -> str:
    blob = f"{target_role}\n{jd_text}\n{briefing_text}".lower()
    insurance_hits = sum(
        token in blob
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
    )
    if insurance_hits >= 3:
        return "insurance_it_strategy"
    gtm_hits = sum(
        token in blob
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
    )
    agentic_hits = sum(
        token in blob
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
    return 2 if section_id == "competencies" else 0


def _section_allowed(section_id: str, eligibility: Any) -> bool:
    allowed_values = {str(value) for value in (eligibility or []) if str(value).strip()}
    if section_id in _SHARED_SECTION_ELIGIBILITY:
        return bool(set(_SHARED_SECTION_ELIGIBILITY[section_id]) & allowed_values)
    return section_id in allowed_values


def _allocate_employer_root_budgets(
    *,
    candidates_by_employer: dict[str, list[dict[str, Any]]],
    employer_weights: dict[str, float],
    max_items: int,
) -> dict[str, int]:
    active = {
        employer: employer_weights.get(employer, 0.0)
        for employer, rows in candidates_by_employer.items()
        if rows and employer_weights.get(employer, 0.0) > 0.0
    }
    if not active:
        return {}
    total = sum(active.values())
    exact = {employer: (weight / total) * max_items for employer, weight in active.items()}
    budgets: dict[str, int] = {}
    for employer, value in exact.items():
        floor = int(math.floor(value))
        if floor == 0 and active[employer] >= 0.30 and max_items >= len(active):
            floor = 1
        budgets[employer] = min(floor, len(candidates_by_employer[employer]))
    remaining = max_items - sum(budgets.values())
    ranked = sorted(active, key=lambda employer: (-(exact[employer] - math.floor(exact[employer])), -active[employer], employer))
    while remaining > 0:
        changed = False
        for employer in ranked:
            if remaining <= 0:
                break
            if budgets.get(employer, 0) >= len(candidates_by_employer[employer]):
                continue
            budgets[employer] = budgets.get(employer, 0) + 1
            remaining -= 1
            changed = True
        if not changed:
            break
    return {employer: count for employer, count in budgets.items() if count > 0}


def _normalized_text(value: str) -> str:
    return " ".join(_WORD_RE.findall(str(value or "").casefold().replace("_", " ")))


def _alignment_score(target_blob: str, candidate_blob: str) -> float:
    target = _normalized_text(target_blob)
    candidate = _normalized_text(candidate_blob)
    if not target or not candidate:
        return 0.0
    score = sum(1.0 for term in _TARGET_TERMS if term in target and term in candidate)
    target_words = set(target.split())
    candidate_words = set(candidate.split())
    overlap = len(target_words & candidate_words)
    score += min(overlap, 8) * 0.1
    return round(score, 6)


def _bundle_target_score(
    bundle: dict[str, Any],
    *,
    target_role: str,
    jd_text: str,
    briefing_text: str,
    briefing_signal_packet: dict[str, Any],
) -> float:
    target_blob = f"{target_role}\n{jd_text}\n{briefing_text}"
    bundle_blob = " ".join(
        [
            str(bundle.get("role_episode_bundle_id") or ""),
            str(bundle.get("bundle_theme") or ""),
            str(bundle.get("claim_text") or ""),
            " ".join(str(value) for value in bundle.get("executive_scope_signals") or []),
            " ".join(str(value) for value in bundle.get("architecture_scope_signals") or []),
            str(bundle.get("operating_context") or ""),
        ]
    )
    score = _alignment_score(target_blob, bundle_blob)
    score += briefing_signal_bonus(
        briefing_signal_packet,
        bundle_blob=bundle_blob.lower(),
        target_blob=target_blob.lower(),
    )
    return round(score, 6)


def _confidence_score(value: str) -> float:
    return {"HIGH": 1.0, "MEDIUM": 0.7, "LOW": 0.35, "BLOCKED": 0.0}.get(
        str(value or "").upper(), 0.5
    )


def _skill_proof_strength(row: dict[str, Any]) -> float:
    source_count = len(row.get("fact_id_links") or []) + len(row.get("source_snippets") or [])
    return round(_confidence_score(str(row.get("confidence_grade") or row.get("confidence") or "")) + min(source_count, 4) * 0.1, 6)


def _skill_target_score(row: dict[str, Any], skill_id: str, target_blob: str) -> float:
    candidate_blob = " ".join(
        [
            skill_id,
            str(row.get("label") or row.get("skill_name") or ""),
            str(row.get("pillar") or ""),
            str(row.get("subpillar") or ""),
            " ".join(str(value) for value in row.get("allowed_phrases") or []),
        ]
    )
    return _alignment_score(target_blob, candidate_blob)


def _metric_target_score(node: dict[str, Any], metric_id: str, target_blob: str) -> float:
    candidate_blob = " ".join(
        [
            metric_id,
            str(node.get("metric") or ""),
            str(node.get("claim_text") or ""),
            str(node.get("metric_type") or ""),
            " ".join(str(value) for value in node.get("surface_tokens") or []),
        ]
    )
    return _alignment_score(target_blob, candidate_blob)


def _claim_text(bundle: dict[str, Any]) -> str:
    claim = str(bundle.get("claim_text") or "").strip()
    if claim:
        return claim
    signals = [str(value).strip() for value in bundle.get("executive_scope_signals") or [] if str(value).strip()]
    return signals[0] if signals else str(bundle.get("bundle_theme") or bundle.get("role_episode_bundle_id") or "").strip()


def _metric_values(metric_ids: list[str], metric_nodes: dict[str, dict[str, Any]]) -> list[str]:
    return [
        str((metric_nodes.get(metric_id) or {}).get("metric") or (metric_nodes.get(metric_id) or {}).get("claim_text") or metric_id).strip()
        for metric_id in metric_ids
        if str(metric_id).strip()
    ]


def _bundle_to_fact(
    bundle: dict[str, Any],
    *,
    employer_lane: str,
    metric_nodes: dict[str, dict[str, Any]],
    selected_skill_ids: list[str],
    selected_metric_ids: list[str],
) -> dict[str, Any]:
    bundle_id = str(bundle.get("role_episode_bundle_id") or "").strip()
    linked_source_fact_ids = [str(value).strip() for value in bundle.get("linked_source_fact_ids") or [] if str(value).strip()]
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
        "graph_skill_node_ids": list(selected_skill_ids),
        "metric_outcome_ids": list(selected_metric_ids),
        "selected_metric_ids": list(selected_metric_ids),
        "allowed_graph_evidence_ids": [bundle_id, *selected_skill_ids, *selected_metric_ids],
        "linked_identity_fact_ids": linked_source_fact_ids,
        "linked_source_fact_ids": linked_source_fact_ids,
        "source_fact_ids": [bundle_id],
        "confidence": str(bundle.get("support_level") or "HIGH"),
        "support_level": str(bundle.get("support_level") or "approved_by_graph_presence"),
        "verification_status": "approved_by_graph_presence",
        "metric_values": _metric_values(selected_metric_ids, metric_nodes),
        "technologies": list(selected_skill_ids),
        "domain": str(bundle.get("bundle_theme") or ""),
    }


def _root_authority(bundle: dict[str, Any], *, section_id: str) -> dict[str, Any]:
    return evaluate_pretarget_authority(
        candidate_id=str(bundle.get("role_episode_bundle_id") or ""),
        candidate_type="role_episode_root",
        section_id=section_id,
        section_allowed=_section_allowed(section_id, bundle.get("section_eligibility")),
        activation_status=str(bundle.get("activation_status") or ""),
        support_level=str(bundle.get("support_level") or ""),
        external_claim_policy=str(bundle.get("external_claim_policy") or ""),
        external_eligible=True,
        claim_eligible=True,
        source_refs=bundle.get("linked_source_fact_ids") or [],
        path_present=True,
    )


def _skill_authority(
    *,
    skill_id: str,
    row: dict[str, Any] | None,
    bundle: dict[str, Any],
    section_id: str,
) -> dict[str, Any]:
    skill = row or {}
    source_refs = list(skill.get("fact_id_links") or []) + list(skill.get("source_snippets") or [])
    eligible = bool(row) and skill_row_eligible_for_external_claim(skill)
    return evaluate_pretarget_authority(
        candidate_id=skill_id,
        candidate_type="leaf_skill",
        section_id=section_id,
        section_allowed=_section_allowed(section_id, bundle.get("section_eligibility")),
        activation_status=str(skill.get("activation_status") or ""),
        support_level=str(skill.get("support_level") or ""),
        external_claim_policy=str(skill.get("external_claim_policy") or ""),
        external_eligible=eligible,
        claim_eligible=eligible,
        source_refs=source_refs,
        path_present=skill_id in {str(value) for value in bundle.get("graph_skill_node_ids") or []},
        extra_reason_codes=[] if row else ["missing_skill_authority_row"],
    )


def _metric_authority(
    *,
    metric_id: str,
    node: dict[str, Any] | None,
    bundle: dict[str, Any],
    section_id: str,
) -> dict[str, Any]:
    metric = node or {}
    bindings = {str(value) for value in metric.get("bundle_bindings") or []}
    bundle_id = str(bundle.get("role_episode_bundle_id") or "")
    path_present = bool(node) and (not bindings or bundle_id in bindings)
    approved = bool(metric.get("approved", True)) if node else False
    return evaluate_pretarget_authority(
        candidate_id=metric_id,
        candidate_type="metric_outcome",
        section_id=section_id,
        section_allowed=_section_allowed(section_id, metric.get("section_eligibility") or bundle.get("section_eligibility")),
        support_level=str(metric.get("support_level") or ""),
        external_claim_policy=str(metric.get("external_claim_policy") or ""),
        external_eligible=bool(node),
        claim_eligible=bool(node),
        approved=approved,
        approval_status=str(metric.get("approval_status") or ""),
        source_refs=bundle.get("linked_source_fact_ids") or [],
        path_present=path_present,
        extra_reason_codes=[] if node else ["missing_metric_authority_row"],
    )


def build_selected_graph_evidence_plan_for_section(
    *,
    repo_root: Path,
    section_id: str,
    target_role: str = "",
    jd_text: str = "",
    briefing_text: str = "",
    limit: int | None = None,
) -> tuple[dict[str, Any], list[str], set[str]]:
    """Traverse, authority-filter, rank, and terminally decision graph evidence."""
    graph = load_augmented_skills_graph(repo_root=repo_root)
    graph_digest = graph_payload_digest(graph)
    skill_by_id = {
        str(row.get("skill_id") or ""): row
        for row in graph.get("skill_rows") or []
        if isinstance(row, dict) and row.get("skill_id")
    }
    recorder = TraversalRecorder(section_id=section_id, max_hop_depth=2)
    prepared_roots: list[dict[str, Any]] = []
    raw_skill_counts_by_employer: dict[str, int] = {}
    raw_metric_counts_by_employer: dict[str, int] = {}

    # Pass 1: authority and actual graph walk only. No targeting text is consulted.
    for employer_lane, filename in _BUNDLE_FILES:
        doc = _load_bundle_doc(repo_root, filename)
        metric_nodes = _bundle_metric_nodes(doc)
        for bundle in doc.get("bundles") or []:
            if not isinstance(bundle, dict):
                continue
            bundle_id = str(bundle.get("role_episode_bundle_id") or "").strip()
            if not bundle_id:
                continue
            root_path = f"root:{bundle_id}"
            recorder.record(
                event_type="node_discovered",
                hop_depth=0,
                target_node_id=bundle_id,
                candidate_path_id=root_path,
                metadata={"candidate_type": "role_episode_root", "employer_lane": employer_lane},
            )
            root_auth = _root_authority(bundle, section_id=section_id)
            recorder.record(
                event_type="authority_evaluated",
                hop_depth=0,
                target_node_id=bundle_id,
                candidate_path_id=root_path,
                authority_pass=bool(root_auth["authority_pass"]),
                reason_codes=root_auth["reason_codes"],
            )

            skill_records: list[dict[str, Any]] = []
            raw_skill_ids = sorted({str(value).strip() for value in bundle.get("graph_skill_node_ids") or [] if str(value).strip()})
            raw_skill_counts_by_employer[employer_lane] = raw_skill_counts_by_employer.get(employer_lane, 0) + len(raw_skill_ids)
            for skill_id in raw_skill_ids:
                path_id = f"{root_path}/skill:{skill_id}"
                recorder.record(
                    event_type="edge_traversed",
                    hop_depth=1,
                    source_node_id=bundle_id,
                    target_node_id=skill_id,
                    edge_type="role_episode_contains_skill",
                    candidate_path_id=path_id,
                )
                authority = _skill_authority(
                    skill_id=skill_id,
                    row=skill_by_id.get(skill_id),
                    bundle=bundle,
                    section_id=section_id,
                )
                recorder.record(
                    event_type="authority_evaluated",
                    hop_depth=1,
                    source_node_id=bundle_id,
                    target_node_id=skill_id,
                    edge_type="role_episode_contains_skill",
                    candidate_path_id=path_id,
                    authority_pass=bool(authority["authority_pass"]),
                    reason_codes=authority["reason_codes"],
                )
                skill_records.append(
                    {
                        "candidate_id": skill_id,
                        "candidate_path_id": path_id,
                        "authority": authority,
                        "row": skill_by_id.get(skill_id) or {},
                    }
                )

            metric_records: list[dict[str, Any]] = []
            raw_metric_ids = sorted({str(value).strip() for value in bundle.get("linked_metric_outcome_ids") or [] if str(value).strip()})
            raw_metric_counts_by_employer[employer_lane] = raw_metric_counts_by_employer.get(employer_lane, 0) + len(raw_metric_ids)
            for metric_id in raw_metric_ids:
                path_id = f"{root_path}/metric:{metric_id}"
                recorder.record(
                    event_type="edge_traversed",
                    hop_depth=1,
                    source_node_id=bundle_id,
                    target_node_id=metric_id,
                    edge_type="role_episode_has_metric_outcome",
                    candidate_path_id=path_id,
                )
                authority = _metric_authority(
                    metric_id=metric_id,
                    node=metric_nodes.get(metric_id),
                    bundle=bundle,
                    section_id=section_id,
                )
                recorder.record(
                    event_type="authority_evaluated",
                    hop_depth=1,
                    source_node_id=bundle_id,
                    target_node_id=metric_id,
                    edge_type="role_episode_has_metric_outcome",
                    candidate_path_id=path_id,
                    authority_pass=bool(authority["authority_pass"]),
                    reason_codes=authority["reason_codes"],
                )
                metric_records.append(
                    {
                        "candidate_id": metric_id,
                        "candidate_path_id": path_id,
                        "authority": authority,
                        "node": metric_nodes.get(metric_id) or {},
                    }
                )

            fact_records: list[dict[str, Any]] = []
            for fact_id in sorted({str(value).strip() for value in bundle.get("linked_source_fact_ids") or [] if str(value).strip()}):
                path_id = f"{root_path}/fact:{fact_id}"
                recorder.record(
                    event_type="edge_traversed",
                    hop_depth=1,
                    source_node_id=bundle_id,
                    target_node_id=fact_id,
                    edge_type="role_episode_supported_by_fact",
                    candidate_path_id=path_id,
                )
                authority = evaluate_pretarget_authority(
                    candidate_id=fact_id,
                    candidate_type="source_fact",
                    section_id=section_id,
                    section_allowed=bool(root_auth["section_allowed"]),
                    external_eligible=True,
                    claim_eligible=True,
                    source_refs=[fact_id],
                    path_present=True,
                )
                recorder.record(
                    event_type="authority_evaluated",
                    hop_depth=1,
                    source_node_id=bundle_id,
                    target_node_id=fact_id,
                    edge_type="role_episode_supported_by_fact",
                    candidate_path_id=path_id,
                    authority_pass=bool(authority["authority_pass"]),
                    reason_codes=authority["reason_codes"],
                )
                fact_records.append(
                    {
                        "candidate_id": fact_id,
                        "candidate_path_id": path_id,
                        "authority": authority,
                    }
                )

            prepared_roots.append(
                {
                    "employer_lane": employer_lane,
                    "bundle": bundle,
                    "metric_nodes": metric_nodes,
                    "candidate_path_id": root_path,
                    "authority": root_auth,
                    "skills": skill_records,
                    "metrics": metric_records,
                    "facts": fact_records,
                }
            )

    if not prepared_roots:
        raise ValueError(f"selected graph evidence plan produced empty traversal for {section_id!r}")

    # Pass 2: target relevance is computed only for authority-passing evidence.
    target_role_profile = _infer_target_role_profile(
        target_role=target_role, jd_text=jd_text, briefing_text=briefing_text
    )
    target_blob = f"{target_role}\n{jd_text}\n{briefing_text}"
    briefing_signal_packet = {
        **extract_briefing_signal_packet(briefing_text),
        "role_family_key": target_role_profile,
    }
    employer_weights = dict(_ROLE_EMPLOYER_WEIGHTS[target_role_profile])
    eligible_roots: list[dict[str, Any]] = []
    for root in prepared_roots:
        if not root["authority"]["authority_pass"]:
            root["target_alignment_score"] = 0.0
            root["ranking_score"] = 0.0
            continue
        authorized_skills = [row for row in root["skills"] if row["authority"]["authority_pass"]]
        authorized_facts = [row for row in root["facts"] if row["authority"]["authority_pass"]]
        skill_cap, _metric_cap, _band = _caps_for(
            section_id=section_id,
            weight=employer_weights.get(root["employer_lane"], 0.0),
        )
        if not authorized_skills or not authorized_facts or skill_cap <= 0:
            root["target_alignment_score"] = 0.0
            root["ranking_score"] = 0.0
            if not authorized_skills:
                reason = "no_authorized_skill_children"
            elif not authorized_facts:
                reason = "no_authorized_source_fact_children"
            else:
                reason = "section_skill_cap_zero"
            root["structural_rejection_reason"] = reason
            continue
        root_alignment = _bundle_target_score(
            root["bundle"],
            target_role=target_role,
            jd_text=jd_text,
            briefing_text=briefing_text,
            briefing_signal_packet=briefing_signal_packet,
        )
        root["target_alignment_score"] = root_alignment
        root["ranking_score"] = round(
            root_alignment + employer_weights.get(root["employer_lane"], 0.0), 6
        )
        for skill in authorized_skills:
            proof = _skill_proof_strength(skill["row"])
            alignment = _skill_target_score(skill["row"], skill["candidate_id"], target_blob)
            skill["proof_strength_raw"] = proof
            skill["target_alignment_score"] = alignment
            skill["ranking_score"] = round(proof + alignment, 6)
        for metric in root["metrics"]:
            if not metric["authority"]["authority_pass"]:
                continue
            proof = 1.0 if metric["node"].get("approved", True) else 0.0
            alignment = _metric_target_score(metric["node"], metric["candidate_id"], target_blob)
            metric["proof_strength_raw"] = proof
            metric["target_alignment_score"] = alignment
            metric["ranking_score"] = round(proof + alignment, 6)
        eligible_roots.append(root)

    if not eligible_roots:
        raise ValueError(f"selected graph evidence plan has no authority-passing roots for {section_id!r}")

    by_employer: dict[str, list[dict[str, Any]]] = {}
    for root in eligible_roots:
        by_employer.setdefault(root["employer_lane"], []).append(root)
    for rows in by_employer.values():
        rows.sort(key=lambda row: (-float(row["ranking_score"]), str(row["bundle"].get("role_episode_bundle_id") or "")))

    max_items = int(
        limit
        or _EMPLOYER_SECTION_LIMITS.get(section_id)
        or _SHARED_SECTION_LIMITS.get(section_id)
        or 8
    )
    if section_id in _SHARED_SECTION_LIMITS:
        budgets = _allocate_employer_root_budgets(
            candidates_by_employer=by_employer,
            employer_weights=employer_weights,
            max_items=max_items,
        )
        selected_roots: list[dict[str, Any]] = []
        for employer in sorted(budgets, key=lambda value: (-employer_weights.get(value, 0.0), value)):
            selected_roots.extend(by_employer[employer][: budgets[employer]])
        selected_roots.sort(
            key=lambda row: (
                -employer_weights.get(row["employer_lane"], 0.0),
                -float(row["ranking_score"]),
                row["employer_lane"],
                str(row["bundle"].get("role_episode_bundle_id") or ""),
            )
        )
    else:
        budgets = {}
        selected_roots = sorted(
            eligible_roots,
            key=lambda row: (
                -float(row["ranking_score"]),
                row["employer_lane"],
                str(row["bundle"].get("role_episode_bundle_id") or ""),
            ),
        )[:max_items]

    selected_root_ids = {
        str(root["bundle"].get("role_episode_bundle_id") or "") for root in selected_roots
    }
    selected_skill_ids_seen: set[str] = set()
    selected_metric_ids_seen: set[str] = set()
    facts: list[dict[str, Any]] = []
    pre_facts: list[dict[str, Any]] = []
    selected_skills: list[dict[str, Any]] = []
    selected_metrics_detail: list[dict[str, Any]] = []
    excluded_due_to_root_cap: list[dict[str, Any]] = []
    excluded_due_to_metric_cap: list[dict[str, Any]] = []
    decisions: list[dict[str, Any]] = []
    skill_caps_by_root: dict[str, int] = {}
    metric_caps_by_root: dict[str, int] = {}
    metric_caps_by_root_before_floor: dict[str, int] = {}
    root_weight_bands: dict[str, str] = {}
    employer_root_weights: dict[str, float] = {}
    selected_skill_counts_by_employer: Counter[str] = Counter(
        {employer: 0 for employer in employer_weights}
    )
    selected_metric_counts_by_employer: Counter[str] = Counter(
        {employer: 0 for employer in employer_weights}
    )
    selected_metric_counts_by_employer_before_floor: Counter[str] = Counter(
        {employer: 0 for employer in employer_weights}
    )

    selected_root_order = {
        str(root["bundle"].get("role_episode_bundle_id") or ""): index
        for index, root in enumerate(selected_roots)
    }
    processing_roots = sorted(
        prepared_roots,
        key=lambda root: (
            0
            if str(root["bundle"].get("role_episode_bundle_id") or "")
            in selected_root_order
            else 1,
            selected_root_order.get(
                str(root["bundle"].get("role_episode_bundle_id") or ""), 10**9
            ),
            str(root["candidate_path_id"]),
        ),
    )

    for root in processing_roots:
        bundle = root["bundle"]
        bundle_id = str(bundle.get("role_episode_bundle_id") or "")
        employer_lane = root["employer_lane"]
        root_selected = bundle_id in selected_root_ids
        if not root["authority"]["authority_pass"]:
            root_reason = list(root["authority"]["reason_codes"])
        elif root.get("structural_rejection_reason"):
            root_reason = [str(root["structural_rejection_reason"])]
        elif root_selected:
            root_reason = ["selected_by_authority_then_rank"]
        else:
            root_reason = ["root_budget_not_selected"]
        root_decision = build_candidate_decision(
            section_id=section_id,
            candidate_id=bundle_id,
            candidate_type="role_episode_root",
            candidate_path_id=root["candidate_path_id"],
            decision="selected" if root_selected else "rejected",
            reason_codes=root_reason,
            authority=root["authority"],
            hop_depth=0,
            root_id=bundle_id,
            employer_lane=employer_lane,
            target_alignment_score=float(root.get("target_alignment_score") or 0.0),
            ranking_score=float(root.get("ranking_score") or 0.0),
            extra={
                "employer": str(bundle.get("employer") or ""),
                "title": str(bundle.get("title") or ""),
                "claim_text": str(bundle.get("claim_text") or ""),
                "claim_action": str(bundle.get("claim_action") or ""),
                "claim_scope": str(bundle.get("claim_scope") or ""),
                "claim_outcome": str(bundle.get("claim_outcome") or ""),
                "linked_source_fact_ids": [
                    str(value)
                    for value in bundle.get("linked_source_fact_ids") or []
                    if str(value).strip()
                ],
                "graph_skill_node_ids": [row["candidate_id"] for row in root["skills"]],
                "metric_outcome_ids": [row["candidate_id"] for row in root["metrics"]],
            },
        )
        decisions.append(root_decision)
        recorder.record(
            event_type="candidate_terminal",
            hop_depth=0,
            target_node_id=bundle_id,
            candidate_path_id=root["candidate_path_id"],
            authority_pass=bool(root["authority"]["authority_pass"]),
            decision=root_decision["decision"],
            reason_codes=root_reason,
        )

        weight = employer_weights.get(employer_lane, 0.0)
        skill_cap, metric_cap, band = _caps_for(section_id=section_id, weight=weight)
        metric_floor = _metric_floor_for_section(section_id)
        eligible_skills = sorted(
            [row for row in root["skills"] if row["authority"]["authority_pass"]],
            key=lambda row: (-float(row.get("ranking_score") or 0.0), row["candidate_id"]),
        )
        eligible_metrics = sorted(
            [row for row in root["metrics"] if row["authority"]["authority_pass"]],
            key=lambda row: (-float(row.get("ranking_score") or 0.0), row["candidate_id"]),
        )
        effective_metric_cap = min(len(eligible_metrics), max(metric_cap, metric_floor))
        skill_caps_by_root[bundle_id] = skill_cap
        metric_caps_by_root_before_floor[bundle_id] = metric_cap
        metric_caps_by_root[bundle_id] = effective_metric_cap
        root_weight_bands[bundle_id] = band
        employer_root_weights[bundle_id] = weight

        selected_skill_rows: list[dict[str, Any]] = []
        selected_metric_rows_before_floor: list[dict[str, Any]] = []
        selected_metric_rows: list[dict[str, Any]] = []
        if root_selected:
            for row in eligible_skills:
                if row["candidate_id"] in selected_skill_ids_seen:
                    continue
                if len(selected_skill_rows) >= skill_cap:
                    break
                selected_skill_rows.append(row)
                selected_skill_ids_seen.add(row["candidate_id"])
            available_metrics = [row for row in eligible_metrics if row["candidate_id"] not in selected_metric_ids_seen]
            selected_metric_rows_before_floor = available_metrics[:metric_cap]
            selected_metric_rows = available_metrics[:effective_metric_cap]
            selected_metric_ids_seen.update(row["candidate_id"] for row in selected_metric_rows)

        selected_skill_ids = [row["candidate_id"] for row in selected_skill_rows]
        selected_metric_ids_before_floor = [row["candidate_id"] for row in selected_metric_rows_before_floor]
        selected_metric_ids = [row["candidate_id"] for row in selected_metric_rows]

        if root_selected:
            selected_skill_counts_by_employer[employer_lane] += len(selected_skill_ids)
            selected_metric_counts_by_employer_before_floor[employer_lane] += len(selected_metric_ids_before_floor)
            selected_metric_counts_by_employer[employer_lane] += len(selected_metric_ids)
            for row in selected_skill_rows:
                selected_skills.append(
                    {
                        "skill_id": row["candidate_id"],
                        "role_episode_bundle_id": bundle_id,
                        "employer_lane": employer_lane,
                        "root_weight": weight,
                        "root_weight_band": band,
                        "proof_strength_raw": row.get("proof_strength_raw", 0.0),
                        "target_alignment_score": row.get("target_alignment_score", 0.0),
                        "ranking_score": row.get("ranking_score", 0.0),
                    }
                )
            for row in selected_metric_rows:
                node = row["node"]
                selected_metrics_detail.append(
                    {
                        "metric_outcome_id": row["candidate_id"],
                        "role_episode_bundle_id": bundle_id,
                        "employer_lane": employer_lane,
                        "root_weight": weight,
                        "root_weight_band": band,
                        "metric": str(node.get("metric") or node.get("claim_text") or row["candidate_id"]),
                        "proof_strength_raw": row.get("proof_strength_raw", 0.0),
                        "target_alignment_score": row.get("target_alignment_score", 0.0),
                        "ranking_score": row.get("ranking_score", 0.0),
                    }
                )
            pre_facts.append(
                _bundle_to_fact(
                    bundle,
                    employer_lane=employer_lane,
                    metric_nodes=root["metric_nodes"],
                    selected_skill_ids=selected_skill_ids,
                    selected_metric_ids=selected_metric_ids_before_floor,
                )
            )
            facts.append(
                _bundle_to_fact(
                    bundle,
                    employer_lane=employer_lane,
                    metric_nodes=root["metric_nodes"],
                    selected_skill_ids=selected_skill_ids,
                    selected_metric_ids=selected_metric_ids,
                )
            )

        selected_skill_set = set(selected_skill_ids)
        for row in root["skills"]:
            if not row["authority"]["authority_pass"]:
                decision, reasons = "rejected", list(row["authority"]["reason_codes"])
            elif not root_selected:
                decision, reasons = "rejected", ["parent_root_not_selected"]
            elif row["candidate_id"] in selected_skill_set:
                decision, reasons = "selected", ["selected_after_full_sibling_ranking"]
            elif row["candidate_id"] in selected_skill_ids_seen:
                decision, reasons = "rejected", ["skill_already_selected_in_section"]
            else:
                decision, reasons = "rejected", ["skill_root_cap"]
                excluded_due_to_root_cap.append(
                    {
                        "graph_evidence_id": row["candidate_id"],
                        "role_episode_bundle_id": bundle_id,
                        "employer_lane": employer_lane,
                        "cap": skill_cap,
                        "reason": "skill_root_cap",
                    }
                )
            candidate = build_candidate_decision(
                section_id=section_id,
                candidate_id=row["candidate_id"],
                candidate_type="leaf_skill",
                candidate_path_id=row["candidate_path_id"],
                decision=decision,
                reason_codes=reasons,
                authority=row["authority"],
                hop_depth=1,
                parent_id=bundle_id,
                root_id=bundle_id,
                employer_lane=employer_lane,
                proof_strength_raw=float(row.get("proof_strength_raw") or 0.0),
                target_alignment_score=float(row.get("target_alignment_score") or 0.0),
                ranking_score=float(row.get("ranking_score") or 0.0),
                path_signature=f"{bundle_id}->role_episode_contains_skill->{row['candidate_id']}",
                extra={
                    "skill_label": str(
                        row["row"].get("label") or row["row"].get("name") or ""
                    ),
                    "source_refs": list(row["authority"].get("source_refs") or []),
                },
            )
            decisions.append(candidate)
            recorder.record(
                event_type="candidate_terminal",
                hop_depth=1,
                source_node_id=bundle_id,
                target_node_id=row["candidate_id"],
                edge_type="role_episode_contains_skill",
                candidate_path_id=row["candidate_path_id"],
                authority_pass=bool(row["authority"]["authority_pass"]),
                decision=decision,
                reason_codes=reasons,
            )

        selected_metric_set = set(selected_metric_ids)
        for row in root["metrics"]:
            if not row["authority"]["authority_pass"]:
                decision, reasons = "rejected", list(row["authority"]["reason_codes"])
            elif not root_selected:
                decision, reasons = "rejected", ["parent_root_not_selected"]
            elif row["candidate_id"] in selected_metric_set:
                decision, reasons = "selected", ["selected_after_full_metric_ranking"]
            elif row["candidate_id"] in selected_metric_ids_seen:
                decision, reasons = "rejected", ["metric_already_selected_in_section"]
            else:
                decision, reasons = "rejected", ["metric_root_cap"]
                excluded_due_to_metric_cap.append(
                    {
                        "graph_evidence_id": row["candidate_id"],
                        "role_episode_bundle_id": bundle_id,
                        "employer_lane": employer_lane,
                        "cap": effective_metric_cap,
                        "reason": "metric_root_cap",
                    }
                )
            candidate = build_candidate_decision(
                section_id=section_id,
                candidate_id=row["candidate_id"],
                candidate_type="metric_outcome",
                candidate_path_id=row["candidate_path_id"],
                decision=decision,
                reason_codes=reasons,
                authority=row["authority"],
                hop_depth=1,
                parent_id=bundle_id,
                root_id=bundle_id,
                employer_lane=employer_lane,
                proof_strength_raw=float(row.get("proof_strength_raw") or 0.0),
                target_alignment_score=float(row.get("target_alignment_score") or 0.0),
                ranking_score=float(row.get("ranking_score") or 0.0),
                path_signature=f"{bundle_id}->role_episode_has_metric_outcome->{row['candidate_id']}",
                extra={
                    "metric": str(row["node"].get("metric") or ""),
                    "metric_type": str(row["node"].get("metric_type") or ""),
                    "metric_claim_text": str(row["node"].get("claim_text") or ""),
                    "metric_surface_tokens": [
                        str(value)
                        for value in row["node"].get("surface_tokens") or []
                        if str(value).strip()
                    ],
                    "source_refs": list(row["authority"].get("source_refs") or []),
                },
            )
            decisions.append(candidate)
            recorder.record(
                event_type="candidate_terminal",
                hop_depth=1,
                source_node_id=bundle_id,
                target_node_id=row["candidate_id"],
                edge_type="role_episode_has_metric_outcome",
                candidate_path_id=row["candidate_path_id"],
                authority_pass=bool(row["authority"]["authority_pass"]),
                decision=decision,
                reason_codes=reasons,
            )

        for row in root["facts"]:
            if not row["authority"]["authority_pass"]:
                decision, reasons = "rejected", list(row["authority"]["reason_codes"])
            elif root_selected:
                decision, reasons = "selected", ["selected_support_fact_with_root"]
            else:
                decision, reasons = "rejected", ["parent_root_not_selected"]
            candidate = build_candidate_decision(
                section_id=section_id,
                candidate_id=row["candidate_id"],
                candidate_type="source_fact",
                candidate_path_id=row["candidate_path_id"],
                decision=decision,
                reason_codes=reasons,
                authority=row["authority"],
                hop_depth=1,
                parent_id=bundle_id,
                root_id=bundle_id,
                employer_lane=employer_lane,
                proof_strength_raw=1.0 if row["authority"]["authority_pass"] else 0.0,
                path_signature=f"{bundle_id}->role_episode_supported_by_fact->{row['candidate_id']}",
                extra={"source_refs": list(row["authority"].get("source_refs") or [])},
            )
            decisions.append(candidate)
            recorder.record(
                event_type="candidate_terminal",
                hop_depth=1,
                source_node_id=bundle_id,
                target_node_id=row["candidate_id"],
                edge_type="role_episode_supported_by_fact",
                candidate_path_id=row["candidate_path_id"],
                authority_pass=bool(row["authority"]["authority_pass"]),
                decision=decision,
                reason_codes=reasons,
            )

    if not facts:
        raise ValueError(f"selected graph evidence plan produced no selected facts for {section_id!r}")

    decisions.sort(
        key=lambda row: (
            int(row.get("hop_depth") or 0),
            str(row.get("candidate_type") or ""),
            str(row.get("candidate_path_id") or ""),
        )
    )
    ordered, allowed = build_allowed_fact_ids_for_plan_facts(facts)
    selected_nodes = [str(fact["role_episode_bundle_id"]) for fact in facts]
    selected_metrics = list(dict.fromkeys(str(row["metric_outcome_id"]) for row in selected_metrics_detail))
    selected_skill_ids_all = [str(row["skill_id"]) for row in selected_skills]
    selected_employer_roots: dict[str, list[str]] = {}
    selected_employers: list[str] = []
    for fact in facts:
        employer_lane = str(fact.get("employer_lane") or "")
        selected_employer_roots.setdefault(employer_lane, []).append(str(fact["role_episode_bundle_id"]))
        employer = str(fact.get("employer") or "")
        if employer and employer not in selected_employers:
            selected_employers.append(employer)

    selected_edges = [
        {
            "edge_type": "role_episode_contains_skill",
            "source": str(row["role_episode_bundle_id"]),
            "target": str(row["skill_id"]),
        }
        for row in selected_skills
    ] + [
        {
            "edge_type": "role_episode_has_metric_outcome",
            "source": str(row["role_episode_bundle_id"]),
            "target": str(row["metric_outcome_id"]),
        }
        for row in selected_metrics_detail
    ]

    pre_depth_report = build_graph_evidence_depth_report({"facts": pre_facts}, section_id=section_id)
    post_depth_report = build_graph_evidence_depth_report({"facts": facts}, section_id=section_id)
    depth_comparison_report = build_graph_evidence_depth_comparison_report(
        section_id=section_id,
        pre_report=pre_depth_report,
        post_report=post_depth_report,
        fix_label="competencies_metric_floor_v1" if section_id == "competencies" else "shared_lane_metric_floor_v1",
    )
    candidate_receipt = build_candidate_receipt(section_id=section_id, decisions=decisions)
    rejected_root_ids = [
        str(row["candidate_id"])
        for row in decisions
        if row.get("candidate_type") == "role_episode_root" and row.get("decision") == "rejected"
    ]
    traversal_receipt = recorder.build_receipt(
        decisions=decisions,
        selected_root_ids=selected_nodes,
        rejected_root_ids=rejected_root_ids,
        target_role_profile=target_role_profile,
    )
    counts = traversal_receipt["frontier_size_by_hop_depth"]
    traversal_receipt["frontier_size_by_hop_depth"] = {
        "0_role_episode_roots": int(counts.get("0") or 0),
        "1_leaf_skill_candidates": sum(1 for row in decisions if row.get("candidate_type") == "leaf_skill"),
        "2_metric_outcome_candidates": sum(1 for row in decisions if row.get("candidate_type") == "metric_outcome"),
        "1_source_fact_candidates": sum(1 for row in decisions if row.get("candidate_type") == "source_fact"),
    }
    authority_rows = [dict(row["authority"]) for row in decisions]
    pretarget_authority_receipt = {
        "schema_version": "c03_pretarget_authority_receipt_v1",
        "section_id": section_id,
        "candidate_count": len(authority_rows),
        "authority_pass_count": sum(1 for row in authority_rows if row.get("authority_pass")),
        "authority_block_count": sum(1 for row in authority_rows if not row.get("authority_pass")),
        "targeting_consulted_count": sum(1 for row in authority_rows if row.get("targeting_consulted")),
        "authority_before_targeting_pass": all(
            row.get("targeting_consulted") is False
            and row.get("authority_evaluated_before_targeting") is True
            for row in authority_rows
        ),
        "authority_decisions_digest": stable_digest(authority_rows),
    }
    concentration_policy = build_graph_skill_concentration_policy(
        counts=dict(selected_skill_counts_by_employer),
        distribution_kind="employer_lane",
        bucket_ids=tuple(employer_weights.keys()),
        context={
            "section_id": section_id,
            "target_role_profile": target_role_profile,
            "target_role": target_role,
        },
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
        "source_authority_contract": {
            "schema_version": "c03_source_authority_contract_v1",
            "authority_source": "augmented_skills_graph",
            "graph_ref": "apps_rg/fact_inventory/master_skills_arsenal_ledger.json",
            "graph_digest": graph_digest,
            "graph_version": graph_version_from_payload(graph),
            "authority_evaluated_before_targeting": True,
            "targeting_inputs_are_non_authority": True,
            "missing_authority_fails_closed": True,
        },
        "pretarget_authority_receipt": pretarget_authority_receipt,
        "target_role_profile": target_role_profile,
        "role_family_key": target_role_profile,
        "graph_weight_profile": {
            "profile": target_role_profile,
            "employer_weights": employer_weights,
            "selection_model": "authority_first_full_sibling_ranking_v2",
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
        "selected_employer_lane_ids": [str(fact.get("employer_lane") or "") for fact in facts],
        "selected_headline_positioning_families": list(_HEADLINE_FAMILIES_BY_PROFILE.get(target_role_profile, ())),
        "selected_competency_families": list(_COMPETENCY_FAMILIES_BY_PROFILE.get(target_role_profile, ())),
        "briefing_signal_packet": briefing_signal_packet,
        "concentration_policy": concentration_policy,
        "excluded_due_to_root_cap": excluded_due_to_root_cap,
        "excluded_due_to_metric_cap": excluded_due_to_metric_cap,
        "allowed_graph_evidence_ids": ordered,
        "selection_rationale": (
            "Authority and source lineage were evaluated before any target-role, JD, or briefing score. "
            "Every bounded root, skill, metric, and source-fact path received a terminal decision after "
            "full sibling ranking; targeting only ordered authority-passing candidates."
        ),
        "skew_diagnostics": {
            "raw_skill_counts_by_employer": raw_skill_counts_by_employer,
            "raw_metric_counts_by_employer": raw_metric_counts_by_employer,
            "selected_skill_counts_by_employer": dict(selected_skill_counts_by_employer),
            "selected_metric_counts_by_employer_before_floor": dict(selected_metric_counts_by_employer_before_floor),
            "selected_metric_counts_by_employer": dict(selected_metric_counts_by_employer),
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
        "required_fact_ids": [str(fact["fact_id"]) for fact in facts],
        "graph_candidate_decision_ledger": decisions,
        "graph_candidate_receipt": candidate_receipt,
        "graph_traversal_receipt": traversal_receipt,
        "graph_evidence_depth_pre_report": pre_depth_report,
        "graph_evidence_depth_report": post_depth_report,
        "graph_evidence_depth_post_report": post_depth_report,
        "graph_evidence_depth_comparison_report": depth_comparison_report,
        "graph_evidence_depth_status": post_depth_report.get("status"),
        "graph_evidence_semantic_coverage_pct": post_depth_report.get("semantic_coverage_pct"),
    }
    final = finalize_canonical_section_plan(plan)
    return final, ordered, allowed


__all__ = ["build_selected_graph_evidence_plan_for_section"]
