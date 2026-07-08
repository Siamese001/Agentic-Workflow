"""apps-test-model: APP CONTRACT.

Deterministic headline X2 gates for fixed-prefix SVP Engineering | X | Y | Z contract.
"""
from __future__ import annotations

import json
from typing import Any

from apps_rg.runtime.sections.headline_lane import (
    build_mock_output,
    normalize_parsed_output,
    snapshot_raw_jd_alignment,
    _rewrite_machine_headline_segments,
)
from apps_rg.runtime.exit.headline_x3 import aggregate_x3
from apps_rg.runtime.validators.headline_x2 import run_headline_x2_gates
from apps_rg.runtime.validators.headline_x2 import check_headline_xyz_literal_grounding


def _fake_judges() -> list[dict[str, Any]]:
    return [
        {"provider_key": "gemini_pro", "evaluator_mode": "MOCKED", "provider_blocked": False},
        {"provider_key": "openai_chatgpt", "evaluator_mode": "MOCKED", "provider_blocked": False},
        {"provider_key": "anthropic_claude", "evaluator_mode": "MOCKED", "provider_blocked": False},
    ]

def _segment_claim_ledger(hl: str, source_fact_ids: list[str]) -> list[dict[str, Any]]:
    parts = [p.strip() for p in hl.split(" | ")]
    if len(parts) >= 4:
        return [
            {"claim_text": parts[1], "source_fact_ids": list(source_fact_ids)},
            {"claim_text": parts[2], "source_fact_ids": list(source_fact_ids)},
            {"claim_text": parts[3], "source_fact_ids": list(source_fact_ids)},
        ]
    return [{"claim_text": hl, "source_fact_ids": list(source_fact_ids)}]


def _base_kwargs(headline: str, **over) -> dict[str, Any]:
    allowed = {"bul_1", "bul_2", "bul_unify_001", "bul_ibm_001", "bul_unify_004"}
    parsed = {
        "headline_line": headline,
        "selected_fact_plan": {
            "section_id": "headline",
            "required_fact_ids": ["bul_1"],
            "facts": [
                {
                    "fact_id": "bul_1",
                    "claim_text": (
                        "Architected Lakehouse Microservices on Databricks; standardized "
                        "AI Lifecycle automation; engineered HPC Trading Workflows; "
                        "shipped Distributed Computing Architectures and Agentic Runtime "
                        "Catalogs with Enterprise Telemetry; led Runtime Governance "
                        "Architecture, Enterprise AI Platforms, Partner Co-Sell Motions, "
                        "Regulated AI Systems, Cloud Data Platforms, and Partner Cloud Ecosystems."
                    ),
                }
            ],
        },
        "claim_ledger": _segment_claim_ledger(headline, ["bul_1"]),
        "jd_alignment": {
            "targeting_only": True,
            "jd_used_as_proof": False,
            "briefing_used_as_proof": False,
            "selected_theme": "t",
            "anti_stuffing_check": "passed",
        },
        "gap_notes": [],
        "change_log": [],
        "self_check": {},
    }
    parsed.update(over.pop("parsed_extra", {}))
    base: dict[str, Any] = {
        "parsed_output": parsed,
        "claim_ledger": parsed["claim_ledger"],
        "jd_text": "enterprise platform delivery",
        "target_company": "",
        "target_title": "SVP Engineering",
        "resume_support_blob": json.dumps({"employment": [], "header": {"name": "A B"}}),
        "employer_names_lower": ["contoso", "fabrikam"],
        "allowed_fact_ids": allowed,
        "runtime_generation_status": "MOCKED",
        "provider_requested": "mock",
        "provider_attempted": "mock",
        "raw_output": json.dumps(parsed),
        "x1d_judges": _fake_judges(),
        "companion_context": "",
        "text_claim_coverage": {
            "schema": "headline_text_claim_coverage_v1",
            "overall_pass": True,
            "segments": [],
        },
    }
    base.update(over)
    return base


def _failed_ids(gates: list[Any]) -> list[str]:
    out: list[str] = []
    for g in gates:
        d = g.to_dict() if hasattr(g, "to_dict") else g
        if not d["pass"]:
            out.append(d["gate_id"])
    return out


def test_valid_canonical_derived_passes() -> None:
    hl = "SVP Engineering | Runtime Governance Architecture | Enterprise AI Platforms | Partner Co-Sell Motions"
    gates = run_headline_x2_gates(headline_line=hl, **_base_kwargs(hl))
    assert _failed_ids(gates) == []


def test_redundant_partner_ecosystem_segments_fail_segments_quality() -> None:
    hl = (
        "SVP Engineering | Provider Egress Governance Infrastructure | "
        "Hyperscaler Alliance Co-Sell | Partner Channel Alliance"
    )
    gates = run_headline_x2_gates(headline_line=hl, **_base_kwargs(hl))
    by_id = {g.gate_id: g for g in gates}

    assert "x2_headline_segments_quality" in _failed_ids(gates)
    assert "semantic_theme_overlap:partner_ecosystem" in str(
        by_id["x2_headline_segments_quality"].observed_value
    )


def test_standalone_vendor_architecture_segment_fails() -> None:
    hl = "SVP Engineering | Databricks Lakehouse | Enterprise AI Platforms | Partner Co-Sell Motions"
    gates = run_headline_x2_gates(headline_line=hl, **_base_kwargs(hl))
    failed = _failed_ids(gates)
    assert "x2_headline_no_standalone_vendor_architecture" in failed
    assert "x2_headline_executive_abstraction_floor" in failed


def test_vendor_terms_allowed_in_proof_not_display() -> None:
    hl = "SVP Engineering | Cloud Data Platforms | Enterprise AI Platforms | Partner Cloud Ecosystems"
    gates = run_headline_x2_gates(headline_line=hl, **_base_kwargs(hl))
    failed = _failed_ids(gates)
    assert "x2_headline_no_standalone_vendor_architecture" not in failed
    assert "x2_headline_vendor_terms_proof_only" not in failed
    assert failed == []


def test_three_segment_line_fails_pipe_gate() -> None:
    hl = "SVP Engineering | Agentic AI Platforms | Distributed AI Infrastructure"
    gates = run_headline_x2_gates(headline_line=hl, **_base_kwargs(hl))
    assert "x2_headline_pipe_four_segments" in _failed_ids(gates)


def test_missing_fixed_prefix_fails() -> None:
    hl = "Engineering Executive | Agentic AI Platforms | Distributed AI Infrastructure | Governed Enterprise Systems"
    gates = run_headline_x2_gates(headline_line=hl, **_base_kwargs(hl))
    assert "x2_headline_pipe_four_segments" in _failed_ids(gates)


def test_word_count_too_short_fails() -> None:
    hl = "SVP Engineering | Agentic AI Platforms | More Here | Extra Bit"
    gates = run_headline_x2_gates(headline_line=hl, **_base_kwargs(hl))
    assert "x2_headline_word_count_10_to_13" in _failed_ids(gates)


def test_word_count_too_long_fails() -> None:
    hl = (
        "SVP Engineering | Agentic AI Platform Products | Distributed AI Infrastructure Systems | "
        "Governed Enterprise Architecture And Scale Delivery"
    )
    gates = run_headline_x2_gates(headline_line=hl, **_base_kwargs(hl))
    assert "x2_headline_word_count_10_to_13" in _failed_ids(gates)


def test_keyword_stuffing_heuristic_fails() -> None:
    hl = (
        "SVP Engineering | AI ML Cloud Data Security | Digital Transformation | "
        "Innovation Leadership Scope"
    )
    gates = run_headline_x2_gates(headline_line=hl, **_base_kwargs(hl))
    assert "x2_headline_no_keyword_stuffing_heuristic" in _failed_ids(gates)


def test_metrics_fail() -> None:
    hl = "SVP Engineering | Agentic AI Platforms | $22M Revenue Growth | Distributed Infrastructure"
    gates = run_headline_x2_gates(headline_line=hl, **_base_kwargs(hl))
    assert "x2_headline_no_metrics" in _failed_ids(gates)


def test_target_company_in_headline_fails() -> None:
    hl = "SVP Engineering | Agentic AI Platforms | Contoso Holdings International | Enterprise Systems"
    gates = run_headline_x2_gates(
        headline_line=hl,
        **_base_kwargs(hl, target_company="Contoso Holdings International"),
    )
    assert "x2_no_target_company_as_experience" in _failed_ids(gates)


def test_unsupported_claim_fact_ids_fail() -> None:
    hl = "SVP Engineering | Agentic AI Platforms | Distributed AI Infrastructure | Governed Enterprise Systems"
    parsed = {
        "headline_line": hl,
        "selected_fact_plan": {"section_id": "headline", "required_fact_ids": ["bul_1"]},
        "claim_ledger": _segment_claim_ledger(hl, ["bul_nope"]),
        "jd_alignment": {
            "targeting_only": True,
            "jd_used_as_proof": False,
            "briefing_used_as_proof": False,
            "selected_theme": "t",
            "anti_stuffing_check": "passed",
        },
        "gap_notes": [],
        "change_log": [],
        "self_check": {},
    }
    gates = run_headline_x2_gates(
        headline_line=hl,
        parsed_output=parsed,
        claim_ledger=parsed["claim_ledger"],
        jd_text="x",
        target_company="",
        target_title="",
        resume_support_blob="{}",
        employer_names_lower=[],
        allowed_fact_ids={"bul_1"},
        runtime_generation_status="MOCKED",
        provider_requested="mock",
        provider_attempted="mock",
        raw_output=json.dumps(parsed),
        x1d_judges=_fake_judges(),
        companion_context="",
    )
    assert "x2_headline_source_supported" in _failed_ids(gates)


def test_dispatch_normalize_merges_schema_keys_for_parser() -> None:
    runtime_payload = {
        "selected_fact_plan": {
            "section_id": "headline",
            "selection_method": "canonical_base_resume_employment_bullets",
            "required_fact_ids": ["bul_unify_001", "bul_ibm_001", "bul_unify_004"],
            "facts": [],
        }
    }
    allowed = {"bul_unify_001", "bul_ibm_001", "bul_unify_004"}
    mo = build_mock_output(runtime_payload)
    out = normalize_parsed_output(mo, runtime_payload, allowed, str(mo["headline_line"]))
    assert out is not None
    for k in ("headline_line", "jd_alignment", "self_check", "claim_ledger"):
        assert k in out
    assert len(out["claim_ledger"]) == 3
    jd = out["jd_alignment"]
    assert jd.get("jd_used_as_proof") is False
    assert jd.get("briefing_used_as_proof") is False
    assert out["self_check"].get("separator_count") == 3
    assert out["self_check"].get("segment_count") == 4


def test_companion_nonempty_missing_companion_used_as_proof_fails() -> None:
    hl = "SVP Engineering | Agentic AI Platforms | Distributed AI Infrastructure | Governed Enterprise Systems"
    kwargs = _base_kwargs(hl, companion_context="### executive_summary\nTone only.")
    jd = kwargs["parsed_output"]["jd_alignment"]
    jd.pop("companion_used_as_proof", None)
    gates = run_headline_x2_gates(headline_line=hl, **kwargs)
    assert "x2_headline_companion_context_not_proof" in _failed_ids(gates)


def test_companion_nonempty_companion_used_as_proof_true_fails() -> None:
    hl = "SVP Engineering | Agentic AI Platforms | Distributed AI Infrastructure | Governed Enterprise Systems"
    kwargs = _base_kwargs(hl, companion_context="### executive_summary\nTone only.")
    kwargs["parsed_output"]["jd_alignment"]["companion_used_as_proof"] = True
    gates = run_headline_x2_gates(headline_line=hl, **kwargs)
    assert "x2_headline_companion_context_not_proof" in _failed_ids(gates)


def test_companion_nonempty_companion_used_as_proof_false_passes() -> None:
    hl = "SVP Engineering | Agentic AI Platforms | Distributed AI Infrastructure | Governed Enterprise Systems"
    kwargs = _base_kwargs(hl, companion_context="### executive_summary\nTone only.")
    kwargs["parsed_output"]["jd_alignment"]["companion_used_as_proof"] = False
    gates = run_headline_x2_gates(headline_line=hl, **kwargs)
    assert "x2_headline_companion_context_not_proof" not in _failed_ids(gates)


def test_companion_empty_missing_companion_used_as_proof_passes_gate() -> None:
    hl = "SVP Engineering | Agentic AI Platforms | Distributed AI Infrastructure | Governed Enterprise Systems"
    kwargs = _base_kwargs(hl)
    jd = kwargs["parsed_output"]["jd_alignment"]
    jd.pop("companion_used_as_proof", None)
    gates = run_headline_x2_gates(headline_line=hl, **kwargs)
    assert "x2_headline_companion_context_not_proof" not in _failed_ids(gates)


def test_companion_empty_companion_used_as_proof_true_fails() -> None:
    hl = "SVP Engineering | Agentic AI Platforms | Distributed AI Infrastructure | Governed Enterprise Systems"
    kwargs = _base_kwargs(hl)
    kwargs["parsed_output"]["jd_alignment"]["companion_used_as_proof"] = True
    gates = run_headline_x2_gates(headline_line=hl, **kwargs)
    assert "x2_headline_companion_context_not_proof" in _failed_ids(gates)


def test_x2_companion_gate_prefers_raw_jd_alignment() -> None:
    hl = "SVP Engineering | Agentic AI Platforms | Distributed AI Infrastructure | Governed Enterprise Systems"
    kwargs = _base_kwargs(hl, companion_context="### executive_summary\nTone only.")
    po = kwargs["parsed_output"]
    po["raw_jd_alignment"] = {
        "targeting_only": True,
        "jd_used_as_proof": False,
        "briefing_used_as_proof": False,
        "selected_theme": "t",
        "anti_stuffing_check": "passed",
    }
    po["jd_alignment"] = {
        **po["raw_jd_alignment"],
        "companion_used_as_proof": False,
    }
    gates = run_headline_x2_gates(headline_line=hl, **kwargs)
    assert "x2_headline_companion_context_not_proof" in _failed_ids(gates)


def test_snapshot_raw_jd_alignment_unaffected_by_normalize_structural_defaults() -> None:
    runtime_payload = {
        "selected_fact_plan": {
            "section_id": "headline",
            "selection_method": "canonical_base_resume_employment_bullets",
            "required_fact_ids": ["bul_unify_001", "bul_ibm_001", "bul_unify_004"],
            "facts": [],
        }
    }
    allowed = {"bul_unify_001", "bul_ibm_001", "bul_unify_004"}
    mo = build_mock_output(runtime_payload)
    mo["jd_alignment"] = {
        "targeting_only": True,
        "jd_used_as_proof": False,
        "briefing_used_as_proof": False,
        "selected_theme": "agentic_platforms",
        "anti_stuffing_check": "passed",
    }
    snapshot_raw_jd_alignment(mo)
    frozen = json.loads(json.dumps(mo["raw_jd_alignment"]))
    out = normalize_parsed_output(mo, runtime_payload, allowed, str(mo["headline_line"]), companion_nonempty=True)
    assert out is not None
    assert out["raw_jd_alignment"] == frozen
    assert "companion_used_as_proof" not in frozen


def test_mocked_runtime_with_passing_x2_still_not_x3_allow() -> None:
    hl = "SVP Engineering | Runtime Governance Architecture | Enterprise AI Platforms | Partner Co-Sell Motions"
    kwargs = _base_kwargs(
        hl,
        runtime_generation_status="MOCKED",
        provider_requested="mock",
        provider_attempted="mock",
    )
    gates = run_headline_x2_gates(headline_line=hl, **kwargs)
    assert _failed_ids(gates) == []
    x2_dicts = [g.to_dict() for g in gates]
    x3 = aggregate_x3(
        resume_display_text=hl,
        claim_ledger=kwargs["claim_ledger"],
        x2_gates=x2_dicts,
        x1d_judges=_fake_judges(),
        runtime_generation_status="MOCKED",
        product_quality_status="PASS",
    )
    assert x3.x3_code != "X3_ALLOW"
    assert x3.pass_ is False


_NEGATIVE_STYLE_GATE_IDS = (
    "x2_no_first_person",
    "x2_no_em_dash",
    "x2_headline_no_inline_source_tags",
)


def test_passing_negative_style_gates_have_clean_evidence_fields() -> None:
    """PASS rows must not reuse failure-only copy in observed_value/failure_reason."""
    hl = "SVP Engineering | Agentic AI Platforms | Distributed AI Infrastructure | Governed Enterprise Systems"
    gates = run_headline_x2_gates(headline_line=hl, **_base_kwargs(hl))
    by_id = {g.gate_id: g for g in gates}
    for gid in _NEGATIVE_STYLE_GATE_IDS:
        g = by_id[gid]
        assert g.pass_ is True
        assert g.failure_reason is None
        assert g.observed_value == "absent"


def test_machine_phrase_repair_rewrites_governed_runtime_architecture() -> None:
    hl = "SVP Engineering | Governed Runtime Architecture | Partner Co-Sell Motions | Distributed Cloud Data"

    repaired, changes = _rewrite_machine_headline_segments(hl)

    assert repaired == "SVP Engineering | Runtime Governance Architecture | Partner Co-Sell Motions | Distributed Cloud Data"
    assert changes == [{"from": "Governed Runtime Architecture", "to": "Runtime Governance Architecture"}]


def test_machine_phrase_repair_rewrites_hyperscaler_alliance_revenue() -> None:
    hl = (
        "SVP Engineering | Distributed Cloud Data Infrastructure | "
        "Egress Governance Controls | Hyperscaler Alliance Revenue"
    )

    repaired, changes = _rewrite_machine_headline_segments(hl)

    assert repaired == (
        "SVP Engineering | Distributed Cloud Data Infrastructure | "
        "Egress Governance Controls | Hyperscaler Partner Ecosystem"
    )
    assert changes == [{"from": "Hyperscaler Alliance Revenue", "to": "Hyperscaler Partner Ecosystem"}]


def test_live_policy_administration_migration_repair_clears_executive_floor() -> None:
    hl = (
        "SVP Engineering | Distributed Cloud Infrastructure | "
        "Hyperscaler Alliance Co-Sell | Policy Administration Migration"
    )
    fact_ids = [
        "reb_unify_distributed_ecosystem_engineering",
        "reb_ibm_aws_alliance_partner_cosell_gtm",
        "reb_insurtech_aws_migration_execution",
    ]
    selected_fact_plan = {
        "section_id": "headline",
        "required_fact_ids": list(fact_ids),
        "selected_claim_fact_ids": list(fact_ids),
        "selected_required_fact_ids": list(fact_ids),
        "facts": [
            {
                "fact_id": "reb_unify_distributed_ecosystem_engineering",
                "claim_text": "Distributed cloud and data execution infrastructure",
                "graph_skill_node_ids": ["skill_sr_cloud_data_platform_engineering"],
            },
            {
                "fact_id": "reb_ibm_aws_alliance_partner_cosell_gtm",
                "claim_text": "Led IBM-AWS alliance co-sell motions for financial-services modernization opportunities",
                "graph_skill_node_ids": ["skill_partner_hyperscaler_cosell"],
            },
            {
                "fact_id": "reb_insurtech_aws_migration_execution",
                "claim_text": (
                    "Led AWS modernization execution for monolithic policy administration "
                    "and insurance platform workloads."
                ),
                "graph_skill_node_ids": ["skill_aws_migration_readiness_assessment"],
            },
        ],
    }
    parsed = {
        "headline_line": hl,
        "selected_fact_plan": selected_fact_plan,
        "claim_ledger": [
            {"claim_text": "Distributed Cloud Infrastructure", "source_fact_ids": [fact_ids[0]]},
            {"claim_text": "Hyperscaler Alliance Co-Sell", "source_fact_ids": [fact_ids[1]]},
            {"claim_text": "Policy Administration Migration", "source_fact_ids": [fact_ids[2]]},
        ],
        "jd_alignment": {
            "targeting_only": True,
            "jd_used_as_proof": False,
            "briefing_used_as_proof": False,
            "selected_theme": "distributed cloud infrastructure, hyperscaler co-sell, policy migration",
            "anti_stuffing_check": "passed",
        },
        "gap_notes": [],
        "change_log": [],
        "self_check": {},
    }
    runtime_payload = {"target_company": "", "selected_fact_plan": selected_fact_plan}

    out = normalize_parsed_output(parsed, runtime_payload, set(fact_ids), hl)

    assert out is not None
    assert out["headline_line"] == (
        "SVP Engineering | Distributed Cloud Infrastructure | "
        "Hyperscaler Alliance Co-Sell | Policy Administration Platforms"
    )
    assert [row["claim_text"] for row in out["claim_ledger"]] == [
        "Distributed Cloud Infrastructure",
        "Hyperscaler Alliance Co-Sell",
        "Policy Administration Platforms",
    ]
    gates = run_headline_x2_gates(
        headline_line=out["headline_line"],
        parsed_output=out,
        claim_ledger=out["claim_ledger"],
        jd_text="enterprise platform delivery",
        target_company="",
        target_title="SVP Engineering",
        resume_support_blob=json.dumps({"employment": [], "header": {"name": "A B"}}),
        employer_names_lower=[],
        allowed_fact_ids=set(fact_ids),
        runtime_generation_status="REAL_LLM",
        provider_requested="external_claude",
        provider_attempted="external_claude",
        raw_output=json.dumps(out),
        raw_model_parsed_before_normalize=parsed,
        x1d_judges=_fake_judges(),
        companion_context="",
        text_claim_coverage={"schema": "headline_text_claim_coverage_v1", "overall_pass": True, "segments": []},
    )
    assert "x2_headline_executive_abstraction_floor" not in _failed_ids(gates)
    assert _failed_ids(gates) == []


def test_live_aws_migration_execution_repair_clears_headline_floors() -> None:
    hl = (
        "SVP Engineering | Distributed Cloud Infrastructure | "
        "Hyperscaler Alliance Co-Sell | AWS Migration Execution"
    )
    fact_ids = [
        "reb_unify_distributed_ecosystem_engineering",
        "skill_provider_and_egress_governance",
        "skill_sr_cloud_data_platform_engineering",
        "reb_ibm_aws_alliance_partner_cosell_gtm",
        "skill_partner_hyperscaler_cosell",
        "skill_sr_w12_hyperscaler_alliance_co_sell",
        "reb_insurtech_aws_migration_execution",
        "skill_aws_migration_readiness_assessment",
    ]
    selected_fact_plan = {
        "section_id": "headline",
        "required_fact_ids": list(fact_ids),
        "selected_claim_fact_ids": list(fact_ids),
        "selected_required_fact_ids": list(fact_ids),
        "facts": [
            {
                "fact_id": "reb_unify_distributed_ecosystem_engineering",
                "claim_text": "Distributed cloud and data execution infrastructure",
                "graph_skill_node_ids": ["skill_sr_cloud_data_platform_engineering"],
            },
            {
                "fact_id": "reb_ibm_aws_alliance_partner_cosell_gtm",
                "claim_text": "Led IBM-AWS alliance co-sell motions for financial-services modernization opportunities",
                "graph_skill_node_ids": ["skill_partner_hyperscaler_cosell"],
            },
            {
                "fact_id": "reb_insurtech_aws_migration_execution",
                "claim_text": (
                    "Led AWS modernization execution for monolithic policy administration "
                    "and insurance platform workloads."
                ),
                "graph_skill_node_ids": ["skill_aws_migration_readiness_assessment"],
            },
        ],
    }
    parsed = {
        "headline_line": hl,
        "selected_fact_plan": selected_fact_plan,
        "claim_ledger": [
            {"claim_text": "Distributed Cloud Infrastructure", "source_fact_ids": fact_ids[:3]},
            {"claim_text": "Hyperscaler Alliance Co-Sell", "source_fact_ids": fact_ids[3:6]},
            {"claim_text": "AWS Migration Execution", "source_fact_ids": fact_ids[6:]},
        ],
        "jd_alignment": {
            "targeting_only": True,
            "jd_used_as_proof": False,
            "briefing_used_as_proof": False,
            "selected_theme": "distributed cloud infrastructure, hyperscaler co-sell, AWS migration execution",
            "anti_stuffing_check": "passed",
        },
        "gap_notes": [],
        "change_log": [],
        "self_check": {},
    }
    runtime_payload = {"target_company": "", "selected_fact_plan": selected_fact_plan}

    out = normalize_parsed_output(parsed, runtime_payload, set(fact_ids), hl)

    assert out is not None
    assert out["headline_line"] == (
        "SVP Engineering | Distributed Cloud Infrastructure | "
        "Hyperscaler Alliance Co-Sell | Policy Administration Platforms"
    )
    assert out["claim_ledger"][2]["claim_text"] == "Policy Administration Platforms"
    gates = run_headline_x2_gates(
        headline_line=out["headline_line"],
        parsed_output=out,
        claim_ledger=out["claim_ledger"],
        jd_text="enterprise platform delivery",
        target_company="",
        target_title="SVP Engineering",
        resume_support_blob=json.dumps({"employment": [], "header": {"name": "A B"}}),
        employer_names_lower=[],
        allowed_fact_ids=set(fact_ids),
        runtime_generation_status="REAL_LLM",
        provider_requested="external_claude",
        provider_attempted="external_claude",
        raw_output=json.dumps(out),
        raw_model_parsed_before_normalize=parsed,
        x1d_judges=_fake_judges(),
        companion_context="",
        text_claim_coverage={"schema": "headline_text_claim_coverage_v1", "overall_pass": True, "segments": []},
    )
    assert _failed_ids(gates) == []


def test_live_regulated_aws_migration_repair_adds_execution_for_grounding() -> None:
    hl = (
        "SVP Engineering | Distributed Cloud Infrastructure | "
        "Regulated AWS Migration | Hyperscaler Alliance Co-Sell"
    )
    fact_ids = [
        "reb_unify_distributed_ecosystem_engineering",
        "reb_ibm_aws_alliance_partner_cosell_gtm",
        "reb_insurtech_aws_migration_execution",
        "skill_aws_migration_readiness_assessment",
        "skill_partner_hyperscaler_cosell",
        "skill_sr_w12_hyperscaler_alliance_co_sell",
    ]
    selected_fact_plan = {
        "section_id": "headline",
        "required_fact_ids": list(fact_ids),
        "selected_claim_fact_ids": list(fact_ids),
        "selected_required_fact_ids": list(fact_ids),
        "facts": [
            {
                "fact_id": "reb_unify_distributed_ecosystem_engineering",
                "claim_text": "Distributed cloud and data execution infrastructure",
                "graph_skill_node_ids": ["skill_sr_cloud_data_platform_engineering"],
            },
            {
                "fact_id": "reb_ibm_aws_alliance_partner_cosell_gtm",
                "claim_text": "Led IBM-AWS alliance co-sell motions for financial-services modernization opportunities",
                "graph_skill_node_ids": ["skill_partner_hyperscaler_cosell"],
            },
            {
                "fact_id": "reb_insurtech_aws_migration_execution",
                "claim_text": (
                    "Led AWS modernization execution for monolithic policy administration "
                    "and insurance platform workloads."
                ),
                "graph_skill_node_ids": ["skill_aws_migration_readiness_assessment"],
            },
        ],
    }
    parsed = {
        "headline_line": hl,
        "selected_fact_plan": selected_fact_plan,
        "claim_ledger": [
            {"claim_text": "Distributed Cloud Infrastructure", "source_fact_ids": fact_ids},
            {"claim_text": "Regulated AWS Migration", "source_fact_ids": fact_ids},
            {"claim_text": "Hyperscaler Alliance Co-Sell", "source_fact_ids": fact_ids},
        ],
        "jd_alignment": {
            "targeting_only": True,
            "jd_used_as_proof": False,
            "briefing_used_as_proof": False,
            "selected_theme": "distributed cloud infrastructure, regulated AWS migration, hyperscaler co-sell",
            "anti_stuffing_check": "passed",
        },
        "gap_notes": [],
        "change_log": [],
        "self_check": {"word_count": 11},
    }
    runtime_payload = {"target_company": "", "selected_fact_plan": selected_fact_plan}

    out = normalize_parsed_output(parsed, runtime_payload, set(fact_ids), hl)

    assert out is not None
    assert out["headline_line"] == (
        "SVP Engineering | Distributed Cloud Infrastructure | "
        "Regulated AWS Migration Execution | Hyperscaler Alliance Co-Sell"
    )
    assert out["self_check"]["word_count"] == 12
    gates = run_headline_x2_gates(
        headline_line=out["headline_line"],
        parsed_output=out,
        claim_ledger=out["claim_ledger"],
        jd_text="enterprise platform delivery",
        target_company="",
        target_title="SVP Engineering",
        resume_support_blob=json.dumps({"employment": [], "header": {"name": "A B"}}),
        employer_names_lower=[],
        allowed_fact_ids=set(fact_ids),
        runtime_generation_status="REAL_LLM",
        provider_requested="external_claude",
        provider_attempted="external_claude",
        raw_output=json.dumps(out),
        raw_model_parsed_before_normalize=parsed,
        x1d_judges=_fake_judges(),
        companion_context="",
        text_claim_coverage={"schema": "headline_text_claim_coverage_v1", "overall_pass": True, "segments": []},
    )
    assert _failed_ids(gates) == []


def test_live_aws_migration_modernization_execution_repair_clears_headline_floors() -> None:
    hl = (
        "SVP Engineering | Distributed Cloud Infrastructure | "
        "Governed Partner Cosell Alliances | AWS Migration Modernization Execution"
    )
    fact_ids = [
        "reb_unify_distributed_ecosystem_engineering",
        "reb_unify_partner_channel_cosell",
        "reb_ibm_aws_alliance_partner_cosell_gtm",
        "reb_insurtech_aws_migration_execution",
    ]
    selected_fact_plan = {
        "section_id": "headline",
        "required_fact_ids": list(fact_ids),
        "selected_claim_fact_ids": list(fact_ids),
        "selected_required_fact_ids": list(fact_ids),
        "facts": [
            {
                "fact_id": "reb_unify_distributed_ecosystem_engineering",
                "claim_text": "Distributed cloud and data execution infrastructure",
                "graph_skill_node_ids": ["skill_sr_cloud_data_platform_engineering"],
            },
            {
                "fact_id": "reb_unify_partner_channel_cosell",
                "claim_text": "Governed partner cosell alliances, partner co-sell, and cloud vendor joint GTM motions",
                "graph_skill_node_ids": ["skill_partner_co_selling"],
            },
            {
                "fact_id": "reb_ibm_aws_alliance_partner_cosell_gtm",
                "claim_text": "Led IBM-AWS alliance co-sell motions for modernization opportunities",
                "graph_skill_node_ids": ["skill_partner_hyperscaler_cosell"],
            },
            {
                "fact_id": "reb_insurtech_aws_migration_execution",
                "claim_text": (
                    "Led AWS modernization execution for monolithic policy administration "
                    "platforms and insurance platform workloads."
                ),
                "graph_skill_node_ids": ["skill_aws_migration_readiness_assessment"],
            },
        ],
    }
    parsed = {
        "headline_line": hl,
        "selected_fact_plan": selected_fact_plan,
        "claim_ledger": [
            {"claim_text": "Distributed Cloud Infrastructure", "source_fact_ids": fact_ids[:1]},
            {"claim_text": "Governed Partner Cosell Alliances", "source_fact_ids": fact_ids[1:3]},
            {"claim_text": "AWS Migration Modernization Execution", "source_fact_ids": fact_ids[3:]},
        ],
        "jd_alignment": {
            "targeting_only": True,
            "jd_used_as_proof": False,
            "briefing_used_as_proof": False,
            "selected_theme": "distributed cloud infrastructure, governed partner co-sell, AWS migration modernization execution",
            "anti_stuffing_check": "passed",
        },
        "gap_notes": [],
        "change_log": [],
        "self_check": {},
    }
    runtime_payload = {"target_company": "", "selected_fact_plan": selected_fact_plan}

    out = normalize_parsed_output(parsed, runtime_payload, set(fact_ids), hl)

    assert out is not None
    assert out["headline_line"] == (
        "SVP Engineering | Distributed Cloud Infrastructure | "
        "Governed Partner Cosell Alliances | Policy Administration Platforms"
    )
    assert out["claim_ledger"][2]["claim_text"] == "Policy Administration Platforms"
    gates = run_headline_x2_gates(
        headline_line=out["headline_line"],
        parsed_output=out,
        claim_ledger=out["claim_ledger"],
        jd_text="enterprise platform delivery",
        target_company="",
        target_title="SVP Engineering",
        resume_support_blob=json.dumps({"employment": [], "header": {"name": "A B"}}),
        employer_names_lower=[],
        allowed_fact_ids=set(fact_ids),
        runtime_generation_status="REAL_LLM",
        provider_requested="external_claude",
        provider_attempted="external_claude",
        raw_output=json.dumps(out),
        raw_model_parsed_before_normalize=parsed,
        x1d_judges=_fake_judges(),
        companion_context="",
        text_claim_coverage={"schema": "headline_text_claim_coverage_v1", "overall_pass": True, "segments": []},
    )
    assert "x2_headline_executive_abstraction_floor" not in _failed_ids(gates)
    assert "x2_headline_vendor_terms_proof_only" not in _failed_ids(gates)
    assert _failed_ids(gates) == []


def test_live_partner_alliance_cosell_repair_binds_graph_skills() -> None:
    hl = (
        "SVP Engineering | Distributed Cloud Infrastructure | "
        "Regulated AWS Modernization | Partner Alliance Cosell"
    )
    fact_ids = [
        "reb_ibm_aws_modernization_architecture",
        "reb_unify_distributed_ecosystem_engineering",
        "reb_unify_partner_channel_cosell",
    ]
    selected_fact_plan = {
        "section_id": "headline",
        "required_fact_ids": list(fact_ids),
        "selected_claim_fact_ids": list(fact_ids),
        "selected_required_fact_ids": list(fact_ids),
        "facts": [
            {
                "fact_id": "reb_unify_distributed_ecosystem_engineering",
                "claim_text": "Distributed cloud and data execution infrastructure",
                "graph_skill_node_ids": [
                    "skill_sr_cloud_data_platform_engineering",
                    "skill_dense_sparse_exact_retrieval_design",
                ],
            },
            {
                "fact_id": "reb_unify_partner_channel_cosell",
                "claim_text": "AI Partnerships, Co-Sell Channel & Alliance GTM",
                "graph_skill_node_ids": [
                    "skill_partner_partner_motions",
                    "skill_partner_co_selling",
                    "skill_partner_cloud_vendor_joint_gtm",
                ],
            },
            {
                "fact_id": "reb_ibm_aws_modernization_architecture",
                "claim_text": (
                    "Led AWS modernization architecture for regulated financial-services "
                    "workloads moving from on-prem constraints to cloud-native delivery patterns"
                ),
                "graph_skill_node_ids": [
                    "skill_p2_tech_aws_modernization_patterns",
                    "skill_p2_tech_reference_architecture",
                ],
            },
        ],
        "selected_skills": [
            {
                "skill_id": "skill_partner_co_selling",
                "role_episode_bundle_id": "reb_unify_partner_channel_cosell",
            }
        ],
    }
    parsed = {
        "headline_line": hl,
        "selected_fact_plan": selected_fact_plan,
        "claim_ledger": _segment_claim_ledger(hl, fact_ids),
        "jd_alignment": {
            "targeting_only": True,
            "jd_used_as_proof": False,
            "briefing_used_as_proof": False,
            "selected_theme": "t",
            "anti_stuffing_check": "passed",
        },
        "gap_notes": [],
        "change_log": [],
        "self_check": {},
    }
    runtime_payload = {
        "target_company": "",
        "selected_fact_plan": selected_fact_plan,
    }

    out = normalize_parsed_output(parsed, runtime_payload, set(fact_ids), hl)

    assert out is not None
    assert out["headline_line"] == (
        "SVP Engineering | Distributed Cloud Infrastructure | "
        "Regulated AWS Modernization | Co-Sell Channel Alliance"
    )
    lineage = next(
        row
        for row in out["change_log"]
        if isinstance(row, dict) and row.get("operation") == "headline_graph_skill_lineage_binding"
    )
    assert "skill_partner_co_selling" in lineage["graph_skill_node_ids"]
    assert "reb_unify_partner_channel_cosell" in lineage["source_fact_ids"]

    fact_text = {
        fact["fact_id"]: fact["claim_text"]
        for fact in selected_fact_plan["facts"]
        if isinstance(fact, dict)
    }
    ok, _observed, failure = check_headline_xyz_literal_grounding(
        headline_line=out["headline_line"],
        claim_ledger=out["claim_ledger"],
        fact_id_to_text=fact_text,
    )
    assert ok is True, failure

    from apps_rg.runtime.validators.headline_positioning_x2 import run_headline_positioning_x2_gates

    positioning_gates = {
        g.gate_id: g
        for g in run_headline_positioning_x2_gates(
            headline_line=out["headline_line"],
            parsed_output=out,
            proof_pool_metadata={
                "headline_positioning_bundle_consumption": True,
                "headline_positioning_bundles": [
                    {
                        "headline_positioning_bundle_id": "hpb_dummy",
                        "linked_source_fact_ids": ["fact_dummy"],
                        "graph_skill_node_ids": ["skill_dummy"],
                    }
                ],
            },
            jd_text="enterprise platform delivery",
        )
    }
    assert positioning_gates["x2_headline_graph_skill_node_ids_required"].passed
    assert positioning_gates["x2_headline_source_fact_or_graph_lineage_required"].passed
