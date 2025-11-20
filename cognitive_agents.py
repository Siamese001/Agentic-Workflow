# FILE: cognitive_agents.py
"""
Unified Cognitive Agents (v10_10) — INTELLIGENT PERSONAS

This module hosts ALL LLM-based cognition for v10_10:

    1. StrategyLLMAgent
       - Tree-of-Thought strategy generation
       - Branch selection

    2. DraftingGuild
       - Structure specialist (outline)
       - Narrative specialist (content)
       - Compliance specialist (critique)

    3. SemanticQAAgent
       - Semantic QA over draft + evidence

    4. ConstitutionalSafetyAgent
       - Constitutional safety checks (PII, policy, professionalism)

Design constraints:
    - No high-level orchestration (L3).
    - No state mutation (L4).
    - No policy decisions (L5).
    - All model calls via runtime_utils.invoke_model().
    - All prompts fetched from registry.PromptRegistry.

This file is imported by L2; L1 must NEVER call these agents directly.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import json

from models import (
    JobInput,
    ResumeInput,
    WorkflowConfig,
    ComplexityLevel,
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


# =============================================================================
# Base LLM Agent
# =============================================================================


@dataclass
class LLMBaseAgent:
    """
    Base class for all cognitive LLM agents.

    Dependencies (DI):
        - routing_policy: model selection logic
        - meta_profile:   historical signals (may be None)
        - prompt_registry:central prompt governance
        - sandbox:        execution sandbox config
    """

    routing_policy: RoutingPolicy
    meta_profile: Optional[Any]
    prompt_registry: PromptRegistry
    sandbox: SandboxConfig

    def _call_llm(self, prompt_id: str, variables: Dict[str, Any]) -> str:
        """
        Render a prompt and call the routed LLM.

        Expects PromptRegistry.get_prompt(prompt_id) to return a bundle with:
            - .render(variables) -> str
            - .temperature
            - .max_tokens
        """
        bundle = self.prompt_registry.get_prompt(prompt_id)
        rendered = bundle.render(variables)

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
# 1. StrategyLLMAgent (ToT)
# =============================================================================


class StrategyLLMAgent(LLMBaseAgent):
    """
    Strategy agent performing Tree-of-Thought exploration and branch selection.
    """

    def run_strategy(self, plan: StrategyPlan, ctx) -> StrategyResult:
        """
        Generate multiple strategy branches and select a winner.
        """
        branches: List[StrategyBranch] = []

        num_branches = self.routing_policy.strategy_branches_for(plan.complexity)
        for i in range(num_branches):
            text = self._call_llm(
                "strategy_generate_branch",
                {
                    "job": ctx.job.model_dump(),
                    "resume": ctx.resume.model_dump(),
                    "plan": plan.model_dump(),
                    "complexity": plan.complexity.value,
                    "branch_index": i,
                },
            )
            branches.append(StrategyBranch(id=f"branch_{i}", text=text))

        judge = self._call_llm(
            "strategy_select_branch",
            {
                "job": ctx.job.model_dump(),
                "resume": ctx.resume.model_dump(),
                "branches": [b.text for b in branches],
                "complexity": plan.complexity.value,
            },
        )

        chosen_idx = 0
        try:
            chosen_idx = int(judge.strip())
        except Exception:
            chosen_idx = 0

        chosen_idx = max(0, min(chosen_idx, len(branches) - 1))

        record_event(
            "strategy_branch_selected",
            {"chosen_index": chosen_idx, "total_branches": len(branches)},
        )

        return StrategyResult(
            branches=branches,
            chosen_branch_id=branches[chosen_idx].id,
        )


# =============================================================================
# 2. DraftingGuild (Structure → Narrative → Compliance)
# =============================================================================


class DraftingGuild(LLMBaseAgent):
    """
    Multi-specialist drafting pipeline:

        • Structure specialist: defines outline & section structure.
        • Narrative specialist: writes section text.
        • Compliance specialist: reviews and annotates sections.

    All are implemented via prompts; this class orchestrates them *within L2*.
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
        # 1. Structure Specialist: propose JSON structure for sections
        chosen_strategy_text = strategy_result.get_chosen_branch_text()
        struct_raw = self._call_llm(
            "drafting_structure",
            {
                "job": job.model_dump(),
                "resume": resume.model_dump(),
                "drafting_plan": drafting_plan.model_dump(),
                "strategy_branch": chosen_strategy_text,
                "rag_evidence": [e.text for e in rag_result.evidence],
            },
        )
        sections = self._parse_structure(struct_raw, drafting_plan)

        # 2. Narrative Specialist: write content per section
        for section in sections:
            narrative_text = self._call_llm(
                "drafting_narrative",
                {
                    "job": job.model_dump(),
                    "resume": resume.model_dump(),
                    "drafting_plan": drafting_plan.model_dump(),
                    "section": section.title,
                    "outline": section.outline,
                },
            )
            section.text = narrative_text

        # 3. Compliance Specialist: annotate each section
        for section in sections:
            compliance_notes = self._call_llm(
                "drafting_compliance",
                {
                    "drafting_plan": drafting_plan.model_dump(),
                    "section_title": section.title,
                    "section_text": section.text,
                    "target_tone": drafting_plan.target_tone,
                },
            )
            section.compliance_notes = compliance_notes

        record_event(
            "drafting_guild_completed",
            {"num_sections": len(sections), "mode": drafting_plan.mode.value},
        )

        return DraftingResult(
            sections=sections,
            mode=drafting_plan.mode,
        )

    # -------------------------------------------------------------------------
    # Helper: parse structure JSON
    # -------------------------------------------------------------------------

    def _parse_structure(
        self, struct_text: str, plan: DraftingPlan
    ) -> List[DraftSectionResult]:
        """
        Interpret the structure specialist output as JSON.

        Expected format:
            [
              {"title": "...", "outline": "..."},
              ...
            ]

        Fallback: if not JSON, treat each line as a section title.
        """
        try:
            raw = json.loads(struct_text)
        except Exception:
            lines = [l.strip() for l in struct_text.splitlines() if l.strip()]
            raw = [{"title": line, "outline": ""} for line in lines]

        sections: List[DraftSectionResult] = []
        for entry in raw:
            title = entry.get("title", "Untitled Section")
            outline = entry.get("outline", "")
            sections.append(
                DraftSectionResult(
                    title=title,
                    outline=outline,
                    text="",
                    compliance_notes="",
                )
            )

        return sections


# =============================================================================
# 3. SemanticQAAgent
# =============================================================================


class SemanticQAAgent(LLMBaseAgent):
    """
    Semantic QA Agent.

    Evaluates each QACheck in QAPlan against:
        - the current DraftingResult
        - RAG evidence
        - job/resume inputs
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
            result = self._parse_qa_result(raw, check.id)
            results.append(result)

        record_event(
            "qa_semantic_completed",
            {
                "num_checks": len(qa_plan.checks),
                "num_failed": sum(1 for r in results if not r.passed),
            },
        )
        return QAResult(checks=results)

    def _parse_qa_result(self, raw: str, check_id: str) -> QACheckResult:
        """
        Parse LLM QA JSON into QACheckResult.
        """
        try:
            data = json.loads(raw)
            return QACheckResult(
                id=check_id,
                passed=bool(data.get("passed", False)),
                reason=str(data.get("reason", "")),
                severity=int(data.get("severity", 1)),
            )
        except Exception:
            record_event("qa_semantic_malformed_json", {"check_id": check_id})
            return QACheckResult(
                id=check_id,
                passed=False,
                reason="Malformed QA JSON from model",
                severity=3,
            )


# =============================================================================
# 4. ConstitutionalSafetyAgent
# =============================================================================


class ConstitutionalSafetyAgent(LLMBaseAgent):
    """
    Constitutional Safety Agent.

    Evaluates the draft for:
        - PII exposure
        - Disallowed / risky content (policy)
        - Professionalism issues
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
            finding = self._parse_safety_result(raw, check.id)
            findings.append(finding)

        record_event(
            "safety_constitutional_completed",
            {
                "num_findings": len(findings),
                "num_blocking": sum(1 for f in findings if f.blocking),
            },
        )
        return SafetyResult(findings=findings)

    def _parse_safety_result(self, raw: str, check_id: str) -> SafetyFinding:
        """
        Parse LLM safety JSON into SafetyFinding.
        """
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
                reason="Malformed safety JSON from model",
            )
