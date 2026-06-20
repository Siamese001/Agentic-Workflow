"""OpenAIJudge — per-dimension LLM-as-Judge via OpenAI Responses API (LJH3.1).

Mirrors the structure of :class:`agentic_core.evaluation.judges.codex_judge.ClaudeJudge`:
one LLM call per dimension, ``temperature=0`` for determinism, JSON-mode
response format, Unknown escape hatch honored, provider errors surface
as Unknown on the affected dimension (never a guessed numeric score).

Used in :class:`agentic_core.evaluation.judges.consensus.ConsensusJudge`
alongside :class:`GeminiJudge` and :class:`ClaudeJudge` to mitigate the
self-preference bias that single-family graders exhibit on own-family
outputs (MT-Bench, Patronus guidance).
"""

from __future__ import annotations

from agentic_core.config.model_catalog import (
    OPENAI_GPT4O_MINI_MODEL_ID,
)

import importlib
import logging
import os
from typing import Any

from agentic_core.evaluation.judges.llm_judge import (
    DIMENSION_RUBRICS,
    DIMENSIONS,
    UNKNOWN,
    JudgeScore,
    _coerce_dim_score,
    _extract_dim_payload,
    _extract_reasoning,
)

_log = logging.getLogger(__name__)

__all__ = ["OpenAIJudge"]


class OpenAIJudge:
    """Per-dimension judge backed by OpenAI's ``openai`` SDK.

    Requires ``OPENAI_API_KEY``. Model override via ``OPENAI_MODEL`` env
    var. ``temperature=0.0`` and ``response_format={"type": "json_object"}``
    for structured output.
    """

    DEFAULT_MODEL = OPENAI_GPT4O_MINI_MODEL_ID

    def __init__(self, openai_client: Any = None, model: str | None = None) -> None:
        self._client = openai_client
        env_model = os.getenv("OPENAI_MODEL")
        self._model = model or env_model or self.DEFAULT_MODEL

    @property
    def model_id(self) -> str:
        return self._model

    def _get_client(self) -> Any:
        if self._client is not None:
            return self._client
        try:
            openai_mod = importlib.import_module("openai")
        except ImportError as exc:
            raise RuntimeError("OpenAIJudge: openai SDK not installed") from exc
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OpenAIJudge: OPENAI_API_KEY missing")
        self._client = openai_mod.OpenAI(api_key=api_key)
        return self._client

    def _generate(self, prompt: str) -> str:
        client = self._get_client()
        completion = client.chat.completions.create(
            model=self._model,
            temperature=0.0,
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}],
        )
        return completion.choices[0].message.content or ""

    def _score_dimension(
        self,
        dimension: str,
        query: str,
        context: str,
        answer: str,
    ) -> tuple[float, str | None, str]:
        rubric = DIMENSION_RUBRICS[dimension]
        prompt = f"{rubric}\n\nQuery: {query}\n\nContext:\n{context}\n\nAnswer:\n{answer}"
        try:
            raw = self._generate(prompt)
        except (RuntimeError, ValueError) as exc:
            return UNKNOWN, f"provider_error: {exc}", ""
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

        aggregate_reasoning = "; ".join(f"[{dim}] {per_dim_reasoning[dim][:200]}" for dim in DIMENSIONS)
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
