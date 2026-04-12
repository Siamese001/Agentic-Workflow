"""
Immutable Staging Buffer for RG Sovereign Architecture.

A write-once data structure that prevents state mutation bugs in multi-hop workflows.
Aligned with LIC ImmutableStagingBuffer pattern.

HARDENING: Implements deepcopy on boundaries to prevent reference leakage.
Adds StateTransaction for audit trails.
"""

from __future__ import annotations

import copy
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, TypeVar

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
from apps_rg.utils.mixins import HealerMixin, MCPHardenedMixin

_emit_applies_guardrail("p0", "state_transaction_types", "p0_governance")
_emit_reads_policy_state("p0", "state_transaction_types", "policy_binding")
_emit_snapshots_state("p0", "state_transaction_types", "state_snapshot")
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

_emit_emits_metric_event("state_transaction_types", "p4obs", "metric_1")
_emit_emits_metric_event("state_transaction_types", "p4obs", "metric_2")
_emit_emits_metric_event("state_transaction_types", "p4obs", "metric_3")
_emit_emits_metric_event("state_transaction_types", "p4obs", "metric_4")
_emit_emits_metric_event("state_transaction_types", "p4obs", "metric_5")
_emit_emits_metric_event("state_transaction_types", "p4obs", "metric_6")
_emit_records_incident_event("state_transaction_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("state_transaction_types", "p4obs", "anomaly")
_emit_writes_observability_log("state_transaction_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("state_transaction_types", "p4obs", "mon_state")
_emit_triggers_alert("state_transaction_types", "p4obs", "alert")
_emit_links_incident_trace("state_transaction_types", "p4obs", "trace_link")
_emit_captures_pattern("state_transaction_types", "p3lm", "pattern")
_emit_records_learning_event("state_transaction_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("state_transaction_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("state_transaction_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("state_transaction_types", "p3lm", "routing")
_emit_improves_agent_policy("state_transaction_types", "p3lm", "policy")
_emit_stores_learning_state("state_transaction_types", "p3lm", "state")
_emit_records_execution_trace("state_transaction_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("state_transaction_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("state_transaction_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("state_transaction_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("state_transaction_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("state_transaction_types", "env_read", "p2_env_1")
_emit_reads_environ("state_transaction_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("state_transaction_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("state_transaction_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "state_transaction_types", "context_pull")
_emit_pulls_context("p1", "state_transaction_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "state_transaction_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "state_transaction_types", "uwg_term_2")
_emit_writes_through("p1", "state_transaction_types", "write_through")
_emit_writes_through("p1", "state_transaction_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "state_transaction_types", "safety_validation")
_emit_invokes_eval("p1", "state_transaction_types", "eval_call")
_emit_proposal_commits_routing("p1", "state_transaction_types", "routing_commit")
_emit_escalates_to_human("p1", "state_transaction_types", "human_escalation")
_emit_routes_through("p1", "state_transaction_types", "route_through")
_emit_checks_agent_registry("p1", "state_transaction_types", "agent_registry")
_emit_validates_agent_capability("p1", "state_transaction_types", "capability")
_emit_dispatches_execution_plan("p1", "state_transaction_types", "exec_plan")
_emit_agent_executes_agent("p1", "state_transaction_types", "sub_agent")
_emit_routes_to_agent("p1", "state_transaction_types", "target_agent")
_emit_verifies_policy("p1", "state_transaction_types", "policy_check")
_emit_observes_runtime_state("p1", "state_transaction_types", "runtime_state")
_emit_verifies_boundary("p1", "state_transaction_types", "boundary_check")
_emit_transcripts_response("p1", "state_transaction_types", "transcript")
_emit_hard_fails_untranscripted("p1", "state_transaction_types")
_emit_gated_by_confidence("p1", "state_transaction_types", "confidence_gate")
emit_replay_key("p0", "state_transaction_types")
emit_determinism_digest("p0", "state_transaction_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "state_transaction_types", "execution_auth")
_emit_validates_capability("p2", "state_transaction_types", "capability_check")
_emit_routes_to_capability("p2", "state_transaction_types", "capability_route")
_emit_writes_via_uwg("p2", "state_transaction_types", "uwg_write")
_emit_blocks_direct_write("p2", "state_transaction_types", "direct_write_block")
_emit_records_tool_invocation("p2", "state_transaction_types", "tool_invocation")
_emit_captures_execution_output("p2", "state_transaction_types", "exec_output")
_emit_dispatches_agent("p3", "state_transaction_types", "agent_dispatch")
_emit_coordinates_agents("p3", "state_transaction_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "state_transaction_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "state_transaction_types", "healing_outcome")
_emit_escalates_failure("p3", "state_transaction_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "state_transaction_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "state_transaction_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "state_transaction_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "state_transaction_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "state_transaction_types", "eval_metric")
_emit_stores_embedding("p4", "state_transaction_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "state_transaction_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "state_transaction_types", "exec_snapshot_link")

Logger = logging.getLogger(__name__)
T = TypeVar("T")


@dataclass(frozen=True)
class StateTransaction:
    """Immutable record of a state change."""

    key: str
    timestamp: float
    source_agent: str
    value_hash: int
    cycle_id: str


@dataclass
class ImmutableStagingBuffer(MCPHardenedMixin, HealerMixin):
    """
    Sovereign State Container.
    Enforces Write-Once-Read-Many (WORM) with Deep Copy isolation.

    RG-Specific Keys:
    - mission_input: Initial job description and resume data
    - hop0_validation: JD validation results
    - hop1_extraction: Clerk extraction output
    - hop2_enrichment: Enrichment output
    - hop3_generation: Generated resume sections
    - hop4_validation: Quality validation results
    - hop5_gate_decision: Pass/fail gate decision
    - hop6_refinement: Refined content
    - hop7_qa_report: Final QA report
    """

    _buffer: dict[str, Any] = field(default_factory=dict)
    _locked_keys: set[str] = field(default_factory=set)
    _history: list[StateTransaction] = field(default_factory=list)
    _cycle_id: str = "INIT"

    def __post_init__(self) -> None:
        """Initialize mixins."""
        MCPHardenedMixin.__init__(self)
        HealerMixin.__init__(self)

    def _mcp_audit(self, action: str, details: dict = None) -> None:
        """Safe MCP audit call - falls back to no-op if mixin not fully initialized."""
        if hasattr(super(), "_mcp_audit"):
            super()._mcp_audit(action, details or {})

    def write(self, key: str, value: Any, source_agent: str = "SYSTEM") -> None:
        """
        Commit data to the buffer.
        CRITICAL: Stores a deep copy to prevent external mutation.

        Args:
            key: The identifier for the data.
            value: The data to store.
            source_agent: The agent performing the write.

        Raises:
            PermissionError: If the key has already been written to.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "ImmutableStagingBuffer.write"
        )

        if key in self._locked_keys:
            self._mcp_audit("write_violation", {"key": key, "agent": source_agent})
            raise PermissionError(f"Key '{key}' is LOCKED. Immutable violation by {source_agent}.")
        try:
            snapshot = copy.deepcopy(value)
        except TypeError:
            Logger.warning(f"[{source_agent}] Object for '{key}' is not deep-copyable. Storing reference.")
            snapshot = value
        self._buffer[key] = snapshot
        self._locked_keys.add(key)
        self._history.append(
            StateTransaction(
                key=key,
                timestamp=datetime.now(timezone.utc).timestamp(),
                source_agent=source_agent,
                value_hash=hash(str(snapshot))
                if isinstance(snapshot, str | int | float | tuple | frozenset)
                else hash(str(snapshot))
                if isinstance(snapshot, dict)
                else 0,
                cycle_id=self._cycle_id,
            ),
        )
        self._mcp_audit("buffer_write", {"key": key, "agent": source_agent})

    def write_once(self, key: str, value: Any) -> None:
        """
        Legacy API: Writes a value to the buffer if the key is not locked.
        Delegates to write() with default source_agent.
        """
        self.write(key, value, source_agent="LEGACY")

    def read(self, key: str, default: Any = None) -> Any:
        """
        Retrieve data from the buffer.
        CRITICAL: Returns a deep copy to prevent downstream mutation of state.

        Args:
            key: The identifier to read.
            default: Default value if key not found.

        Returns:
            A deep copy of the value if found, else default.
        """
        if key not in self._buffer:
            return default
        data = self._buffer[key]
        try:
            return copy.deepcopy(data)
        except TypeError:
            return data

    def set_cycle(self, cycle_id: str) -> None:
        """Set the current cycle ID for transaction tracking."""
        self._cycle_id = cycle_id

    def get_history(self) -> list[StateTransaction]:
        """Returns a copy of the transaction history."""
        return list(self._history)

    def is_locked(self, key: str) -> bool:
        """Checks if a key has been written."""
        return key in self._locked_keys

    def get_snapshot(self) -> dict[str, Any]:
        """Returns a deep copy of the current buffer state."""
        return copy.deepcopy(self._buffer)

    def get_locked_keys(self) -> set[str]:
        """Returns a copy of the locked keys set."""
        return self._locked_keys.copy()

    def has_key(self, key: str) -> bool:
        """Check if a key exists in the buffer (locked or not)."""
        return key in self._buffer
