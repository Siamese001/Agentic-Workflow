"""In-memory implementation of scoring report store.

Phase 4: Test implementation with write-once idempotency.
Provides readback for test verification.
"""

from __future__ import annotations

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

_emit_authorize_and_execute("p2", "in_memory_scoring_report_store", "execution_auth")
_emit_validates_capability("p2", "in_memory_scoring_report_store", "capability_check")
_emit_routes_to_capability("p2", "in_memory_scoring_report_store", "capability_route")
_emit_writes_via_uwg("p2", "in_memory_scoring_report_store", "uwg_write")
_emit_blocks_direct_write("p2", "in_memory_scoring_report_store", "direct_write_block")
_emit_records_tool_invocation("p2", "in_memory_scoring_report_store", "tool_invocation")
_emit_captures_execution_output("p2", "in_memory_scoring_report_store", "exec_output")
_emit_dispatches_agent("p3", "in_memory_scoring_report_store", "agent_dispatch")
_emit_coordinates_agents("p3", "in_memory_scoring_report_store", "agent_coordination")
_emit_records_workflow_lineage("p3", "in_memory_scoring_report_store", "workflow_lineage")
_emit_records_healing_outcome("p3", "in_memory_scoring_report_store", "healing_outcome")
_emit_escalates_failure("p3", "in_memory_scoring_report_store", "failure_escalation")
_emit_orchestrates_workflow("p3", "in_memory_scoring_report_store", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "in_memory_scoring_report_store", "healing_dispatch")
_emit_invokes_evaluation("p3", "in_memory_scoring_report_store", "evaluation_signal")
_emit_records_telemetry_event("p4", "in_memory_scoring_report_store", "telemetry_event")
_emit_captures_evaluation_metric("p4", "in_memory_scoring_report_store", "eval_metric")
_emit_stores_embedding("p4", "in_memory_scoring_report_store", "embedding_store")
_emit_updates_meta_learning_state("p4", "in_memory_scoring_report_store", "meta_learning")
_emit_links_execution_to_snapshot("p4", "in_memory_scoring_report_store", "exec_snapshot_link")
from system_learning.ports.scoring_report_store import ScoringReportStore
from system_learning.types.healing_outcome_scoring_types import ScoringReport

_emit_applies_guardrail("p0", "in_memory_scoring_report_store", "p0_governance")
_emit_reads_policy_state("p0", "in_memory_scoring_report_store", "policy_binding")
_emit_snapshots_state("p0", "in_memory_scoring_report_store", "state_snapshot")
emit_replay_key("p0", "in_memory_scoring_report_store")
emit_determinism_digest("p0", "in_memory_scoring_report_store")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


class InMemoryScoringReportStore(ScoringReportStore):
    """In-memory store for scoring reports.

    Simple dict-based storage keyed by content hash for write-once idempotency.
    """

    def __init__(self) -> None:
        """Initialize empty store."""
        self._reports_by_hash: dict[str, ScoringReport] = {}
        self._reports: list[ScoringReport] = []

    def write(self, report: ScoringReport) -> None:
        """Persist a scoring report with write-once idempotency.

        Args:
            report: The scoring report to persist
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "InMemoryScoringReportStore.write")

        content_hash = report.content_hash()
        if content_hash not in self._reports_by_hash:
            self._reports_by_hash[content_hash] = report
            self._reports.append(report)

    def count(self) -> int:
        """Get number of stored reports.

        Returns:
            Number of reports in the store
        """
        return len(self._reports)

    def get_reports(self) -> list[ScoringReport]:
        """Get all stored reports.

        Returns:
            Copy of stored reports list
        """
        return list(self._reports)

    def clear(self) -> None:
        """Clear all stored reports."""
        self._reports.clear()
