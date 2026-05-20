"""Build W4A graph structures and hardened skill rows for master_skills_arsenal_ledger."""
from __future__ import annotations

from typing import Any

from apps_rg.fact_inventory.arsenal_graph_w4a_spec import (
    AGENTIC_CAPABILITY_DOMAINS,
    CAREER_EPOCHS,
    EXTERNAL_CLAIM_POLICIES,
    GRAPH_LAYERS,
    IDENTITY_NODE,
    RESUME_GENERATION_POLICY,
    _AGENTIC_ROW_TEMPLATE,
    _SKILL_TO_DOMAIN,
)

EPOCH_AGENTIC = "epoch_agentic_ai_runtime_architecture"
EPOCH_ACTUARIAL = "epoch_actuarial_financial_engineering"
EPOCH_PARTNER = "epoch_partner_gtm_revenue_leadership"

ACTUARIAL_CHAIN_SKILL_IDS: tuple[str, ...] = (
    "skill_actuarial_fsa_fellowship",
    "skill_insurance_liabilities_embedded_options",
    "skill_insurance_liabilities_insurance_liabilities",
    "skill_derivatives_exotic_options",
    "skill_derivatives_structured_derivatives",
    "skill_greeks_delta",
    "skill_greeks_gamma",
    "skill_greeks_vega",
    "skill_greeks_rho",
    "skill_greeks_convexity",
    "skill_capital_capital_modeling",
    "skill_capital_reserving",
    "skill_risk_enterprise_risk_controls",
)

PARTNER_CHAIN_SKILL_IDS: tuple[str, ...] = (
    "skill_partner_aws_ecosystem",
    "skill_partner_cloud_partner_ecosystem",
    "skill_partner_partner_engineering",
    "skill_partner_co_selling",
    "skill_partner_pre_sales",
    "skill_partner_gtm_enablement",
    "skill_partner_enterprise_negotiations",
    "skill_partner_pnl_oversight",
)


def _resume_hardening_fields(
    capability: str,
    *,
    external_policy: str,
    quant: str | None = None,
) -> dict[str, Any]:
    ats = [w for w in capability.lower().split() if len(w) > 3][:8]
    return {
        "ats_keywords": ats,
        "achievement_framing_guidance": (
            f"Frame {capability} with scope, mechanism, and outcome; metrics only from linked fact_id."
        ),
        "quantification_policy": quant
        or "No invented numbers; require metric-bound fact_id or approved derivative.",
        "narrative_synthesis_guidance": (
            "Synthesize only from linked fact_id_links and approved bundles; skill_id is not proof."
        ),
        "claim_verification_policy": (
            "External resume claims allowed only when external_claim_policy permits and fact_id backs metrics."
        ),
        "zero_hallucination_guardrail": (
            f"Do not claim {capability} beyond repo evidence and linked facts; fail closed if proof missing."
        ),
    }


def build_agentic_skill_row(
    skill_id: str,
    capability: str,
    source_concepts: list[str],
    snippet: str,
    fact_links: list[str],
    repo_files: list[str],
) -> dict[str, Any]:
    domain_id = _SKILL_TO_DOMAIN[skill_id]
    domain = next(d for d in AGENTIC_CAPABILITY_DOMAINS if d["domain_id"] == domain_id)
    weak = len(snippet.strip()) < 24
    has_fact = bool(fact_links)
    if weak:
        ext_policy = "weak_snippet_internal_only"
        support = "INTERNAL_ONLY"
        visibility = "never_external"
        proj = "internal_rank_only"
    elif has_fact:
        ext_policy = "derived_supported_with_fact"
        support = "DERIVED_SUPPORTED"
        visibility = "role_family_match"
        proj = "rank_and_project_facts"
    else:
        ext_policy = "repo_portfolio_not_resume_default"
        support = "REPO_EVIDENCE_PORTFOLIO"
        visibility = "role_family_match"
        proj = "portfolio_eligible_internal_default"

    row: dict[str, Any] = {
        "skill_id": skill_id,
        "node_type": "skill_row",
        "domain": domain["label"],
        "domain_id": domain_id,
        "pillar": domain["pillar"],
        "subpillar": capability,
        "capability": capability,
        "career_stage": "current",
        "career_epoch": EPOCH_AGENTIC,
        "source_concepts": source_concepts,
        "repo_evidence_files": repo_files,
        "source_resume_files": [],
        "source_snippets": [snippet] if snippet else [],
        "fact_id_links": list(fact_links),
        "user_confirmed": False,
        "support_level": support,
        "role_family_weights": {
            "ENGINEERING_PLATFORM": 1.0,
            "AI_SOLUTIONS_ARCHITECTURE": 0.95,
            "AI_GOVERNANCE_RISK": 0.85,
            "EXECUTIVE_LEADERSHIP": 0.8,
            "PARTNERSHIPS_GTM": 0.75,
        },
        "allowed_phrases": [capability.lower()],
        "forbidden_phrases": ["autonomous AGI without oversight", "unsupervised production agents"],
        "allowed_sections": ["executive_summary", "competencies", "unify_bullets"],
        "visibility_rule": visibility,
        "evidence_risk": "low" if has_fact else "medium",
        "activation_status": "DRAFT",
        "human_confirmation_required": False,
        "projection_behavior": proj,
        "external_claim_policy": ext_policy,
    }
    row.update(_resume_hardening_fields(capability, external_policy=ext_policy))
    return row


def build_agentic_runtime_matrix() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for tpl in _AGENTIC_ROW_TEMPLATE:
        sid, cap, concepts, snippet, facts, repos = tpl
        rows.append(build_agentic_skill_row(sid, cap, concepts, snippet, facts, repos))
    return rows


def enhance_legacy_skill_row(row: dict[str, Any]) -> dict[str, Any]:
    """Add W4A graph fields to actuarial/partner matrix rows without changing proof semantics."""
    out = dict(row)
    sid = str(out["skill_id"])
    support = str(out.get("support_level") or "")
    if support == "USER_CONFIRMED_PENDING_SOURCE":
        out["external_claim_policy"] = "pending_source_internal_only"
        out["projection_behavior"] = "internal_rank_only"
    elif support in ("DIRECT_FROM_RESUME_ARCHIVE", "BUNDLE_SUPPORTED", "DERIVED_SUPPORTED"):
        out["external_claim_policy"] = (
            "external_resume_claim_requires_active_fact_or_confirmed_snippet"
            if out.get("source_snippets") or out.get("fact_id_links")
            else "weak_snippet_internal_only"
        )
        out["projection_behavior"] = "rank_and_project_facts"
    else:
        out["external_claim_policy"] = out.get("external_claim_policy") or "repo_portfolio_not_resume_default"
        out["projection_behavior"] = out.get("projection_behavior") or "internal_rank_only"

    if sid.startswith("skill_actuarial_") or sid.startswith("skill_derivatives_") or sid.startswith("skill_greeks_"):
        out["career_epoch"] = EPOCH_ACTUARIAL
        out.setdefault("domain_id", "domain_actuarial_foundation")
        out.setdefault("domain", "Actuarial Foundation")
    elif sid.startswith("skill_partner_"):
        out["career_epoch"] = EPOCH_PARTNER
        out.setdefault("domain_id", "domain_partner_gtm")
        out.setdefault("domain", "Partner GTM")
    elif sid.startswith("skill_risk_") or sid.startswith("skill_capital_"):
        out["career_epoch"] = EPOCH_ACTUARIAL
        out.setdefault("domain_id", "domain_enterprise_risk")
        out.setdefault("domain", "Enterprise Risk")
    else:
        out.setdefault("career_epoch", "cross_career")
        out.setdefault("domain_id", out.get("domain_id") or "domain_legacy_matrix")
        out.setdefault("domain", out.get("domain") or out.get("subpillar") or "Legacy Matrix")

    cap = str(out.get("subpillar") or out.get("capability") or sid)
    out.setdefault("capability", cap)
    out.setdefault("source_concepts", [])
    out.setdefault("repo_evidence_files", [])
    out.setdefault("node_type", "skill_row")
    out.update(
        _resume_hardening_fields(
            cap,
            external_policy=str(out.get("external_claim_policy") or ""),
        )
    )
    return out


def _node(
    node_id: str,
    node_type: str,
    label: str,
    description: str,
    *,
    support_level: str = "DERIVED_SUPPORTED",
    visibility_rule: str = "role_family_match",
    activation_status: str = "DRAFT",
    evidence_risk: str = "low",
    source_refs: list[str] | None = None,
    projection_behavior: str = "graph_structure",
    external_claim_policy: str = "skill_projection_not_proof",
) -> dict[str, Any]:
    return {
        "node_id": node_id,
        "node_type": node_type,
        "label": label,
        "description": description,
        "support_level": support_level,
        "visibility_rule": visibility_rule,
        "activation_status": activation_status,
        "evidence_risk": evidence_risk,
        "source_refs": source_refs or [],
        "projection_behavior": projection_behavior,
        "external_claim_policy": external_claim_policy,
    }


def _edge(
    edge_id: str,
    edge_type: str,
    source: str,
    target: str,
    rationale: str,
    *,
    projection_behavior: str = "graph_traversal",
    external_claim_policy: str = "skill_projection_not_proof",
    validation_status: str = "validated",
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    out = {
        "edge_id": edge_id,
        "edge_type": edge_type,
        "source_node_id": source,
        "target_node_id": target,
        "rationale": rationale,
        "projection_behavior": projection_behavior,
        "external_claim_policy": external_claim_policy,
        "validation_status": validation_status,
    }
    if extra:
        out.update(extra)
    return out


def append_senior_role_bridge_edges(
    edges: list[dict[str, Any]],
    bridge_specs: list[dict[str, Any]],
    *,
    valid_pillar_ids: set[str],
) -> None:
    """Evidence-gated pillar phase bridges (W8–W11); traversal-only, not external proof."""
    for spec in bridge_specs:
        src = str(spec.get("source_pillar_id") or "")
        tgt = str(spec.get("target_pillar_id") or "")
        family = str(spec.get("bridge_edge_family") or "unknown")
        edge_type = str(spec.get("edge_type") or "pillar_phase_bridge")
        tgt_ok = tgt in valid_pillar_ids or (
            edge_type == "pillar_section_eligibility" and tgt.startswith("section_")
        )
        if src not in valid_pillar_ids or not tgt_ok:
            continue
        eid = str(spec.get("edge_id") or f"edge_bridge_{family}_{src}_to_{tgt}")
        edges.append(
            _edge(
                eid,
                str(spec.get("edge_type") or "pillar_phase_bridge"),
                src,
                tgt,
                str(spec.get("rationale") or f"Phase bridge: {family}"),
                projection_behavior=str(spec.get("projection_behavior") or "graph_traversal_forward"),
                external_claim_policy=str(spec.get("external_claim_policy") or "internal_traversal_only"),
                validation_status=str(spec.get("validation_status") or "validated"),
                extra={
                    "bridge_edge_family": family,
                    "direction": str(spec.get("direction") or "forward"),
                    "evidence_fact_ids": list(spec.get("evidence_fact_ids") or []),
                    "evidence_sources": list(spec.get("evidence_sources") or []),
                },
            )
        )


def build_graph_nodes(
    pillars: list[dict[str, Any]],
    skill_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    nodes: list[dict[str, Any]] = []
    nodes.append(_node(
        IDENTITY_NODE["node_id"],
        "identity_north_star",
        IDENTITY_NODE["label"],
        IDENTITY_NODE["description"],
        projection_behavior="identity_anchor",
        external_claim_policy="atomic_fact_default_external_proof",
    ))
    for ep in CAREER_EPOCHS:
        nodes.append(_node(
            ep["node_id"],
            "career_epoch",
            ep["label"],
            f"Career epoch: {ep['label']}",
            projection_behavior="epoch_filter",
        ))
    for p in pillars:
        nodes.append(_node(
            p["pillar_id"],
            "domain_pillar",
            p["name"],
            str(p.get("description") or ""),
            source_refs=list(p.get("linked_fact_ids") or [])[:5],
        ))
    for d in AGENTIC_CAPABILITY_DOMAINS:
        nodes.append(_node(
            d["domain_id"],
            "capability_domain",
            d["label"],
            f"Capability domain: {d['label']}",
            source_refs=[d["pillar"]],
        ))
    for row in skill_rows:
        sid = row["skill_id"]
        nodes.append(_node(
            sid,
            "skill_row",
            str(row.get("capability") or sid),
            str(row.get("source_snippets") or [""])[0][:200] if row.get("source_snippets") else sid,
            support_level=str(row.get("support_level") or "DRAFT"),
            visibility_rule=str(row.get("visibility_rule") or "role_family_match"),
            activation_status=str(row.get("activation_status") or "DRAFT"),
            evidence_risk=str(row.get("evidence_risk") or "medium"),
            source_refs=list(row.get("source_concepts") or []),
            projection_behavior=str(row.get("projection_behavior") or "internal_rank_only"),
            external_claim_policy=str(row.get("external_claim_policy") or "repo_portfolio_not_resume_default"),
        ))
    return nodes


def build_graph_edges(
    skill_rows: list[dict[str, Any]],
    pillars: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []
    identity = IDENTITY_NODE["node_id"]

    for ep in CAREER_EPOCHS:
        eid = ep["node_id"]
        edges.append(_edge(f"edge_identity_epoch_{eid}", "identity_supported_by_epoch", identity, eid, "Identity grounded in career epoch"))
        for pid in ep.get("pillars") or []:
            edges.append(_edge(f"edge_epoch_pillar_{eid}_{pid}", "epoch_contains_pillar", eid, pid, "Epoch contains domain pillar"))
            edges.append(_edge(f"edge_identity_pillar_{pid}", "identity_supported_by_pillar", identity, pid, "Identity supported by pillar"))

    pillar_ids = {p["pillar_id"] for p in pillars}
    for d in AGENTIC_CAPABILITY_DOMAINS:
        pid = d["pillar"]
        if pid in pillar_ids:
            edges.append(_edge(
                f"edge_pillar_domain_{d['domain_id']}",
                "pillar_contains_capability_domain",
                pid,
                d["domain_id"],
                "Pillar contains capability domain",
            ))

    for row in skill_rows:
        sid = row["skill_id"]
        did = str(row.get("domain_id") or "")
        if did:
            edges.append(_edge(f"edge_domain_skill_{sid}", "capability_domain_contains_skill", did, sid, "Domain contains skill"))
        epoch = str(row.get("career_epoch") or "")
        if epoch:
            edges.append(_edge(f"edge_epoch_skill_{sid}", "epoch_contains_skill", epoch, sid, "Epoch contains skill"))
        for concept in row.get("source_concepts") or []:
            cid = f"concept_{concept.replace(' ', '_')[:48]}"
            edges.append(_edge(
                f"edge_skill_concept_{sid}_{cid}",
                "skill_supported_by_source_concept",
                sid,
                cid,
                f"Skill supported by source concept {concept}",
            ))
        for repo in row.get("repo_evidence_files") or []:
            rid = f"repo_{hash(repo) & 0xFFFFFF:06x}"
            edges.append(_edge(
                f"edge_skill_repo_{sid}_{rid}",
                "skill_supported_by_repo_evidence",
                sid,
                rid,
                f"Repo evidence: {repo}",
            ))
        for fid in row.get("fact_id_links") or []:
            edges.append(_edge(
                f"edge_skill_fact_{sid}_{fid}",
                "skill_supported_by_fact",
                sid,
                fid,
                "Skill anchored to atomic proof fact",
                external_claim_policy="atomic_fact_default_external_proof",
            ))
        policy = str(row.get("external_claim_policy") or "")
        if policy in ("pending_source_internal_only", "weak_snippet_internal_only", "repo_portfolio_not_resume_default"):
            edges.append(_edge(
                f"edge_block_external_{sid}",
                "projection_excludes_blocked_skill",
                sid,
                "policy_external_claim_policy",
                f"Block external: {policy}",
                external_claim_policy=policy,
            ))
        elif policy == "derived_supported_with_fact" or row.get("fact_id_links"):
            edges.append(_edge(
                f"edge_external_eligible_{sid}",
                "skill_external_claim_eligible",
                sid,
                "policy_external_claim_policy",
                "Conditionally eligible when fact active",
            ))
        else:
            edges.append(_edge(
                f"edge_internal_only_{sid}",
                "skill_projection_only_internal",
                sid,
                "policy_external_claim_policy",
                "Internal ranking only",
            ))
        if row.get("human_confirmation_required"):
            edges.append(_edge(
                f"edge_human_confirm_{sid}",
                "skill_requires_human_confirmation",
                sid,
                "policy_external_claim_policy",
                "Requires human confirmation",
            ))
        for sec in row.get("allowed_sections") or []:
            edges.append(_edge(
                f"edge_skill_section_{sid}_{sec}",
                "skill_allowed_in_section",
                sid,
                f"section_{sec}",
                f"Allowed in {sec}",
            ))

    # Actuarial chain edges
    chain = [s for s in ACTUARIAL_CHAIN_SKILL_IDS if any(r["skill_id"] == s for r in skill_rows)]
    for i in range(len(chain) - 1):
        edges.append(_edge(
            f"edge_actuarial_chain_{chain[i]}_{chain[i+1]}",
            "capability_domain_contains_skill",
            "pillar_actuarial_foundation",
            chain[i + 1],
            "Actuarial foundation chain",
        ))
    edges.append(_edge("edge_epoch_actuarial_pillar", "epoch_contains_pillar", EPOCH_ACTUARIAL, "pillar_actuarial_foundation", "Actuarial epoch"))

    # Partner chain
    pchain = [s for s in PARTNER_CHAIN_SKILL_IDS if any(r["skill_id"] == s for r in skill_rows)]
    for i in range(len(pchain) - 1):
        edges.append(_edge(
            f"edge_partner_chain_{i}",
            "capability_domain_contains_skill",
            "pillar_partner_gtm_alliances",
            pchain[i + 1],
            "Partner GTM chain",
        ))
    edges.append(_edge("edge_epoch_partner_pillar", "epoch_contains_pillar", EPOCH_PARTNER, "pillar_partner_gtm_alliances", "Partner epoch"))

    # Defensive policy edges
    for pol_id in EXTERNAL_CLAIM_POLICIES:
        edges.append(_edge(
            f"edge_policy_{pol_id}",
            "srfs_requires_fact_id_only",
            pol_id,
            "policy_external_claim_policy",
            EXTERNAL_CLAIM_POLICIES[pol_id]["description"],
            external_claim_policy=pol_id,
        ))
    edges.append(_edge("edge_jd_targeting", "jd_briefing_targeting_only", "jd_text", "policy_jd_briefing_targeting_only", "JD targeting only"))
    edges.append(_edge("edge_section_block_pending", "section_blocks_pending_source_skill", "section_executive_summary", "policy_pending_source_internal_only", "Block pending skills from exec external"))
    edges.append(_edge("edge_section_block_no_fact", "section_blocks_skill_without_fact", "section_executive_summary", "policy_skill_projection_not_proof", "Skills without facts cannot proof"))

    return edges


def build_w4a_graph_package(
    *,
    pillars: list[dict[str, Any]],
    legacy_skill_rows: list[dict[str, Any]],
    bridge_specs: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    agentic_rows = build_agentic_runtime_matrix()
    enhanced_legacy = [enhance_legacy_skill_row(r) for r in legacy_skill_rows]
    seen: set[str] = set()
    skill_rows: list[dict[str, Any]] = []
    for row in enhanced_legacy + agentic_rows:
        sid = row["skill_id"]
        if sid in seen:
            continue
        seen.add(sid)
        skill_rows.append(row)

    nodes = build_graph_nodes(pillars, skill_rows)
    edges = build_graph_edges(skill_rows, pillars)
    if bridge_specs:
        append_senior_role_bridge_edges(
            edges,
            bridge_specs,
            valid_pillar_ids={str(p["pillar_id"]) for p in pillars},
        )

    agentic_by_domain: dict[str, list[str]] = {}
    for row in agentic_rows:
        did = str(row.get("domain_id") or "")
        agentic_by_domain.setdefault(did, []).append(row["skill_id"])

    return {
        "graph_metadata": {
            "schema_version": "master_skills_arsenal_graph_v1",
            "w4a_hardened": True,
            "primary_taxonomy": "capability_domain",
            "source_coded_taxonomy_forbidden_as_primary": True,
            "node_count": len(nodes),
            "edge_count": len(edges),
            "deep_agentic_row_count": len(agentic_rows),
        },
        "graph_layers": GRAPH_LAYERS,
        "graph_nodes": nodes,
        "graph_edges": edges,
        "external_claim_policies": EXTERNAL_CLAIM_POLICIES,
        "agentic_runtime_matrix": agentic_rows,
        "agentic_capability_domains": AGENTIC_CAPABILITY_DOMAINS,
        "graph_validation_rules": {
            "capability_domain_primary_taxonomy": True,
            "skill_id_never_source_fact_id": True,
            "jd_briefing_never_proof": True,
            "pending_source_internal_only": True,
            "repo_portfolio_not_resume_default": True,
            "weak_snippet_internal_only": True,
            "every_skill_has_domain_and_epoch": True,
        },
        "resume_generation_policy": RESUME_GENERATION_POLICY,
        "skill_rows": skill_rows,
        "agentic_rows_by_domain": agentic_by_domain,
    }
