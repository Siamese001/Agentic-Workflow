"""Unit tests: executive summary graph-backed painting-plan X2 gates."""

from __future__ import annotations

from apps_rg.runtime.sections.executive_summary_composition import (
    build_executive_summary_composition_plan,
    build_sentence_arc,
    check_brushstroke_fact_support,
    check_composition_plan_present,
    check_dominant_brushstroke_coherence,
    check_graph_skill_coverage,
    check_mechanism_inventory_control,
    check_s1_dominant_brushstroke_thesis,
    format_composition_plan_for_pa,
    is_mechanism_inventory_sentence,
)
from apps_rg.runtime.validators.executive_summary_x2 import check_graph_evidence_sentence_responsibility_shape


def _graph_pool() -> dict[str, object]:
    return {"graph_skills_proof_pool": True, "proof_pool_type": "augmented_skills_graph"}


def _facts() -> list[dict[str, object]]:
    return [
        {
            "fact_id": "fact_engineering_platform_001",
            "claim_text": (
                "Architected governed agentic AI platforms with deterministic routing, "
                "multi-agent orchestration, and GraphRAG retrieval."
            ),
        },
        {
            "fact_id": "fact_governance_003",
            "claim_text": "Implemented Basel III / CCAR data lineage and automated validation frameworks.",
        },
    ]


def test_s1_light_routing_qualifier_passes() -> None:
    s1 = (
        "Engineering executive building governed agentic AI platforms with routing discipline "
        "for regulated enterprise environments."
    )
    ok, reason = check_s1_dominant_brushstroke_thesis(s1)
    assert ok is True, reason


def test_s1_mechanism_list_fails() -> None:
    s1 = (
        "Engineering executive operationalizing platforms through deterministic routing, "
        "retrieval, and telemetry across the enterprise."
    )
    ok, reason = check_s1_dominant_brushstroke_thesis(s1)
    assert ok is False
    assert reason


def test_s1_through_routing_retrieval_telemetry_inventory_fails() -> None:
    s1 = (
        "Leader improving delivery through deterministic routing, retrieval, and telemetry "
        "while scaling programs."
    )
    inv, _ = is_mechanism_inventory_sentence(s1)
    assert inv is True
    ok, _ = check_mechanism_inventory_control(s1 + " Second. Third. Fourth.")
    assert ok is False


def test_s2_platform_brushstroke_routing_passes_shape_gate() -> None:
    text = (
        "Engineering executive building governed agentic AI platforms for regulated enterprise environments. "
        "Designed runtime systems combining deterministic routing, multi-agent orchestration, and "
        "GraphRAG retrieval with validation controls and traceability. "
        "Standardized AI lifecycle practices across intake, validation, execution, monitoring, and remediation. "
        "Connected governance themes to enterprise operating rhythms without adding unsupported metrics. "
        "Delivered measurable commercial outcomes grounded in cited executive facts. "
        "Integrated AWS and FSA credentials reinforce quantitative credibility for stakeholders."
    )
    ok, reason = check_graph_evidence_sentence_responsibility_shape(text, _graph_pool())
    assert ok is True, reason


def test_composition_plan_missing_graph_refs_fails_when_claimed() -> None:
    plan = {
        "composition_style": "executive_painting",
        "brushstrokes": [{"brushstroke_id": "B1", "support_status": "SUPPORTED", "required_fact_ids": []}],
        "graph_skill_refs": [],
        "graph_backed_composition_claimed": True,
    }
    ok, reason = check_graph_skill_coverage(plan, {"graph_skill_refs": []})
    assert ok is False
    assert reason


def test_brushstroke_unsupported_fact_fails() -> None:
    plan = build_executive_summary_composition_plan(
        selected_facts=_facts(),
        allowed_fact_ids={"fact_engineering_platform_001", "fact_governance_003"},
        target_role="SVP Engineering",
        target_company="Brown & Brown",
    )
    for bs in plan["brushstrokes"]:
        if isinstance(bs, dict) and bs.get("brushstroke_id") == "B1_executive_identity":
            bs["support_status"] = "UNSUPPORTED"
    ledger = [{"claim_text": "x", "source_fact_ids": ["fact_governance_003"]}]
    ok, reason = check_brushstroke_fact_support(
        plan, ledger, {"fact_governance_003", "fact_engineering_platform_001"}
    )
    assert ok is False
    assert reason


def test_composition_plan_present_requires_artifact_fields() -> None:
    ok, reason = check_composition_plan_present(
        {"executive_summary_composition_plan": {"composition_style": "executive_painting", "brushstrokes": []}},
        artifacts_dir=None,
        proof_pool_metadata={"graph_skills_proof_pool": True, "proof_pool_type": "augmented_skills_graph"},
    )
    assert ok is False
    assert reason


def test_strategy_target_emits_svp_sentence_arc() -> None:
    plan = build_executive_summary_composition_plan(
        selected_facts=_facts(),
        allowed_fact_ids={"fact_engineering_platform_001", "fact_governance_003"},
        target_role="SVP, IT Strategy & Innovation",
        target_company="Brown & Brown",
    )
    assert plan.get("strategy_executive_arc") is True
    assert "leadership-first" in str(plan.get("target_picture") or "").lower()
    arc = plan.get("sentence_arc") or []
    assert len(arc) == 6
    assert arc[2].get("arc_role") == "scale_operating_model"
    assert arc[4].get("arc_role") == "commercial_strategy"
    pa_block = format_composition_plan_for_pa(plan)
    assert "narrative_arc_weights" in pa_block
    assert "executive_strategy_thesis" in pa_block
    assert "S3" in pa_block


def test_build_sentence_arc_default_has_six_rows() -> None:
    arc = build_sentence_arc(target_role="VP Engineering", strategy_executive=False)
    assert len(arc) == 6
    assert arc[0]["brushstroke_id"] == "B1_executive_identity"
    assert "leadership" in arc[0]["guidance"].lower()


def test_dominant_brushstroke_coherence_passes_thesis() -> None:
    plan = build_executive_summary_composition_plan(
        selected_facts=_facts(),
        allowed_fact_ids={"fact_engineering_platform_001"},
        target_role="SVP",
        target_company="Corp",
    )
    text = (
        "Engineering executive building governed agentic platforms for regulated enterprises. "
        "Architected routing and orchestration with GraphRAG retrieval. "
        "Leads lifecycle commercialization across programs. "
        "Delivered proof-backed outcomes. "
        "Closes with integrated credential depth."
    )
    ok, _ = check_dominant_brushstroke_coherence(text, plan)
    assert ok is True
