"""Layer-3 orchestration for bullet + draft generation."""

from __future__ import annotations

import copy
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from agent_stacks_v10_8.state_adapter_stack import StateAdapterStack
from core_v10_7 import BaseAgent

from .bullet_execution import BulletExecutionStack
from .bullet_planning import BulletPlanningStack
from .draft_planning import DraftPlanningStack
from .drafting_execution import DraftingExecutionStack


class DraftOrchestratorStack(BaseAgent):
    """Runs the deterministic sequencing for bullets + draft assembly."""

    def __init__(self, context: Any, debug_mode: bool = False) -> None:
        super().__init__(context, debug_mode)
        self._adapter = StateAdapterStack(context, debug_mode)
        self._bullet_planning = BulletPlanningStack(context, debug_mode)
        self._bullet_execution = BulletExecutionStack(context, debug_mode)
        self._draft_planning = DraftPlanningStack(context, debug_mode)
        self._draft_execution = DraftingExecutionStack(context, debug_mode)

    async def run_async(
        self,
        state: Dict[str, Any],
        workflow_id: Optional[str] = None,
        state_snapshot: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        workflow_id = workflow_id or state.get("metadata", {}).get("workflow_id", "")
        current_state = state
        baseline = state_snapshot or state
        hil_next_step = (state.get("hil", {}).get("next_step") or "").upper()
        run_bullet_phase = hil_next_step != "DRAFTING"

        if run_bullet_phase:
            bullet_plan_patch = await self._bullet_planning.run_async(current_state, workflow_id)
            current_state, bullet_plan = self._apply_plan_patch(
                current_state, bullet_plan_patch, bucket="bullets"
            )
            self._append_a2a_message(
                current_state,
                message_type="BULLETS_PLANNED",
                payload={
                    "workflow_id": workflow_id,
                    "sections": len(bullet_plan.get("target_sections", [])),
                },
            )
            self.log_feedback(
                workflow_id,
                "bullet_planning",
                "signal",
                {"target_sections": len(bullet_plan.get("target_sections", []))},
            )

            bullet_execution_patch = await self._bullet_execution.run_async(current_state, workflow_id)
            current_state = self._apply_state_patch(current_state, bullet_execution_patch)
            bullets = current_state.get("bullets", {}).get("generated_bullets", [])
            self._append_a2a_message(
                current_state,
                message_type="BULLETS_GENERATED",
                payload={
                    "workflow_id": workflow_id,
                    "bullet_count": len(bullets),
                },
            )
            self.log_feedback(
                workflow_id,
                "bullet_generation",
                "success",
                {"bullet_count": len(bullets)},
            )
            await self._record_arbitration(current_state, "bullets_post_selection", workflow_id)

        draft_plan_patch = await self._draft_planning.run_async(current_state, workflow_id)
        current_state, draft_plan = self._apply_plan_patch(
            current_state, draft_plan_patch, bucket="draft"
        )
        self._append_a2a_message(
            current_state,
            message_type="DRAFT_PLANNED",
            payload={
                "workflow_id": workflow_id,
                "structure": len(draft_plan.get("structure", [])),
            },
        )
        self.log_feedback(
            workflow_id,
            "draft_planning",
            "signal",
            {"structure": len(draft_plan.get("structure", []))},
        )

        draft_execution_patch = await self._draft_execution.run_async(
            current_state,
            workflow_id,
        )
        current_state = self._apply_state_patch(current_state, draft_execution_patch)
        current_state = await self._maybe_retry_drafting(current_state, workflow_id)

        sections = current_state.get("draft", {}).get("sections", {})
        self._append_a2a_message(
            current_state,
            message_type="DRAFT_EXECUTED",
            payload={
                "workflow_id": workflow_id,
                "sections": len(sections),
                "baseline_sections": len(baseline.get("draft", {}).get("sections", {})),
            },
        )
        self.log_feedback(
            workflow_id,
            "draft_execution",
            "success",
            {"sections": len(sections)},
        )
        await self._record_arbitration(current_state, "draft_post_assembly", workflow_id)

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

    async def _record_arbitration(
        self, state: Dict[str, Any], stage: str, workflow_id: str
    ) -> None:
        engine = getattr(self.context, "arbitration_engine", None)
        if engine is None:
            return
        report = await engine.run_check(stage, state)
        bucket = state.setdefault("arbitration", {})
        bucket[stage] = report.model_dump()
        self.log_feedback(
            workflow_id,
            f"{stage}_arbitration",
            "signal",
            {"decision": report.decision, "confidence": report.confidence},
        )

    async def _maybe_retry_drafting(
        self, state: Dict[str, Any], workflow_id: str
    ) -> Dict[str, Any]:
        scm = getattr(self, "self_correction_manager", None)
        critique_status = self._extract_critique_status(state)
        if critique_status not in {"revise", "block"}:
            return state
        if not (scm and scm.can_retry(workflow_id, "drafting")):
            return state

        report = scm.start_retry(
            workflow_id,
            "drafting",
            issue="critique_panel_requested_changes",
            action="rerun_drafting",
            metadata={"critique_status": critique_status},
        )
        self._append_a2a_message(
            state,
            message_type="DRAFT_RETRY_TRIGGERED",
            payload={"workflow_id": workflow_id, "status": critique_status},
        )
        self.log_feedback(
            workflow_id,
            "drafting_retry",
            "retry",
            {"status": critique_status},
        )

        retry_patch = await self._draft_execution.run_async(state, workflow_id)
        state = self._apply_state_patch(state, retry_patch)
        updated_status = self._extract_critique_status(state)
        resolved = updated_status not in {"revise", "block"}
        scm.finalize_retry(report, resolved, {"critique_status": updated_status})
        self.log_feedback(
            workflow_id,
            "drafting_retry",
            "success" if resolved else "failure",
            {"resolved": resolved, "status": updated_status},
        )
        return state

    def _extract_critique_status(self, state: Dict[str, Any]) -> str:
        draft_bucket = state.get("draft", {})
        artifacts = draft_bucket.get("artifacts", {})
        possible_payloads = []
        if isinstance(draft_bucket.get("critique_panel"), dict):
            possible_payloads.append(draft_bucket["critique_panel"])
        if isinstance(artifacts, dict):
            if isinstance(artifacts.get("critique"), dict):
                possible_payloads.append(artifacts.get("critique"))
            draft_artifacts = artifacts.get("draft")
            if isinstance(draft_artifacts, dict) and isinstance(draft_artifacts.get("critique"), dict):
                possible_payloads.append(draft_artifacts.get("critique"))

        # Some stacks emit critiques into the top-level artifacts bucket before the
        # draft adapter normalizes them. Capture those payloads as well to maintain
        # parity with older stack structures.
        top_level_artifacts = state.get("artifacts", {})
        if isinstance(top_level_artifacts, dict):
            nested_artifacts = top_level_artifacts.get("artifacts")
            if isinstance(nested_artifacts, dict):
                if isinstance(nested_artifacts.get("critique"), dict):
                    possible_payloads.append(nested_artifacts.get("critique"))
                draft_artifacts = nested_artifacts.get("draft")
                if (
                    isinstance(draft_artifacts, dict)
                    and isinstance(draft_artifacts.get("critique"), dict)
                ):
                    possible_payloads.append(draft_artifacts.get("critique"))

        for payload in possible_payloads:
            status = payload.get("overall_status")
            if status:
                return str(status).lower()
        return "approved"

    def _apply_plan_patch(
        self,
        state: Dict[str, Any],
        patch: Dict[str, Any],
        *,
        bucket: str,
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        sanitized_patch = copy.deepcopy(patch)
        plan_payload: Dict[str, Any] = {}
        preserved_plan = self._detach_plan(state, bucket)
        bucket_body = sanitized_patch.get(bucket)
        if isinstance(bucket_body, dict):
            plan_payload = copy.deepcopy(bucket_body.pop("plan", {}) or {})
            if not bucket_body:
                sanitized_patch.pop(bucket, None)
        state = self._apply_state_patch(state, sanitized_patch)
        final_plan = plan_payload or preserved_plan
        if final_plan:
            state.setdefault(bucket, {})["plan"] = final_plan
        return state, final_plan

    def _detach_plan(self, state: Dict[str, Any], bucket: str) -> Dict[str, Any]:
        container = state.get(bucket)
        if isinstance(container, dict) and "plan" in container:
            preserved = copy.deepcopy(container["plan"])
            container.pop("plan", None)
            if not container:
                state.pop(bucket, None)
            return preserved
        return {}

    def _apply_state_patch(self, state: Dict[str, Any], patch: Dict[str, Any]) -> Dict[str, Any]:
        preserved_plans = {
            "draft": self._detach_plan(state, "draft"),
            "bullets": self._detach_plan(state, "bullets"),
        }
        updated_state = self._adapter.apply_patch(state, patch)
        for bucket, plan in preserved_plans.items():
            if plan:
                updated_state.setdefault(bucket, {})["plan"] = plan
        return updated_state
