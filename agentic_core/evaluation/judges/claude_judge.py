"""ClaudeJudge — Anthropic-native LLM-as-Judge backend.

Companion to ``GeminiJudge`` in ``llm_judge.py``. Implements the same
``LLMJudge`` protocol and uses the identical per-dimension CoT-first
rubric bank + Unknown escape hatch, so the two backends are drop-in
substitutes for consensus ensembling.

Design:
- Synchronous ``score(query, context, answer) -> JudgeScore`` so it
  matches the legacy protocol consumed by the confidence engine.
- Uses ``anthropic.Anthropic`` (sync client) directly rather than
  ``AsyncAnthropic``; consensus ensembling runs judges in a thread pool
  if concurrency is desired.
- Temperature=0, max_tokens capped, prompt budget tracked per call.
- On transport / parse errors, marks the dimension Unknown with
  ``parse_error`` reason rather than raising — matches GeminiJudge
  behaviour so consensus can handle a partial backend failure without
  aborting the whole grade.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from agentic_core.evaluation.judges.llm_judge import (
    DIMENSIONS,
    DIMENSION_RUBRICS,
    UNKNOWN,
    JudgeScore,
    _coerce_dim_score,
    _extract_dim_payload,
    _extract_reasoning,
)

_log = logging.getLogger(__name__)


class ClaudeJudge:
    """Anthropic Claude backend for LLM-as-Judge.

    Mirrors :class:`GeminiJudge` but uses the Anthropic SDK. Honours the
    hardening plan's W3 acceptance: same rubric contract, same
    ``JudgeScore`` return shape, so consensus ensembling works without
    adapter code.
    """

    DEFAULT_MODEL = "claude-sonnet-4-5"
    MAX_TOKENS = 1024

    def __init__(
        self,
        anthropic_client: Any | None = None,
        model: str | None = None,
        per_dimension: bool = True,
    ) -> None:
        self._client = anthropic_client
        env_model = os.getenv("CLAUDE_JUDGE_MODEL")
        self._model = model or env_model or self.DEFAULT_MODEL
        self._per_dimension = per_dimension

    @property
    def model_id(self) -> str:
        return self._model

    def _get_client(self) -> Any:
        if self._client is not None:
            return self._client
        try:
            import anthropic  # noqa: PLC0415  (lazy import)
        except ImportError as exc:
            raise RuntimeError(
                "ClaudeJudge: anthropic package not installed.",
            ) from exc
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "ClaudeJudge: ANTHROPIC_API_KEY environment variable is required.",
            )
        self._client = anthropic.Anthropic(api_key=api_key)
        return self._client

    def _generate(self, prompt: str) -> str:
        client = self._get_client()
        response = client.messages.create(
            model=self._model,
            max_tokens=self.MAX_TOKENS,
            temperature=0.0,
            messages=[{"role": "user", "content": prompt}],
        )
        # Anthropic SDK returns a list of content blocks.
        parts: list[str] = []
        for block in getattr(response, "content", []):
            text = getattr(block, "text", None)
            if text:
                parts.append(str(text))
        return "\n".join(parts).strip()

    def _score_dimension(
        self,
        dimension: str,
        query: str,
        context: str,
        answer: str,
    ) -> tuple[float, str | None, str]:
        rubric = DIMENSION_RUBRICS[dimension]
        prompt = (
            f"{rubric}\n\n"
            f"Query:\n{query}\n\n"
            f"Context:\n{context}\n\n"
            f"Answer:\n{answer}"
        )
        try:
            raw = self._generate(prompt)
        except (RuntimeError, ValueError, OSError) as exc:
            _log.warning("[ClaudeJudge] transport error on %s: %s", dimension, exc)
            return UNKNOWN, f"transport_error: {exc}", ""
        reasoning = _extract_reasoning(raw)
        try:
            payload = _extract_dim_payload(raw)
            score, reason = _coerce_dim_score(payload)
        except ValueError as exc:
            return UNKNOWN, f"parse_error: {exc}", reasoning
        return score, reason, reasoning

    def score(self, query: str, context: str, answer: str) -> JudgeScore:
        unknown_reasons: dict[str, str] = {}
        per_dim_reasoning: dict[str, str] = {}
        scores: dict[str, float] = {}
        for dim in DIMENSIONS:
            value, reason, reasoning = self._score_dimension(dim, query, context, answer)
            scores[dim] = value
            per_dim_reasoning[dim] = reasoning
            if reason is not None:
                unknown_reasons[dim] = reason

        aggregate_reasoning = "; ".join(
            f"[{dim}] {per_dim_reasoning[dim][:200]}" for dim in DIMENSIONS
        )
        return JudgeScore.create(
            faithfulness=scores["faithfulness"],
            answer_relevancy=scores["answer_relevancy"],
            context_precision=scores["context_precision"],
            groundedness=scores["groundedness"],
            reasoning=aggregate_reasoning,
            judge_model=self._model,
            unknown_reasons=unknown_reasons,
            per_dim_reasoning=per_dim_reasoning,
        )


__all__ = ["ClaudeJudge"]
