"""Gemini judge shim for ``system_learning.confidence`` (LJH1.2).

Previously returned hardcoded 0.85 regardless of input. Now delegates to
the canonical ``agentic_core.evaluation.judges.llm_judge.GeminiJudge``
which fires one LLM call per dimension (LJH2.1) and honors the Unknown
escape hatch (LJH2.2).
"""

from __future__ import annotations

from typing import Any

from .llm_judge import LLMJudge as _ConfidenceJudge

__all__ = ["GeminiJudge", "GeminiE2EJudge", "score_with_gemini", "evaluate_e2e"]


class GeminiJudge:
    """Wrapper delegating to the canonical per-dim Gemini judge."""

    def __init__(self, model: str = "gemini-2.5-flash") -> None:
        self.model = model
        self._judge = _ConfidenceJudge(model=model)

    def score(self, output: str, criteria: dict[str, Any] | None = None) -> float:
        return self._judge.score(output, criteria)


class GeminiE2EJudge:
    """End-to-end Gemini judge (input/output pair)."""

    def __init__(self, model: str = "gemini-2.5-flash") -> None:
        self.model = model
        self._judge = _ConfidenceJudge(model=model)

    def evaluate(self, input_text: str, output_text: str) -> dict[str, Any]:
        return self._judge.evaluate(input_text, output_text)


def score_with_gemini(output: str, criteria: dict[str, Any] | None = None) -> float:
    return GeminiJudge().score(output, criteria)


def evaluate_e2e(input_text: str, output_text: str) -> dict[str, Any]:
    return GeminiE2EJudge().evaluate(input_text, output_text)
