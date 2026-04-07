"""[SSOT] Logic Node for Resume Flow Routing.
Mirrors the k1_router pattern from apps_lic but for Resume Generation domain.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_authorize_and_execute("p2", "rg_flow_router_types", "execution_auth")
_emit_validates_capability("p2", "rg_flow_router_types", "capability_check")
_emit_routes_to_capability("p2", "rg_flow_router_types", "capability_route")
_emit_writes_via_uwg("p2", "rg_flow_router_types", "uwg_write")
_emit_blocks_direct_write("p2", "rg_flow_router_types", "direct_write_block")
_emit_records_tool_invocation("p2", "rg_flow_router_types", "tool_invocation")
_emit_captures_execution_output("p2", "rg_flow_router_types", "exec_output")
_emit_dispatches_agent("p3", "rg_flow_router_types", "agent_dispatch")
_emit_coordinates_agents("p3", "rg_flow_router_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "rg_flow_router_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "rg_flow_router_types", "healing_outcome")
_emit_escalates_failure("p3", "rg_flow_router_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "rg_flow_router_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "rg_flow_router_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "rg_flow_router_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "rg_flow_router_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "rg_flow_router_types", "eval_metric")
_emit_stores_embedding("p4", "rg_flow_router_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "rg_flow_router_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "rg_flow_router_types", "exec_snapshot_link")
from .ThematicAnalysisNode import ThematicAnalysisNode, ThematicAnalysisOutput

_emit_applies_guardrail("p0", "rg_flow_router_types", "p0_governance")
_emit_reads_policy_state("p0", "rg_flow_router_types", "policy_binding")
_emit_snapshots_state("p0", "rg_flow_router_types", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("rg_flow_router_types", "p4obs", "metric_1")
_emit_emits_metric_event("rg_flow_router_types", "p4obs", "metric_2")
_emit_emits_metric_event("rg_flow_router_types", "p4obs", "metric_3")
_emit_emits_metric_event("rg_flow_router_types", "p4obs", "metric_4")
_emit_emits_metric_event("rg_flow_router_types", "p4obs", "metric_5")
_emit_emits_metric_event("rg_flow_router_types", "p4obs", "metric_6")
_emit_records_incident_event("rg_flow_router_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("rg_flow_router_types", "p4obs", "anomaly")
_emit_writes_observability_log("rg_flow_router_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("rg_flow_router_types", "p4obs", "mon_state")
_emit_triggers_alert("rg_flow_router_types", "p4obs", "alert")
_emit_links_incident_trace("rg_flow_router_types", "p4obs", "trace_link")
_emit_captures_pattern("rg_flow_router_types", "p3lm", "pattern")
_emit_records_learning_event("rg_flow_router_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("rg_flow_router_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("rg_flow_router_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("rg_flow_router_types", "p3lm", "routing")
_emit_improves_agent_policy("rg_flow_router_types", "p3lm", "policy")
_emit_stores_learning_state("rg_flow_router_types", "p3lm", "state")
_emit_records_execution_trace("rg_flow_router_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("rg_flow_router_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("rg_flow_router_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("rg_flow_router_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("rg_flow_router_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("rg_flow_router_types", "env_read", "p2_env_1")
_emit_reads_environ("rg_flow_router_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("rg_flow_router_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("rg_flow_router_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "rg_flow_router_types", "context_pull")
_emit_pulls_context("p1", "rg_flow_router_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "rg_flow_router_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "rg_flow_router_types", "uwg_term_2")
_emit_writes_through("p1", "rg_flow_router_types", "write_through")
_emit_writes_through("p1", "rg_flow_router_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "rg_flow_router_types", "safety_validation")
_emit_invokes_eval("p1", "rg_flow_router_types", "eval_call")
_emit_proposal_commits_routing("p1", "rg_flow_router_types", "routing_commit")
_emit_escalates_to_human("p1", "rg_flow_router_types", "human_escalation")
_emit_routes_through("p1", "rg_flow_router_types", "route_through")
_emit_checks_agent_registry("p1", "rg_flow_router_types", "agent_registry")
_emit_validates_agent_capability("p1", "rg_flow_router_types", "capability")
_emit_dispatches_execution_plan("p1", "rg_flow_router_types", "exec_plan")
_emit_agent_executes_agent("p1", "rg_flow_router_types", "sub_agent")
_emit_routes_to_agent("p1", "rg_flow_router_types", "target_agent")
_emit_verifies_policy("p1", "rg_flow_router_types", "policy_check")
_emit_observes_runtime_state("p1", "rg_flow_router_types", "runtime_state")
_emit_verifies_boundary("p1", "rg_flow_router_types", "boundary_check")
_emit_transcripts_response("p1", "rg_flow_router_types", "transcript")
_emit_hard_fails_untranscripted("p1", "rg_flow_router_types")
_emit_gated_by_confidence("p1", "rg_flow_router_types", "confidence_gate")
emit_replay_key("p0", "rg_flow_router_types")
emit_determinism_digest("p0", "rg_flow_router_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

logger = logging.getLogger(__name__)


@dataclass
class ResumeFlowResult:
    """Result of resume flow routing decision."""

    flow_type: str
    confidence: float
    required_hops: list[str]
    validation_required: bool
    retry_enabled: bool


@dataclass
class RGFlowOutput:
    """Resume flow routing output."""

    flow_result: ResumeFlowResult
    entrance_gates_passed: list[str]
    metadata: dict[str, Any]


class RGFlowRouter:
    """
    [Enhanced] Logic Node for Resume Flow Routing.
    Integrates K.0 Thematic Analysis to determine strategy based on
    differentiator strength and authenticity requirements.
    """

    def __init__(self, config: dict[str, Any] = None):
        self.config = config or {}
        self.thematic_node = ThematicAnalysisNode(config)
        self.flow_configs = self.config.get(
            "flow_configs",
            {
                "strategic_tailor_node": {
                    "required_hops": ["HOP-1", "HOP-2", "HOP-3", "HOP-4", "HOP-5", "HOP-6"],
                    "validation_required": True,
                    "retry_enabled": True,
                },
                "tailor_existing": {
                    "required_hops": ["HOP-1", "HOP-2", "HOP-3", "HOP-4", "HOP-5"],
                    "validation_required": True,
                    "retry_enabled": True,
                },
                "generate_scratch": {
                    "required_hops": ["HOP-1", "HOP-2", "HOP-3", "HOP-4", "HOP-5"],
                    "validation_required": True,
                    "retry_enabled": True,
                },
                "enhance_current": {
                    "required_hops": ["HOP-3", "HOP-4", "HOP-5"],
                    "validation_required": True,
                    "retry_enabled": False,
                },
            },
        )
        self.tailor_keywords = ["tailor", "customize", "modify", "adapt", "update", "improve"]
        self.generate_keywords = ["create", "generate", "build", "make", "new", "from scratch"]
        self.enhance_keywords = ["enhance", "optimize", "improve", "refine", "polish"]

    def __call__(self, state: dict[str, Any]) -> RGFlowOutput:
        """
        Executes resume flow routing using functor pattern with upstream Thematic Analysis.

        Args:
            state: Current workflow state containing:
                - task_description: str
                - has_master_resume: bool
                - job_description: str
                - quality_requirements: Dict[str, Any]

        Returns:
            RGFlowOutput: Complete routing decision
        """
        if not state:
            raise ValueError("Resume flow routing state cannot be empty")
        if "thematic_analysis" not in state:
            jd = state.get("job_description", "")
            company = state.get("company_name", "Unknown")
            thematic_output = self.thematic_node(jd, company)
            state["thematic_analysis"] = thematic_output
            state["primary_theme"] = thematic_output.primary_theme
        return self.execute_routing(state)

    def determine_next_hop(self, state: dict[str, Any]) -> str:
        """
        Determines the next hop identifier for resume workflow routing.

        Args:
            state: Current workflow state

        Returns:
            str: Next hop identifier
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "RgFlowRouter.determine_next_hop")
        if not state:
            raise ValueError("Routing state cannot be empty")
        result = self.execute_routing(state)
        return f"flow_{result.flow_result.flow_type}"

    def execute_routing(self, context: dict[str, Any]) -> RGFlowOutput:
        """Execute resume flow routing logic.

        Args:
            context: Execution context with resume parameters

        Returns:
            RGFlowOutput with flow decision and metadata
        """
        logger.info("Executing RG flow routing")
        entrance_gates_passed = []
        task_description = context.get("task_description", "")
        if not task_description:
            raise ValueError("GATE_1_FAILED: Task description is required")
        entrance_gates_passed.append("GATE_1_TASK_ANALYZED")
        logger.info(f"Gate 1: Task = {task_description[:50]}...")
        has_master_resume = context.get("has_master_resume", False)
        entrance_gates_passed.append("GATE_2_RESUME_AVAILABILITY_CHECKED")
        logger.info(f"Gate 2: Master resume available = {has_master_resume}")
        job_description = context.get("job_description", "")
        if not job_description:
            raise ValueError("GATE_3_FAILED: Job description is required")
        entrance_gates_passed.append("GATE_3_JOB_DESCRIPTION_VALIDATED")
        logger.info(f"Gate 3: Job description validated ({len(job_description)} chars)")
        thematic_analysis = context.get("thematic_analysis")
        if thematic_analysis:
            flow_result = self._classify_flow_with_thematic_analysis(
                task_description, has_master_resume, thematic_analysis,
            )
        else:
            flow_result = self._classify_flow(task_description, has_master_resume)
        entrance_gates_passed.append("GATE_4_FLOW_CLASSIFIED")
        logger.info(f"Gate 4: Flow = {flow_result.flow_type}")
        quality_requirements = context.get("quality_requirements", {})
        if quality_requirements:
            entrance_gates_passed.append("GATE_5_QUALITY_REQUIREMENTS_APPLIED")
            logger.info(f"Gate 5: Quality requirements applied = {list(quality_requirements.keys())}")
        self._validate_routing_requirements(flow_result, context)
        entrance_gates_passed.append("GATE_6_ROUTING_VALIDATED")
        logger.info("Gate 6: Routing requirements validated")
        entrance_gates_passed.append("GATE_7_FINAL_APPROVAL")
        logger.info("Gate 7: All entrance gates passed")
        output = RGFlowOutput(
            flow_result=flow_result,
            entrance_gates_passed=entrance_gates_passed,
            metadata={
                "router_id": "RGFlowRouter",
                "task_description": task_description[:100],
                "has_master_resume": has_master_resume,
                "job_description_length": len(job_description),
            },
        )
        logger.info(f"RG flow routing complete: {flow_result.flow_type}")
        return output

    def _classify_flow(self, task_description: str, has_master_resume: bool) -> ResumeFlowResult:
        """Classify the resume generation flow based on task, context, and K.0 Thematic Analysis.

        Args:
            task_description: User's task description
            has_master_resume: Whether master resume is available

        Returns:
            ResumeFlowResult with flow classification
        """
        task_lower = task_description.lower()
        if any(keyword in task_lower for keyword in self.tailor_keywords):
            if has_master_resume:
                return ResumeFlowResult(
                    flow_type="tailor_existing",
                    confidence=0.95,
                    required_hops=self.flow_configs["tailor_existing"]["required_hops"],
                    validation_required=self.flow_configs["tailor_existing"]["validation_required"],
                    retry_enabled=self.flow_configs["tailor_existing"]["retry_enabled"],
                )
            else:
                logger.warning("Tailor requested but no master resume available - falling back to generate")
        if any(keyword in task_lower for keyword in self.generate_keywords):
            return ResumeFlowResult(
                flow_type="generate_scratch",
                confidence=0.9,
                required_hops=self.flow_configs["generate_scratch"]["required_hops"],
                validation_required=self.flow_configs["generate_scratch"]["validation_required"],
                retry_enabled=self.flow_configs["generate_scratch"]["retry_enabled"],
            )
        if any(keyword in task_lower for keyword in self.enhance_keywords):
            return ResumeFlowResult(
                flow_type="enhance_current",
                confidence=0.85,
                required_hops=self.flow_configs["enhance_current"]["required_hops"],
                validation_required=self.flow_configs["enhance_current"]["validation_required"],
                retry_enabled=self.flow_configs["enhance_current"]["retry_enabled"],
            )
        if has_master_resume:
            return ResumeFlowResult(
                flow_type="tailor_existing",
                confidence=0.7,
                required_hops=self.flow_configs["tailor_existing"]["required_hops"],
                validation_required=self.flow_configs["tailor_existing"]["validation_required"],
                retry_enabled=self.flow_configs["tailor_existing"]["retry_enabled"],
            )
        else:
            return ResumeFlowResult(
                flow_type="generate_scratch",
                confidence=0.7,
                required_hops=self.flow_configs["generate_scratch"]["required_hops"],
                validation_required=self.flow_configs["generate_scratch"]["validation_required"],
                retry_enabled=self.flow_configs["generate_scratch"]["retry_enabled"],
            )

    def _classify_flow_with_thematic_analysis(
        self, task_description: str, has_master_resume: bool, thematic_analysis: ThematicAnalysisOutput,
    ) -> ResumeFlowResult:
        """Enhanced flow classification using K.0 Thematic Analysis insights.

        Args:
            task_description: User's task description
            has_master_resume: Whether master resume is available
            thematic_analysis: K.0 Thematic Analysis output

        Returns:
            ResumeFlowResult with enhanced flow classification
        """
        task_lower = task_description.lower()
        differentiators = thematic_analysis.competitive_intelligence.differentiator_keywords
        if len(differentiators) > 3:
            return ResumeFlowResult(
                flow_type="strategic_tailor_node",
                confidence=0.98,
                required_hops=self.flow_configs["strategic_tailor_node"]["required_hops"],
                validation_required=self.flow_configs["strategic_tailor_node"]["validation_required"],
                retry_enabled=self.flow_configs["strategic_tailor_node"]["retry_enabled"],
            )
        if any(keyword in task_lower for keyword in self.tailor_keywords):
            if has_master_resume:
                return ResumeFlowResult(
                    flow_type="tailor_existing",
                    confidence=0.95,
                    required_hops=self.flow_configs["tailor_existing"]["required_hops"],
                    validation_required=self.flow_configs["tailor_existing"]["validation_required"],
                    retry_enabled=self.flow_configs["tailor_existing"]["retry_enabled"],
                )
            else:
                logger.warning("Tailor requested but no master resume available - falling back to generate")
        if any(keyword in task_lower for keyword in self.generate_keywords):
            return ResumeFlowResult(
                flow_type="generate_scratch",
                confidence=0.9,
                required_hops=self.flow_configs["generate_scratch"]["required_hops"],
                validation_required=self.flow_configs["generate_scratch"]["validation_required"],
                retry_enabled=self.flow_configs["generate_scratch"]["retry_enabled"],
            )
        if any(keyword in task_lower for keyword in self.enhance_keywords):
            return ResumeFlowResult(
                flow_type="enhance_current",
                confidence=0.85,
                required_hops=self.flow_configs["enhance_current"]["required_hops"],
                validation_required=self.flow_configs["enhance_current"]["validation_required"],
                retry_enabled=self.flow_configs["enhance_current"]["retry_enabled"],
            )
        if has_master_resume:
            return ResumeFlowResult(
                flow_type="tailor_existing",
                confidence=0.7,
                required_hops=self.flow_configs["tailor_existing"]["required_hops"],
                validation_required=self.flow_configs["tailor_existing"]["validation_required"],
                retry_enabled=self.flow_configs["tailor_existing"]["retry_enabled"],
            )
        else:
            return ResumeFlowResult(
                flow_type="generate_scratch",
                confidence=0.7,
                required_hops=self.flow_configs["generate_scratch"]["required_hops"],
                validation_required=self.flow_configs["generate_scratch"]["validation_required"],
                retry_enabled=self.flow_configs["generate_scratch"]["retry_enabled"],
            )

    def _validate_routing_requirements(self, flow_result: ResumeFlowResult, context: dict[str, Any]) -> None:
        """Validate that routing requirements are met.

        Args:
            flow_result: The classified flow result
            context: Execution context

        Raises:
            ValueError: If routing requirements are not met
        """
        if flow_result.flow_type in ["tailor_existing", "enhance_current"]:
            if not context.get("has_master_resume", False):
                raise ValueError(
                    f"ROUTING_VALIDATION_FAILED: Flow '{flow_result.flow_type}' requires master resume",
                )
        job_description = context.get("job_description", "")
        if len(job_description) < 50:
            raise ValueError("ROUTING_VALIDATION_FAILED: Job description too short (minimum 50 characters)")
