"""LLM judge shim for ``system_learning.confidence`` (LJH1.1 + LJH1.2).

This module previously returned a hardcoded ``{"score": 0.80, "passed": True}``
regardless of input — an unacceptable deception for a confidence pipeline.
It is now a thin shim that delegates to the canonical judge in
``agentic_core.evaluation.judges.llm_judge`` and FAILS FAST when no
provider is available, rather than fabricating scores.
"""

from __future__ import annotations

from typing import Any

from agentic_core.evaluation.judges.llm_judge import (
    DIMENSIONS,
    UNKNOWN,
    GeminiJudge,
    JudgeScore,
    LLMJudge as _LLMJudgeProtocol,
    NullJudge,
    _is_nan,
)

__all__ = ["LLMJudge", "evaluate", "score_output"]


class LLMJudge:
    """Confidence-layer wrapper that delegates to the canonical judge.

    Conforms to ``agentic_core.evaluation.judges.llm_judge.LLMJudge``
    Protocol indirectly via the underlying ``GeminiJudge`` / ``NullJudge``.
    """

    def __init__(
        self,
        model: str | None = None,
        *,
        underlying: _LLMJudgeProtocol | None = None,
    ) -> None:
        self.model = model or "default"
        if underlying is not None:
            self._judge: _LLMJudgeProtocol = underlying
        else:
            # Prefer real provider; fall back to NullJudge only when explicitly
            # requested (tests). Raising on missing provider is the point.
            try:
                self._judge = GeminiJudge(model=model)
            except RuntimeError:
                # Provider unavailable — explicit fail-fast on use, not here.
                self._judge = GeminiJudge(model=model)

    @staticmethod
    def _aggregate(score: JudgeScore) -> tuple[float, dict[str, Any]]:
        """Reduce a per-dimension ``JudgeScore`` to a [0,1] confidence value."""
        known = {d: getattr(score, d) for d in DIMENSIONS if not _is_nan(getattr(score, d))}
        if not known:
            return 0.0, {
                "passed": False,
                "reason": "all_dimensions_unknown",
                "unknown_reasons": list(score.unknown_reasons),
            }
        avg_1_5 = sum(known.values()) / len(known)
        # Rescale 1-5 -> 0-1
        confidence = max(0.0, min(1.0, (avg_1_5 - 1.0) / 4.0))
        return confidence, {
            "passed": confidence >= 0.6,
            "reason": "scored",
            "dimensions_scored": list(known.keys()),
            "unknown_count": len(DIMENSIONS) - len(known),
            "judge_model": score.judge_model,
            "deterministic_digest": score.deterministic_digest,
        }

    def evaluate(self, prompt: str, response: str) -> dict[str, Any]:
        """Evaluate prompt/response pair using the canonical judge.

        The ``prompt`` is treated as ``query`` and ``response`` as ``answer``
        with no external context — this is a degraded mode; callers with
        retrieval context should use ``agentic_core...GeminiJudge.score``
        directly and pass ``context``.
        """
        score = self._judge.score(prompt, "", response)
        confidence, meta = self._aggregate(score)
        return {
            "score": confidence,
            "passed": meta["passed"],
            "feedback": score.reasoning or meta["reason"],
            "criteria_met": len(DIMENSIONS) - meta.get("unknown_count", len(DIMENSIONS)),
            "metadata": meta,
        }

    def score(self, output: str, criteria: dict[str, Any] | None = None) -> float:
        """Score ``output`` as a confidence value in [0,1]."""
        _ = criteria  # reserved for future per-dim weighting
        score = self._judge.score("", "", output)
        confidence, _meta = self._aggregate(score)
        return confidence


def evaluate(prompt: str, response: str) -> dict[str, Any]:
    """Module-level convenience — delegates to ``LLMJudge().evaluate``."""
    return LLMJudge().evaluate(prompt, response)


def score_output(output: str, criteria: dict[str, Any] | None = None) -> float:
    """Module-level convenience — delegates to ``LLMJudge().score``."""
    return LLMJudge().score(output, criteria)


# Re-export for tests and downstream compatibility.
__all__ += ["DIMENSIONS", "NullJudge", "UNKNOWN"]
