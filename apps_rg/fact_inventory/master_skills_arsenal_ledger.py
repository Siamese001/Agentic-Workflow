"""Master skills arsenal ledger — skills layer beside atomic facts (apps_rg only)."""
from __future__ import annotations

import json
import re
from collections import Counter
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

REPO_REL = Path("apps_rg") / "fact_inventory" / "master_skills_arsenal_ledger.json"

REQUIRED_TOP_LEVEL: tuple[str, ...] = (
    "metadata",
    "support_levels",
    "visibility_rules",
    "activation_statuses",
    "pillars",
    "skill_rows",
    "actuarial_career_matrix",
    "partner_gtm_matrix",
    "role_family_projection_profiles",
    "validation_rules",
)

W4A_TOP_LEVEL: tuple[str, ...] = (
    "graph_metadata",
    "graph_layers",
    "graph_nodes",
    "graph_edges",
    "external_claim_policies",
    "agentic_runtime_matrix",
    "agentic_capability_domains",
    "graph_validation_rules",
    "resume_generation_policy",
)

NON_EXTERNAL_CLAIM_POLICIES = frozenset(
    {
        "internal_only",
        "pending_source_internal_only",
        "weak_snippet_internal_only",
        "repo_portfolio_not_resume_default",
    }
)

NON_EXTERNAL_SUPPORT_LEVELS = frozenset(
    {"INTERNAL_ONLY", "REPO_EVIDENCE_PORTFOLIO", "TARGETING_ONLY", "STYLE_ONLY", "BLOCKED"}
)

REQUIRED_SKILL_ROW_FIELDS: tuple[str, ...] = (
    "skill_id",
    "fact_id_links",
    "pillar",
    "subpillar",
    "career_stage",
    "source_resume_files",
    "source_snippets",
    "user_confirmed",
    "support_level",
    "role_family_weights",
    "allowed_phrases",
    "forbidden_phrases",
    "allowed_sections",
    "visibility_rule",
    "evidence_risk",
    "activation_status",
    "human_confirmation_required",
)

PROOF_FORBIDDEN_SUPPORT_LEVELS = frozenset(
    {"TARGETING_ONLY", "STYLE_ONLY", "BLOCKED", "USER_CONFIRMED_PENDING_SOURCE"}
)

JD_BRIEFING_FORBIDDEN_FACT_ID_PREFIXES = frozenset(
    {"jd", "briefing", "job_description", "targeting_jd", "targeting_briefing"}
)

C03_REQUIRED_GRAPH_HARDENING_NODES = frozenset(
    {
        "capability_metric_heterogeneity_selection",
        "capability_reverse_graph_traversal",
        "capability_sibling_rejection_receipts",
        "skill_c03_metric_heterogeneity_selection",
        "skill_c03_reverse_traversal_receipts",
        "skill_c03_sibling_skill_rejection_reasoning",
    }
)

C03_REQUIRED_GRAPH_HARDENING_EDGE_TYPES = frozenset(
    {
        "capability_domain_contains_skill",
        "skill_supported_by_fact",
    }
)

ISSUE_SAMPLE_LIMIT = 12
NON_SHAPE_GRAPH_HEALTH_ISSUE_CODES = frozenset(
    {"GRAPH_NODE_REQUIRED_SOURCE_REFS_MISSING"}
)

REGISTERED_GRAPH_NODE_TYPES = frozenset(
    {
        "atomic_proof_fact",
        "bullet_fact",
        "capability_domain",
        "career_epoch",
        "career_track",
        "certification_evidence",
        "domain_pillar",
        "employment",
        "experience_evidence",
        "external_claim_policy",
        "identity_north_star",
        "metric",
        "metric_bucket",
        "policy",
        "policy_rule",
        "repository_evidence",
        "resume_section_projection",
        "skill",
        "skill_row",
        "source_concept",
        "targeting_input",
    }
)

REGISTERED_GRAPH_EDGE_TYPES = frozenset(
    {
        "capability_domain_contains_skill",
        "career_track_contains_capability_domain",
        "career_track_contains_epoch",
        "career_track_contains_pillar",
        "career_track_precedes_career_track",
        "employment_hosts_fact",
        "employment_in_career_track",
        "employment_produces_skill",
        "epoch_contains_pillar",
        "epoch_contains_skill",
        "identity_supported_by_epoch",
        "identity_supported_by_pillar",
        "jd_briefing_targeting_only",
        "metric_bucket_contains_metric",
        "metric_supports_business_outcome",
        "pillar_contains_capability_domain",
        "pillar_phase_bridge",
        "pillar_section_eligibility",
        "projection_excludes_blocked_skill",
        "section_blocks_pending_source_skill",
        "section_blocks_skill_without_fact",
        "section_can_select_skill",
        "skill_allowed_in_section",
        "skill_can_surface_metric",
        "skill_external_claim_eligible",
        "skill_has_metric_bucket",
        "skill_projection_only_internal",
        "skill_reinforces_skill",
        "skill_requires_human_confirmation",
        "skill_supported_by_fact",
        "skill_supported_by_repo_evidence",
        "skill_supported_by_source_concept",
        "srfs_requires_fact_id_only",
    }
)

# These exact graph references are closed contract constants. Dynamic derived
# endpoints are registered only when another canonical ledger surface derives
# them; a matching name prefix alone never grants endpoint authority.
DERIVED_GRAPH_ENDPOINT_EXACT_TYPES: dict[str, str] = {
    "atomic_fact_default_external_proof": "external_claim_policy",
    "cross_career": "career_epoch",
    "jd_text": "targeting_input",
    "section:competencies": "resume_section_projection",
    "section:executive_summary": "resume_section_projection",
    "section:experience": "resume_section_projection",
    "section:selected_achievements": "resume_section_projection",
    "section_competencies": "resume_section_projection",
    "section_early_career": "resume_section_projection",
    "section_executive_summary": "resume_section_projection",
    "section_headline": "resume_section_projection",
    "section_ibm_bullets": "resume_section_projection",
    "section_ibm_narrative": "resume_section_projection",
    "section_insurtech_bullets": "resume_section_projection",
    "section_insurtech_narrative": "resume_section_projection",
    "section_unify_bullets": "resume_section_projection",
    "section_unify_narrative": "resume_section_projection",
}

_REPO_ENDPOINT_ID = re.compile(r"^repo_[0-9a-f]{6}$")
_SOURCE_REF_PREFIX_TYPES: tuple[tuple[str, str], ...] = (
    ("fact_", "atomic_proof_fact"),
    ("bul_", "bullet_fact"),
    ("cert_", "certification_evidence"),
    ("exp_", "experience_evidence"),
)

GRAPH_ONLY_SUPPORT_LEVELS = frozenset({"POLICY"})
GRAPH_ONLY_VISIBILITY_RULES = frozenset(
    {
        "internal_runtime_and_resume_when_fact_backed",
        "internal_runtime_only",
        "internal_traversal_only",
    }
)
GRAPH_ONLY_EXTERNAL_CLAIM_POLICIES = frozenset(
    {
        "allowed_with_fact_link",
        "derived_supported_with_fact",
        "internal_only",
        "internal_traversal_only",
    }
)
PROVENANCE_EXEMPT_EXTERNAL_CLAIM_POLICIES = frozenset(
    {
        "internal_only",
        "internal_traversal_only",
        "jd_briefing_targeting_only",
        "pending_source_internal_only",
        "repo_portfolio_not_resume_default",
        "skill_projection_not_proof",
        "weak_snippet_internal_only",
    }
)
REGISTERED_GRAPH_EVIDENCE_RISKS = frozenset({"low", "medium", "high"})
REGISTERED_GRAPH_EDGE_VALIDATION_STATUSES = frozenset({"validated", "ACTIVE_CONFIRMED"})

REGISTERED_GRAPH_EDGE_SIGNATURES: dict[str, frozenset[tuple[str, str]]] = {
    "capability_domain_contains_skill": frozenset(
        {
            ("capability_domain", "skill"),
            ("capability_domain", "skill_row"),
            ("domain_pillar", "skill_row"),
        }
    ),
    "career_track_contains_capability_domain": frozenset({("career_track", "capability_domain")}),
    "career_track_contains_epoch": frozenset({("career_track", "career_epoch")}),
    "career_track_contains_pillar": frozenset({("career_track", "domain_pillar")}),
    "career_track_precedes_career_track": frozenset({("career_track", "career_track")}),
    "employment_hosts_fact": frozenset({("employment", "atomic_proof_fact")}),
    "employment_in_career_track": frozenset({("employment", "career_track")}),
    "employment_produces_skill": frozenset(
        {("employment", "skill"), ("employment", "skill_row")}
    ),
    "epoch_contains_pillar": frozenset({("career_epoch", "domain_pillar")}),
    "epoch_contains_skill": frozenset(
        {("career_epoch", "skill"), ("career_epoch", "skill_row")}
    ),
    "identity_supported_by_epoch": frozenset({("identity_north_star", "career_epoch")}),
    "identity_supported_by_pillar": frozenset({("identity_north_star", "domain_pillar")}),
    "jd_briefing_targeting_only": frozenset({("targeting_input", "policy_rule")}),
    "metric_bucket_contains_metric": frozenset({("metric_bucket", "metric")}),
    "metric_supports_business_outcome": frozenset({("metric", "metric_bucket")}),
    "pillar_contains_capability_domain": frozenset({("domain_pillar", "capability_domain")}),
    "pillar_phase_bridge": frozenset({("domain_pillar", "domain_pillar")}),
    "pillar_section_eligibility": frozenset(
        {("domain_pillar", "resume_section_projection")}
    ),
    "projection_excludes_blocked_skill": frozenset({("skill_row", "policy")}),
    "section_blocks_pending_source_skill": frozenset(
        {("resume_section_projection", "policy_rule")}
    ),
    "section_blocks_skill_without_fact": frozenset(
        {("resume_section_projection", "policy_rule")}
    ),
    "section_can_select_skill": frozenset({("resume_section_projection", "skill")}),
    "skill_allowed_in_section": frozenset(
        {
            ("skill", "resume_section_projection"),
            ("skill_row", "resume_section_projection"),
        }
    ),
    "skill_can_surface_metric": frozenset({("skill", "metric")}),
    "skill_external_claim_eligible": frozenset({("skill_row", "policy")}),
    "skill_has_metric_bucket": frozenset({("skill", "metric_bucket")}),
    "skill_projection_only_internal": frozenset({("skill_row", "policy")}),
    "skill_reinforces_skill": frozenset({("skill", "skill")}),
    "skill_requires_human_confirmation": frozenset({("skill_row", "policy")}),
    "skill_supported_by_fact": frozenset(
        {
            ("skill", "atomic_proof_fact"),
            ("skill", "bullet_fact"),
            ("skill", "certification_evidence"),
            ("skill", "experience_evidence"),
            ("skill_row", "atomic_proof_fact"),
            ("skill_row", "bullet_fact"),
            ("skill_row", "certification_evidence"),
            ("skill_row", "experience_evidence"),
        }
    ),
    "skill_supported_by_repo_evidence": frozenset({("skill_row", "repository_evidence")}),
    "skill_supported_by_source_concept": frozenset({("skill_row", "source_concept")}),
    "srfs_requires_fact_id_only": frozenset(
        {("external_claim_policy", "policy"), ("policy_rule", "policy")}
    ),
}


def _register_endpoint_type(registry: dict[str, str], endpoint_id: Any, endpoint_type: str) -> None:
    normalized = str(endpoint_id or "").strip()
    if not normalized:
        return
    existing = registry.get(normalized)
    if existing is not None and existing != endpoint_type:
        registry[normalized] = "__type_conflict__"
        return
    registry[normalized] = endpoint_type


def _register_source_refs(registry: dict[str, str], source_refs: Any) -> None:
    if not isinstance(source_refs, list):
        return
    for raw_ref in source_refs:
        reference = str(raw_ref or "").strip()
        for prefix, endpoint_type in _SOURCE_REF_PREFIX_TYPES:
            if reference.startswith(prefix):
                _register_endpoint_type(registry, reference, endpoint_type)
                break


def _register_fact_reference(registry: dict[str, str], fact_id: Any) -> None:
    reference = str(fact_id or "").strip()
    for prefix, endpoint_type in _SOURCE_REF_PREFIX_TYPES:
        if reference.startswith(prefix):
            _register_endpoint_type(registry, reference, endpoint_type)
            return


def derive_registered_graph_endpoint_types(ledger: Mapping[str, Any]) -> dict[str, str]:
    """Derive non-node endpoint types from independent canonical ledger fields.

    The result is deterministic for a fixed ledger. Prefix shape is used only
    after a value has appeared in an authority-bearing canonical field; graph
    edge endpoints cannot register themselves merely by looking well formed.
    """
    registry = dict(DERIVED_GRAPH_ENDPOINT_EXACT_TYPES)
    policies = ledger.get("external_claim_policies")
    if isinstance(policies, dict):
        for raw_policy_id in policies:
            policy_id = str(raw_policy_id or "").strip()
            if not policy_id:
                continue
            _register_endpoint_type(registry, policy_id, "external_claim_policy")
            _register_endpoint_type(registry, f"policy_{policy_id}", "policy_rule")

    skill_rows_by_id: dict[str, Mapping[str, Any]] = {}
    raw_skill_rows = ledger.get("skill_rows")
    if isinstance(raw_skill_rows, list):
        for raw_row in raw_skill_rows:
            if not isinstance(raw_row, dict):
                continue
            skill_id = str(raw_row.get("skill_id") or "").strip()
            if skill_id:
                skill_rows_by_id[skill_id] = raw_row
            _register_endpoint_type(registry, raw_row.get("domain_id"), "capability_domain")
            _register_endpoint_type(registry, raw_row.get("career_epoch"), "career_epoch")
            for fact_id in raw_row.get("fact_id_links") or []:
                _register_fact_reference(registry, fact_id)
            for field in ("primary_fact_id", "source_ledger_ref"):
                _register_fact_reference(registry, raw_row.get(field))
            for concept in raw_row.get("source_concepts") or []:
                normalized_concept = str(concept or "").strip()
                if normalized_concept:
                    _register_endpoint_type(
                        registry,
                        f"concept_{normalized_concept.replace(' ', '_')[:48]}",
                        "source_concept",
                    )
            for section in raw_row.get("allowed_sections") or []:
                normalized_section = str(section or "").strip()
                if normalized_section:
                    _register_endpoint_type(
                        registry,
                        f"section_{normalized_section}",
                        "resume_section_projection",
                    )

    raw_nodes = ledger.get("graph_nodes")
    if isinstance(raw_nodes, list):
        for raw_node in raw_nodes:
            if not isinstance(raw_node, dict):
                continue
            _register_endpoint_type(registry, raw_node.get("domain_id"), "capability_domain")
            for fact_id in raw_node.get("fact_id_links") or []:
                _register_fact_reference(registry, fact_id)
            for field in ("primary_fact_id", "source_fact_id"):
                _register_fact_reference(registry, raw_node.get(field))
            _register_source_refs(registry, raw_node.get("source_refs"))

    # Historical repository endpoint IDs were materialized with a nonportable
    # hash. Bind them through a strict three-way canonical join instead of
    # accepting every repo_* token: skill row path, edge rationale, and edge ID.
    raw_edges = ledger.get("graph_edges")
    if isinstance(raw_edges, list):
        for raw_edge in raw_edges:
            if not isinstance(raw_edge, dict):
                continue
            if str(raw_edge.get("edge_type") or "").strip() != "skill_supported_by_repo_evidence":
                continue
            source_id = str(raw_edge.get("source_node_id") or "").strip()
            target_id = str(raw_edge.get("target_node_id") or "").strip()
            edge_id = str(raw_edge.get("edge_id") or "").strip()
            rationale = str(raw_edge.get("rationale") or "").strip()
            skill_row = skill_rows_by_id.get(source_id)
            repo_files = {
                str(path or "").strip()
                for path in (skill_row.get("repo_evidence_files") or [] if skill_row else [])
                if str(path or "").strip()
            }
            if (
                _REPO_ENDPOINT_ID.fullmatch(target_id)
                and edge_id == f"edge_skill_repo_{source_id}_{target_id}"
                and any(rationale == f"Repo evidence: {path}" for path in repo_files)
            ):
                _register_endpoint_type(registry, target_id, "repository_evidence")
    return registry


def classify_derived_graph_endpoint(
    endpoint_id: Any,
    registered_endpoint_types: Mapping[str, str] | None = None,
) -> str | None:
    """Resolve only exact or canonically derived endpoint registrations."""
    normalized = str(endpoint_id or "").strip()
    if not normalized:
        return None
    registry = registered_endpoint_types or DERIVED_GRAPH_ENDPOINT_EXACT_TYPES
    endpoint_type = registry.get(normalized)
    return endpoint_type if endpoint_type and endpoint_type != "__type_conflict__" else None


def graph_node_requires_source_refs(node: Mapping[str, Any]) -> bool:
    """Return whether the node's claim policy requires canonical provenance locators."""
    if str(node.get("support_level") or "").strip() == "POLICY":
        return False
    if str(node.get("visibility_rule") or "").strip() in {
        "internal_runtime_only",
        "internal_traversal_only",
    }:
        return False
    claim_policy = str(node.get("external_claim_policy") or "").strip()
    return bool(claim_policy and claim_policy not in PROVENANCE_EXEMPT_EXTERNAL_CLAIM_POLICIES)


def _registered_values(value: Any) -> set[str]:
    if isinstance(value, dict):
        return {str(item).strip() for item in value if str(item).strip()}
    if isinstance(value, list):
        return {str(item).strip() for item in value if str(item).strip()}
    return set()


def _add_issue(issues: list[str], code: str, offenders: Iterable[Any]) -> None:
    unique_offenders = sorted({str(item) for item in offenders if str(item).strip()})
    if unique_offenders:
        issues.append(
            f"{code}: count={len(unique_offenders)} "
            f"offenders={unique_offenders[:ISSUE_SAMPLE_LIMIT]}"
        )


def collect_canonical_graph_issues(ledger: dict[str, Any]) -> list[str]:
    """Return deterministic canonical-graph issues without mutating or writing state."""
    issues: list[str] = []
    raw_nodes = ledger.get("graph_nodes")
    raw_edges = ledger.get("graph_edges")
    if not isinstance(raw_nodes, list):
        return ["GRAPH_NODES_NOT_LIST: count=1 offenders=['graph_nodes']"]
    if not isinstance(raw_edges, list):
        return ["GRAPH_EDGES_NOT_LIST: count=1 offenders=['graph_edges']"]

    metadata = ledger.get("metadata") if isinstance(ledger.get("metadata"), dict) else {}
    graph_metadata = (
        ledger.get("graph_metadata") if isinstance(ledger.get("graph_metadata"), dict) else {}
    )
    w4a_hardened = bool(metadata.get("w4a_hardened") or graph_metadata.get("w4a_hardened"))
    support_levels = _registered_values(ledger.get("support_levels")) | set(
        GRAPH_ONLY_SUPPORT_LEVELS
    )
    visibility_rules = _registered_values(ledger.get("visibility_rules")) | set(
        GRAPH_ONLY_VISIBILITY_RULES
    )
    activation_statuses = _registered_values(ledger.get("activation_statuses"))
    external_claim_policies = _registered_values(ledger.get("external_claim_policies")) | set(
        GRAPH_ONLY_EXTERNAL_CLAIM_POLICIES
    )
    derived_endpoint_types = derive_registered_graph_endpoint_types(ledger)

    node_ids: list[str] = []
    node_types_by_id: dict[str, str] = {}
    blank_node_ids: list[str] = []
    non_object_nodes: list[str] = []
    node_type_blank: list[str] = []
    node_type_unknown: list[str] = []
    node_evidence_missing: list[str] = []
    source_refs_invalid: list[str] = []
    source_refs_required_missing: list[str] = []
    support_unknown: list[str] = []
    visibility_unknown: list[str] = []
    activation_unknown: list[str] = []
    evidence_risk_unknown: list[str] = []
    node_claim_policy_unknown: list[str] = []
    node_text_fields = (
        "label",
        "description",
        "support_level",
        "visibility_rule",
        "activation_status",
        "evidence_risk",
        "projection_behavior",
        "external_claim_policy",
    )
    for index, node in enumerate(raw_nodes):
        locator = f"graph_nodes[{index}]"
        if not isinstance(node, dict):
            non_object_nodes.append(locator)
            continue
        node_id = str(node.get("node_id") or "").strip()
        if not node_id:
            blank_node_ids.append(locator)
            node_id = locator
        else:
            node_ids.append(node_id)
        node_type = str(node.get("node_type") or "").strip()
        if not node_type:
            node_type_blank.append(node_id)
        elif node_type not in REGISTERED_GRAPH_NODE_TYPES:
            node_type_unknown.append(f"{node_id}={node_type}")
        if node_id not in node_types_by_id:
            node_types_by_id[node_id] = node_type
        if not w4a_hardened:
            continue
        for field in node_text_fields:
            if not str(node.get(field) or "").strip():
                node_evidence_missing.append(f"{node_id}.{field}")
        source_refs = node.get("source_refs")
        if not isinstance(source_refs, list) or any(
            not str(source_ref or "").strip() for source_ref in source_refs
        ):
            source_refs_invalid.append(node_id)
        elif graph_node_requires_source_refs(node) and not source_refs:
            source_refs_required_missing.append(node_id)
        support = str(node.get("support_level") or "").strip()
        if support and support not in support_levels:
            support_unknown.append(f"{node_id}={support}")
        visibility = str(node.get("visibility_rule") or "").strip()
        if visibility and visibility not in visibility_rules:
            visibility_unknown.append(f"{node_id}={visibility}")
        activation = str(node.get("activation_status") or "").strip()
        if activation and activation not in activation_statuses:
            activation_unknown.append(f"{node_id}={activation}")
        evidence_risk = str(node.get("evidence_risk") or "").strip().lower()
        if evidence_risk and evidence_risk not in REGISTERED_GRAPH_EVIDENCE_RISKS:
            evidence_risk_unknown.append(f"{node_id}={node.get('evidence_risk')}")
        claim_policy = str(node.get("external_claim_policy") or "").strip()
        if claim_policy and claim_policy not in external_claim_policies:
            node_claim_policy_unknown.append(f"{node_id}={claim_policy}")

    _add_issue(issues, "GRAPH_NODE_NOT_OBJECT", non_object_nodes)
    _add_issue(issues, "GRAPH_NODE_ID_BLANK", blank_node_ids)
    _add_issue(
        issues,
        "GRAPH_NODE_ID_DUPLICATE",
        (node_id for node_id, count in Counter(node_ids).items() if count > 1),
    )
    _add_issue(issues, "GRAPH_NODE_TYPE_BLANK", node_type_blank)
    _add_issue(issues, "GRAPH_NODE_TYPE_UNREGISTERED", node_type_unknown)
    _add_issue(issues, "GRAPH_NODE_EVIDENCE_FIELD_MISSING", node_evidence_missing)
    _add_issue(issues, "GRAPH_NODE_SOURCE_REFS_INVALID", source_refs_invalid)
    _add_issue(
        issues,
        "GRAPH_NODE_REQUIRED_SOURCE_REFS_MISSING",
        source_refs_required_missing,
    )
    _add_issue(issues, "GRAPH_NODE_SUPPORT_LEVEL_UNREGISTERED", support_unknown)
    _add_issue(issues, "GRAPH_NODE_VISIBILITY_RULE_UNREGISTERED", visibility_unknown)
    _add_issue(issues, "GRAPH_NODE_ACTIVATION_STATUS_UNREGISTERED", activation_unknown)
    _add_issue(issues, "GRAPH_NODE_EVIDENCE_RISK_UNREGISTERED", evidence_risk_unknown)
    _add_issue(
        issues,
        "GRAPH_NODE_EXTERNAL_CLAIM_POLICY_UNREGISTERED",
        node_claim_policy_unknown,
    )

    edge_ids: list[str] = []
    logical_triples: list[str] = []
    non_object_edges: list[str] = []
    blank_edge_ids: list[str] = []
    edge_type_blank: list[str] = []
    edge_type_unknown: list[str] = []
    endpoint_blank: list[str] = []
    endpoint_unknown: list[str] = []
    signature_invalid: list[str] = []
    edge_evidence_missing: list[str] = []
    edge_claim_policy_unknown: list[str] = []
    edge_validation_unknown: list[str] = []
    edge_text_fields = (
        "rationale",
        "projection_behavior",
        "external_claim_policy",
        "validation_status",
    )
    for index, edge in enumerate(raw_edges):
        locator = f"graph_edges[{index}]"
        if not isinstance(edge, dict):
            non_object_edges.append(locator)
            continue
        edge_id = str(edge.get("edge_id") or "").strip()
        if not edge_id:
            blank_edge_ids.append(locator)
            edge_id = locator
        else:
            edge_ids.append(edge_id)
        edge_type = str(edge.get("edge_type") or "").strip()
        if not edge_type:
            edge_type_blank.append(edge_id)
        elif edge_type not in REGISTERED_GRAPH_EDGE_TYPES:
            edge_type_unknown.append(f"{edge_id}={edge_type}")
        source_id = str(edge.get("source_node_id") or "").strip()
        target_id = str(edge.get("target_node_id") or "").strip()
        if not source_id:
            endpoint_blank.append(f"{edge_id}.source_node_id")
        if not target_id:
            endpoint_blank.append(f"{edge_id}.target_node_id")
        if source_id and edge_type and target_id:
            logical_triples.append(f"{source_id}|{edge_type}|{target_id}")
        source_type = node_types_by_id.get(source_id) or classify_derived_graph_endpoint(
            source_id, derived_endpoint_types
        )
        target_type = node_types_by_id.get(target_id) or classify_derived_graph_endpoint(
            target_id, derived_endpoint_types
        )
        if source_id and source_type is None:
            endpoint_unknown.append(f"{edge_id}.source_node_id={source_id}")
        if target_id and target_type is None:
            endpoint_unknown.append(f"{edge_id}.target_node_id={target_id}")
        allowed_signatures = REGISTERED_GRAPH_EDGE_SIGNATURES.get(edge_type)
        if (
            allowed_signatures is not None
            and source_type is not None
            and target_type is not None
            and (source_type, target_type) not in allowed_signatures
        ):
            signature_invalid.append(
                f"{edge_id}={edge_type}({source_type}->{target_type})"
            )
        if not w4a_hardened:
            continue
        for field in edge_text_fields:
            if not str(edge.get(field) or "").strip():
                edge_evidence_missing.append(f"{edge_id}.{field}")
        claim_policy = str(edge.get("external_claim_policy") or "").strip()
        if claim_policy and claim_policy not in external_claim_policies:
            edge_claim_policy_unknown.append(f"{edge_id}={claim_policy}")
        validation_status = str(edge.get("validation_status") or "").strip()
        if (
            validation_status
            and validation_status not in REGISTERED_GRAPH_EDGE_VALIDATION_STATUSES
        ):
            edge_validation_unknown.append(f"{edge_id}={validation_status}")

    _add_issue(issues, "GRAPH_EDGE_NOT_OBJECT", non_object_edges)
    _add_issue(issues, "GRAPH_EDGE_ID_BLANK", blank_edge_ids)
    _add_issue(
        issues,
        "GRAPH_EDGE_ID_DUPLICATE",
        (edge_id for edge_id, count in Counter(edge_ids).items() if count > 1),
    )
    _add_issue(
        issues,
        "GRAPH_EDGE_TRIPLE_DUPLICATE",
        (triple for triple, count in Counter(logical_triples).items() if count > 1),
    )
    _add_issue(issues, "GRAPH_EDGE_TYPE_BLANK", edge_type_blank)
    _add_issue(issues, "GRAPH_EDGE_TYPE_UNREGISTERED", edge_type_unknown)
    _add_issue(issues, "GRAPH_EDGE_ENDPOINT_BLANK", endpoint_blank)
    _add_issue(issues, "GRAPH_EDGE_ENDPOINT_UNREGISTERED", endpoint_unknown)
    _add_issue(issues, "GRAPH_EDGE_SIGNATURE_INVALID", signature_invalid)
    _add_issue(issues, "GRAPH_EDGE_EVIDENCE_FIELD_MISSING", edge_evidence_missing)
    _add_issue(
        issues,
        "GRAPH_EDGE_EXTERNAL_CLAIM_POLICY_UNREGISTERED",
        edge_claim_policy_unknown,
    )
    _add_issue(
        issues,
        "GRAPH_EDGE_VALIDATION_STATUS_UNREGISTERED",
        edge_validation_unknown,
    )

    if "node_count" in graph_metadata and graph_metadata.get("node_count") != len(raw_nodes):
        issues.append(
            "GRAPH_METADATA_NODE_COUNT_MISMATCH: "
            f"offenders=['metadata={graph_metadata.get('node_count')}', 'actual={len(raw_nodes)}']"
        )
    if "edge_count" in graph_metadata and graph_metadata.get("edge_count") != len(raw_edges):
        issues.append(
            "GRAPH_METADATA_EDGE_COUNT_MISMATCH: "
            f"offenders=['metadata={graph_metadata.get('edge_count')}', 'actual={len(raw_edges)}']"
        )
    return issues


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_arsenal_ledger_path(repo_root: Path | None = None) -> Path:
    return (repo_root or _repo_root()) / REPO_REL


def load_master_skills_arsenal_ledger(
    *,
    repo_root: Path | None = None,
    path: Path | None = None,
) -> dict[str, Any]:
    ledger_path = path or default_arsenal_ledger_path(repo_root)
    payload = json.loads(ledger_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("arsenal ledger must be object")
    validate_arsenal_ledger_shape(payload)
    return payload


def arsenal_skill_ids(ledger: dict[str, Any]) -> list[str]:
    rows = ledger.get("skill_rows") or []
    return [str(r["skill_id"]) for r in rows if isinstance(r, dict) and r.get("skill_id")]


def validate_skill_row_shape(row: dict[str, Any]) -> None:
    for field in REQUIRED_SKILL_ROW_FIELDS:
        if field not in row:
            raise ValueError(f"skill_row missing {field}")
    if not isinstance(row["fact_id_links"], list):
        raise TypeError("fact_id_links must be list")
    if not isinstance(row["allowed_phrases"], list):
        raise TypeError("allowed_phrases must be list")
    if not isinstance(row["forbidden_phrases"], list):
        raise TypeError("forbidden_phrases must be list")


def _phrase_overlap(allowed: list[str], forbidden: list[str]) -> list[str]:
    overlaps: list[str] = []
    for a in allowed:
        al = a.lower()
        for f in forbidden:
            fl = f.lower()
            if fl in al or al in fl:
                overlaps.append(a)
                break
    return overlaps


def _is_jd_briefing_fact_id(fact_id: str) -> bool:
    low = fact_id.lower()
    return any(low.startswith(p) or p in low for p in JD_BRIEFING_FORBIDDEN_FACT_ID_PREFIXES)


def skill_row_eligible_for_external_claim(row: dict[str, Any]) -> bool:
    """Whether a skill row may anchor external resume claims (not internal ranking only)."""
    support = str(row.get("support_level") or "")
    policy = str(row.get("external_claim_policy") or "")
    if support in NON_EXTERNAL_SUPPORT_LEVELS:
        return False
    if policy in NON_EXTERNAL_CLAIM_POLICIES:
        return False
    if support == "BLOCKED":
        return False
    if support in ("TARGETING_ONLY", "STYLE_ONLY"):
        return False
    if support == "USER_CONFIRMED_PENDING_SOURCE":
        if row.get("human_confirmation_required", True):
            return False
        if str(row.get("activation_status")) != "ACTIVE_CONFIRMED":
            return False
    if support == "DERIVED_SUPPORTED" and not (row.get("fact_id_links") or []):
        return False
    if support == "REPO_EVIDENCE_PORTFOLIO":
        return False
    snippets = row.get("source_snippets") or []
    facts = row.get("fact_id_links") or []
    if not snippets and not facts:
        return False
    if snippets and all(len(str(s).strip()) < 24 for s in snippets):
        return False
    for fid in facts:
        if _is_jd_briefing_fact_id(str(fid)):
            return False
        if _is_skill_id(str(fid)):
            return False
    if _phrase_overlap(list(row.get("allowed_phrases") or []), list(row.get("forbidden_phrases") or [])):
        return False
    return True


def _is_skill_id(value: str) -> bool:
    return value.startswith("skill_")


def skill_row_eligible_for_internal_ranking(row: dict[str, Any]) -> bool:
    if str(row.get("support_level")) == "BLOCKED":
        return False
    return True


def validate_skill_row_for_external_output(row: dict[str, Any]) -> list[str]:
    """Return violation messages; empty list means eligible for external claim use."""
    violations: list[str] = []
    validate_skill_row_shape(row)
    support = str(row.get("support_level") or "")
    if support == "BLOCKED":
        violations.append("BLOCKED cannot be selected for external output")
    if support in ("TARGETING_ONLY", "STYLE_ONLY"):
        violations.append(f"{support} cannot be used as proof")
    if support == "USER_CONFIRMED_PENDING_SOURCE":
        if row.get("human_confirmation_required", True):
            violations.append("USER_CONFIRMED_PENDING_SOURCE requires human confirmation")
        elif str(row.get("activation_status")) != "ACTIVE_CONFIRMED":
            violations.append("USER_CONFIRMED_PENDING_SOURCE requires ACTIVE_CONFIRMED")
    if support == "DERIVED_SUPPORTED" and not (row.get("fact_id_links") or []):
        violations.append("DERIVED_SUPPORTED requires fact_id_links")
    snippets = row.get("source_snippets") or []
    facts = row.get("fact_id_links") or []
    if not snippets and not facts:
        violations.append("external claim requires source_snippets or fact_id_links")
    for fid in facts:
        if _is_jd_briefing_fact_id(str(fid)):
            violations.append(f"JD/briefing cannot appear as fact_id_links: {fid}")
    overlaps = _phrase_overlap(
        list(row.get("allowed_phrases") or []),
        list(row.get("forbidden_phrases") or []),
    )
    if overlaps:
        violations.append(f"allowed_phrases overlap forbidden: {overlaps[:3]}")
    return violations


def validate_w4a_graph_shape(ledger: dict[str, Any]) -> None:
    if not ledger.get("metadata", {}).get("w4a_hardened"):
        return
    for key in W4A_TOP_LEVEL:
        if key not in ledger:
            raise ValueError(f"W4A arsenal ledger missing top-level key: {key}")
    nodes = ledger.get("graph_nodes") or []
    edges = ledger.get("graph_edges") or []
    if not isinstance(nodes, list) or not nodes:
        raise ValueError("graph_nodes must be non-empty list when w4a_hardened")
    if not isinstance(edges, list) or not edges:
        raise ValueError("graph_edges must be non-empty list when w4a_hardened")
    for node in nodes:
        for field in (
            "node_id",
            "node_type",
            "label",
            "description",
            "support_level",
            "visibility_rule",
            "activation_status",
            "evidence_risk",
            "source_refs",
            "projection_behavior",
            "external_claim_policy",
        ):
            if field not in node:
                raise ValueError(f"graph node {node.get('node_id')} missing {field}")
    for edge in edges:
        for field in (
            "edge_id",
            "edge_type",
            "source_node_id",
            "target_node_id",
            "rationale",
            "projection_behavior",
            "external_claim_policy",
            "validation_status",
        ):
            if field not in edge:
                raise ValueError(f"graph edge {edge.get('edge_id')} missing {field}")


def validate_c03_graph_hardening_shape(ledger: dict[str, Any]) -> None:
    """Validate the additive C0.3 graph hardening layer when present.

    This is intentionally not required for older ledgers. Once the overwrite is
    applied, all required nodes and edge types must exist and must remain graph
    authority, not broad ledger fallback.
    """
    marker = (ledger.get("metadata") or {}).get("c03_actual_graph_full_zero_loss_overwrite")
    if not marker:
        return
    node_ids = {str(n.get("node_id")) for n in ledger.get("graph_nodes") or [] if isinstance(n, dict)}
    missing = sorted(C03_REQUIRED_GRAPH_HARDENING_NODES - node_ids)
    if missing:
        raise ValueError(f"C0.3 graph hardening missing nodes: {missing}")
    edge_types = {str(e.get("edge_type")) for e in ledger.get("graph_edges") or [] if isinstance(e, dict)}
    missing_edge_types = sorted(C03_REQUIRED_GRAPH_HARDENING_EDGE_TYPES - edge_types)
    if missing_edge_types:
        raise ValueError(f"C0.3 graph hardening missing edge types: {missing_edge_types}")
    for sid in (n for n in C03_REQUIRED_GRAPH_HARDENING_NODES if n.startswith("skill_")):
        linked = [
            e
            for e in ledger.get("graph_edges") or []
            if isinstance(e, dict)
            and str(e.get("source_node_id")) == sid
            and str(e.get("edge_type")) == "skill_supported_by_fact"
        ]
        if not linked:
            raise ValueError(f"C0.3 hardening skill has no skill_supported_by_fact edge: {sid}")


def validate_arsenal_ledger_shape(ledger: dict[str, Any]) -> None:
    for key in REQUIRED_TOP_LEVEL:
        if key not in ledger:
            raise ValueError(f"arsenal ledger missing top-level key: {key}")
    graph_issues = collect_canonical_graph_issues(ledger)
    blocking_graph_issues = [
        issue
        for issue in graph_issues
        if issue.split(":", 1)[0] not in NON_SHAPE_GRAPH_HEALTH_ISSUE_CODES
    ]
    if blocking_graph_issues:
        raise ValueError(
            "canonical graph validation failed: " + "; ".join(blocking_graph_issues)
        )
    validate_w4a_graph_shape(ledger)
    validate_c03_graph_hardening_shape(ledger)
    rows = ledger.get("skill_rows")
    if not isinstance(rows, list):
        raise TypeError("skill_rows must be list")
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            raise TypeError("skill_row must be dict")
        validate_skill_row_shape(row)
        sid = str(row["skill_id"])
        if sid in seen:
            raise ValueError(f"duplicate skill_id: {sid}")
        seen.add(sid)
        support_levels = ledger.get("support_levels") or []
        if row["support_level"] not in support_levels:
            raise ValueError(f"unknown support_level on {sid}: {row['support_level']}")
        act = str(row.get("activation_status"))
        if act not in (ledger.get("activation_statuses") or []):
            raise ValueError(f"unknown activation_status on {sid}: {act}")


def assert_no_jd_briefing_as_proof_fact_ids(fact_ids: Iterable[str]) -> None:
    for fid in fact_ids:
        if _is_jd_briefing_fact_id(str(fid)):
            raise ValueError(f"JD/briefing cannot be proof fact id: {fid}")
