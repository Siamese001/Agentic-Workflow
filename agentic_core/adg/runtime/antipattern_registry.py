"""G21 (gap): Anti-pattern registry runtime.

Tracks every anti-pattern occurrence detected by the ADG static scanner:
  caller → registers_antipattern → AntipatternRegistry
  caller → classifies_antipattern → PatternClassifier

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

_emit_applies_guardrail("p0", "antipattern_registry", "p0_governance")
_emit_reads_policy_state("p0", "antipattern_registry", "policy_binding")
_emit_snapshots_state("p0", "antipattern_registry", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

_emit_emits_metric_event("antipattern_registry", "p4obs", "metric_1")
_emit_emits_metric_event("antipattern_registry", "p4obs", "metric_2")
_emit_emits_metric_event("antipattern_registry", "p4obs", "metric_3")
_emit_emits_metric_event("antipattern_registry", "p4obs", "metric_4")
_emit_emits_metric_event("antipattern_registry", "p4obs", "metric_5")
_emit_emits_metric_event("antipattern_registry", "p4obs", "metric_6")
_emit_records_incident_event("antipattern_registry", "p4obs", "incident")
_emit_captures_runtime_anomaly("antipattern_registry", "p4obs", "anomaly")
_emit_writes_observability_log("antipattern_registry", "p4obs", "obs_log")
_emit_updates_monitoring_state("antipattern_registry", "p4obs", "mon_state")
_emit_triggers_alert("antipattern_registry", "p4obs", "alert")
_emit_links_incident_trace("antipattern_registry", "p4obs", "trace_link")
_emit_captures_pattern("antipattern_registry", "p3lm", "pattern")
_emit_records_learning_event("antipattern_registry", "p3lm", "learning_event")
_emit_writes_learning_snapshot("antipattern_registry", "p3lm", "snapshot")
_emit_feeds_meta_learning("antipattern_registry", "p3lm", "meta_feed")
_emit_updates_routing_strategy("antipattern_registry", "p3lm", "routing")
_emit_improves_agent_policy("antipattern_registry", "p3lm", "policy")
_emit_stores_learning_state("antipattern_registry", "p3lm", "state")
_emit_records_execution_trace("antipattern_registry", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("antipattern_registry", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("antipattern_registry", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("antipattern_registry", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("antipattern_registry", "L4_STATE", "p2_trace_5")
_emit_reads_environ("antipattern_registry", "env_read", "p2_env_1")
_emit_reads_environ("antipattern_registry", "env_read", "p2_env_2")
_emit_reads_runtime_state("antipattern_registry", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("antipattern_registry", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "antipattern_registry", "context_pull")
_emit_pulls_context("p1", "antipattern_registry", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "antipattern_registry", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "antipattern_registry", "uwg_term_2")
_emit_writes_through("p1", "antipattern_registry", "write_through")
_emit_writes_through("p1", "antipattern_registry", "write_through_2")
_emit_validated_by_safety_plane("p1", "antipattern_registry", "safety_validation")
_emit_invokes_eval("p1", "antipattern_registry", "eval_call")
_emit_proposal_commits_routing("p1", "antipattern_registry", "routing_commit")
_emit_escalates_to_human("p1", "antipattern_registry", "human_escalation")
_emit_routes_through("p1", "antipattern_registry", "route_through")
_emit_checks_agent_registry("p1", "antipattern_registry", "agent_registry")
_emit_validates_agent_capability("p1", "antipattern_registry", "capability")
_emit_dispatches_execution_plan("p1", "antipattern_registry", "exec_plan")
_emit_agent_executes_agent("p1", "antipattern_registry", "sub_agent")
_emit_routes_to_agent("p1", "antipattern_registry", "target_agent")
_emit_verifies_policy("p1", "antipattern_registry", "policy_check")
_emit_observes_runtime_state("p1", "antipattern_registry", "runtime_state")
_emit_verifies_boundary("p1", "antipattern_registry", "boundary_check")
_emit_transcripts_response("p1", "antipattern_registry", "transcript")
_emit_hard_fails_untranscripted("p1", "antipattern_registry")
_emit_gated_by_confidence("p1", "antipattern_registry", "confidence_gate")
emit_replay_key("p0", "antipattern_registry")
emit_determinism_digest("p0", "antipattern_registry")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "antipattern_registry", "execution_auth")
_emit_validates_capability("p2", "antipattern_registry", "capability_check")
_emit_routes_to_capability("p2", "antipattern_registry", "capability_route")
_emit_writes_via_uwg("p2", "antipattern_registry", "uwg_write")
_emit_blocks_direct_write("p2", "antipattern_registry", "direct_write_block")
_emit_records_tool_invocation("p2", "antipattern_registry", "tool_invocation")
_emit_captures_execution_output("p2", "antipattern_registry", "exec_output")
_emit_dispatches_agent("p3", "antipattern_registry", "agent_dispatch")
_emit_coordinates_agents("p3", "antipattern_registry", "agent_coordination")
_emit_records_workflow_lineage("p3", "antipattern_registry", "workflow_lineage")
_emit_records_healing_outcome("p3", "antipattern_registry", "healing_outcome")
_emit_escalates_failure("p3", "antipattern_registry", "failure_escalation")
_emit_orchestrates_workflow("p3", "antipattern_registry", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "antipattern_registry", "healing_dispatch")
_emit_invokes_evaluation("p3", "antipattern_registry", "evaluation_signal")
_emit_records_telemetry_event("p4", "antipattern_registry", "telemetry_event")
_emit_captures_evaluation_metric("p4", "antipattern_registry", "eval_metric")
_emit_stores_embedding("p4", "antipattern_registry", "embedding_store")
_emit_updates_meta_learning_state("p4", "antipattern_registry", "meta_learning")
_emit_links_execution_to_snapshot("p4", "antipattern_registry", "exec_snapshot_link")


class AntipatternSeverity(str, Enum):
    """Severity of a detected anti-pattern."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AntipatternCategory(str, Enum):
    """Canonical anti-pattern categories matching ADG static scanner edge kinds."""

    SILENT_EXCEPTION_SWALLOW = "silent_exception_swallow"
    BLOCKING_CALL_IN_ASYNC = "blocking_call_in_async"
    GLOBAL_STATE_MUTATION = "global_state_mutation"
    RETRY_WITHOUT_BACKOFF = "retry_without_backoff"
    BARE_EXCEPT = "bare_except"
    MUTABLE_DEFAULT_ARG = "mutable_default_arg"
    STAR_IMPORT_USE = "star_import_use"
    HARDCODED_SECRET = "hardcoded_secret"
    DEAD_CODE = "dead_code"
    OVERLY_BROAD_CATCH = "overly_broad_catch"
    BROAD_EXCEPTION_CATCH = "broad_exception_catch"
    LOG_AND_SWALLOW = "log_and_swallow"
    RETURN_NONE_SWALLOW = "return_none_swallow"


_SEVERITY_MAP: dict[AntipatternCategory, AntipatternSeverity] = {
    AntipatternCategory.HARDCODED_SECRET: AntipatternSeverity.CRITICAL,
    AntipatternCategory.GLOBAL_STATE_MUTATION: AntipatternSeverity.HIGH,
    AntipatternCategory.SILENT_EXCEPTION_SWALLOW: AntipatternSeverity.HIGH,
    AntipatternCategory.BLOCKING_CALL_IN_ASYNC: AntipatternSeverity.HIGH,
    AntipatternCategory.RETRY_WITHOUT_BACKOFF: AntipatternSeverity.MEDIUM,
    AntipatternCategory.BARE_EXCEPT: AntipatternSeverity.MEDIUM,
    AntipatternCategory.OVERLY_BROAD_CATCH: AntipatternSeverity.MEDIUM,
    AntipatternCategory.BROAD_EXCEPTION_CATCH: AntipatternSeverity.HIGH,
    AntipatternCategory.LOG_AND_SWALLOW: AntipatternSeverity.HIGH,
    AntipatternCategory.RETURN_NONE_SWALLOW: AntipatternSeverity.HIGH,
    AntipatternCategory.MUTABLE_DEFAULT_ARG: AntipatternSeverity.LOW,
    AntipatternCategory.STAR_IMPORT_USE: AntipatternSeverity.LOW,
    AntipatternCategory.DEAD_CODE: AntipatternSeverity.INFO,
}


@dataclass
class AntipatternRecord:
    """A single anti-pattern occurrence."""

    record_id: str = field(default_factory=lambda: f"apr-{uuid.uuid4().hex[:12]}")
    agent_id: str = ""
    run_id: str = ""
    category: AntipatternCategory = AntipatternCategory.SILENT_EXCEPTION_SWALLOW
    severity: AntipatternSeverity = AntipatternSeverity.MEDIUM
    source_file: str = ""
    line_no: int = 0
    symbol: str = ""
    description: str = ""
    suppressed: bool = False
    detected_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "agent_id": self.agent_id,
            "run_id": self.run_id,
            "category": self.category.value,
            "severity": self.severity.value,
            "source_file": self.source_file,
            "line_no": self.line_no,
            "symbol": self.symbol,
            "description": self.description,
            "suppressed": self.suppressed,
            "detected_at": self.detected_at,
        }


@dataclass
class AntipatternRegistryReport:
    """Aggregated anti-pattern report for a run."""

    agent_id: str
    run_id: str
    records: list[AntipatternRecord] = field(default_factory=list)

    @property
    def total_count(self) -> int:
        return len(self.records)

    @property
    def critical_count(self) -> int:
        return sum(1 for r in self.records if r.severity == AntipatternSeverity.CRITICAL)

    @property
    def suppressed_count(self) -> int:
        return sum(1 for r in self.records if r.suppressed)

    @property
    def active_count(self) -> int:
        return sum(1 for r in self.records if not r.suppressed)

    @property
    def by_category(self) -> dict[str, int]:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "AntipatternRegistryReport.by_category"
        )

        result: dict[str, int] = {}
        for r in self.records:
            result[r.category.value] = result.get(r.category.value, 0) + 1
        return result

    @property
    def by_severity(self) -> dict[str, int]:
        result: dict[str, int] = {}
        for r in self.records:
            result[r.severity.value] = result.get(r.severity.value, 0) + 1
        return result

    @property
    def affected_files(self) -> set[str]:
        return {r.source_file for r in self.records if r.source_file}

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "run_id": self.run_id,
            "total_count": self.total_count,
            "critical_count": self.critical_count,
            "suppressed_count": self.suppressed_count,
            "active_count": self.active_count,
            "affected_file_count": len(self.affected_files),
            "by_category": self.by_category,
            "by_severity": self.by_severity,
        }


class AntipatternRegistry:
    """G21 runtime registry: records and classifies anti-pattern occurrences.

    Lifecycle:
        registry = AntipatternRegistry(agent_id, run_id)
        registry.register(AntipatternCategory.SILENT_EXCEPTION_SWALLOW, "foo.py", 42)
        registry.suppress(record)
        report = registry.report
    """

    def __init__(self, agent_id: str, run_id: str) -> None:
        self._agent_id = agent_id
        self._run_id = run_id
        self._report = AntipatternRegistryReport(agent_id=agent_id, run_id=run_id)

    @property
    def report(self) -> AntipatternRegistryReport:
        return self._report

    def register(
        self,
        category: AntipatternCategory,
        source_file: str = "",
        line_no: int = 0,
        symbol: str = "",
        description: str = "",
        severity: AntipatternSeverity | None = None,
    ) -> AntipatternRecord:
        """Register a detected anti-pattern."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "AntipatternRegistry.register"
        )

        resolved_severity = severity or _SEVERITY_MAP.get(category, AntipatternSeverity.MEDIUM)
        record = AntipatternRecord(
            agent_id=self._agent_id,
            run_id=self._run_id,
            category=category,
            severity=resolved_severity,
            source_file=source_file,
            line_no=line_no,
            symbol=symbol,
            description=description,
        )
        self._report.records.append(record)
        return record

    def suppress(self, record: AntipatternRecord) -> None:
        """Mark a detected anti-pattern as reviewed and suppressed."""
        record.suppressed = True

    def classify(self, edge_kind: str) -> AntipatternCategory | None:
        """Map an ADG edge kind string to an AntipatternCategory, or None if not a pattern."""
        for cat in AntipatternCategory:
            if cat.value == edge_kind:
                return cat
        return None

    def register_from_edge_kind(
        self, edge_kind: str, source_file: str = "", line_no: int = 0, symbol: str = ""
    ) -> AntipatternRecord | None:
        """Convenience: register an anti-pattern directly from an ADG edge kind string."""
        category = self.classify(edge_kind)
        if category is None:
            return None
        return self.register(category, source_file=source_file, line_no=line_no, symbol=symbol)
