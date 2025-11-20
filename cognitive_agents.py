# FILE: 10_10/cognitive_agents.py
"""
Unified Cognitive Agents (v10_10 · Phase 2)
===========================================

This module implements ALL LLM-based cognition for the v10_10 workflow.

L2 is the only layer allowed to call these agents.

Four agents are defined (L2 cognition only):
    • StrategyLLMAgent            – strategy reasoning
    • DraftingGuild              – resume drafting
    • SemanticQAAgent            – QA reasoning
    • ConstitutionalSafetyAgent  – safety / policy review

Phase 2 changes:
    • All LLM calls go through the Phase-2 prompt system:
          – prompt_builder.build_*_prompt()
          – prompt_system_v10_10 / registry ACLs
    • No inline prompt strings.
    • Prompt ACLs (layers / agents / model tiers) enforced in prompt_builder.
    • Prompt envelopes provide deterministic multi-section context.
    • L1/L3/L4/L5 remain pure – no LLM calls outside this module.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import json

from models import (
    JobInput,
    ResumeInput,
    WorkflowConfig,
    ExecutionContext,
    StrategyPlan,
    StrategyBranch,
    StrategyResult,
    RAGResult,
    DraftingPlan,
    DraftSectionResult,
    DraftingResult,
    QAPlan,
    QACheckResult,
    QAResult,
    SafetyPlan,
    SafetyFinding,
    SafetyResult,
)
from routing import RoutingPolicy
from runtime_utils import invoke_model, SandboxConfig
from observability import record_event, record_exception
from meta_profile import MetaProfileSnapshot
from prompt_builder import (
    PromptInstance,
    build_strategy_prompt,
    build_drafting_prompt,
    build_qa_prompt,
    build_safety_prompt,
)


# =============================================================================
# Base LLM Agent (shared invocation logic)
# =============================================================================


@dataclass
class LLMBaseAgent:
    """
    Base class for all v10_10 cognitive agents.

    Responsibilities:
        • Take a PromptInstance from prompt_builder.
        • Select the concrete model via RoutingPolicy.
        • Invoke the model via runtime_utils.invoke_model.
        • Emit basic observability events.

    This class must remain **L2-only** and must not perform:
        • planning (L1),
        • orchestration / retries (L3),
        • state mutation (L4),
        • safety policy enforcement (L5).
    """

    routing_policy: RoutingPolicy
    sandbox: SandboxConfig
    meta_profile: Optional[MetaProfileSnapshot] = None

    def _call_llm(self, prompt: PromptInstance) -> str:
        """
        Execute a single LLM call for the given prompt instance.
        """
        # Derive an optional complexity hint for routing from the plan.
        complexity = None
        plan = prompt.variables.get("plan")
        if plan is not None and hasattr(plan, "complexity"):
            # StrategyPlan, DraftingPlan, etc. may expose a complexity attribute.
            complexity = getattr(plan, "complexity", None)

        # Select the concrete model.
        try:
            model = self.routing_policy.select_model(
                task=prompt.prompt_id,
                complexity=complexity,
                meta_profile=self.meta_profile,
            )
        except Exception as exc:
            record_exception("llm_model_select_failure", exc)
            raise

        # Derive LLM parameters from prompt metadata (with safe fallbacks).
        llm_meta = prompt.definition.metadata.get("llm", {})
        temperature = float(llm_meta.get("temperature", 0.2))
        max_tokens = int(llm_meta.get("max_tokens", 1024))

        record_event(
            "llm_call_start",
            {
                "prompt_id": prompt.prompt_id,
                "layer": prompt.layer,
                "agent": prompt.agent,
                "model_tier": prompt.model_tier,
            },
        )

        try:
            text = invoke_model(
                model=model,
                prompt=prompt.rendered,
                sandbox=self.sandbox,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            record_event(
                "llm_call_success",
                {
                    "prompt_id": prompt.prompt_id,
                    "layer": prompt.layer,
                    "agent": prompt.agent,
                    "model": model,
                },
            )
            return text
        except Exception as exc:
            record_exception("llm_call_failure", exc)
            raise


# =============================================================================
# Strategy LLM Agent
# =============================================================================


class StrategyLLMAgent(LLMBaseAgent):
    """
    Strategy cognition for the workflow.

    Phase 2 implementation:
        • Uses a single, envelope-based strategy prompt.
        • Returns a StrategyResult with one chosen branch.
        • Tree-of-Thought fan-out can be reintroduced in a later phase by
          simply looping over build_strategy_prompt() and _call_llm().
    """

    def run_strategy(self, plan: StrategyPlan, ctx: ExecutionContext) -> StrategyResult:
        # Build the Phase-2 strategy prompt instance.
        prompt = build_strategy_prompt(
            plan=plan,
            ctx=ctx,
            layer="L2",
            agent="strategy",
            model_tier="balanced",
        )

        raw = self._call_llm(prompt)

        # For now we treat the entire output as a single branch.
        branch = StrategyBranch(id="branch_0", text=raw or "")

        record_event(
            "strategy_completed",
            {
                "num_branches": 1,
                "chosen_branch_id": branch.id,
                "complexity": getattr(plan, "complexity", None),
            },
        )

        return StrategyResult(branches=[branch], chosen_branch_id=branch.id)


# =============================================================================
# Drafting Guild
# =============================================================================


class DraftingGuild(LLMBaseAgent):
    """
    Drafting agent that turns strategy + evidence into resume content.

    Phase 2 implementation:
        • Uses a single drafting prompt envelope per call.
        • Emits a DraftingResult with at least one section.
        • Parsing is robust to both JSON and free-form markdown output.
    """

    def run_drafting(
        self,
        drafting_plan: DraftingPlan,
        job: JobInput,
        resume: ResumeInput,
        strategy_result: StrategyResult,
        rag_result: RAGResult,
        config: WorkflowConfig,
    ) -> DraftingResult:

        # Construct a minimal ExecutionContext for the builder.
        ctx = ExecutionContext(
            job=job,
            resume=resume,
            config=config,
            routing_policy=self.routing_policy,
            sandbox_config=self.sandbox,
            prompt_registry=None,
            cache_manager=None,
            meta_profile_snapshot=self.meta_profile,
        )

        prompt = build_drafting_prompt(
            plan=drafting_plan,
            ctx=ctx,
            strategy=strategy_result,
            rag=rag_result,
            layer="L2",
            agent="drafting",
            model_tier="balanced",
        )

        raw = self._call_llm(prompt)

        sections = self._parse_drafting_output(raw, drafting_plan)

        record_event(
            "drafting_completed",
            {
                "num_sections": len(sections),
                "mode": getattr(drafting_plan.mode, "value", str(drafting_plan.mode)),
            },
        )

        return DraftingResult(sections=sections, mode=drafting_plan.mode)

    # ------------------------------------------------------------------ #
    # Parsing helpers
    # ------------------------------------------------------------------ #

    def _parse_drafting_output(
        self,
        raw: str,
        plan: DraftingPlan,
    ) -> List[DraftSectionResult]:
        """
        Parse drafting output into DraftSectionResult objects.

        The parser is intentionally tolerant:

            1) If the output is JSON, expect a list of objects:
                   [{"title": "...", "text": "...", "outline": "..."}]
            2) Otherwise, treat the entire text as a single section whose
               title is taken from the first planned section (if any).
        """
        if not raw:
            return [
                DraftSectionResult(
                    title=(plan.sections[0].title if plan.sections else "Main"),
                    outline="",
                    text="",
                    compliance_notes="",
                )
            ]

        # Attempt JSON path first.
        try:
            data = json.loads(raw)
            if isinstance(data, list):
                sections: List[DraftSectionResult] = []
                for idx, entry in enumerate(data):
                    title = entry.get("title") or (
                        plan.sections[idx].title if idx < len(plan.sections) else f"Section {idx+1}"
                    )
                    sections.append(
                        DraftSectionResult(
                            title=title,
                            outline=str(entry.get("outline", "")),
                            text=str(entry.get("text", "")),
                            compliance_notes=str(entry.get("compliance_notes", "")),
                        )
                    )
                if sections:
                    return sections
        except Exception:
            record_event("drafting_non_json_output", {})

        # Fallback: single-section wrapping of free-form text.
        title = plan.sections[0].title if plan.sections else "Main"
        return [
            DraftSectionResult(
                title=title,
                outline="",
                text=raw.strip(),
                compliance_notes="",
            )
        ]


# =============================================================================
# Semantic QA Agent
# =============================================================================


class SemanticQAAgent(LLMBaseAgent):
    """
    QA agent that evaluates drafted content against QAPlan checks.

    Output is a QAResult with structured QACheckResult items.
    """

    def run_qa(
        self,
        qa_plan: QAPlan,
        draft: DraftingResult,
        rag: RAGResult,
        job: JobInput,
        resume: ResumeInput,
        config: WorkflowConfig,
    ) -> QAResult:

        # Build a local ExecutionContext for the builder.
        ctx = ExecutionContext(
            job=job,
            resume=resume,
            config=config,
            routing_policy=self.routing_policy,
            sandbox_config=self.sandbox,
            prompt_registry=None,
            cache_manager=None,
            meta_profile_snapshot=self.meta_profile,
        )

        prompt = build_qa_prompt(
            plan=qa_plan,
            ctx=ctx,
            drafting=draft,
            rag=rag,
            layer="L3",
            agent="qa",
            model_tier="balanced",
        )

        raw = self._call_llm(prompt)

        findings = self._parse_qa(raw, qa_plan)

        record_event(
            "qa_completed",
            {
                "num_checks": len(findings),
                "num_errors": sum(1 for f in findings if f.status == "error"),
                "num_warnings": sum(1 for f in findings if f.status == "warning"),
            },
        )

        return QAResult(findings=findings, summary="")

    # ------------------------------------------------------------------ #
    # Parsing helpers
    # ------------------------------------------------------------------ #

    def _parse_qa(self, raw: str, qa_plan: QAPlan) -> List[QACheckResult]:
        """
        Parse QA output.

        Expected (happy path) format:

            [
              {"check_id": "...", "status": "ok|warning|error", "message": "...", "details": {...}},
              ...
            ]

        Fallback:
            • On malformed JSON, return one "error" entry per check with a generic message.
        """
        if not raw:
            return [
                QACheckResult(
                    check_id=chk.id,
                    status="error",
                    message="No QA output produced",
                    details={},
                )
                for chk in qa_plan.checks
            ]

        try:
            data = json.loads(raw)
            if not isinstance(data, list):
                raise ValueError("QA output must be a JSON list")

            findings: List[QACheckResult] = []
            by_id = {chk.id: chk for chk in qa_plan.checks}

            for item in data:
                check_id = str(item.get("check_id") or item.get("id") or "")
                if not check_id or check_id not in by_id:
                    # Skip unknown checks, but record an event.
                    record_event("qa_unknown_check_id", {"check_id": check_id})
                    continue
                status = str(item.get("status", "error"))
                message = str(item.get("message", ""))
                details = item.get("details") or {}
                findings.append(
                    QACheckResult(
                        check_id=check_id,
                        status=status,
                        message=message,
                        details=details,
                    )
                )

            if findings:
                return findings
        except Exception:
            record_event("qa_malformed_json", {})

        # Fallback: generic error for each configured check.
        return [
            QACheckResult(
                check_id=chk.id,
                status="error",
                message="Malformed QA JSON output",
                details={},
            )
            for chk in qa_plan.checks
        ]


# =============================================================================
# Constitutional Safety Agent
# =============================================================================


class ConstitutionalSafetyAgent(LLMBaseAgent):
    """
    Safety agent that performs final safety / policy checks.

    Output is a SafetyResult with structured SafetyFinding items.
    """

    def run_safety(
        self,
        safety_plan: SafetyPlan,
        draft: DraftingResult,
        qa_result: QAResult,
        job: JobInput,
        resume: ResumeInput,
        config: WorkflowConfig,
    ) -> SafetyResult:

        # Build a local ExecutionContext for the builder.
        ctx = ExecutionContext(
            job=job,
            resume=resume,
            config=config,
            routing_policy=self.routing_policy,
            sandbox_config=self.sandbox,
            prompt_registry=None,
            cache_manager=None,
            meta_profile_snapshot=self.meta_profile,
        )

        prompt = build_safety_prompt(
            plan=safety_plan,
            ctx=ctx,
            qa=qa_result,
            layer="L5",
            agent="safety",
            model_tier="balanced",
        )

        raw = self._call_llm(prompt)

        findings = self._parse_safety(raw, safety_plan)

        # Derive an overall status.
        overall_status = "ok"
        if any(f.status == "blocked" for f in findings):
            overall_status = "blocked"
        elif any(f.status == "warning" for f in findings):
            overall_status = "warning"

        record_event(
            "safety_completed",
            {
                "num_findings": len(findings),
                "overall_status": overall_status,
            },
        )

        return SafetyResult(findings=findings, overall_status=overall_status)

    # ------------------------------------------------------------------ #
    # Parsing helpers
    # ------------------------------------------------------------------ #

    def _parse_safety(self, raw: str, safety_plan: SafetyPlan) -> List[SafetyFinding]:
        """
        Parse safety output.

        Expected (happy path) format:

            [
              {"id": "...", "status": "ok|blocked|warning", "message": "...", "details": {...}},
              ...
            ]

        Fallback:
            • On malformed JSON, return one "blocked" entry per check.
        """
        if not raw:
            return [
                SafetyFinding(
                    id=chk.id,
                    status="blocked",
                    message="No safety output produced",
                    details={},
                )
                for chk in safety_plan.checks
            ]

        try:
            data = json.loads(raw)
            if not isinstance(data, list):
                raise ValueError("Safety output must be a JSON list")

            findings: List[SafetyFinding] = []
            by_id = {chk.id: chk for chk in safety_plan.checks}

            for item in data:
                check_id = str(item.get("id") or item.get("check_id") or "")
                if not check_id or check_id not in by_id:
                    record_event("safety_unknown_check_id", {"check_id": check_id})
                    continue

                status = str(item.get("status", "blocked"))
                message = str(item.get("message", ""))
                details = item.get("details") or {}

                findings.append(
                    SafetyFinding(
                        id=check_id,
                        status=status,
                        message=message,
                        details=details,
                    )
                )

            if findings:
                return findings
        except Exception:
            record_event("safety_malformed_json", {})

        # Fallback: generic blocked finding per check.
        return [
            SafetyFinding(
                id=chk.id,
                status="blocked",
                message="Malformed safety JSON output",
                details={},
            )
            for chk in safety_plan.checks
        ]
