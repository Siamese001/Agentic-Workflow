from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

"\nChange Tracker - Sovereign Healing Audit Trail\nCanon-compliant utility for tracking file modifications by healer/fixer agents.\n\nLocation: agentic_core/utils/general_helpers/change_tracker.py\nDepth: 3 (per SSOT semantic_l2_registry['utils']['general_helpers'])\nPurpose: Domain-agnostic core utility for miscellaneous tracking\n"
import uuid
from collections import defaultdict
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
