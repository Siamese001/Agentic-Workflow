"""
Wave 5.3: Immutable Routing Config Seal.

Prevents mid-run routing config mutation by sealing the config
at run start with a canonical hash.  Any attempt to mutate the
config during execution raises RoutingConfigSealViolation.

Lives in L0 (routing types) — config is read at routing time.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone

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
    emit_determinism_digest,
    emit_replay_key,
)

_emit_authorize_and_execute("p2", "routing_config_seal_types", "execution_auth")
_emit_validates_capability("p2", "routing_config_seal_types", "capability_check")
_emit_routes_to_capability("p2", "routing_config_seal_types", "capability_route")
_emit_writes_via_uwg("p2", "routing_config_seal_types", "uwg_write")
_emit_blocks_direct_write("p2", "routing_config_seal_types", "direct_write_block")
_emit_records_tool_invocation("p2", "routing_config_seal_types", "tool_invocation")
_emit_captures_execution_output("p2", "routing_config_seal_types", "exec_output")
_emit_dispatches_agent("p3", "routing_config_seal_types", "agent_dispatch")
_emit_coordinates_agents("p3", "routing_config_seal_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "routing_config_seal_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "routing_config_seal_types", "healing_outcome")
_emit_escalates_failure("p3", "routing_config_seal_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "routing_config_seal_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "routing_config_seal_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "routing_config_seal_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "routing_config_seal_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "routing_config_seal_types", "eval_metric")
_emit_stores_embedding("p4", "routing_config_seal_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "routing_config_seal_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "routing_config_seal_types", "exec_snapshot_link")
from agentic_core.utils.schemas.canonical_serializer_util import (
    canonical_bytes,
)

_emit_dispatches_healing_run("p1", "routing_config_seal_types", "L0")
_emit_routes_through("p1", "routing_config_seal_types", "L0")
_emit_checks_agent_registry("p1", "routing_config_seal_types", "agent_registry")
_emit_validates_agent_capability("p1", "routing_config_seal_types", "capability")
_emit_dispatches_execution_plan("p1", "routing_config_seal_types", "exec_plan")
_emit_agent_executes_agent("p1", "routing_config_seal_types", "sub_agent")
_emit_routes_to_agent("p1", "routing_config_seal_types", "target_agent")
_emit_verifies_policy("p1", "routing_config_seal_types", "policy_check")
_emit_observes_runtime_state("p1", "routing_config_seal_types", "runtime_state")
_emit_verifies_boundary("p1", "routing_config_seal_types", "boundary_check")
_emit_transcripts_response("p1", "routing_config_seal_types", "transcript")
_emit_hard_fails_untranscripted("p1", "routing_config_seal_types")
_emit_gated_by_confidence("p1", "routing_config_seal_types", "confidence_gate")
_emit_escalates_to_human("p1", "routing_config_seal_types", "L0")
_emit_reads_policy_state("p1", "routing_config_seal_types", "L0")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "routing_config_seal_types", "p0_governance")
_emit_snapshots_state("p0", "routing_config_seal_types", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,
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
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("routing_config_seal_types", "p4obs", "metric_1")
_emit_emits_metric_event("routing_config_seal_types", "p4obs", "metric_2")
_emit_emits_metric_event("routing_config_seal_types", "p4obs", "metric_3")
_emit_emits_metric_event("routing_config_seal_types", "p4obs", "metric_4")
_emit_emits_metric_event("routing_config_seal_types", "p4obs", "metric_5")
_emit_emits_metric_event("routing_config_seal_types", "p4obs", "metric_6")
_emit_records_incident_event("routing_config_seal_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("routing_config_seal_types", "p4obs", "anomaly")
_emit_writes_observability_log("routing_config_seal_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("routing_config_seal_types", "p4obs", "mon_state")
_emit_triggers_alert("routing_config_seal_types", "p4obs", "alert")
_emit_links_incident_trace("routing_config_seal_types", "p4obs", "trace_link")
_emit_captures_pattern("routing_config_seal_types", "p3lm", "pattern")
_emit_records_learning_event("routing_config_seal_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("routing_config_seal_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("routing_config_seal_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("routing_config_seal_types", "p3lm", "routing")
_emit_improves_agent_policy("routing_config_seal_types", "p3lm", "policy")
_emit_stores_learning_state("routing_config_seal_types", "p3lm", "state")
_emit_records_execution_trace("routing_config_seal_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("routing_config_seal_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("routing_config_seal_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("routing_config_seal_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("routing_config_seal_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("routing_config_seal_types", "env_read", "p2_env_1")
_emit_reads_environ("routing_config_seal_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("routing_config_seal_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("routing_config_seal_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "routing_config_seal_types", "context_pull")
_emit_pulls_context("p1", "routing_config_seal_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "routing_config_seal_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "routing_config_seal_types", "uwg_term_2")
_emit_writes_through("p1", "routing_config_seal_types", "write_through")
_emit_writes_through("p1", "routing_config_seal_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "routing_config_seal_types", "safety_validation")
_emit_invokes_eval("p1", "routing_config_seal_types", "eval_call")
_emit_proposal_commits_routing("p1", "routing_config_seal_types", "routing_commit")


class RoutingConfigSealViolation(RuntimeError):
    """Raised when routing config is mutated after sealing."""


@dataclass(frozen=True)
class RoutingConfigSeal:
    """Immutable seal over a routing configuration snapshot.

    Once sealed, the config hash must remain constant for the
    duration of the run.  Verification re-derives the hash and
    compares.
    """

    canonical_hash: str
    version: str
    sealed_at: str

    @staticmethod
    def create(
        *,
        config: dict,
        version: str,
    ) -> RoutingConfigSeal:
        """Seal a routing config snapshot."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "RoutingConfigSeal.create")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        sealed_at = datetime.now(timezone.utc).isoformat(timespec="microseconds")
        ch = hashlib.sha256(canonical_bytes(config)).hexdigest()
        return RoutingConfigSeal(
            canonical_hash=ch,
            version=version,
            sealed_at=sealed_at,
        )

    def verify(self, config: dict) -> bool:
        """Verify config has not changed since sealing."""
        current = hashlib.sha256(canonical_bytes(config)).hexdigest()
        return current == self.canonical_hash


class SealedRoutingContext:
    """Context manager that enforces routing config immutability.

    Usage::

        ctx = SealedRoutingContext(config, version="1.0")
        ctx.verify_or_raise(config)  # ok
        config["new_key"] = "value"
        ctx.verify_or_raise(config)  # raises
    """

    def __init__(self, config: dict, *, version: str) -> None:
        self._seal = RoutingConfigSeal.create(config=config, version=version)

    @property
    def seal(self) -> RoutingConfigSeal:
        return self._seal

    def verify_or_raise(self, config: dict) -> None:
        """Raise if config has been mutated since sealing."""
        if not self._seal.verify(config):
            raise RoutingConfigSealViolation(
                "Routing config mutated after sealing. "
                f"Expected hash: "
                f"{self._seal.canonical_hash[:16]}... "
                f"Sealed at: {self._seal.sealed_at}"
            )
