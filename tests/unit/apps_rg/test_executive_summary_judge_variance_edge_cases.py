"""Edge-case coverage for dual-panel judge score variance receipts."""

from __future__ import annotations

from pathlib import Path

from apps_rg.runtime.sections.executive_summary_judge_variance import (
    build_judge_score_variance_receipt,
    emit_judge_score_variance_if_dual_panel,
)


def test_coerce_score_from_normalized_score() -> None:
    prior = [
        {
            "provider_key": "gemini",
            "evaluator_mode": "MODEL_BACKED",
            "normalized_score": 0.9,
            "judge_packet_hash": "pkt1",
        },
    ]
    refreshed = [
        {
            "provider_key": "gemini",
            "evaluator_mode": "MODEL_BACKED",
            "normalized_score": 0.84,
            "judge_packet_hash": "pkt1",
        },
    ]
    receipt = build_judge_score_variance_receipt(
        prior_judges=prior,
        refreshed_judges=refreshed,
        judge_packet_hash="pkt1",
    )
    assert len(receipt["comparisons"]) == 1
    assert receipt["comparisons"][0]["score_before"] == 4.5
    assert receipt["comparisons"][0]["score_after"] == 4.2


def test_skips_provider_blocked_and_non_model_backed() -> None:
    prior = [
        {
            "provider_key": "gemini",
            "evaluator_mode": "MODEL_BACKED",
            "score": 4.5,
            "judge_packet_hash": "pkt1",
        },
        {
            "provider_key": "openai",
            "evaluator_mode": "MODEL_BACKED",
            "provider_blocked": True,
            "score": 4.0,
            "judge_packet_hash": "pkt1",
        },
        {
            "provider_key": "mock",
            "evaluator_mode": "HEURISTIC",
            "score": 5.0,
            "judge_packet_hash": "pkt1",
        },
    ]
    refreshed = [
        {
            "provider_key": "gemini",
            "evaluator_mode": "MODEL_BACKED",
            "score": 4.5,
            "judge_packet_hash": "pkt1",
        },
        {
            "provider_key": "openai",
            "evaluator_mode": "MODEL_BACKED",
            "provider_blocked": True,
            "score": 3.0,
            "judge_packet_hash": "pkt1",
        },
    ]
    receipt = build_judge_score_variance_receipt(
        prior_judges=prior,
        refreshed_judges=refreshed,
        judge_packet_hash="pkt1",
    )
    assert len(receipt["comparisons"]) == 1
    assert receipt["comparisons"][0]["provider_key"] == "gemini"
    assert receipt["any_variance_flagged"] is False


def test_hash_mismatch_excludes_comparison() -> None:
    prior = [
        {
            "provider_key": "gemini",
            "evaluator_mode": "MODEL_BACKED",
            "score": 4.5,
            "judge_packet_hash": "other_hash",
        },
    ]
    refreshed = [
        {
            "provider_key": "gemini",
            "evaluator_mode": "MODEL_BACKED",
            "score": 3.0,
            "judge_packet_hash": "pkt1",
        },
    ]
    receipt = build_judge_score_variance_receipt(
        prior_judges=prior,
        refreshed_judges=refreshed,
        judge_packet_hash="pkt1",
    )
    assert receipt["comparisons"] == []
    assert receipt["any_variance_flagged"] is False


def test_emit_returns_none_without_prior_panel(tmp_path: Path) -> None:
    assert (
        emit_judge_score_variance_if_dual_panel(
            artifact_dir=tmp_path,
            prior_judges=[],
            refreshed_judges=[
                {
                    "provider_key": "gemini",
                    "evaluator_mode": "MODEL_BACKED",
                    "score": 4.0,
                    "judge_packet_hash": "pkt1",
                },
            ],
            judge_packet_hash="pkt1",
        )
        is None
    )


def test_emit_returns_none_when_no_comparable_providers(tmp_path: Path) -> None:
    assert (
        emit_judge_score_variance_if_dual_panel(
            artifact_dir=tmp_path,
            prior_judges=[
                {
                    "provider_key": "gemini",
                    "evaluator_mode": "MODEL_BACKED",
                    "score": 4.5,
                    "judge_packet_hash": "wrong",
                },
            ],
            refreshed_judges=[
                {
                    "provider_key": "openai",
                    "evaluator_mode": "MODEL_BACKED",
                    "score": 4.0,
                    "judge_packet_hash": "pkt1",
                },
            ],
            judge_packet_hash="pkt1",
        )
        is None
    )
