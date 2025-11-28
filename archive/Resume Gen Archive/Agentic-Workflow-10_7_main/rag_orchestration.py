"""Layer-3 orchestration for the v10.8 RAG workflow."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from agent_stacks_v10_8.state_adapter_stack import StateAdapterStack
from core_v10_7 import BaseAgent

from .rag_execution import RAGExecutionStack
from .rag_planning import RAGPlanningStack


class RAGOrchestratorStack(BaseAgent):
    """Coordinates RAG planning and execution without adding new heuristics."""

    def __init__(self, context: Any, debug_mode: bool = False) -> None:
        super().__init__(context, debug_mode)
        self._adapter = StateAdapterStack(context, debug_mode)
        self._planning = RAGPlanningStack(context, debug_mode)
        self._execution = RAGExecutionStack(context, debug_mode)
        self.safety_policy = getattr(context, "safety_policy", None)
        self.policy_stack = getattr(context, "policy_stack", None)
        self.constitutional_engine = getattr(context, "constitutional_engine", None)

    async def run_async(
        self, state: Dict[str, Any], workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        workflow_id = workflow_id or state.get("metadata", {}).get("workflow_id", "")
        current_state = state

        plan_patch = await self._planning.run_async(current_state, workflow_id)
        plan_payload = self._ensure_plan_metadata(plan_patch)
        current_state = self._adapter.apply_patch(current_state, plan_patch)
        self._append_a2a_message(
            current_state,
            message_type="PLAN_CREATED",
            payload={
                "workflow_id": workflow_id,
                "goal": plan_payload.get("goal", ""),
            },
        )
        self.log_feedback(
            workflow_id,
            "rag_plan",
            "signal",
            {"goal": plan_payload.get("goal"), "use_hyde": plan_payload.get("use_hyde", True)},
        )

        self._append_a2a_message(
            current_state,
            message_type="EXECUTION_STARTED",
            payload={"workflow_id": workflow_id, "query_count": len(plan_payload.get("retrieval_queries", []))},
        )
        self.log_feedback(
            workflow_id,
            "rag_execution",
            "signal",
            {"phase": "start", "queries": len(plan_payload.get("retrieval_queries", []))},
        )

        execution_patch = await self._execution.run_async(current_state, workflow_id)
        current_state = self._adapter.apply_patch(current_state, execution_patch)
        current_state = await self._maybe_retry_rag(
            current_state, workflow_id, plan_payload
        )

        bullets = current_state.get("resume", {}).get("experience_bullets", [])
        self._append_a2a_message(
            current_state,
            message_type="EXECUTION_COMPLETED",
            payload={
                "workflow_id": workflow_id,
                "bullet_count": len(bullets),
            },
        )
        self.log_feedback(
            workflow_id,
            "rag_execution",
            "success",
            {"phase": "complete", "bullets": len(bullets)},
        )

        await self._record_arbitration(current_state, workflow_id)
        safety_report = current_state.get("safety_report") or {}
        policy_decision = current_state.get("policy_decision") or {}
        constitutional_review = current_state.get("constitutional_review") or {}
        if not hasattr(safety_report, "dict"):
            safety_report = type("_Wrapper", (), {"dict": lambda self: dict(safety_report or {})})()
        if not hasattr(policy_decision, "dict"):
            policy_decision = type("_Wrapper", (), {"dict": lambda self: dict(policy_decision or {})})()
        if not hasattr(constitutional_review, "dict"):
            constitutional_review = type(
                "_Wrapper", (), {"dict": lambda self: dict(constitutional_review or {})}
            )()
        current_state["safety_report"] = safety_report.dict()
        current_state["policy_decision"] = policy_decision.dict()
        current_state["constitutional_review"] = constitutional_review.dict()
        return current_state

    def _append_a2a_message(
        self, state: Dict[str, Any], *, message_type: str, payload: Dict[str, Any]
    ) -> None:
        channel = state.setdefault("a2a", {})
        messages = channel.setdefault("messages", [])
        messages.append(
            {
                "sender": self.__class__.__name__,
                "recipient": "ALL",
                "message_type": message_type,
                "payload": payload,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    def _ensure_plan_metadata(self, plan_patch: Dict[str, Any]) -> Dict[str, Any]:
        plan_payload = (plan_patch.get("rag", {}) or {}).get("plan", {})
        if isinstance(plan_payload, dict) and "use_hyde" not in plan_payload:
            plan_payload["use_hyde"] = True
        return plan_payload

    async def _maybe_retry_rag(
        self,
        state: Dict[str, Any],
        workflow_id: str,
        plan_payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        scm = getattr(self, "self_correction_manager", None)
        bullets = state.get("resume", {}).get("experience_bullets", [])
        should_retry = plan_payload.get("use_hyde", True) and not bullets
        if not (should_retry and scm and scm.can_retry(workflow_id, "rag")):
            return state

        report = scm.start_retry(
            workflow_id,
            "rag",
            issue="hyde_zero_results",
            action="rerun_without_hyde",
            metadata={"query_count": len(plan_payload.get("retrieval_queries", []))},
        )
        plan_payload["use_hyde"] = False
        self._append_a2a_message(
            state,
            message_type="RETRY_TRIGGERED",
            payload={"workflow_id": workflow_id, "reason": "hyde_zero_results"},
        )
        self.log_feedback(
            workflow_id,
            "rag_retry",
            "retry",
            {"reason": "hyde_zero_results"},
        )

        retry_patch = await self._execution.run_async(state, workflow_id)
        state = self._adapter.apply_patch(state, retry_patch)
        bullets_after = state.get("resume", {}).get("experience_bullets", [])
        resolved = bool(bullets_after)
        scm.finalize_retry(report, resolved, {"bullet_count": len(bullets_after)})
        self.log_feedback(
            workflow_id,
            "rag_retry",
            "success" if resolved else "failure",
            {"resolved": resolved, "bullet_count": len(bullets_after)},
        )
        return state

    async def _record_arbitration(self, state: Dict[str, Any], workflow_id: str) -> None:
        engine = getattr(self.context, "arbitration_engine", None)
        if engine is None:
            return
        report = await engine.run_check("prompt_rag_join", state)
        bucket = state.setdefault("arbitration", {})
        bucket["prompt_rag_join"] = report.model_dump()
        self.log_feedback(
            workflow_id,
            "rag_arbitration",
            "signal",
            {
                "decision": report.decision,
                "confidence": report.confidence,
            },
        )
