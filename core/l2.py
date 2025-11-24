from __future__ import annotations

"""Business-facing entry point for the second execution layer.

This file keeps older and newer parts of the system using the same "L2"
execution logic, even if they import it in different ways. By acting as a
stable front door, it protects existing workflows from breaking as the code
evolves. This matters for resume quality because it ensures that the core
steps which search for relevant evidence, draft content, run quality checks,
and apply safety reviews keep behaving consistently across versions.

In practice, this layer coordinates how the system gathers supporting
information about a candidate and a role, then passes that context into the
drafting and review steps. That flow helps keep resumes tightly aligned to the
job description while still being safe, accurate, and easy for recruiters to
scan.
"""

import sys
import os
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

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import l2 as l2_module  # type: ignore[import]

_execute_strategy = l2_module._execute_strategy
_execute_drafting = l2_module._execute_drafting
_execute_qa = l2_module._execute_qa
_execute_safety = l2_module._execute_safety
_maybe_run_hyde_query = l2_module._maybe_run_hyde_query
_build_base_query = l2_module._build_base_query


async def _execute_retrieval(
    plans: WorkflowPlanBundle,
    ctx: ExecutionContext,
) -> RAGResult:
    """Gather the most relevant evidence to guide resume rewriting.

    This step decides what information the system should look at before it
    rewrites or evaluates a resume: for example, job description details,
    company context, and other supporting material. By carefully building and
    running the right search queries, it increases the chances that the model
    focuses on the skills, achievements, and requirements that matter most for
    the role.

    In business terms, this retrieval pass is what keeps the resume grounded
    in the actual job, instead of producing a generic rewrite. When the
    evidence is high-quality and on-topic, later drafting and quality checks
    can produce resumes that feel tailored, relevant, and credible to a
    recruiter.
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
