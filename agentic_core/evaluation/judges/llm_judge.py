"""LLM-as-Judge evaluation harness.

Provides:
- ``JudgeScore``   — immutable score dataclass with deterministic digest
- ``LLMJudge``     — Protocol for all judge implementations
- ``NullJudge``    — Deterministic stub for CI (no LLM calls)
- ``GeminiJudge``  — Production judge via Gemini with structured rubric
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

_RUBRIC = '\nYou are an expert evaluator for RAG (Retrieval-Augmented Generation) systems.\nScore the following on a scale of 1-5 (integers only):\n\n- faithfulness: Is every claim in the answer supported by the provided context?\n  1=completely unsupported, 5=every claim fully grounded.\n- answer_relevancy: Does the answer directly and completely address the query?\n  1=off-topic, 5=directly addresses every part.\n- context_precision: Is the retrieved context relevant to answering the query?\n  1=irrelevant, 5=all context highly relevant.\n- groundedness: Are the factual claims in the answer grounded in the context?\n  1=hallucinated, 5=fully grounded.\n\nProvide a short reasoning (≤2 sentences).\n\nRespond ONLY with valid JSON:\n{"faithfulness": <1-5>, "answer_relevancy": <1-5>,\n "context_precision": <1-5>, "groundedness": <1-5>,\n "reasoning": "<text>"}\n'


@dataclass(frozen=True)
class JudgeScore:
    """Immutable score from an LLM judge."""

    faithfulness: float
    answer_relevancy: float
    context_precision: float
    groundedness: float
    reasoning: str
    judge_model: str
    deterministic_digest: str

    @classmethod
    def create(
        cls,
        faithfulness: float,
        answer_relevancy: float,
        context_precision: float,
        groundedness: float,
        reasoning: str,
        judge_model: str,
    ) -> JudgeScore:
        canonical = json.dumps(
            {
                "faithfulness": faithfulness,
                "answer_relevancy": answer_relevancy,
                "context_precision": context_precision,
                "groundedness": groundedness,
                "judge_model": judge_model,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        return cls(
            faithfulness=faithfulness,
            answer_relevancy=answer_relevancy,
            context_precision=context_precision,
            groundedness=groundedness,
            reasoning=reasoning,
            judge_model=judge_model,
            deterministic_digest=digest,
        )


@runtime_checkable
class LLMJudge(Protocol):
    """Protocol for all judge implementations."""

    def score(self, query: str, context: str, answer: str) -> JudgeScore: ...


class NullJudge:
    """Deterministic stub judge for CI — always returns fixed scores.

    Use in unit tests to avoid any LLM API calls.
    """

    FIXED_SCORE = 3.0

    def score(self, query: str, context: str, answer: str) -> JudgeScore:
        return JudgeScore.create(
            faithfulness=self.FIXED_SCORE,
            answer_relevancy=self.FIXED_SCORE,
            context_precision=self.FIXED_SCORE,
            groundedness=self.FIXED_SCORE,
            reasoning="NullJudge: deterministic stub",
            judge_model="null",
        )


class GeminiJudge:
    """Production judge via Gemini with structured rubric.

    Requires ``GEMINI_API_KEY`` or an injected ``gemini_client``.
    Temperature is forced to 0.0 for maximum determinism.
    Parse failures retry once after stripping markdown fences.
    """

    MODEL_ID = "gemini-1.5-flash"

    def __init__(self, gemini_client=None) -> None:
        self._client = gemini_client

    def _get_client(self):
        if self._client is not None:
            return self._client
        try:
            from agentic_core.L2_execution.enforcement.SovereignLLMGateway import get_llm_gateway

            return get_llm_gateway()
        except Exception as exc:
            raise RuntimeError("GeminiJudge: no LLM client available") from exc

    @staticmethod
    def _clean(raw: str) -> str:
        return re.sub("```(?:json)?|```", "", raw).strip()

    @staticmethod
    def _parse(raw: str) -> dict:
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return json.loads(GeminiJudge._clean(raw))

    def score(self, query: str, context: str, answer: str) -> JudgeScore:
        prompt = f"{_RUBRIC}\n\nQuery: {query}\n\nContext:\n{context}\n\nAnswer:\n{answer}"
        client = self._get_client()
        raw = client.generate(prompt=prompt, temperature=0.0)
        data = self._parse(raw)
        return JudgeScore.create(
            faithfulness=float(data.get("faithfulness", 1)),
            answer_relevancy=float(data.get("answer_relevancy", 1)),
            context_precision=float(data.get("context_precision", 1)),
            groundedness=float(data.get("groundedness", 1)),
            reasoning=str(data.get("reasoning", "")),
            judge_model=self.MODEL_ID,
        )


__all__ = ["JudgeScore", "LLMJudge", "NullJudge", "GeminiJudge"]
