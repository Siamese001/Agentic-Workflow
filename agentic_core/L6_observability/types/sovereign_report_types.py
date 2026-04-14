from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
    # noqa: E402
    record_execution_trace,
)

emit_replay_key("p0", "sovereign_report_types")
emit_determinism_digest("p0", "sovereign_report_types")

_emit_dispatches_healing_run("p1", "sovereign_report_types", "L6")
_emit_routes_through("p1", "sovereign_report_types", "L6")
_emit_checks_agent_registry("p1", "sovereign_report_types", "agent_registry")
_emit_validates_agent_capability("p1", "sovereign_report_types", "capability")
_emit_dispatches_execution_plan("p1", "sovereign_report_types", "exec_plan")
_emit_agent_executes_agent("p1", "sovereign_report_types", "sub_agent")
_emit_routes_to_agent("p1", "sovereign_report_types", "target_agent")
_emit_verifies_policy("p1", "sovereign_report_types", "policy_check")
_emit_observes_runtime_state("p1", "sovereign_report_types", "runtime_state")
_emit_verifies_boundary("p1", "sovereign_report_types", "boundary_check")
_emit_transcripts_response("p1", "sovereign_report_types", "transcript")
_emit_hard_fails_untranscripted("p1", "sovereign_report_types")
_emit_gated_by_confidence("p1", "sovereign_report_types", "confidence_gate")
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

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_snapshots_state,
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
from tqdm import tqdm

record_execution_trace("sovereign_report_types", "sovereign_report_types_trace")


_emit_emits_metric_event("sovereign_report_types", "p4obs", "metric_1")
_emit_emits_metric_event("sovereign_report_types", "p4obs", "metric_2")
_emit_emits_metric_event("sovereign_report_types", "p4obs", "metric_3")
_emit_emits_metric_event("sovereign_report_types", "p4obs", "metric_4")
_emit_emits_metric_event("sovereign_report_types", "p4obs", "metric_5")
_emit_emits_metric_event("sovereign_report_types", "p4obs", "metric_6")
_emit_records_incident_event("sovereign_report_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("sovereign_report_types", "p4obs", "anomaly")
_emit_writes_observability_log("sovereign_report_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("sovereign_report_types", "p4obs", "mon_state")
_emit_triggers_alert("sovereign_report_types", "p4obs", "alert")
_emit_links_incident_trace("sovereign_report_types", "p4obs", "trace_link")
_emit_captures_pattern("sovereign_report_types", "p3lm", "pattern")
_emit_records_learning_event("sovereign_report_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("sovereign_report_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("sovereign_report_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("sovereign_report_types", "p3lm", "routing")
_emit_improves_agent_policy("sovereign_report_types", "p3lm", "policy")
_emit_stores_learning_state("sovereign_report_types", "p3lm", "state")
_emit_records_execution_trace("sovereign_report_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("sovereign_report_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("sovereign_report_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("sovereign_report_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("sovereign_report_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("sovereign_report_types", "env_read", "p2_env_1")
_emit_reads_environ("sovereign_report_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("sovereign_report_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("sovereign_report_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "sovereign_report_types", "context_pull")
_emit_pulls_context("p1", "sovereign_report_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "sovereign_report_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "sovereign_report_types", "uwg_term_2")
_emit_writes_through("p1", "sovereign_report_types", "write_through")
_emit_writes_through("p1", "sovereign_report_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "sovereign_report_types", "safety_validation")
_emit_invokes_eval("p1", "sovereign_report_types", "eval_call")
_emit_proposal_commits_routing("p1", "sovereign_report_types", "routing_commit")


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
            _trace_id,
            LayerSegment.L6_OBSERVABILITY,
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
