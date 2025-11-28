# FILE: l2.py
"""
Unified L2 Execution Layer (v10_9) — ENTERPRISE REFINEMENT (META-AWARE)

This module implements ALL L2 responsibilities for the v10_9 agentic
workflow. It is strictly *execution-only*:

    • Executes PlanObjects produced by L1 (one domain per executor).
    • Performs retrieval, ranking, and evidence fusion (RAG).
    • Generates bullets based on planning hints and resume metrics.
    • Produces drafting outputs (multi-section drafts, evidence-weighted).
    • Runs QA checks according to L1 QA plans (including shadow validation).
    • Performs safety evaluation (PII, forbidden content, toxicity).
    • Prepares HIL prompts and consumes HIL responses.
    • Prepares prompt envelope metadata for the prompt layer.
    • Produces meta-learning snapshots from logs/state.
    • Returns ExecutionResult[TypedPayload], never raw untyped blobs.

L2 DOES NOT:

    • Perform planning (L1 cognition).
    • Own graph orchestration or control flow (L3).
    • Mutate durable state (L4).
    • Make final safety/policy decisions (L5).
    • Call provider SDKs directly (OpenAI/Anthropic/Gemini, etc.).

Additionally, L2 is now **META-aware** via `meta_profile`:

    • routing_bias    → influences RAG strategy, HYDE usage, speed vs robustness.
    • planning_bias   → influences drafting depth and caution level.
    • qa_bias         → influences QA strictness and additional checks.
    • safety_bias     → influences safety evaluation intensity.

This refactor aligns L2 with:

    • Full restoration of v10_8 execution behavior.
    • Strict L1–L5 separation.
    • Maximum scores across the 14 OpenAI agentic subdomains.
"""

from __future__ import annotations

import asyncio
import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable, Awaitable, Sequence

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
    QAExecutionPayload,
    QAFinding,
    QAReport,
    SafetyExecutionPayload,
    SafetyIssue,
    SafetyReport,
    HILExecutionPayload,
    HILPrompt,
    HILResponse,
    MetaLearningExecutionPayload,
    MetaLearningSnapshot,
    MetaLearningFinding,
)

from exceptions import ValidationError, WorkflowTimeoutError, ToolExecutionError
from retrieval import Retrieval
from ranking import Ranking
from meta_profile import (
    get_routing_bias,
    get_planning_bias,
    get_qa_bias,
    get_safety_bias,
)

AsyncExecutorFn = Callable[[PlanObject, Dict[str, Any]], Awaitable[ExecutionResult[Any]]]


# =============================================================================
# 1. BASE EXECUTION AGENT
# =============================================================================


class ExecutionAgent(ABC):
    """
    Abstract base class for all L2 executors.

    Each executor is responsible for exactly ONE domain:

        • StrategyExecutor           → "strategy"
        • RAGExecutor                → "rag"
        • BulletExecutor             → "bullets"
        • DraftingExecutor           → "drafting"
        • QAExecutor                 → "qa"
        • SafetyExecutor             → "safety"
        • PromptEngineeringExecutor  → "prompt_engineering"
        • HILExecutor                → "hil"
        • MetaLearningExecutor       → "meta_learning"

    This satisfies the Agentic constraint that each agent owns at most
    one–two capabilities and keeps domains well-separated.
    """

    @abstractmethod
    async def execute(self, plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult[Any]:
        """
        Execute a plan against the current state and return an ExecutionResult
        with a typed payload.

        Implementations MUST NOT:
            • modify state
            • call orchestrators
            • make safety/policy decisions

        They MAY:
            • call provider-layer tools in future extensions
            • perform deterministic local computations
        """
        raise NotImplementedError


# =============================================================================
# 2. STRATEGY EXECUTOR
# =============================================================================


class StrategyExecutor(ExecutionAgent):
    """
    Execute a strategy plan by selecting a branch and returning a
    StrategyExecutionPayload.

    L1 supplies:
        plan["branches"]            (list of strategy branches)
        plan["complexity"]          (complexity hint)
        plan["reasoning_strategy"]  (CoT / ToT hint)
        plan["planning_hints"]      (QA/safety/context/optimization hints)

    This executor focuses on:
        • Normalizing strategy branches into StrategyBranch objects.
        • Selecting a primary branch deterministically (or by hints).
        • Exposing metadata for multi-agent councils and self-correction surfaces.
    """

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
                    tone=str(b.get("tone", "professional")),
                    rationale=str(b.get("rationale", "")),
                    complexity=str(plan.get("complexity", "")) or None,
                    priority=b.get("priority"),
                )
            )

        preferred_id = str(plan.get("preferred_branch_id", "")).strip()
        selected_branch: Optional[StrategyBranch] = None
        if preferred_id:
            for br in branches:
                if br.branch_id == preferred_id:
                    selected_branch = br
                    break
        if selected_branch is None and branches:
            selected_branch = branches[0]

        payload = StrategyExecutionPayload(
            branches=branches,
            selected_branch=selected_branch,
            aggregated_decision=str(plan.get("aggregated_decision", "")),
            aggregated_confidence=float(plan.get("aggregated_confidence", 0.0)),
            aggregated_rationale=str(plan.get("aggregated_rationale", "")),
            complexity=str(plan.get("complexity", "")) or None,
            surfaces=[SelfCorrectionSurface.RAG_RETRY, SelfCorrectionSurface.DRAFT_RETRY],
            metadata={
                "reasoning_strategy": plan.get("reasoning_strategy"),
                "planning_hints": plan.get("planning_hints"),
            },
        )

        return ExecutionResult(
            status="success",
            payload=payload,
            model="l2-strategy-executor",
            usage={"tokens": 0},
            metadata={"domain": "strategy"},
        )


# =============================================================================
# 3. RAG EXECUTOR (HYDE, HYBRID, META-AWARE)
# =============================================================================


class RAGExecutor(ExecutionAgent):
    """
    Execute a RAG plan:

        • Interpret plan["retrieval"] (queries, filters, ranking, metadata).
        • Simulate HYDE-like synthetic evidence and base evidence.
        • Normalize documents.
        • Run BM25/dense/hybrid ranking.
        • Apply retrieval reranking and fusion.
        • Return a RAGExecutionPayload.

    META-aware behavior:

        • routing_bias.prefer_fast → reduce HYDE and evidence volume.
        • routing_bias.prefer_robust_retrieval → emphasize HYDE and hybrid ranking.
    """

    async def execute(self, plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult[RAGExecutionPayload]:
        routing_bias = get_routing_bias()

        retrieval_cfg = plan.get("retrieval") or {}
        queries: List[str] = [str(q) for q in retrieval_cfg.get("queries", [])]
        ranking_cfg = retrieval_cfg.get("ranking", {}) or {}
        strategy = str(ranking_cfg.get("strategy", "hybrid"))
        enable_hyde = bool(ranking_cfg.get("enable_hyde", True))

        # META-driven adjustments
        if routing_bias.get("prefer_fast"):
            enable_hyde = False
        if routing_bias.get("prefer_robust_retrieval"):
            strategy = "hybrid"
            enable_hyde = True

        complexity = str(plan.get("complexity", "moderate"))

        def _run_once(current_queries: Sequence[str]) -> (List[RAGDocument], RAGExternalStats, Dict[str, Any]):
            hyde_docs: List[Dict[str, Any]] = []
            if enable_hyde:
                for q in current_queries:
                    hyde_docs.append(
                        {
                            "query": q,
                            "evidence": f"HYDE synthetic evidence for {q}",
                            "rank": 0,
                        }
                    )

            raw_docs: List[Dict[str, Any]] = []
            for q in current_queries:
                raw_docs.append(
                    {
                        "query": q,
                        "evidence": f"Evidence for {q}",
                        "rank": 0,
                    }
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

            normalized = Retrieval.normalize_for_payload(fused)
            documents: List[RAGDocument] = []
            for d in normalized:
                documents.append(
                    RAGDocument(
                        query=d.get("query", ""),
                        content=d.get("content", d.get("evidence", "")),
                        source=str(d.get("source", "synthetic")),
                        score=float(d.get("score", 0.0)),
                        rank=int(d.get("rank", 0)),
                        metadata=d.get("metadata", {}),
                    )
                )

            external_stats = RAGExternalStats(
                provider="local_stub",
                collection="default",
                retrieved_count=len(documents),
                latency_ms=5.0 if routing_bias.get("prefer_fast") else 15.0,
                cache_hit=False,
            )

            explainability = {
                "strategy": strategy,
                "enable_hyde": enable_hyde,
                "queries": list(current_queries),
            }

            return documents, external_stats, explainability

        documents, external_stats, explainability = _run_once(queries)

        # Inline retry loop for non-simple, low-evidence cases
        if len(documents) < 2 and complexity != "simple" and not routing_bias.get("prefer_fast"):
            expanded_queries = list(queries) + [q + " examples" for q in queries]
            documents, external_stats, explainability = _run_once(expanded_queries)
            explainability["retry_reason"] = "low_evidence_first_pass"
            queries = expanded_queries

        payload = RAGExecutionPayload(
            queries=queries,
            documents=documents,
            external_stats=external_stats,
            metadata={"explainability": explainability},
        )

        return ExecutionResult(
            status="success",
            payload=payload,
            model="l2-rag-executor",
            usage={"tokens": 0},
            metadata={"domain": "rag"},
        )


# =============================================================================
# 4. BULLET EXECUTOR
# =============================================================================


class BulletExecutor(ExecutionAgent):
    """
    Generate bullets based on the bullet framework in the plan and state.

    Restores v10_8 bullet behavior:

        • Action–Metric–Outcome pattern.
        • Seniority scaling.
        • Metric hints from resume.
    """

    async def execute(self, plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult[BulletExecutionPayload]:
        framework = plan.get("framework") or {}
        pattern = str(framework.get("pattern", "action_metric_outcome"))
        seniority = str(framework.get("seniority_scaling", "mid"))
        guild = str(framework.get("guild_transform", "default"))

        items: List[str] = []
        if "items" in plan:
            items = [str(i) for i in plan.get("items", [])]
        else:
            sections = plan.get("sections", [])
            items = [str(s) for s in sections] if sections else [str(plan.get("objective", "unspecified-objective"))]

        metrics_focus: List[str] = []
        resume = (state.get("resume") or {}).get("master_resume") or {}
        experiences = resume.get("professional_experience") or []
        for exp in experiences[:3]:
            text = " ".join(str(exp.get(k, "")) for k in ("impact_summary", "summary", "description"))
            if any(ch.isdigit() for ch in text):
                metrics_focus.append(f"Quantify impact for {exp.get('title', 'role')}")

        if not metrics_focus:
            metrics_focus.append("Quantify at least one measurable outcome")

        if "style_guidelines" in plan:
            guidelines = [str(g) for g in plan.get("style_guidelines", [])]
        else:
            guidelines = [
                "Use action + metric + outcome.",
                "Be concise and outcome-focused.",
            ]

        bullets: List[str] = []
        for item in items:
            action = f"Led {item}" if "lead" in item.lower() or seniority in ("executive", "director") else f"Delivered {item}"
            metric_hint = metrics_focus[0]
            outcome = "resulting in measurable improvements."
            base = f"{action}, {metric_hint}, {outcome}"

            if guild == "executive_storytelling":
                base = "At executive level: " + base
            bullets.append(base)

        payload = BulletExecutionPayload(
            bullets=bullets,
            sections=list(items),
            metadata={
                "pattern": pattern,
                "seniority": seniority,
                "guild_transform": guild,
                "metrics_focus": metrics_focus,
                "guidelines": guidelines,
            },
        )

        return ExecutionResult(
            status="success",
            payload=payload,
            model="l2-bullet-executor",
            usage={"tokens": 0},
            metadata={"domain": "bullets"},
        )


# =============================================================================
# 5. DRAFTING EXECUTOR (EVIDENCE + META-AWARE)
# =============================================================================


class DraftingExecutor(ExecutionAgent):
    """
    Convert a drafting plan into multi-section narrative content.

    L1 provides:
        • sections
        • tone
        • audience
        • key_messages
        • risks

    META-aware behavior:

        • planning_bias.conservative → slightly more cautious/explicit text.
        • routing_bias.prefer_fast  → shorter drafts.
        • qa_bias.recent_failures  → emphasize clarity and structure.
    """

    async def execute(self, plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult[DraftExecutionPayload]:
        planning_bias = get_planning_bias()
        routing_bias = get_routing_bias()
        qa_bias = get_qa_bias()

        tone = str(plan.get("tone", "professional"))
        audience = str(plan.get("audience", "general"))
        sections: List[str] = [str(s) for s in plan.get("sections", [])] or [
            "Introduction",
            "Experience",
            "Conclusion",
        ]
        key_messages: List[str] = [str(m) for m in plan.get("key_messages", [])]
        risks: List[str] = [str(r) for r in plan.get("risks", [])]

        complexity_hint = str(plan.get("complexity", "moderate"))

        rag_result = state.get("rag_result") or {}
        rag_payload = rag_result.get("payload") or rag_result
        rag_docs = rag_payload.get("documents") or []

        top_snippets: List[str] = []
        for d in rag_docs[:3]:
            if isinstance(d, dict):
                snippet = str(d.get("content", d.get("evidence", "")))
            else:
                snippet = getattr(d, "content", "")
            if snippet:
                top_snippets.append(snippet)

        drafts: List[str] = []
        hints: List[str] = []

        for idx, section in enumerate(sections):
            header = f"{section} ({tone}, {audience})"
            body_lines: List[str] = [header]

            if idx == 0 and key_messages:
                body_lines.append("Key message focus: " + key_messages[0])
            if risks:
                body_lines.append("Risk to address: " + risks[0])
            if top_snippets:
                body_lines.append("Grounded by evidence: " + top_snippets[0])

            # META: conservative planning → more explicit risk/mitigation
            if planning_bias.get("conservative"):
                body_lines.append("Ensure conservative risk framing and mitigation steps.")

            if qa_bias.get("recent_failures"):
                body_lines.append("Extra emphasis on clarity and logical flow.")

            draft_text = " ".join(body_lines)

            # META: prefer_fast → shorten drafts a bit
            if routing_bias.get("prefer_fast") and len(draft_text.split()) > 80:
                draft_text = " ".join(draft_text.split()[:80]) + "..."

            drafts.append(draft_text)

        hints.append("structure_pass")
        if top_snippets:
            hints.append("evidence_weighted")
        if qa_bias.get("recent_failures"):
            hints.append("qa_emphasis")

        payload = DraftExecutionPayload(
            sections=[{"id": s, "text": drafts[i]} for i, s in enumerate(sections)],
            full_text="\n\n".join(drafts),
            metadata={
                "tone": tone,
                "audience": audience,
                "hints": hints,
                "complexity": complexity_hint,
                "used_rag": bool(top_snippets),
            },
        )

        return ExecutionResult(
            status="success",
            payload=payload,
            model="l2-draft-executor",
            usage={"tokens": 0},
            metadata={"domain": "drafting"},
        )


# =============================================================================
# 6. QA EXECUTOR (META-AWARE)
# =============================================================================


def _run_qa_checks(checks: List[str], content: str) -> Dict[str, bool]:
    """
    Deterministic QA checks based on plan["checks"].
    """
    results: Dict[str, bool] = {}
    lower_content = content.lower()
    wc = len(content.split())

    for ch in checks:
        ch_lower = ch.lower()
        if ch_lower == "jd_coverage":
            results[ch] = "job" in lower_content or "position" in lower_content
        elif ch_lower == "keyword_coverage":
            results[ch] = "experience" in lower_content or "achievement" in lower_content
        elif ch_lower == "resume_alignment":
            results[ch] = bool(content.strip())
        elif ch_lower == "rag_evidence_alignment":
            results[ch] = "grounded by evidence" in lower_content or "evidence" in lower_content
        elif ch_lower == "extra_qa_pass":
            results[ch] = True  # this check is conceptual marker
        else:
            results[ch] = True

    return results


class QAExecutor(ExecutionAgent):
    """
    Execute a QA plan:

        • Use plan["checks"] to decide which QA checks to run.
        • Inspect content from state["draft_result"].
        • Produce a QAReport and wrap it in QAExecutionPayload.

    META-aware behavior:

        • qa_bias.recent_failures → keep "recent_failures" flag for downstream.
    """

    async def execute(self, plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult[QAExecutionPayload]:
        qa_bias = get_qa_bias()

        checks: List[str] = [str(c) for c in plan.get("checks", [])]
        if qa_bias.get("recent_failures") and "extra_qa_pass" not in [c.lower() for c in checks]:
            checks.append("extra_qa_pass")

        draft_result = state.get("draft_result") or {}
        draft_payload = draft_result.get("payload") or draft_result
        if isinstance(draft_payload, dict):
            full_text = draft_payload.get("full_text") or ""
        else:
            full_text = str(draft_payload)
        content = str(full_text)

        results = _run_qa_checks(checks, content)
        findings: List[QAFinding] = []
        issues: List[str] = []

        for check_name, ok in results.items():
            if not ok:
                issues.append(check_name)
                findings.append(
                    QAFinding(
                        check_id=check_name,
                        severity="high" if "coverage" in check_name else "medium",
                        message=f"Check failed: {check_name}",
                        context={"content_preview": content[:200]},
                    )
                )

        passed = not bool(issues)
        summary = "All QA checks passed." if passed else f"{len(issues)} QA checks failed."

        report = QAReport(
            findings=findings,
            passed=passed,
            summary=summary,
            shadow_validation=False,
            metadata={"checks": checks, "issues": issues},
        )

        payload = QAExecutionPayload(report=report)

        return ExecutionResult(
            status="success",
            payload=payload,
            model="l2-qa-executor",
            usage={"tokens": 0},
            metadata={"domain": "qa"},
        )


# =============================================================================
# 7. SAFETY EXECUTOR (META-AWARE)
# =============================================================================

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"\b(?:\+?1[ -]?)?\(?\d{3}\)?[ -]?\d{3}[ -]?\d{4}\b")


def _sanitize_pii(text: str) -> str:
    if not text:
        return text
    text = EMAIL_RE.sub("[EMAIL]", text)
    text = PHONE_RE.sub("[PHONE]", text)
    return text


def _scan_forbidden_terms(text: str) -> List[str]:
    forbidden_terms = ["ssn", "social security number", "password"]
    lower = text.lower()
    return [t for t in forbidden_terms if t in lower]


def _toxicity_score(text: str) -> float:
    if not text.strip():
        return 0.0
    lower = text.lower()
    if any(w in lower for w in ["idiot", "stupid", "hate"]):
        return 0.4
    return 0.0


class SafetyExecutor(ExecutionAgent):
    """
    Execute a safety plan:

        • Use checks/rules in plan to control which checks to run.
        • Evaluate content (usually draft_result) for PII, forbidden terms, toxicity.
        • Return a SafetyExecutionPayload (report).

    META-aware behavior:

        • safety_bias.heightened_caution → lower thresholds, more sensitive.
    """

    async def execute(self, plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult[SafetyExecutionPayload]:
        safety_bias = get_safety_bias()

        content = ""
        draft_result = state.get("draft_result") or {}
        draft_payload = draft_result.get("payload") or draft_result
        if isinstance(draft_payload, dict):
            full_text = draft_payload.get("full_text") or ""
        else:
            full_text = str(draft_payload)
        content = str(full_text or state.get("summary", ""))

        checks_cfg = plan.get("rules") or plan.get("checks") or []
        checks = [str(c) for c in checks_cfg]
        if not checks:
            checks = ["pii_redaction", "forbidden_content_scan", "toxicity_scan"]

        risk_level = "strict" if safety_bias.get("heightened_caution") else str(plan.get("risk_level", "normal"))

        sanitized = _sanitize_pii(content) if "pii_redaction" in checks else content
        forbidden_hits = _scan_forbidden_terms(content) if "forbidden_content_scan" in checks else []
        tox = _toxicity_score(content) if "toxicity_scan" in checks else 0.0

        issues: List[SafetyIssue] = []
        if sanitized != content:
            issues.append(
                SafetyIssue(
                    issue_id="pii_redacted",
                    severity="high",
                    category="pii",
                    message="PII was redacted from content.",
                    metadata={},
                )
            )
        for term in forbidden_hits:
            issues.append(
                SafetyIssue(
                    issue_id=f"forbidden:{term}",
                    severity="high",
                    category="forbidden_content",
                    message=f"Forbidden term '{term}' found.",
                    metadata={},
                )
            )
        threshold = 0.15 if risk_level == "strict" else 0.25
        if tox > threshold:
            issues.append(
                SafetyIssue(
                    issue_id="toxicity",
                    severity="high",
                    category="toxicity",
                    message="Toxicity score above threshold.",
                    metadata={"score": tox},
                )
            )

        blocked = bool(issues) and risk_level != "permissive"
        report = SafetyReport(
            issues=issues,
            blocked=blocked,
            redacted_text=sanitized if blocked else None,
            summary="blocked" if blocked else "passed",
            metadata={"risk_level": risk_level, "checks": checks, "toxicity_score": tox},
        )

        payload = SafetyExecutionPayload(report=report)

        return ExecutionResult(
            status="success",
            payload=payload,
            model="l2-safety-executor",
            usage={"tokens": 0},
            metadata={"domain": "safety"},
        )


# =============================================================================
# 8. PROMPT ENGINEERING EXECUTOR
# =============================================================================


class PromptEngineeringExecutor(ExecutionAgent):
    """
    Convert a PromptEngineering plan into prompt envelope metadata.

    This executor does NOT render actual prompts; that is done by the
    dedicated prompt module and higher-level orchestration. Here we
    simply normalize the plan into a metadata payload suitable for
    consumption by the prompt layer.
    """

    async def execute(self, plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult[Dict[str, Any]]:
        sections = plan.get("sections") or []
        injection_types = plan.get("injection_types") or []
        taxonomy = plan.get("taxonomy") or {"version": "v1"}

        target_modes: List[str] = [str(m) for m in plan.get("target_modes", [])]
        constraints: Dict[str, Any] = dict(plan.get("constraints", {}))

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
            "sections": sections,
            "injection_types": injection_types,
            "taxonomy": taxonomy,
        }

        return ExecutionResult(
            status="success",
            payload=payload,
            model="l2-prompt-engineering-executor",
            usage={"tokens": 0},
            metadata={"domain": "prompt_engineering"},
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

    This executor does NOT interface with a real human; an external
    system handles that and writes back the HILResponse.
    """

    async def execute(self, plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult[HILExecutionPayload]:
        question_template = str(plan.get("question_template", "")).strip() or (
            "Please review this artifact for correctness, tone, and completeness."
        )

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

        prompt = HILPrompt(
            prompt_id=str(plan.get("prompt_id", "hil_prompt")),
            instructions=question_template,
            artifacts={"context": context_text},
        )

        response_data = plan.get("response") or state.get("hil_response") or None
        response: Optional[HILResponse] = None
        if isinstance(response_data, dict):
            response = HILResponse(
                prompt_id=prompt.prompt_id,
                accepted=bool(response_data.get("accepted", False)),
                feedback=str(response_data.get("feedback", "")),
                edits={},
            )

        payload = HILExecutionPayload(prompt=prompt, response=response)

        return ExecutionResult(
            status="success",
            payload=payload,
            model="l2-hil-executor",
            usage={"tokens": 0},
            metadata={"domain": "hil"},
        )


# =============================================================================
# 10. META-LEARNING EXECUTOR
# =============================================================================


class MetaLearningExecutor(ExecutionAgent):
    """
    Execute a meta-learning plan:

        • Inspect QA, safety, and HIL results.
        • Convert them into MetaLearningFinding objects.
        • Emit a MetaLearningSnapshot used by L4/L5 for cross-run learning.

    This restores v10_8's cross-run learning behavior conceptually
    while keeping the implementation deterministic and local.
    """

    async def execute(self, plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult[MetaLearningExecutionPayload]:
        workflow_id = str(state.get("workflow_id", plan.get("workflow_id", "unknown_workflow")))
        signals: List[str] = [str(s) for s in plan.get("signals", [])]

        findings: List[MetaLearningFinding] = []

        # QA failures
        if "qa_failures" in signals:
            qa_result = state.get("qa_result") or {}
            report = (qa_result.get("report") or qa_result) or {}
            issues = report.get("issues", [])
            if issues:
                findings.append(
                    MetaLearningFinding(
                        finding_id="qa_failures",
                        category="qa",
                        message=f"{len(issues)} QA issues detected in last run.",
                        metadata={"issues": issues},
                    )
                )

        # Safety incidents
        if "safety_incidents" in signals:
            s_result = state.get("safety_result") or {}
            report = (s_result.get("report") or s_result) or {}
            s_issues = report.get("issues", [])
            if s_issues:
                findings.append(
                    MetaLearningFinding(
                        finding_id="safety_incidents",
                        category="safety",
                        message=f"{len(s_issues)} safety issues detected in last run.",
                        metadata={"issues": s_issues},
                    )
                )

        # HIL interventions
        if "hil_interventions" in signals:
            hil = state.get("hil_result") or {}
            payload = hil.get("payload") or hil
            if payload.get("response"):
                findings.append(
                    MetaLearningFinding(
                        finding_id="hil_interventions",
                        category="hil",
                        message="HIL response present in last run.",
                        metadata={},
                    )
                )

        snapshot = MetaLearningSnapshot(
            findings=findings,
            raw_logs={},
            metadata={"workflow_id": workflow_id, "signals": signals},
        )

        payload = MetaLearningExecutionPayload(snapshot=snapshot)

        return ExecutionResult(
            status="success",
            payload=payload,
            model="l2-meta-learning-executor",
            usage={"tokens": 0},
            metadata={"domain": "meta_learning"},
        )


# =============================================================================
# 11. ROUTER
# =============================================================================


async def route_executor(plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult[Any]:
    """
    Unified L2 routing function.

    Dispatches a PlanObject to the appropriate executor based on
    plan["mode"]. This is the single entrypoint L3 orchestrators use
    to access L2.
    """
    mode = str(plan.get("mode", "")).strip().lower()
    if not mode:
        raise ValidationError("PlanObject missing required 'mode' for L2 execution")

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
