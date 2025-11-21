# FILE: 10_10/cognitive_agents.py
"""
Unified Cognitive Agents (v10_10 · Phase 3)
===========================================

This module implements ALL LLM-based cognition for the v10_10 workflow.

L2 is the only layer allowed to call these agents.

Agents (L2 cognition only):
    • StrategyLLMAgent            – strategy reasoning
    • DraftingGuild              – resume drafting
    • SemanticQAAgent            – QA reasoning + RAG reasoning
    • ConstitutionalSafetyAgent  – safety / policy review

Design constraints:
    • Only this module may invoke LLMs.
    • No planning (L1), orchestration (L3), state mutation (L4),
      or safety policy enforcement (L5).
    • All calls use PromptInstance + ACL from prompt_builder.
    • All model selection goes through RoutingPolicy.
    • All LLM calls go through runtime_utils.invoke_model.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence

from models import (
    StrategyResult,
    StrategyBranch,
    RAGResult,
    DraftingResult,
    DraftSection,
    QAResult,
    QAFinding,
    SafetyResult,
    SafetyFinding,
    Evidence,
)
from routing import RoutingPolicy
from runtime_utils import invoke_model, SandboxConfig
from observability import record_event, record_exception
from meta_profile import MetaProfileSnapshot
from prompt_builder import (
    PromptInstance,
    build_strategy_prompt,
    build_drafting_prompt,
    build_rag_prompt,
    build_qa_prompt,
    build_safety_prompt,
)


# =============================================================================
# Local prompt context
# =============================================================================


@dataclass
class _PromptContext:
    """
    Lightweight context object passed to prompt_builder.

    We intentionally avoid depending on models.ExecutionContext here;
    prompt_builder only needs job, resume, config, which we expose
    directly.
    """

    job: Any
    resume: Any
    config: Any


# =============================================================================
# Base LLM Agent
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
        meta = prompt.definition.metadata or {}
        llm_meta = meta.get("llm", {}) or {}
        temperature = float(llm_meta.get("temperature", 0.2))
        max_tokens = int(llm_meta.get("max_tokens", 1024))

        record_event(
            "llm_call_start",
            {
                "prompt_id": prompt.prompt_id,
                "layer": prompt.layer,
                "agent": prompt.agent,
                "model_tier": prompt.model_tier,
                "temperature": temperature,
                "max_tokens": max_tokens,
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
            return text or ""
        except Exception as exc:
            record_exception("llm_call_failure", exc)
            raise


# =============================================================================
# Strategy LLM Agent
# =============================================================================


class StrategyLLMAgent(LLMBaseAgent):
    """
    Strategy cognition for the workflow.

    Phase 3 implementation:
        • Uses a single, envelope-based strategy prompt.
        • Returns a StrategyResult with one chosen branch.
    """

    async def run_strategy(
        self,
        strategy_plan: Any,
        job: Any,
        resume: Any,
        config: Any,
    ) -> StrategyResult:
        """
        Asynchronous entrypoint used by L2.
        """
        ctx = _PromptContext(job=job, resume=resume, config=config)

        prompt = build_strategy_prompt(
            plan=strategy_plan,
            ctx=ctx,
            layer="L2",
            agent="strategy",
            model_tier="balanced",
        )

        raw = self._call_llm(prompt).strip()

        # For now we treat the entire output as a single branch.
        branch = StrategyBranch(id="branch_0", text=raw or "")

        record_event(
            "strategy_completed",
            {
                "num_branches": 1,
                "chosen_branch_id": branch.id,
                "complexity": getattr(strategy_plan, "complexity", None),
            },
        )

        return StrategyResult(branches=[branch], chosen_branch_id=branch.id)


# =============================================================================
# Drafting Guild
# =============================================================================


class DraftingGuild(LLMBaseAgent):
    """
    Drafting agent that turns strategy + evidence into resume content.

    Phase 3 implementation:
        • Uses a single drafting prompt envelope per call.
        • Emits a DraftingResult with at least one DraftSection.
        • Parsing is robust to both JSON and free-form text output.
    """

    async def run_drafting(
        self,
        drafting_plan: Any,
        job: Any,
        resume: Any,
        strategy_result: StrategyResult,
        rag_result: RAGResult,
        config: Any,
    ) -> DraftingResult:
        ctx = _PromptContext(job=job, resume=resume, config=config)

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
                "mode": getattr(getattr(drafting_plan, "mode", None), "value", str(getattr(drafting_plan, "mode", ""))),
            },
        )

        return DraftingResult(sections=sections)

    def _parse_drafting_output(self, raw: str, plan: Any) -> List[DraftSection]:
        """
        Parse drafting output into DraftSection objects.

        Heuristics:

            1) If the output is JSON and looks like a list of sections:
                   [{"title": "...", "text": "..."}]
               we map each element to a DraftSection.

            2) Otherwise, treat the entire text as a single section whose
               title is taken from the first planned section title if available.
        """
        if not raw:
            title = ""
            if getattr(plan, "sections", None):
                title = getattr(plan.sections[0], "title", "") or ""
            return [
                DraftSection(
                    id="section_0",
                    title=title or "Resume",
                    text="",
                    metadata={},
                )
            ]

        # Try JSON path.
        try:
            data = json.loads(raw)
            if isinstance(data, list):
                sections: List[DraftSection] = []
                for idx, entry in enumerate(data):
                    if not isinstance(entry, dict):
                        continue
                    title = str(entry.get("title") or f"Section {idx+1}")
                    text = str(entry.get("text") or "")
                    sections.append(
                        DraftSection(
                            id=f"section_{idx}",
                            title=title,
                            text=text,
                            metadata={},
                        )
                    )
                if sections:
                    return sections
        except Exception:
            record_event("drafting_non_json_output", {})

        # Fallback: single-section wrapping of free-form text.
        title = ""
        if getattr(plan, "sections", None):
            title = getattr(plan.sections[0], "title", "") or ""
        return [
            DraftSection(
                id="section_0",
                title=title or "Resume",
                text=raw.strip(),
                metadata={},
            )
        ]


# =============================================================================
# Semantic QA Agent (QA + RAG reasoning)
# =============================================================================


class SemanticQAAgent(LLMBaseAgent):
    """
    QA agent that evaluates drafted content and performs RAG reasoning.

    Outputs:
        • QAResult with structured QAFinding items.
        • RAG reasoning text for Phase-3 reasoning stage.
    """

    async def run_qa(
        self,
        qa_plan: Any,
        draft: DraftingResult,
        rag: RAGResult,
        job: Any,
        resume: Any,
        config: Any,
    ) -> QAResult:
        ctx = _PromptContext(job=job, resume=resume, config=config)

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

        findings = self._parse_qa_output(raw, qa_plan)

        record_event(
            "qa_completed",
            {
                "num_findings": len(findings),
                "num_high_severity": sum(1 for f in findings if f.severity.lower() == "high"),
            },
        )

        return QAResult(findings=findings)

    async def run_rag_reasoning(
        self,
        prompt: PromptInstance,
        evidence: Sequence[Evidence],
        job: Any,
        resume: Any,
        config: Any,
    ) -> str:
        """
        Phase-3 RAG reasoning.

        L2 passes a pre-built RAG prompt; this method simply calls the LLM
        and returns the reasoning text. L2 turns this into a synthetic
        Evidence item.
        """
        raw = self._call_llm(prompt)
        text = (raw or "").strip()

        record_event(
            "rag_reasoning_completed",
            {
                "prompt_id": prompt.prompt_id,
                "evidence_count": len(list(evidence or [])),
                "text_len": len(text),
            },
        )
        return text

    def _parse_qa_output(self, raw: str, qa_plan: Any) -> List[QAFinding]:
        """
        Parse QA output into QAFinding items.

        If JSON parsing fails, we fall back to a single generic finding.
        """
        if not raw:
            return [
                QAFinding(
                    id="generic",
                    category="qa",
                    severity="high",
                    message="No QA output produced",
                    metadata={},
                )
            ]

        # JSON path: expect list of objects with id / severity / message / category.
        try:
            data = json.loads(raw)
            if not isinstance(data, list):
                raise ValueError("QA output must be a JSON list")

            findings: List[QAFinding] = []
            for item in data:
                if not isinstance(item, dict):
                    continue
                fid = str(
                    item.get("id")
                    or item.get("check_id")
                    or "unknown"
                )
                severity = str(item.get("severity", "medium"))
                category = str(item.get("category", "qa"))
                message = str(item.get("message", ""))
                metadata = item.get("details") or item.get("metadata") or {}

                findings.append(
                    QAFinding(
                        id=fid,
                        category=category,
                        severity=severity,
                        message=message,
                        metadata=metadata,
                    )
                )

            if findings:
                return findings
        except Exception:
            record_event("qa_malformed_json", {})

        # Fallback: generic finding containing the raw text.
        return [
            QAFinding(
                id="generic",
                category="qa",
                severity="medium",
                message=raw.strip(),
                metadata={},
            )
        ]


# =============================================================================
# Constitutional Safety Agent
# =============================================================================


class ConstitutionalSafetyAgent(LLMBaseAgent):
    """
    Safety agent that performs final safety / policy checks.

    Output is a SafetyResult with structured SafetyFinding items.
    """

    async def run_safety(
        self,
        safety_plan: Any,
        draft: DraftingResult,
        qa_result: QAResult,
        job: Any,
        resume: Any,
        config: Any,
    ) -> SafetyResult:
        ctx = _PromptContext(job=job, resume=resume, config=config)

        prompt = build_safety_prompt(
            plan=safety_plan,
            ctx=ctx,
            qa=qa_result,
            layer="L5",
            agent="safety",
            model_tier="balanced",
        )

        raw = self._call_llm(prompt)

        findings = self._parse_safety_output(raw, safety_plan)

        record_event(
            "safety_completed",
            {
                "num_findings": len(findings),
                "num_high_severity": sum(1 for f in findings if f.severity.lower() == "high"),
            },
        )

        return SafetyResult(findings=findings)

    def _parse_safety_output(self, raw: str, safety_plan: Any) -> List[SafetyFinding]:
        """
        Parse safety output into SafetyFinding items.

        If JSON parsing fails, we fall back to conservative "blocked" findings.
        """
        # If nothing returned, treat as blocked.
        if not raw:
            checks = getattr(safety_plan, "checks", []) or []
            if not checks:
                return [
                    SafetyFinding(
                        check_id="generic",
                        category="safety",
                        severity="high",
                        message="No safety output produced",
                        details={},
                    )
                ]

            return [
                SafetyFinding(
                    check_id=getattr(chk, "id", "unknown"),
                    category="safety",
                    severity="high",
                    message="No safety output produced",
                    details={},
                )
                for chk in checks
            ]

        try:
            data = json.loads(raw)
            if not isinstance(data, list):
                raise ValueError("Safety output must be a JSON list")

            findings: List[SafetyFinding] = []
            checks = getattr(safety_plan, "checks", []) or []
            by_id = {getattr(chk, "id", ""): chk for chk in checks}

            for item in data:
                if not isinstance(item, dict):
                    continue
                cid = str(item.get("check_id") or item.get("id") or "")
                if not cid:
                    cid = "unknown"

                # Unknown check ids are still allowed but logged.
                if checks and cid not in by_id:
                    record_event("safety_unknown_check_id", {"check_id": cid})

                severity = str(item.get("severity", "high"))
                category = str(item.get("category", "safety"))
                message = str(item.get("message", ""))
                details = item.get("details") or {}

                findings.append(
                    SafetyFinding(
                        check_id=cid,
                        category=category,
                        severity=severity,
                        message=message,
                        details=details,
                    )
                )

            if findings:
                return findings
        except Exception:
            record_event("safety_malformed_json", {})

        # Fallback: generic blocked finding.
        return [
            SafetyFinding(
                check_id="generic",
                category="safety",
                severity="high",
                message="Malformed safety JSON output",
                details={},
            )
        ]
