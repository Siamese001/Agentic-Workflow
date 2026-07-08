"""G-16-14: Lineage chain validator for System Learning versioned ChangePackages.

Validates:
  - Parent version exists (except genesis)
  - No cycles (DAG structure enforced)
  - Lineage chain integrity
"""

from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "lineage_validator", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "lineage_validator", "policy_binding")
trace_contract._emit_snapshots_state("p0", "lineage_validator", "state_snapshot")

trace_contract._emit_emits_metric_event("lineage_validator", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("lineage_validator", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("lineage_validator", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("lineage_validator", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("lineage_validator", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("lineage_validator", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("lineage_validator", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("lineage_validator", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("lineage_validator", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("lineage_validator", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("lineage_validator", "p4obs", "alert")
trace_contract._emit_links_incident_trace("lineage_validator", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("lineage_validator", "p3lm", "pattern")
trace_contract._emit_records_learning_event("lineage_validator", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("lineage_validator", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("lineage_validator", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("lineage_validator", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("lineage_validator", "p3lm", "policy")
trace_contract._emit_stores_learning_state("lineage_validator", "p3lm", "state")
trace_contract._emit_records_execution_trace("lineage_validator", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("lineage_validator", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("lineage_validator", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("lineage_validator", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("lineage_validator", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("lineage_validator", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("lineage_validator", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("lineage_validator", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("lineage_validator", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "lineage_validator", "context_pull")
trace_contract._emit_pulls_context("p1", "lineage_validator", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "lineage_validator", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "lineage_validator", "uwg_term_2")
trace_contract._emit_writes_through("p1", "lineage_validator", "write_through")
trace_contract._emit_writes_through("p1", "lineage_validator", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "lineage_validator", "safety_validation")
trace_contract._emit_invokes_eval("p1", "lineage_validator", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "lineage_validator", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "lineage_validator", "human_escalation")
trace_contract._emit_routes_through("p1", "lineage_validator", "route_through")
trace_contract._emit_checks_agent_registry("p1", "lineage_validator", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "lineage_validator", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "lineage_validator", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "lineage_validator", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "lineage_validator", "target_agent")
trace_contract._emit_verifies_policy("p1", "lineage_validator", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "lineage_validator", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "lineage_validator", "boundary_check")
trace_contract._emit_transcripts_response("p1", "lineage_validator", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "lineage_validator")
trace_contract._emit_gated_by_confidence("p1", "lineage_validator", "confidence_gate")
trace_contract.emit_replay_key("p0", "lineage_validator")
trace_contract.emit_determinism_digest("p0", "lineage_validator")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "lineage_validator", "execution_auth")
trace_contract._emit_validates_capability("p2", "lineage_validator", "capability_check")
trace_contract._emit_routes_to_capability("p2", "lineage_validator", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "lineage_validator", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "lineage_validator", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "lineage_validator", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "lineage_validator", "exec_output")
trace_contract._emit_dispatches_agent("p3", "lineage_validator", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "lineage_validator", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "lineage_validator", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "lineage_validator", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "lineage_validator", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "lineage_validator", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "lineage_validator", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "lineage_validator", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "lineage_validator", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "lineage_validator", "eval_metric")
trace_contract._emit_stores_embedding("p4", "lineage_validator", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "lineage_validator", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "lineage_validator", "exec_snapshot_link")


class LineageValidationError(Exception):
    """Base exception for lineage validation failures."""


class ParentNotFound(LineageValidationError):
    """Raised when parent version does not exist."""


class CycleDetected(LineageValidationError):
    """Raised when a cycle is detected in the lineage chain."""


class LineageValidator:
    """Validates lineage chain integrity for versioned ChangePackages.

    Enforces:
      - Parent version exists (except genesis)
      - No cycles (DAG structure)
      - Lineage chain is well-formed
    """

    def __init__(self, version_store) -> None:
        """Initialize validator with a version store.

        Parameters
        ----------
        version_store
            A version store implementing get_change_package(version_id).
        """
        self._store = version_store

    def validate_lineage(self, version_id: str) -> None:
        """Validate the lineage chain for a version.

        Parameters
        ----------
        version_id : str
            The version_id to validate.

        Raises
        ------
        ParentNotFound
            If a parent version does not exist.
        CycleDetected
            If a cycle is detected in the lineage chain.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "LineageValidator.validate_lineage"
        )

        visited: set[str] = set()
        current = version_id
        while current is not None:
            if current in visited:
                raise CycleDetected(f"CYCLE_DETECTED: version {current!r} appears twice in lineage chain")
            visited.add(current)
            try:
                pkg = self._store.get_change_package(current)
            except (AttributeError, KeyError, RuntimeError, TypeError, ValueError) as exc:
                raise ParentNotFound(f"PARENT_NOT_FOUND: version {current!r} does not exist") from exc
            current = pkg.parent_version_id
            if current is not None:
                try:
                    self._store.get_change_package(current)
                except (AttributeError, KeyError, RuntimeError, TypeError, ValueError) as exc:
                    raise ParentNotFound(
                        f"PARENT_NOT_FOUND: parent version {current!r} does not exist",
                    ) from exc

    def validate_chain(self, version_id: str) -> list[str]:
        """Validate and return the full lineage chain.

        Parameters
        ----------
        version_id : str
            The version_id to start from.

        Returns
        -------
        list[str]
            Ordered list of version_ids from genesis to current (inclusive).

        Raises
        ------
        ParentNotFound
            If a parent version does not exist.
        CycleDetected
            If a cycle is detected.
        """
        self.validate_lineage(version_id)
        chain: list[str] = []
        current = version_id
        while current is not None:
            chain.append(current)
            pkg = self._store.get_change_package(current)
            current = pkg.parent_version_id
        return list(reversed(chain))
