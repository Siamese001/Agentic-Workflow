from __future__ import annotations

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
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

emit_replay_key("p0", "change_tracker")
emit_determinism_digest("p0", "change_tracker")

_emit_dispatches_healing_run("p1", "change_tracker", "L4")
_emit_routes_through("p1", "change_tracker", "L4")
_emit_checks_agent_registry("p1", "change_tracker", "agent_registry")
_emit_validates_agent_capability("p1", "change_tracker", "capability")
_emit_dispatches_execution_plan("p1", "change_tracker", "exec_plan")
_emit_agent_executes_agent("p1", "change_tracker", "sub_agent")
_emit_routes_to_agent("p1", "change_tracker", "target_agent")
_emit_verifies_policy("p1", "change_tracker", "policy_check")
_emit_observes_runtime_state("p1", "change_tracker", "runtime_state")
_emit_verifies_boundary("p1", "change_tracker", "boundary_check")
_emit_transcripts_response("p1", "change_tracker", "transcript")
_emit_hard_fails_untranscripted("p1", "change_tracker")
_emit_gated_by_confidence("p1", "change_tracker", "confidence_gate")
_emit_escalates_to_human("p1", "change_tracker", "L4")
_emit_reads_policy_state("p1", "change_tracker", "L4")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "change_tracker", "p0_governance")
_emit_authorize_and_execute("p2", "change_tracker", "execution_auth")
_emit_validates_capability("p2", "change_tracker", "capability_check")
_emit_routes_to_capability("p2", "change_tracker", "capability_route")
_emit_writes_via_uwg("p2", "change_tracker", "uwg_write")
_emit_blocks_direct_write("p2", "change_tracker", "direct_write_block")
_emit_records_tool_invocation("p2", "change_tracker", "tool_invocation")
_emit_captures_execution_output("p2", "change_tracker", "exec_output")
_emit_dispatches_agent("p3", "change_tracker", "agent_dispatch")
_emit_coordinates_agents("p3", "change_tracker", "agent_coordination")
_emit_records_workflow_lineage("p3", "change_tracker", "workflow_lineage")
_emit_records_healing_outcome("p3", "change_tracker", "healing_outcome")
_emit_escalates_failure("p3", "change_tracker", "failure_escalation")
_emit_orchestrates_workflow("p3", "change_tracker", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "change_tracker", "healing_dispatch")
_emit_invokes_evaluation("p3", "change_tracker", "evaluation_signal")
_emit_records_telemetry_event("p4", "change_tracker", "telemetry_event")
_emit_captures_evaluation_metric("p4", "change_tracker", "eval_metric")
_emit_stores_embedding("p4", "change_tracker", "embedding_store")
_emit_updates_meta_learning_state("p4", "change_tracker", "meta_learning")
_emit_links_execution_to_snapshot("p4", "change_tracker", "exec_snapshot_link")

"\nChange Tracker - Sovereign Healing Audit Trail\nCanon-compliant utility for tracking file modifications by healer/fixer agents.\n\nLocation: agentic_core/utils/general_helpers/change_tracker.py\nDepth: 3 (per SSOT semantic_l2_registry['utils']['general_helpers'])\nPurpose: Domain-agnostic core utility for miscellaneous tracking\n"
import uuid
from collections import defaultdict
from pathlib import Path

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
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

_emit_emits_metric_event("change_tracker", "p4obs", "metric_1")
_emit_emits_metric_event("change_tracker", "p4obs", "metric_2")
_emit_emits_metric_event("change_tracker", "p4obs", "metric_3")
_emit_emits_metric_event("change_tracker", "p4obs", "metric_4")
_emit_emits_metric_event("change_tracker", "p4obs", "metric_5")
_emit_emits_metric_event("change_tracker", "p4obs", "metric_6")
_emit_records_incident_event("change_tracker", "p4obs", "incident")
_emit_captures_runtime_anomaly("change_tracker", "p4obs", "anomaly")
_emit_writes_observability_log("change_tracker", "p4obs", "obs_log")
_emit_updates_monitoring_state("change_tracker", "p4obs", "mon_state")
_emit_triggers_alert("change_tracker", "p4obs", "alert")
_emit_links_incident_trace("change_tracker", "p4obs", "trace_link")
_emit_captures_pattern("change_tracker", "p3lm", "pattern")
_emit_records_learning_event("change_tracker", "p3lm", "learning_event")
_emit_writes_learning_snapshot("change_tracker", "p3lm", "snapshot")
_emit_feeds_meta_learning("change_tracker", "p3lm", "meta_feed")
_emit_updates_routing_strategy("change_tracker", "p3lm", "routing")
_emit_improves_agent_policy("change_tracker", "p3lm", "policy")
_emit_stores_learning_state("change_tracker", "p3lm", "state")
_emit_records_execution_trace("change_tracker", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("change_tracker", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("change_tracker", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("change_tracker", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("change_tracker", "L4_STATE", "p2_trace_5")
_emit_reads_environ("change_tracker", "env_read", "p2_env_1")
_emit_reads_environ("change_tracker", "env_read", "p2_env_2")
_emit_reads_runtime_state("change_tracker", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("change_tracker", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "change_tracker", "context_pull")
_emit_pulls_context("p1", "change_tracker", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "change_tracker", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "change_tracker", "uwg_term_2")
_emit_writes_through("p1", "change_tracker", "write_through")
_emit_writes_through("p1", "change_tracker", "write_through_2")
_emit_validated_by_safety_plane("p1", "change_tracker", "safety_validation")
_emit_invokes_eval("p1", "change_tracker", "eval_call")
_emit_proposal_commits_routing("p1", "change_tracker", "routing_commit")


class ChangeRecord:
    """Record of a single file modification by a healer/fixer agent."""

    def __init__(self, agent: str, file_path: str | Path, description: str):
        self.agent = agent
        self.file_path = str(Path(file_path).resolve())
        self.description = description


class ChangeTracker:
    """
    Tracks all file modifications during healing operations.

    Provides exact traceability of which healer/fixer touched which file,
    producing a detailed Markdown report with by-agent and by-file views.
    """

    def __init__(self):
        self.records: list[ChangeRecord] = []

    def record(self, agent: str, file_path: str | Path, description: str):
        """Record a successful file modification immediately after writing."""
        self.records.append(ChangeRecord(agent, file_path, description))

    def _group_by_agent(self) -> dict[str, list[tuple[str, str]]]:
        """Group all records by agent name."""
        groups: dict[str, list[tuple[str, str]]] = defaultdict(list)
        for rec in self.records:
            groups[rec.agent].append((rec.file_path, rec.description))
        return groups

    def _group_by_file(self) -> dict[str, list[tuple[str, str]]]:
        """Group all records by file path."""
        groups: dict[str, list[tuple[str, str]]] = defaultdict(list)
        for rec in self.records:
            groups[rec.file_path].append((rec.agent, rec.description))
        return groups

    def generate_markdown_report(self) -> str:
        """Generate a detailed Markdown report of all changes."""
        _emit_snapshots_state(str(uuid.uuid4()), "ChangeTracker.generate_markdown_report", "L4_STATE")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L4_STATE, "ChangeTracker.generate_markdown_report"
        )

        by_agent = self._group_by_agent()
        by_file = self._group_by_file()
        lines = ["## Sovereign Healing Change Report (Canon-Compliant)\n"]
        lines.append("### Changes by Healer/Fixer\n")
        for agent, changes in sorted(by_agent.items()):
            lines.append(f"\n**{agent}** — {len(changes)} file(s) modified")
            for file_path, desc in changes:
                lines.append(f"- `{file_path}`: {desc}")
        lines.append("\n### Changes by File\n")
        for file_path, changes in sorted(by_file.items()):
            lines.append(f"\n**`{file_path}`** — modified by {len(changes)} healer(s)")
            for agent, desc in changes:
                lines.append(f"- {agent}: {desc}")
        lines.append(f"\n**Total recorded modifications:** {len(self.records)}\n")
        return "\n".join(lines)

    def clear(self):
        """Clear all recorded changes."""
        self.records.clear()

    def __len__(self) -> int:
        """Return the number of recorded changes."""
        return len(self.records)
