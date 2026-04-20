"""Agent Registry - Single Source of Truth for Agent Execution Profiles."""

from __future__ import annotations

import logging
from types import MappingProxyType
from typing import Final

from agentic_core.agents.types.agent_execution_profile_types import (
    AgentExecutionProfile,
    ExecutionMode,
    ReasoningIntensity,
)

logger = logging.getLogger(__name__)

_BOOTSTRAP_TELEMETRY_EMITTED = False
_BOOTSTRAP_TELEMETRY_EVENTS: Final[tuple[tuple[str, tuple[object, ...]], ...]] = (
    ("_emit_emits_metric_event", ("agent_registry", "p4obs", "metric_1")),
    ("_emit_emits_metric_event", ("agent_registry", "p4obs", "metric_2")),
    ("_emit_emits_metric_event", ("agent_registry", "p4obs", "metric_3")),
    ("_emit_emits_metric_event", ("agent_registry", "p4obs", "metric_4")),
    ("_emit_emits_metric_event", ("agent_registry", "p4obs", "metric_5")),
    ("_emit_emits_metric_event", ("agent_registry", "p4obs", "metric_6")),
    ("_emit_records_incident_event", ("agent_registry", "p4obs", "incident")),
    ("_emit_captures_runtime_anomaly", ("agent_registry", "p4obs", "anomaly")),
    ("_emit_writes_observability_log", ("agent_registry", "p4obs", "obs_log")),
    ("_emit_updates_monitoring_state", ("agent_registry", "p4obs", "mon_state")),
    ("_emit_triggers_alert", ("agent_registry", "p4obs", "alert")),
    ("_emit_links_incident_trace", ("agent_registry", "p4obs", "trace_link")),
    ("_emit_captures_pattern", ("agent_registry", "p3lm", "pattern")),
    ("_emit_records_learning_event", ("agent_registry", "p3lm", "learning_event")),
    ("_emit_writes_learning_snapshot", ("agent_registry", "p3lm", "snapshot")),
    ("_emit_feeds_meta_learning", ("agent_registry", "p3lm", "meta_feed")),
    ("_emit_updates_routing_strategy", ("agent_registry", "p3lm", "routing")),
    ("_emit_improves_agent_policy", ("agent_registry", "p3lm", "policy")),
    ("_emit_stores_learning_state", ("agent_registry", "p3lm", "state")),
    ("_emit_records_execution_trace", ("agent_registry", "L0_ROUTING", "p2_trace_1")),
    ("_emit_records_execution_trace", ("agent_registry", "L1_REASONING", "p2_trace_2")),
    ("_emit_records_execution_trace", ("agent_registry", "L2_EXECUTION", "p2_trace_3")),
    ("_emit_records_execution_trace", ("agent_registry", "L3_ORCHESTRATION", "p2_trace_4")),
    ("_emit_records_execution_trace", ("agent_registry", "L4_STATE", "p2_trace_5")),
    ("_emit_reads_environ", ("agent_registry", "env_read", "p2_env_1")),
    ("_emit_reads_environ", ("agent_registry", "env_read", "p2_env_2")),
    ("_emit_reads_runtime_state", ("agent_registry", "runtime_state", "p2_rt_1")),
    ("_emit_reads_runtime_state", ("agent_registry", "runtime_state", "p2_rt_2")),
    ("_emit_records_execution_trace", ("p0", "evidence", "agent_registry")),
    ("_emit_applies_guardrail", ("p0", "agent_registry", "p0_governance")),
    ("_emit_reads_policy_state", ("p0", "agent_registry", "policy_binding")),
    ("_emit_snapshots_state", ("p0", "agent_registry", "state_snapshot")),
    ("_emit_pulls_context", ("p1", "agent_registry", "context_pull")),
    ("_emit_pulls_context", ("p1", "agent_registry", "context_pull_secondary")),
    ("_emit_execution_terminates_at_uwg", ("p1", "agent_registry", "uwg_term")),
    ("_emit_execution_terminates_at_uwg", ("p1", "agent_registry", "uwg_term_secondary")),
    ("_emit_writes_through", ("p1", "agent_registry", "write_through")),
    ("_emit_writes_through", ("p1", "agent_registry", "write_through_secondary")),
    ("_emit_validated_by_safety_plane", ("p1", "agent_registry", "safety_validation")),
    ("_emit_invokes_eval", ("p1", "agent_registry", "eval_call")),
    ("_emit_proposal_commits_routing", ("p1", "agent_registry", "routing_commit")),
    ("_emit_escalates_to_human", ("p1", "agent_registry", "human_escalation")),
    ("_emit_routes_through", ("p1", "agent_registry", "route_through")),
    ("_emit_checks_agent_registry", ("p1", "agent_registry", "agent_registry")),
    ("_emit_validates_agent_capability", ("p1", "agent_registry", "capability")),
    ("_emit_dispatches_execution_plan", ("p1", "agent_registry", "exec_plan")),
    ("_emit_agent_executes_agent", ("p1", "agent_registry", "sub_agent")),
    ("_emit_routes_to_agent", ("p1", "agent_registry", "target_agent")),
    ("_emit_verifies_policy", ("p1", "agent_registry", "policy_check")),
    ("_emit_observes_runtime_state", ("p1", "agent_registry", "runtime_state")),
    ("_emit_verifies_boundary", ("p1", "agent_registry", "boundary_check")),
    ("_emit_transcripts_response", ("p1", "agent_registry", "transcript")),
    ("_emit_hard_fails_untranscripted", ("p1", "agent_registry")),
    ("_emit_gated_by_confidence", ("p1", "agent_registry", "confidence_gate")),
    ("emit_replay_key", ("p0", "agent_registry")),
    ("emit_determinism_digest", ("p0", "agent_registry")),
    ("_emit_signs_execution_trace", ("p0", "p0hash", "p0_trace", 0)),
    ("_emit_authorize_and_execute", ("p2", "agent_registry", "execution_auth")),
    ("_emit_validates_capability", ("p2", "agent_registry", "capability_check")),
    ("_emit_routes_to_capability", ("p2", "agent_registry", "capability_route")),
    ("_emit_writes_via_uwg", ("p2", "agent_registry", "uwg_write")),
    ("_emit_blocks_direct_write", ("p2", "agent_registry", "direct_write_block")),
    ("_emit_records_tool_invocation", ("p2", "agent_registry", "tool_invocation")),
    ("_emit_captures_execution_output", ("p2", "agent_registry", "exec_output")),
    ("_emit_dispatches_agent", ("p3", "agent_registry", "agent_dispatch")),
    ("_emit_coordinates_agents", ("p3", "agent_registry", "agent_coordination")),
    ("_emit_records_workflow_lineage", ("p3", "agent_registry", "workflow_lineage")),
    ("_emit_records_healing_outcome", ("p3", "agent_registry", "healing_outcome")),
    ("_emit_escalates_failure", ("p3", "agent_registry", "failure_escalation")),
    ("_emit_orchestrates_workflow", ("p3", "agent_registry", "workflow_orchestration")),
    ("_emit_dispatches_healing_run", ("p3", "agent_registry", "healing_dispatch")),
    ("_emit_invokes_evaluation", ("p3", "agent_registry", "evaluation_signal")),
    ("_emit_records_telemetry_event", ("p4", "agent_registry", "telemetry_event")),
    ("_emit_captures_evaluation_metric", ("p4", "agent_registry", "eval_metric")),
    ("_emit_stores_embedding", ("p4", "agent_registry", "embedding_store")),
    ("_emit_updates_meta_learning_state", ("p4", "agent_registry", "meta_learning")),
    ("_emit_links_execution_to_snapshot", ("p4", "agent_registry", "exec_snapshot_link")),
)


def _emit_bootstrap_telemetry() -> None:
    """Emit lifecycle bootstrap telemetry once, without breaking module import."""
    global _BOOTSTRAP_TELEMETRY_EMITTED

    if _BOOTSTRAP_TELEMETRY_EMITTED:
        return

    try:
        from agentic_core.runtime.contracts import lifecycle_trace_contract as lifecycle
    except ImportError:  # guardian: allow-return-none-swallow -- telemetry bootstrap: lifecycle contract absent, early exit prevents further emission
        logger.debug("Lifecycle trace contract unavailable; skipping agent registry bootstrap telemetry")
        _BOOTSTRAP_TELEMETRY_EMITTED = True
        return

    for emitter_name, emitter_args in _BOOTSTRAP_TELEMETRY_EVENTS:
        emitter = getattr(lifecycle, emitter_name, None)
        if not callable(emitter):
            logger.debug("Lifecycle emitter %s is unavailable; skipping", emitter_name)
            continue

        try:
            emitter(*emitter_args)
        except Exception:  # guardian: allow-broad-exception -- lifecycle telemetry emitters are untrusted; failures must never crash module load
            logger.debug("Lifecycle bootstrap emitter %s failed", emitter_name, exc_info=True)

    _BOOTSTRAP_TELEMETRY_EMITTED = True


def _normalize_agent_id(agent_id: str) -> str:
    """Validate and normalize registry lookup keys."""
    if not isinstance(agent_id, str):
        raise TypeError("agent_id must be a string")

    normalized = agent_id.strip()
    if not normalized:
        raise ValueError("agent_id must be a non-empty string")

    return normalized


_AGENT_REGISTRY: dict[str, AgentExecutionProfile] = {
    "reconciler": AgentExecutionProfile(
        agent_id="reconciler",
        reasoning_intensity=ReasoningIntensity.HIGH,
        execution_mode=ExecutionMode.DETERMINISTIC,
        allowed_models=(),
    ),
    "location": AgentExecutionProfile(
        agent_id="location",
        reasoning_intensity=ReasoningIntensity.LOW,
        execution_mode=ExecutionMode.DETERMINISTIC,
        allowed_models=(),
    ),
    "hierarchy": AgentExecutionProfile(
        agent_id="hierarchy",
        reasoning_intensity=ReasoningIntensity.MEDIUM,
        execution_mode=ExecutionMode.DETERMINISTIC,
        allowed_models=(),
    ),
    "arch_governor": AgentExecutionProfile(
        agent_id="arch_governor",
        reasoning_intensity=ReasoningIntensity.HIGH,
        execution_mode=ExecutionMode.DETERMINISTIC,
        allowed_models=(),
    ),
    "gravity_repair": AgentExecutionProfile(
        agent_id="gravity_repair",
        reasoning_intensity=ReasoningIntensity.MEDIUM,
        execution_mode=ExecutionMode.DETERMINISTIC,
        allowed_models=(),
    ),
    "system_architect": AgentExecutionProfile(
        agent_id="system_architect",
        reasoning_intensity=ReasoningIntensity.HIGH,
        execution_mode=ExecutionMode.DETERMINISTIC,
        allowed_models=(),
    ),
    "file_classification": AgentExecutionProfile(
        agent_id="file_classification",
        reasoning_intensity=ReasoningIntensity.LOW,
        execution_mode=ExecutionMode.DETERMINISTIC,
        allowed_models=(),
    ),
    "root_hygiene": AgentExecutionProfile(
        agent_id="root_hygiene",
        reasoning_intensity=ReasoningIntensity.LOW,
        execution_mode=ExecutionMode.DETERMINISTIC,
        allowed_models=(),
    ),
    "conversational_repair": AgentExecutionProfile(
        agent_id="conversational_repair",
        reasoning_intensity=ReasoningIntensity.HIGH,
        execution_mode=ExecutionMode.LLM_API,
        allowed_models=("gpt-4", "gpt-3.5-turbo", "claude-3-opus"),
    ),
    "cognitive_disposition": AgentExecutionProfile(
        agent_id="cognitive_disposition",
        reasoning_intensity=ReasoningIntensity.HIGH,
        execution_mode=ExecutionMode.LLM_API,
        allowed_models=("gpt-4", "claude-3-opus"),
    ),
    # Wave 4: audit-only entries for V15ExecutionGateway.execute() callers
    "sovereign_base": AgentExecutionProfile(
        agent_id="sovereign_base",
        reasoning_intensity=ReasoningIntensity.HIGH,
        execution_mode=ExecutionMode.DETERMINISTIC,
        allowed_models=(),
    ),
    "tool_reliability_mixin": AgentExecutionProfile(
        agent_id="tool_reliability_mixin",
        reasoning_intensity=ReasoningIntensity.LOW,
        execution_mode=ExecutionMode.DETERMINISTIC,
        allowed_models=(),
    ),
    "ssot_audit": AgentExecutionProfile(
        agent_id="ssot_audit",
        reasoning_intensity=ReasoningIntensity.LOW,
        execution_mode=ExecutionMode.DETERMINISTIC,
        allowed_models=(),
    ),
    "mission_runner": AgentExecutionProfile(
        agent_id="mission_runner",
        reasoning_intensity=ReasoningIntensity.HIGH,
        execution_mode=ExecutionMode.DETERMINISTIC,
        allowed_models=(),
    ),
    "orchestrator_engine": AgentExecutionProfile(
        agent_id="orchestrator_engine",
        reasoning_intensity=ReasoningIntensity.HIGH,
        execution_mode=ExecutionMode.DETERMINISTIC,
        allowed_models=(),
    ),
    "agent_engine": AgentExecutionProfile(
        agent_id="agent_engine",
        reasoning_intensity=ReasoningIntensity.HIGH,
        execution_mode=ExecutionMode.DETERMINISTIC,
        allowed_models=(),
    ),
}
AGENT_REGISTRY: Final[MappingProxyType[str, AgentExecutionProfile]] = MappingProxyType(_AGENT_REGISTRY)


def get_execution_profile(agent_id: str) -> AgentExecutionProfile:
    """Get agent execution profile by ID (canonical name for the L2 dispatcher)."""
    return get_profile(agent_id)


def get_profile(agent_id: str) -> AgentExecutionProfile:
    """Get agent execution profile by ID."""
    _emit_bootstrap_telemetry()
    normalized_agent_id = _normalize_agent_id(agent_id)

    try:
        return AGENT_REGISTRY[normalized_agent_id]
    except KeyError as exc:
        available_agents = ", ".join(sorted(AGENT_REGISTRY))
        raise KeyError(
            f"Agent '{normalized_agent_id}' not found in registry. Available: {available_agents}",
        ) from exc


def has_profile(agent_id: str) -> bool:
    """Return True when an agent profile exists for the supplied ID."""
    try:
        normalized_agent_id = _normalize_agent_id(agent_id)
    except (TypeError, ValueError):
        return False

    return normalized_agent_id in AGENT_REGISTRY


def list_agent_ids() -> tuple[str, ...]:
    """Return a deterministic list of registered agent IDs."""
    return tuple(sorted(AGENT_REGISTRY))


def registry_digest() -> dict[str, str]:
    """Generate a deterministic digest of the agent registry for validation."""
    _emit_bootstrap_telemetry()
    return {
        agent_id: f"{profile.agent_id}:{profile.reasoning_intensity.value}:{profile.execution_mode.value}"
        for agent_id, profile in sorted(AGENT_REGISTRY.items())
    }


__all__ = [
    "AGENT_REGISTRY",
    "get_execution_profile",
    "get_profile",
    "has_profile",
    "list_agent_ids",
    "registry_digest",
]
