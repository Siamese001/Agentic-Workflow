# === CONSOLIDATED FILE ===
# TIMESTAMP: 2025-11-17T16:29:33.152041Z
# TARGET: draft_stack.py
# SOURCE FILES:
# - /workspace/Agentic-Workflow/_latest_extract/stacks_v/draft_orchestration.py | SHA256: b0c430b6b50fe6a64eb457b7fd0483a74e49b965fb8884481be14850bde6b84e
# - /workspace/Agentic-Workflow/_latest_extract/stacks_v/draft_planning.py | SHA256: 3884704b5ad9547fa76c7329baa9a6db3baab3db66d80ba8d4d026f3b9684cc7
# - /workspace/Agentic-Workflow/_latest_extract/stacks_v/drafting_execution.py | SHA256: cb0b7eb63324b79a2cf4e9edd22d8d071b3015610685b1681ca5eaa93cb2e7ed
# MERGE RULE: 10_8 overrides 10_7; namespace collisions suffixed with __srcN


# ==== BEGIN SOURCE: /workspace/Agentic-Workflow/_latest_extract/stacks_v/draft_orchestration.py (sha256=b0c430b6b50fe6a64eb457b7fd0483a74e49b965fb8884481be14850bde6b84e) ====
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
        self.safety_policy = getattr(context, "safety_policy", None)
        self.policy_stack = getattr(context, "policy_stack", None)
        self.constitutional_engine = getattr(context, "constitutional_engine", None)

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
# ==== END SOURCE: /workspace/Agentic-Workflow/_latest_extract/stacks_v/draft_orchestration.py ====
# ==== BEGIN SOURCE: /workspace/Agentic-Workflow/_latest_extract/stacks_v/draft_planning.py (sha256=3884704b5ad9547fa76c7329baa9a6db3baab3db66d80ba8d4d026f3b9684cc7) ====
"""Deterministic Level-1 planner for the drafting stack."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from core_v10_7 import BaseAgent, DraftPlan

from .planning_utils import (
    collect_sections,
    describe_experience,
    extract_job_profile,
    extract_resume_profile,
    missing_requirements,
)


class DraftPlanningStack(BaseAgent):
    """Creates a low-latency drafting plan using only state inspection."""

    def __init____src2(self, context: Any, debug_mode: bool = False) -> None:
        super().__init__(context, debug_mode)

    async def run_async(
        self, state: Dict[str, Any], workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        plan = self._build_plan(state)
        return {"draft": {"plan": plan.model_dump()}}

    def _build_plan(self, state: Dict[str, Any]) -> DraftPlan:
        job_profile = extract_job_profile(state)
        resume_profile = extract_resume_profile(state)
        experiences = resume_profile["experiences"]
        structure = self._structure(state, job_profile)
        tone = self._tone(state)
        key_messages = self._key_messages(job_profile, experiences, resume_profile)
        review_gates = self._review_gates(job_profile)
        risks = self._risks(job_profile, experiences)
        return DraftPlan(
            structure=structure,
            tone=tone,
            key_messages=key_messages,
            review_gates=review_gates,
            risks=risks,
        )

    def _structure(
        self, state: Dict[str, Any], job_profile: Dict[str, Any]
    ) -> List[str]:
        sections = collect_sections(state)
        structure = ["Executive Summary"]
        if job_profile["team"]:
            structure.append(f"Team Narrative – {job_profile['team']}")
        structure.extend(section.title() for section in sections if section)
        return structure

    def _tone(self, state: Dict[str, Any]) -> str:
        strategy_plan = state.get("strategy", {}).get("strategy_plan") or {}
        if hasattr(strategy_plan, "model_dump"):
            strategy_plan = strategy_plan.model_dump()
        return strategy_plan.get("tone") or "Professional"

    def _key_messages(
        self,
        job_profile: Dict[str, Any],
        experiences: List[Dict[str, Any]],
        resume_profile: Dict[str, Any],
    ) -> List[str]:
        messages: List[str] = []
        if job_profile["title"]:
            messages.append(f"Position candidate as the obvious {job_profile['title']}")
        if experiences:
            messages.append(
                f"Highlight {describe_experience(experiences[0])} as the anchor story"
            )
        if resume_profile["summary"]:
            messages.append("Carry forward unique resume summary language")
        if job_profile["requirements"]:
            messages.append(
                f"Explicitly cover JD focus areas: {', '.join(job_profile['requirements'][:3])}"
            )
        return messages

    def _review_gates(self, job_profile: Dict[str, Any]) -> List[str]:
        gates = [
            "Narrative continuity review",
            "Quantified impact audit",
            "QA + tone alignment check",
        ]
        if job_profile["location"]:
            gates.append("Localization + market nuance review")
        return gates

    def _risks(
        self,
        job_profile: Dict[str, Any],
        experiences: List[Dict[str, Any]],
    ) -> List[str]:
        risks = ["Guard against hallucinating responsibilities not in resume"]
        missing = missing_requirements(job_profile["requirements"], experiences)
        if missing:
            risks.append(
                f"JD gaps detected: {', '.join(missing[:3])}. Address proactively."
            )
        return risks
# ==== END SOURCE: /workspace/Agentic-Workflow/_latest_extract/stacks_v/draft_planning.py ====
# ==== BEGIN SOURCE: /workspace/Agentic-Workflow/_latest_extract/stacks_v/drafting_execution.py (sha256=cb0b7eb63324b79a2cf4e9edd22d8d071b3015610685b1681ca5eaa93cb2e7ed) ====
"""Pure action implementation of the v10.8 drafting execution stack."""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

from core_v10_7 import BaseAgent, DraftPlan, StrategyPlan
from agent_stacks_v10_8.components.drafting import (
    ComplianceEditorAgent,
    NarrativeStylistAgent,
    StructureLeadAgent,
)
from agent_stacks_v10_8.state_adapter_stack import StateAdapterStack


class DraftingExecutionStack(BaseAgent):
    """Applies a DraftPlan by invoking deterministic drafting specialists."""

    def __init____src3(self, context: Any, debug_mode: bool = False) -> None:
        super().__init__(context, debug_mode)
        self.structure_lead = StructureLeadAgent(context, debug_mode)
        self.narrative_stylist = NarrativeStylistAgent(context, debug_mode)
        self.compliance_editor = ComplianceEditorAgent(context, debug_mode)
        self.safety_policy = getattr(context, "safety_policy", None)
        self.policy_stack = getattr(context, "policy_stack", None)
        self.constitutional_engine = getattr(context, "constitutional_engine", None)
        self._adapter = StateAdapterStack(context, debug_mode)

    async def run_async(
        self, state: Dict[str, Any], workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        workflow_id = workflow_id or state.get("metadata", {}).get("workflow_id", "")
        plan = self._plan_from_state(state)
        bullets = state.get("bullets", {}).get("generated_bullets", [])
        strategy = self._strategy_from_state(state, plan)

        structure_packet = await self.structure_lead.run_async(
            bullets, strategy, workflow_id
        )
        narrative_packet = await self.narrative_stylist.run_async(
            structure_packet.sections, strategy, workflow_id
        )
        compliance_packet = await self.compliance_editor.run_async(
            narrative_packet.sections, workflow_id
        )

        final_sections = self._apply_plan_structure(plan, compliance_packet.sections)
        artifacts = {
            "draft": {
                "structure": structure_packet.model_dump(),
                "narrative": narrative_packet.model_dump(),
                "compliance": compliance_packet.model_dump(),
            }
        }

        patch = {
            "draft": {
                "plan": plan.model_dump(),
                "sections": final_sections,
                "tone": plan.tone,
                "structure": plan.structure,
            },
            "artifacts": {"artifacts": artifacts},
        }
        mem_patch = self._adapter.patch_memory(
            agent_notes=self._append_agent_note(state, plan, final_sections)
        )
        patch.update(mem_patch.model_dump(exclude_none=True))
        safety_report = state.get("safety_report") or {}
        policy_decision = state.get("policy_decision") or {}
        constitutional_review = state.get("constitutional_review") or {}
        if not hasattr(safety_report, "dict"):
            safety_report = type("_Wrapper", (), {"dict": lambda self: dict(safety_report or {})})()
        if not hasattr(policy_decision, "dict"):
            policy_decision = type("_Wrapper", (), {"dict": lambda self: dict(policy_decision or {})})()
        if not hasattr(constitutional_review, "dict"):
            constitutional_review = type(
                "_Wrapper", (), {"dict": lambda self: dict(constitutional_review or {})}
            )()
        patch["safety_report"] = safety_report.dict()
        patch["policy_decision"] = policy_decision.dict()
        patch["constitutional_review"] = constitutional_review.dict()
        return patch

    def _plan_from_state(self, state: Dict[str, Any]) -> DraftPlan:
        plan_payload = state.get("draft", {}).get("plan")
        if plan_payload is None:
            raise ValueError("Draft plan missing from state['draft']['plan']")
        if isinstance(plan_payload, DraftPlan):
            return plan_payload
        return DraftPlan.model_validate(plan_payload)

    def _strategy_from_state(self, state: Dict[str, Any], plan: DraftPlan) -> StrategyPlan:
        strategy_payload = state.get("strategy", {}).get("strategy_plan")
        if isinstance(strategy_payload, StrategyPlan):
            base = strategy_payload
        elif strategy_payload:
            base = StrategyPlan.model_validate(strategy_payload)
        else:
            base = StrategyPlan(
                strategy_name="draft-plan",
                focus_areas=plan.key_messages or ["core narrative"],
                key_achievements_to_highlight=plan.key_messages[:3],
                tone=plan.tone,
            )
        if base.tone != plan.tone:
            base.tone = plan.tone
        return base

    def _append_agent_note(
        self,
        state: Dict[str, Any],
        plan: DraftPlan,
        sections: Dict[str, Any],
    ) -> list[str]:
        existing = state.get("memory", {}).get("episodic", {}).get("agent_notes") or []
        note = (
            f"Draft assembled with {len(sections)} sections; tone set to {plan.tone}"
        )
        return [*existing, note]

    def _apply_plan_structure(
        self, plan: DraftPlan, sections: Dict[str, Any]
    ) -> Dict[str, Any]:
        ordered_sections: Dict[str, Any] = {}
        for section_name in plan.structure:
            key = section_name.lower().replace(" ", "_")
            payload = json.loads(json.dumps(sections.get(key) or sections.get(section_name) or {}))
            if key == "executive_summary" and plan.key_messages:
                summary = payload.get("draft", "")
                highlights = "; ".join(plan.key_messages)
                payload["draft"] = f"{summary} | Key Messages: {highlights}".strip()
                payload["tone"] = plan.tone
            ordered_sections[key] = payload
        return ordered_sections

    async def run_from_state_async(
        self, state: Dict[str, Any], workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Route drafting orchestration through the L2 stack."""

        from .draft_orchestration import DraftOrchestratorStack

        orchestrator = DraftOrchestratorStack(self.context, self.debug_mode)
        return await orchestrator.run_async(
            state,
            workflow_id or state.get("metadata", {}).get("workflow_id", ""),
            state_snapshot=state,
        )
# ==== END SOURCE: /workspace/Agentic-Workflow/_latest_extract/stacks_v/drafting_execution.py ====
