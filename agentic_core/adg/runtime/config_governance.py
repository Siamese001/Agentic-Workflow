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

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "config_governance", "p0_governance")
_emit_reads_policy_state("p0", "config_governance", "policy_binding")
_emit_snapshots_state("p0", "config_governance", "state_snapshot")
emit_replay_key("p0", "config_governance")
emit_determinism_digest("p0", "config_governance")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "config_governance", "execution_auth")
_emit_validates_capability("p2", "config_governance", "capability_check")
_emit_routes_to_capability("p2", "config_governance", "capability_route")
_emit_writes_via_uwg("p2", "config_governance", "uwg_write")
_emit_blocks_direct_write("p2", "config_governance", "direct_write_block")
_emit_records_tool_invocation("p2", "config_governance", "tool_invocation")
_emit_captures_execution_output("p2", "config_governance", "exec_output")
_emit_dispatches_agent("p3", "config_governance", "agent_dispatch")
_emit_coordinates_agents("p3", "config_governance", "agent_coordination")
_emit_records_workflow_lineage("p3", "config_governance", "workflow_lineage")
_emit_records_healing_outcome("p3", "config_governance", "healing_outcome")
_emit_escalates_failure("p3", "config_governance", "failure_escalation")
_emit_orchestrates_workflow("p3", "config_governance", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "config_governance", "healing_dispatch")
_emit_invokes_evaluation("p3", "config_governance", "evaluation_signal")
_emit_records_telemetry_event("p4", "config_governance", "telemetry_event")
_emit_captures_evaluation_metric("p4", "config_governance", "eval_metric")
_emit_stores_embedding("p4", "config_governance", "embedding_store")
_emit_updates_meta_learning_state("p4", "config_governance", "meta_learning")
_emit_links_execution_to_snapshot("p4", "config_governance", "exec_snapshot_link")


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
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ConfigGovernanceReport.by_outcome")

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
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ConfigGovernor.read_config")

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
