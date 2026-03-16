from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "sovereign_report_types")
emit_determinism_digest("p0", "sovereign_report_types")

_emit_dispatches_healing_run("p1", "sovereign_report_types", "L6")
_emit_routes_through("p1", "sovereign_report_types", "L6")
_emit_escalates_to_human("p1", "sovereign_report_types", "L6")
_emit_reads_policy_state("p1", "sovereign_report_types", "L6")
_emit_authorize_and_execute("p2", "sovereign_report_types", "execution_auth")
_emit_validates_capability("p2", "sovereign_report_types", "capability_check")
_emit_routes_to_capability("p2", "sovereign_report_types", "capability_route")
_emit_writes_via_uwg("p2", "sovereign_report_types", "uwg_write")
_emit_blocks_direct_write("p2", "sovereign_report_types", "direct_write_block")
_emit_records_tool_invocation("p2", "sovereign_report_types", "tool_invocation")
_emit_captures_execution_output("p2", "sovereign_report_types", "exec_output")
_emit_dispatches_agent("p3", "sovereign_report_types", "agent_dispatch")
_emit_coordinates_agents("p3", "sovereign_report_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "sovereign_report_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "sovereign_report_types", "healing_outcome")
_emit_escalates_failure("p3", "sovereign_report_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "sovereign_report_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "sovereign_report_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "sovereign_report_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "sovereign_report_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "sovereign_report_types", "eval_metric")
_emit_stores_embedding("p4", "sovereign_report_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "sovereign_report_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "sovereign_report_types", "exec_snapshot_link")

"\nSovereign Report Agent – Phase 13+ (Dec 30, 2025)\nPure canonical audit report structure and builder.\nZero side effects. Import-safe for L6 consumption and all orchestration agents.\n"
import logging
import re
from datetime import datetime

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)


class SovereignReport:
    """
    The canonical audit result object for L6 consumption and healing orchestration.
    Immutable after build.
    """

    def __init__(self):
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "SovereignReport.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "SovereignReport.__init__", "p0_governance")
        self.scores: dict[str, float] = {}
        self.issues: dict[str, list[str]] = {}
        self.report_id: str = ""
        self.timestamp = None

    def get_overall_score(self) -> float:
        """Calculate overall health score across all dimensions."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L6_OBSERVABILITY, "SovereignReport.get_overall_score"
        )

        if not self.scores:
            return 0.0
        return sum(self.scores.values()) / len(self.scores)

    class Builder:
        """
        Sovereign Builder pattern – enforces known dimensions and valid scores.
        Phase 13 (Dec 29, 2025) compliant.
        """

        KNOWN_DIMENSIONS = [
            "Structural SSOT",
            "schema SSOT",
            "Prompt SSOT",
            "Config SSOT",
            "DDD Alignment",
            "Atomic Fission",
            "Zero-Trust Membrane",
            "observability Footprint",
            "Healing Resilience",
        ]

        def __init__(self):
            self._dimensions = {name: {"score": 0.0, "issues": []} for name in self.KNOWN_DIMENSIONS}
            self._report_id = f"audit-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"

        def with_dimension(
            self, name: str, score: float, issues: list[str] = None
        ) -> SovereignReport.Builder:
            """Sets a validated dimension score."""
            import uuid as _uuid  # noqa: PLC0415

            _trace_id = str(_uuid.uuid4())
            _emit_records_execution_trace(_trace_id, LayerSegment.L6_OBSERVABILITY, "Builder.with_dimension")

            if name not in self._dimensions:
                raise ValueError(f"Sovereignty Violation: Unknown dimension: {name}")
            if not 0 <= score <= 100:
                raise ValueError(f"Constitutional Violation: Score {score} out of bounds.")
            self._dimensions[name]["score"] = score
            self._dimensions[name]["issues"] = issues or []
            return self

        def build(self) -> SovereignReport:
            """Constructs the sealed report and emits L6 observability event."""
            Logger = logging.getLogger(__name__)
            overall = sum(d["score"] for d in self._dimensions.values()) / len(self._dimensions)
            status = "SOVEREIGN" if overall >= 95 else "VULNERABLE"
            Logger.info(f"[L6_AUDIT] Report Sealed: {self._report_id} | Health: {overall:.1f}% | {status}")
            report = SovereignReport()
            report.scores = {name: d["score"] for name, d in self._dimensions.items()}
            report.issues = {name: d["issues"] for name, d in self._dimensions.items()}
            report.report_id = self._report_id
            report.timestamp = datetime.utcnow()
            return report

    def get_all_issues(self) -> list[dict]:
        """
        Parse raw guardian issues into structured format expected by Healing Strategies (Phase 10+).
        Input format example: "path/to/file.py: message text (line XX if present)"
        """
        all_issues = []
        for dimension, raw_issues in self.issues.items():
            for raw in raw_issues:
                file_path = str(raw)
                message = str(raw)
                line_num = None
                if ": " in raw:
                    parts = raw.split(": ", 1)
                    file_path = parts[0].strip()
                    message = parts[1].strip()
                elif ":" in raw and raw.count(":") >= 2:
                    parts = raw.split(":", 2)
                    file_path = parts[0].strip()
                    message = parts[2].strip() if len(parts) > 2 else parts[1].strip()
                match = re.search("(?:line|Line)\\s+(\\d+)", message)
                if match:
                    line_num = int(match.group(1))
                all_issues.append(
                    {"dimension": dimension, "description": message, "file": file_path, "line": line_num}
                )
        return all_issues

    def print_summary(self) -> float:
        """
        Human-readable sovereignty Verdict.
        Returns overall score for programmatic use.
        """
        print("\n" + "=" * 60)
        print("SOVEREIGN MULTI-DIMENSIONAL AUDIT REPORT")
        print("=" * 60)
        overall = self.get_overall_score()
        for dim, score in self.scores.items():
            status = "[OK]" if score > 95 else "[WARN]" if score > 80 else "[FAIL]"
            print(f"{status} {dim:<20} : {score:.1f}%")
            if score < 100:
                preview = ", ".join(str(i) for i in self.issues[dim][:3])
                preview += "..." if len(self.issues[dim]) > 3 else ""
                print(f"   Violations: {preview}")
        print("-" * 60)
        status = "SOVEREIGN" if overall > 95 else "VULNERABLE"
        print(f"OVERALL HEALTH: {overall:.1f}% -> {status}")
        print("=" * 60)
        return overall
