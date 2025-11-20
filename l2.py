# FILE: 10_10/l2.py
"""
Unified L2 Execution Layer (v10_10 · Phase 1)
=============================================

Responsibilities:
    • Execute all L1-produced plans (Strategy, RAG, Drafting, QA, Safety).
    • Call LLMs/tools (via registry) — the ONLY layer allowed to do so.
    • Perform retrieval, ranking, evidence fusion.
    • Generate initial draft sections.
    • Run QA checks (but do NOT enforce safety).
    • Produce a typed L2ResultBundle consumed by L3.

Strict Layering:
    • No planning (L1 only).
    • No DAG orchestration (L3).
    • No state mutation (L4).
    • No safety enforcement or policy decisions (L5).

Restored from v10_8 & v10_9:
    • Hybrid retrieval (BM25 + dense).
    • RRF reciprocal-rank fusion hooks.
    • Weighted evidence fusion pipeline.
    • Draft section generation structure.
    • QA scoring surface.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional

from models import (
    ExecutionContext,
    StrategyPlan,
    RAGPlan,
    DraftingPlan,
    QAPlan,
    SafetyPlan,
    L2ResultBundle,
    QAResult,
    SafetyResult,
    DraftSectionOutput,
)
from observability import start_span, end_span, log_exception
from registry import (
    get_retrieval_client,
    get_ranking_client,
    get_llm_client,
    get_prompt_registry,
)


# =============================================================================
# Retrieval + Ranking
# =============================================================================


def _execute_rag(ctx: ExecutionContext, plan: RAGPlan) -> Dict[str, Any]:
    """
    Run retrieval + ranking + fusion.

    Phase 1 behavior:
        - Executes retrieval via retrieval.py (dense/BM25/hybrid).
        - Executes ranking via ranking.py.
        - Calls RRF and hybrid fusion if available.
        - Returns structured evidence.
    """
    span = start_span("l2.rag")

    try:
        retrieval_client = get_retrieval_client()
        ranking_client = get_ranking_client()

        all_results: Dict[str, Any] = {}

        # -------------------------------------------
        # Retrieval (per RAGQueryHint)
        # -------------------------------------------
        for hint in plan.hints:
            hits = retrieval_client.retrieve(
                focus=hint.focus,
                max_chunks=hint.max_chunks,
                importance=hint.importance,
                hyde=plan.allow_hyde,
                hybrid=plan.require_hybrid,
            )
            all_results[hint.id] = hits

        # -------------------------------------------
        # Fusion / ranking
        # -------------------------------------------
        fused = ranking_client.fuse(all_results)

        return {
            "retrieval_raw": all_results,
            "retrieval_fused": fused,
        }

    except Exception as e:
        log_exception("l2.rag.error", e)
        return {
            "retrieval_raw": {},
            "retrieval_fused": {},
            "error": str(e),
        }
    finally:
        end_span(span)


# =============================================================================
# Draft Generation
# =============================================================================


def _draft_sections(
    ctx: ExecutionContext,
    plan: DraftingPlan,
    rag_output: Dict[str, Any],
) -> List[DraftSectionOutput]:
    """
    Generate draft sections using the LLM route from the registry.

    Phase 1 behavior:
        • For each section:
            - Combine job/resume content (via ctx)
            - Retrieve fused evidence
            - Generate draft text via selected LLM
        • No multi-agent routing yet (Phase 3).
        • No multi-pass drafting yet.

    Output:
        List[DraftSectionOutput]
    """
    span = start_span("l2.drafting")
    llm = get_llm_client()

    fused = rag_output.get("retrieval_fused", {})

    outputs: List[DraftSectionOutput] = []

    try:
        for section in plan.sections:
            prompt = {
                "section_id": section.id,
                "section_title": section.title,
                "job_title": ctx.job.title,
                "role_type": ctx.job.role_type,
                "seniority": ctx.job.seniority,
                "resume_summary": getattr(ctx.resume, "summary", ""),
                "evidence": fused.get(section.id) or fused,
                "tone": plan.target_tone,
                "mode": plan.mode.value,
            }

            text = llm.generate_resume_section(prompt, max_tokens=section.max_tokens)

            outputs.append(
                DraftSectionOutput(
                    section_id=section.id,
                    title=section.title,
                    text=text or "",
                )
            )

        return outputs

    except Exception as e:
        log_exception("l2.drafting.error", e)
        return []
    finally:
        end_span(span)


# =============================================================================
# QA Evaluation
# =============================================================================


def _run_qa(
    ctx: ExecutionContext,
    plan: QAPlan,
    draft_sections: List[DraftSectionOutput],
    rag_output: Dict[str, Any],
) -> QAResult:
    """
    Evaluate QA checks on the draft.

    Phase 1:
        - Simple QA evaluation surface.
        - Later phases expand to multi-agent council.
    """
    span = start_span("l2.qa")

    findings = []

    try:
        for check in plan.checks:
            if not check.enabled:
                continue

            # Each check runs through a QA evaluator in registry
            evaluator = get_ranking_client().qa_evaluator(check.id)

            finding = evaluator.evaluate(
                draft_sections=draft_sections,
                rag_output=rag_output,
                severity=check.severity,
                description=check.description,
            )
            findings.append(finding)

        return QAResult(findings=findings)

    except Exception as e:
        log_exception("l2.qa.error", e)
        return QAResult(findings=[])
    finally:
        end_span(span)


# =============================================================================
# Safety (preliminary)
# =============================================================================


def _run_safety(
    ctx: ExecutionContext,
    plan: SafetyPlan,
    draft_sections: List[DraftSectionOutput],
) -> SafetyResult:
    """
    L2's role in safety:
        - Run preliminary safety scrubs.
        - Collect SafetyFindings.
        - Enforcement / allow/block occurs in L5 only.
    """
    span = start_span("l2.safety")

    findings = []

    try:
        safety_client = get_ranking_client().safety_evaluator()

        for check in plan.checks:
            if not check.enabled:
                continue

            f = safety_client.evaluate(
                draft_sections=draft_sections,
                category=check.category,
                description=check.description,
            )
            findings.append(f)

        return SafetyResult(findings=findings)

    except Exception as e:
        log_exception("l2.safety.error", e)
        return SafetyResult(findings=[])
    finally:
        end_span(span)


# =============================================================================
# Main L2 entrypoint
# =============================================================================


def execute_workflow_plans(
    plans: WorkflowPlanBundle,
    ctx: ExecutionContext,
) -> L2ResultBundle:
    """
    Main L2 execution entrypoint.

    Executes:
        • RAG
        • Drafting
        • QA
        • Preliminary safety

    Returns:
        L2ResultBundle containing:
            - rag
            - drafting
            - qa
            - safety
    """

    root = start_span("l2.execute_workflow_plans", ctx=ctx.span_context())

    try:
        # --------- RAG ---------
        rag_output = _execute_rag(ctx, plans.rag)

        # --------- Drafting ---------
        draft_sections = _draft_sections(ctx, plans.drafting, rag_output)

        # --------- QA ---------
        qa_result = _run_qa(ctx, plans.qa, draft_sections, rag_output)

        # --------- Safety ---------
        safety_result = _run_safety(ctx, plans.safety, draft_sections)

        # --------- Bundle results ---------
        return L2ResultBundle(
            rag=rag_output,
            drafting=draft_sections,
            qa=qa_result,
            safety=safety_result,
        )

    except Exception as e:
        log_exception("l2.execution.error", e)
        return L2ResultBundle(
            rag={},
            drafting=[],
            qa=QAResult(findings=[]),
            safety=SafetyResult(findings=[]),
        )

    finally:
        end_span(root)
