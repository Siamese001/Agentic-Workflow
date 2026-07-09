"""Unit tests for apps_lic.policy.judge_base.

Covers the JudgeBase contractual surfaces:
  1. Rubric YAML schema validation (RubricLoadError on malformed input)
  2. JudgeScorecard shape (matches the reference doc's OUTPUT ARTIFACT spec)
  3. Score-band bucketing
  4. ABSTAIN-on-evaluate-raise (D6 — never propagate evaluate_fn exceptions)
  5. X3 disposition mapping via judge_disposition_policy.yaml (D3)
  6. ROUTER_DECISION marker emission (constitutional §29)

Plus integration tests on each shipped rubric:
  - judge_hop6_alignment.yaml (live rubric coverage via JudgeBase contract)
  - judge_hop1_classifier.yaml (W3-P1 deferred but rubric loadable)
  - judge_hop2_grounding.yaml  (W3-P2 deferred but rubric loadable)
  - judge_hop8_narrative.yaml  (W3-P3 deferred but rubric loadable)
"""
from __future__ import annotations

import logging
from pathlib import Path
from textwrap import dedent

import pytest

from apps_lic.policy.judge_base import (
    JudgeBase,
    JudgeScorecard,
    Rubric,
    RubricLoadError,
)

REPO_ROOT = Path(__file__).resolve().parents[5]
RUBRIC_DIR = REPO_ROOT / "apps_lic" / "policy" / "rubrics"
DISPOSITION_POLICY = REPO_ROOT / "apps_lic" / "policy" / "judge_disposition_policy.yaml"


# ---------------------------------------------------------------------- #
# Rubric schema validation
# ---------------------------------------------------------------------- #


def test_rubric_missing_file_raises(tmp_path):
    with pytest.raises(RubricLoadError, match="not found"):
        Rubric.load(tmp_path / "nope.yaml")


def test_rubric_missing_required_keys_raises(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("rubric_id: only\n")
    logging.info("C3 write receipt: malformed rubric fixture written")
    with pytest.raises(RubricLoadError, match="missing required"):
        Rubric.load(bad)


def test_rubric_empty_score_bands_raises(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        dedent(
            """
            rubric_id: r
            rubric_version: "1.0.0"
            judge_name: J
            score_bands: []
            """
        )
    )
    with pytest.raises(RubricLoadError, match="score_bands"):
        Rubric.load(bad)


def test_rubric_band_for_score_returns_highest_threshold():
    rubric = Rubric.load(RUBRIC_DIR / "judge_hop6_alignment.yaml")
    assert rubric.band_for_score(0.0) == "WEAK"
    assert rubric.band_for_score(0.30) == "MODERATE"
    assert rubric.band_for_score(0.55) == "STRONG"
    assert rubric.band_for_score(0.99) == "STRONG"


# ---------------------------------------------------------------------- #
# JudgeBase contractual behavior
# ---------------------------------------------------------------------- #


def _ok_evaluate(state, rubric):
    """Test-double evaluator: score = state['score']; no codes / refs."""
    return (state["score"], [], [], "")


def _failing_evaluate(state, rubric):
    raise RuntimeError("simulated evaluate failure")


@pytest.fixture
def alignment_judge():
    return JudgeBase(
        rubric_path=RUBRIC_DIR / "judge_hop6_alignment.yaml",
        evaluate_fn=_ok_evaluate,
    )


def test_scorecard_shape_matches_reference_spec(alignment_judge):
    sc = alignment_judge.judge({"score": 0.8}, emit_marker=False)
    # Reference doc OUTPUT ARTIFACT: judge_scorecard, gate_verdict
    # (=verdict), reason_codes[], evidence_refs[], confidence,
    # abstain_flag, remediation_hint, X3 disposition.
    assert isinstance(sc, JudgeScorecard)
    assert sc.judge_name == "HOP6_StrategicAlignment"
    assert sc.rubric_version == "1.0.0"
    assert 0.0 <= sc.score <= 1.0
    assert sc.verdict in {"PASS", "FAIL", "UNKNOWN"}
    assert sc.x3_disposition in {"ALLOW", "REVISE", "DENY", "HITL", "ABSTAIN"}
    assert isinstance(sc.reason_codes, tuple)
    assert isinstance(sc.evidence_refs, tuple)
    assert 0.0 <= sc.confidence <= 1.0
    assert isinstance(sc.abstain_flag, bool)
    assert isinstance(sc.remediation_hint, str)


def test_strong_score_routes_to_allow(alignment_judge):
    sc = alignment_judge.judge({"score": 0.95}, emit_marker=False)
    assert sc.x3_disposition == "ALLOW"
    assert sc.verdict == "PASS"
    assert sc.abstain_flag is False


def test_moderate_score_routes_to_revise(alignment_judge):
    sc = alignment_judge.judge({"score": 0.40}, emit_marker=False)
    assert sc.x3_disposition == "REVISE"


def test_weak_score_on_hop6_routes_to_deny(alignment_judge):
    sc = alignment_judge.judge({"score": 0.05}, emit_marker=False)
    # judge_disposition_policy.yaml: weak_band_hop6_strategic_alignment → DENY
    assert sc.x3_disposition == "DENY"
    assert sc.verdict == "FAIL"


def test_evaluate_raise_returns_abstain_scorecard(tmp_path):
    """D6: evaluate_fn raise must convert to ABSTAIN, never propagate."""
    judge = JudgeBase(
        rubric_path=RUBRIC_DIR / "judge_hop6_alignment.yaml",
        evaluate_fn=_failing_evaluate,
    )
    sc = judge.judge({"score": 0.99}, emit_marker=False)
    assert sc.x3_disposition == "ABSTAIN"
    assert sc.abstain_flag is True
    assert sc.verdict == "UNKNOWN"
    assert "evaluate_fn_raised" in sc.reason_codes
    assert "simulated evaluate failure" in sc.remediation_hint


def test_score_clamped_to_unit_range(alignment_judge):
    sc_high = alignment_judge.judge({"score": 1.5}, emit_marker=False)
    assert sc_high.score == 1.0
    sc_low = alignment_judge.judge({"score": -0.5}, emit_marker=False)
    assert sc_low.score == 0.0


def test_judge_rejects_non_dict_state(alignment_judge):
    with pytest.raises(TypeError, match="state must be dict"):
        alignment_judge.judge("nope", emit_marker=False)  # type: ignore[arg-type]


def test_to_dict_round_trip(alignment_judge):
    sc = alignment_judge.judge({"score": 0.8}, emit_marker=False)
    d = sc.to_dict()
    assert set(d.keys()) >= {
        "judge_name",
        "rubric_version",
        "score",
        "verdict",
        "x3_disposition",
        "reason_codes",
        "evidence_refs",
        "confidence",
        "abstain_flag",
        "remediation_hint",
        "backend",
    }
    assert isinstance(d["reason_codes"], list)
    assert isinstance(d["evidence_refs"], list)


# ---------------------------------------------------------------------- #
# ROUTER_DECISION marker emission (§29)
# ---------------------------------------------------------------------- #


def test_router_decision_marker_emitted_via_disposition_policy(alignment_judge, capsys):
    alignment_judge.judge({"score": 0.95}, emit_marker=True)
    captured = capsys.readouterr().out
    assert "ROUTER_DECISION:" in captured
    assert "router=judge_dispositions" in captured


def test_marker_suppressed_when_emit_marker_false(alignment_judge, capsys):
    alignment_judge.judge({"score": 0.95}, emit_marker=False)
    captured = capsys.readouterr().out
    assert "ROUTER_DECISION:" not in captured


# ---------------------------------------------------------------------- #
# All four shipped rubrics load
# ---------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "rubric_filename, expected_judge_name",
    [
        ("judge_hop6_alignment.yaml", "HOP6_StrategicAlignment"),
        ("judge_hop1_classifier.yaml", "HOP1_LLMFallbackClassifier"),
        ("judge_hop2_grounding.yaml", "HOP2_StrategicBriefFaithfulness"),
        ("judge_hop8_narrative.yaml", "HOP8_ExecutiveSummary"),
    ],
)
def test_all_shipped_rubrics_load(rubric_filename, expected_judge_name):
    rubric = Rubric.load(RUBRIC_DIR / rubric_filename)
    assert rubric.judge_name == expected_judge_name
    assert rubric.rubric_version == "1.0.0"
    # Bands must be sortable + non-empty.
    assert len(rubric.score_bands) >= 2
    # Each rubric must declare its deterministic-backend params.
    assert isinstance(rubric.params, dict)

