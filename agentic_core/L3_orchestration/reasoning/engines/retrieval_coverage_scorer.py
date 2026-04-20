from __future__ import annotations

from dataclasses import dataclass
import math
import os
import statistics
import threading
import time
from typing import Any


@dataclass(frozen=True)
class RetrievalCoverageResult:
    advisory: bool
    evaluator_name: str
    evaluator_version: str
    coverage_score: float
    should_rerank: bool
    gap_signal: str
    latency_ms: float
    budget_status: str
    fallback_reason: str

    def __post_init__(self) -> None:
        if self.advisory is not True:
            raise ValueError("advisory must always be True")


class HeuristicCoverageScorer:
    evaluator_name = "heuristic_coverage_scorer"
    evaluator_version = "1.2.0"

    @staticmethod
    def _coerce_score(value: Any) -> float:
        try:
            score = float(value)
        except (TypeError, ValueError):
            return 0.0
        if not math.isfinite(score):
            return 0.0
        return max(0.0, min(1.0, score))

    @classmethod
    def _extract_score(cls, chunk: Any) -> float:
        if isinstance(chunk, (int, float)):
            return cls._coerce_score(chunk)
        if isinstance(chunk, dict):
            for key in ("combined_score", "score", "relevance_score", "similarity"):
                if key in chunk:
                    return cls._coerce_score(chunk.get(key))
            return 0.0
        for attr in ("combined_score", "score", "relevance_score", "similarity"):
            if hasattr(chunk, attr):
                return cls._coerce_score(getattr(chunk, attr, 0.0))
        return 0.0

    @classmethod
    def _scores(cls, chunks: list[Any]) -> list[float]:
        return [cls._extract_score(chunk) for chunk in chunks]

    @staticmethod
    def _gap_signal(scores: list[float], coverage: float) -> str:
        if not scores:
            return "empty"
        if all(score == 0.0 for score in scores):
            return "no_signal"
        if len(scores) > 1 and scores[0] - statistics.mean(scores[1:]) > 0.5:
            return "top_heavy"
        if coverage < 0.45:
            return "low_relevance"
        if len(scores) > 1 and statistics.pstdev(scores) < 0.05:
            return "low_sim_spread"
        return "ok"

    def score(self, chunks: list[Any]) -> RetrievalCoverageResult:
        started = time.perf_counter()
        if not chunks:
            return RetrievalCoverageResult(
                advisory=True,
                evaluator_name=self.evaluator_name,
                evaluator_version=self.evaluator_version,
                coverage_score=0.0,
                should_rerank=False,
                gap_signal="empty",
                latency_ms=(time.perf_counter() - started) * 1000.0,
                budget_status="ok",
                fallback_reason="",
            )

        scores = self._scores(chunks)
        coverage = self._coerce_score(sum(scores) / max(1, len(scores)))
        return RetrievalCoverageResult(
            advisory=True,
            evaluator_name=self.evaluator_name,
            evaluator_version=self.evaluator_version,
            coverage_score=coverage,
            should_rerank=coverage < 0.45,
            gap_signal=self._gap_signal(scores, coverage),
            latency_ms=(time.perf_counter() - started) * 1000.0,
            budget_status="ok",
            fallback_reason="",
        )


_SHADOW_BUFFER: list[RetrievalCoverageResult] = []
_SHADOW_BUFFER_LOCK = threading.Lock()


def _bounded_reason(reason: Any, limit: int = 240) -> str:
    text = "" if reason is None else str(reason).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def _append_shadow_result(result: RetrievalCoverageResult) -> None:
    with _SHADOW_BUFFER_LOCK:
        _SHADOW_BUFFER.append(result)


def drain_shadow_buffer() -> list[RetrievalCoverageResult]:
    with _SHADOW_BUFFER_LOCK:
        drained = list(_SHADOW_BUFFER)
        _SHADOW_BUFFER.clear()
    return drained


def get_coverage_scorer_mode() -> str:
    mode = os.environ.get("COVERAGE_SCORER_MODE", "shadow").strip().lower()
    return mode if mode in {"off", "shadow", "advisory_active"} else "shadow"


def _budget_ms() -> float:
    raw = os.environ.get("COVERAGE_SCORER_BUDGET_MS", "200")
    try:
        budget = float(raw)
    except (TypeError, ValueError):
        return 200.0
    if not math.isfinite(budget) or budget <= 0:
        return 200.0
    return budget


def score_coverage(
    chunks: list[Any], scorer: Any | None = None
) -> tuple[RetrievalCoverageResult | None, bool]:
    mode = get_coverage_scorer_mode()
    if mode == "off":
        return None, False

    scorer = scorer or HeuristicCoverageScorer()
    started = time.perf_counter()
    try:
        result = scorer.score(chunks)
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        budget_ms = _budget_ms()
        if elapsed_ms > budget_ms:
            fallback = RetrievalCoverageResult(
                advisory=True,
                evaluator_name=getattr(scorer, "evaluator_name", "unknown"),
                evaluator_version=getattr(scorer, "evaluator_version", "0"),
                coverage_score=0.0,
                should_rerank=False,
                gap_signal="budget_exceeded",
                latency_ms=elapsed_ms,
                budget_status="budget_exceeded",
                fallback_reason=f"coverage scoring exceeded {budget_ms:.0f} ms budget",
            )
            _append_shadow_result(fallback)
            return None, False
    except Exception as exc:  # guardian: allow-broad-exception -- coverage scoring boundary: fallback result returned on any error
        fallback = RetrievalCoverageResult(
            advisory=True,
            evaluator_name=getattr(scorer, "evaluator_name", "unknown"),
            evaluator_version=getattr(scorer, "evaluator_version", "0"),
            coverage_score=0.0,
            should_rerank=False,
            gap_signal="fallback",
            latency_ms=(time.perf_counter() - started) * 1000.0,
            budget_status="fallback",
            fallback_reason=_bounded_reason(exc),
        )
        _append_shadow_result(fallback)
        return None, False

    if mode == "shadow":
        _append_shadow_result(result)
        return result, False
    return result, bool(result.should_rerank)


__all__ = [
    "HeuristicCoverageScorer",
    "RetrievalCoverageResult",
    "drain_shadow_buffer",
    "get_coverage_scorer_mode",
    "score_coverage",
]
