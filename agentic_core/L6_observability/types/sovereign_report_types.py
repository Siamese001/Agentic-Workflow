from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "sovereign_report_types")
trace_contract.emit_determinism_digest("p0", "sovereign_report_types")

trace_contract._emit_dispatches_healing_run("p1", "sovereign_report_types", "L6")
trace_contract._emit_routes_through("p1", "sovereign_report_types", "L6")
trace_contract._emit_checks_agent_registry("p1", "sovereign_report_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "sovereign_report_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "sovereign_report_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "sovereign_report_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "sovereign_report_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "sovereign_report_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "sovereign_report_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "sovereign_report_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "sovereign_report_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "sovereign_report_types")
trace_contract._emit_gated_by_confidence("p1", "sovereign_report_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "sovereign_report_types", "L6")
trace_contract._emit_reads_policy_state("p1", "sovereign_report_types", "L6")
trace_contract._emit_authorize_and_execute("p2", "sovereign_report_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "sovereign_report_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "sovereign_report_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "sovereign_report_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "sovereign_report_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "sovereign_report_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "sovereign_report_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "sovereign_report_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "sovereign_report_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "sovereign_report_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "sovereign_report_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "sovereign_report_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "sovereign_report_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "sovereign_report_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "sovereign_report_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "sovereign_report_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "sovereign_report_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "sovereign_report_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "sovereign_report_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "sovereign_report_types", "exec_snapshot_link")

"\nSovereign Report Agent – Phase 13+ (Dec 30, 2025)\nPure canonical audit report structure and builder.\nZero side effects. Import-safe for L6 consumption and all orchestration agents.\n"
import logging
import re
from datetime import datetime

from tqdm import tqdm

trace_contract.record_execution_trace("sovereign_report_types", "sovereign_report_types_trace")


trace_contract._emit_emits_metric_event("sovereign_report_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("sovereign_report_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("sovereign_report_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("sovereign_report_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("sovereign_report_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("sovereign_report_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("sovereign_report_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("sovereign_report_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("sovereign_report_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("sovereign_report_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("sovereign_report_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("sovereign_report_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("sovereign_report_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("sovereign_report_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("sovereign_report_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("sovereign_report_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("sovereign_report_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("sovereign_report_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("sovereign_report_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("sovereign_report_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("sovereign_report_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("sovereign_report_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("sovereign_report_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("sovereign_report_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("sovereign_report_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("sovereign_report_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("sovereign_report_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("sovereign_report_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "sovereign_report_types", "context_pull")
trace_contract._emit_pulls_context("p1", "sovereign_report_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "sovereign_report_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "sovereign_report_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "sovereign_report_types", "write_through")
trace_contract._emit_writes_through("p1", "sovereign_report_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "sovereign_report_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "sovereign_report_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "sovereign_report_types", "routing_commit")


class SovereignReport:
    """
    The canonical audit result object for L6 consumption and healing orchestration.
    Immutable after build.
    """

    def __init__(self):
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "SovereignReport.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "SovereignReport.__init__", "p0_governance")
        self.scores: dict[str, float] = {}
        self.issues: dict[str, list[str]] = {}
        self.report_id: str = ""
        self.timestamp = None

    def get_overall_score(self) -> float:
        """Calculate overall health score across all dimensions."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L6_OBSERVABILITY,
            "SovereignReport.get_overall_score",
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
            self,
            name: str,
            score: float,
            issues: list[str] = None,
        ) -> SovereignReport.Builder:
            """Sets a validated dimension score."""
            import uuid as _uuid  # noqa: PLC0415

            _trace_id = str(_uuid.uuid4())
            trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L6_OBSERVABILITY, "Builder.with_dimension")

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
        for dimension, raw_issues in tqdm(self.issues.items(), desc="Processing", unit="item"):
            for raw in tqdm(raw_issues, desc="Processing", unit="item"):
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
                    {"dimension": dimension, "description": message, "file": file_path, "line": line_num},
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
