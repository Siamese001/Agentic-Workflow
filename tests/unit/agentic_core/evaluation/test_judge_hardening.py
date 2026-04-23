"""LJH hardening smoke tests — bias, schema, stability, ensemble (LJH2.3 + friends).

Covers the cross-cutting concerns the hardening plan prescribes without
requiring any live LLM provider. Designed to run in <2s on CI.
"""

from __future__ import annotations

import math
from typing import Any

import pytest

from agentic_core.evaluation.judges.llm_judge import (
    DIMENSIONS,
    UNKNOWN,
    JudgeScore,
    NullJudge,
    _is_nan,
)
from agentic_core.evaluation.judges.consensus import ConsensusJudge
from agentic_core.evaluation.judges.schema import (
    JudgeResponseError,
    validate_dim_response,
)
# Import directly from the stability module (metrics/__init__.py has
# unrelated pre-existing import errors that would shadow this).
import importlib
_stability = importlib.import_module("agentic_core.evaluation.metrics.stability")
StabilityReport = _stability.StabilityReport
pass_at_k = _stability.pass_at_k
pass_hat_k = _stability.pass_hat_k


# ---------------------------------------------------------------------------
# LJH2.2 — Unknown escape hatch
# ---------------------------------------------------------------------------


def _mk_score(**overrides: Any) -> JudgeScore:
    kwargs: dict[str, Any] = {
        "faithfulness": 3.0,
        "answer_relevancy": 3.0,
        "context_precision": 3.0,
        "groundedness": 3.0,
        "reasoning": "test",
        "judge_model": "test-model",
    }
    kwargs.update(overrides)
    return JudgeScore.create(**kwargs)


def test_unknown_dimension_is_nan() -> None:
    score = _mk_score(faithfulness=UNKNOWN, unknown_reasons={"faithfulness": "insufficient"})
    assert score.is_unknown("faithfulness")
    assert not score.is_unknown("answer_relevancy")
    assert "faithfulness" in dict(score.unknown_reasons)


def test_all_unknown_gives_unknown_rate_one() -> None:
    score = _mk_score(
        faithfulness=UNKNOWN,
        answer_relevancy=UNKNOWN,
        context_precision=UNKNOWN,
        groundedness=UNKNOWN,
        unknown_reasons={d: "abstain" for d in DIMENSIONS},
    )
    assert score.unknown_rate() == 1.0
    assert score.known_dimensions() == {}


# ---------------------------------------------------------------------------
# LJH1.3 — Pydantic schema validation
# ---------------------------------------------------------------------------


def test_schema_accepts_valid_score() -> None:
    parsed = validate_dim_response({"score": 4, "unknown_reason": None})
    assert parsed["score"] == 4
    assert parsed["unknown_reason"] is None


def test_schema_accepts_unknown_sentinel() -> None:
    parsed = validate_dim_response({"score": "Unknown", "unknown_reason": "no context"})
    assert parsed["score"] == "Unknown"
    assert parsed["unknown_reason"] == "no context"


def test_schema_rejects_out_of_range() -> None:
    with pytest.raises(JudgeResponseError):
        validate_dim_response({"score": 7})


def test_schema_rejects_non_numeric() -> None:
    with pytest.raises(JudgeResponseError):
        validate_dim_response({"score": "maybe"})


# ---------------------------------------------------------------------------
# LJH5.1 — pass@k / pass^k
# ---------------------------------------------------------------------------


def test_pass_at_k_all_success() -> None:
    assert pass_at_k(n=10, c=10, k=1) == 1.0
    assert pass_at_k(n=10, c=10, k=5) == 1.0


def test_pass_at_k_no_success() -> None:
    assert pass_at_k(n=10, c=0, k=1) == 0.0
    assert pass_at_k(n=10, c=0, k=5) == 0.0


def test_pass_at_k_partial() -> None:
    # 5/10 success, k=1 -> 0.5 exact
    assert math.isclose(pass_at_k(n=10, c=5, k=1), 0.5)
    # Higher k raises pass@k (more shots on goal)
    assert pass_at_k(n=10, c=5, k=3) > pass_at_k(n=10, c=5, k=1)


def test_pass_hat_k_falls_with_k() -> None:
    # 75% per-trial success -> pass^3 = 0.75**3 ~ 0.422
    assert math.isclose(pass_hat_k(n=4, c=3, k=3), 0.75 ** 3, rel_tol=1e-9)
    # pass^k is monotonically non-increasing in k
    assert pass_hat_k(n=4, c=3, k=1) >= pass_hat_k(n=4, c=3, k=5)


def test_stability_report_from_results() -> None:
    results = [True, True, False, True, False, True, True]
    report = StabilityReport.from_results(results, k_values=(1, 3))
    assert report.n == 7
    assert report.c == 5
    assert math.isclose(report.pass_rate, 5 / 7)
    assert len(report.pass_at_k_values) == 2
    assert len(report.pass_hat_k_values) == 2


def test_pass_at_k_rejects_bad_args() -> None:
    with pytest.raises(ValueError):
        pass_at_k(n=5, c=10, k=1)  # c > n
    with pytest.raises(ValueError):
        pass_at_k(n=5, c=2, k=0)  # k < 1


# ---------------------------------------------------------------------------
# LJH2.3 — Bias battery (plumbing checks using NullJudge)
# ---------------------------------------------------------------------------


def test_nulljudge_is_deterministic() -> None:
    """Position swap must not change NullJudge output."""
    j = NullJudge()
    s1 = j.score("q", "c", "a")
    s2 = j.score("a", "c", "q")  # swap query and answer
    assert s1.faithfulness == s2.faithfulness
    assert s1.deterministic_digest == s2.deterministic_digest


def test_nulljudge_invariant_to_length_inflation() -> None:
    """Verbose answers should not alter NullJudge score (stub baseline)."""
    j = NullJudge()
    s_short = j.score("q", "c", "yes")
    s_long = j.score("q", "c", "yes. " * 200)
    assert s_short.faithfulness == s_long.faithfulness


# ---------------------------------------------------------------------------
# LJH3.2 — ConsensusJudge variance surfacing (uses stub judges)
# ---------------------------------------------------------------------------


class _FixedJudge:
    """Test double that returns a pre-computed JudgeScore."""

    def __init__(self, scores: dict[str, float], judge_model: str = "fixed") -> None:
        self._scores = scores
        self._judge_model = judge_model

    def score(self, query: str, context: str, answer: str) -> JudgeScore:  # noqa: ARG002
        return JudgeScore.create(
            faithfulness=self._scores["faithfulness"],
            answer_relevancy=self._scores["answer_relevancy"],
            context_precision=self._scores["context_precision"],
            groundedness=self._scores["groundedness"],
            reasoning="fixed",
            judge_model=self._judge_model,
        )


def test_consensus_median_on_three_judges() -> None:
    """Three judges, trimmed mean drops min+max."""
    j1 = _FixedJudge({d: 1.0 for d in DIMENSIONS}, "j1")
    j2 = _FixedJudge({d: 3.0 for d in DIMENSIONS}, "j2")
    j3 = _FixedJudge({d: 5.0 for d in DIMENSIONS}, "j3")
    consensus = ConsensusJudge([j1, j2, j3])
    result = consensus.grade("q", "c", "a")
    # trimmed-mean of {1,3,5} -> 3.0 exactly
    assert math.isclose(result.score.faithfulness, 3.0)


def test_consensus_unknown_propagates_when_all_abstain() -> None:
    j1 = _FixedJudge({d: UNKNOWN for d in DIMENSIONS}, "j1")
    j2 = _FixedJudge({d: UNKNOWN for d in DIMENSIONS}, "j2")
    consensus = ConsensusJudge([j1, j2])
    result = consensus.grade("q", "c", "a")
    for d in DIMENSIONS:
        assert _is_nan(getattr(result.score, d))
