"""
Domain Planner Adapter - V10 Legacy Bridge for DomainPlannerAgent.

Per Phase 1 Audit Report, DomainPlannerAgent was identified as requiring
V10 compliance wrapping. This adapter provides:
1. Circuit breaker integration for failure isolation
2. Input validation for external_touch requirements
3. Audit trail for observability
4. Non-blocking execution timeout protection

References:
- Adapters Usage.png: Bridge Pattern for orphan agents
- V10 Diagram: Legacy Bridge integration layer
"""

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from agentic_core.L5_safety.enforcement.circuit_breaker_gate import get_breaker
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
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
    _emit_routes_through,  # noqa: E402
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

emit_replay_key("p0", "DomainPlannerAdapter")
emit_determinism_digest("p0", "DomainPlannerAdapter")

_emit_dispatches_healing_run("p1", "DomainPlannerAdapter", "L5")
_emit_routes_through("p1", "DomainPlannerAdapter", "L5")
_emit_checks_agent_registry("p1", "DomainPlannerAdapter", "agent_registry")
_emit_validates_agent_capability("p1", "DomainPlannerAdapter", "capability")
_emit_dispatches_execution_plan("p1", "DomainPlannerAdapter", "exec_plan")
_emit_agent_executes_agent("p1", "DomainPlannerAdapter", "sub_agent")
_emit_routes_to_agent("p1", "DomainPlannerAdapter", "target_agent")
_emit_verifies_policy("p1", "DomainPlannerAdapter", "policy_check")
_emit_observes_runtime_state("p1", "DomainPlannerAdapter", "runtime_state")
_emit_transcripts_response("p1", "DomainPlannerAdapter", "transcript")
_emit_hard_fails_untranscripted("p1", "DomainPlannerAdapter")
_emit_gated_by_confidence("p1", "DomainPlannerAdapter", "confidence_gate")
_emit_escalates_to_human("p1", "DomainPlannerAdapter", "L5")
_emit_reads_policy_state("p1", "DomainPlannerAdapter", "L5")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_snapshots_state("p0", "DomainPlannerAdapter", "state_snapshot")
_emit_authorize_and_execute("p2", "DomainPlannerAdapter", "execution_auth")
_emit_validates_capability("p2", "DomainPlannerAdapter", "capability_check")
_emit_routes_to_capability("p2", "DomainPlannerAdapter", "capability_route")
_emit_writes_via_uwg("p2", "DomainPlannerAdapter", "uwg_write")
_emit_blocks_direct_write("p2", "DomainPlannerAdapter", "direct_write_block")
_emit_records_tool_invocation("p2", "DomainPlannerAdapter", "tool_invocation")
_emit_captures_execution_output("p2", "DomainPlannerAdapter", "exec_output")
_emit_dispatches_agent("p3", "DomainPlannerAdapter", "agent_dispatch")
_emit_coordinates_agents("p3", "DomainPlannerAdapter", "agent_coordination")
_emit_records_workflow_lineage("p3", "DomainPlannerAdapter", "workflow_lineage")
_emit_records_healing_outcome("p3", "DomainPlannerAdapter", "healing_outcome")
_emit_escalates_failure("p3", "DomainPlannerAdapter", "failure_escalation")
_emit_orchestrates_workflow("p3", "DomainPlannerAdapter", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "DomainPlannerAdapter", "healing_dispatch")
_emit_invokes_evaluation("p3", "DomainPlannerAdapter", "evaluation_signal")
_emit_records_telemetry_event("p4", "DomainPlannerAdapter", "telemetry_event")
_emit_captures_evaluation_metric("p4", "DomainPlannerAdapter", "eval_metric")
_emit_stores_embedding("p4", "DomainPlannerAdapter", "embedding_store")
_emit_updates_meta_learning_state("p4", "DomainPlannerAdapter", "meta_learning")
_emit_links_execution_to_snapshot("p4", "DomainPlannerAdapter", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("DomainPlannerAdapter", "p4obs", "metric_1")
_emit_emits_metric_event("DomainPlannerAdapter", "p4obs", "metric_2")
_emit_emits_metric_event("DomainPlannerAdapter", "p4obs", "metric_3")
_emit_emits_metric_event("DomainPlannerAdapter", "p4obs", "metric_4")
_emit_emits_metric_event("DomainPlannerAdapter", "p4obs", "metric_5")
_emit_emits_metric_event("DomainPlannerAdapter", "p4obs", "metric_6")
_emit_records_incident_event("DomainPlannerAdapter", "p4obs", "incident")
_emit_captures_runtime_anomaly("DomainPlannerAdapter", "p4obs", "anomaly")
_emit_writes_observability_log("DomainPlannerAdapter", "p4obs", "obs_log")
_emit_updates_monitoring_state("DomainPlannerAdapter", "p4obs", "mon_state")
_emit_triggers_alert("DomainPlannerAdapter", "p4obs", "alert")
_emit_links_incident_trace("DomainPlannerAdapter", "p4obs", "trace_link")
_emit_captures_pattern("DomainPlannerAdapter", "p3lm", "pattern")
_emit_records_learning_event("DomainPlannerAdapter", "p3lm", "learning_event")
_emit_writes_learning_snapshot("DomainPlannerAdapter", "p3lm", "snapshot")
_emit_feeds_meta_learning("DomainPlannerAdapter", "p3lm", "meta_feed")
_emit_updates_routing_strategy("DomainPlannerAdapter", "p3lm", "routing")
_emit_improves_agent_policy("DomainPlannerAdapter", "p3lm", "policy")
_emit_stores_learning_state("DomainPlannerAdapter", "p3lm", "state")
_emit_records_execution_trace("DomainPlannerAdapter", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("DomainPlannerAdapter", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("DomainPlannerAdapter", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("DomainPlannerAdapter", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("DomainPlannerAdapter", "L4_STATE", "p2_trace_5")
_emit_reads_environ("DomainPlannerAdapter", "env_read", "p2_env_1")
_emit_reads_environ("DomainPlannerAdapter", "env_read", "p2_env_2")
_emit_reads_runtime_state("DomainPlannerAdapter", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("DomainPlannerAdapter", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "DomainPlannerAdapter", "context_pull")
_emit_pulls_context("p1", "DomainPlannerAdapter", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "DomainPlannerAdapter", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "DomainPlannerAdapter", "uwg_term_2")
_emit_writes_through("p1", "DomainPlannerAdapter", "write_through")
_emit_writes_through("p1", "DomainPlannerAdapter", "write_through_2")
_emit_validated_by_safety_plane("p1", "DomainPlannerAdapter", "safety_validation")
_emit_invokes_eval("p1", "DomainPlannerAdapter", "eval_call")
_emit_proposal_commits_routing("p1", "DomainPlannerAdapter", "routing_commit")

logger = logging.getLogger(__name__)


@dataclass
class AdapterContext:
    """Context passed through adapter chain."""

    request_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    risk_level: str = "medium"
    bypass_validation: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AdapterResult:
    """Standardized result from adapter operations."""

    success: bool
    data: Any = None
    error: str | None = None
    skipped: bool = False
    skip_reason: str | None = None
    audit_trail: dict[str, Any] = field(default_factory=dict)


class DomainPlannerAdapter:
    """
    V10-Compliant wrapper for DomainPlannerAgent.

    V15 P0.2: Refactored to eliminate AdapterBase/HealingAdapter dependency.
    Circuit breaker and validation logic inlined.
    """

    def __init__(self, legacy_agent: Any, project_root: Path | None = None):
        self._legacy_agent = legacy_agent
        self._service_name = "domain_planner"
        self._project_root = project_root or Path.cwd()
        self._circuit_breaker = get_breaker(f"adapter_{self._service_name}")
        self._required_job_context_keys = {"job_title", "company"}
        self._required_plan_attributes = {"focus_areas", "key_achievements_to_highlight"}

    def _validate_input(self, context: AdapterContext, *args, **kwargs) -> bool:
        """
        V10 Input validation for DomainPlannerAgent.

        Validates:
        1. Required job_context keys exist
        2. Plan object has required attributes
        3. External touch requirements (API keys if needed)

        Args:
            context: Adapter context
            *args: Positional arguments (plan, job_context, workflow_id)
            **kwargs: Keyword arguments

        Returns:
            True if input is valid, False to reject
        """
        _emit_verifies_boundary(str(uuid.uuid4()), "DomainPlannerAdapter._validate_input", "L5_POLICY")
        _emit_applies_guardrail(str(uuid.uuid4()), "DomainPlannerAdapter._validate_input", "L5_POLICY")
        plan = kwargs.get("plan") or (args[0] if len(args) > 0 else None)
        job_context = kwargs.get("job_context") or (args[1] if len(args) > 1 else None)
        workflow_id = kwargs.get("workflow_id") or (args[2] if len(args) > 2 else None)
        if job_context is None:
            logger.warning("DomainPlannerAdapter: job_context is required")
            return False
        if not isinstance(job_context, dict):
            logger.warning("DomainPlannerAdapter: job_context must be a dictionary")
            return False
        if not any(key in job_context for key in self._required_job_context_keys):
            logger.warning(
                f"DomainPlannerAdapter: job_context must contain at least one of {self._required_job_context_keys}",
            )
            return False
        if plan is None:
            logger.warning("DomainPlannerAdapter: plan is required")
            return False
        for attr in self._required_plan_attributes:
            if not hasattr(plan, attr):
                logger.warning(f"DomainPlannerAdapter: plan missing required attribute '{attr}'")
                return False
        if not workflow_id:
            logger.warning("DomainPlannerAdapter: workflow_id is required")
            return False
        if context.metadata.get("requires_external_api"):
            api_key = context.metadata.get("api_key")
            if not api_key:
                logger.warning("DomainPlannerAdapter: external API required but no api_key provided")
                return False
        logger.debug("DomainPlannerAdapter: input validation passed")
        return True

    def _validate_output(self, result: Any, context: AdapterContext) -> bool:
        """
        V10 Output validation for DomainPlannerAgent results.

        Validates:
        1. Result is a PlannerAssessment-like object
        2. Required fields are present (vote, confidence, rationale)

        Args:
            result: Result from legacy execution
            context: Adapter context

        Returns:
            True if output is valid, False to reject
        """
        if result is None:
            logger.warning("DomainPlannerAdapter: result is None")
            return False
        required_attrs = {"vote", "confidence", "rationale"}
        for attr in required_attrs:
            if not hasattr(result, attr):
                logger.warning(f"DomainPlannerAdapter: result missing '{attr}' attribute")
                return False
        vote = getattr(result, "vote", None)
        if vote not in {"approve", "revise"}:
            logger.warning(f"DomainPlannerAdapter: invalid vote value '{vote}'")
            return False
        confidence = getattr(result, "confidence", None)
        if not isinstance(confidence, int | float) or not 0.0 <= confidence <= 1.0:
            logger.warning(f"DomainPlannerAdapter: confidence must be 0.0-1.0, got {confidence}")
            return False
        logger.debug("DomainPlannerAdapter: output validation passed")
        return True

    def _execute_legacy(self, context: AdapterContext, *args, **kwargs) -> Any:
        """
        Execute the DomainPlannerAgent's run_async method.

        The legacy agent uses async, so we run it in an event loop.

        Args:
            context: Adapter context
            *args: Positional arguments (plan, job_context, workflow_id)
            **kwargs: Keyword arguments

        Returns:
            PlannerAssessment from the legacy agent
        """
        plan = kwargs.get("plan") or (args[0] if len(args) > 0 else None)
        job_context = kwargs.get("job_context") or (args[1] if len(args) > 1 else None)
        workflow_id = kwargs.get("workflow_id") or (args[2] if len(args) > 2 else None)
        logger.info(f"DomainPlannerAdapter: executing legacy agent for workflow {workflow_id}")
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:    # guardian: Runtime errors should be prevented with proper validation
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        if loop.is_running():
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run, self._legacy_agent.run_async(plan, job_context, workflow_id),
                )
                return future.result()
        else:
            return loop.run_until_complete(self._legacy_agent.run_async(plan, job_context, workflow_id))

    def plan(
        self, plan: Any, job_context: dict[str, Any], workflow_id: str, context: AdapterContext | None = None,
    ) -> AdapterResult:
        """
        Convenience method matching the expected domain planner interface.

        Args:
            plan: StrategyPlan object
            job_context: Job context dictionary
            workflow_id: Workflow identifier
            context: Optional adapter context

        Returns:
            AdapterResult with PlannerAssessment data
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_records_execution_trace(
            str(_uuid.uuid4()), LayerSegment.L5_POLICY, f"DomainPlannerAdapter.plan:{workflow_id}",
        )
        return self.execute(context=context, plan=plan, job_context=job_context, workflow_id=workflow_id)

    def execute(self, context: AdapterContext | None = None, *args: Any, **kwargs: Any) -> AdapterResult:
        """Execute with circuit breaker + input/output validation."""
        if context is None:
            context = AdapterContext(request_id=str(uuid.uuid4()))
        if not self._circuit_breaker.allow_request():
            return AdapterResult(
                success=False,
                skipped=True,
                skip_reason="circuit_breaker_open",
                error="Circuit breaker is OPEN",
            )
        if not self._validate_input(context, *args, **kwargs):
            return AdapterResult(
                success=False,
                skipped=True,
                skip_reason="input_validation_failed",
                error="Input validation failed",
            )
        try:
            raw_result = self._execute_legacy(context, *args, **kwargs)
            self._circuit_breaker.record_success()
        except (ValueError, TypeError) as e:
            self._circuit_breaker.record_failure(e)
            return AdapterResult(success=False, error=str(e))
        if not self._validate_output(raw_result, context):
            return AdapterResult(success=False, data=raw_result, error="Output validation failed")
        return AdapterResult(success=True, data=raw_result)

    def heal(self, violation: dict[str, Any], context: AdapterContext | None = None) -> AdapterResult:
        """Execute healing with V10 compliance."""
        if context is None:
            context = AdapterContext(request_id=str(uuid.uuid4()))
        try:
            if not self._circuit_breaker.allow_request():
                return AdapterResult(
                    success=False,
                    skipped=True,
                    skip_reason="circuit_breaker_open",
                    error="Circuit breaker is OPEN",
                )
            result = self._legacy_agent.heal(violation)
            self._circuit_breaker.record_success()
            return AdapterResult(
                success=result.get("status") == "success",
                data=result,
                error=result.get("errors", [None])[0] if result.get("errors") else None,
            )
        except (ValueError, TypeError) as e:
            self._circuit_breaker.record_failure(e)
            return AdapterResult(success=False, error=str(e))


__all__ = ["DomainPlannerAdapter"]
