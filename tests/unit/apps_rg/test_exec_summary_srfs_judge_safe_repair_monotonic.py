"""Unit tests: SRFS judge-safe repair monotonic acceptance (regression guard)."""

from __future__ import annotations

from apps_rg.runtime.sections.exec_summary_srfs_judge_safe import (
    _apply_srfs_judge_safe_repair_core,
    apply_srfs_judge_safe_repair,
    duplicate_sentence_or_claim_count,
    evaluate_judge_safe_repair_monotonicity,
)
from apps_rg.runtime.validators.executive_summary_x2 import _resume_word_count


def _srfs(*, fact_ids: list[str] | None = None) -> dict[str, object]:
    ids = fact_ids or [
        "fact_engineering_platform_001",
        "fact_governance_003",
        "fact_exec_002",
        "fact_certs_001",
        "fact_quant_hpc_003",
    ]
    return {
        "artifact_path_resolved": "artifacts/apps_rg/fact_inventory/selected_role_fact_set_active.json",
        "executive_summary_selected_fact_ids": ids,
    }


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
            "claim_text": (
                "Implemented Basel III / CCAR data lineage, cataloging, and automated validation "
                "frameworks that cut regulatory reporting errors by 40%."
            ),
        },
        {
            "fact_id": "fact_exec_002",
            "claim_text": (
                "Productized platform capabilities into reusable services, generating $22M in IP-led "
                "revenue and expanding gross margins by 20%."
            ),
        },
        {
            "fact_id": "fact_certs_001",
            "claim_text": (
                "Holds AWS Certified Machine Learning Engineer - Associate, AWS Certified Solutions "
                "Architect - Professional, Databricks Lakehouse Fundamentals, and Fellow of the "
                "Society of Actuaries credentials."
            ),
        },
        {
            "fact_id": "fact_quant_hpc_003",
            "claim_text": (
                "Built advanced quantitative foundation through derivatives pricing, multi-Greek hedging, "
                "capital modeling, and FSA credential across Towers Perrin, ING, and Aetna."
            ),
        },
    ]


def _plan() -> dict[str, object]:
    return {
        "schema": "executive_summary_composition_plan_v1",
        "composition_style": "executive_painting",
        "dominant_brushstroke_id": "B2_governed_platform_system",
        "brushstrokes": [
            {
                "brushstroke_id": "B4_business_role_fit",
                "support_status": "SUPPORTED",
                "required_fact_ids": ["fact_certs_001", "fact_quant_hpc_001"],
            }
        ],
        "graph_backed_composition_claimed": True,
    }


def test_reject_repair_below_95_when_pre_above_threshold() -> None:
    pre_text = (
        "Engineering executive with extensive experience in designing and operationalizing governed "
        "agentic AI platforms for regulated enterprise workflows. Led the development of deterministic "
        "routing, multi-agent orchestration, GraphRAG retrieval, sandboxed execution, and policy gating, "
        "improving reliability and auditability. Productized these capabilities into reusable platform "
        "services, generating $22M in IP-led revenue, expanding gross margins by 20%, and scaling the ML "
        "engineering organization from 8 to 28 specialists. Holds AWS Certified Machine Learning Engineer - "
        "Associate, AWS Certified Solutions Architect - Professional, Databricks Lakehouse Fundamentals, "
        "and Fellow of the Society of Actuaries credentials."
    )
    post_text = (
        "Engineering executive with extensive experience in designing and operationalizing governed "
        "agentic AI platforms for regulated enterprise workflows. Implemented Basel III / CCAR data "
        "lineage, cataloging, and automated validation frameworks that cut regulatory reporting errors "
        "by 40%. Leads platform lifecycle across architecture, operating model, and engineering scale-out, "
        "and implements Basel III and CCAR data lineage, cataloging, and automated validation frameworks "
        "that cut regulatory reporting errors by 40%. Scaled ML engineering organization from 8 to 28 "
        "specialists, including senior engineers and platform leads."
    )
    assert _resume_word_count(pre_text) > _resume_word_count(post_text)
    assert _resume_word_count(post_text) < 95
    srfs = _srfs()
    facts = _facts()
    pre = {"resume_display_text": pre_text, "claim_ledger": [], "executive_summary_composition_plan": _plan()}
    post = {"resume_display_text": post_text, "claim_ledger": [], "executive_summary_composition_plan": _plan()}
    meta = evaluate_judge_safe_repair_monotonicity(pre, post, facts, srfs)
    assert meta["repair_candidate_accepted"] is False
    assert "word_count_regression" in (meta.get("rejection_reason") or "")
    assert meta["chosen_text_source"] == "pre_repair"


def test_reject_repair_introducing_duplicate_claim() -> None:
    pre_text = (
        "Engineering executive building governed agentic AI platforms for regulated enterprise environments. "
        "Designed runtime systems combining deterministic routing and GraphRAG retrieval with validation controls. "
        "Standardized AI lifecycle practices across intake, validation, execution, monitoring, and remediation. "
        "Delivered measurable commercial outcomes grounded in cited executive facts with platform scale discipline. "
        "Integrated AWS and FSA credentials reinforce quantitative credibility for stakeholders and enterprise risk."
    )
    post_text = (
        "Engineering executive building governed agentic AI platforms for regulated enterprise environments. "
        "Implemented Basel III / CCAR data lineage, cataloging, and automated validation frameworks that cut "
        "regulatory reporting errors by 40%. Leads platform lifecycle across architecture, operating model, and "
        "engineering scale-out, and implements Basel III and CCAR data lineage, cataloging, and automated validation "
        "frameworks that cut regulatory reporting errors by 40%. Scaled ML engineering organization from 8 to 28 "
        "specialists, including senior engineers and platform leads. Holds AWS Certified Solutions Architect credentials."
    )
    srfs = _srfs()
    facts = _facts()
    pre = {"resume_display_text": pre_text, "claim_ledger": []}
    post = {"resume_display_text": post_text, "claim_ledger": []}
    assert duplicate_sentence_or_claim_count(pre_text, []) == 0
    assert duplicate_sentence_or_claim_count(post_text, []) >= 1
    meta = evaluate_judge_safe_repair_monotonicity(pre, post, facts, srfs)
    assert meta["repair_candidate_accepted"] is False
    assert "duplicate" in (meta.get("rejection_reason") or "").lower()


def test_reject_repair_dropping_s5_when_required() -> None:
    pre_text = (
        "Engineering executive building governed agentic AI platforms for regulated enterprise environments. "
        "Designed runtime systems combining deterministic routing and GraphRAG retrieval with validation controls. "
        "Standardized AI lifecycle practices across intake, validation, execution, monitoring, and remediation. "
        "Delivered measurable commercial outcomes grounded in cited executive facts with platform scale discipline. "
        "Integrated AWS and FSA credentials reinforce quantitative credibility for stakeholders and enterprise risk."
    )
    post_text = (
        "Engineering executive building governed agentic AI platforms for regulated enterprise environments. "
        "Designed runtime systems combining deterministic routing and GraphRAG retrieval with validation controls. "
        "Standardized AI lifecycle practices across intake, validation, execution, monitoring, and remediation. "
        "Delivered measurable commercial outcomes grounded in cited executive facts with platform scale discipline. "
        "Scaled ML engineering organization from 8 to 28 specialists, including senior engineers and platform leads."
    )
    srfs = _srfs()
    facts = _facts()
    pre = {
        "resume_display_text": pre_text,
        "claim_ledger": [],
        "executive_summary_composition_plan": _plan(),
    }
    post = {"resume_display_text": post_text, "claim_ledger": [], "executive_summary_composition_plan": _plan()}
    meta = evaluate_judge_safe_repair_monotonicity(pre, post, facts, srfs)
    assert meta["s5_required"] is True
    assert meta["repair_candidate_accepted"] is False
    assert "s5_credentials_dropped" in (meta.get("rejection_reason") or "")


def test_accept_repair_removing_unsupported_claim_preserving_density() -> None:
    pre_text = (
        "Engineering executive building governed agentic AI platforms for regulated enterprise environments "
        "with sustained delivery across architecture, operating model, and engineering scale-out programs. "
        "Designed runtime systems combining deterministic routing, multi-agent orchestration, and GraphRAG retrieval "
        "with vector services and API gateways for enterprise data pipelines across regulated workflows. "
        "Standardized AI lifecycle practices across intake, validation, execution, monitoring, and remediation "
        "while preserving auditability, runtime stability, and traceability for enterprise stakeholders. "
        "Delivered measurable commercial outcomes grounded in cited executive facts with platform scale discipline "
        "and accountable governance for regulated platform programs across the enterprise portfolio. "
        "Integrated AWS and FSA credentials reinforce quantitative credibility for stakeholders and enterprise risk."
    )
    post_text = (
        "Engineering executive building governed agentic AI platforms for regulated enterprise environments "
        "with sustained delivery across architecture, operating model, and engineering scale-out programs. "
        "Designed runtime systems combining deterministic routing, multi-agent orchestration, and GraphRAG retrieval "
        "with validation controls, policy gating, and traceability for regulated enterprise workflows across platform operations. "
        "Standardized AI lifecycle practices across intake, validation, execution, monitoring, and remediation "
        "while preserving auditability, runtime stability, and traceability for enterprise stakeholders. "
        "Delivered measurable commercial outcomes grounded in cited executive facts with platform scale discipline "
        "and accountable governance for regulated platform programs across the enterprise portfolio. "
        "Integrated AWS and FSA credentials reinforce quantitative credibility for stakeholders and enterprise risk."
    )
    srfs = _srfs()
    facts = _facts()
    pre = {"resume_display_text": pre_text, "claim_ledger": []}
    post = {"resume_display_text": post_text, "claim_ledger": []}
    assert _resume_word_count(post_text) >= _resume_word_count(pre_text)
    assert _resume_word_count(post_text) >= 95
    meta = evaluate_judge_safe_repair_monotonicity(pre, post, facts, srfs)
    assert meta["repair_candidate_accepted"] is True
    assert meta["chosen_text_source"] == "repair_candidate"


def test_apply_repair_receipt_records_chosen_source_on_regression() -> None:
    pre_text = (
        "Engineering executive with extensive experience in designing and operationalizing governed "
        "agentic AI platforms for regulated enterprise workflows. Led the development of deterministic "
        "routing, multi-agent orchestration, GraphRAG retrieval, sandboxed execution, and policy gating, "
        "improving reliability and auditability. Productized these capabilities into reusable platform "
        "services, generating $22M in IP-led revenue, expanding gross margins by 20%, and scaling the ML "
        "engineering organization from 8 to 28 specialists. Holds AWS Certified Machine Learning Engineer - "
        "Associate, AWS Certified Solutions Architect - Professional, Databricks Lakehouse Fundamentals, "
        "and Fellow of the Society of Actuaries credentials."
    )
    srfs = _srfs()
    facts = _facts()
    parsed = {
        "resume_display_text": pre_text,
        "claim_ledger": [
            {"claim_text": "thesis", "source_fact_ids": ["fact_engineering_platform_006"]},
            {"claim_text": "mechanism", "source_fact_ids": ["fact_engineering_platform_001"]},
            {"claim_text": "commercial", "source_fact_ids": ["fact_exec_002"]},
            {"claim_text": "creds", "source_fact_ids": ["fact_certs_001"]},
        ],
        "executive_summary_composition_plan": _plan(),
    }
    out, meta = apply_srfs_judge_safe_repair(parsed, facts, srfs)
    assert meta is not None
    assert meta["pre_repair_word_count"] > meta["post_repair_word_count"]
    assert meta["chosen_text_source"] == "pre_repair"
    assert meta["repair_candidate_accepted"] is False
    assert out["resume_display_text"] == pre_text
    assert meta["before_resume_display_text"] == pre_text
    assert "rejection_reason" in meta
    assert "monotonic_x2_check" in meta
    assert "duplicate_detection_result" in meta


def test_core_candidate_differs_but_apply_keeps_pre_on_monotonic_reject() -> None:
    """When core rewrites regress density, wrapper must not publish the candidate."""
    pre_text = (
        "Engineering executive with extensive experience in designing and operationalizing governed "
        "agentic AI platforms for regulated enterprise workflows. Led the development of deterministic "
        "routing, multi-agent orchestration, GraphRAG retrieval, sandboxed execution, and policy gating, "
        "improving reliability and auditability. Productized these capabilities into reusable platform "
        "services, generating $22M in IP-led revenue, expanding gross margins by 20%, and scaling the ML "
        "engineering organization from 8 to 28 specialists. Holds AWS Certified Machine Learning Engineer - "
        "Associate, AWS Certified Solutions Architect - Professional, Databricks Lakehouse Fundamentals, "
        "and Fellow of the Society of Actuaries credentials."
    )
    srfs = _srfs()
    facts = _facts()
    parsed = {
        "resume_display_text": pre_text,
        "claim_ledger": [
            {"claim_text": "a", "source_fact_ids": ["fact_engineering_platform_001"]},
            {"claim_text": "b", "source_fact_ids": ["fact_engineering_platform_001"]},
            {"claim_text": "c", "source_fact_ids": ["fact_exec_002"]},
            {"claim_text": "d", "source_fact_ids": ["fact_certs_001"]},
        ],
    }
    candidate = _apply_srfs_judge_safe_repair_core(parsed, facts, srfs)
    assert candidate["resume_display_text"] != pre_text
    out, meta = apply_srfs_judge_safe_repair(parsed, facts, srfs)
    assert out["resume_display_text"] == pre_text
    assert meta is not None
    assert meta["post_repair_word_count"] < meta["pre_repair_word_count"] or (
        "x2_exec_summary_srfs_density_word_count" in meta["post_repair_failed_gates"]
    )
