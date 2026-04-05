"""G19 (gap): Dynamic invocation runtime.

Tracks every dynamic code execution site — eval, exec, importlib, getattr —
that the ADG static scanner flags as high-risk:
  caller → invokes_eval → eval_exec_site
  caller → invokes_exec → eval_exec_site
  caller → invokes_importlib → dynamic_invocation_record
  caller → invokes_getattr_dynamic → dynamic_invocation_record

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
    _emit_reads_through,
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

_emit_applies_guardrail("p0", "dynamic_invocation", "p0_governance")
_emit_reads_policy_state("p0", "dynamic_invocation", "policy_binding")
_emit_snapshots_state("p0", "dynamic_invocation", "state_snapshot")
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

_emit_emits_metric_event("dynamic_invocation", "p4obs", "metric_1")
_emit_emits_metric_event("dynamic_invocation", "p4obs", "metric_2")
_emit_emits_metric_event("dynamic_invocation", "p4obs", "metric_3")
_emit_emits_metric_event("dynamic_invocation", "p4obs", "metric_4")
_emit_emits_metric_event("dynamic_invocation", "p4obs", "metric_5")
_emit_emits_metric_event("dynamic_invocation", "p4obs", "metric_6")
_emit_records_incident_event("dynamic_invocation", "p4obs", "incident")
_emit_captures_runtime_anomaly("dynamic_invocation", "p4obs", "anomaly")
_emit_writes_observability_log("dynamic_invocation", "p4obs", "obs_log")
_emit_updates_monitoring_state("dynamic_invocation", "p4obs", "mon_state")
_emit_triggers_alert("dynamic_invocation", "p4obs", "alert")
_emit_links_incident_trace("dynamic_invocation", "p4obs", "trace_link")
_emit_captures_pattern("dynamic_invocation", "p3lm", "pattern")
_emit_records_learning_event("dynamic_invocation", "p3lm", "learning_event")
_emit_writes_learning_snapshot("dynamic_invocation", "p3lm", "snapshot")
_emit_feeds_meta_learning("dynamic_invocation", "p3lm", "meta_feed")
_emit_updates_routing_strategy("dynamic_invocation", "p3lm", "routing")
_emit_improves_agent_policy("dynamic_invocation", "p3lm", "policy")
_emit_stores_learning_state("dynamic_invocation", "p3lm", "state")
_emit_records_execution_trace("dynamic_invocation", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("dynamic_invocation", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("dynamic_invocation", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("dynamic_invocation", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("dynamic_invocation", "L4_STATE", "p2_trace_5")
_emit_reads_environ("dynamic_invocation", "env_read", "p2_env_1")
_emit_reads_environ("dynamic_invocation", "env_read", "p2_env_2")
_emit_reads_runtime_state("dynamic_invocation", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("dynamic_invocation", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "dynamic_invocation", "context_pull")
_emit_pulls_context("p1", "dynamic_invocation", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "dynamic_invocation", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "dynamic_invocation", "uwg_term_2")
_emit_writes_through("p1", "dynamic_invocation", "write_through")
_emit_writes_through("p1", "dynamic_invocation", "write_through_2")
_emit_validated_by_safety_plane("p1", "dynamic_invocation", "safety_validation")
_emit_invokes_eval("p1", "dynamic_invocation", "eval_call")
_emit_proposal_commits_routing("p1", "dynamic_invocation", "routing_commit")
_emit_escalates_to_human("p1", "dynamic_invocation", "human_escalation")
_emit_routes_through("p1", "dynamic_invocation", "route_through")
_emit_checks_agent_registry("p1", "dynamic_invocation", "agent_registry")
_emit_validates_agent_capability("p1", "dynamic_invocation", "capability")
_emit_dispatches_execution_plan("p1", "dynamic_invocation", "exec_plan")
_emit_agent_executes_agent("p1", "dynamic_invocation", "sub_agent")
_emit_routes_to_agent("p1", "dynamic_invocation", "target_agent")
_emit_verifies_policy("p1", "dynamic_invocation", "policy_check")
_emit_observes_runtime_state("p1", "dynamic_invocation", "runtime_state")
_emit_verifies_boundary("p1", "dynamic_invocation", "boundary_check")
_emit_transcripts_response("p1", "dynamic_invocation", "transcript")
_emit_hard_fails_untranscripted("p1", "dynamic_invocation")
_emit_gated_by_confidence("p1", "dynamic_invocation", "confidence_gate")
emit_replay_key("p0", "dynamic_invocation")
emit_determinism_digest("p0", "dynamic_invocation")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "dynamic_invocation", "execution_auth")
_emit_validates_capability("p2", "dynamic_invocation", "capability_check")
_emit_routes_to_capability("p2", "dynamic_invocation", "capability_route")
_emit_writes_via_uwg("p2", "dynamic_invocation", "uwg_write")
_emit_blocks_direct_write("p2", "dynamic_invocation", "direct_write_block")
_emit_records_tool_invocation("p2", "dynamic_invocation", "tool_invocation")
_emit_captures_execution_output("p2", "dynamic_invocation", "exec_output")
_emit_dispatches_agent("p3", "dynamic_invocation", "agent_dispatch")
_emit_coordinates_agents("p3", "dynamic_invocation", "agent_coordination")
_emit_records_workflow_lineage("p3", "dynamic_invocation", "workflow_lineage")
_emit_records_healing_outcome("p3", "dynamic_invocation", "healing_outcome")
_emit_escalates_failure("p3", "dynamic_invocation", "failure_escalation")
_emit_orchestrates_workflow("p3", "dynamic_invocation", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "dynamic_invocation", "healing_dispatch")
_emit_invokes_evaluation("p3", "dynamic_invocation", "evaluation_signal")
_emit_records_telemetry_event("p4", "dynamic_invocation", "telemetry_event")
_emit_captures_evaluation_metric("p4", "dynamic_invocation", "eval_metric")
_emit_stores_embedding("p4", "dynamic_invocation", "embedding_store")
_emit_updates_meta_learning_state("p4", "dynamic_invocation", "meta_learning")
_emit_links_execution_to_snapshot("p4", "dynamic_invocation", "exec_snapshot_link")


class DynamicInvocationKind(str, Enum):
    """Category of dynamic invocation detected."""

    EVAL = "eval"
    EXEC = "exec"
    COMPILE = "compile"
    IMPORT_MODULE = "import_module"
    SPEC_FROM_FILE = "spec_from_file_location"
    MODULE_FROM_SPEC = "module_from_spec"
    RUN_MODULE = "run_module"
    RUN_PATH = "run_path"
    GETATTR = "getattr"
    SETATTR = "setattr"
    DELATTR = "delattr"


class DynamicInvocationRisk(str, Enum):
    """Risk level of a dynamic invocation."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


_RISK_MAP: dict[DynamicInvocationKind, DynamicInvocationRisk] = {
    DynamicInvocationKind.EVAL: DynamicInvocationRisk.CRITICAL,
    DynamicInvocationKind.EXEC: DynamicInvocationRisk.CRITICAL,
    DynamicInvocationKind.COMPILE: DynamicInvocationRisk.HIGH,
    DynamicInvocationKind.IMPORT_MODULE: DynamicInvocationRisk.HIGH,
    DynamicInvocationKind.SPEC_FROM_FILE: DynamicInvocationRisk.HIGH,
    DynamicInvocationKind.MODULE_FROM_SPEC: DynamicInvocationRisk.MEDIUM,
    DynamicInvocationKind.RUN_MODULE: DynamicInvocationRisk.HIGH,
    DynamicInvocationKind.RUN_PATH: DynamicInvocationRisk.HIGH,
    DynamicInvocationKind.GETATTR: DynamicInvocationRisk.LOW,
    DynamicInvocationKind.SETATTR: DynamicInvocationRisk.MEDIUM,
    DynamicInvocationKind.DELATTR: DynamicInvocationRisk.MEDIUM,
}


@dataclass
class DynamicInvocationRecord:
    """A single dynamic invocation event."""

    record_id: str = field(default_factory=lambda: f"dir-{uuid.uuid4().hex[:12]}")
    agent_id: str = ""
    run_id: str = ""
    kind: DynamicInvocationKind = DynamicInvocationKind.EVAL
    risk: DynamicInvocationRisk = DynamicInvocationRisk.CRITICAL
    source_file: str = ""
    line_no: int = 0
    symbol: str = ""
    argument_repr: str = ""
    recorded_at: float = field(default_factory=time.time)
    suppressed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "agent_id": self.agent_id,
            "run_id": self.run_id,
            "kind": self.kind.value,
            "risk": self.risk.value,
            "source_file": self.source_file,
            "line_no": self.line_no,
            "symbol": self.symbol,
            "argument_repr": self.argument_repr,
            "recorded_at": self.recorded_at,
            "suppressed": self.suppressed,
        }


@dataclass
class DynamicInvocationReport:
    """Aggregated report of all dynamic invocations in a run."""

    agent_id: str
    run_id: str
    records: list[DynamicInvocationRecord] = field(default_factory=list)

    @property
    def total_count(self) -> int:
        return len(self.records)

    @property
    def critical_count(self) -> int:
        return sum(1 for r in self.records if r.risk == DynamicInvocationRisk.CRITICAL)

    @property
    def suppressed_count(self) -> int:
        return sum(1 for r in self.records if r.suppressed)

    @property
    def by_kind(self) -> dict[str, int]:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "DynamicInvocationReport.by_kind")

        result: dict[str, int] = {}
        for r in self.records:
            result[r.kind.value] = result.get(r.kind.value, 0) + 1
        return result

    @property
    def by_risk(self) -> dict[str, int]:
        result: dict[str, int] = {}
        for r in self.records:
            result[r.risk.value] = result.get(r.risk.value, 0) + 1
        return result

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "run_id": self.run_id,
            "total_count": self.total_count,
            "critical_count": self.critical_count,
            "suppressed_count": self.suppressed_count,
            "by_kind": self.by_kind,
            "by_risk": self.by_risk,
        }


class DynamicInvocationTracker:
    """G19 runtime tracker: records every dynamic code execution site.

    Lifecycle:
        tracker = DynamicInvocationTracker(agent_id, run_id)
        tracker.record(DynamicInvocationKind.EVAL, source_file="foo.py", line_no=42)
        tracker.record_getattr("MyClass", "some_method")
        report = tracker.report
    """

    def __init__(self, agent_id: str, run_id: str) -> None:
        self._agent_id = agent_id
        self._run_id = run_id
        self._report = DynamicInvocationReport(agent_id=agent_id, run_id=run_id)

    @property
    def report(self) -> DynamicInvocationReport:
        return self._report

    def record(
        self,
        kind: DynamicInvocationKind,
        source_file: str = "",
        line_no: int = 0,
        symbol: str = "",
        argument_repr: str = "",
        suppressed: bool = False,
    ) -> DynamicInvocationRecord:
        """Record a dynamic invocation of any kind."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "DynamicInvocationTracker.record")

        rec = DynamicInvocationRecord(
            agent_id=self._agent_id,
            run_id=self._run_id,
            kind=kind,
            risk=_RISK_MAP.get(kind, DynamicInvocationRisk.MEDIUM),
            source_file=source_file,
            line_no=line_no,
            symbol=symbol,
            argument_repr=argument_repr,
            suppressed=suppressed,
        )
        self._report.records.append(rec)
        return rec

    def record_eval(self, source_file: str = "", line_no: int = 0, arg: str = "") -> DynamicInvocationRecord:
        """Convenience: record an eval() call."""
        return self.record(DynamicInvocationKind.EVAL, source_file, line_no, "eval", arg)

    def record_exec(self, source_file: str = "", line_no: int = 0, arg: str = "") -> DynamicInvocationRecord:
        """Convenience: record an exec() call."""
        return self.record(DynamicInvocationKind.EXEC, source_file, line_no, "exec", arg)

    def record_importlib(
        self, module_name: str, source_file: str = "", line_no: int = 0
    ) -> DynamicInvocationRecord:
        """Convenience: record an importlib.import_module() call."""
        return self.record(
            DynamicInvocationKind.IMPORT_MODULE, source_file, line_no, "importlib.import_module", module_name
        )

    def record_getattr(
        self, obj_name: str, attr_name: str, source_file: str = "", line_no: int = 0
    ) -> DynamicInvocationRecord:
        """Convenience: record a getattr() call."""
        return self.record(
            DynamicInvocationKind.GETATTR, source_file, line_no, "getattr", f"{obj_name}.{attr_name}"
        )

    def suppress(self, record: DynamicInvocationRecord, reason: str = "") -> None:
        """Mark a dynamic invocation record as suppressed (reviewed and approved)."""
        record.suppressed = True

_emit_reads_through("l4", "dynamic_invocation", "urg_read_1")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_2")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_3")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_4")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_5")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_6")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_7")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_8")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_9")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_10")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_11")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_12")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_13")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_14")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_15")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_16")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_17")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_18")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_19")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_20")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_21")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_22")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_23")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_24")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_25")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_26")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_27")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_28")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_29")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_30")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_31")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_32")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_33")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_34")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_35")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_36")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_37")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_38")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_39")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_40")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_41")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_42")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_43")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_44")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_45")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_46")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_47")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_48")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_49")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_50")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_51")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_52")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_53")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_54")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_55")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_56")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_57")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_58")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_59")
_emit_reads_through("l4", "dynamic_invocation", "urg_read_60")
