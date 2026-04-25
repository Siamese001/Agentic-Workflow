"""Retrieval-scoped reflexion loop — ADR-060 implementation.

The loop wraps a single-pass retriever with grade → decide → expand →
re-retrieve, capped at 3 iterations and a wall-clock budget. Layer-scoped to
L1: the executor here MAY NOT import from L3 per the boundary rules in W4.2.

The CRAG paper grades retrieved chunks per-pass. This implementation
preserves that shape with a tiered decision rule:

    * If ≥ ``k_min`` chunks are RELEVANT and 0 ABORT signals → converged.
    * If at least one is RELEVANT or AMBIGUOUS → expand (rewrite/hop/swap)
      and re-retrieve, up to ``max_iters``.
    * If all IRRELEVANT for two consecutive iterations → abstain.

The retriever itself is injected as a callable so the loop is testable
without ChromaDB / vLLM. The orchestrator (`rag_orchestrator.py`) is the
production caller; tests use stub callables.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable

from agentic_core.runtime.types.reflection_types import (
    L1_RETRIEVAL_ACTIONS,
    ReflectionNextAction,
    ReflectionTrace,
    ReflectionVerdict,
)

from .retrieval_grader import (
    Chunk,
    GradeVerdict,
    GradeVerdictKind,
    RetrievalGrader,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Configuration + result types
# ---------------------------------------------------------------------------


@dataclass
class ReflectiveLoopConfig:
    """Bounded-loop knobs. All defaults match ADR-060 §1."""

    max_iters: int = 3
    """Hard cap on retrieval passes within a single query."""

    iter_budget_ms: int = 800
    """Wall-clock budget per iteration. Breach forces stop with `cap`."""

    total_budget_ms: int = 3000
    """Wall-clock budget across all iterations."""

    relevant_k_min: int = 3
    """Min RELEVANT chunks needed to declare ``converged``."""

    consecutive_irrelevant_to_abort: int = 2
    """Two consecutive all-irrelevant passes → abstain."""

    def __post_init__(self) -> None:
        if self.max_iters < 1:
            raise ValueError("max_iters must be >= 1")
        if self.iter_budget_ms <= 0 or self.total_budget_ms <= 0:
            raise ValueError("budgets must be positive")
        if self.relevant_k_min < 1:
            raise ValueError("relevant_k_min must be >= 1")


@dataclass
class ReflectiveLoopResult:
    """Output of a reflective loop run."""

    final_chunks: list[Chunk]
    final_verdicts: list[GradeVerdict]
    iterations: int
    outcome: str  # one of agentic_core.L6_observability.semconv.rag.OUTCOME_*
    evidence_quality: str  # strong | weak | none
    traces: list[ReflectionTrace] = field(default_factory=list)
    last_query: str = ""

    @property
    def abstained(self) -> bool:
        from agentic_core.L6_observability.semconv import (
            rag as semconv,
        )  # guardian: allow-layer-violation -- imports semconv CONSTANTS (OUTCOME_*) only, not code; L1 trace attribute names must match L6 emitter contract verbatim, otherwise dashboards and queries break

        return self.outcome == semconv.OUTCOME_ABSTAINED


# ---------------------------------------------------------------------------
# Retriever / expander callables (injected)
# ---------------------------------------------------------------------------


RetrieverFn = Callable[[str], list[Chunk]]
"""``query -> list[Chunk]``. Must be deterministic for a fixed corpus snapshot."""

ExpanderFn = Callable[[str, list[GradeVerdict]], tuple[str, ReflectionNextAction]]
"""``(query, verdicts) -> (rewritten_query, action)``.

The expander chooses an action from ``L1_RETRIEVAL_ACTIONS`` based on the
verdict distribution. Implementations may consult ADR-058 transforms (HyDE,
step-back, decomposition, self-query) or graph hops; this module treats it
as a black box and only enforces that the returned action is L1-scoped.
"""


def _default_expander(query: str, verdicts: list[GradeVerdict]) -> tuple[str, ReflectionNextAction]:
    """Trivial built-in expander: append a clarifier and rewrite the query.

    Production code should inject a real expander (transform-aware). This
    default exists so the loop is functional in tests without wiring all of
    ADR-058's transform catalog.
    """

    if not verdicts:
        return query, ReflectionNextAction.REWRITE_QUERY
    relevant = sum(1 for v in verdicts if v.verdict == GradeVerdictKind.RELEVANT)
    if relevant > 0:
        # We had partial signal — keep the query; let the caller decide.
        return query, ReflectionNextAction.REWRITE_QUERY
    # All non-relevant — try a structural alternative.
    return f"{query} (rephrase: focus on definitions and concepts)", ReflectionNextAction.TRANSFORM_SWAP


# ---------------------------------------------------------------------------
# Loop
# ---------------------------------------------------------------------------


def _verdict_dist(verdicts: list[GradeVerdict]) -> dict[str, int]:
    return {kind.value: sum(1 for v in verdicts if v.verdict == kind) for kind in GradeVerdictKind}


def _decide(
    verdicts: list[GradeVerdict],
    *,
    relevant_k_min: int,
) -> tuple[ReflectionVerdict, ReflectionNextAction]:
    """Map a verdict distribution to an (overall verdict, next action) pair."""

    dist = _verdict_dist(verdicts)
    relevant = dist[GradeVerdictKind.RELEVANT.value]
    ambiguous = dist[GradeVerdictKind.AMBIGUOUS.value]
    irrelevant = dist[GradeVerdictKind.IRRELEVANT.value]

    if relevant >= relevant_k_min:
        return ReflectionVerdict.ACCEPT, ReflectionNextAction.ACCEPT_AS_IS
    if relevant > 0 or ambiguous > 0:
        return ReflectionVerdict.REVISE, ReflectionNextAction.REWRITE_QUERY
    if irrelevant > 0:
        return ReflectionVerdict.REVISE, ReflectionNextAction.TRANSFORM_SWAP
    # No verdicts at all — degenerate case.
    return ReflectionVerdict.ABORT, ReflectionNextAction.ABSTAIN


def run_reflective_retrieval(
    *,
    query: str,
    retriever: RetrieverFn,
    grader: RetrievalGrader,
    config: ReflectiveLoopConfig | None = None,
    expander: ExpanderFn | None = None,
) -> ReflectiveLoopResult:
    """Execute the bounded CRAG-style reflective loop.

    All callable injections must be free of side effects across iterations
    that the loop does not observe. Loop telemetry is emitted into the
    returned ``ReflectiveLoopResult.traces`` for caller-side OTel forwarding
    (the loop itself does not import OTel to keep it test-clean).
    """

    from agentic_core.L6_observability.semconv import rag as semconv  # noqa: PLC0415  # guardian: allow-layer-violation -- semconv constants only (OUTCOME_*, attribute keys); identical contract to the .abstained property at L92; L1 cannot inline-redefine these without drifting from the L6 emitter SSOT

    if not query.strip():
        raise ValueError("query must be non-empty")
    cfg = config or ReflectiveLoopConfig()
    expand = expander or _default_expander

    overall_start = time.monotonic()
    current_query = query
    consecutive_all_irrelevant = 0

    final_chunks: list[Chunk] = []
    final_verdicts: list[GradeVerdict] = []
    traces: list[ReflectionTrace] = []
    outcome: str = semconv.OUTCOME_CAP

    for iter_idx in range(cfg.max_iters):
        iter_start = time.monotonic()

        # Total budget check FIRST so we don't even start an iteration we
        # cannot finish.
        elapsed_total_ms = (iter_start - overall_start) * 1000
        if elapsed_total_ms >= cfg.total_budget_ms:
            outcome = semconv.OUTCOME_BUDGET_EXCEEDED
            traces.append(
                _trace(
                    iter_idx,
                    [],
                    ReflectionVerdict.ABORT,
                    f"total_budget exceeded ({elapsed_total_ms:.0f}ms)",
                    None,
                    grader,
                )
            )
            break

        # Retrieve.
        try:
            chunks = retriever(current_query)
        except (RuntimeError, ValueError) as exc:
            logger.warning("retriever raised in iter %d: %s", iter_idx, exc)
            outcome = semconv.OUTCOME_ERROR
            traces.append(
                _trace(
                    iter_idx,
                    [],
                    ReflectionVerdict.ABORT,
                    f"retriever_error: {exc}"[:240],
                    ReflectionNextAction.ABSTAIN,
                    grader,
                )
            )
            break

        # Grade.
        verdicts = grader.grade(current_query, chunks)
        final_chunks = chunks
        final_verdicts = verdicts

        # Iteration-budget check after the (potentially expensive) grade
        # call. Honors the per-iter SLO without aborting mid-grade.
        iter_elapsed_ms = (time.monotonic() - iter_start) * 1000
        budget_breached = iter_elapsed_ms >= cfg.iter_budget_ms

        verdict, next_action = _decide(verdicts, relevant_k_min=cfg.relevant_k_min)
        rationale = (
            f"dist={_verdict_dist(verdicts)} iter_ms={iter_elapsed_ms:.0f} budget_breach={budget_breached}"
        )[:240]
        traces.append(
            _trace(
                iter_idx,
                verdicts,
                verdict,
                rationale,
                next_action,
                grader,
            )
        )

        # Convergence.
        if verdict == ReflectionVerdict.ACCEPT:
            outcome = semconv.OUTCOME_CONVERGED
            break

        # Two consecutive all-irrelevant → abstain.
        dist = _verdict_dist(verdicts)
        if (
            dist[GradeVerdictKind.RELEVANT.value] == 0
            and dist[GradeVerdictKind.AMBIGUOUS.value] == 0
            and dist[GradeVerdictKind.IRRELEVANT.value] > 0
        ):
            consecutive_all_irrelevant += 1
        else:
            consecutive_all_irrelevant = 0
        if consecutive_all_irrelevant >= cfg.consecutive_irrelevant_to_abort:
            outcome = semconv.OUTCOME_ABSTAINED
            break

        # Budget breach this iter — stop without expansion.
        if budget_breached:
            outcome = semconv.OUTCOME_BUDGET_EXCEEDED
            break

        # Expand for next iteration.
        next_query, expand_action = expand(current_query, verdicts)
        if expand_action not in L1_RETRIEVAL_ACTIONS:
            raise RuntimeError(
                f"expander returned non-L1 action {expand_action!r}; "
                f"allowed: {sorted(a.value for a in L1_RETRIEVAL_ACTIONS)}"
            )
        if expand_action == ReflectionNextAction.ABSTAIN:
            outcome = semconv.OUTCOME_ABSTAINED
            break
        current_query = next_query

    iterations = len(traces)
    evidence_quality = _evidence_quality(outcome, final_verdicts)
    return ReflectiveLoopResult(
        final_chunks=final_chunks,
        final_verdicts=final_verdicts,
        iterations=iterations,
        outcome=outcome,
        evidence_quality=evidence_quality,
        traces=traces,
        last_query=current_query,
    )


def _trace(
    iter_idx: int,
    verdicts: list[GradeVerdict],
    verdict: ReflectionVerdict,
    rationale: str,
    next_action: ReflectionNextAction | None,
    grader: RetrievalGrader,
) -> ReflectionTrace:
    return ReflectionTrace(
        iteration=iter_idx,
        evidence_in=verdicts,
        verdict=verdict,
        rationale=rationale,
        next_action=next_action,
        grader_identity=grader.grader_identity,
        emitted_at=datetime.now(timezone.utc),
        extras={"verdict_dist": _verdict_dist(verdicts)} if verdicts else {},
    )


def _evidence_quality(
    outcome: str,
    verdicts: list[GradeVerdict],
) -> str:
    from agentic_core.L6_observability.semconv import rag as semconv  # noqa: PLC0415  # guardian: allow-layer-violation -- semconv constants only (EVIDENCE_*, OUTCOME_*); L1 evidence-quality summarisation must label outcomes with the same strings the L6 emitter uses for trace attributes — divergence here breaks downstream queries and dashboards

    if outcome == semconv.OUTCOME_ABSTAINED:
        return semconv.EVIDENCE_NONE
    if outcome == semconv.OUTCOME_CONVERGED:
        return semconv.EVIDENCE_STRONG
    # Cap / budget / error — call it weak iff we still found at least one
    # relevant chunk; else none.
    relevant = sum(1 for v in verdicts if v.verdict == GradeVerdictKind.RELEVANT)
    if relevant >= 1:
        return semconv.EVIDENCE_WEAK
    return semconv.EVIDENCE_NONE


__all__ = [
    "ExpanderFn",
    "ReflectiveLoopConfig",
    "ReflectiveLoopResult",
    "RetrieverFn",
    "run_reflective_retrieval",
]
