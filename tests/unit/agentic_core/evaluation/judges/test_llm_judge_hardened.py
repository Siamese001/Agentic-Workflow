"""Unit tests for the hardened LLM-as-Judge implementation.

Covers the W2-W5 deliverables from plan
``llm-as-judge-hardening-anthropic-e7b1a4``:
- Per-dimension CoT-first scoring via GeminiJudge with a stub client.
- Unknown escape hatch and NaN semantics.
- Parse-error → Unknown fallback.
- Consensus aggregation (trimmed-mean) + disagreement flags.
- Pairwise position-swap bias mitigation.
- Reference-based grading.
- Cohen's kappa and Krippendorff's alpha.
- Drift monitor thresholds.
"""

from __future__ import annotations

import math
from typing import Iterator

import pytest

from agentic_core.evaluation.judges.calibration import (
    cohens_kappa,
    krippendorffs_alpha,
)
from agentic_core.evaluation.judges.consensus import (
    ConsensusJudge,
    DEFAULT_DISAGREEMENT_THRESHOLD,
)
from agentic_core.evaluation.judges.llm_judge import (
    DIMENSIONS,
    GeminiJudge,
    JudgeScore,
    NullJudge,
    _is_nan,
)
from agentic_core.evaluation.judges.pairwise_reference import (
    PairwiseJudge,
    ReferenceJudge,
)
from agentic_core.L6_observability.judge_drift import analyze_drift


# ---------------------------------------------------------------------------
# Stub Gemini client. ``generate_content`` returns responses from a scripted
# queue so tests can exercise both valid-score and malformed response paths.
# ---------------------------------------------------------------------------


class _FakeResponse:
    def __init__(self, text: str) -> None:
        self.text = text


class _StubGeminiClient:
    def __init__(self, responses: list[str]) -> None:
        self._iter: Iterator[str] = iter(responses)

    def generate_content(self, prompt: str, generation_config: dict) -> _FakeResponse:
        try:
            text = next(self._iter)
        except StopIteration:
            text = '{"score": 3}'
        # sanity: temperature is zero per hardening plan
        assert generation_config.get("temperature") == 0.0
        return _FakeResponse(text)


def _dim_response(score: int | str, reasoning: str = "stub") -> str:
    if isinstance(score, str):
        return (
            f"<reasoning>{reasoning}</reasoning>\n"
            f'{{"score": "{score}", "unknown_reason": "insufficient context"}}'
        )
    return (
        f"<reasoning>{reasoning}</reasoning>\n"
        f'{{"score": {score}, "unknown_reason": null}}'
    )


# ---------------------------------------------------------------------------
# NullJudge sanity
# ---------------------------------------------------------------------------


def test_null_judge_is_deterministic() -> None:
    judge = NullJudge()
    a = judge.score("q", "ctx", "ans")
    b = judge.score("q", "ctx", "ans")
    assert a.deterministic_digest == b.deterministic_digest
    assert a.faithfulness == 3.0
    assert a.unknown_rate() == 0.0


# ---------------------------------------------------------------------------
# Per-dimension scoring + Unknown semantics
# ---------------------------------------------------------------------------


def test_gemini_judge_per_dimension_scoring() -> None:
    client = _StubGeminiClient(
        [
            _dim_response(5, "faithful"),
            _dim_response(4, "relevant"),
            _dim_response(5, "precise"),
            _dim_response(5, "grounded"),
        ],
    )
    judge = GeminiJudge(gemini_client=client)
    score = judge.score("q", "ctx", "ans")
    assert score.faithfulness == 5.0
    assert score.answer_relevancy == 4.0
    assert score.context_precision == 5.0
    assert score.groundedness == 5.0
    assert score.unknown_rate() == 0.0
    # Reasoning is captured but aggregated into the human-readable field.
    per_dim_map = dict(score.per_dim_reasoning)
    for dim in DIMENSIONS:
        assert per_dim_map[dim].startswith(("faithful", "relevant", "precise", "grounded"))


def test_gemini_judge_unknown_escape_hatch() -> None:
    client = _StubGeminiClient(
        [
            _dim_response("Unknown", "not enough context"),
            _dim_response(4),
            _dim_response(5),
            _dim_response("Unknown", "ambiguous"),
        ],
    )
    judge = GeminiJudge(gemini_client=client)
    score = judge.score("q", "ctx", "ans")
    assert score.is_unknown("faithfulness")
    assert not score.is_unknown("answer_relevancy")
    assert score.is_unknown("groundedness")
    assert score.unknown_rate() == 0.5
    reasons = dict(score.unknown_reasons)
    assert "insufficient context" in reasons["faithfulness"]


def test_gemini_judge_parse_error_becomes_unknown() -> None:
    # First dimension response is malformed; should degrade to Unknown,
    # remaining dimensions should still score normally.
    client = _StubGeminiClient(
        [
            "<reasoning>broken</reasoning>\n{not json}",
            _dim_response(4),
            _dim_response(5),
            _dim_response(3),
        ],
    )
    judge = GeminiJudge(gemini_client=client)
    score = judge.score("q", "ctx", "ans")
    assert score.is_unknown("faithfulness")
    reasons = dict(score.unknown_reasons)
    assert "parse_error" in reasons["faithfulness"]
    assert score.answer_relevancy == 4.0


def test_judge_score_digest_excludes_reasoning() -> None:
    a = JudgeScore.create(
        faithfulness=5.0,
        answer_relevancy=5.0,
        context_precision=5.0,
        groundedness=5.0,
        reasoning="first reasoning",
        judge_model="m",
    )
    b = JudgeScore.create(
        faithfulness=5.0,
        answer_relevancy=5.0,
        context_precision=5.0,
        groundedness=5.0,
        reasoning="completely different reasoning",
        judge_model="m",
    )
    # Anthropic recommendation: reasoning is stored-and-audited, not fed
    # into the score-identity hash.
    assert a.deterministic_digest == b.deterministic_digest


def test_judge_score_digest_stable_with_unknown() -> None:
    a = JudgeScore.create(
        faithfulness=float("nan"),
        answer_relevancy=4.0,
        context_precision=5.0,
        groundedness=float("nan"),
        reasoning="x",
        judge_model="m",
        unknown_reasons={"faithfulness": "r1", "groundedness": "r2"},
    )
    b = JudgeScore.create(
        faithfulness=float("nan"),
        answer_relevancy=4.0,
        context_precision=5.0,
        groundedness=float("nan"),
        reasoning="x",
        judge_model="m",
        unknown_reasons={"faithfulness": "r1", "groundedness": "r2"},
    )
    assert a.deterministic_digest == b.deterministic_digest
    assert _is_nan(a.faithfulness)


# ---------------------------------------------------------------------------
# Consensus aggregation
# ---------------------------------------------------------------------------


class _FixedJudge:
    """Stub that returns a hand-crafted JudgeScore irrespective of inputs."""

    def __init__(self, score: JudgeScore) -> None:
        self._score = score

    def score(self, query: str, context: str, answer: str) -> JudgeScore:
        return self._score


def _score(
    f: float, r: float, p: float, g: float, model: str = "stub",
    unknown_reasons: dict[str, str] | None = None,
) -> JudgeScore:
    return JudgeScore.create(
        faithfulness=f,
        answer_relevancy=r,
        context_precision=p,
        groundedness=g,
        reasoning=f"stub-{model}",
        judge_model=model,
        unknown_reasons=unknown_reasons,
    )


def test_consensus_trimmed_mean_with_three_judges() -> None:
    consensus = ConsensusJudge(
        [
            _FixedJudge(_score(5, 5, 5, 5, "a")),
            _FixedJudge(_score(3, 3, 3, 3, "b")),
            _FixedJudge(_score(1, 1, 1, 1, "c")),
        ],
    )
    result = consensus.grade("q", "c", "a")
    # min=1 and max=5 are trimmed → mean of [3] = 3.0 per dimension.
    assert result.score.faithfulness == 3.0
    assert result.score.answer_relevancy == 3.0
    assert result.score.context_precision == 3.0
    assert result.score.groundedness == 3.0
    assert len(result.per_judge) == 3


def test_consensus_flags_disagreement() -> None:
    consensus = ConsensusJudge(
        [
            _FixedJudge(_score(5, 4, 4, 4, "a")),
            _FixedJudge(_score(1, 4, 4, 4, "b")),  # large range on faithfulness
        ],
        disagreement_threshold=DEFAULT_DISAGREEMENT_THRESHOLD,
    )
    result = consensus.grade("q", "c", "a")
    assert "faithfulness" in result.flagged_dimensions
    disagreement_map = dict(result.disagreements)
    assert disagreement_map["faithfulness"] == 4.0
    assert disagreement_map["answer_relevancy"] == 0.0


def test_consensus_returns_unknown_when_all_judges_abstain() -> None:
    consensus = ConsensusJudge(
        [
            _FixedJudge(
                _score(float("nan"), 4, 4, 4, "a",
                       unknown_reasons={"faithfulness": "no ctx"})
            ),
            _FixedJudge(
                _score(float("nan"), 4, 4, 4, "b",
                       unknown_reasons={"faithfulness": "parse_error"})
            ),
        ],
    )
    result = consensus.grade("q", "c", "a")
    assert result.score.is_unknown("faithfulness")
    reasons = dict(result.score.unknown_reasons)
    assert "no ctx" in reasons["faithfulness"]
    assert "parse_error" in reasons["faithfulness"]


def test_consensus_rejects_empty_judge_list() -> None:
    with pytest.raises(ValueError):
        ConsensusJudge([])


# ---------------------------------------------------------------------------
# Pairwise position-swap bias mitigation
# ---------------------------------------------------------------------------


def _pairwise_response(winner: str, confidence: float = 0.9) -> str:
    return (
        f"<reasoning>stub</reasoning>\n"
        f'{{"winner": "{winner}", "confidence": {confidence}, "unknown_reason": null}}'
    )


def test_pairwise_swap_agrees() -> None:
    responses = [
        _pairwise_response("A", 0.9),
        _pairwise_response("B", 0.9),  # swapped: expected flip A→B
    ]
    idx = {"i": 0}

    def generate(prompt: str) -> str:
        out = responses[idx["i"]]
        idx["i"] += 1
        return out

    judge = PairwiseJudge(generate=generate, judge_model="stub")
    verdict = judge.compare("q", "c", "answer_a", "answer_b")
    assert verdict.winner == "A"
    assert verdict.position_swap_applied
    assert verdict.position_swap_agreed is True


def test_pairwise_position_bias_detected() -> None:
    # Judge picks A both times → reveals position bias, degrade to TIE.
    responses = [
        _pairwise_response("A", 0.9),
        _pairwise_response("A", 0.9),
    ]
    idx = {"i": 0}

    def generate(prompt: str) -> str:
        out = responses[idx["i"]]
        idx["i"] += 1
        return out

    judge = PairwiseJudge(generate=generate, judge_model="stub")
    verdict = judge.compare("q", "c", "answer_a", "answer_b")
    assert verdict.winner == "TIE"
    assert verdict.position_swap_agreed is False
    assert "position bias" in verdict.reasoning


def test_pairwise_skips_swap_on_tie() -> None:
    def generate(prompt: str) -> str:
        return _pairwise_response("TIE", 0.5)

    judge = PairwiseJudge(generate=generate, judge_model="stub")
    verdict = judge.compare("q", "c", "answer_a", "answer_b")
    assert verdict.winner == "TIE"
    assert verdict.position_swap_applied is False


# ---------------------------------------------------------------------------
# Reference-based grading
# ---------------------------------------------------------------------------


def test_reference_judge_all_dimensions() -> None:
    def generate(prompt: str) -> str:
        return (
            "<reasoning>stub</reasoning>\n"
            '{"factual_equivalence": 5, "coverage": 4, '
            '"no_extraneous_claims": "Unknown", '
            '"unknown_reasons": {"no_extraneous_claims": "too short"}}'
        )

    judge = ReferenceJudge(generate=generate, judge_model="stub")
    verdict = judge.grade("q", "c", "candidate", "reference")
    assert verdict.scores["factual_equivalence"] == 5.0
    assert verdict.scores["coverage"] == 4.0
    assert math.isnan(verdict.scores["no_extraneous_claims"])
    assert "too short" in verdict.unknown_reasons["no_extraneous_claims"]


# ---------------------------------------------------------------------------
# Calibration (Cohen's kappa + Krippendorff's alpha)
# ---------------------------------------------------------------------------


def test_cohens_kappa_perfect_agreement_is_one() -> None:
    a = [1, 2, 3, 4, 5]
    b = [1, 2, 3, 4, 5]
    assert cohens_kappa(a, b) == 1.0


def test_cohens_kappa_ignores_unknown_pairs() -> None:
    a = [1, 2, 3, 4, 5, "Unknown"]
    b = [1, 2, 3, 4, 5, 5]
    assert cohens_kappa(a, b) == 1.0


def test_krippendorffs_alpha_perfect_rows() -> None:
    # All ratings identical per row → alpha == 1.0
    rows = [[1, 1], [3, 3], [5, 5]]
    assert krippendorffs_alpha(rows) == 1.0


def test_krippendorffs_alpha_handles_missing() -> None:
    rows = [[1, 1], [5, None], [3, 3]]
    # Row with a missing rater is filtered, remaining rows are perfect.
    assert krippendorffs_alpha(rows) == 1.0


# ---------------------------------------------------------------------------
# Drift monitor
# ---------------------------------------------------------------------------


def test_drift_monitor_kappa_below_floor_raises_event() -> None:
    current = {
        "n_items": 50,
        "dimension_kappa": {"faithfulness": 0.40},
        "dimension_alpha": {"faithfulness": 0.50},
        "unknown_rate_by_dim": {"faithfulness": 0.10},
    }
    report = analyze_drift(
        current,
        unknown_budgets={"faithfulness": 0.20},
        judge_id="gemini",
    )
    kinds = {e.kind for e in report.events}
    assert "kappa_below_floor" in kinds
    assert "alpha_below_floor" in kinds
    assert report.has_drift


def test_drift_monitor_unknown_over_budget() -> None:
    current = {
        "n_items": 50,
        "dimension_kappa": {"faithfulness": 0.80},
        "dimension_alpha": {"faithfulness": 0.80},
        "unknown_rate_by_dim": {"faithfulness": 0.50},
    }
    report = analyze_drift(
        current,
        unknown_budgets={"faithfulness": 0.20},
        judge_id="gemini",
    )
    assert any(e.kind == "unknown_over_budget" for e in report.events)
    assert report.worst_severity in {"MEDIUM", "HIGH"}


def test_drift_monitor_kappa_regression() -> None:
    current = {
        "n_items": 50,
        "dimension_kappa": {"faithfulness": 0.70},
        "dimension_alpha": {"faithfulness": 0.70},
        "unknown_rate_by_dim": {"faithfulness": 0.05},
    }
    previous = {
        "n_items": 50,
        "dimension_kappa": {"faithfulness": 0.88},
        "dimension_alpha": {"faithfulness": 0.88},
        "unknown_rate_by_dim": {"faithfulness": 0.05},
    }
    report = analyze_drift(current, previous=previous, judge_id="gemini")
    assert any(e.kind == "kappa_regression" for e in report.events)
