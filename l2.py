# FILE: 10_10/l2.py
"""
Unified L2 Execution Layer (v10_10 · Phase 2)
=============================================

Responsibilities:
    • Execute StrategyPlan, RAGPlan, DraftingPlan, QAPlan, SafetyPlan.
    • Perform all LLM calls (via cognitive_agents), plus retrieval hooks.
    • Produce structured outputs:
          – StrategyResult
          – RAGResult
          – DraftingResult
          – QAResult
          – SafetyResult
    • Wrap all computation in deterministic observability spans.
    • NO state mutation (L4 only).

Layering Rules:
    • L1 performs planning only (no LLM, no retrieval).
    • L2 performs execution: retrieval + ranking + LLM calls.
    • L3 orchestrates DAG and concurrency, no LLM calls.
    • L4 is the only legal state mutation surface.
    • L5 performs safety enforcement and policy decisions.
"""

from __future__ import annotations

import asyncio
from typing import Any

from models import (
    ExecutionContext,
    WorkflowPlanBundle,
    StrategyResult,
    StrategyBranch,
    RAGResult,
    DraftingResult,
    QAResult,
    QACheckResult,
    SafetyResult,
    SafetyFinding,
    L2ResultBundle,
)
from observability import start_span, end_span, log_exception, emit_cost_snapshot
from retrieval import run_rag_retrieval
from cognitive_agents import (
    StrategyLLMAgent,
    DraftingGuild,
    SemanticQAAgent,
    ConstitutionalSafetyAgent,
)


# =============================================================================
# Strategy Execution
# =============================================================================


async def _execute_strategy(
    plans: WorkflowPlanBundle,
    ctx: ExecutionContext,
) -> StrategyResult:
    """
    Run the strategy agent with the StrategyPlan using the Phase-2
    cognitive agent + prompt builder layer.
    """
    span = start_span("l2.strategy", ctx=ctx.span_context())
    try:
        agent = StrategyLLMAgent(
            routing_policy=ctx.routing_policy,
            sandbox=ctx.sandbox_config,
            meta_profile=ctx.meta_profile_snapshot,
        )
        # Strategy agent returns a StrategyResult directly.
        result = agent.run_strategy(plans.strategy, ctx)
        return result
    except Exception as exc:
        log_exception("l2.strategy_error", exc)
        # Fallback: synthesize a minimal StrategyResult encoding the error.
        return StrategyResult(
            branches=[StrategyBranch(id="error", text=str(exc))],
            chosen_branch_id="error",
        )
    finally:
        end_span(span)


# =============================================================================
# Retrieval Execution (Phase 3 · RAG pipeline)
# =============================================================================


def _build_rag_raw_hits(plans: WorkflowPlanBundle, ctx: ExecutionContext) -> list[dict]:
    """
    Construct a deterministic set of raw retrieval hits from the in-memory
    job and resume inputs.

    This is intentionally simple and side-effect free:

        • No external DB/vector calls (kept in-process and testable).
        • Chunks are derived from:
              – job.posting_text
              – job.requirements[]
              – resume.summary
              – resume.experience_sections[]
        • Context budgeting is applied using WorkflowConfig.rag_* knobs.
    """
    job = ctx.job
    resume = ctx.resume
    cfg = ctx.config

    raw_hits: list[dict] = []

    # Job posting as a single chunk.
    if getattr(job, "posting_text", None):
        raw_hits.append(
            {
                "evidence": job.posting_text,
                "score": 1.0,
                "source": "job_posting",
            }
        )

    # Individual job requirements (truncated by rag_max_job_chunks).
    max_job_chunks = getattr(cfg, "rag_max_job_chunks", 8)
    for idx, req in enumerate(getattr(job, "requirements", [])[:max_job_chunks]):
        if not req:
            continue
        raw_hits.append(
            {
                "evidence": str(req),
                "score": 1.0,
                "source": "job_requirement",
            }
        )

    # Resume summary as a single chunk.
    if getattr(resume, "summary", None):
        raw_hits.append(
            {
                "evidence": resume.summary,
                "score": 1.0,
                "source": "resume_summary",
            }
        )

    # Resume experience sections (truncated by rag_max_resume_chunks).
    max_resume_chunks = getattr(cfg, "rag_max_resume_chunks", 8)
    for section in getattr(resume, "experience_sections", [])[:max_resume_chunks]:
        text = (
            section.get("text")
            or section.get("description")
            or section.get("summary")
            or ""
        )
        if not text:
            continue
        raw_hits.append(
            {
                "evidence": str(text),
                "score": 1.0,
                "source": "resume_experience",
            }
        )

    # Hybrid padding: if there is room, include combined job+resume text.
    max_hybrid_chunks = getattr(cfg, "rag_max_hybrid_chunks", 12)
    if (
        len(raw_hits) < max_hybrid_chunks
        and getattr(job, "posting_text", None)
        and getattr(resume, "summary", None)
    ):
        combined_text = f"JOB: {job.posting_text}\n\nRESUME: {resume.summary}"
        raw_hits.append(
            {
                "evidence": combined_text,
                "score": 1.0,
                "source": "job_resume_hybrid",
            }
        )

    return raw_hits


async def _execute_retrieval(
    plans: WorkflowPlanBundle,
    ctx: ExecutionContext,
) -> RAGResult:
    """
    Phase-3 RAG execution.

    This wires L2 into the deterministic retrieval pipeline:

        1. Build raw hits from job + resume (no external side effects).
        2. Call retrieval.run_rag_retrieval() to:
              – normalize
              – deduplicate
              – safety-filter
              – rank (via ranking.rank_evidence)
        3. Wrap the Evidence list in a typed RAGResult.

    All heavy lifting (normalization, ranking, safety) lives in
    retrieval.py / ranking.py. L2 only orchestrates and applies the
    WorkflowConfig context budgets.
    """
    span = start_span("l2.retrieval", ctx=ctx.span_context())
    try:
        rag_plan = plans.rag

        raw_hits = _build_rag_raw_hits(plans, ctx)
        if not raw_hits:
            # Deterministic empty result if there is literally nothing
            # to retrieve from job/resume inputs.
            return RAGResult(evidence=[], used_hyde=False)

        evidence_list = run_rag_retrieval(
            rag_plan=rag_plan,
            job=ctx.job,
            resume=ctx.resume,
            config=ctx.config,
            strategy_hint=None,
            sandbox=ctx.sandbox_config,
            raw_hits=raw_hits,
        )

        return RAGResult(evidence=evidence_list, used_hyde=False)
    except Exception as exc:
        log_exception("l2.retrieval_error", exc)
        # On any failure, downstream layers must still be able to run.
        return RAGResult(evidence=[], used_hyde=False)
    finally:
        end_span(span)


# =============================================================================
# Drafting Execution
# =============================================================================


async def _execute_drafting(
    plans: WorkflowPlanBundle,
    strategy_result: StrategyResult,
    rag_result: RAGResult,
    ctx: ExecutionContext,
) -> DraftingResult:
    """
    Run the drafting agent with:
        - DraftingPlan
        - StrategyResult
        - RAGResult (evidence, if any)
    """
    span = start_span("l2.drafting", ctx=ctx.span_context())
    try:
        agent = DraftingGuild(
            routing_policy=ctx.routing_policy,
            sandbox=ctx.sandbox_config,
            meta_profile=ctx.meta_profile_snapshot,
        )

        result = agent.run_drafting(
            drafting_plan=plans.drafting,
            job=ctx.job,
            resume=ctx.resume,
            strategy_result=strategy_result,
            rag_result=rag_result,
            config=ctx.config,
        )
        return result
    except Exception as exc:
        log_exception("l2.drafting_error", exc)
        # Fallback: empty DraftingResult in the configured mode.
        return DraftingResult(sections=[])
    finally:
        end_span(span)


# =============================================================================
# QA Execution
# =============================================================================


async def _execute_qa(
    plans: WorkflowPlanBundle,
    drafting_result: DraftingResult,
    rag_result: RAGResult,
    ctx: ExecutionContext,
) -> QAResult:
    """
    Run the QA agent on the drafted document + retrieval evidence.
    """
    span = start_span("l2.qa", ctx=ctx.span_context())
    try:
        agent = SemanticQAAgent(
            routing_policy=ctx.routing_policy,
            sandbox=ctx.sandbox_config,
            meta_profile=ctx.meta_profile_snapshot,
        )

        result = agent.run_qa(
            qa_plan=plans.qa,
            draft=drafting_result,
            rag=rag_result,
            job=ctx.job,
            resume=ctx.resume,
            config=ctx.config,
        )
        return result
    except Exception as exc:
        log_exception("l2.qa_error", exc)
        # Fallback: single internal-error QA finding.
        return QAResult(
            findings=[
                QACheckResult(
                    check_id="qa_internal_error",
                    category="internal",
                    status="error",
                    message=str(exc),
                    details={},
                )
            ]
        )
    finally:
        end_span(span)


# =============================================================================
# Safety Execution
# =============================================================================


async def _execute_safety(
    plans: WorkflowPlanBundle,
    drafting_result: DraftingResult,
    qa_result: QAResult,
    ctx: ExecutionContext,
) -> SafetyResult:
    """
    Run the safety agent on drafted content + QA findings.
    """
    span = start_span("l2.safety", ctx=ctx.span_context())
    try:
        agent = ConstitutionalSafetyAgent(
            routing_policy=ctx.routing_policy,
            sandbox=ctx.sandbox_config,
            meta_profile=ctx.meta_profile_snapshot,
        )

        result = agent.run_safety(
            safety_plan=plans.safety,
            draft=drafting_result,
            qa=qa_result,
            job=ctx.job,
            resume=ctx.resume,
            config=ctx.config,
        )
        return result
    except Exception as exc:
        log_exception("l2.safety_error", exc)
        # Fallback: single blocked finding.
        return SafetyResult(
            findings=[
                SafetyFinding(
                    check_id="safety_internal_error",
                    category="internal",
                    status="blocked",
                    message=str(exc),
                    details={},
                )
            ]
        )
    finally:
        end_span(span)


# =============================================================================
# L2 Orchestration (called by L3)
# =============================================================================


async def run_l2(
    plans: WorkflowPlanBundle,
    ctx: ExecutionContext,
) -> L2ResultBundle:
    """
    Main L2 entrypoint called by the L3 orchestrator.

    It runs:
        • Strategy
        • Retrieval
        • Drafting
        • QA
        • Safety

    With concurrency:
        • Strategy + Retrieval in parallel.
        • Drafting → QA → Safety sequentially.
    """
    span = start_span("l2.run", ctx=ctx.span_context())
    try:
        # Strategy and RAG can be independent
        strategy_task = asyncio.create_task(_execute_strategy(plans, ctx))
        rag_task = asyncio.create_task(_execute_retrieval(plans, ctx))

        # Wait for Strategy + RAG to complete before drafting
        strategy_result, rag_result = await asyncio.gather(strategy_task, rag_task)

        drafting_result = await _execute_drafting(plans, strategy_result, rag_result, ctx)
        qa_result = await _execute_qa(plans, drafting_result, rag_result, ctx)
        safety_result = await _execute_safety(plans, drafting_result, qa_result, ctx)

        # Emit a coarse-grained cost snapshot from the context, if available.
        if ctx.cost_snapshot is not None:
            emit_cost_snapshot(ctx.cost_snapshot)

        return L2ResultBundle(
            strategy=strategy_result,
            rag=rag_result,
            drafting=drafting_result,
            qa=qa_result,
            safety=safety_result,
        )
    except Exception as exc:
        log_exception("l2.run_error", exc)
        # On catastrophic failure, synthesize an empty result bundle.
        empty_strategy = StrategyResult(
            branches=[StrategyBranch(id="error", text=str(exc))],
            chosen_branch_id="error",
        )
        empty_rag = RAGResult(evidence=[], used_hyde=False)
        empty_drafting = DraftingResult(sections=[])
        empty_qa = QAResult(
            findings=[
                QACheckResult(
                    check_id="qa_internal_error",
                    category="internal",
                    status="error",
                    message=str(exc),
                    details={},
                )
            ]
        )
        empty_safety = SafetyResult(
            findings=[
                SafetyFinding(
                    check_id="safety_internal_error",
                    category="internal",
                    status="blocked",
                    message=str(exc),
                    details={},
                )
            ]
        )

        # Emit a best-effort cost snapshot if present.
        if ctx.cost_snapshot is not None:
            emit_cost_snapshot(ctx.cost_snapshot)

        return L2ResultBundle(
            strategy=empty_strategy,
            rag=empty_rag,
            drafting=empty_drafting,
            qa=empty_qa,
            safety=empty_safety,
        )
    finally:
        end_span(span)
