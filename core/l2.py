from __future__ import annotations

"""Core L2 execution shim.

This module re-exports the historical top-level l2 functions so callers
can import from core.l2 without breaking existing code.

It also explicitly exposes the internal ``_execute_*`` helpers required by
``workflow_graph.py`` when importing from ``core.l2``.
"""

from typing import Optional

from core.models.models import (  # type: ignore[attr-defined]
    ExecutionContext,
    WorkflowPlanBundle,
    RAGResult,
    RAGPlan,
    RetrievalConfig,
)
from runtime.observability import start_span, end_span, log_exception
from meta.retrieval import run_rag_retrieval

from l2 import (  # type: ignore[import]
    _execute_strategy,
    _execute_drafting,
    _execute_qa,
    _execute_safety,
    _maybe_run_hyde_query,
    _build_base_query,
)
from l2 import *  # noqa: F401,F403


async def _execute_retrieval(
    plans: WorkflowPlanBundle,
    ctx: ExecutionContext,
) -> RAGResult:
    """Snapshot-local retrieval shim for tests and workflow_graph.

    This mirrors the Phase-3 l2._execute_retrieval semantics but resolves
    helpers via the core.l2 namespace so that tests can monkeypatch
    ``_maybe_run_hyde_query`` and ``run_rag_retrieval`` on core.l2.
    """

    span = start_span("l2.retrieval", ctx=ctx.span_context())
    try:
        rag_plan: Optional[RAGPlan] = getattr(plans, "rag", None)
        retrieval_cfg = ctx.retrieval or RetrievalConfig()

        query = _build_base_query(ctx)
        hyde_query = await _maybe_run_hyde_query(rag_plan, ctx)

        evidence_list = run_rag_retrieval(
            query=query,
            ctx=ctx,
            retrieval_cfg=retrieval_cfg,
            hyde_query=hyde_query,
            council_vote=None,
        )

        return RAGResult(
            evidence=list(evidence_list or []),
            used_hyde=hyde_query is not None,
        )
    except Exception as exc:  # noqa: BLE001
        log_exception("l2.retrieval_error", exc)
        return RAGResult(evidence=[], used_hyde=False)
    finally:
        end_span(span)


__all__ = [
    # Internal execution helpers used by workflow_graph
    "_execute_strategy",
    "_execute_retrieval",
    "_execute_drafting",
    "_execute_qa",
    "_execute_safety",
    "_maybe_run_hyde_query",
]
