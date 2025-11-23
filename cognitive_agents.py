# FILE: 10_10/cognitive_agents.py
"""
Unified Cognitive Agents (v10_10 · Phase 3 — FINAL)
===================================================

This module implements ALL LLM-based cognition for the v10_10 workflow.

L2 is the only layer allowed to call these agents.

Agents (L2 cognition only):
    • StrategyLLMAgent            – strategy reasoning
    • DraftingGuild              – resume drafting
    • SemanticQAAgent            – QA reasoning + RAG reasoning
    • ConstitutionalSafetyAgent  – safety / policy review
    • HYDEQueryAgent             – HYDE synthetic query generation
    • QACouncilAgent             – QA council aggregation

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
from typing import Any, List, Optional, Sequence

from models import (
    AgentCard,
    AgentRole,
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
    CouncilVote,
)
from core.routing import RoutingPolicy
from runtime_utils import invoke_model, SandboxConfig
from observability import record_event, record_exception
from meta_profile import MetaProfileSnapshot
from prompt_builder import (
    PromptInstance,
    build_strategy_prompt,
    build_drafting_prompt,
    build_qa_prompt,
    build_safety_prompt,
    build_hyde_prompt,
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
# Base LLM agent
# =============================================================================


class LLMBaseAgent:
    """
    Base class for all L2 cognitive agents.

    This class centralizes:
        • RoutingPolicy-based model selection.
        • SandboxConfig usage.
        • invoke_model() calls.
        • Basic observability events.

    This class must remain **L2-only** and must not perform:
        • planning (L1),
        • orchestration / retries (L3),
        • state mutation (L4),
        • safety policy enforcement (L5).
    """

    routing_policy: RoutingPolicy
    sandbox: SandboxConfig
    meta_profile: Optional[MetaProfileSnapshot] = None
    agent_card: AgentCard

    def __init__(
        self,
        routing_policy: RoutingPolicy,
        sandbox: SandboxConfig,
        meta_profile: Optional[MetaProfileSnapshot] = None,
        agent_card: Optional[AgentCard] = None,
    ) -> None:
        self.routing_policy = routing_policy
        self.sandbox = sandbox
        self.meta_profile = meta_profile

        if agent_card is not None:
            self.agent_card = agent_card
        else:
            # Derive a default AgentCard based on concrete subclass.
            name = self.__class__.__name__
            role_map = {
                "StrategyLLMAgent": AgentRole.PLANNER,
                "DraftingGuild": AgentRole.EXECUTION,
                "SemanticQAAgent": AgentRole.QA,
                "ConstitutionalSafetyAgent": AgentRole.SAFETY,
                "HYDEQueryAgent": AgentRole.META,
                "QACouncilAgent": AgentRole.QA,
            }
            role = role_map.get(name, AgentRole.META)

            default_capabilities: List[str] = []
            if name == "StrategyLLMAgent":
                default_capabilities = ["planning", "strategy_reasoning"]
            elif name == "DraftingGuild":
                default_capabilities = ["drafting", "content_generation"]
            elif name == "SemanticQAAgent":
                default_capabilities = ["qa", "rag_reasoning"]
            elif name == "ConstitutionalSafetyAgent":
                default_capabilities = ["safety_analysis"]
            elif name == "HYDEQueryAgent":
                default_capabilities = ["hyde_query_generation"]
            elif name == "QACouncilAgent":
                default_capabilities = ["qa_council_aggregation"]

            self.agent_card = AgentCard(
                agent_id=name,
                role=role,
                capabilities=default_capabilities,
                allowed_tools=[],
                policy_scope={},
            )

    # ------------------------------------------------------------------
    # Tool permission helper
    # ------------------------------------------------------------------

    def _check_tool_allowed(self, tool_name: str) -> None:
        """Raise PermissionError if tool_name is not allowed for this agent.

        This helper is intentionally opt-in: existing agents only enforce
        tool ACLs where they explicitly call _check_tool_allowed.
        """

        allowed = list(self.agent_card.allowed_tools or [])
        if not allowed:
            # Empty allowed_tools means "no ACL applied" for now.
            return

        if tool_name not in allowed:
            raise PermissionError(
                f"Agent '{self.agent_card.agent_id}' is not allowed to use tool '{tool_name}'"
            )

    def _call_llm(self, prompt: PromptInstance) -> str:
        """
        Execute a single LLM call for the given prompt instance.
        """
        # Derive an optional complexity hint for routing from the plan.
        complexity: Optional[str] = None
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
        except Exception as exc:  # noqa: BLE001
            record_exception("routing_policy_error", exc)
            raise

        record_event(
            "llm_call_start",
            {
                "prompt_id": prompt.prompt_id,
                "model": getattr(model, "name", str(model)),
                "layer": prompt.layer,
                "agent": prompt.agent,
                "agent_id": self.agent_card.agent_id,
                "agent_role": self.agent_card.role.value,
                "agent_capabilities": list(self.agent_card.capabilities or []),
            },
        )

        try:
            raw = invoke_model(
                model=model,
                prompt=prompt,
                sandbox=self.sandbox,
            )
            record_event(
                "llm_call_success",
                {
                    "prompt_id": prompt.prompt_id,
                    "model": getattr(model, "name", str(model)),
                    "layer": prompt.layer,
                    "agent": prompt.agent,
                    "agent_id": self.agent_card.agent_id,
                    "agent_role": self.agent_card.role.value,
                    "agent_capabilities": list(self.agent_card.capabilities or []),
                },
            )
            return raw
        except Exception as exc:  # noqa: BLE001
            record_exception("llm_call_failure", exc)
            record_event(
                "llm_call_failure_event",
                {
                    "prompt_id": prompt.prompt_id,
                    "model": getattr(model, "name", str(model)),
                    "layer": prompt.layer,
                    "agent": prompt.agent,
                    "agent_id": self.agent_card.agent_id,
                    "agent_role": self.agent_card.role.value,
                    "agent_capabilities": list(self.agent_card.capabilities or []),
                },
            )
            raise


# =============================================================================
# Strategy Agent
# =============================================================================


class StrategyLLMAgent(LLMBaseAgent):
    """
    Strategy agent responsible for high-level reasoning.

    Outputs:
        • StrategyResult
        • StrategyBranch list (internally)
    """

    async def run_strategy(
        self,
        strategy_plan: Any,
        job: Any,
        resume: Any,
        config: Any,
    ) -> StrategyResult:
        ctx = _PromptContext(job=job, resume=resume, config=config)

        prompt = build_strategy_prompt(
            plan=strategy_plan,
            ctx=ctx,
            layer="L2",
            agent="strategy",
            model_tier="balanced",
        )

        raw = self._call_llm(prompt)
        text = (raw or "").strip()

        # Try to parse structured strategy output; fallback to a simple branch.
        branches: List[StrategyBranch] = []
        try:
            data = json.loads(text)
            if isinstance(data, list):
                for item in data:
                    try:
                        branches.append(
                            StrategyBranch(
                                id=str(item.get("id") or len(branches)),
                                description=str(item.get("description") or ""),
                                weight=float(item.get("weight", 1.0)),
                            )
                        )
                    except Exception:
                        continue
            else:
                raise ValueError("Strategy output must be a JSON list")
        except Exception:
            # Fallback: single generic branch.
            branches = [
                StrategyBranch(
                    id="default",
                    description=text or "Default strategy branch",
                    weight=1.0,
                )
            ]

        result = StrategyResult(branches=branches)
        record_event(
            "strategy_completed",
            {
                "num_branches": len(branches),
                "text_len": len(text),
            },
        )
        return result


# =============================================================================
# Drafting Agent
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
        text = (raw or "").strip()

        # Try to parse as JSON list of sections.
        sections: List[DraftSection] = []
        try:
            data = json.loads(text)
            if not isinstance(data, list):
                raise ValueError("Drafting output must be a JSON list")

            for item in data:
                try:
                    sections.append(
                        DraftSection(
                            id=str(item.get("id") or len(sections)),
                            title=str(item.get("title") or ""),
                            body=str(item.get("body") or ""),
                            metadata=dict(item.get("metadata") or {}),
                        )
                    )
                except Exception:
                    continue
        except Exception:
            # Fallback: a single section using the full text.
            sections = [
                DraftSection(
                    id="full",
                    title="Auto-generated Resume",
                    body=text,
                    metadata={},
                )
            ]

        result = DraftingResult(sections=sections)
        record_event(
            "drafting_completed",
            {
                "num_sections": len(sections),
                "text_len": len(text),
            },
        )
        return result


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
        """
        Run QA over drafted resume + retrieval evidence.
        """
        ctx = _PromptContext(job=job, resume=resume, config=config)

        prompt = build_qa_prompt(
            plan=qa_plan,
            ctx=ctx,
            draft=draft,
            rag=rag,
            layer="L2",
            agent="qa",
            model_tier="balanced",
        )

        raw = self._call_llm(prompt)
        text = (raw or "").strip()

        findings = self._parse_qa_output(text, qa_plan)
        result = QAResult(findings=findings)

        record_event(
            "qa_completed",
            {
                "num_findings": len(findings),
                "text_len": len(text),
            },
        )
        return result

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

        try:
            data = json.loads(raw)
            if not isinstance(data, list):
                raise ValueError("QA output must be a JSON list")

            findings: List[QAFinding] = []
            for item in data:
                try:
                    findings.append(
                        QAFinding(
                            id=str(item.get("id") or len(findings)),
                            category=str(item.get("category") or "qa"),
                            severity=str(item.get("severity") or "medium"),
                            message=str(item.get("message") or ""),
                            metadata=dict(item.get("metadata") or {}),
                        )
                    )
                except Exception:
                    continue

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
    Safety agent that performs a constitutional safety pass.

    This agent does *not* enforce policy; it only produces SafetyResult
    findings for L5 to interpret and enforce.
    """

    async def run_safety(
        self,
        safety_plan: Any,
        draft: DraftingResult,
        rag: RAGResult,
        qa_result: QAResult,
        job: Any,
        resume: Any,
        config: Any,
    ) -> SafetyResult:
        """
        Run the constitutional safety review over all available evidence.
        """
        ctx = _PromptContext(job=job, resume=resume, config=config)

        prompt = build_safety_prompt(
            plan=safety_plan,
            ctx=ctx,
            draft=draft,
            rag=rag,
            qa=qa_result,
            layer="L2",
            agent="safety",
            model_tier="balanced",
        )

        raw = self._call_llm(prompt)
        text = (raw or "").strip()

        findings = self._parse_safety_output(text, safety_plan)
        result = SafetyResult(findings=findings)

        record_event(
            "safety_completed",
            {
                "num_findings": len(findings),
                "num_high_severity": sum(
                    1 for f in findings if f.severity.lower() == "high"
                ),
            },
        )
        return result

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
                    check_id=str(chk),
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
            for idx, item in enumerate(data):
                try:
                    check_id = str(
                        item.get("check_id")
                        or (checks[idx] if idx < len(checks) else idx)
                    )
                    findings.append(
                        SafetyFinding(
                            check_id=check_id,
                            category=str(item.get("category") or "safety"),
                            severity=str(item.get("severity") or "medium"),
                            message=str(item.get("message") or ""),
                            details=dict(item.get("details") or {}),
                        )
                    )
                except Exception:
                    continue

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


# =============================================================================
# HYDE Query Agent
# =============================================================================


class HYDEQueryAgent(LLMBaseAgent):
    """
    HYDE (Hypothetical Document) query generator.

    This agent generates an idealized answer for use as a dense retrieval proxy.
    L2 decides when to call it based on the RAGPlan and config flags.
    """

    async def run_hyde_query(
        self,
        rag_plan: Any,  # RAGPlan; kept as Any to avoid circular typing issues.
        ctx: Any,  # ExecutionContext; passed through to prompt_builder.
    ) -> str:
        prompt = build_hyde_prompt(
            plan=rag_plan,
            ctx=ctx,
            layer="L2",
            agent="rag",
            model_tier="balanced",
        )
        raw = self._call_llm(prompt)
        text = (raw or "").strip()

        record_event(
            "hyde_query_completed",
            {
                "prompt_id": prompt.prompt_id,
                "text_len": len(text),
            },
        )
        return text


# =============================================================================
# QA Council Agent
# =============================================================================


class QACouncilAgent(LLMBaseAgent):
    """
    QA-council aggregation agent.

    This agent consumes a PromptInstance specifically designed for council
    aggregation and returns a typed CouncilVote object.

    NOTE:
        The concrete prompt template is defined in prompt_builder; this class
        only executes the prompt and interprets the JSON response.
    """

    async def run_council(
        self,
        prompt: PromptInstance,
    ) -> CouncilVote:
        raw = self._call_llm(prompt)
        text = (raw or "").strip()

        if not text:
            record_event("qa_council_empty_output", {})
            return CouncilVote(
                members=0,
                selected_id=None,
                scores={},
                ties=[],
                reason="empty_output",
            )

        try:
            data = json.loads(text)
            if not isinstance(data, dict):
                raise ValueError("Council output must be a JSON object")

            vote = CouncilVote(**data)
            record_event(
                "qa_council_completed",
                {
                    "members": vote.members,
                    "selected_id": vote.selected_id,
                    "num_scores": len(vote.scores),
                },
            )
            return vote
        except Exception:
            record_event(
                "qa_council_malformed_json",
                {"raw_len": len(text)},
            )
            return CouncilVote(
                members=0,
                selected_id=None,
                scores={},
                ties=[],
                reason="malformed_or_unparseable",
            )
