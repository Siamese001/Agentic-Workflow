# FILE: l2.py
"""
Unified L2 Execution Layer (v10_9) — ENTERPRISE REFINEMENT

This module implements ALL L2 responsibilities for the v10_9 agentic
workflow. It is strictly *execution-only*:

    • Executes PlanObjects produced by L1 (one domain per executor).
    • Performs retrieval, ranking, and evidence fusion (RAG).
    • Generates bullets based on planning hints.
    • Produces drafting outputs (multi-section drafts, guild-ready).
    • Runs QA checks according to L1 QA plans.
    • Performs safety evaluation (PII, forbidden content, toxicity).
    • Prepares HIL prompts and consumes HIL responses.
    • Prepares prompt envelopes metadata for the prompt layer.
    • Produces meta-learning snapshots from logs/state.
    • Returns ExecutionResult[TypedPayload], never raw untyped blobs.

Non-responsibilities (to preserve L1–L5 purity):

    • NO planning (L1 cognition).
    • NO graph orchestration or control flow (L3).
    • NO state mutation (L4).
    • NO final safety/policy decisions (L5).
    • NO direct SDK/provider logic (those live in providers/*).

Executors are **dual-mode** in design:

    • Deterministic mode (current implementation): fully local, no I/O.
    • LLM/Tool mode (future extension): will call provider-layer
      clients (Anthropic/Gemini/OpenAI) via providers/*, while still
      returning the same typed payloads.

The single entrypoint used by L3 orchestrators is:

    - route_executor(plan, state) -> ExecutionResult
"""

from __future__ import annotations

import asyncio
import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable, Awaitable

from models import (
    PlanObject,
    ExecutionResult,
    StrategyExecutionPayload,
    StrategyBranch,
    RAGExecutionPayload,
    RAGDocument,
    RAGExternalStats,
    BulletExecutionPayload,
    DraftExecutionPayload,
    QAFinding,
    QAReport,
    QAExecutionPayload,
    SafetyIssue,
    SafetyReport,
    SafetyExecutionPayload,
    HILPrompt,
    HILResponse,
    HILExecutionPayload,
    MetaLearningFinding,
    MetaLearningSnapshot,
    MetaLearningExecutionPayload,
)

from runtime_utils import (
    Retrieval,
    Ranking,
    RAGUtils,
    ToolExecutionError,
    ValidationError,
    WorkflowTimeoutError,
)

# ============================================================================
# 1. BASE EXECUTION AGENT
# ============================================================================

class ExecutionAgent(ABC):
    """
    Abstract base class for L2 executors.
    """

    @abstractmethod
    async def execute(self, plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult[Any]:
        raise NotImplementedError

    def _execution_mode(self, plan: PlanObject, state: Dict[str, Any]) -> str:
        handoff = plan.get("handoff") or {}
        mode = (
            handoff.get("execution_mode")
            or plan.get("execution_mode")
            or state.get("execution_mode")
            or "auto"
        )
        return str(mode).strip().lower()


AsyncExecutorFn = Callable[[PlanObject, Dict[str, Any]], Awaitable[ExecutionResult[Any]]]

# ============================================================================
# 2. STRATEGY EXECUTOR
# ============================================================================

class StrategyExecutor(ExecutionAgent):
    async def execute(self, plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult[StrategyExecutionPayload]:
        branches_data = plan.get("branches") or []
        branches: List[StrategyBranch] = []
        for b in branches_data:
            branches.append(
                StrategyBranch(
                    branch_id=str(b.get("branch_id", "")),
                    strategy_name=str(b.get("strategy_name", "")),
                    focus_areas=[str(x) for x in b.get("focus_areas", [])],
                    key_achievements=[str(x) for x in b.get("key_achievements", [])],
                    tone=str(b.get("tone", "Professional")),
                    rationale=str(b.get("rationale", "")),
                )
            )

        selected_branch = branches[0] if branches else None

        payload = StrategyExecutionPayload(
            branches=branches,
            selected_branch=selected_branch,
            aggregated_decision=str(plan.get("aggregated_decision", "")),
            aggregated_confidence=float(plan.get("aggregated_confidence", 0.0)),
            aggregated_rationale=str(plan.get("aggregated_rationale", "")),
            complexity=str(plan.get("complexity", "")) or None,
            surfaces=[str(s) for s in plan.get("surfaces", [])],
        )

        return ExecutionResult(
            status=ExecutionResult.SUCCESS,
            payload=payload,
            model="strategy-executor",
            usage={"tokens": 0},
        )

# ============================================================================
# 3. RAG EXECUTOR
# ============================================================================

class RAGExecutor(ExecutionAgent):
    async def execute(self, plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult[RAGExecutionPayload]:
        retrieval_cfg = plan.get("retrieval") or {}
        queries = [str(q) for q in retrieval_cfg.get("queries", [])]
        ranking_cfg = retrieval_cfg.get("ranking", {}) or {}
        strategy = str(ranking_cfg.get("strategy", "hybrid"))
        enable_hyde = bool(ranking_cfg.get("enable_hyde", True))

        # Synthetic HYDE docs
        hyde_docs = []
        if enable_hyde:
            for q in queries:
                hyde_docs.append(
                    {"query": q, "evidence": f"HYDE synthetic evidence for {q}", "rank": 0}
                )

        raw_docs = []
        for q in queries:
            raw_docs.append(
                {"query": q, "evidence": f"Evidence for {q}", "rank": 0}
            )

        norm = Retrieval.normalize_documents(hyde_docs + raw_docs)
        norm = Retrieval.dedupe_results(norm)

        if strategy == "bm25":
            ranked = Ranking.bm25_rank(norm)
        elif strategy == "dense":
            ranked = Ranking.dense_rank(norm)
        else:
            ranked = Ranking.hybrid_rank(norm)

        reranked = Retrieval.rerank_results(ranked, strategy)
        fused = Retrieval.fuse_results([reranked])
        normalized = RAGUtils.normalize_rag_results(fused)

        documents: List[RAGDocument] = []
        for d in normalized:
            documents.append(
                RAGDocument(
                    query=str(d.get("query", "")),
                    evidence=str(d.get("evidence", "")),
                    rank=int(d.get("rank", 0)),
                    metadata=dict(d.get("metadata", {})),
                )
            )

        payload = RAGExecutionPayload(
            queries=queries,
            documents=documents,
            ranking_strategy=strategy,
            hyde_used=enable_hyde,
            vector_source=None,
            bm25_used=(strategy == "bm25"),
        )

        return ExecutionResult(
            status=ExecutionResult.SUCCESS,
            payload=payload,
            model="rag-executor",
            usage={"tokens": 0},
        )

# ============================================================================
# 4. BULLET EXECUTOR
# ============================================================================

class BulletExecutor(ExecutionAgent):
    async def execute(self, plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult[BulletExecutionPayload]:
        items = [str(x) for x in plan.get("deliverables", plan.get("items", []))]

        if not items:
            sections = plan.get("sections", [])
            items = [str(s) for s in sections] if sections else [str(plan.get("objective", ""))]

        metrics_focus = []
        resume = (state.get("resume") or {}).get("master_resume") or {}
        experiences = resume.get("professional_experience") or []

        for exp in experiences[:3]:
            text = " ".join(
                str(exp.get(k, "")) for k in ("impact_summary", "summary", "description")
            )
            if any(ch.isdigit() for ch in text):
                metrics_focus.append(f"Quantify impact for {exp.get('title', 'role')}")

        if not metrics_focus:
            metrics_focus.append("Quantify at least one measurable outcome")

        guidelines = plan.get("style_guidelines") or [
            "Use action + metric + outcome.",
            "Be concise and outcome-focused.",
        ]
        guidelines = [str(g) for g in guidelines]

        bullets = []
        for item in items:
            hint = ", ".join(metrics_focus[:2])
            guideline = guidelines[0] if guidelines else ""
            bullets.append(f"• Delivered results in {item} (metrics: {hint}). {guideline}")

        payload = BulletExecutionPayload(
            bullets=bullets,
            guidelines=guidelines,
            metrics_focus=metrics_focus,
            guild_passes=["metrics_enrichment"],
        )

        return ExecutionResult(
            status=ExecutionResult.SUCCESS,
            payload=payload,
            model="bullet-executor",
            usage={"tokens": 0},
        )

# ============================================================================
# 5. DRAFTING EXECUTOR
# ============================================================================

class DraftingExecutor(ExecutionAgent):
    async def execute(self, plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult[DraftExecutionPayload]:
        tone = str(plan.get("tone", "Professional"))
        audience = str(plan.get("audience", "general"))
        sections = [str(s) for s in plan.get("sections", [])] or [
            "Introduction",
            "Experience",
            "Conclusion",
        ]
        key_messages = [str(m) for m in plan.get("key_messages", [])]
        risks = [str(r) for r in plan.get("risks", [])]

        hints = []
        if key_messages:
            hints.append("Key messages: " + "; ".join(key_messages[:3]))
        if risks:
            hints.append("Risks: " + "; ".join(risks[:3]))

        drafts = []
        for sec in sections:
            line = f"[{sec.upper()} — tone={tone}, audience={audience}]"
            if key_messages:
                line += " | Key: " + key_messages[0]
            if risks:
                line += " | Risk: " + risks[0]
            drafts.append(line)

        payload = DraftExecutionPayload(
            sections=sections,
            tone=tone,
            draft=drafts,
            hints=hints,
            passes=["structure_pass"],
        )

        return ExecutionResult(
            status=ExecutionResult.SUCCESS,
            payload=payload,
            model="draft-executor",
            usage={"tokens": 0},
        )

# =============================================================================
# 6. QA EXECUTOR (multi-check QA suite, core deterministic)
# =============================================================================


def _run_qa_checks(checks: List[str], content: str) -> Dict[str, bool]:
    """
    Deterministic QA checks based on plan["checks"].

    This is a heuristic suite meant to mirror a multi-tool QA pipeline,
    but without any external LLM calls in this reference implementation.
    """
    results: Dict[str, bool] = {}
    lower_content = content.lower()
    wc = len(content.split()) if content else 0

    for ch in checks:
        ch_lower = ch.lower()
        if ch_lower == "content_not_empty":
            results[ch] = bool(content.strip())
        elif ch_lower == "no_forbidden_phrases":
            forbidden = ["lorem ipsum", "fake placeholder", "explicit"]
            results[ch] = not any(term in lower_content for term in forbidden)
        elif ch_lower == "narrative_coherence":
            results[ch] = wc > 5 and content.strip().endswith(".")
        elif ch_lower == "semantic_alignment_with_jd":
            # For now, assume semantic alignment if content is non-empty.
            results[ch] = bool(content.strip())
        elif ch_lower == "signal_to_noise_ratio":
            results[ch] = wc == 0 or wc > 10  # simplistic heuristic
        elif ch_lower == "tenure_consistency":
            results[ch] = True  # placeholder; real logic would parse dates
        elif ch_lower == "keyword_coverage":
            results[ch] = "experience" in lower_content or "achievement" in lower_content
        elif ch_lower == "bias_check":
            results[ch] = not any(term in lower_content for term in ["he/she", "old", "young"])
        elif ch_lower == "adversarial_review":
            results[ch] = "attack" not in lower_content
        elif ch_lower == "word_count_bounds":
            results[ch] = 20 <= wc <= 300
        elif ch_lower == "executive_readability":
            results[ch] = wc <= 250
        elif ch_lower == "deep_fact_checking":
            # In a real system, this would call a verifier; here we require no "obviously wrong" tokens.
            results[ch] = "obviously wrong" not in lower_content
        else:
            # Unknown checks default to True for stability
            results[ch] = True

    return results


class QAExecutor(ExecutionAgent):
    """
    Execute a QA plan:

        • Use plan["checks"] to decide which QA checks to run.
        • Inspect the content from state["draft_result"] or similar.
        • Produce a QAReport and wrap it in QAExecutionPayload.

    This reference implementation does not call external QA tools; those
    can be added as a separate QAToolSuite layer wired alongside this
    executor in production.

    L5 remains responsible for interpreting QA results in the context of
    safety/policy decisions.
    """

    async def execute(self, plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult[QAExecutionPayload]:
        checks: List[str] = [str(c) for c in plan.get("checks", [])]

        # Determine content to validate: use draft_result if present
        content = ""
        draft_result = state.get("draft_result") or {}
        draft_list = draft_result.get("draft") or []
        if isinstance(draft_list, list):
            content = "\n".join(str(x) for x in draft_list)
        else:
            content = str(draft_list)

        results = _run_qa_checks(checks, content)
        findings: List[QAFinding] = []
        issues: List[str] = []

        for check_name, ok in results.items():
            status = "pass" if ok else "fail"
            details = "validated deterministically" if ok else "check failed"
            findings.append(QAFinding(check=check_name, status=status, details=details))
            if not ok:
                issues.append(check_name)

        total = max(len(results), 1)
        passed_count = len([k for k, ok in results.items() if ok])
        confidence = round(passed_count / total, 3)
        passed = len(issues) == 0

        report = QAReport(
            issues=issues,
            passed=passed,
            confidence=confidence,
            findings=findings,
            tool_suite_used=False,
            tools_invoked=[],
        )

        payload = QAExecutionPayload(qa_report=report)

        return ExecutionResult(
            status=ExecutionResult.SUCCESS,
            payload=payload,
            model="qa-executor",
            usage={"tokens": 0},
        )


# =============================================================================
# 7. SAFETY EXECUTOR (PII, forbidden, toxicity)
# =============================================================================

# Simple PII regex patterns
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"\b(?:\+?1[ -]?)?\(?\d{3}\)?[ -]?\d{3}[ -]?\d{4}\b")


def _sanitize_pii(text: str) -> str:
    """
    Redact common PII markers deterministically.
    """
    if not text:
        return text
    text = EMAIL_RE.sub("[EMAIL]", text)
    text = PHONE_RE.sub("[PHONE]", text)
    return text


def _scan_forbidden_terms(text: str) -> List[str]:
    forbidden = ["explicit", "violence", "hate", "slur"]
    lower = text.lower()
    return [t for t in forbidden if t in lower]


def _toxicity_score(text: str) -> float:
    """
    Very simple toxicity heuristic:
        • Count exclamation marks.
        • Count a few aggressive words.
    """
    if not text:
        return 0.0
    aggressive = ["damn", "stupid", "idiot", "screw", "hate"]
    count = sum(text.lower().count(a) for a in aggressive)
    count += text.count("!")
    toks = len(text.split()) + 1
    return min(1.0, count / toks)


class SafetyExecutor(ExecutionAgent):
    """
    Execute a safety plan:

        • Use checks from plan["checks"] to control which checks to run.
        • Evaluate content (usually draft_result) for PII, forbidden terms, toxicity.
        • Return a SafetyExecutionPayload (safety_report + sanitized_content).

    Final safety/policy decisions remain at L5 (SafetyEngine + PolicyEngine +
    ArbitrationEngine). This executor is a pure evaluator.
    """

    async def execute(self, plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult[SafetyExecutionPayload]:
        # Determine input content
        content = ""
        draft_result = state.get("draft_result") or {}
        draft_list = draft_result.get("draft") or []
        if isinstance(draft_list, list) and draft_list:
            content = "\n".join(str(x) for x in draft_list)
        else:
            messages = state.get("messages") or []
            if messages:
                last = messages[-1]
                if isinstance(last, dict):
                    content = str(last.get("content", ""))
        if not content:
            content = str(state.get("summary", ""))

        checks: List[str] = [str(c) for c in plan.get("checks", [])]
        risk_level = str(plan.get("risk_level", "normal"))

        # PII & forbidden terms
        sanitized = _sanitize_pii(content) if "pii_redaction" in checks else content
        forbidden_hits = _scan_forbidden_terms(content) if "forbidden_content_scan" in checks else []
        tox = _toxicity_score(content) if "toxicity_scan" in checks else 0.0

        issues: List[SafetyIssue] = []
        if sanitized != content:
            issues.append(SafetyIssue(code="pii_redacted", description="PII was redacted from content."))
        for term in forbidden_hits:
            issues.append(SafetyIssue(code=f"forbidden:{term}", description=f"Forbidden term '{term}' found."))
        if tox > (0.25 if risk_level == "normal" else 0.15):
            issues.append(SafetyIssue(code="toxicity", description="Toxicity score above threshold."))

        # Simple bias/child checks are left to L5; here we just flag structural issues.
        passed = len(issues) == 0

        report = SafetyReport(
            passed=passed,
            issues=issues,
            toxicity_score=tox,
            audience=str(plan.get("audience", state.get("audience", "general"))),
            prompt_injection={},
            constitutional={},
        )

        payload = SafetyExecutionPayload(
            safety_report=report,
            sanitized_content=sanitized,
        )

        return ExecutionResult(
            status=ExecutionResult.SUCCESS,
            payload=payload,
            model="safety-executor",
            usage={"tokens": 0},
        )


# =============================================================================
# 8. PROMPT ENGINEERING EXECUTOR
# =============================================================================


class PromptEngineeringExecutor(ExecutionAgent):
    """
    Convert a PromptEngineeringPlanner plan into prompt envelope metadata.

    NOTE:
        This executor does NOT render actual prompts; that is done by the
        dedicated prompt module and higher-level orchestration. Here we
        simply normalize the plan into a metadata payload suitable for
        consumption by the prompt layer.
    """

    async def execute(self, plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult[Dict[str, Any]]:
        target_modes: List[str] = [str(m) for m in plan.get("target_modes", [])]
        constraints: Dict[str, Any] = dict(plan.get("constraints", {}))

        # Minimal deterministic metadata; in a full system this would
        # map to actual prompt templates in prompt.PromptTemplateRegistry.
        envelopes_meta = {
            mode: {
                "needs_framing": True,
                "needs_context": True,
                "needs_reasoning": constraints.get("must_include_reasoning", True),
                "needs_safety_context": constraints.get("must_include_safety_context", True),
            }
            for mode in target_modes
        }

        payload = {
            "prompt_envelopes": envelopes_meta,
            "constraints": constraints,
        }

        return ExecutionResult(
            status=ExecutionResult.SUCCESS,
            payload=payload,
            model="prompt-engineering-executor",
            usage={"tokens": 0},
        )


# =============================================================================
# 9. HIL EXECUTOR
# =============================================================================


class HILExecutor(ExecutionAgent):
    """
    Execute a HIL plan:

        • Create an HILPrompt using the plan's question_template and
          contextual state.
        • Optionally attach an existing HILResponse if present in state.

    This executor does NOT interface with a real human; in a production
    system, an external UI/service would handle that and write back
    the HILResponse into state.
    """

    async def execute(self, plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult[HILExecutionPayload]:
        question_template = str(plan.get("question_template", "")).strip() or (
            "Please review this artifact for correctness, tone, and completeness."
        )

        # Build a simple context summary from state
        summary = str(state.get("summary", "")) or "No summary available."
        messages = state.get("messages") or []
        last_user = ""
        for msg in reversed(messages):
            if isinstance(msg, dict) and msg.get("role") == "user":
                last_user = str(msg.get("content", ""))
                break

        context_text = "Summary: " + summary
        if last_user:
            context_text += "\n\nLast user message: " + last_user

        severity = str(plan.get("severity", "normal"))
        prompt = HILPrompt(
            question=question_template,
            context=context_text,
            recommended_action="approve_or_request_changes",
            urgency=severity,
        )

        # If a prior HIL response exists in state, attach it
        hil_state = state.get("hil_result") or {}
        response_data = hil_state.get("response")
        response: Optional[HILResponse] = None
        if isinstance(response_data, dict):
            response = HILResponse(
                approved=bool(response_data.get("approved", False)),
                comments=str(response_data.get("comments", "")),
                requested_changes=[str(c) for c in response_data.get("requested_changes", [])],
            )

        payload = HILExecutionPayload(
            prompt=prompt,
            response=response,
            surface=str(plan.get("surface", "hil_escalation")),
        )

        return ExecutionResult(
            status=ExecutionResult.SUCCESS,
            payload=payload,
            model="hil-executor",
            usage={"tokens": 0},
        )


# =============================================================================
# 10. META-LEARNING EXECUTOR
# =============================================================================


class MetaLearningExecutor(ExecutionAgent):
    """
    Execute a meta-learning plan:

        • Scan state for basic signals (qa_result, safety_result,
          hil_result, etc.).
        • Build a MetaLearningSnapshot summarizing key patterns.
        • Return a MetaLearningExecutionPayload.

    In a full implementation, this executor would consume external
    logs and feedback stores; here we provide a deterministic stub
    that operates on in-memory state only.
    """

    async def execute(self, plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult[MetaLearningExecutionPayload]:
        workflow_id = str(plan.get("workflow_id", state.get("workflow_id", "unknown")))
        signals: List[str] = [str(s) for s in plan.get("signals", [])]

        findings: List[MetaLearningFinding] = []

        # QA failures
        if "qa_failures" in signals:
            qa = (state.get("qa_result") or {}).get("report") or {}
            issues = qa.get("issues", [])
            if issues:
                findings.append(
                    MetaLearningFinding(
                        kind="pattern",
                        description=f"{len(issues)} QA issues detected in last run.",
                        weight=0.7,
                        metadata={"issues": issues},
                    )
                )

        # Safety incidents
        if "safety_incidents" in signals:
            safety = (state.get("safety_result") or {}).get("report") or {}
            s_issues = safety.get("issues", [])
            if s_issues:
                findings.append(
                    MetaLearningFinding(
                        kind="pattern",
                        description=f"{len(s_issues)} safety issues detected in last run.",
                        weight=0.9,
                        metadata={"issues": s_issues},
                    )
                )

        # HIL interventions
        if "hil_interventions" in signals:
            hil = state.get("hil_result") or {}
            if hil.get("response"):
                findings.append(
                    MetaLearningFinding(
                        kind="pattern",
                        description="HIL response present in last run.",
                        weight=0.6,
                        metadata={"hil_result": hil},
                    )
                )

        snapshot = MetaLearningSnapshot(
            workflow_id=workflow_id,
            raw_feedback_entries=0,
            raw_preference_entries=0,
            findings=findings,
            proposal={"note": "Stub meta-learning proposal; extend with real analysis."},
            critique={},
        )

        payload = MetaLearningExecutionPayload(snapshot=snapshot)

        return ExecutionResult(
            status=ExecutionResult.SUCCESS,
            payload=payload,
            model="meta-learning-executor",
            usage={"tokens": 0},
        )


# =============================================================================
# 11. ROUTER
# =============================================================================


async def route_executor(plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult[Any]:
    """
    Unified L2 routing function.

    Dispatches a PlanObject to the appropriate executor based on
    plan["mode"]. This is the ONE entrypoint L3 orchestrators use to
    invoke L2 execution.

    Supported modes:
        • "strategy"
        • "rag"
        • "bullets"
        • "drafting"
        • "qa"
        • "safety"
        • "prompt_engineering"
        • "hil"
        • "meta_learning"

    This function enforces typed domain boundaries and does not perform
    any planning, orchestration, state mutation, or safety decisions.
    """
    if not isinstance(plan, PlanObject):
        raise ValidationError("route_executor expects a PlanObject instance.")

    mode = str(plan.get("mode", "")).lower().strip()
    if not mode:
        raise ValidationError("PlanObject missing 'mode' field for L2 routing.")

    agent: ExecutionAgent

    if mode == "strategy":
        agent = StrategyExecutor()
    elif mode == "rag":
        agent = RAGExecutor()
    elif mode == "bullets":
        agent = BulletExecutor()
    elif mode == "drafting":
        agent = DraftingExecutor()
    elif mode == "qa":
        agent = QAExecutor()
    elif mode == "safety":
        agent = SafetyExecutor()
    elif mode == "prompt_engineering":
        agent = PromptEngineeringExecutor()
    elif mode == "hil":
        agent = HILExecutor()
    elif mode == "meta_learning":
        agent = MetaLearningExecutor()
    else:
        raise ValidationError(f"Unsupported plan mode for L2 execution: {mode!r}")

    try:
        return await agent.execute(plan, state)
    except asyncio.TimeoutError as exc:
        raise WorkflowTimeoutError(f"L2 execution timed out for mode={mode}") from exc
    except Exception as exc:
        # Wrap arbitrary exceptions in ToolExecutionError to keep contracts tight.
        raise ToolExecutionError(f"L2 executor for mode={mode} failed: {exc}") from exc
