"""Retrieval Coverage Scorer — advisory-only C5 coverage signal.

MVP-1: Heuristic scorer only (no ML model).  A pluggable ``RetrievalCoverageScorer``
protocol allows a learned model to be swapped in later without touching the caller.

Architecture invariants (enforced by tests):
  - ``RetrievalCoverageResult.advisory`` is **always** True.
  - Scorer output never reaches X1C / X2 hard-gate logic.
  - Fail-closed: any exception or budget overrun returns a fallback result;
    callers fall back to the existing evidence pipeline unchanged.
  - ``COVERAGE_SCORER_MODE=off`` → scorer not called; no telemetry emitted.
  - ``COVERAGE_SCORER_MODE=shadow`` → score + capture; rerank NOT triggered.
  - ``COVERAGE_SCORER_MODE=advisory_active`` → score + capture + rerank trigger.

No L4 writes.  Shadow captures go to an in-memory ring buffer only.
"""

from __future__ import annotations

import collections
import logging
import math
import os
import time
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

_log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

_COVERAGE_SCORER_MODE_ENV = "COVERAGE_SCORER_MODE"
_COVERAGE_SCORER_BUDGET_MS_ENV = "COVERAGE_SCORER_BUDGET_MS"
_VALID_MODES = frozenset({"off", "shadow", "advisory_active"})
_RERANK_THRESHOLD = 0.45  # coverage_score below this triggers should_rerank=True
_EVALUATOR_VERSION = "0.1.0-heuristic"  # bump when scorer logic changes; drives C1 replay digest


def get_coverage_scorer_mode() -> str:
    """Return the active scorer mode.

    Reads ``COVERAGE_SCORER_MODE`` env var.
    Values: ``'off'`` | ``'shadow'`` | ``'advisory_active'``.  Default: ``'shadow'``.
    """
    raw = os.getenv(_COVERAGE_SCORER_MODE_ENV, "shadow").lower().strip()
    return raw if raw in _VALID_MODES else "shadow"


def get_coverage_scorer_budget_ms() -> float:
    """Return the max allowed wall-clock ms for a scorer call.  Default: 50.0."""
    try:
        return float(os.getenv(_COVERAGE_SCORER_BUDGET_MS_ENV, "50"))
    except ValueError:
        return 50.0


# ---------------------------------------------------------------------------
# Result contract
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RetrievalCoverageResult:
    """Advisory-only output of the coverage scorer.

    ``advisory`` is always ``True``.  Downstream code MUST NOT gate on this
    score in any hard-gate logic path (X1C, X2, UWG).
    """

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
        if not self.advisory:
            raise ValueError("RetrievalCoverageResult.advisory must always be True")


def _fallback_result(
    evaluator_name: str,
    evaluator_version: str,
    latency_ms: float,
    budget_status: str,
    reason: str,
) -> RetrievalCoverageResult:
    return RetrievalCoverageResult(
        advisory=True,
        evaluator_name=evaluator_name,
        evaluator_version=evaluator_version,
        coverage_score=0.0,
        should_rerank=False,
        gap_signal="",
        latency_ms=latency_ms,
        budget_status=budget_status,
        fallback_reason=reason,
    )


# ---------------------------------------------------------------------------
# Protocol
# ---------------------------------------------------------------------------


@runtime_checkable
class RetrievalCoverageScorer(Protocol):
    """Pluggable scorer interface.  MVP is ``HeuristicCoverageScorer``.
    A learned cross-encoder or classifier can implement this protocol later.
    """

    evaluator_name: str
    evaluator_version: str

    def score(self, chunks: list[Any]) -> RetrievalCoverageResult:
        """Score coverage of *chunks*.

        Args:
            chunks: list of objects with a numeric ``combined_score`` attribute
                    (``HybridSearchResult`` or anything duck-typing it).

        Returns:
            ``RetrievalCoverageResult`` — always advisory.
        """


# ---------------------------------------------------------------------------
# Heuristic scorer (MVP — no ML model)
# ---------------------------------------------------------------------------


class HeuristicCoverageScorer:
    """Signal-based coverage scorer.  No model dependency.

    Computes coverage from the distribution of ``combined_score`` values across
    the retrieved chunks.  Signals:

    * ``mean_score`` — average relevance
    * ``score_spread`` — std dev; low spread + low mean = top-heavy retrieval
    * ``above_threshold_ratio`` — fraction of chunks above a relevance floor
    * ``gap_signal`` — text label summarising the dominant failure mode

    This is intentionally simple: the purpose is to start collecting shadow
    telemetry and prove the insertion point before a trained model is added.
    """

    evaluator_name: str = "heuristic_coverage_scorer"
    evaluator_version: str = _EVALUATOR_VERSION

    _RELEVANCE_FLOOR: float = 0.4
    _ADEQUATE_RATIO: float = 0.5

    def score(self, chunks: list[Any]) -> RetrievalCoverageResult:
        t0 = time.perf_counter()

        if not chunks:
            latency_ms = (time.perf_counter() - t0) * 1000
            return RetrievalCoverageResult(
                advisory=True,
                evaluator_name=self.evaluator_name,
                evaluator_version=self.evaluator_version,
                coverage_score=0.0,
                should_rerank=False,
                gap_signal="empty",
                latency_ms=round(latency_ms, 3),
                budget_status="ok",
                fallback_reason="",
            )

        scores = [float(getattr(c, "combined_score", getattr(c, "score", 0.0))) for c in chunks]
        n = len(scores)
        mean = sum(scores) / n
        variance = sum((s - mean) ** 2 for s in scores) / n
        std = math.sqrt(variance)
        above = sum(1 for s in scores if s >= self._RELEVANCE_FLOOR) / n

        # Composite coverage score
        coverage = min(1.0, max(0.0, (mean * 0.5) + (above * 0.4) + (min(std, 0.25) / 0.25 * 0.1)))

        should_rerank = coverage < _RERANK_THRESHOLD

        # Gap signal
        if n == 0 or mean < 0.2:
            gap = "low_relevance"
        elif above < 0.3:
            gap = "top_heavy"
        elif std < 0.05 and mean < 0.5:
            gap = "low_sim_spread"
        else:
            gap = "ok"

        latency_ms = (time.perf_counter() - t0) * 1000
        return RetrievalCoverageResult(
            advisory=True,
            evaluator_name=self.evaluator_name,
            evaluator_version=self.evaluator_version,
            coverage_score=round(coverage, 4),
            should_rerank=should_rerank,
            gap_signal=gap,
            latency_ms=round(latency_ms, 3),
            budget_status="ok",
            fallback_reason="",
        )


# ---------------------------------------------------------------------------
# Shadow training capture buffer (in-memory, no L4 writes)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ShadowTrainingCapture:
    """Telemetry record for future training data.

    Written to ``_SHADOW_BUFFER`` ring buffer.  Drained by
    ``ShadowEvaluationRunner``.  Never written to L4 or UWG directly.
    """

    run_id: str
    query_id: str
    chunk_ids: tuple[str, ...]
    sim_mean: float
    sim_std: float
    sim_min: float
    sim_max: float
    coverage_score: float
    should_rerank: bool
    rerank_triggered: bool
    gap_signal: str
    evaluator_version: str
    latency_ms: float
    budget_status: str
    fallback_reason: str
    x1d_groundedness_hook: float
    captured_at_utc: float


_SHADOW_BUFFER: collections.deque[ShadowTrainingCapture] = collections.deque(maxlen=100)


def drain_shadow_buffer() -> list[ShadowTrainingCapture]:
    """Drain and return all captures from the ring buffer."""
    items = list(_SHADOW_BUFFER)
    _SHADOW_BUFFER.clear()
    return items


def _emit_shadow_capture(
    bundle_chunks: list[Any],
    result: RetrievalCoverageResult,
    rerank_triggered: bool,
    run_id: str = "",
    query_id: str = "",
) -> None:
    chunk_ids = tuple(getattr(c, "chunk_id", "") for c in bundle_chunks)
    scores = [float(getattr(c, "combined_score", getattr(c, "score", 0.0))) for c in bundle_chunks]
    n = len(scores)
    sim_mean = sum(scores) / n if n else 0.0
    variance = sum((s - sim_mean) ** 2 for s in scores) / n if n else 0.0
    sim_std = math.sqrt(variance)
    sim_min = min(scores) if scores else 0.0
    sim_max = max(scores) if scores else 0.0

    _SHADOW_BUFFER.append(
        ShadowTrainingCapture(
            run_id=run_id,
            query_id=query_id,
            chunk_ids=chunk_ids,
            sim_mean=round(sim_mean, 4),
            sim_std=round(sim_std, 4),
            sim_min=round(sim_min, 4),
            sim_max=round(sim_max, 4),
            coverage_score=result.coverage_score,
            should_rerank=result.should_rerank,
            rerank_triggered=rerank_triggered,
            gap_signal=result.gap_signal,
            evaluator_version=result.evaluator_version,
            latency_ms=result.latency_ms,
            budget_status=result.budget_status,
            fallback_reason=result.fallback_reason,
            x1d_groundedness_hook=-1.0,
            captured_at_utc=time.time(),
        )
    )


# ---------------------------------------------------------------------------
# Top-level safe scorer call
# ---------------------------------------------------------------------------

_DEFAULT_SCORER = HeuristicCoverageScorer()


def score_coverage(
    chunks: list[Any],
    scorer: RetrievalCoverageScorer | None = None,
    run_id: str = "",
    query_id: str = "",
) -> tuple[RetrievalCoverageResult | None, bool]:
    """Score coverage of *chunks* and optionally emit shadow capture.

    Wraps the scorer call with:
    - mode gate (returns ``None`` when mode is ``"off"``)
    - budget enforcement
    - exception isolation (fail-closed)
    - shadow telemetry capture when mode is ``"shadow"`` or ``"advisory_active"``

    Args:
        chunks: retrieved chunks (must have ``combined_score`` or ``score`` attr)
        scorer: scorer instance; defaults to ``HeuristicCoverageScorer``
        run_id: opaque run identifier for shadow capture
        query_id: originating query identifier for shadow capture

    Returns:
        Tuple ``(result_or_none, rerank_triggered)``.
        ``result_or_none`` is ``None`` when mode is ``"off"`` or on hard fallback.
        ``rerank_triggered`` is ``True`` only when mode is ``"advisory_active"``
        and ``result.should_rerank`` is ``True``.
    """
    mode = get_coverage_scorer_mode()
    if mode == "off":
        return None, False

    active_scorer = scorer or _DEFAULT_SCORER
    budget_ms = get_coverage_scorer_budget_ms()
    t0 = time.perf_counter()

    try:
        result = active_scorer.score(chunks)
        elapsed = (time.perf_counter() - t0) * 1000

        if elapsed > budget_ms:
            fallback = _fallback_result(
                active_scorer.evaluator_name,
                active_scorer.evaluator_version,
                elapsed,
                "budget_exceeded",
                f"scorer exceeded {budget_ms:.0f}ms budget (actual={elapsed:.1f}ms)",
            )
            _log.warning(
                "coverage_scorer budget_exceeded latency_ms=%.1f budget_ms=%.0f",
                elapsed,
                budget_ms,
            )
            _emit_shadow_capture(chunks, fallback, False, run_id, query_id)
            return None, False

    except Exception as exc:  # guardian: allow-broad-exception -- intentional scorer isolation; all exceptions logged and converted to fallback
        elapsed = (time.perf_counter() - t0) * 1000
        fallback = _fallback_result(
            active_scorer.evaluator_name,
            active_scorer.evaluator_version,
            elapsed,
            "fallback",
            str(exc),
        )
        _log.warning("coverage_scorer exception fallback: %s", exc)
        _emit_shadow_capture(chunks, fallback, False, run_id, query_id)
        return None, False

    rerank_triggered = mode == "advisory_active" and result.should_rerank
    _emit_shadow_capture(chunks, result, rerank_triggered, run_id, query_id)

    return result, rerank_triggered


# ---------------------------------------------------------------------------
# Runtime E1 bind — mirrors wire_shadow_mode_scorer() in artifact_loader.py
# ---------------------------------------------------------------------------


def wire_coverage_scorer_to_envelope(
    envelope_builder: Any,
    *,
    evaluator_version: str = _EVALUATOR_VERSION,
) -> None:
    """Bind the coverage scorer version hash into a replay envelope at E1.

    Call once at run startup, after the ``EnvelopeBuilder`` has been created and
    before any scoring happens.  This ensures the C1 determinism digest reflects
    the exact scorer artifact used during the run.

    No-op when:
      - ``envelope_builder`` is ``None``
      - ``COVERAGE_SCORER_MODE=off``

    The ``envelope_builder`` is typed ``Any`` to avoid a hard import cycle; at
    runtime it must be an ``EnvelopeBuilder`` instance (duck-typing: it must
    implement ``with_coverage_scorer(evaluator_version: str)``).

    Advisory-only: binds the scorer version for replay fidelity only; never
    gates allow / deny / escalate / commit decisions.
    """
    if envelope_builder is None:
        return
    mode = get_coverage_scorer_mode()
    if mode == "off":
        return
    envelope_builder.with_coverage_scorer(evaluator_version)
