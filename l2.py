# FILE: 10_10/l2.py
"""
Unified L2 Execution Layer (v10_10 · Phase 3)
=============================================

Responsibilities:
    • Execute StrategyPlan, RAGPlan, DraftingPlan, QAPlan, SafetyPlan.
    • Perform all LLM calls (via cognitive_agents), plus retrieval hooks.
    • Produce structured outputs:
          – StrategyResult
          – RAGResult (evidence + Phase-3 RAG reasoning signal)
          – DraftingResult
          – QAResult
          – SafetyResult
    • Wrap all computation in deterministic observability spans.
    • NO state mutation (L4 only).

This module is the only legal place where L2 cognition is orchestrated.

Design constraints:
    1) No direct provider SDK usage.
       All LLM calls are delegated to cognitive_agents.
    2) No state mutation (WorkflowStatePatch is applied in L4).
    3) No RAG ranking logic (lives in retrieval.py / ranking.py).
    4) No DAG orchestration (lives in workflow_graph.py).
"""

from __future__ import annotations

import asyncio
from typing import Any

from models import (
    ExecutionContext,
    WorkflowPlanBundle,
    StrategyResult,
    StrategyBranch,
    Evidence,
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
from prompt_builder import build_rag_prompt
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
    Run the strategy agent with the StrategyPlan using the Phase-2/3
    cognitive agent + prompt builder layer.
    """
    span = start_span("l2.strategy", ctx=ctx.span_context())
    try:
        agent = StrategyLLMAgent(
            routing_policy=ctx.routing_policy,
            sandbox=ctx.sandbox_config,
            meta_profile=ctx.meta_profile_snapshot,
        )
        result = await agent.run_strategy(
            strategy_plan=plans.strategy,
            job=ctx.job,
            resume=ctx.resume,
            config=ctx.config,
        )
        return result
    except Exception as exc:  # noqa: BLE001
        log_exception("l2.strategy_error", exc)

        # Fallback: deterministic "single branch" strategy.
        fallback_branch = StrategyBranch(
            id="fallback",
            text="Default strategy: straightforward resume tailoring.",
        )
        return StrategyResult(branches=[fallback_branch], chosen_branch_id="fallback")
    finally:
        end_span(span)


# =============================================================================
# Retrieval Raw-Hit Construction
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
    for req in getattr(job, "requirements", [])[:max_job_chunks]:
        if not req:
            continue
        raw_hits.append(
            {
                "evidence": str(req),
                "score": 1.0,
                "source": "job_requirement",
            }
        )

    # Resume summary as one chunk, if present.
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

    # Hybrid padding: combined job+resume text if there is room.
    max_hybrid_chunks = getattr(cfg, "rag_max_hybrid_chunks", 12)
    if (
        len(raw_hits) < max_hybrid_chunks
        and getattr(job, "posting_text", None)
        and getattr(resume, "summary", None)
    ):
        hybrid_text = f"{job.posting_text}\n\n{resume.summary}"
        raw_hits.append(
            {
                "evidence": hybrid_text,
                "score": 1.0,
                "source": "hybrid_job_resume",
            }
        )

    return raw_hits


# =============================================================================
# Retrieval Execution
# =============================================================================


async def _execute_retrieval(
    plans: WorkflowPlanBundle,
    ctx: ExecutionContext,
) -> RAGResult:
    """
    Phase-3 RAG execution.

    This wires L2 into the deterministic retrieval pipeline:

        1. Build raw hits from job + resume (no external side effects).
        2. Call retrieval.run_rag_retrieval() to:
              – normalize / deduplicate
              – apply per-retriever failure fallback
              – rank (RRF, BM25, dense, hybrid, HYDE)
        3. Wrap the Evidence list in a typed RAGResult.

    All heavy lifting (normalization, ranking, fallback) lives in
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
            strategy_hint=rag_plan.strategy_hint,
            sandbox=ctx.sandbox_config,
            raw_hits=raw_hits,
        )

        return RAGResult(evidence=evidence_list, used_hyde=False)
    except Exception as exc:  # noqa: BLE001
        log_exception("l2.retrieval_error", exc)
        # On any failure, downstream layers must still be able to run.
        return RAGResult(evidence=[], used_hyde=False)
    finally:
        end_span(span)


# =============================================================================
# RAG Reasoning Execution (Phase 3)
# =============================================================================


async def _execute_rag_reasoning(
    plans: WorkflowPlanBundle,
    rag_result: RAGResult,
    ctx: ExecutionContext,
) -> RAGResult:
    """
    Phase-3 RAG reasoning step.

    Runs between retrieval and drafting:

        1. Build a RAG prompt using build_rag_prompt.
        2. Call a lightweight LLM agent to reason over the retrieved
           evidence (no additional retrieval).
        3. Inject the reasoning as a synthetic Evidence item at the
           front of the evidence list.

    On any failure, this function logs the exception and returns the
    original rag_result unchanged so that downstream stages can still
    execute.
    """
    span = start_span("l2.rag_reasoning", ctx=ctx.span_context())
    try:
        if not rag_result.evidence:
            # No evidence → nothing to reason about; short-circuit.
            return rag_result

        # Build a RAG reasoning prompt.
        prompt = build_rag_prompt(
            job=ctx.job,
            resume=ctx.resume,
            strategy_result=None,
            rag_result=rag_result,
            config=ctx.config,
        )

        # For Phase 3, we re-use the QA agent infrastructure to perform
        # a focused reasoning pass, but treat it as "context synthesis".
        agent = SemanticQAAgent(
            routing_policy=ctx.routing_policy,
            sandbox=ctx.sandbox_config,
            meta_profile=ctx.meta_profile_snapshot,
        )

        # The agent is expected to produce a textual synthesis of the
        # retrieved evidence that can be treated as an extra Evidence item.
        reasoning_text = await agent.run_rag_reasoning(
            prompt=prompt,
            evidence=rag_result.evidence,
            job=ctx.job,
            resume=ctx.resume,
            config=ctx.config,
        )

        if not reasoning_text:
            # Graceful fallback: no synthetic evidence added.
            return rag_result

        synthetic_ev = Evidence(
            id="rag_reasoning_synthesis",
            text=reasoning_text,
            score=1.0,
            source="rag_reasoning",
            metadata={"synthetic": True},
        )

        # Prepend the synthetic evidence to the existing list.
        new_evidence = [synthetic_ev] + list(rag_result.evidence or [])
        return RAGResult(evidence=new_evidence, used_hyde=rag_result.used_hyde)
    except Exception as exc:  # noqa: BLE001
        log_exception("l2.rag_reasoning_error", exc)
        return rag_result
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
    Run the drafting guild over the StrategyResult + RAGResult.

    DraftingGuild is responsible for:
        • Section planning
        • Bullet generation
        • Formatting choices

    It returns a DraftingResult with structured draft sections.
    """
    span = start_span("l2.drafting", ctx=ctx.span_context())
    try:
        agent = DraftingGuild(
            routing_policy=ctx.routing_policy,
            sandbox=ctx.sandbox_config,
            meta_profile=ctx.meta_profile_snapshot,
        )
        result = await agent.run_drafting(
            drafting_plan=plans.drafting,
            job=ctx.job,
            resume=ctx.resume,
            strategy_result=strategy_result,
            rag_result=rag_result,
            config=ctx.config,
        )
        return result
    except Exception as exc:  # noqa: BLE001
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
    Run the QA agent over the drafted resume + retrieval evidence.

    The QA agent produces structured QACheckResult findings.
    """
    span = start_span("l2.qa", ctx=ctx.span_context())
    try:
        agent = SemanticQAAgent(
            routing_policy=ctx.routing_policy,
            sandbox=ctx.sandbox_config,
            meta_profile=ctx.meta_profile_snapshot,
        )

        result = await agent.run_qa(
            qa_plan=plans.qa,
            draft=drafting_result,
            rag=rag_result,
            job=ctx.job,
            resume=ctx.resume,
            config=ctx.config,
        )
        return result
    except Exception as exc:  # noqa: BLE001
        log_exception("l2.qa_error", exc)
        return QAResult(findings=[])
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
    Run the safety agent over the drafted resume + QA findings.

    SafetyResult is a lightweight summary of policy findings and is
    consumed by L5 for final enforcement decisions.
    """
    span = start_span("l2.safety", ctx=ctx.span_context())
    try:
        agent = ConstitutionalSafetyAgent(
            routing_policy=ctx.routing_policy,
            sandbox=ctx.sandbox_config,
            meta_profile=ctx.meta_profile_snapshot,
        )

        result = await agent.run_safety(
            safety_plan=plans.safety,
            draft=drafting_result,
            qa_result=qa_result,
            job=ctx.job,
            resume=ctx.resume,
            config=ctx.config,
        )
        return result
    except Exception as exc:  # noqa: BLE001
        log_exception("l2.safety_error", exc)

        # Fallback: treat the entire safety stage as a single finding
        # indicating internal failure; this is interpreted by L5 as a
        # "fail closed" signal.
        finding = SafetyFinding(
            check_id="safety_internal_error",
            category="internal_error",
            severity="high",
            message="Safety agent failed; see logs for details.",
            details={},
        )
        return SafetyResult(findings=[finding])
    finally:
        end_span(span)


# =============================================================================
# Top-Level L2 Execution Orchestration
# =============================================================================


async def run_l2(
    plans: WorkflowPlanBundle,
    ctx: ExecutionContext,
) -> L2ResultBundle:
    """
    Execute all L2 stages for the workflow:

        • Strategy
        • Retrieval
        • RAG reasoning
        • Drafting
        • QA
        • Safety

    With concurrency:
        • Strategy + Retrieval in parallel.
        • RAG reasoning → Drafting → QA → Safety sequentially.
    """
    span = start_span("l2.run", ctx=ctx.span_context())
    try:
        # Strategy and RAG can be independent.
        strategy_task = asyncio.create_task(_execute_strategy(plans, ctx))
        rag_task = asyncio.create_task(_execute_retrieval(plans, ctx))

        # Wait for Strategy + RAG to complete before drafting.
        strategy_result, rag_result = await asyncio.gather(strategy_task, rag_task)

        # Phase 3: RAG reasoning stage between retrieval and drafting.
        rag_result = await _execute_rag_reasoning(plans, rag_result, ctx)

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
    except Exception as exc:  # noqa: BLE001
        log_exception("l2.run_error", exc)

        # In the event of a catastrophic failure, we still return a fully
        # populated but "empty" bundle so that downstream layers have a
        # deterministic contract.
        empty_strategy = StrategyResult(branches=[], chosen_branch_id=None)
        empty_rag = RAGResult(evidence=[], used_hyde=False)
        empty_drafting = DraftingResult(sections=[])
        empty_qa = QAResult(findings=[])
        empty_safety = SafetyResult(
            findings=[
                SafetyFinding(
                    check_id="l2_run_error",
                    category="internal_error",
                    severity="high",
                    message="L2.run failed; see logs for details.",
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
