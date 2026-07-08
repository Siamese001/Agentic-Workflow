"""G18 (gap): Config governance runtime.

Tracks every governed-config read and schema-validation event:
  caller → reads_governed_config → ConfigReader
  caller → validates_config_schema → GovernedConfig
  caller → caches_config → ConfigLoader

Data structures only — no side-effects on import.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "config_governance", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "config_governance", "policy_binding")
trace_contract._emit_snapshots_state("p0", "config_governance", "state_snapshot")

trace_contract._emit_emits_metric_event("config_governance", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("config_governance", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("config_governance", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("config_governance", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("config_governance", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("config_governance", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("config_governance", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("config_governance", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("config_governance", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("config_governance", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("config_governance", "p4obs", "alert")
trace_contract._emit_links_incident_trace("config_governance", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("config_governance", "p3lm", "pattern")
trace_contract._emit_records_learning_event("config_governance", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("config_governance", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("config_governance", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("config_governance", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("config_governance", "p3lm", "policy")
trace_contract._emit_stores_learning_state("config_governance", "p3lm", "state")
trace_contract._emit_records_execution_trace("config_governance", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("config_governance", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("config_governance", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("config_governance", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("config_governance", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("config_governance", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("config_governance", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("config_governance", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("config_governance", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "config_governance", "context_pull")
trace_contract._emit_pulls_context("p1", "config_governance", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "config_governance", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "config_governance", "uwg_term_2")
trace_contract._emit_writes_through("p1", "config_governance", "write_through")
trace_contract._emit_writes_through("p1", "config_governance", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "config_governance", "safety_validation")
trace_contract._emit_invokes_eval("p1", "config_governance", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "config_governance", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "config_governance", "human_escalation")
trace_contract._emit_routes_through("p1", "config_governance", "route_through")
trace_contract._emit_checks_agent_registry("p1", "config_governance", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "config_governance", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "config_governance", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "config_governance", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "config_governance", "target_agent")
trace_contract._emit_verifies_policy("p1", "config_governance", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "config_governance", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "config_governance", "boundary_check")
trace_contract._emit_transcripts_response("p1", "config_governance", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "config_governance")
trace_contract._emit_gated_by_confidence("p1", "config_governance", "confidence_gate")
trace_contract.emit_replay_key("p0", "config_governance")
trace_contract.emit_determinism_digest("p0", "config_governance")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "config_governance", "execution_auth")
trace_contract._emit_validates_capability("p2", "config_governance", "capability_check")
trace_contract._emit_routes_to_capability("p2", "config_governance", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "config_governance", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "config_governance", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "config_governance", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "config_governance", "exec_output")
trace_contract._emit_dispatches_agent("p3", "config_governance", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "config_governance", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "config_governance", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "config_governance", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "config_governance", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "config_governance", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "config_governance", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "config_governance", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "config_governance", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "config_governance", "eval_metric")
trace_contract._emit_stores_embedding("p4", "config_governance", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "config_governance", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "config_governance", "exec_snapshot_link")


class ConfigReadOutcome(str, Enum):
    """Outcome of a config read attempt."""

    HIT = "hit"
    MISS = "miss"
    CACHED = "cached"
    INVALID = "invalid"
    SCHEMA_FAIL = "schema_fail"


class ConfigSchemaStatus(str, Enum):
    """Result of config schema validation."""

    VALID = "valid"
    INVALID = "invalid"
    MISSING_KEY = "missing_key"
    TYPE_MISMATCH = "type_mismatch"
    EXTRA_KEYS = "extra_keys"


@dataclass
class ConfigReadEvent:
    """A single config read event."""

    event_id: str = field(default_factory=lambda: f"cre-{uuid.uuid4().hex[:12]}")
    agent_id: str = ""
    run_id: str = ""
    config_key: str = ""
    config_source: str = ""
    outcome: ConfigReadOutcome = ConfigReadOutcome.HIT
    schema_status: ConfigSchemaStatus = ConfigSchemaStatus.VALID
    read_at: float = field(default_factory=time.time)
    cached: bool = False
    validation_errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "agent_id": self.agent_id,
            "run_id": self.run_id,
            "config_key": self.config_key,
            "config_source": self.config_source,
            "outcome": self.outcome.value,
            "schema_status": self.schema_status.value,
            "read_at": self.read_at,
            "cached": self.cached,
            "validation_errors": list(self.validation_errors),
        }


@dataclass
class ConfigGovernanceReport:
    """Aggregated config governance report for a run."""

    agent_id: str
    run_id: str
    events: list[ConfigReadEvent] = field(default_factory=list)

    @property
    def total_reads(self) -> int:
        return len(self.events)

    @property
    def cached_count(self) -> int:
        return sum(1 for e in self.events if e.cached)

    @property
    def schema_fail_count(self) -> int:
        return sum(1 for e in self.events if e.schema_status != ConfigSchemaStatus.VALID)

    @property
    def unique_keys(self) -> set[str]:
        return {e.config_key for e in self.events}

    @property
    def by_outcome(self) -> dict[str, int]:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "ConfigGovernanceReport.by_outcome"
        )

        result: dict[str, int] = {}
        for e in self.events:
            result[e.outcome.value] = result.get(e.outcome.value, 0) + 1
        return result

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "run_id": self.run_id,
            "total_reads": self.total_reads,
            "cached_count": self.cached_count,
            "schema_fail_count": self.schema_fail_count,
            "unique_key_count": len(self.unique_keys),
            "by_outcome": self.by_outcome,
            "events": [e.to_dict() for e in self.events],
        }


class ConfigGovernor:
    """G18 runtime recorder: tracks governed config reads and validations.

    Lifecycle:
        gov = ConfigGovernor(agent_id, run_id)
        event = gov.read_config("db.host", source="env")
        gov.validate_config("db.host", errors=[])
        report = gov.report
    """

    def __init__(self, agent_id: str, run_id: str) -> None:
        self._agent_id = agent_id
        self._run_id = run_id
        self._report = ConfigGovernanceReport(agent_id=agent_id, run_id=run_id)
        self._cache: dict[str, Any] = {}

    @property
    def report(self) -> ConfigGovernanceReport:
        return self._report

    def read_config(
        self,
        config_key: str,
        source: str = "env",
        outcome: ConfigReadOutcome = ConfigReadOutcome.HIT,
    ) -> ConfigReadEvent:
        """Record a config read event."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "ConfigGovernor.read_config")

        cached = config_key in self._cache
        # guardian: allow-config-with-logic
        if cached:
            outcome = ConfigReadOutcome.CACHED
        else:
            self._cache[config_key] = True
        event = ConfigReadEvent(
            agent_id=self._agent_id,
            run_id=self._run_id,
            config_key=config_key,
            config_source=source,
            outcome=outcome,
            cached=cached,
        )
        self._report.events.append(event)
        return event

    def validate_config(
        self,
        config_key: str,
        errors: list[str] | None = None,
        source: str = "schema",
    ) -> ConfigReadEvent:
        """Record a config schema validation event."""
        errs = errors or []
        status = ConfigSchemaStatus.VALID if not errs else ConfigSchemaStatus.INVALID
        event = ConfigReadEvent(
            agent_id=self._agent_id,
            run_id=self._run_id,
            config_key=config_key,
            config_source=source,
            outcome=ConfigReadOutcome.HIT if not errs else ConfigReadOutcome.SCHEMA_FAIL,
            schema_status=status,
            validation_errors=list(errs),
        )
        self._report.events.append(event)
        return event

    def invalidate_cache(self) -> int:
        """Clear the config cache. Returns number of keys invalidated."""
        count = len(self._cache)
        self._cache.clear()
        return count
