"""W3 — immutable candidate pool + best-of publish ranking."""

from __future__ import annotations

from typing import Any

from apps_rg.runtime.sections.executive_summary_candidate_pool import (
    CandidatePool,
    finalize_pool_publish,
    freeze_candidate_snapshot,
    publish_rank_metrics,
    select_best_publish_candidate,
)


def _model_judge(pk: str, score: float, *, major_fails: int = 0) -> dict[str, Any]:
    dims = {
        "factual_support": "PASS",
        "executive_signal": "PASS",
        "resume_voice": "PASS",
        "ats_alignment_without_keyword_stuffing": "PASS",
        "anti_overfit": "PASS",
        "synthesis_quality": "PASS",
        "evidence_utilization": "PASS",
        "deterministic_alignment": "PASS",
    }
    for i in range(major_fails):
        dims[list(dims.keys())[i]] = "FAIL"
    return {
        "provider_key": pk,
        "evaluator_mode": "MODEL_BACKED",
        "score": score,
        "dimension_verdicts": dims,
    }


def _minimal_snapshot(
    candidate_id: str,
    *,
    resume: str = "Line one. Line two. Line three. Line four. Line five. Line six.",
    publish_eligible: bool = True,
) -> Any:
    parsed = {
        "resume_display_text": resume,
        "claim_ledger": [
            {
                "claim_id": "c1",
                "claim_text": "40% growth",
                "source_fact_ids": ["f1"],
            },
        ],
    }
    x2 = [{"gate_id": "x2_test", "pass": True}]
    x1d = [_model_judge("claude", 4.0), _model_judge("openai", 4.0)]
    return freeze_candidate_snapshot(
        candidate_id=candidate_id,
        raw_output='{"resume_display_text": "x"}',
        parsed=parsed,
        resume_display_text=resume,
        claim_ledger=list(parsed["claim_ledger"]),
        x2_gates=x2,
        x1d_judges=x1d,
        allowed_fact_ids={"f1"},
        prompt_hash="abc123",
        model_name="retired_provider-test",
        publish_eligible=publish_eligible,
        scores_freshness="soft_failed_only",
    )


def test_freeze_snapshot_digest_stable() -> None:
    a = _minimal_snapshot("scratch")
    b = _minimal_snapshot("scratch")
    assert a.candidate_digest == b.candidate_digest
    assert len(a.candidate_digest) == 64


def test_publish_rank_metrics_min_holistic() -> None:
    judges = [_model_judge("claude", 4.0), _model_judge("openai", 3.5)]
    min_s, sum_s, major = publish_rank_metrics(judges)
    assert min_s == 3.5
    assert sum_s == 7.5
    assert major == 0


def test_select_best_prefers_higher_min_score() -> None:
    scratch = _minimal_snapshot("scratch")
    regen = _minimal_snapshot("regen_cycle_1", resume="Regen prose. " * 6)
    ranked = [
        (scratch, [_model_judge("claude", 4.0), _model_judge("openai", 4.0)]),
        (regen, [_model_judge("claude", 4.5), _model_judge("openai", 4.2)]),
    ]
    winner, _, receipt = select_best_publish_candidate(ranked)
    assert winner.candidate_id == "regen_cycle_1"
    assert receipt["rank_comparison"]


def test_select_best_tie_prefers_scratch() -> None:
    scratch = _minimal_snapshot("scratch")
    regen = _minimal_snapshot("regen_cycle_1", resume="Regen prose. " * 6)
    judges = [_model_judge("claude", 4.0), _model_judge("openai", 4.0)]
    ranked = [(scratch, judges), (regen, list(judges))]
    winner, _, _ = select_best_publish_candidate(ranked)
    assert winner.candidate_id == "scratch"


def test_parse_ok_x2_pass_alone_not_pool_eligible_without_g3() -> None:
    """X2/parse path without G3 accept must not add regen to publish pool."""
    pool = CandidatePool()
    pool.add(_minimal_snapshot("scratch", publish_eligible=True))
    regen = _minimal_snapshot("regen_cycle_1", publish_eligible=False)
    pool.add(regen)
    eligible = pool.publish_eligible()
    assert len(eligible) == 1
    assert eligible[0].candidate_id == "scratch"


def test_pool_only_scratch_when_regen_not_eligible() -> None:
    pool = CandidatePool()
    pool.add(_minimal_snapshot("scratch", publish_eligible=True))
    pool.add(_minimal_snapshot("regen_cycle_1", publish_eligible=False))
    assert [s.candidate_id for s in pool.publish_eligible()] == ["scratch"]


def test_w3_brown_070105_rank_publishes_scratch_not_regressed_regen() -> None:
    """Brown 4.2: Claude 4.0→3.6 regen must lose argmax to scratch (full-panel rank)."""
    import json
    from pathlib import Path

    fixture = (
        Path(__file__).resolve().parents[3]
        / "artifacts"
        / "apps_rg"
        / "runtime_proofs"
        / "executive_summary"
        / "real"
        / "exec_summary_20260526_070105"
        / "judge_remediation_cycles.json"
    )
    if not fixture.is_file():
        import pytest

        pytest.skip(f"fixture missing: {fixture}")
    cycle = json.loads(fixture.read_text(encoding="utf-8"))["cycles"][0]
    before = {r["provider_key"]: r for r in cycle["scores_before"]["providers"]}
    after = {r["provider_key"]: r for r in cycle["scores_after"]["providers"]}

    def _from_row(row: dict[str, Any]) -> dict[str, Any]:
        return {
            "provider_key": row["provider_key"],
            "evaluator_mode": "MODEL_BACKED",
            "score": row["score"],
            "normalized_score": row["normalized_score"],
            "pass": row["pass"],
        }

    scratch = _minimal_snapshot("scratch")
    regen = _minimal_snapshot("regen_cycle_1", resume="Regen from Brown. " * 6)
    ranked = [
        (scratch, [_from_row(before[pk]) for pk in before]),
        (regen, [_from_row(after[pk]) for pk in after]),
    ]
    winner, _, _ = select_best_publish_candidate(ranked)
    assert winner.candidate_id == "scratch"
    assert before["anthropic_claude"]["score"] == 4.0
    assert after["anthropic_claude"]["score"] == 3.6


def test_finalize_publish_rebinds_scratch_on_regress(tmp_path: Any) -> None:
    pool = CandidatePool()
    scratch_resume = "Scratch anchor. " * 6
    regen_resume = "Regen worse. " * 6
    pool.add(_minimal_snapshot("scratch", resume=scratch_resume, publish_eligible=True))
    pool.add(_minimal_snapshot("regen_cycle_1", resume=regen_resume, publish_eligible=True))

    def _rescore(snap: Any) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        if snap.candidate_id == "scratch":
            return (
                [_model_judge("claude", 4.0), _model_judge("openai", 4.0)],
                {"rescore_mode": "full_panel"},
            )
        return (
            [_model_judge("claude", 3.6), _model_judge("openai", 4.0)],
            {"rescore_mode": "full_panel"},
        )

    l2: dict[str, Any] = {}
    result = finalize_pool_publish(
        pool,
        artifact_dir=tmp_path,
        write_json_fn=lambda p, d: p.write_text(__import__("json").dumps(d), encoding="utf-8"),
        rescore_full_panel=_rescore,
        enrich_parsed_for_x2_fn=lambda parsed, **_: dict(parsed),
        build_coverage_fn=lambda _t, _l, _a: {"rows": []},
        allowed_fact_ids={"f1"},
        input_payload_hash="h",
        runtime_payload={},
        write_x2_fn=lambda _p, _g: None,
        write_x1d_fn=lambda _d, _j: None,
        l2_output=l2,
        scratch_anchor_resume=scratch_resume,
    )
    assert result.selected is not None
    assert result.selected.candidate_id == "scratch"
    assert scratch_resume.strip() in (tmp_path / "resume_display_text.txt").read_text(encoding="utf-8")
    integrity = __import__("json").loads(
        (tmp_path / "publish_integrity_receipt.json").read_text(encoding="utf-8"),
    )
    assert integrity["published_candidate_digest"] == integrity["final_artifact_digest_source"]
    assert integrity["publish_selected_snapshot_id"] == "scratch"

