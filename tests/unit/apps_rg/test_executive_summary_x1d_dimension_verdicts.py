"""Unit tests for executive_summary X1D dimension_verdicts and operator matrix."""

from __future__ import annotations

import json

import pytest

from apps_rg.runtime.judges.executive_summary_x1d import _make_model_backed_output
from apps_rg.runtime.judges.executive_summary_x1d_dimension_verdicts import (
    EXEC_SUMMARY_RUBRIC_DIMENSION_IDS,
    build_x1d_dimension_matrix,
    ensure_dimension_verdicts,
    infer_dimension_verdicts_from_judge_blob,
    write_x1d_dimension_matrix_artifact,
)
from apps_rg.runtime.sections.executive_summary_judge_remediation import (
    build_judge_remediation_user_message,
)


def _all_pass_gates() -> dict[str, dict[str, bool]]:
    return {
        "x2_exec_summary_sentence_count_6": {"pass": True, "detail": "ok"},
        "x2_exec_summary_evidence_utilization": {"pass": True, "detail": "ok"},
        "x2_exec_summary_no_credential_dump": {"pass": True, "detail": "ok"},
    }


def test_infer_dimension_verdicts_from_claude_style_blob() -> None:
    body = {
        "pass": False,
        "score": 3.0,
        "findings": ["bullet stack", "weak domain alignment to insurance brokerage"],
        "quality_flags": ["bullet_stack_prose", "weak_domain_targeting"],
        "fail_reasons": ["Insufficient executive synthesis"],
    }
    verdicts = infer_dimension_verdicts_from_judge_blob(body, deterministic_gate_summary=_all_pass_gates())
    assert verdicts["deterministic_alignment"]["pass"] is True
    assert verdicts["executive_signal"]["pass"] is False
    assert verdicts["ats_alignment_without_keyword_stuffing"]["pass"] is False


def test_ensure_dimension_verdicts_validates_explicit_block() -> None:
    body = {
        "score_scale": "0_to_5",
        "score": 4.0,
        "threshold": 4.0,
        "pass": True,
        "decisive_failure": False,
        "findings": [],
        "cited_sentence_indexes": [],
        "remediation_suggestions": [],
        "dimension_verdicts": {
            dim: {"pass": True, "severity": "none", "codes": []}
            for dim in EXEC_SUMMARY_RUBRIC_DIMENSION_IDS
        },
    }
    out, inferred = ensure_dimension_verdicts(body, deterministic_gate_summary=_all_pass_gates())
    assert inferred is False
    assert len(out["dimension_verdicts"]) == 8


def test_make_model_backed_output_attaches_dimension_verdicts() -> None:
    body = {
        "score_scale": "0_to_5",
        "score": 3.0,
        "threshold": 4.0,
        "pass": False,
        "decisive_failure": False,
        "findings": ["weak synthesis narrative"],
        "cited_sentence_indexes": [1],
        "remediation_suggestions": [],
        "quality_flags": ["bullet_stack_prose"],
    }
    out = _make_model_backed_output(
        "anthropic_claude",
        "h",
        "m",
        dict(body),
        deterministic_gate_summary=_all_pass_gates(),
    )
    assert out.dimension_verdicts
    assert "synthesis_quality" in out.dimension_verdicts
    assert out.dimension_verdicts["deterministic_alignment"]["pass"] is True


def test_dimension_matrix_consensus_fail() -> None:
    judges = [
        {
            "evaluator_mode": "MODEL_BACKED",
            "provider_key": "gemini_pro",
            "provider_name": "Gemini",
            "pass": False,
            "dimension_verdicts": {
                "synthesis_quality": {"pass": False, "severity": "major", "codes": ["bullet_stack_prose"]},
                **{d: {"pass": True, "severity": "none", "codes": []} for d in EXEC_SUMMARY_RUBRIC_DIMENSION_IDS if d != "synthesis_quality"},
            },
        },
        {
            "evaluator_mode": "MODEL_BACKED",
            "provider_key": "anthropic_claude",
            "provider_name": "Claude",
            "pass": False,
            "dimension_verdicts": {
                "synthesis_quality": {"pass": False, "severity": "major", "codes": ["bullet_stack_prose"]},
                **{d: {"pass": True, "severity": "none", "codes": []} for d in EXEC_SUMMARY_RUBRIC_DIMENSION_IDS if d != "synthesis_quality"},
            },
        },
        {
            "evaluator_mode": "MODEL_BACKED",
            "provider_key": "openai_chatgpt",
            "provider_name": "OpenAI",
            "pass": True,
            "dimension_verdicts": {d: {"pass": True, "severity": "none", "codes": []} for d in EXEC_SUMMARY_RUBRIC_DIMENSION_IDS},
        },
    ]
    matrix = build_x1d_dimension_matrix(judges)
    assert matrix["by_dimension"]["synthesis_quality"]["consensus_fail"] is True
    assert matrix["by_dimension"]["synthesis_quality"]["fail_count"] == 2


def test_write_matrix_artifact(tmp_path) -> None:
    judges = [
        {
            "evaluator_mode": "MODEL_BACKED",
            "provider_key": "openai_chatgpt",
            "pass": True,
            "dimension_verdicts": {d: {"pass": True, "severity": "none", "codes": []} for d in EXEC_SUMMARY_RUBRIC_DIMENSION_IDS},
        },
    ]
    path = write_x1d_dimension_matrix_artifact(tmp_path / "x1d_dimension_matrix.json", judges)
    body = json.loads(open(path, encoding="utf-8").read())
    assert body["schema"] == "executive_summary_x1d_dimension_matrix_v1"


def test_regen_message_includes_dimension_block() -> None:
    judges = [
        {
            "evaluator_mode": "MODEL_BACKED",
            "provider_key": "gemini_pro",
            "provider_name": "Gemini",
            "pass": False,
            "normalized_score": 0.6,
            "normalized_threshold": 0.8,
            "dimension_verdicts": {
                "synthesis_quality": {"pass": False, "severity": "major", "codes": ["bullet_stack_prose"]},
                **{d: {"pass": True, "severity": "none", "codes": []} for d in EXEC_SUMMARY_RUBRIC_DIMENSION_IDS if d != "synthesis_quality"},
            },
        },
    ]
    msg = build_judge_remediation_user_message(x1d_judges=judges, unused_fact_ids=[], allowed_fact_count=6)
    assert "DIMENSION_VERDICTS" in msg
    assert "synthesis_quality" in msg
