"""Human-in-the-loop routing and reconciliation agents."""

import asyncio
import json
import math
import os
from datetime import datetime
from typing import Any

from core_v10_7 import (
    BaseAgent,
    HILAmbiguityReport,
    HILFeedbackIntent,
    HILFeedbackRoute,
    HILReconciliationResult,
    PersonaConsensus,
    PersonaReviewDecision,
    PydanticSchemaError,
    StrategyPlan,
    _format_prompt_with_defaults,
    track_metrics,
)
from pydantic import BaseModel, Field


class VirtualReviewerPersonaAgent(BaseAgent):
    """Persona-specialized reviewer that interprets human feedback."""

    PersonaPrompt = """
    You are acting as the {persona} reviewer.
    Specialty focus: {focus}
    Human feedback:
    {human_feedback}

    Clustered intents summary:
    {intent_summary}

    Provide a JSON object with keys:
    - persona (string)
    - approval (boolean)
    - confidence (0-1 float)
    - key_concerns (list of strings)
    - proposed_actions (list of strings)
    - escalation_recommended (boolean)
    """

    def __init__(self, context: "WorkflowContext", persona: str, focus: str, debug_mode: bool = False):
        super().__init__(context, debug_mode)
        self.persona = persona
        self.focus = focus

    @track_metrics("run_virtual_reviewer_persona")
    async def run_async(
        self,
        human_feedback: str,
        intent_clusters: list[HILFeedbackIntent],
        workflow_id: str,
    ) -> PersonaReviewDecision:
        client = self.get_model_client("qa_model")
        intent_summary = (
            json.dumps([intent.model_dump() for intent in intent_clusters])
            if intent_clusters
            else "[]"
        )
        prompt = await _format_prompt_with_defaults(
            self.PersonaPrompt,
            {
                "persona": self.persona,
                "focus": self.focus,
                "human_feedback": human_feedback,
                "intent_summary": intent_summary,
            },
            self.budget_manager,
            client.goal_state,
            client.top_failures,
        )

        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.qa_model.temperature,
            response_format="json_object",
        )

        validated_output, error = self.validator.validate(
            response["content"],
            PersonaReviewDecision,
        )
        if error:
            self.log_warning(
                f"Persona {self.persona} validation failed: {error}. Using fallback decision."
            )
            fallback = PersonaReviewDecision(
                persona=self.persona,
                approval=False,
                confidence=0.0,
                key_concerns=["Unable to parse persona feedback"],
                proposed_actions=[],
                escalation_recommended=True,
            )
            self.log_feedback(
                workflow_id,
                "virtual_persona_decision",
                "error",
                fallback.model_dump(),
            )
            return fallback

        self.log_feedback(
            workflow_id,
            "virtual_persona_decision",
            "success",
            validated_output.model_dump(),
        )

        return validated_output


class VirtualReviewerCouncilAgent(BaseAgent):
    """Coordinates persona reviewers to negotiate a consensus."""

    DEFAULT_PERSONAS = [
        {
            "name": "Legal",
            "focus": "Ensure compliance, risk mitigation, and policy adherence.",
        },
        {
            "name": "Brand",
            "focus": "Protect voice, tone, and reputation considerations.",
        },
        {
            "name": "SME",
            "focus": "Validate technical accuracy and subject-matter fidelity.",
        },
    ]

    @track_metrics("run_virtual_reviewer_council")
    async def run_async(
        self,
        human_feedback: str,
        intent_clusters: list[HILFeedbackIntent],
        workflow_id: str,
    ) -> PersonaConsensus:
        persona_tasks = []
        for persona in self.DEFAULT_PERSONAS:
            persona_agent = VirtualReviewerPersonaAgent(
                self.context,
                persona["name"],
                persona["focus"],
                self.debug_mode,
            )
            persona_tasks.append(
                persona_agent.run_async(human_feedback, intent_clusters, workflow_id)
            )

        persona_decisions = await asyncio.gather(*persona_tasks)
        approvals = sum(1 for decision in persona_decisions if decision.approval)
        escalations = any(
            decision.escalation_recommended for decision in persona_decisions
        )
        approved = approvals >= math.ceil(len(persona_decisions) / 2)

        negotiated_actions: list[str] = []
        for decision in persona_decisions:
            for action in decision.proposed_actions:
                if action not in negotiated_actions:
                    negotiated_actions.append(action)

        rationale = (
            "Consensus approved"
            if approved
            else "Consensus blocked by persona concerns"
        )

        consensus = PersonaConsensus(
            approved=approved,
            persona_decisions=persona_decisions,
            negotiated_actions=negotiated_actions,
            rationale=rationale,
            escalation_recommended=escalations,
        )

        self.log_feedback(
            workflow_id,
            "virtual_council_consensus",
            "success",
            consensus.model_dump(),
        )

        return consensus


class HILFeedbackSummarizerAgent(BaseAgent):
    """Clusters human edits into reusable intents for downstream routing."""

    class SummarizerOutput(BaseModel):
        intent_clusters: list[HILFeedbackIntent] = Field(default_factory=list)
        delegation_score: float = Field(0.0, ge=0.0, le=1.0)
        recommended_node: str = Field("DRAFTING")
        recommended_specialists: list[str] = Field(default_factory=list)

    @track_metrics("run_hil_feedback_summarizer")
    async def run_async(
        self,
        human_feedback: str,
        state_snapshot: dict[str, Any] | None,
        workflow_id: str,
    ) -> SummarizerOutput:
        if not human_feedback.strip():
            return self.SummarizerOutput()

        client = self.get_model_client("qa_model")
        prompt_body = {
            "human_feedback": human_feedback,
            "state_snapshot": json.dumps(state_snapshot or {}, default=str),
        }
        prompt = await _format_prompt_with_defaults(
            "Cluster human edits into intents and recommend routing.",
            prompt_body,
            self.budget_manager,
            client.goal_state,
            client.top_failures,
        )

        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.qa_model.temperature,
            response_format="json_object",
        )

        validated_output, error = self.validator.validate(
            response["content"],
            self.SummarizerOutput,
        )
        if error:
            self.log_warning(
                f"Summarizer validation failed: {error}. Using default routing."
            )
            output = self.SummarizerOutput()
        else:
            output = validated_output

        self.log_feedback(
            workflow_id,
            "hil_intent_summary",
            "success" if not error else "warning",
            {
                "delegation_score": output.delegation_score,
                "recommended_node": output.recommended_node,
                "intent_count": len(output.intent_clusters),
            },
        )

        return output


class HILReconciliationAgent(BaseAgent):
    """Integrates specialist human feedback back into the draft."""

    @track_metrics("run_hil_reconciliation")
    async def run_async(
        self,
        draft_sections: dict[str, Any],
        specialist_feedback: list[str],
        persona_consensus: PersonaConsensus | None,
        workflow_id: str,
    ) -> HILReconciliationResult:
        if not specialist_feedback:
            empty_result = HILReconciliationResult(
                integrated_text=json.dumps(draft_sections),
                change_log=["No specialist feedback provided"],
                unresolved_questions=[],
            )
            self.log_feedback(
                workflow_id,
                "hil_reconciliation",
                "warning",
                empty_result.model_dump(),
            )
            return empty_result

        client = self.get_model_client("qa_model")
        prompt = await _format_prompt_with_defaults(
            """
            Integrate the following specialist feedback into the draft.
            Draft sections:
            {draft}
            Specialist feedback entries:
            {feedback}
            Persona consensus summary:
            {consensus}

            Respond as JSON with keys: integrated_text (string), change_log (list of strings), unresolved_questions (list).
            """,
            {
                "draft": json.dumps(draft_sections, default=str),
                "feedback": json.dumps(specialist_feedback, default=str),
                "consensus": json.dumps(
                    persona_consensus.model_dump() if persona_consensus else {},
                    default=str,
                ),
            },
            self.budget_manager,
            client.goal_state,
            client.top_failures,
        )

        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.qa_model.temperature,
            response_format="json_object",
        )

        validated_output, error = self.validator.validate(
            response["content"],
            HILReconciliationResult,
        )
        if error:
            self.log_warning(
                f"Reconciliation validation failed: {error}. Returning fallback."
            )
            fallback = HILReconciliationResult(
                integrated_text=json.dumps(draft_sections),
                change_log=[f"Reconciliation failed validation: {error}"],
                unresolved_questions=specialist_feedback,
            )
            self.log_feedback(
                workflow_id,
                "hil_reconciliation",
                "error",
                fallback.model_dump(),
            )
            return fallback

        self.log_feedback(
            workflow_id,
            "hil_reconciliation",
            "success",
            validated_output.model_dump(),
        )

        return validated_output


class HILAmbiguityDetectorAgent(BaseAgent):
    """Detects ambiguity in strategy outputs."""

    @track_metrics("run_ambiguity_detector")
    async def run_async(
        self,
        strategy: StrategyPlan,
        workflow_id: str,
    ) -> dict[str, Any]:
        self.log_info("Detecting ambiguity (v10.7)...")
        client = self.get_model_client("qa_model")

        prompt_template = self.prompt_manager.get_template("hil_ambiguity_detector")

        prompt = await _format_prompt_with_defaults(
            prompt_template,
            {"strategy": strategy.model_dump_json()},
            self.budget_manager,
            client.goal_state,
            client.top_failures,
        )

        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.model_config.qa_model.temperature,
            response_format="json_object",
        )

        validated_output, error = self.validator.validate(
            response["content"],
            HILAmbiguityReport,
        )
        if error:
            raise PydanticSchemaError(
                f"HILAmbiguityDetector failed validation: {error}"
            )

        self.log_feedback(
            workflow_id,
            "ambiguity_detection",
            "success",
            {"detected": validated_output.ambiguity_detected},
        )

        return {"ambiguity_report": validated_output}


class HILFeedbackRouterAgent(BaseAgent):
    """Routes human feedback with persona negotiation and delegation."""

    @track_metrics("run_feedback_router")
    async def run_async(
        self,
        human_feedback: str,
        workflow_id: str,
        state_snapshot: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        self.log_info("Routing human feedback with persona council...")

        try:
            log_path = self.config.meta_loop_config.preference_log_path
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            with open(log_path, "a") as log_file:
                json.dump(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "workflow_id": workflow_id,
                        "feedback": human_feedback,
                    },
                    log_file,
                )
                log_file.write("\n")
        except Exception as exc:  # pragma: no cover - defensive logging
            self.log_error(f"Failed to log HIL preference feedback: {exc}")

        if not human_feedback.strip():
            self.log_warning(
                "No human feedback supplied. Defaulting to drafting continuation."
            )
            default_route = HILFeedbackRoute(next_step="DRAFTING", payload=None)
            return default_route.model_dump()

        summarizer = HILFeedbackSummarizerAgent(self.context, self.debug_mode)
        summary_output = await summarizer.run_async(
            human_feedback,
            state_snapshot,
            workflow_id,
        )
        intent_clusters = summary_output.intent_clusters

        council = VirtualReviewerCouncilAgent(self.context, self.debug_mode)
        persona_consensus = await council.run_async(
            human_feedback,
            intent_clusters,
            workflow_id,
        )

        delegated_specialists = summary_output.recommended_specialists
        delegation_score = summary_output.delegation_score

        delegation_threshold = getattr(
            self.config.agent_stacks,
            "hil_delegation_threshold",
            0.65,
        )
        strategy_threshold = getattr(
            self.config.agent_stacks,
            "hil_strategy_threshold",
            0.45,
        )

        next_step = summary_output.recommended_node or "DRAFTING"
        if not persona_consensus.approved:
            self.log_info(
                "Persona consensus blocked. Routing to strategy for clarification."
            )
            next_step = "STRATEGY"

        elif (
            delegation_score >= delegation_threshold
            and delegated_specialists
        ):
            self.log_info(
                "Delegation threshold met (%s >= %s). Escalating to specialists.",
                f"{delegation_score:.2f}",
                delegation_threshold,
            )
            next_step = "DELEGATE_SPECIALIST"

        elif (
            delegation_score >= strategy_threshold
            and summary_output.recommended_node == "STRATEGY"
        ):
            self.log_info(
                "Strategy adjustments recommended based on delegation score."
            )
            next_step = "STRATEGY"

        payload = None
        if intent_clusters:
            payload = intent_clusters[0].summary

        route = HILFeedbackRoute(
            next_step=next_step,
            payload=payload,
            intent_clusters=intent_clusters,
            delegated_specialists=delegated_specialists,
            persona_consensus=persona_consensus,
        )

        return route.model_dump()
