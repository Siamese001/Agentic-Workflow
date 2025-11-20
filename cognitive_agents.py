# FILE: 10_10/cognitive_agents.py
"""
Unified Cognitive Agents (v10_10) — Intelligent Personas
========================================================

This module implements ALL LLM-based cognition for the v10_10 workflow.

L2 is the only layer allowed to call these agents.

Four agents are defined:
    • StrategyLLMAgent            (Tree-of-Thought planning)
    • DraftingGuild              (Structure → Narrative → Compliance)
    • SemanticQAAgent            (Semantic QA reasoning)
    • ConstitutionalSafetyAgent  (Policy / PII / Harm content review)

Each agent:
    - Receives RoutingPolicy (model selection)
    - Receives PromptRegistry (prompt templates)
    - Receives SandboxConfig (safe execution constraints)
    - Receives MetaProfileSnapshot (optional)
    - Calls LLMs ONLY via runtime_utils.invoke_model()

This file contains ZERO:
    - planning (L1 does that)
    - orchestration (L3)
    - state persistence (L4)
    - policy decisions (L5)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import json

from models import (
    JobInput,
    ResumeInput,
    WorkflowConfig,
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
from registry import PromptRegistry
from routing import RoutingPolicy
from runtime_utils import invoke_model, SandboxConfig
from observability import record_event, record_exception
from meta_profile import MetaProfileSnapshot


# =============================================================================
# Base LLM Agent
# =============================================================================

@dataclass
class LLMBaseAgent:
    """
    Base class for all 10_10 cognitive agents.
    Contains no agent-specific logic — only:
        • routing
        • prompt rendering
        • LLM invocation
        • observability
    """

    routing_policy: RoutingPolicy
    meta_profile: Optional[MetaProfileSnapshot]
    prompt_registry: PromptRegistry
    sandbox: SandboxConfig

    def _call_llm(self, prompt_id: str, variables: Dict[str, Any]) -> str:
        """
        Render a prompt and call the correct LLM.

        variables is a dict of primitives or JSON-serializable objects.
        """
        bundle = self.prompt_registry.get_prompt(prompt_id)
        rendered = bundle.render(variables)

        # Choose model.
        model = self.routing_policy.select_model(
            task=prompt_id,
            complexity=variables.get("complexity"),
            meta_profile=self.meta_profile,
        )

        try:
            text = invoke_model(
                model=model,
                prompt=rendered,
                sandbox=self.sandbox,
                temperature=bundle.temperature,
                max_tokens=bundle.max_tokens,
            )
            return text
        except Exception as exc:
            record_exception("llm_call_failure", exc)
            raise


# =============================================================================
# Strategy LLM Agent (Tree-of-Thought)
# =============================================================================

class StrategyLLMAgent(LLMBaseAgent):
    """
    Generate multiple candidate strategy branches and select a winner.
    """

    def run_strategy(self, plan: StrategyPlan, ctx) -> StrategyResult:
        branches: List[StrategyBranch] = []

        num_branches = self.routing_policy.strategy_branches_for(plan.complexity)
        for idx in range(num_branches):
            raw_branch = self._call_llm(
                "strategy_generate_branch",
                {
                    "job": ctx.job.model_dump(),
                    "resume": ctx.resume.model_dump(),
                    "plan": plan.model_dump(),
                    "complexity": plan.complexity.value,
                    "branch_index": idx,
                },
            )
            branches.append(StrategyBranch(id=f"branch_{idx}", text=raw_branch))

        judge_raw = self._call_llm(
            "strategy_select_branch",
            {
                "job": ctx.job.model_dump(),
                "resume": ctx.resume.model_dump(),
                "branches": [b.text for b in branches],
                "complexity": plan.complexity.value,
            },
        )

        # Attempt parse of chosen index
        try:
            chosen_idx = int(judge_raw.strip())
            chosen_idx = max(0, min(chosen_idx, len(branches) - 1))
        except Exception:
            chosen_idx = 0

        record_event(
            "strategy_branch_selected",
            {"chosen_index": chosen_idx, "total_branches": len(branches)},
        )

        return StrategyResult(
            branches=branches,
            chosen_branch_id=branches[chosen_idx].id,
        )


# =============================================================================
# Drafting Guild (Structure → Narrative → Compliance)
# =============================================================================

class DraftingGuild(LLMBaseAgent):
    """
    Three-phase drafting pipeline:
        1. Structure Specialist  → section outline
        2. Narrative Specialist  → write content
        3. Compliance Specialist → critique content
    """

    def run_drafting(
        self,
        drafting_plan: DraftingPlan,
        job: JobInput,
        resume: ResumeInput,
        strategy_result,
        rag_result: RAGResult,
        config: WorkflowConfig,
    ) -> DraftingResult:

        chosen_strat_text = strategy_result.get_chosen_branch_text()

        # ----------------------------
        # 1. Structure Specialist
        # ----------------------------
        struct_raw = self._call_llm(
            "drafting_structure",
            {
                "job": job.model_dump(),
                "resume": resume.model_dump(),
                "drafting_plan": drafting_plan.model_dump(),
                "strategy_branch": chosen_strat_text,
                "rag_evidence": [e.text for e in rag_result.evidence],
            },
        )

        sections = self._parse_structure(struct_raw, drafting_plan)

        # ----------------------------
        # 2. Narrative Specialist
        # ----------------------------
        for sec in sections:
            narrative = self._call_llm(
                "drafting_narrative",
                {
                    "job": job.model_dump(),
                    "resume": resume.model_dump(),
                    "drafting_plan": drafting_plan.model_dump(),
                    "section": sec.title,
                    "outline": sec.outline,
                },
            )
            sec.text = narrative

        # ----------------------------
        # 3. Compliance Specialist
        # ----------------------------
        for sec in sections:
            notes = self._call_llm(
                "drafting_compliance",
                {
                    "drafting_plan": drafting_plan.model_dump(),
                    "section_title": sec.title,
                    "section_text": sec.text,
                    "target_tone": drafting_plan.target_tone,
                },
            )
            sec.compliance_notes = notes

        record_event(
            "drafting_guild_completed",
            {"num_sections": len(sections), "mode": drafting_plan.mode.value},
        )

        return DraftingResult(sections=sections, mode=drafting_plan.mode)

    # -----------------------------------------------------------------
    # Parse structure specialist JSON
    # -----------------------------------------------------------------

    def _parse_structure(self, raw: str, plan: DraftingPlan) -> List[DraftSectionResult]:
        """
        Expected output:
            [
              {"title": "...", "outline": "..."},
              ...
            ]
        If not JSON, treat lines as titles.
        """
        try:
            data = json.loads(raw)
        except Exception:
            # fallback: one title per non-empty line
            lines = [l.strip() for l in raw.splitlines() if l.strip()]
            data = [{"title": line, "outline": ""} for line in lines]

        sections: List[DraftSectionResult] = []
        for entry in data:
            sections.append(
                DraftSectionResult(
                    title=entry.get("title", "Untitled Section"),
                    outline=entry.get("outline", ""),
                    text="",
                    compliance_notes="",
                )
            )
        return sections


# =============================================================================
# Semantic QA Agent
# =============================================================================

class SemanticQAAgent(LLMBaseAgent):
    """
    Evaluate each QACheck in QAPlan via semantic reasoning.
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

        results: List[QACheckResult] = []

        for check in qa_plan.checks:
            raw = self._call_llm(
                "qa_semantic_check",
                {
                    "check": check.model_dump(),
                    "draft": draft.model_dump(),
                    "rag_evidence": [e.text for e in rag.evidence],
                    "job": job.model_dump(),
                    "resume": resume.model_dump(),
                },
            )
            results.append(self._parse_qa(raw, check.id))

        record_event(
            "qa_semantic_completed",
            {
                "num_checks": len(results),
                "num_failed": sum(1 for r in results if not r.passed),
            },
        )

        return QAResult(checks=results)

    def _parse_qa(self, raw: str, check_id: str) -> QACheckResult:
        try:
            data = json.loads(raw)
            return QACheckResult(
                id=check_id,
                passed=bool(data.get("passed", False)),
                reason=str(data.get("reason", "")),
                severity=int(data.get("severity", 1)),
            )
        except Exception:
            record_event("qa_malformed_json", {"check_id": check_id})
            return QACheckResult(
                id=check_id,
                passed=False,
                reason="Malformed QA JSON",
                severity=3,
            )


# =============================================================================
# Constitutional Safety Agent
# =============================================================================

class ConstitutionalSafetyAgent(LLMBaseAgent):
    """
    Evaluate content for:
        • PII leakage
        • Harmful / disallowed content
        • Professionalism issues
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

        findings: List[SafetyFinding] = []

        for check in safety_plan.checks:
            raw = self._call_llm(
                "safety_check",
                {
                    "check": check.model_dump(),
                    "draft": draft.model_dump(),
                    "qa": qa_result.model_dump(),
                    "job": job.model_dump(),
                    "resume": resume.model_dump(),
                },
            )
            findings.append(self._parse_safety(raw, check.id))

        record_event(
            "safety_constitutional_completed",
            {
                "num_findings": len(findings),
                "num_blocking": sum(1 for f in findings if f.blocking),
            },
        )

        return SafetyResult(findings=findings)

    def _parse_safety(self, raw: str, check_id: str) -> SafetyFinding:
        try:
            data = json.loads(raw)
            return SafetyFinding(
                id=check_id,
                category=str(data.get("category", "")),
                blocking=bool(data.get("blocking", False)),
                reason=str(data.get("reason", "")),
            )
        except Exception:
            record_event("safety_malformed_json", {"check_id": check_id})
            return SafetyFinding(
                id=check_id,
                category="unknown",
                blocking=True,
                reason="Malformed safety JSON",
            )
