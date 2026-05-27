"""W1 — Brown SVP gap hardening (E0 S6, proof-gap regen filter, delta allowlist)."""

from __future__ import annotations

from typing import Any

import pytest

from apps_rg.prompt_assembly.e0_examples import example_after_text
from apps_rg.runtime.sections.executive_summary_judge_remediation import (
    collect_judge_remediation_delta_lines,
)
from apps_rg.runtime.sections.executive_summary_regen_delta_policy import (
    DELTA_CLASS_EXECUTIVE_SIGNAL_AND_VOICE,
    DELTA_CLASS_S6_FORWARD_SYNTHESIS,
    build_regen_sentence_allowlist,
    resolve_delta_class,
)
from apps_rg.runtime.sections.executive_summary_repair_policy import (
    regen_artificial_caps_enabled,
)
from apps_rg.runtime.sections.executive_summary_synthesis_contract import (
    filter_judge_remediation_feedback_for_proof_gap,
    has_svp_targeting_proof_gap,
)


def _brown_allowed_fact_ids() -> set[str]:
    return {
        "fact_exec_002",
        "fact_engineering_platform_006",
        "fact_engineering_platform_001",
        "fact_governance_003",
        "fact_quant_hpc_001",
        "fact_quant_hpc_003",
    }


def test_e0_positive_svp_s6_compliant() -> None:
    prose = example_after_text("executive_summary", "exec_summary_pos_svp_it_strategy_001")
    low = prose.lower()
    assert "looking ahead" not in low
    assert "extend that arc toward" not in low
    assert "innovation incubation" in low


def test_has_svp_targeting_proof_gap_brown_pool() -> None:
    assert has_svp_targeting_proof_gap(allowed_fact_ids=_brown_allowed_fact_ids()) is True


def test_proof_gap_filters_insurance_remediation_lines() -> None:
    lines = [
        "JUDGE_DELTA_SOURCE provider_key=anthropic_claude provider_name=Anthropic Claude",
        "- Anthropic Claude remediation: Sharpen S1 to signal insurance brokerage context.",
        "- Anthropic Claude finding: S6 thin recap.",
    ]
    filtered, meta = filter_judge_remediation_feedback_for_proof_gap(
        lines,
        allowed_fact_ids=_brown_allowed_fact_ids(),
    )
    joined = "\n".join(filtered).lower()
    assert meta["proof_gap_filter"] == "active"
    assert meta["dropped_count"] >= 1
    assert "insurance brokerage" not in joined
    assert "proof_gap_reframe" in joined


@pytest.fixture
def _caps_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("APPS_RG_EXEC_SUMMARY_REGEN_CAPS", raising=False)


def test_s6_allowlist_strict_when_caps_disabled(_caps_disabled: None) -> None:
    assert regen_artificial_caps_enabled() is False
    judges = [
        {
            "provider_key": "anthropic_claude",
            "evaluator_mode": "MODEL_BACKED",
            "provider_status": "MODEL_BACKED_FAIL",
            "pass": False,
            "cited_sentence_indexes": [1, 5, 6],
            "findings": ["S6 thin recap."],
        },
    ]
    allow, meta = build_regen_sentence_allowlist(judges, DELTA_CLASS_S6_FORWARD_SYNTHESIS)
    assert allow == frozenset({6})
    assert "delta_class_s6_strict" in meta["allowlist_sources"]


def _anthropic_brown_soft_fail() -> dict[str, Any]:
    return {
        "provider_key": "anthropic_claude",
        "evaluator_mode": "MODEL_BACKED",
        "provider_status": "MODEL_BACKED_FAIL",
        "pass": False,
        "score": 3.8,
        "cited_sentence_indexes": [1, 5, 6],
        "findings": [
            "S6 is a thin forward-looking recap.",
            "S5 reads as biographical inventory.",
        ],
        "dimension_verdicts": {
            "synthesis_quality": {
                "pass": False,
                "severity": "minor",
                "codes": ["thin_s6_recap"],
            },
            "executive_signal": {"pass": True, "severity": "none", "codes": []},
            "resume_voice": {"pass": True, "severity": "none", "codes": []},
            "factual_support": {"pass": True, "severity": "none", "codes": []},
            "ats_alignment_without_keyword_stuffing": {
                "pass": True,
                "severity": "none",
                "codes": [],
            },
            "anti_overfit": {"pass": True, "severity": "none", "codes": []},
            "evidence_utilization": {"pass": True, "severity": "none", "codes": []},
            "deterministic_alignment": {"pass": True, "severity": "none", "codes": []},
        },
    }


def test_anthropic_multi_sentence_cite_routes_composite_delta_class() -> None:
    judges = [_anthropic_brown_soft_fail()]
    assert resolve_delta_class(judges) == DELTA_CLASS_EXECUTIVE_SIGNAL_AND_VOICE


def test_collect_delta_includes_proof_boundary_guard(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_JUDGE_REGEN_PRESCRIPTIVE_DELTA", "1")
    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_REGEN_LEGACY_BLOCK", "0")
    lines = collect_judge_remediation_delta_lines(
        [_anthropic_brown_soft_fail()],
        unused_fact_ids=[],
        allowed_fact_count=6,
        allowed_fact_ids=_brown_allowed_fact_ids(),
        compact=True,
    )
    joined = "\n".join(lines)
    assert "PROOF_BOUNDARY_REGEN" in joined
    for line in lines:
        low = line.lower()
        if "remediation:" in low or "finding:" in low:
            assert "insurance brokerage" not in low
            assert "federated insurance" not in low
