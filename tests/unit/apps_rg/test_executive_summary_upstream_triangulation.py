"""Dimension upstream triangulation and judge cost controls."""

from __future__ import annotations

from apps_rg.runtime.sections.executive_summary_judge_remediation import (
    evaluate_judge_remediation_trigger,
)
from apps_rg.runtime.sections.executive_summary_repair_policy import (
    JUDGE_REGEN_MAX_ATTEMPTS,
    POST_REGEN_JUDGE_RESCORE_FULL_PANEL,
    POST_REGEN_JUDGE_RESCORE_SOFT_ONLY,
    post_regen_judge_rescore_mode,
)
from apps_rg.runtime.sections.executive_summary_upstream_triangulation import (
    build_dimension_upstream_triangulation,
    consensus_failed_dimensions,
    solitary_dimension_severe_soft_fail,
)


def _judge(
    pk: str,
    *,
    score: float,
    passed: bool,
    dimension_verdicts: dict | None = None,
) -> dict:
    return {
        "provider_key": pk,
        "evaluator_mode": "MODEL_BACKED",
        "provider_status": "MODEL_BACKED_PASS" if passed else "MODEL_BACKED_FAIL",
        "pass": passed,
        "score": score,
        "normalized_score": score / 5.0,
        "normalized_threshold": 0.8,
        "decisive_failure": False,
        "dimension_verdicts": dimension_verdicts or {},
    }


def test_default_judge_regen_cap_is_three() -> None:
    assert JUDGE_REGEN_MAX_ATTEMPTS == 3


def test_post_regen_rescore_defaults_full_panel(monkeypatch) -> None:
    monkeypatch.delenv("APPS_RG_EXEC_SUMMARY_POST_REGEN_JUDGE_MODE", raising=False)
    assert post_regen_judge_rescore_mode() == POST_REGEN_JUDGE_RESCORE_FULL_PANEL


def test_post_regen_rescore_can_be_lowered_to_soft_only(monkeypatch) -> None:
    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_POST_REGEN_JUDGE_MODE", "soft_failed_only")
    assert post_regen_judge_rescore_mode() == POST_REGEN_JUDGE_RESCORE_SOFT_ONLY


def test_consensus_failed_dimensions_two_judges() -> None:
    judges = [
        _judge(
            "openai_chatgpt",
            score=3.2,
            passed=False,
            dimension_verdicts={
                "synthesis_quality": {"pass": False, "severity": "major", "codes": ["weak_synthesis"]},
                "executive_signal": {"pass": False, "severity": "major", "codes": []},
            },
        ),
        _judge(
            "anthropic_claude",
            score=3.4,
            passed=False,
            dimension_verdicts={
                "synthesis_quality": {"pass": False, "severity": "major", "codes": []},
                "executive_signal": {"pass": False, "severity": "major", "codes": []},
            },
        ),
        _judge("gemini_pro", score=4.5, passed=True),
    ]
    failed = consensus_failed_dimensions(judges, min_fail_count=2)
    assert "synthesis_quality" in failed
    assert "executive_signal" in failed


def test_solitary_dimension_major_soft_fail() -> None:
    solo = _judge(
        "anthropic_claude",
        score=3.4,
        passed=False,
        dimension_verdicts={
            "synthesis_quality": {"pass": False, "severity": "major", "codes": ["inventory"]},
        },
    )
    ok, dims = solitary_dimension_severe_soft_fail(solo)
    assert ok is True
    assert "synthesis_quality" in dims


def test_trigger_uses_dimension_consensus() -> None:
    judges = [
        _judge(
            "openai_chatgpt",
            score=3.2,
            passed=False,
            dimension_verdicts={
                "synthesis_quality": {"pass": False, "severity": "major", "codes": []},
            },
        ),
        _judge(
            "anthropic_claude",
            score=3.4,
            passed=False,
            dimension_verdicts={
                "synthesis_quality": {"pass": False, "severity": "major", "codes": []},
            },
        ),
        _judge("gemini_pro", score=4.5, passed=True),
    ]
    ok, receipt = evaluate_judge_remediation_trigger(
        judges, runtime_generation_status="REAL_LLM", x2_passed=True
    )
    assert ok is True
    assert receipt.get("trigger_mode") == "any_judge_below_floor"


def test_triangulation_maps_qwen_surfaces() -> None:
    judges = [
        _judge(
            "anthropic_claude",
            score=3.4,
            passed=False,
            dimension_verdicts={
                "synthesis_quality": {"pass": False, "severity": "major", "codes": ["weak_synthesis"]},
            },
        ),
        _judge("gemini_pro", score=4.5, passed=True),
        _judge("openai_chatgpt", score=4.2, passed=True),
    ]
    doc = build_dimension_upstream_triangulation(
        x1d_judges=judges,
        x2_failed_gate_ids=[],
        post_regen_judge_mode="soft_failed_only",
    )
    assert doc["schema"] == "executive_summary_dimension_upstream_triangulation_v1"
    assert "compiled_prompt.txt" in doc["qwen_prompt_refs"]["compiled_prompt"]
    synth_rows = [r for r in doc["per_dimension"] if r["dimension_id"] == "synthesis_quality"]
    assert synth_rows
    assert "executive_summary_composition_plan.json" in synth_rows[0]["qwen_prompt_surfaces"]


def test_triangulation_x2_block_recommends_qwen_first() -> None:
    doc = build_dimension_upstream_triangulation(
        x1d_judges=[],
        x2_failed_gate_ids=["x2_exec_summary_no_credential_dump"],
    )
    assert "X2 blocked" in doc["recommended_next_step"]
    assert "compiled_prompt" in doc["recommended_next_step"].lower() or "composition" in doc["recommended_next_step"].lower()
