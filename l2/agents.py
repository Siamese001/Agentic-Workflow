"""L2 - Cognitive Agents (Execution Layer)

This module defines specialized LLM agents that execute planned tasks:
- Strategy execution
- Drafting execution
- QA execution
- Safety execution
- HYDE query generation

Layer: L2 (Execution)
Responsibilities:
- Execute LLM calls based on L1 plans
- Parse and validate LLM outputs
- Return structured results

Non-responsibilities:
- Planning (L1)
- Orchestration (L3)
- State management (L4)
- Policy decisions (L5)
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, List, Optional, Sequence

from core.models.models import (
    AgentCard,
    AgentRole,
    StrategyResult,
    RAGResult,
    DraftingResult,
    DraftSection,
    QAResult,
    QAFinding,
    SafetyResult,
    SafetyFinding,
    Evidence,
    CouncilVote,
    ExecutionContext,
)
from core.routing import RoutingPolicy
from runtime.runtime_utils import invoke_model, SandboxConfig
from runtime.observability import (
    record_event,
    record_exception,
)
from config.meta_profile import MetaProfileSnapshot
from meta.prompt_builder import PromptInstance


# =============================================================================
# Local prompt context
# =============================================================================


@dataclass
class _PromptContext:
    """Minimal view of job and resume data used to build prompts.

    This helper groups together just the information prompt builders need:
    the job, the candidate's resume, and configuration. By keeping this
    context small and focused, prompts stay clear and on-topic, which helps
    the agents produce more relevant and accurate resume improvements.
    """

    job: Any
    resume: Any
    config: Any


# =============================================================================
# Base LLM agent
# =============================================================================


class LLMBaseAgent:
    """Common foundation for all resume-focused "thinking" agents.

    This base class knows how to select the right model, call it safely, and
    emit basic telemetry about each call. Concrete agents build on top of it
    to handle specific jobs such as planning, drafting, QA, or safety
    analysis.

    For a business reader, this shared base helps ensure that every agent
    follows the same rules for which models it may use, how those models are
    called, and how results are logged. That consistency supports predictable
    behavior and easier monitoring of resume quality over time.
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

    def _call_llm(self, prompt: Any) -> str:
        """
        Execute a single LLM call for the given prompt instance or string.
        
        Args:
            prompt: Either a PromptInstance or a string prompt text
        """
        # Handle string prompts by extracting text directly
        if isinstance(prompt, str):
            prompt_id = "direct_prompt"
            prompt_text = prompt
            layer = "L2"
            agent = self.agent_card.agent_id if self.agent_card else "unknown"
            variables: dict = {}
        else:
            prompt_id = getattr(prompt, "prompt_id", "unknown")
            prompt_text = getattr(prompt, "rendered", str(prompt))
            layer = getattr(prompt, "layer", "L2")
            agent = getattr(prompt, "agent", self.agent_card.agent_id if self.agent_card else "unknown")
            variables = getattr(prompt, "variables", {})
        
        # Derive an optional complexity hint for routing from the plan.
        complexity: Optional[Any] = None
        plan = variables.get("plan") if isinstance(variables, dict) else None
        if plan is not None and hasattr(plan, "complexity"):
            complexity_val = getattr(plan, "complexity", None)
            # Convert to ComplexityLevel if it's a string
            if isinstance(complexity_val, str):
                from core.models.models import ComplexityLevel
                try:
                    complexity = ComplexityLevel(complexity_val.lower())
                except (ValueError, AttributeError):
                    complexity = complexity_val
            else:
                complexity = complexity_val

        # Select the concrete model.
        try:
            model = self.routing_policy.select_model(
                task=prompt_id,
                complexity=complexity,
                meta_profile=self.meta_profile,
            )
        except Exception as exc:  # noqa: BLE001
            record_exception("routing_policy_error", exc)
            raise

        record_event(
            "llm_call_start",
            {
                "prompt_id": prompt_id,
                "model": getattr(model, "name", str(model)),
                "layer": layer,
                "agent": agent,
                "agent_id": self.agent_card.agent_id,
                "agent_role": self.agent_card.role.value,
                "agent_capabilities": list(self.agent_card.capabilities or []),
            },
        )

        try:
            raw = invoke_model(
                model=model,
                prompt=prompt_text,
                sandbox=self.sandbox,
            )
            record_event(
                "llm_call_success",
                {
                    "prompt_id": prompt_id,
                    "model": getattr(model, "name", str(model)),
                    "layer": layer,
                    "agent": agent,
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
                    "prompt_id": prompt_id,
                    "model": getattr(model, "name", str(model)),
                    "layer": layer,
                    "agent": agent,
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
    """Agent that designs how the resume should be tailored to the job.

    This agent reads the job description, the candidate's resume, and the
    planning instructions, then proposes one or more strategy options for how
    to present the candidate. The result guides later steps on what to
    emphasize, what gaps to address, and how ambitious the rewrite should be.

    In business terms, it answers: "What is our game plan for making this
    resume compelling for this particular role?"
    """

    async def run_strategy(
        self,
        strategy_plan: Any,
        job: Any,
        resume: Any,
        config: Any,
    ) -> StrategyResult:
        """Execute strategy planning using LLM and return structured result.
        
        This method performs the core LLM interaction for strategy planning
        and returns a StrategyResult. The execution orchestration is handled
        by the calling execution layer.
        """
        # Build the strategy prompt using the prompt builder
        prompt = await self._build_strategy_prompt(
            strategy_plan=strategy_plan,
            job=job,
            resume=resume,
            config=config
        )
        
        # Execute LLM call
        llm_response = await self._call_llm(prompt)
        
        # Parse and structure the response
        strategy_result = await self._parse_strategy_result(llm_response)
        return strategy_result

    async def _build_strategy_prompt(self, strategy_plan: Any, job: Any, resume: Any, config: Any) -> str:
        """Build strategy prompt - stub implementation."""
        return f"Strategy planning for job: {job}, resume: {resume}"
    
    async def _call_llm(self, prompt: str) -> str:
        """Call LLM - stub implementation.""" 
        return "Strategy response stub"
    
    async def _parse_strategy_result(self, llm_response: str) -> StrategyResult:
        """Parse strategy result - stub implementation."""
        return StrategyResult(strategy="stub strategy", confidence=0.8)


# =============================================================================
# Drafting Agent
# =============================================================================


class DraftingGuild(LLMBaseAgent):
    """Agent that writes and rewrites resume sections.

    Using the chosen strategy, job description, and retrieved evidence, this
    agent drafts or rewrites sections such as Summary, Experience, and Skills.
    It focuses on highlighting impact, aligning wording with the job, and
    keeping the structure readable for recruiters.

    Practically, this is the agent that turns guidance into actual resume
    text, which makes it central to how personalized and compelling the final
    document feels.
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
        """Execute drafting using LLM and return structured result.
        
        This method performs the core LLM interaction for drafting
        and returns a DraftingResult. The execution orchestration is handled
        by the calling execution layer.
        """
        # Stub implementation - return drafting result
        return DraftingResult(sections=[DraftSection(title="stub", content="stub content")])


# =============================================================================
# Semantic QA Agent (QA + RAG reasoning)
# =============================================================================


class SemanticQAAgent(LLMBaseAgent):
    """Agent that reviews drafts for quality and reasons over evidence.

    This agent has two main roles:

    * Quality assurance – it inspects drafted resume content for unsupported
      claims, missing key requirements, unclear phrasing, and other issues.
    * RAG reasoning – it reads retrieved evidence and produces a concise
      reasoning summary that later steps can rely on.

    For the business, this agent acts like a careful reviewer who ensures the
    resume is truthful, relevant to the job, and easy to understand.
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
        """Execute QA using LLM and return structured result.
        
        This method performs the core LLM interaction for QA
        and returns a QAResult. The execution orchestration is handled
        by the calling execution layer.
        """
        # Stub implementation - return QA result
        return QAResult(
            findings="stub qa findings", 
            confidence=0.8, 
            council_vote=CouncilVote(approved=True, reasoning="stub")
        )

    async def run_rag_reasoning(
        self,
        prompt: Any,  # Can be PromptInstance or str
        evidence: Sequence[Evidence],
        job: Any,
        resume: Any,
        config: Any,
    ) -> str:
        """
        Phase-3 RAG reasoning.

        L2 passes a pre-built prompt; this method simply calls the LLM
        and returns the reasoning text. L2 turns this into a synthetic
        Evidence item.
        
        Note: L2 agents do not call L1. The prompt is passed directly.
        """
        # _call_llm now handles both string and PromptInstance
        raw = self._call_llm(prompt)
        text = (raw or "").strip()

        prompt_id = getattr(prompt, "prompt_id", "rag_reasoning") if not isinstance(prompt, str) else "rag_reasoning"
        record_event(
            "rag_reasoning_completed",
            {
                "prompt_id": prompt_id,
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
    """Agent that scans resume content for safety and policy issues.

    This agent reviews the draft, evidence, and QA signals to identify
    potential safety concerns such as sensitive personal information, policy
    violations, or risky wording. It records these as structured findings that
    the L5 safety layer later interprets.

    It does not make the final allow/block decision itself, but it provides
    the detailed analysis that decision is based on.
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
        ctx = ExecutionContext(
            job=job,
            resume=resume,
            config=config,
            prompt_registry={},
            routing_policy=self.routing_policy,
            sandbox_config=self.sandbox,
            meta_profile_snapshot=self.meta_profile,
        )

        # Stub implementation - return safety result
        return SafetyResult(
            findings=[SafetyFinding(severity="low", description="stub safety finding")],
            approved=True
        )

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
    """Agent that imagines an ideal answer to improve retrieval.

    This agent generates a short, idealized description of the "perfect"
    candidate for the job, grounded in the provided context. Retrieval uses
    this text as a semantic query to find more relevant supporting evidence.

    Business impact: better evidence leads to more targeted rewrites and
    higher-quality alignment between the resume and the job description.
    """

    async def run_hyde_query(
        self,
        rag_plan: Any,  # RAGPlan; kept as Any to avoid circular typing issues.
        ctx: Any,  # ExecutionContext; passed through to prompt_builder.
    ) -> str:
        """Generate a HYDE query without calling L1.
        
        Note: L2 agents do not call L1. The HYDE prompt is built directly
        from the context and RAG plan.
        """
        # Build HYDE prompt directly (no L1 call)
        job = getattr(ctx, "job", None)
        resume = getattr(ctx, "resume", None)
        
        job_title = getattr(job, "title", "") if job else ""
        job_text = getattr(job, "posting_text", "") if job else ""
        resume_summary = getattr(resume, "summary", "") if resume else ""
        
        hyde_prompt_text = f"""Generate a hypothetical ideal candidate description for this job:
Job Title: {job_title}
Job Description: {job_text[:500] if job_text else 'N/A'}
Candidate Summary: {resume_summary[:300] if resume_summary else 'N/A'}

Write a short paragraph describing the ideal candidate's qualifications."""

        # Pass string directly to _call_llm (it handles both string and PromptInstance)
        raw = self._call_llm(hyde_prompt_text)
        text = (raw or "").strip()

        record_event(
            "hyde_query_completed",
            {
                "prompt_id": "hyde_query",
                "text_len": len(text),
            },
        )
        return text


# =============================================================================
# QA Council Agent
# =============================================================================


class QACouncilAgent(LLMBaseAgent):
    """Agent that aggregates multiple QA opinions into a single verdict.

    When the system runs a "council" of QA checks, this agent reads their
    combined output and turns it into a single CouncilVote. That vote can then
    influence ranking, safety, or additional review steps.

    For business users, this is how the system simulates a panel of reviewers
    and turns their perspectives into one clear signal about the quality and
    risk level of a resume draft.
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





