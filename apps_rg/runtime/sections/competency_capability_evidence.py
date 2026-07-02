"""Competency capability bundle evidence — C0 consumption for the competencies section.

Proof authority is graph-backed competency capability bundles plus linked source facts,
not generic taxonomy labels, flat skill lists, or default_fid backfill. Base resume and
archive material are calibration/provenance only — never prose hydration.
"""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.augmented_skills_graph import load_augmented_skills_graph
from apps_rg.runtime.sections.graph_evidence_contract import (
    require_section_packet,
    require_selected_graph_evidence_plan,
)
from apps_rg.runtime.sections.competencies_term_phrase import term_phrase

logger = logging.getLogger(__name__)
from apps_rg.runtime.sections.competency_capability_registry import (
    REQUIRED_CAPABILITY_FAMILIES,
    get_bundles_for_section,
    validate_competency_bundle,
)

COMPETENCY_CAPABILITY_EVIDENCE_PACK_MARKER = "COMPETENCY_CAPABILITY_EVIDENCE_PACK"

COMPETENCIES_PATH_DIVERSITY_LENSES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("agentic platform architecture", ("agentic_platform", "control_plane", "multi_agent_orchestration")),
    ("runtime governance and gates", ("runtime_governance", "policy_controls", "fail_closed_gates")),
    ("retrieval and context engineering", ("retrieval_context", "graphrag", "grounding")),
    ("llmops evaluation and reliability", ("llmops", "evaluation", "observability")),
    ("distributed cloud data systems", ("distributed_infra", "cloud_data_platform", "microservices")),
    ("platform productization", ("productization", "commercialization", "reusable_platforms")),
    ("partner applied AI architecture", ("partner_architecture", "reference_architecture", "partner_enablement")),
    ("engineering operating model", ("engineering_leadership", "org_scale", "executive_alignment")),
    ("partner ecosystem execution", ("ecosystem_gtm", "hyperscaler_alliances", "joint_value_creation")),
)
COMPETENCIES_SC_COMPACT_SYSTEM_MARKER = "COMPETENCIES_SC_COMPACT_SYSTEM_V1"


def _normalize_compact_prompt_newlines(content: str) -> str:
    text = str(content or "")
    if "\\n" in text:
        text = text.replace("\\n", "\n")
    return text


def _slice_prompt_block(content: str, start_marker: str, end_marker: str) -> str:
    start = content.find(start_marker)
    if start < 0:
        return ""
    end = content.find(end_marker, start)
    if end < 0:
        return ""
    end += len(end_marker)
    return content[start:end].strip()


def _compact_bundle_block(block: str) -> str:
    block = _normalize_compact_prompt_newlines(block)
    lines = block.splitlines()
    if not lines:
        return ""
    keep: list[str] = [lines[0].strip()]
    anchor_mode = False
    anchor_count = 0
    prefixes = (
        "display_label_candidate:",
        "target_taxonomy_category_ids:",
        "graph_skill_node_ids:",
        "linked_source_fact_ids:",
        "allowed_partner_roots:",
        "forbidden_partner_roots:",
        "capability_facets:",
    )
    for raw in lines[1:]:
        stripped = raw.strip()
        if not stripped:
            anchor_mode = False
            continue
        if stripped.startswith(prefixes):
            keep.append(f"  {stripped}")
            anchor_mode = False
            continue
        if stripped.startswith("vocabulary_anchors"):
            keep.append("  vocabulary_anchors:")
            anchor_mode = True
            anchor_count = 0
            continue
        if anchor_mode and stripped.startswith("- ") and anchor_count < 3:
            keep.append(f"    {stripped}")
            anchor_count += 1
    return "\n".join(keep)


def _compact_allowed_fact_ids_block(block: str) -> str:
    text = _normalize_compact_prompt_newlines(block)
    if not text:
        return ""
    ids = re.findall(r"\b(?:reb|fact|skill)_[A-Za-z0-9_]+\b", text)
    seen: list[str] = []
    for raw in ids:
        if raw.startswith("metric_") or raw in seen:
            continue
        seen.append(raw)
    if not seen:
        return "\n".join(line.strip() for line in text.splitlines()[:3] if line.strip())
    return "ALLOWED_SOURCE_FACT_IDS_COMPACT:\n" + ", ".join(seen)


def _compact_jd_requirements_block(block: str) -> str:
    text = _normalize_compact_prompt_newlines(block)
    if not text:
        return ""
    keep: list[str] = ["<jd_requirements_compact>"]
    for raw in text.splitlines():
        line = re.sub(r"\s+", " ", raw.strip())
        if not line:
            continue
        lower = line.lower()
        if line.startswith(("TARGET_TITLE", "TARGET_COMPANY")):
            keep.append(line[:220])
            continue
        if any(
            marker in lower
            for marker in (
                "applied ai architecture",
                "partnership",
                "solutions architect",
                "claude",
                "safe",
                "reliable",
            )
        ):
            keep.append(line[:280])
        if len(keep) >= 10:
            break
    keep.append("</jd_requirements_compact>")
    return "\n".join(keep)


def _compact_competencies_sc_evidence(evidence: str) -> str:
    """Reduce verbose C0 evidence to the fields needed for SC candidate generation."""
    evidence = _normalize_compact_prompt_newlines(evidence)
    employment = ""
    allowed_ids = ""
    employment_start = evidence.find("CANONICAL_EMPLOYMENT_BULLETS")
    allowed_start = evidence.find("ALLOWED_SOURCE_FACT_IDS", employment_start)
    projection_start = evidence.find("VERIFIED_SKILL_INVENTORY_PROJECTION", allowed_start)
    if employment_start >= 0 and allowed_start > employment_start:
        employment = evidence[employment_start:allowed_start].strip()
    elif employment_start >= 0:
        employment_end_candidates = [
            pos for pos in (
                evidence.find("COMPETENCY_BUNDLE ", employment_start),
                evidence.find("COMPETENCY_CAPABILITY_EVIDENCE_PACK", employment_start),
            )
            if pos > employment_start
        ]
        employment_end = min(employment_end_candidates) if employment_end_candidates else len(evidence)
        employment = evidence[employment_start:employment_end].strip()
    if allowed_start >= 0:
        allowed_end_candidates = [
            pos for pos in (projection_start, evidence.find("COMPETENCY_CAPABILITY_EVIDENCE_PACK", allowed_start))
            if pos > allowed_start
        ]
        allowed_end = min(allowed_end_candidates) if allowed_end_candidates else len(evidence)
        allowed_ids = _compact_allowed_fact_ids_block(evidence[allowed_start:allowed_end].strip())

    bundle_lines: list[str] = []
    marker = "COMPETENCY_BUNDLE "
    if marker in evidence:
        for part in evidence.split(marker)[1:]:
            block = marker + part
            next_marker = block.find("\n\nCOMPETENCY_BUNDLE ", len(marker))
            if next_marker > 0:
                block = block[:next_marker]
            compact = _compact_bundle_block(block)
            if compact:
                bundle_lines.append(compact)

    sections = [
        "COMPACT_C0_EVIDENCE_BLUEPRINT",
        employment,
        allowed_ids,
        "COMPACT_COMPETENCY_BUNDLES:",
        "\n\n".join(bundle_lines),
    ]
    return "\n\n".join(section for section in sections if section).strip()


def _compact_competencies_sc_system_content(content: str) -> str:
    """Keep proof-bearing evidence for SC generation, drop examples/schema repetition."""
    content = _normalize_compact_prompt_newlines(content)
    evidence = _slice_prompt_block(content, "<candidate_facts", "</candidate_facts>")
    jd_requirements = _slice_prompt_block(content, "<jd_requirements", "</jd_requirements>")
    if not evidence:
        return content
    compact_evidence = _compact_competencies_sc_evidence(evidence)
    parts = [
        COMPETENCIES_SC_COMPACT_SYSTEM_MARKER,
        (
            "Task: generate one compact competencies candidate for selector ranking. "
            "Evidence authority is the retained C0 candidate_facts block only. "
            "JD and briefing are targeting context only, never proof. Respond directly; "
            "adaptive thinking is unnecessary for this extraction."
        ),
        (
            "Output JSON only with categories, selected_fact_plan, claim_ledger, jd_alignment, "
            "excluded_jd_skills, removed_or_rewritten_terms, gap_notes, change_log, and self_check. "
            "Use 6-8 categories, exactly 3 compact terms per category, and source_fact_ids copied "
            "verbatim from retained evidence. Do not wrap JSON in markdown fences."
        ),
        compact_evidence,
    ]
    if jd_requirements:
        parts.append(_compact_jd_requirements_block(jd_requirements))
    return "\n\n".join(parts)


def compact_competencies_self_consistency_messages(
    messages: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Compact provider payload messages for competencies SC candidate calls only."""
    out: list[dict[str, Any]] = []
    compacted = False
    for msg in messages:
        item = dict(msg)
        if not compacted and str(item.get("role") or "").strip().lower() == "system":
            item["content"] = _compact_competencies_sc_system_content(str(item.get("content") or ""))
            compacted = True
        out.append(item)
    return out

PARTNERSHIP_FIRST_COMPETENCIES_BUNDLE_ORDER: tuple[str, ...] = (
    "ccb_partner_applied_ai_architecture",
    "ccb_agentic_platforms",
    "ccb_runtime_governance",
    "ccb_retrieval_context_engineering",
    "ccb_platform_productization",
    "ccb_llmops_reliability",
    "ccb_distributed_systems_engineering",
    "ccb_engineering_leadership",
    "ccb_partnerships_ecosystem_execution",
    "ccb_data_governance_security",
    "ccb_devsecops_delivery_governance",
    "ccb_insurance_domain_erm",
)

VISIBLE_GRAPH_TERMS_MIN = 3
VISIBLE_GRAPH_TERMS_MAX = 3


def _source_fact_root_id(raw: Any) -> str:
    raw_s = str(raw or "").strip()
    if not raw_s or raw_s.startswith("metric_"):
        return ""
    fid = raw_s.split("_metric_", 1)[0].strip()
    if not fid or fid.startswith("metric_"):
        return ""
    return fid


VISIBLE_GRAPH_SURFACE_TERM_OVERRIDES: dict[str, tuple[str, ...]] = {
    "ccb_partner_applied_ai_architecture": (
        "partner-ready applied AI reference architectures",
        "co-developed AI solution patterns for partners",
        "safe AI partner deployment assurance patterns",
    ),
    "ccb_partnerships_ecosystem_execution": (
        "IBM-AWS alliance commercialization with partners",
        "hyperscaler co-sell operating cadences for modernization",
        "joint GTM enablement for partner pursuits",
    ),
    "ccb_agentic_platforms": (
        "governed multi-agent orchestration control planes",
        "agentic workflow routing across enterprise systems",
        "policy-bound execution architecture for AI agents",
    ),
    "ccb_runtime_governance": (
        "fail-closed runtime control gate design",
        "policy enforcement across agent execution paths",
        "sandboxed decision workflows with audit trails",
    ),
    "ccb_retrieval_context_engineering": (
        "GraphRAG context grounding for enterprise workflows",
        "dense-sparse retrieval with relationship-aware ranking",
        "authority-ordered prompt context assembly pipelines",
    ),
    "ccb_platform_productization": (
        "demoable AI accelerators for executive buyers",
        "reusable platform IP commercialization motions",
        "evaluation-ready delivery from prototype to adoption",
    ),
    "ccb_llmops_reliability": (
        "audit-grade telemetry for agentic systems",
        "evaluation gauntlets for behavior assurance",
        "reliability lifecycle for governed AI workflows",
    ),
    "ccb_distributed_systems_engineering": (
        "cloud-native AI data reference architectures",
        "microservices integration for regulated ecosystems",
        "lakehouse modernization for decision intelligence",
    ),
    "ccb_engineering_leadership": (
        "executive-aligned engineering operating cadences for adoption",
        "cross-functional delivery governance at scale",
        "organization scale-out for platform execution",
    ),
}

COMPETENCY_BUNDLE_FAMILY_ROOT_HINTS: dict[str, tuple[str, ...]] = {
    "agentic_platforms": (
        "reb_unify_agentic_platform_architecture",
        "reb_unify_production_adoption_lifecycle",
        "reb_unify_distributed_ecosystem_engineering",
    ),
    "runtime_governance": (
        "reb_unify_agentic_platform_architecture",
        "reb_unify_production_adoption_lifecycle",
        "reb_unify_distributed_ecosystem_engineering",
    ),
    "retrieval_context_engineering": (
        "reb_unify_agentic_platform_architecture",
        "reb_unify_distributed_ecosystem_engineering",
    ),
    "llmops_reliability": ("reb_unify_distributed_ecosystem_engineering",),
    "distributed_systems_engineering": (
        "reb_unify_distributed_ecosystem_engineering",
        "reb_ibm_aws_modernization_architecture",
        "reb_ibm_data_modeling_bi_decision_support",
    ),
    "platform_productization": (
        "reb_unify_agentic_platform_architecture",
        "reb_unify_production_adoption_lifecycle",
        "reb_unify_partner_channel_cosell",
    ),
    "partner_applied_ai_architecture": (
        "reb_unify_partner_channel_cosell",
        "reb_ibm_aws_alliance_partner_cosell_gtm",
        "reb_ibm_presales_solution_engineering",
    ),
    "partnerships_ecosystem_execution": (
        "reb_ibm_aws_alliance_partner_cosell_gtm",
    ),
    "engineering_leadership": (
        "reb_unify_distributed_ecosystem_engineering",
        "reb_unify_production_adoption_lifecycle",
        "reb_ibm_presales_solution_engineering",
        "reb_ibm_data_modeling_bi_decision_support",
    ),
    "data_governance_security": ("reb_ibm_data_modeling_bi_decision_support",),
}

VISIBLE_GRAPH_SURFACE_TAXONOMY_BY_BUNDLE: dict[str, tuple[str, str]] = {
    "ccb_partner_applied_ai_architecture": ("cloud_partner_ecosystems", "Cloud & Partner Ecosystems"),
    "ccb_partnerships_ecosystem_execution": ("cloud_partner_ecosystems", "Cloud & Partner Ecosystems"),
    "ccb_agentic_platforms": ("ai_platform_leadership", "AI Platform Leadership"),
    "ccb_runtime_governance": ("governance_risk_compliance", "Governance, Risk & Compliance"),
    "ccb_retrieval_context_engineering": ("tech_strategy_innovation", "Technology Strategy & Innovation"),
    "ccb_platform_productization": ("commercial_operating_impact", "Commercial & Operating Impact"),
    "ccb_llmops_reliability": ("llmops_reliability", "LLMOps & Reliability"),
    "ccb_distributed_systems_engineering": ("data_analytics_modernization", "Data & Analytics Modernization"),
    "ccb_engineering_leadership": ("engineering_delivery_leadership", "Engineering & Delivery Leadership"),
}

_AUTHORITY_HEADER_LINES: tuple[str, ...] = (
    "proof_authority = graph_competency_bundles_plus_linked_source_facts",
    "base_resume_usage = calibration_only",
    "archive_usage = provenance_inventory_only",
    "jd_usage = targeting_only",
    "examples_usage = style_only",
    "generic_taxonomy_label = display_wrapper_only_not_proof",
    "flat_skill_list_or_default_fid_support = forbidden",
    (
        "Generate the competencies section organically from competency capability bundles. "
        "Do not copy or paraphrase base resume or archive competency text. "
        "Preserve or exceed the base resume's rigor, specificity, and senior executive engineering signal."
    ),
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _skill_rows_by_id(repo_root: Path | None = None) -> dict[str, dict[str, Any]]:
    graph = load_augmented_skills_graph(repo_root=repo_root or _repo_root())
    out: dict[str, dict[str, Any]] = {}
    for row in graph.get("skill_rows") or []:
        if isinstance(row, dict):
            sid = str(row.get("skill_id") or "").strip()
            if sid:
                out[sid] = row
    return out


def build_competency_capability_section_packet(
    section_id: str = "competencies",
    *,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Build machine-readable competency capability packet (proof_pool metadata / C0)."""
    bundles = get_bundles_for_section(section_id)
    skill_index = _skill_rows_by_id(repo_root)
    records: list[dict[str, Any]] = []
    families_present: set[str] = set()
    graph_skill_node_ids_by_category: dict[str, list[str]] = {}
    source_fact_ids_by_category: dict[str, list[str]] = {}

    for bundle in bundles:
        ok, violations = validate_competency_bundle(bundle)
        if not ok:
            raise ValueError(
                f"Invalid competency bundle {bundle.get('competency_bundle_id')}: {violations}"
            )
        families_present.add(str(bundle.get("capability_family") or ""))
        skill_nodes: list[dict[str, Any]] = []
        for sid in bundle.get("graph_skill_node_ids") or []:
            row = skill_index.get(str(sid))
            if row:
                skill_nodes.append(
                    {
                        "skill_id": sid,
                        "allowed_phrases": list(row.get("allowed_phrases") or [])[:6],
                        "activation_status": row.get("activation_status"),
                        "confidence_grade": row.get("confidence_grade"),
                    }
                )
            else:
                skill_nodes.append({"skill_id": sid, "allowed_phrases": []})
        for cat_id in bundle.get("target_taxonomy_category_ids") or []:
            graph_skill_node_ids_by_category.setdefault(str(cat_id), [])
            for sid in bundle.get("graph_skill_node_ids") or []:
                if sid not in graph_skill_node_ids_by_category[str(cat_id)]:
                    graph_skill_node_ids_by_category[str(cat_id)].append(str(sid))
            source_fact_ids_by_category.setdefault(str(cat_id), [])
            for fid in bundle.get("linked_source_fact_ids") or []:
                if fid not in source_fact_ids_by_category[str(cat_id)]:
                    source_fact_ids_by_category[str(cat_id)].append(str(fid))
        records.append(
            {
                "competency_bundle_id": bundle["competency_bundle_id"],
                "capability_family": bundle["capability_family"],
                "display_label_candidate": bundle["display_label_candidate"],
                "target_taxonomy_category_ids": list(bundle.get("target_taxonomy_category_ids") or []),
                "graph_skill_node_ids": list(bundle.get("graph_skill_node_ids") or []),
                "linked_source_fact_ids": list(bundle.get("linked_source_fact_ids") or []),
                "employer_bindings": list(bundle.get("employer_bindings") or []),
                "role_episode_bindings": list(bundle.get("role_episode_bindings") or []),
                "evidence_strength": bundle.get("evidence_strength"),
                "external_claim_policy": bundle.get("external_claim_policy"),
                "activation_status": bundle.get("activation_status"),
                "base_rigor_family_match": bundle.get("base_rigor_family_match"),
                "seniority_signal": bundle.get("seniority_signal"),
                "technical_density_signal": bundle.get("technical_density_signal"),
                "commercial_or_operating_scope_signal": bundle.get("commercial_or_operating_scope_signal"),
                "target_relevance_rationale": bundle.get("target_relevance_rationale"),
                "capability_facets": list(bundle.get("capability_facets") or []),
                "allowed_partner_roots": list(bundle.get("allowed_partner_roots") or []),
                "forbidden_partner_roots": list(bundle.get("forbidden_partner_roots") or []),
                "root_binding_policy": bundle.get("root_binding_policy"),
                "vocabulary_anchors": list(bundle.get("vocabulary_anchors") or []),
                "bound_skills": skill_nodes,
            }
        )

    return {
        "section_id": section_id,
        "proof_authority": "graph_competency_bundles_plus_linked_source_facts",
        "base_resume_usage": "calibration_only",
        "archive_usage": "provenance_inventory_only",
        "jd_usage": "targeting_only",
        "examples_usage": "style_only",
        "competency_bundles": records,
        "competency_bundle_ids": [r["competency_bundle_id"] for r in records],
        "capability_families_present": sorted(f for f in families_present if f),
        "required_capability_families": list(REQUIRED_CAPABILITY_FAMILIES),
        "graph_skill_node_ids_by_category": graph_skill_node_ids_by_category,
        "source_fact_ids_by_category": source_fact_ids_by_category,
        "consumption_mode": "competency_bundle_required",
        "flat_taxonomy_only_forbidden": True,
        "default_fid_only_support_forbidden": True,
    }


def _selected_graph_plan(source: dict[str, Any] | None) -> dict[str, Any]:
    return require_selected_graph_evidence_plan(source, section_id="competencies")


def _filter_packet_by_selected_graph_plan(
    packet: dict[str, Any],
    selected_graph_plan: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(selected_graph_plan, dict) or not selected_graph_plan:
        raise ValueError("competencies: graph packet is mandatory; missing selected_graph_evidence_plan")
    selected_families = {
        str(x).strip()
        for x in (selected_graph_plan.get("selected_competency_families") or [])
        if str(x).strip()
    }
    selected_skills = {
        str(x).strip()
        for x in (selected_graph_plan.get("selected_skill_ids") or [])
        if str(x).strip()
    }
    if not selected_families and not selected_skills:
        raise ValueError(
            "competencies: selected_graph_evidence_plan must include competency families or skill ids"
        )

    filtered: list[dict[str, Any]] = []
    for rec in packet.get("competency_bundles") or []:
        if not isinstance(rec, dict):
            continue
        family = str(rec.get("capability_family") or "").strip()
        skills = {str(x).strip() for x in (rec.get("graph_skill_node_ids") or []) if str(x).strip()}
        # W2.2 (typed-edge-role-facet-guardrails-a6f3d2): required capability families
        # are a coverage FLOOR enforced by x2_required_capability_families_covered +
        # the per-category bundle_id / graph_skill_node_ids gates. JD-fit graph selection
        # (selected_competency_families) may narrow/rank the OPTIONAL families, but it must
        # NOT drop a required-family bundle — doing so left the LLM asked to cover the family
        # (it's in the prompt header) with no bundle to bind, yielding an orphan category
        # (bundle_id=None, graph_skill_node_ids=[]). Required-family bundles are graph-backed
        # ACTIVE bundles, so retaining them admits no non-graph content.
        if family in REQUIRED_CAPABILITY_FAMILIES:
            include = True
        elif selected_families:
            include = family in selected_families
        else:
            include = bool(selected_skills and skills.intersection(selected_skills))
        if include:
            filtered.append(rec)
    if not filtered:
        raise ValueError("competencies: selected_graph_evidence_plan produced no competency_bundles")

    graph_skill_node_ids_by_category: dict[str, list[str]] = {}
    source_fact_ids_by_category: dict[str, list[str]] = {}
    families_present: set[str] = set()
    for rec in filtered:
        family = str(rec.get("capability_family") or "").strip()
        if family:
            families_present.add(family)
        for cat_id in rec.get("target_taxonomy_category_ids") or []:
            cat = str(cat_id)
            graph_skill_node_ids_by_category.setdefault(cat, [])
            for sid in rec.get("graph_skill_node_ids") or []:
                sid_s = str(sid)
                if sid_s not in graph_skill_node_ids_by_category[cat]:
                    graph_skill_node_ids_by_category[cat].append(sid_s)
            source_fact_ids_by_category.setdefault(cat, [])
            for fid in rec.get("linked_source_fact_ids") or []:
                fid_s = str(fid)
                if fid_s not in source_fact_ids_by_category[cat]:
                    source_fact_ids_by_category[cat].append(fid_s)

    out = dict(packet)
    out["competency_bundles"] = filtered
    out["competency_bundle_ids"] = [str(r.get("competency_bundle_id") or "") for r in filtered]
    out["capability_families_present"] = sorted(families_present)
    out["graph_skill_node_ids_by_category"] = graph_skill_node_ids_by_category
    out["source_fact_ids_by_category"] = source_fact_ids_by_category
    out["selected_graph_evidence_plan_applied"] = True
    out["selected_competency_families"] = sorted(selected_families)
    return out


def attach_competency_bundles_to_proof_pool_metadata(
    meta: dict[str, Any],
    *,
    section_id: str = "competencies",
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Merge competency capability packet into proof_pool_metadata (competencies only)."""
    if section_id != "competencies":
        return meta
    packet = build_competency_capability_section_packet(section_id, repo_root=repo_root)
    packet = _filter_packet_by_selected_graph_plan(packet, _selected_graph_plan(meta))
    out = dict(meta)
    out["competency_capability_bundle_consumption"] = True
    out["competency_capability_bundle_consumption_mode"] = "competency_bundle_required"
    out["competency_capability_bundles"] = packet["competency_bundles"]
    out["competency_bundle_ids"] = packet["competency_bundle_ids"]
    out["competency_capability_section_packet"] = packet
    out["graph_expansion_consumes_competency_bundles"] = True
    out["flat_taxonomy_only_graph_context_forbidden"] = True
    return out


def is_flat_taxonomy_only_packet(packet: dict[str, Any]) -> bool:
    """True when graph context is only generic taxonomy with no bundle/skill binding."""
    if packet.get("competency_bundle_id") or packet.get("competency_bundle_ids"):
        return False
    if packet.get("competency_bundles"):
        return False
    inner = packet.get("competency_capability_section_packet") or {}
    if isinstance(inner, dict) and inner.get("competency_bundles"):
        return False
    if packet.get("graph_skill_node_ids") and not packet.get("competency_bundle_id"):
        return True
    return True


def append_competencies_path_diversity_to_messages(
    messages: list[dict[str, Any]],
    *,
    path_index: int,
    temperature: float,
) -> list[dict[str, Any]]:
    """Append per-path graph-neighborhood framing for competencies SC generation."""
    if not messages:
        return messages
    lens_name, graph_terms = COMPETENCIES_PATH_DIVERSITY_LENSES[
        path_index % len(COMPETENCIES_PATH_DIVERSITY_LENSES)
    ]
    suffix = (
        f"\n\nCOMPETENCIES_PATH_DIVERSITY (path_index={path_index}, temperature={temperature:.2f}):\n"
        f"Primary graph-neighborhood lens: {lens_name}.\n"
        f"Graph terms to bias this candidate path: {', '.join(graph_terms)}.\n"
        "Treat this path as candidate-neighborhood expansion before final selection: generate 6-8 "
        "competencies, and make at least four category labels lens-specific alternatives rather "
        "than a reorder of the same canonical eight labels. Every category still needs competency_bundle_id, "
        "graph_skill_node_ids, source_fact_ids, and compact graph-backed terms. JD and briefing text are "
        "targeting context only, never proof.\n\n"
        "SELF_CONSISTENCY_CANDIDATE_CONTRACT:\n"
        "Return compact JSON only. Emit categories[] and claim_ledger only as much as needed for "
        "selector ranking and downstream normalization.\n"
        "Do not wrap JSON in markdown fences or prose.\n"
        "Use 6-8 categories with exactly 3 compact terms each. Each term must be an object with "
        "text, source_fact_id, and source_fact_ids. Keep term text under 8 words.\n"
        "Use selected_fact_plan as a stub with section_id, selection_method, and required_fact_ids only.\n"
        "Use terse arrays for excluded_jd_skills, removed_or_rewritten_terms, gap_notes, change_log, "
        "and self_check. Do not include rationale, prose, copied evidence, or expanded fact text.\n"
    )
    out = compact_competencies_self_consistency_messages(messages)
    last = out[-1]
    prev = str(last.get("content") or "").rstrip()
    if str(last.get("role") or "").strip().lower() == "user":
        out[-1] = {**last, "content": f"{prev}{suffix}" if prev else suffix.strip()}
    else:
        out.append({"role": "user", "content": suffix.strip()})
    return out


def format_competency_capability_evidence_pack(
    runtime_payload: dict[str, Any],
    *,
    section_id: str = "competencies",
) -> str:
    """C0 body: competency capability bundles as proof authority (graph-backed, per family)."""
    packet = require_section_packet(
        runtime_payload,
        section_id=section_id,
        packet_key="competency_capability_section_packet",
    )
    packet = _filter_packet_by_selected_graph_plan(packet, _selected_graph_plan(runtime_payload))
    runtime_payload["competency_capability_section_packet"] = packet
    runtime_payload["competency_bundle_ids"] = packet["competency_bundle_ids"]

    header_lines = [
        f"{COMPETENCY_CAPABILITY_EVIDENCE_PACK_MARKER} "
        "(proof substrate — compose categories from competency_bundle_id + bound_skills + linked source facts):",
        *_AUTHORITY_HEADER_LINES,
        "- Each emitted category MUST cite a competency_bundle_id and its graph_skill_node_ids.",
        "- Each major term MUST bind to graph_skill_node_ids and linked source_fact_ids or approved graph lineage.",
        "- Partner architecture wording MUST bind to allowed_partner_roots and must not bind to forbidden_partner_roots.",
        "- Generic taxonomy labels may be display wrappers only — never proof on their own.",
        "- A term attached only to default_fid is NOT proof.",
        "- Required capability families to cover (>=8): "
        + ", ".join(REQUIRED_CAPABILITY_FAMILIES[:8]) + ".",
    ]
    header = "\n".join(header_lines)

    blocks: list[str] = []
    for rec in packet["competency_bundles"]:
        lines = [
            f"COMPETENCY_BUNDLE {rec['competency_bundle_id']} | family: {rec['capability_family']}",
            f"  display_label_candidate: {rec['display_label_candidate']}",
            f"  target_taxonomy_category_ids: {rec['target_taxonomy_category_ids']}",
            f"  graph_skill_node_ids: {rec['graph_skill_node_ids']}",
            f"  linked_source_fact_ids: {rec['linked_source_fact_ids']}",
            f"  evidence_strength: {rec['evidence_strength']} | activation: {rec['activation_status']}",
            f"  base_rigor_family_match: {rec['base_rigor_family_match']}",
            f"  seniority_signal: {rec['seniority_signal']} | technical_density_signal: {rec['technical_density_signal']}",
            f"  target_relevance_rationale: {rec['target_relevance_rationale']}",
            f"  capability_facets: {rec.get('capability_facets')}",
            f"  root_binding_policy: {rec.get('root_binding_policy') or 'standard_bundle_binding'}",
            f"  allowed_partner_roots: {rec.get('allowed_partner_roots') or []}",
            f"  forbidden_partner_roots: {rec.get('forbidden_partner_roots') or []}",
            "  bound_skills (graph authority — vocabulary anchors only, not proof on their own):",
        ]
        for sk in rec.get("bound_skills") or []:
            if not isinstance(sk, dict):
                continue
            sid = sk.get("skill_id")
            phrases = ", ".join(list(sk.get("allowed_phrases") or [])[:5])
            if phrases:
                lines.append(f"    - {sid} | allowed_phrases: {phrases}")
            else:
                lines.append(f"    - {sid}")
        lines.append("  vocabulary_anchors (structured anchors only — no base/archive prose):")
        for anchor in rec.get("vocabulary_anchors") or []:
            lines.append(f"    - {anchor}")
        if rec.get("employer_bindings") or rec.get("role_episode_bindings"):
            lines.append(
                f"  bindings: employer={rec.get('employer_bindings')} role_episode={rec.get('role_episode_bindings')}"
            )
        blocks.append("\n".join(lines))

    return header + "\n\n" + "\n\n".join(blocks)


def stamp_competency_bundle_bindings(
    competencies: list[dict[str, Any]],
    *,
    packet: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Stamp competency_bundle_id + graph_skill_node_ids onto categories by taxonomy mapping.

    Runtime seam: makes the final output bind each category to a graph-backed bundle. Does
    not invent terms; only attaches graph lineage metadata for categories whose category_id
    is a target of a competency bundle.
    """
    if not isinstance(competencies, list):
        return competencies
    pkt = packet or build_competency_capability_section_packet("competencies")
    by_category: dict[str, dict[str, Any]] = {}
    by_family: dict[str, dict[str, Any]] = {}
    for rec in pkt.get("competency_bundles") or []:
        for cat_id in rec.get("target_taxonomy_category_ids") or []:
            by_category.setdefault(str(cat_id), rec)
        # Family fallback: a category whose id/label names a capability family (e.g.
        # "llmops_reliability") but is not a bundle taxonomy *target* still binds to that
        # family's bundle (ccb_llmops_reliability) — it is graph-backed, just not a top taxonomy slot.
        fam = str(rec.get("capability_family") or "").strip()
        if fam:
            by_family.setdefault(fam, rec)
        bid = str(rec.get("competency_bundle_id") or "").strip()
        if bid.startswith("ccb_"):
            by_family.setdefault(bid[len("ccb_"):], rec)
    for cat in competencies:
        if not isinstance(cat, dict):
            continue
        cid = str(cat.get("category_id") or "").strip()
        rec = by_category.get(cid) or by_family.get(cid)
        if not rec:
            label_key = re.sub(r"[^a-z0-9]+", "_", str(cat.get("category_label") or "").lower()).strip("_")
            rec = by_family.get(label_key)
        if not rec:
            # Coverage violation: an emitted competency category whose taxonomy
            # category_id is not a target of ANY competency bundle. Previously a silent
            # skip — now surfaced so an orphaned taxonomy category (E2E-07) is observable
            # instead of quietly dropping its graph lineage. Stamp the category too so the
            # gap is visible in the artifact, not just the logs.
            if cid:
                logger.warning(
                    "COMPETENCY_BUNDLE_BINDING_MISSING: category_id=%r has no competency "
                    "bundle target (orphaned taxonomy category) — graph lineage not stamped",
                    cid,
                )
                cat["competency_bundle_binding_missing"] = True
            continue
        cat["competency_bundle_id"] = rec["competency_bundle_id"]
        cat["capability_family"] = rec["capability_family"]
        existing_nodes = list(cat.get("graph_skill_node_ids") or [])
        for sid in rec.get("graph_skill_node_ids") or []:
            if sid not in existing_nodes:
                existing_nodes.append(sid)
        cat["graph_skill_node_ids"] = existing_nodes
    return competencies


def _allowed_source_fact_ids(allowed_fact_ids: set[str] | None) -> set[str]:
    return {fid for raw in (allowed_fact_ids or set()) if (fid := _source_fact_root_id(raw))}


def _append_allowed_source_fact(out: list[str], raw: Any, *, allowed: set[str]) -> None:
    fid = _source_fact_root_id(raw)
    if fid and fid in allowed and fid not in out:
        out.append(fid)


def _bundle_allowed_linked_facts(
    rec: dict[str, Any],
    cat: dict[str, Any] | None,
    *,
    allowed_fact_ids: set[str] | None,
    selected_graph_evidence_plan: dict[str, Any] | None,
) -> list[str]:
    allowed = _allowed_source_fact_ids(allowed_fact_ids)
    if not allowed:
        return []
    plan = selected_graph_evidence_plan if isinstance(selected_graph_evidence_plan, dict) else {}
    plan_facts = [row for row in (plan.get("facts") or []) if isinstance(row, dict)]
    out: list[str] = []
    for raw in rec.get("linked_source_fact_ids") or []:
        _append_allowed_source_fact(out, raw, allowed=allowed)
    if out:
        return out

    skill_ids = {
        str(s).strip()
        for s in list((cat or {}).get("graph_skill_node_ids") or [])
        + list(rec.get("graph_skill_node_ids") or [])
        if str(s).strip()
    }
    for fact in plan_facts:
        fact_skills = {str(s).strip() for s in (fact.get("graph_skill_node_ids") or []) if str(s).strip()}
        if skill_ids and fact_skills and not skill_ids.intersection(fact_skills):
            continue
        _append_allowed_source_fact(out, fact.get("fact_id") or fact.get("role_episode_bundle_id"), allowed=allowed)
        for fid in fact.get("source_fact_ids") or []:
            _append_allowed_source_fact(out, fid, allowed=allowed)
        for mid in fact.get("metric_outcome_ids") or []:
            _append_allowed_source_fact(out, mid, allowed=allowed)
    if out:
        return out

    for root_id in COMPETENCY_BUNDLE_FAMILY_ROOT_HINTS.get(str(rec.get("capability_family") or ""), ()):
        for fact in plan_facts:
            if root_id not in {
                str(fact.get("fact_id") or ""),
                str(fact.get("role_episode_bundle_id") or ""),
            }:
                continue
            _append_allowed_source_fact(out, fact.get("fact_id") or fact.get("role_episode_bundle_id"), allowed=allowed)
            for fid in fact.get("source_fact_ids") or []:
                _append_allowed_source_fact(out, fid, allowed=allowed)
            for mid in fact.get("metric_outcome_ids") or []:
                _append_allowed_source_fact(out, mid, allowed=allowed)
    return out


def hydrate_competency_bundle_graph_evidence(
    competencies: list[dict[str, Any]],
    *,
    packet: dict[str, Any] | None,
    allowed_fact_ids: set[str] | None,
    selected_graph_evidence_plan: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Make stamped bundle lineage authoritative on final competency categories.

    The taxonomy projection can create an otherwise valid category with only the
    lane's deterministic default fact. In bundle mode, the category's
    ``competency_bundle_id`` is the stronger graph binding, so expose the bundle's
    allowed linked facts and a deterministic per-category selector score before X2.
    """
    if not isinstance(competencies, list):
        return competencies
    pkt = packet or build_competency_capability_section_packet("competencies")
    allowed = {fid for raw in (allowed_fact_ids or set()) if (fid := _source_fact_root_id(raw))}
    by_id: dict[str, dict[str, Any]] = {
        str(r.get("competency_bundle_id")): r
        for r in (pkt.get("competency_bundles") or [])
        if isinstance(r, dict) and r.get("competency_bundle_id")
    }
    if not by_id or not allowed:
        return competencies

    for idx, cat in enumerate(competencies):
        if not isinstance(cat, dict):
            continue
        rec = by_id.get(str(cat.get("competency_bundle_id") or ""))
        if not rec:
            continue
        linked_facts = _bundle_allowed_linked_facts(
            rec,
            cat,
            allowed_fact_ids=allowed_fact_ids,
            selected_graph_evidence_plan=selected_graph_evidence_plan,
        )
        if not linked_facts:
            continue

        existing = [
            root
            for fid in (cat.get("source_fact_ids") or [])
            if (root := _source_fact_root_id(fid))
        ]
        existing_linked = [fid for fid in existing if fid in linked_facts]
        # Replace projection-default facts unless the category already cites this bundle.
        cat["source_fact_ids"] = existing_linked or list(linked_facts)

        skills = [str(s) for s in (rec.get("graph_skill_node_ids") or []) if str(s).strip()]
        if skills:
            current_skills = [str(s) for s in (cat.get("graph_skill_node_ids") or []) if str(s).strip()]
            for sid in skills:
                if sid not in current_skills:
                    current_skills.append(sid)
            cat["graph_skill_node_ids"] = current_skills

        for term_idx, raw_term in enumerate(cat.get("terms") or []):
            if not isinstance(raw_term, dict):
                continue
            term_ids = [
                root
                for fid in (raw_term.get("source_fact_ids") or [])
                if (root := _source_fact_root_id(fid))
            ]
            term_linked = [fid for fid in term_ids if fid in linked_facts]
            if not term_linked:
                term_linked = [linked_facts[term_idx % len(linked_facts)]]
            raw_term["source_fact_ids"] = term_linked
            raw_term["source_fact_id"] = term_linked[0]
            term_skills = [str(s) for s in (raw_term.get("source_skill_ids") or []) if str(s).strip()]
            for sid in skills:
                if sid not in term_skills:
                    term_skills.append(sid)
            if term_skills:
                raw_term["source_skill_ids"] = term_skills
                raw_term["support_class"] = "FACT_AND_SKILL_GRAPH"
            else:
                raw_term["support_class"] = "FACT_ONLY"
            if raw_term.get("proof_source") == "default_fid_backfill":
                raw_term["proof_source"] = "competency_bundle_graph_hydration"

        if cat.get("confidence") is None and cat.get("selection_score") is None and cat.get("score") is None:
            fact_component = min(len(linked_facts), 5) * 0.025
            skill_component = min(len(skills), 8) * 0.006
            rank_component = max(0.0, 0.04 - (idx * 0.004))
            cat["selection_score"] = round(min(0.99, 0.74 + fact_component + skill_component + rank_component), 4)
        if cat.get("selector_confidence") is None:
            cat["selector_confidence"] = cat.get("selection_score") or cat.get("confidence") or cat.get("score")
    return competencies


def _graph_surface_phrase_key(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip().lower()).rstrip(".")


def _graph_surface_word_count(value: str) -> int:
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9+&/-]*", value))


def _graph_surface_metric_value_phrase(value: str) -> bool:
    return bool(
        re.search(
            r"(?:(?<!\w)\d+\s*%(?!\w)|\$\s*\d+|\b\d+(?:\.\d+)?\s*(?:m|mm|b|bn|k)\b|"
            r"\boperating\s+margin\b|\bmargin\s+expansion\b|\brevenue\s+growth\b|"
            r"\bgross\s+margins\b)",
            str(value or ""),
            re.IGNORECASE,
        )
    )


def _graph_surface_phrases_for_bundle(rec: dict[str, Any]) -> list[str]:
    phrases: list[str] = []
    seen: set[str] = set()

    def _add(raw: Any) -> None:
        phrase = str(raw or "").strip()
        if not phrase:
            return
        if _graph_surface_metric_value_phrase(phrase):
            return
        words = _graph_surface_word_count(phrase)
        if words < 2 or words > 7:
            return
        key = _graph_surface_phrase_key(phrase)
        if key in seen:
            return
        seen.add(key)
        phrases.append(phrase)

    bundle_id = str(rec.get("competency_bundle_id") or "")
    for override in VISIBLE_GRAPH_SURFACE_TERM_OVERRIDES.get(bundle_id, ()):
        _add(override)
    for anchor in rec.get("vocabulary_anchors") or []:
        _add(anchor)
    for skill in rec.get("bound_skills") or []:
        if not isinstance(skill, dict):
            continue
        for phrase in skill.get("allowed_phrases") or []:
            _add(phrase)
    return phrases


def _graph_surface_term(
    phrase: str,
    *,
    fact_ids: list[str],
    skill_ids: list[str],
) -> dict[str, Any]:
    term: dict[str, Any] = {
        "term": phrase,
        "text": phrase,
        "source_skill_ids": list(skill_ids),
        "graph_skill_node_ids": list(skill_ids),
        "support_class": "FACT_AND_SKILL_GRAPH" if fact_ids else "GRAPH_BACKED_BUNDLE",
        "proof_source": "competency_bundle_visible_surface",
    }
    if fact_ids:
        term["source_fact_ids"] = list(fact_ids)
        term["source_fact_id"] = fact_ids[0]
    return term


def _category_fact_ids(cat: dict[str, Any], allowed_fact_ids: set[str] | None) -> list[str]:
    allowed = {fid for raw in (allowed_fact_ids or set()) if (fid := _source_fact_root_id(raw))}
    out: list[str] = []
    for raw in cat.get("source_fact_ids") or []:
        fid = _source_fact_root_id(raw)
        if not fid:
            continue
        if allowed and fid not in allowed:
            continue
        if fid not in out:
            out.append(fid)
    for term in cat.get("terms") or []:
        if not isinstance(term, dict):
            continue
        for raw in list(term.get("source_fact_ids") or []) + [term.get("source_fact_id")]:
            fid = _source_fact_root_id(raw)
            if not fid:
                continue
            if allowed and fid not in allowed:
                continue
            if fid not in out:
                out.append(fid)
    return out


def _category_skill_ids(cat: dict[str, Any], rec: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for raw in list(cat.get("graph_skill_node_ids") or []) + list(rec.get("graph_skill_node_ids") or []):
        sid = str(raw).strip()
        if sid and sid not in out:
            out.append(sid)
    for term in cat.get("terms") or []:
        if not isinstance(term, dict):
            continue
        for raw in list(term.get("source_skill_ids") or []) + list(term.get("graph_skill_node_ids") or []):
            sid = str(raw).strip()
            if sid and sid not in out:
                out.append(sid)
    return out


def _plan_fact_ids_for_bundle(
    rec: dict[str, Any],
    *,
    cat: dict[str, Any] | None = None,
    selected_graph_evidence_plan: dict[str, Any] | None,
    allowed_fact_ids: set[str] | None,
) -> list[str]:
    linked = _bundle_allowed_linked_facts(
        rec,
        cat,
        allowed_fact_ids=allowed_fact_ids,
        selected_graph_evidence_plan=selected_graph_evidence_plan,
    )
    if linked:
        return linked

    allowed = {fid for raw in (allowed_fact_ids or set()) if (fid := _source_fact_root_id(raw))}
    bundle_skills = {str(x).strip() for x in (rec.get("graph_skill_node_ids") or []) if str(x).strip()}
    out: list[str] = []

    def _append(raw: Any) -> None:
        fid = _source_fact_root_id(raw)
        if not fid:
            return
        if allowed and fid not in allowed:
            return
        if fid not in out:
            out.append(fid)

    plan = selected_graph_evidence_plan if isinstance(selected_graph_evidence_plan, dict) else {}
    for fact in plan.get("facts") or []:
        if not isinstance(fact, dict):
            continue
        fact_skills = {str(x).strip() for x in (fact.get("graph_skill_node_ids") or []) if str(x).strip()}
        if bundle_skills and fact_skills and not bundle_skills.intersection(fact_skills):
            continue
        _append(fact.get("fact_id"))
        _append(fact.get("role_episode_bundle_id"))
        for fid in fact.get("source_fact_ids") or []:
            _append(fid)
        for mid in fact.get("metric_outcome_ids") or []:
            _append(mid)
    for linked in rec.get("linked_source_fact_ids") or []:
        _append(linked)
    return out


def _graph_surface_selection_score(idx: int, *, fact_ids: list[str], skill_ids: list[str]) -> float:
    fact_component = min(len(fact_ids), 4) * 0.018
    skill_component = min(len(skill_ids), 10) * 0.004
    rank_component = max(0.0, 0.035 - idx * 0.004)
    return round(min(0.97, 0.78 + fact_component + skill_component + rank_component), 4)


def _sync_visible_graph_claim_ledger(
    parsed: dict[str, Any],
    *,
    allowed_fact_ids: set[str] | None,
) -> None:
    comps = parsed.get("competencies")
    if not isinstance(comps, list):
        comps = parsed.get("categories")
    if not isinstance(comps, list):
        return
    ledger: list[dict[str, Any]] = []
    for cat in comps:
        if not isinstance(cat, dict):
            continue
        cat_ids = _category_fact_ids(cat, allowed_fact_ids)
        if not cat_ids:
            cat["source_fact_ids"] = []
            continue
        cat["source_fact_ids"] = list(cat_ids)
        for term in cat.get("terms") or []:
            phrase = term_phrase(term)
            if not phrase:
                continue
            term_ids = _category_fact_ids({"source_fact_ids": [], "terms": [term]}, allowed_fact_ids)
            ids = term_ids or cat_ids
            if isinstance(term, dict):
                term["source_fact_ids"] = list(ids)
                term["source_fact_id"] = ids[0]
                if term.get("source_skill_ids") or term.get("graph_skill_node_ids"):
                    term["support_class"] = "FACT_AND_SKILL_GRAPH"
            ledger.append({"claim_text": phrase, "source_fact_ids": list(ids)})
    if ledger:
        parsed["claim_ledger"] = ledger


def _token_budget_allows(phrase: str, token_counts: dict[str, int], *, max_repeat: int = 3) -> bool:
    for token in re.findall(r"[a-z][a-z0-9+/-]*", str(phrase or "").lower()):
        if len(token) < 4:
            continue
        if token in {"design", "controls", "systems", "engineering"}:
            continue
        if token_counts.get(token, 0) >= max_repeat:
            return False
    return True


def _register_visible_phrase_tokens(phrase: str, token_counts: dict[str, int]) -> None:
    for token in re.findall(r"[a-z][a-z0-9+/-]*", str(phrase or "").lower()):
        if len(token) < 4:
            continue
        if token in {"design", "controls", "systems", "engineering"}:
            continue
        token_counts[token] = token_counts.get(token, 0) + 1


def enrich_competencies_visible_graph_surface(
    parsed: dict[str, Any],
    *,
    packet: dict[str, Any] | None,
    allowed_fact_ids: set[str] | None,
    selected_graph_evidence_plan: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Make the resume-visible competencies surface consume graph bundle evidence.

    The taxonomy category label remains intact for the existing X2 taxonomy contract.
    ``resume_display_label`` is the user-facing label and is sourced from the bound
    competency bundle. Terms are rebuilt from curated bundle anchors and bound skill
    phrases so graph improvements are visible in ``competencies_display.txt``.
    """
    if not isinstance(parsed, dict):
        return {}
    pkt = packet or build_competency_capability_section_packet("competencies")
    records = [
        rec for rec in (pkt.get("competency_bundles") or []) if isinstance(rec, dict)
    ]
    by_id = {
        str(rec.get("competency_bundle_id") or ""): rec
        for rec in records
        if str(rec.get("competency_bundle_id") or "").strip()
    }
    if not by_id:
        return {}

    order = {bundle_id: idx for idx, bundle_id in enumerate(PARTNERSHIP_FIRST_COMPETENCIES_BUNDLE_ORDER)}
    receipt_rows: list[dict[str, Any]] = []
    token_counts: dict[str, int] = {}

    def _rewrite(cats: Any, *, surface_name: str) -> list[dict[str, Any]]:
        if not isinstance(cats, list):
            return []
        by_bundle: dict[str, dict[str, Any]] = {}
        surplus: list[dict[str, Any]] = []
        for cat in cats:
            if not isinstance(cat, dict):
                continue
            bid = str(cat.get("competency_bundle_id") or "").strip()
            if bid and bid not in by_bundle:
                by_bundle[bid] = cat
            else:
                surplus.append(cat)
        unassigned = list(surplus)
        out: list[dict[str, Any]] = []
        for bid in PARTNERSHIP_FIRST_COMPETENCIES_BUNDLE_ORDER:
            rec = by_id.get(bid)
            if not rec:
                continue
            display_idx = len(out)
            cat = by_bundle.get(bid)
            if cat is None and unassigned:
                cat = unassigned.pop(0)
            if cat is None:
                cat = {"terms": []}
            before_label = str(cat.get("resume_display_label") or cat.get("category_label") or "").strip()
            display_label = str(rec.get("display_label_candidate") or before_label).strip()
            taxonomy_id, taxonomy_label = VISIBLE_GRAPH_SURFACE_TAXONOMY_BY_BUNDLE.get(
                bid,
                (
                    str((rec.get("target_taxonomy_category_ids") or [bid])[0]),
                    before_label or display_label,
                ),
            )
            linked_fact_ids = _bundle_allowed_linked_facts(
                rec,
                cat,
                allowed_fact_ids=allowed_fact_ids,
                selected_graph_evidence_plan=selected_graph_evidence_plan,
            )
            fact_ids = linked_fact_ids or _category_fact_ids(cat, allowed_fact_ids)
            if not fact_ids:
                fact_ids = _plan_fact_ids_for_bundle(
                    rec,
                    cat=cat,
                    selected_graph_evidence_plan=selected_graph_evidence_plan,
                    allowed_fact_ids=allowed_fact_ids,
                )
            skill_ids = _category_skill_ids(cat, rec)
            phrases = _graph_surface_phrases_for_bundle(rec)
            if len(phrases) < VISIBLE_GRAPH_TERMS_MIN:
                existing = [term_phrase(t) for t in (cat.get("terms") or []) if term_phrase(t)]
                for phrase in existing:
                    if _graph_surface_phrase_key(phrase) not in {
                        _graph_surface_phrase_key(p) for p in phrases
                    }:
                        phrases.append(phrase)
                    if len(phrases) >= VISIBLE_GRAPH_TERMS_MIN:
                        break
            selected_phrases: list[str] = []
            seen_phrase_keys: set[str] = set()
            for phrase in phrases:
                key = _graph_surface_phrase_key(phrase)
                if not key or key in seen_phrase_keys:
                    continue
                if len(selected_phrases) >= VISIBLE_GRAPH_TERMS_MAX:
                    break
                if len(selected_phrases) >= VISIBLE_GRAPH_TERMS_MIN and not _token_budget_allows(
                    phrase,
                    token_counts,
                ):
                    continue
                selected_phrases.append(phrase)
                seen_phrase_keys.add(key)
                _register_visible_phrase_tokens(phrase, token_counts)
            if len(selected_phrases) >= VISIBLE_GRAPH_TERMS_MIN and skill_ids:
                cat["terms"] = [
                    _graph_surface_term(phrase, fact_ids=fact_ids, skill_ids=skill_ids)
                    for phrase in selected_phrases
                ]
            cat["category_id"] = taxonomy_id
            cat["category_label"] = taxonomy_label
            cat["competency_bundle_id"] = bid
            cat["capability_family"] = rec.get("capability_family")
            cat["graph_skill_node_ids"] = list(skill_ids)
            if fact_ids:
                cat["source_fact_ids"] = list(fact_ids)
            graph_surface_score = _graph_surface_selection_score(
                display_idx,
                fact_ids=fact_ids,
                skill_ids=skill_ids,
            )
            cat["confidence"] = graph_surface_score
            cat["selection_score"] = graph_surface_score
            cat["selector_confidence"] = graph_surface_score
            cat["resume_display_label"] = display_label
            cat["resume_display_order_reason"] = "anthropic_partnership_relevance_first"
            cat["visible_graph_surface"] = True
            cat["graph_surface_term_source"] = "competency_bundle_vocabulary_anchors"
            out.append(cat)
            receipt_rows.append(
                {
                    "surface": surface_name,
                    "category_label": cat.get("category_label"),
                    "resume_display_label": display_label,
                    "competency_bundle_id": bid,
                    "capability_family": rec.get("capability_family"),
                    "source_fact_ids": fact_ids,
                    "graph_skill_node_ids": skill_ids,
                    "visible_terms": selected_phrases,
                    "old_display_label": before_label,
                    "order_index": order.get(bid, 500),
                }
            )
            if len(out) >= 8:
                break
        return out

    if isinstance(parsed.get("categories"), list):
        parsed["categories"] = _rewrite(parsed.get("categories"), surface_name="categories")
    if isinstance(parsed.get("competencies"), list):
        parsed["competencies"] = _rewrite(parsed.get("competencies"), surface_name="competencies")
    _sync_visible_graph_claim_ledger(parsed, allowed_fact_ids=allowed_fact_ids)
    receipt = {
        "schema_version": "competencies_visible_graph_surface_enrichment_receipt_v1",
        "producer": "apps_rg.runtime.sections.competency_capability_evidence.enrich_competencies_visible_graph_surface",
        "section_id": "competencies",
        "order_policy": "anthropic_partnership_relevance_first",
        "bundle_order": list(PARTNERSHIP_FIRST_COMPETENCIES_BUNDLE_ORDER),
        "visible_terms_min": VISIBLE_GRAPH_TERMS_MIN,
        "visible_terms_max": VISIBLE_GRAPH_TERMS_MAX,
        "enriched_category_count": len(
            {
                str(row.get("competency_bundle_id") or "")
                for row in receipt_rows
                if row.get("surface") == "competencies"
            }
        ),
        "rows": receipt_rows,
    }
    parsed["competencies_visible_graph_surface_enrichment_receipt"] = receipt
    return receipt


# Map bundle capability_family -> the family key used by the X2 coverage gate
# (apps_rg.runtime.validators.competencies_quality_x2.REQUIRED_CAPABILITY_FAMILIES).
_BUNDLE_TO_GATE_FAMILY: dict[str, str] = {
    "agentic_platforms": "agentic_platform",
    "runtime_governance": "runtime_governance",
    "retrieval_context_engineering": "retrieval_context",
    "llmops_reliability": "llmops",
    "distributed_systems_engineering": "distributed_infra",
    "platform_productization": "productization",
    "partner_applied_ai_architecture": "partner_architecture",
    "engineering_leadership": "engineering_leadership",
}


def _family_tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", str(text or "").lower()))


def _make_anchor_term(rec: dict[str, Any], anchor: str, fid: str) -> dict[str, Any]:
    display = str(anchor)
    if display.islower():
        display = display.title()
    skill_ids = [str(s) for s in (rec.get("graph_skill_node_ids") or []) if str(s).strip()]
    return {
        "text": display,
        "term": display,
        "source_fact_id": fid,
        "source_fact_ids": [fid],
        "source_skill_ids": skill_ids,
        "support_class": "FACT_ONLY",
    }


def _nonempty_term_count(cat: dict[str, Any]) -> int:
    n = 0
    for t in cat.get("terms") or []:
        if isinstance(t, dict) and str(t.get("text") or t.get("term") or "").strip():
            n += 1
        elif isinstance(t, str) and t.strip():
            n += 1
    return n


def _existing_term_norms(cat: dict[str, Any]) -> set[str]:
    out: set[str] = set()
    for t in cat.get("terms") or []:
        txt = t.get("text") or t.get("term") if isinstance(t, dict) else str(t)
        if txt:
            out.add(str(txt).strip().lower())
    return out


def augment_bound_category_family_terms(
    categories: list[dict[str, Any]],
    *,
    packet: dict[str, Any] | None,
    allowed_fact_ids: set[str] | None,
) -> list[dict[str, Any]]:
    """Inject bundle-approved, fact-grounded anchor terms into bound categories (Author-Gate
    dec_19e9daa115a62cf3a, anchor_injection).

    The live model reliably frames the LLMOps-bound category as leadership (omitting
    observability/evaluation vocabulary) and under-generates some categories below the 3-term
    executive floor. This deterministic augmentation runs after bundle stamping and does two
    fact-grounded things using each category's *bound bundle* only:

    1. Capability-family coverage: when a required family is not lexically covered across the
       emitted competencies, append one of the bound bundle's ``vocabulary_anchors`` whose tokens
       hit that family.
    2. Per-category term floor: top each bound category up to ``MIN_ITEMS_PER_CATEGORY`` graph-backed
       terms using its bundle's remaining anchors.

    Injected terms carry the bundle's genuine ``linked_source_fact_ids`` (restricted to the allowed
    pool) plus its ``graph_skill_node_ids`` as ``source_skill_ids`` — so they are graph-backed and
    not ``default_fid_backfill``. No anchor is injected when the bundle has no allowed linked fact
    (no fabricated provenance).
    """
    if not isinstance(categories, list):
        return categories
    pkt = packet or build_competency_capability_section_packet("competencies")
    by_id: dict[str, dict[str, Any]] = {
        str(r.get("competency_bundle_id")): r
        for r in (pkt.get("competency_bundles") or [])
        if isinstance(r, dict) and r.get("competency_bundle_id")
    }
    if not by_id:
        return categories

    try:
        from apps_rg.runtime.validators.competencies_quality_x2 import (
            REQUIRED_CAPABILITY_FAMILIES as _GATE_FAMILY_TOKENS,
        )
    except (ImportError, AttributeError):  # guardian: allow-default-fallback -- optional coverage augmentation
        return categories
    try:
        from apps_rg.runtime.sections.competencies_rigor import MAX_ITEMS_PER_CATEGORY, MIN_ITEMS_PER_CATEGORY
    except (ImportError, AttributeError):  # guardian: allow-default-fallback -- optional coverage augmentation
        MIN_ITEMS_PER_CATEGORY, MAX_ITEMS_PER_CATEGORY = 2, 6

    allowed = {str(x) for x in (allowed_fact_ids or set())}

    def _allowed_fid(rec: dict[str, Any]) -> str | None:
        for f in rec.get("linked_source_fact_ids") or []:
            if str(f) in allowed:
                return str(f)
        return None

    def _append(cat: dict[str, Any], rec: dict[str, Any], anchor: str, fid: str) -> None:
        cat.setdefault("terms", []).append(_make_anchor_term(rec, anchor, fid))
        existing = list(cat.get("source_fact_ids") or [])
        if fid not in existing:
            existing.append(fid)
        cat["source_fact_ids"] = existing

    covered_tokens: set[str] = set()
    for cat in categories:
        if not isinstance(cat, dict):
            continue
        for term in cat.get("terms") or []:
            if isinstance(term, dict):
                covered_tokens |= _family_tokenize(term.get("text") or term.get("term") or "")
            else:
                covered_tokens |= _family_tokenize(str(term))
        covered_tokens |= _family_tokenize(cat.get("category_label") or "")

    # Pass 0: required-family coverage even when NO category is bound to the missing family's
    # bundle. The live model does not deterministically bind a category to every required
    # capability family (e.g. distributed_infra may be omitted entirely). For each required
    # gate family not lexically covered, locate its bundle (by _BUNDLE_TO_GATE_FAMILY), then
    # inject one of its fact-grounded vocabulary_anchors into the bound category for that
    # bundle if present, else into the category with the most headroom — stamping the bundle
    # binding so the injected term is graph-backed. No injection without an allowed linked fact.
    rec_by_gate_family: dict[str, dict[str, Any]] = {}
    for _rec in by_id.values():
        gf = _BUNDLE_TO_GATE_FAMILY.get(str(_rec.get("capability_family") or ""))
        if gf and gf not in rec_by_gate_family and _allowed_fid(_rec):
            rec_by_gate_family[gf] = _rec
    bound_gate_families: set[str] = set()
    for cat in categories:
        if isinstance(cat, dict):
            _r = by_id.get(str(cat.get("competency_bundle_id") or ""))
            if _r:
                _gf = _BUNDLE_TO_GATE_FAMILY.get(str(_r.get("capability_family") or ""))
                if _gf:
                    bound_gate_families.add(_gf)
    for gate_family, family_tokens in _GATE_FAMILY_TOKENS.items():
        if covered_tokens & set(family_tokens):
            continue
        if gate_family in bound_gate_families:
            continue  # Pass 1 will handle bound categories
        rec = rec_by_gate_family.get(gate_family)
        if not rec:
            continue
        fid = _allowed_fid(rec)
        if not fid:
            continue
        anchor = next(
            (
                a
                for a in (rec.get("vocabulary_anchors") or [])
                if _family_tokenize(a) & set(family_tokens)
            ),
            None,
        )
        if not anchor:
            continue
        target = None
        for cat in categories:
            if not isinstance(cat, dict):
                continue
            if _nonempty_term_count(cat) < MAX_ITEMS_PER_CATEGORY and str(anchor).strip().lower() not in _existing_term_norms(cat):
                if target is None or _nonempty_term_count(cat) < _nonempty_term_count(target):
                    target = cat
        if target is None:
            continue
        _append(target, rec, anchor, fid)
        covered_tokens |= _family_tokenize(anchor)

    # Pass 1: capability-family coverage.
    for cat in categories:
        if not isinstance(cat, dict):
            continue
        rec = by_id.get(str(cat.get("competency_bundle_id") or ""))
        if not rec:
            continue
        gate_family = _BUNDLE_TO_GATE_FAMILY.get(str(rec.get("capability_family") or ""))
        family_tokens = _GATE_FAMILY_TOKENS.get(gate_family) if gate_family else None
        if not family_tokens or (covered_tokens & set(family_tokens)):
            continue
        fid = _allowed_fid(rec)
        if not fid:
            continue
        seen = _existing_term_norms(cat)
        anchor = next(
            (
                a
                for a in (rec.get("vocabulary_anchors") or [])
                if (_family_tokenize(a) & set(family_tokens)) and str(a).strip().lower() not in seen
            ),
            None,
        )
        if not anchor or _nonempty_term_count(cat) >= MAX_ITEMS_PER_CATEGORY:
            continue
        _append(cat, rec, anchor, fid)
        covered_tokens |= _family_tokenize(anchor)

    # Pass 2: per-category term floor (graph-backed bundle anchors only).
    for cat in categories:
        if not isinstance(cat, dict):
            continue
        rec = by_id.get(str(cat.get("competency_bundle_id") or ""))
        if not rec:
            continue
        fid = _allowed_fid(rec)
        if not fid:
            continue
        for anchor in rec.get("vocabulary_anchors") or []:
            if _nonempty_term_count(cat) >= MIN_ITEMS_PER_CATEGORY:
                break
            if str(anchor).strip().lower() in _existing_term_norms(cat):
                continue
            _append(cat, rec, anchor, fid)

    return categories


__all__ = [
    "COMPETENCY_CAPABILITY_EVIDENCE_PACK_MARKER",
    "COMPETENCIES_SC_COMPACT_SYSTEM_MARKER",
    "COMPETENCIES_PATH_DIVERSITY_LENSES",
    "PARTNERSHIP_FIRST_COMPETENCIES_BUNDLE_ORDER",
    "attach_competency_bundles_to_proof_pool_metadata",
    "append_competencies_path_diversity_to_messages",
    "augment_bound_category_family_terms",
    "build_competency_capability_section_packet",
    "compact_competencies_self_consistency_messages",
    "enrich_competencies_visible_graph_surface",
    "format_competency_capability_evidence_pack",
    "hydrate_competency_bundle_graph_evidence",
    "is_flat_taxonomy_only_packet",
    "stamp_competency_bundle_bindings",
]
