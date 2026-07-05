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
