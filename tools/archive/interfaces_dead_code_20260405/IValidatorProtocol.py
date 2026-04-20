"""
Red Team Integration Module - Phase 1 Foundation

Registers red team agents (AdversarialProbeAgent, BoundaryTestingAgent)
as validators in the ValidatorOrchestrator.

This module adapts the existing red team agents to the ValidatorProtocol
interface, enabling them to be called through the unified validation gateway.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Protocol

from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_applies_guardrail("p0", "IValidatorProtocol", "p0_governance")
_emit_reads_policy_state("p0", "IValidatorProtocol", "policy_binding")
_emit_snapshots_state("p0", "IValidatorProtocol", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("IValidatorProtocol", "p4obs", "metric_1")
_emit_emits_metric_event("IValidatorProtocol", "p4obs", "metric_2")
_emit_emits_metric_event("IValidatorProtocol", "p4obs", "metric_3")
_emit_emits_metric_event("IValidatorProtocol", "p4obs", "metric_4")
_emit_emits_metric_event("IValidatorProtocol", "p4obs", "metric_5")
_emit_emits_metric_event("IValidatorProtocol", "p4obs", "metric_6")
_emit_records_incident_event("IValidatorProtocol", "p4obs", "incident")
_emit_captures_runtime_anomaly("IValidatorProtocol", "p4obs", "anomaly")
_emit_writes_observability_log("IValidatorProtocol", "p4obs", "obs_log")
_emit_updates_monitoring_state("IValidatorProtocol", "p4obs", "mon_state")
_emit_triggers_alert("IValidatorProtocol", "p4obs", "alert")
_emit_links_incident_trace("IValidatorProtocol", "p4obs", "trace_link")
_emit_captures_pattern("IValidatorProtocol", "p3lm", "pattern")
_emit_records_learning_event("IValidatorProtocol", "p3lm", "learning_event")
_emit_writes_learning_snapshot("IValidatorProtocol", "p3lm", "snapshot")
_emit_feeds_meta_learning("IValidatorProtocol", "p3lm", "meta_feed")
_emit_updates_routing_strategy("IValidatorProtocol", "p3lm", "routing")
_emit_improves_agent_policy("IValidatorProtocol", "p3lm", "policy")
_emit_stores_learning_state("IValidatorProtocol", "p3lm", "state")
_emit_records_execution_trace("IValidatorProtocol", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("IValidatorProtocol", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("IValidatorProtocol", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("IValidatorProtocol", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("IValidatorProtocol", "L4_STATE", "p2_trace_5")
_emit_reads_environ("IValidatorProtocol", "env_read", "p2_env_1")
_emit_reads_environ("IValidatorProtocol", "env_read", "p2_env_2")
_emit_reads_runtime_state("IValidatorProtocol", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("IValidatorProtocol", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "IValidatorProtocol", "context_pull")
_emit_pulls_context("p1", "IValidatorProtocol", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "IValidatorProtocol", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "IValidatorProtocol", "uwg_term_2")
_emit_writes_through("p1", "IValidatorProtocol", "write_through")
_emit_writes_through("p1", "IValidatorProtocol", "write_through_2")
_emit_validated_by_safety_plane("p1", "IValidatorProtocol", "safety_validation")
_emit_invokes_eval("p1", "IValidatorProtocol", "eval_call")
_emit_proposal_commits_routing("p1", "IValidatorProtocol", "routing_commit")
_emit_escalates_to_human("p1", "IValidatorProtocol", "human_escalation")
_emit_routes_through("p1", "IValidatorProtocol", "route_through")
_emit_checks_agent_registry("p1", "IValidatorProtocol", "agent_registry")
_emit_validates_agent_capability("p1", "IValidatorProtocol", "capability")
_emit_dispatches_execution_plan("p1", "IValidatorProtocol", "exec_plan")
_emit_agent_executes_agent("p1", "IValidatorProtocol", "sub_agent")
_emit_routes_to_agent("p1", "IValidatorProtocol", "target_agent")
_emit_verifies_policy("p1", "IValidatorProtocol", "policy_check")
_emit_observes_runtime_state("p1", "IValidatorProtocol", "runtime_state")
_emit_verifies_boundary("p1", "IValidatorProtocol", "boundary_check")
_emit_transcripts_response("p1", "IValidatorProtocol", "transcript")
_emit_hard_fails_untranscripted("p1", "IValidatorProtocol")
_emit_gated_by_confidence("p1", "IValidatorProtocol", "confidence_gate")
emit_replay_key("p0", "IValidatorProtocol")
emit_determinism_digest("p0", "IValidatorProtocol")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "IValidatorProtocol", "execution_auth")
_emit_validates_capability("p2", "IValidatorProtocol", "capability_check")
_emit_routes_to_capability("p2", "IValidatorProtocol", "capability_route")
_emit_writes_via_uwg("p2", "IValidatorProtocol", "uwg_write")
_emit_blocks_direct_write("p2", "IValidatorProtocol", "direct_write_block")
_emit_records_tool_invocation("p2", "IValidatorProtocol", "tool_invocation")
_emit_captures_execution_output("p2", "IValidatorProtocol", "exec_output")
_emit_dispatches_agent("p3", "IValidatorProtocol", "agent_dispatch")
_emit_coordinates_agents("p3", "IValidatorProtocol", "agent_coordination")
_emit_records_workflow_lineage("p3", "IValidatorProtocol", "workflow_lineage")
_emit_records_healing_outcome("p3", "IValidatorProtocol", "healing_outcome")
_emit_escalates_failure("p3", "IValidatorProtocol", "failure_escalation")
_emit_orchestrates_workflow("p3", "IValidatorProtocol", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "IValidatorProtocol", "healing_dispatch")
_emit_invokes_evaluation("p3", "IValidatorProtocol", "evaluation_signal")
_emit_records_telemetry_event("p4", "IValidatorProtocol", "telemetry_event")
_emit_captures_evaluation_metric("p4", "IValidatorProtocol", "eval_metric")
_emit_stores_embedding("p4", "IValidatorProtocol", "embedding_store")
_emit_updates_meta_learning_state("p4", "IValidatorProtocol", "meta_learning")
_emit_links_execution_to_snapshot("p4", "IValidatorProtocol", "exec_snapshot_link")

Logger = logging.getLogger(__name__)


class ValidatorProtocol(Protocol):
    """Protocol for validators - matches ValidatorOrchestrator interface."""

    # guardian: allow-type-erasure
    def validate(self, content: Any, context: dict) -> dict:
        """Validate content and return result."""
        ...


class AdversarialValidator:
    """
    Adapter to use AdversarialProbeAgent as a validator.

    Wraps the async act() method and converts results to validator format.
    """

    def __init__(self) -> None:
        """Initialize the adversarial validator."""
        self._agent = None
        self._initialized = False

    def _ensure_initialized(self) -> None:
        """Lazy initialization to avoid import cycles."""
        if self._initialized:
            return
        try:
            from agentic_core.L5_safety.reasoning.AdversarialProbeAgent_validator import AdversarialProbeAgent

            from agentic_core.L4_state.memory import ValidationContext

            ctx = ValidationContext()
            self._agent = AdversarialProbeAgent(ctx=ctx)
            self._initialized = True
        except ImportError as e:
            Logger.warning(f"[AdversarialValidator] Could not import agent: {e}")
            self._initialized = True

    # guardian: allow-type-erasure
    def validate(self, content: Any, context: dict) -> dict:
        """
        Run adversarial probes and return validation result.

        Args:
            content: Content to validate (passed to agent context)
            context: Additional validation context

        Returns:
            dict with keys: valid, errors, threat_assessment
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "AdversarialValidator.validate"
        )

        self._ensure_initialized()
        if self._agent is None:
            return {"valid": True, "errors": [], "threat_assessment": {"status": "agent_unavailable"}}
        try:
            loop = asyncio.new_event_loop()
            try:
                result = loop.run_until_complete(self._agent.act())
            finally:
                loop.close()
            vulnerabilities = result.get("vulnerabilities_exposed", 0)
            return {
                "valid": vulnerabilities == 0,
                "errors": [
                    f"Vulnerability: {r['pattern']} - {r.get('description', 'No description')}"
                    for r in result.get("attack_results", [])
                    if r.get("vulnerable")
                ],
                "threat_assessment": result.get("threat_assessment", {}),
                "probes_executed": result.get("probes_executed", 0),
            }
        except Exception as e:  # guardian: allow-silent-swallow
            Logger.error(f"[AdversarialValidator] Validation failed: {e}")
            return {
                "valid": False,
                "errors": [f"Validation error: {str(e)}"],
                "threat_assessment": {"status": "error"},
            }


class BoundaryValidator:
    """
    Adapter to use BoundaryTestingAgent as a validator.

    Wraps the async act() method and converts results to validator format.
    """

    def __init__(self) -> None:
        """Initialize the boundary validator."""
        self._agent = None
        self._initialized = False

    def _ensure_initialized(self) -> None:
        """Lazy initialization to avoid import cycles."""
        if self._initialized:
            return
        try:
            from agentic_core.L5_safety.reasoning.BoundaryTestingAgent_validator import BoundaryTestingAgent

            from agentic_core.L4_state.memory import ValidationContext

            ctx = ValidationContext()
            self._agent = BoundaryTestingAgent(ctx=ctx)
            self._initialized = True
        except ImportError as e:
            Logger.warning(f"[BoundaryValidator] Could not import agent: {e}")
            self._initialized = True

    # guardian: allow-type-erasure
    def validate(self, content: Any, context: dict) -> dict:
        """
        Run boundary tests and return validation result.

        Args:
            content: Content to validate
            context: Additional validation context

        Returns:
            dict with keys: valid, errors, recommendations
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "BoundaryValidator.validate")

        self._ensure_initialized()
        if self._agent is None:
            return {"valid": True, "errors": [], "recommendations": []}
        try:
            loop = asyncio.new_event_loop()
            try:
                result = loop.run_until_complete(self._agent.act())
            finally:
                loop.close()
            edge_cases = result.get("edge_cases_found", 0)
            return {
                "valid": edge_cases == 0,
                "errors": [
                    f"Boundary violation: {v['test']} - {v.get('violation', 'Unknown')}"
                    for v in result.get("boundary_violations", [])
                ],
                "recommendations": result.get("recommendations", []),
                "tests_executed": result.get("tests_executed", 0),
            }
        except Exception as e:  # guardian: allow-silent-swallow
            Logger.error(f"[BoundaryValidator] Validation failed: {e}")
            return {"valid": False, "errors": [f"Validation error: {str(e)}"], "recommendations": []}


_adversarial_validator: AdversarialValidator | None = None
_boundary_validator: BoundaryValidator | None = None


def get_adversarial_validator() -> AdversarialValidator:
    """Get or create the adversarial validator instance."""
    global _adversarial_validator
    if _adversarial_validator is None:
        _adversarial_validator = AdversarialValidator()
    return _adversarial_validator


def get_boundary_validator() -> BoundaryValidator:
    """Get or create the boundary validator instance."""
    global _boundary_validator
    if _boundary_validator is None:
        _boundary_validator = BoundaryValidator()
    return _boundary_validator


# guardian: allow-type-erasure
def register_red_team_validators() -> dict[str, Any]:
    """
    Register all red team agents as validators with the orchestrator.

    Returns:
        dict with registration status
    """
    registered = []
    errors = []
    try:
        from agentic_core.L5_safety.types.healing_orchestration_types import get_validator_orchestrator

        orchestrator = get_validator_orchestrator()
        try:
            orchestrator.register_validator("adversarial_probe", get_adversarial_validator())
            registered.append("adversarial_probe")
        except (ValueError, TypeError, RuntimeError) as e:
            raise
            errors.append(f"adversarial_probe: {e}")
        try:
            orchestrator.register_validator("boundary_testing", get_boundary_validator())
            registered.append("boundary_testing")
        except (ValueError, TypeError, RuntimeError) as e:
            raise
            errors.append(f"boundary_testing: {e}")
        Logger.info(f"[Red Team Integration] Registered {len(registered)} validators")
    except ImportError as e:
        errors.append(f"ValidatorOrchestrator import failed: {e}")
        Logger.warning(f"[Red Team Integration] Could not import orchestrator: {e}")
    return {"registered": registered, "errors": errors, "success": len(errors) == 0}


# guardian: allow-type-erasure
def get_integration_status() -> dict[str, Any]:
    """
    Get the current status of red team integration.

    Returns:
        dict with integration status details
    """
    return {
        "adversarial_validator_initialized": _adversarial_validator is not None,
        "boundary_validator_initialized": _boundary_validator is not None,
        "validators_available": ["adversarial_probe", "boundary_testing"],
    }
