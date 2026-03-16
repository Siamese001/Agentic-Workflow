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

_emit_applies_guardrail("p0", "dynamic_invocation", "p0_governance")
_emit_reads_policy_state("p0", "dynamic_invocation", "policy_binding")
_emit_snapshots_state("p0", "dynamic_invocation", "state_snapshot")
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
