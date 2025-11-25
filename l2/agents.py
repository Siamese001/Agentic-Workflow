"""
L2 execution agents for résumé processing.

Executes model calls to generate strategy, drafting, QA, and safety improvements for your résumé.
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
    MetaProfileSnapshot,
    PromptInstance,
)
from core.routing import RoutingPolicy
from runtime.runtime_utils import invoke_model, SandboxConfig
from runtime.observability import (
    record_event,
    record_exception,
)


# =============================================================================
# Local prompt context
# =============================================================================


@dataclass
class _PromptContext:
    """
    Groups job and resume data for prompt building.

    Ensures prompts stay focused on relevant information to improve résumé accuracy and job alignment.
    """

    job: Any
    resume: Any
    config: Any


# =============================================================================
# Base LLM agent
# =============================================================================


class LLMBaseAgent:
    """
    Foundation for all résumé thinking agents.

    Ensures consistent model selection and logging to improve résumé quality predictability.
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
        """
        Initializes agent with routing and safety controls.

        Guarantees proper model selection and security for consistent résumé improvement results.
        """
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

    def _check_tool_allowed(self, tool_name: str) -> None:
        """
        Validates tool permissions for security.

        Ensures only authorized tools are used to protect résumé data integrity.
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
        Executes LLM call with proper routing.

        Ensures optimal model selection for consistent résumé improvement quality.
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
    """
    Designs résumé tailoring strategy for specific jobs.

    Analyzes job requirements to create targeted improvement plans for better alignment.
    """

    async def run_strategy(
        self,
        strategy_plan: Any,
        job: Any,
        resume: Any,
        config: Any,
    ) -> StrategyResult:
        """
        Executes strategy planning for résumé optimization.

        Generates targeted improvement plans to enhance job description alignment.
        """
        # Build the strategy prompt using the prompt builder
        prompt = await self._build_strategy_prompt(
            strategy_plan=strategy_plan,
            job=job,
            resume=resume,
            config=config
        )
        
        # Execute LLM call
        llm_response = self._call_llm(prompt)
        
        # Parse and structure the response
        strategy_result = await self._parse_strategy_result(llm_response)
        return strategy_result

    async def _build_strategy_prompt(self, strategy_plan: Any, job: Any, resume: Any, config: Any) -> str:
        """
        Builds strategy prompt from job and resume data.

        Creates focused prompts to generate targeted résumé improvement strategies.
        """
        return f"Strategy planning for job: {job}, resume: {resume}"
    
    async def _parse_strategy_result(self, llm_response: str) -> StrategyResult:
        """
        Parses LLM response into structured strategy result.

        Converts raw model output into actionable résumé improvement recommendations.
        """
        return StrategyResult(
            plan=llm_response,
            confidence=0.8,
            reasoning="Strategy generated based on job analysis",
            evidence=[],
        )


# =============================================================================
# Drafting Agent
# =============================================================================


class DraftingGuild(LLMBaseAgent):
    """
    Writes and rewrites résumé sections based on strategy.

    Creates compelling résumé content that aligns with job requirements and highlights impact.
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
        """
        Executes résumé drafting with strategic guidance.

        Generates tailored résumé sections that emphasize relevant skills and accomplishments.
        """
        # Stub implementation - return drafting result
        return DraftingResult(sections=[DraftSection(title="stub", content="stub content")])


# =============================================================================
# Semantic QA Agent (QA + RAG reasoning)
# =============================================================================


class SemanticQAAgent(LLMBaseAgent):
    """
    Reviews résumé drafts for quality and evidence alignment.

    Ensures résumé claims are supported and content meets job description requirements.
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
        Performs quality assurance on résumé drafts.

        Identifies unsupported claims and missing requirements to improve résumé accuracy.
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
        Analyzes evidence to support résumé claims.

        Generates reasoning summaries that validate résumé content against job requirements.
        """
        # _call_llm now handles both string and PromptInstance
        reasoning = self._call_llm(prompt)
        return reasoning


# =============================================================================
# Safety Agent
# =============================================================================


class ConstitutionalSafetyAgent(LLMBaseAgent):
    """
    Validates résumé content for safety and compliance.

    Ensures résumé meets professional standards and avoids problematic content.
    """

    async def run_safety(
        self,
        safety_plan: Any,
        draft: DraftingResult,
        job: Any,
        resume: Any,
        config: Any,
    ) -> SafetyResult:
        """
        Performs safety validation on résumé content.

        Identifies potential issues to maintain professional résumé quality.
        """
        # Stub implementation - return safety result
        return SafetyResult(
            findings=[SafetyFinding(
                type="stub_finding",
                severity="low", 
                description="Stub safety check"
            )],
            approved=True,
            confidence=0.9
        )


# =============================================================================
# HYDE Query Agent
# =============================================================================


class HYDEQueryAgent(LLMBaseAgent):
    """
    Generates hypothetical document queries for retrieval.

    Creates effective search queries to find relevant résumé improvement evidence.
    """

    async def run_hyde_query(
        self,
        hyde_plan: Any,
        job: Any,
        resume: Any,
        config: Any,
    ) -> str:
        """
        Generates hypothetical résumé document queries.

        Creates search queries that improve evidence retrieval for résumé enhancement.
        """
        # Stub implementation - return HYDE query
        return "hypothetical resume document stub"


# =============================================================================
# QA Council Agent
# =============================================================================


class QACouncilAgent(LLMBaseAgent):
    """
    Aggregates multiple QA agent evaluations.

    Combines quality assessments to ensure comprehensive résumé validation.
    """

    async def run_qa_council(
        self,
        qa_plan: Any,
        draft: DraftingResult,
        job: Any,
        resume: Any,
        config: Any,
    ) -> QAResult:
        """
        Coordinates multiple quality assurance evaluations.

        Synthesizes diverse QA perspectives to improve résumé accuracy and completeness.
        """
        # Stub implementation - return council result
        return QAResult(
            findings="council qa findings",
            confidence=0.85,
            council_vote=CouncilVote(
                approved=True, 
                reasoning="Council consensus"
            )
        )


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
        # ExecutionContext created but not used in stub implementation
        # ctx = ExecutionContext(
        #     job=job,
        #     resume=resume,
        #     config=config,
        #     prompt_registry={},
        #     routing_policy=self.routing_policy,
        #     sandbox_config=self.sandbox,
        #     meta_profile_snapshot=self.meta_profile,
        # )

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





