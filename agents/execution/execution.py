"""
L2 execution layer for résumé improvement tasks.

Executes cognitive agents to generate strategy, drafting, QA, and safety improvements for comprehensive résumé enhancement.
"""

# FILE: l2.py

from __future__ import annotations

import asyncio
from typing import Any, List, Optional, Sequence, Tuple

from core.models.models import (
    ExecutionContext,
    WorkflowPlanBundle,
    StrategyResult,
    StrategyBranch,
    Evidence,
    RAGResult,
    DraftingResult,
    DraftSection,
    QAResult,
    SafetyResult,
    L2ResultBundle,
    RAGPlan,
    RetrievalConfig,
    CouncilVote,
)

from runtime.observability import start_span, end_span, log_exception, emit_cost_snapshot, record_event
from meta.schema_validation import validate_schema_version
import meta.retrieval as _retrieval_module
from infrastructure.di_container import inject_dependencies, get_service
from safety.policy import SafetyEngine
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .agents import (
        StrategyLLMAgent,
        DraftingGuild,
        SemanticQAAgent,
        ConstitutionalSafetyAgent,
        HYDEQueryAgent,
    )
from eval.health.adapter import collect_error_events
from eval.health.failure_detector import detect_repeated_failures
from eval.health.repair_policies import propose_repairs

# Module-level reference for test patching compatibility
run_rag_retrieval = _retrieval_module.run_rag_retrieval


"""
Provides helper functions for reliable résumé processing execution.

Ensures robust operation and error handling for comprehensive résumé improvement workflows.
"""


def _safe_getattr(obj: Any, name: str, default: Any = "") -> Any:
    """
    Safely accesses object attributes for reliable résumé processing.
    
    Prevents errors that could interrupt comprehensive résumé improvement workflows.
    """
    try:
        return getattr(obj, name, default)
    except Exception:  # pragma: no cover - extreme defensive
        return default


def _build_base_query(ctx: ExecutionContext) -> str:
    """
    Constructs search query from job and resume data.
    
    Creates focused queries to find relevant evidence for résumé improvement.
    """
    job = _safe_getattr(ctx, "job", None)
    resume = _safe_getattr(ctx, "resume", None)

    parts: List[str] = []

    if job is not None:
        title = _safe_getattr(job, "title", "") or ""
        company = _safe_getattr(job, "company", "") or ""
        posting = _safe_getattr(job, "posting_text", "") or ""
        header = "Job:".strip()
        body = "\n".join(p for p in [title, company, posting] if p)
        if body:
            parts.append(f"{header}\n{body}".strip())

    if resume is not None:
        summary = _safe_getattr(resume, "summary", "") or ""
        if summary:
            parts.append(f"Candidate summary:\n{summary}".strip())

    query = "\n\n".join(p for p in parts if p).strip()
    if not query:
        # Deterministic fallback so retrieval always has a non-empty query.
        query = "tailor resume to job requirements"
    return query


def _compute_council_vote_from_qa(qa_result: QAResult) -> CouncilVote:
    """
    Derives quality assessment vote from QA findings.
    
    Ensures consistent evaluation of résumé improvement quality and safety.
    """
    findings = list(getattr(qa_result, "findings", []) or [])

    high = sum(1 for f in findings if getattr(f, "severity", "").lower() == "high")
    medium = sum(1 for f in findings if getattr(f, "severity", "").lower() == "medium")
    low = sum(1 for f in findings if getattr(f, "severity", "").lower() == "low")

    if high > 0:
        selected = "block"
    elif medium > 0:
        selected = "warn"
    else:
        selected = "pass"

    scores = {
        "block": float(high),
        "warn": float(medium),
        "pass": float(low or 1.0),
    }

    return CouncilVote(
        members=len(findings) or 1,
        selected_id=selected,
        scores=scores,
        ties=[],
        reason="heuristic_from_qa_findings",
    )


def _run_latent_thinking(result: L2ResultBundle, ctx: ExecutionContext) -> None:
    """
    Records thinking trace for résumé improvement analysis.
    
    Maintains observability of decision processes for quality enhancement.
    """
    # L2 does not call L1 - latent thinking plans should be pre-computed
    # and passed via the plans bundle if needed.
    try:
        record_event(
            "l2.latent_thinking",
            {
                "profile": getattr(ctx, "profile_name", "default"),
                "reasoning_mode": "cot",
                "trace_length": 0,
            },
        )
    except Exception:
        return


async def _maybe_run_hyde_query(
    rag_plan: Optional[RAGPlan],
    ctx: ExecutionContext,
) -> Optional[str]:
    """
    Generates hypothetical document queries for better retrieval.
    
    Creates enhanced search queries to find relevant résumé improvement evidence.
    """
    if rag_plan is None or not getattr(rag_plan, "allow_hyde", False):
        return None

    span = start_span("l2.hyde_query", ctx=ctx.span_context())
    try:
        from .agents import HYDEQueryAgent
        agent = HYDEQueryAgent(
            routing_policy=ctx.routing_policy,
            sandbox=ctx.sandbox_config,
            meta_profile=ctx.meta_profile_snapshot,
        )
        text = await agent.run_hyde_query(rag_plan=rag_plan, ctx=ctx)
        text = (text or "").strip()
        return text or None
    except Exception as exc:  # noqa: BLE001
        log_exception("l2.hyde_query_error", exc)
        return None
    finally:
        end_span(span)


"""
Executes résumé strategy planning with optimal model selection.

Generates targeted improvement plans to enhance job description alignment.
"""


async def _execute_strategy(
    plans: WorkflowPlanBundle,
    ctx: ExecutionContext,
) -> StrategyResult:
    """
    Executes résumé strategy planning with optimal model selection.
    
    Generates targeted improvement plans to enhance job description alignment.
    """
    span = start_span("l2.strategy", ctx=ctx.span_context())
    try:
        from .agents import StrategyLLMAgent
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


"""
Executes comprehensive evidence retrieval for résumé improvement.

Gathers relevant data using multiple search strategies to support résumé enhancement.
"""


async def _execute_retrieval(
    plans: WorkflowPlanBundle,
    ctx: ExecutionContext,
) -> RAGResult:
    """
    Executes comprehensive evidence retrieval for résumé improvement.
    
    Gathers relevant data using multiple search strategies to support résumé enhancement.
    """
    span = start_span("l2.retrieval", ctx=ctx.span_context())
    try:
        rag_plan: Optional[RAGPlan] = getattr(plans, "rag", None)
        retrieval_cfg = ctx.retrieval or RetrievalConfig()

        # Ensure dependencies are injected via DI container
        ctx = inject_dependencies(ctx)
        
        query = _build_base_query(ctx)
        
        # Call _maybe_run_hyde_query directly (allows test patching via l2.execution.*)
        hyde_query = await _maybe_run_hyde_query(rag_plan, ctx)

        # Use module-level run_rag_retrieval for retrieval (allows test patching)
        # PineconeAdapter integration is handled inside meta.retrieval if configured
        evidence_list = run_rag_retrieval(
            query=query,
            ctx=ctx,
            retrieval_cfg=retrieval_cfg,
            hyde_query=hyde_query,
            council_vote=None,  # QA council weighting is applied in later phases.
        )

        return RAGResult(evidence=list(evidence_list or []), used_hyde=hyde_query is not None)
    except Exception as exc:  # noqa: BLE001
        log_exception("l2.retrieval_error", exc)
        # On any failure, downstream layers must still be able to run.
        return RAGResult(evidence=[], used_hyde=False)
    finally:
        end_span(span)


"""
Analyzes retrieved evidence for résumé improvement insights.

Processes evidence to extract relevant information for résumé enhancement.
"""


async def _execute_rag_reasoning(
    plans: WorkflowPlanBundle,
    rag_result: RAGResult,
    ctx: ExecutionContext,
) -> RAGResult:
    """
    Analyzes retrieved evidence for résumé improvement insights.
    
    Processes evidence to extract relevant information for résumé enhancement.
    """
    span = start_span("l2.rag_reasoning", ctx=ctx.span_context())
    try:
        evidence_seq: Sequence[Evidence] = list(rag_result.evidence or [])
        if not evidence_seq:
            # Nothing to reason over; propagate the original result.
            return rag_result

        rag_plan: Optional[RAGPlan] = getattr(plans, "rag", None)

        # Build a simple prompt from the RAG plan (no L1 call)
        prompt = "Analyze the following evidence and provide reasoning:"
        if rag_plan:
            prompt = f"RAG strategy: {getattr(rag_plan, 'strategy', 'hybrid')}. {prompt}"

        from .agents import SemanticQAAgent
        agent = SemanticQAAgent(
            routing_policy=ctx.routing_policy,
            sandbox=ctx.sandbox_config,
            meta_profile=ctx.meta_profile_snapshot,
        )
        reasoning_text = await agent.run_rag_reasoning(
            prompt=prompt,
            evidence=evidence_seq,
            job=ctx.job,
            resume=ctx.resume,
            config=ctx.config,
        )
        reasoning_text = (reasoning_text or "").strip()
        if not reasoning_text:
            return rag_result

        synthetic = Evidence(
            text=reasoning_text,
            score=1.0,
            source="rag_reasoning",
            metadata={"layer": "L2", "agent": "rag_reasoning"},
        )

        return RAGResult(
            evidence=list(evidence_seq) + [synthetic],
            used_hyde=rag_result.used_hyde,
        )
    except Exception as exc:  # noqa: BLE001
        log_exception("l2.rag_reasoning_error", exc)
        return rag_result
    finally:
        end_span(span)


"""
Executes résumé content drafting with strategy and evidence.

Generates compelling résumé sections using strategy guidance and retrieved evidence.
"""


async def _execute_drafting(
    plans: WorkflowPlanBundle,
    strategy_result: StrategyResult,
    rag_result: RAGResult,
    ctx: ExecutionContext,
) -> DraftingResult:
    """
    Executes résumé content drafting with strategy and evidence.
    
    Generates compelling résumé sections using strategy guidance and retrieved evidence.
    """
    span = start_span("l2.drafting", ctx=ctx.span_context())
    try:
        from .agents import DraftingGuild
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


"""
Executes quality assurance validation for résumé content.

Ensures résumé accuracy and relevance through comprehensive QA analysis.
"""


async def _execute_qa(
    plans: WorkflowPlanBundle,
    drafting_result: DraftingResult,
    rag_result: RAGResult,
    ctx: ExecutionContext,
) -> Tuple[QAResult, CouncilVote]:
    """
    Executes quality assurance validation for résumé content.
    
    Returns structured QA findings and council vote for résumé quality assessment.
    """
    span = start_span("l2.qa", ctx=ctx.span_context())
    try:
        from .agents import SemanticQAAgent
        agent = SemanticQAAgent(
            routing_policy=ctx.routing_policy,
            sandbox=ctx.sandbox_config,
            meta_profile=ctx.meta_profile_snapshot,
        )
        qa_result = await agent.run_qa(
            qa_plan=plans.qa,
            draft=drafting_result,
            rag=rag_result,
            job=ctx.job,
            resume=ctx.resume,
            config=ctx.config,
        )

        council_vote = _compute_council_vote_from_qa(qa_result)
        return qa_result, council_vote
    except Exception as exc:  # noqa: BLE001
        log_exception("l2.qa_error", exc)
        empty = QAResult(findings=[])
        return empty, _compute_council_vote_from_qa(empty)
    finally:
        end_span(span)


"""
Executes safety validation for résumé compliance and protection.

Ensures résumé content meets safety standards to protect user data and credibility.
"""


async def _execute_safety(
    plans: WorkflowPlanBundle,
    drafting_result: DraftingResult,
    rag_result: RAGResult,
    qa_result: QAResult,
    ctx: ExecutionContext,
) -> SafetyResult:
    """
    Executes safety validation for résumé compliance and protection.
    
    Produces safety assessment for résumé content without making enforcement decisions.
    """
    span = start_span("l2.safety", ctx=ctx.span_context())
    try:
        # Ensure dependencies are injected via DI container
        ctx = inject_dependencies(ctx)
        
        from .agents import ConstitutionalSafetyAgent
        agent = ConstitutionalSafetyAgent(
            routing_policy=ctx.routing_policy,
            sandbox=ctx.sandbox_config,
            meta_profile=ctx.meta_profile_snapshot,
        )
        result = await agent.run_safety(
            safety_plan=plans.safety,
            draft=drafting_result,
            rag=rag_result,
            qa_result=qa_result,
            job=ctx.job,
            resume=ctx.resume,
            config=ctx.config,
        )
        
        # Apply additional safety validation via injected SafetyEngine if available
        safety_engine = ctx.safety_engine or get_service(SafetyEngine)
        if safety_engine and result:
            from safety.types import SafetyContext
            safety_context = SafetyContext(
                content_type="draft",
                source="l2_execution",
                destination="l5_policy",
                content=str(drafting_result),
                user_id=getattr(ctx, "user_id", "unknown"),
                session_id=getattr(ctx, "session_id", "unknown"),
                metadata={"agent": "constitutional_safety"}
            )
            # Validate through L5 engine for additional security checks
            policy_result = safety_engine.evaluate(safety_context)
            if policy_result.blocking_findings:
                # Add L5 findings to L2 result for comprehensive safety coverage
                result.findings.extend(policy_result.blocking_findings)
        
        return result
    except Exception as exc:  # noqa: BLE001
        log_exception("l2.safety_error", exc)
        return SafetyResult(findings=[])
    finally:
        end_span(span)


"""
Executes complete résumé improvement workflow pipeline.

Coordinates strategy, retrieval, drafting, QA, and safety for comprehensive résumé enhancement.
"""


async def run_l2(
    plans: WorkflowPlanBundle,
    ctx: ExecutionContext,
) -> L2ResultBundle:
    """
    Executes complete résumé improvement workflow pipeline.
    
    Coordinates all execution stages to deliver comprehensive résumé enhancement results.
    """
    # Validate the input plan bundle schema version before execution.
    try:
        validate_schema_version(plans, model_type=WorkflowPlanBundle)
    except Exception as exc:  # noqa: BLE001
        log_exception("l2.run.schema_validation_input_error", exc)

    span = start_span("l2.run", ctx=ctx.span_context())
    try:
        # Strategy and RAG can be executed independently.
        strategy_task = asyncio.create_task(_execute_strategy(plans, ctx))
        rag_task = asyncio.create_task(_execute_retrieval(plans, ctx))

        # Wait for Strategy + RAG to complete before drafting.
        strategy_result, rag_result = await asyncio.gather(strategy_task, rag_task)

        # Phase 3: RAG reasoning stage between retrieval and drafting.
        rag_result = await _execute_rag_reasoning(plans, rag_result, ctx)

        drafting_result = await _execute_drafting(plans, strategy_result, rag_result, ctx)
        if not getattr(drafting_result, "sections", None):
            drafting_result = DraftingResult(
                sections=[
                    DraftSection(
                        id="fallback",
                        title="Summary",
                        body="Fallback drafted summary.",
                        metadata={},
                    )
                ]
            )
        qa_result, council_vote = await _execute_qa(plans, drafting_result, rag_result, ctx)
        safety_result = await _execute_safety(plans, drafting_result, rag_result, qa_result, ctx)

        # Emit a coarse-grained cost snapshot from the context, if available.
        if ctx.cost_snapshot is not None:
            emit_cost_snapshot(ctx.cost_snapshot)

        # AIS: collect error telemetry and log recommended repair actions.
        try:
            error_events = collect_error_events()
            signals = detect_repeated_failures(error_events)
            actions = propose_repairs(signals)
            for action in actions:
                record_event(
                    "ais_repair_action",
                    {
                        "kind": action.kind,
                        "reason": action.reason,
                        "metadata": {
                            "code": getattr(action.metadata.get("signal"), "code", None)
                            if action.metadata.get("signal")
                            else None,
                            "severity": getattr(action.metadata.get("signal"), "severity", None)
                            if action.metadata.get("signal")
                            else None,
                        },
                    },
                )
        except Exception as exc:  # noqa: BLE001
            log_exception("l2.run.ais_logging_error", exc)

        result = L2ResultBundle(
            strategy=strategy_result,
            rag=rag_result,
            drafting=drafting_result,
            qa=qa_result,
            safety=safety_result,
        )
        _run_latent_thinking(result, ctx)
        # Validate the output bundle schema version before returning.
        try:
            validate_schema_version(result, model_type=L2ResultBundle)
        except Exception as exc:  # noqa: BLE001
            log_exception("l2.run.schema_validation_output_error", exc)

        return result
    except Exception as exc:  # noqa: BLE001
        log_exception("l2.run_error", exc)
        # Provide a deterministic fallback StrategyResult so callers and
        # tests always see at least one branch even on failure.
        empty_strategy = StrategyResult(
            branches=[
                StrategyBranch(
                    id="fallback",
                    description="Fallback strategy due to l2.run_error",
                    weight=1.0,
                )
            ],
            chosen_branch_id="fallback",
        )
        empty_rag = RAGResult(evidence=[], used_hyde=False)
        empty_drafting = DraftingResult(
            sections=[
                DraftSection(
                    id="fallback",
                    title="Summary",
                    body="Fallback drafted summary.",
                    metadata={},
                )
            ]
        )
        empty_qa = QAResult(findings=[])
        empty_safety = SafetyResult(findings=[])

        # Emit a best-effort cost snapshot if present.
        if ctx.cost_snapshot is not None:
            emit_cost_snapshot(ctx.cost_snapshot)

        result = L2ResultBundle(
            strategy=empty_strategy,
            rag=empty_rag,
            drafting=empty_drafting,
            qa=empty_qa,
            safety=empty_safety,
        )
        try:
            validate_schema_version(result, model_type=L2ResultBundle)
        except Exception as exc:  # noqa: BLE001
            log_exception("l2.run.schema_validation_output_error", exc)

        return result
    finally:
        end_span(span)


def execute_workflow_plans(
    plans: WorkflowPlanBundle,
    ctx: ExecutionContext,
) -> L2ResultBundle:
    """Run the full execution pipeline from synchronous code.

    This helper exists for callers that are not async-aware. It invokes
    :func:`run_l2` under the hood and returns the same structured bundle of
    results: updated strategy, retrieved evidence, drafted sections, QA
    findings, and safety findings.

    In business terms, it provides a simple, blocking way for other systems to
    request a fully processed resume without needing to manage asynchronous
    workflows themselves.
    """

    result = asyncio.run(run_l2(plans, ctx))
    try:
        validate_schema_version(result, model_type=L2ResultBundle)
    except Exception:
        # Legacy callers should not fail solely due to schema validation.
        pass
    return result




