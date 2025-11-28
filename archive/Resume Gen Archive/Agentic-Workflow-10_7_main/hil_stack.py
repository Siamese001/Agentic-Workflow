"""Human-in-the-loop stack shim for v10.8."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from core_v10_7 import PersonaConsensus, StrategyPlan
from agent_stacks_v10_8.components.hil import (
    HILAmbiguityDetectorAgent,
    HILFeedbackRouterAgent,
    HILFeedbackSummarizerAgent,
    HILReconciliationAgent,
    VirtualReviewerCouncilAgent,
)


class HILStackV10_8:
    """Wrapper that exposes the HIL-only capabilities."""

    def __init__(self, context: Any, debug_mode: bool = False) -> None:
        self.context = context
        self.debug_mode = debug_mode
        self._summarizer = HILFeedbackSummarizerAgent(context, debug_mode)
        self._ambiguity_detector = HILAmbiguityDetectorAgent(context, debug_mode)
        self._router = HILFeedbackRouterAgent(context, debug_mode)
        self._reconciliation_agent = HILReconciliationAgent(context, debug_mode)
        self._virtual_council = VirtualReviewerCouncilAgent(context, debug_mode)

    async def summarize_feedback_async(
        self, human_feedback: str, workflow_id: str
    ) -> Dict[str, Any]:
        """Cluster HIL feedback via the v10.7 summarizer."""

        return await self._summarizer.run_async(human_feedback, workflow_id)

    async def detect_ambiguity_async(
        self, strategy_plan: Any, workflow_id: str
    ) -> Dict[str, Any]:
        """Delegate ambiguity detection for strategy plans."""

        if isinstance(strategy_plan, dict):
            typed_plan = StrategyPlan.model_validate(strategy_plan)
        else:
            typed_plan = strategy_plan
        return await self._ambiguity_detector.run_async(typed_plan, workflow_id)

    async def route_feedback_async(
        self,
        feedback: str,
        workflow_id: str,
        state_snapshot: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Delegate routing decisions to the legacy router."""

        return await self._router.run_async(feedback, workflow_id, state_snapshot)

    async def route_from_state_async(
        self, state: Dict[str, Any], workflow_id: str
    ) -> Dict[str, Any]:
        """Read the HIL feedback payload and emit a normalized patch."""

        hil_bucket = state.get("hil", {}) if isinstance(state, dict) else {}
        human_feedback = hil_bucket.get("raw_feedback") or "Default to drafting"
        route = await self.route_feedback_async(human_feedback, workflow_id, state)
        return {
            "hil": {
                "next_step": route.get("next_step"),
                "payload": route.get("payload"),
                "intent_clusters": route.get("intent_clusters", []),
                "delegated_specialists": route.get("delegated_specialists", []),
                "persona_consensus": route.get("persona_consensus"),
                "reconciliation": route.get("reconciliation"),
            }
        }

    async def reconcile_feedback_async(
        self,
        draft_sections: Dict[str, Any],
        specialist_feedback: List[Any],
        persona_consensus: Optional[PersonaConsensus],
        workflow_id: str,
    ) -> Any:
        """Run the reconciliation agent with no behavior change."""

        return await self._reconciliation_agent.run_async(
            draft_sections, specialist_feedback, persona_consensus, workflow_id
        )

    async def reconcile_from_state_async(
        self, state: Dict[str, Any], workflow_id: str
    ) -> Dict[str, Any]:
        """Assemble reconciliation inputs from the shared state tree."""

        hil_bucket = state.get("hil", {}) if isinstance(state, dict) else {}
        specialist_feedback = list(hil_bucket.get("specialist_feedback", []))
        persona_payload = hil_bucket.get("persona_consensus")
        persona_consensus: Optional[PersonaConsensus] = None
        if isinstance(persona_payload, PersonaConsensus):
            persona_consensus = persona_payload
        elif persona_payload:
            try:
                persona_consensus = PersonaConsensus.model_validate(persona_payload)
            except Exception:
                persona_consensus = None

        draft_sections = state.get("draft", {}).get("sections", {})
        result = await self.reconcile_feedback_async(
            draft_sections,
            specialist_feedback,
            persona_consensus,
            workflow_id,
        )
        payload = result.model_dump() if hasattr(result, "model_dump") else result
        return {"hil": {"reconciliation": payload}}

    async def convene_virtual_council_async(
        self, human_feedback: str, intent_clusters: List[Any], workflow_id: str
    ) -> Dict[str, Any]:
        """Convene the existing virtual reviewer council."""

        return await self._virtual_council.run_async(human_feedback, intent_clusters, workflow_id)

    async def inject_edit_from_state_async(
        self, state: Dict[str, Any], workflow_id: str
    ) -> Dict[str, Any]:
        """Build the summary patch for a HIL edit injection."""

        payload = state.get("hil", {}).get("payload")
        if not payload:
            return {}

        reconciliation = state.get("hil", {}).get("reconciliation")
        if reconciliation and reconciliation.get("integrated_text"):
            summary_text = reconciliation["integrated_text"]
        else:
            summary_text = f"[EDITED BY HUMAN]: {payload}"

        existing_summary = state.get("draft", {}).get("sections", {}).get("summary")
        if isinstance(existing_summary, dict):
            summary_payload = dict(existing_summary)
            summary_payload["draft"] = summary_text
        else:
            summary_payload = {"draft": summary_text}

        return {"draft": {"sections": {"summary": summary_payload}}}
