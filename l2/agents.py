"""
Legacy agents wrapper for résumé processing workflow execution.

Provides backward compatibility by delegating operations to atomic L1-L5 architecture for résumé enhancement workflows.
"""

from typing import Any, Optional
from core.models.models import (
    AgentCard,
    AgentRole,
    StrategyResult,
    DraftingResult,
    QAResult,
    SafetyResult,
)
from core.routing import RoutingPolicy
from runtime.runtime_utils import SandboxConfig
from config.meta_profile import MetaProfileSnapshot

# Import atomic integration bridge
from atomic_integration_bridge import (
    AtomicStrategyAgent,
    AtomicDraftingAgent,
    AtomicQAAgent,
    AtomicSafetyAgent,
)

# Legacy agent classes that delegate to atomic layers
class StrategyLLMAgent(AtomicStrategyAgent):
    """
    Legacy strategy agent wrapper for résumé processing workflows.

    Delegates to atomic L1-L5 layers for comprehensive résumé enhancement strategy execution.
    """
    pass

class DraftingGuild(AtomicDraftingAgent):
    """
    Legacy drafting agent wrapper for résumé processing workflows.

    Delegates to atomic L1-L5 layers for comprehensive résumé content generation.
    """
    pass

class SemanticQAAgent(AtomicQAAgent):
    """
    Legacy QA agent wrapper for résumé processing workflows.

    Delegates to atomic L1-L5 layers for comprehensive résumé analysis and validation.
    """
    pass

class ConstitutionalSafetyAgent(AtomicSafetyAgent):
    """
    Legacy safety agent wrapper for résumé processing workflows.

    Delegates to atomic L1-L5 layers for comprehensive résumé content safety validation.
    """
    pass

class HYDEQueryAgent:
    """
    Legacy HYDE query agent for résumé processing retrieval enhancement.

    Delegates to atomic L1-L5 layers for optimized résumé search query generation.
    """
    
    def __init__(self, routing_policy: RoutingPolicy, sandbox: SandboxConfig, meta_profile: Optional[MetaProfileSnapshot] = None):
        self.routing_policy = routing_policy
        self.sandbox = sandbox
        self.meta_profile = meta_profile
    
    async def run_hyde_query(self, rag_plan: Any, ctx: Any) -> str:
        """
        Generates HYDE queries for résumé processing retrieval enhancement.

        Delegates to atomic execution for optimized résumé search query generation.
        """
        # Delegate to L2 LLM caller for pure execution
        from l2.llm_caller import LLMCaller
        llm_caller = LLMCaller(self.routing_policy, self.sandbox)
        
        job = getattr(ctx, "job", None)
        resume = getattr(ctx, "resume", None)
        
        job_title = getattr(job, "title", "") if job else ""
        job_text = getattr(job, "posting_text", "") if job else ""
        resume_summary = getattr(resume, "summary", "") if resume else ""
        
        # Use L1 prompt builder for pure planning
        from l1.prompt_builder import PromptBuilder
        prompt = PromptBuilder.build_strategy_prompt(
            {"target_role": job_title, "reasoning": "HYDE query generation"},
            job,
            resume,
            {}
        )
        
        # Use L2 execution
        result = llm_caller.call_llm(prompt, "hyde_generation")
        return result.strip()

class QACouncilAgent(AtomicQAAgent):
    """
    Legacy QA council agent wrapper for résumé processing workflows.

    Delegates to atomic L1-L5 layers for comprehensive résumé quality assessment.
    """
    pass

# Legacy LLMBaseAgent for backward compatibility
class LLMBaseAgent:
    """
    Legacy base agent class for résumé processing workflow compatibility.

    Delegates to atomic architecture for comprehensive résumé enhancement operations.
    """
    
    def __init__(self, routing_policy: RoutingPolicy, sandbox: SandboxConfig, meta_profile: Optional[MetaProfileSnapshot] = None, agent_card: Optional[AgentCard] = None):
        self.routing_policy = routing_policy
        self.sandbox = sandbox
        self.meta_profile = meta_profile
        self.agent_card = agent_card or AgentCard(
            name="LegacyAgent",
            role=AgentRole.META,
            capabilities=["legacy_compatibility"],
            version="1.0.0",
            description="Legacy wrapper for atomic architecture",
        )
    
    def _call_llm(self, prompt: Any) -> str:
        """Legacy LLM call - delegates to atomic L2 execution."""
        from l2.llm_caller import LLMCaller
        llm_caller = LLMCaller(self.routing_policy, self.sandbox)
        return llm_caller.call_llm(prompt, self.agent_card.role.value)
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





