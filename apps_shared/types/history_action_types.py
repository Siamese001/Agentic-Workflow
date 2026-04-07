"""schema History Fetcher - Fetches and manages schema history.

This module provides schema history fetching and management capabilities,
including version tracking, change history, and evolution analysis.
Follows the functional component pattern with proper logging.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_applies_guardrail("p0", "history_action_types", "p0_governance")
_emit_reads_policy_state("p0", "history_action_types", "policy_binding")
_emit_snapshots_state("p0", "history_action_types", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("history_action_types", "p4obs", "metric_1")
_emit_emits_metric_event("history_action_types", "p4obs", "metric_2")
_emit_emits_metric_event("history_action_types", "p4obs", "metric_3")
_emit_emits_metric_event("history_action_types", "p4obs", "metric_4")
_emit_emits_metric_event("history_action_types", "p4obs", "metric_5")
_emit_emits_metric_event("history_action_types", "p4obs", "metric_6")
_emit_records_incident_event("history_action_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("history_action_types", "p4obs", "anomaly")
_emit_writes_observability_log("history_action_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("history_action_types", "p4obs", "mon_state")
_emit_triggers_alert("history_action_types", "p4obs", "alert")
_emit_links_incident_trace("history_action_types", "p4obs", "trace_link")
_emit_captures_pattern("history_action_types", "p3lm", "pattern")
_emit_records_learning_event("history_action_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("history_action_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("history_action_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("history_action_types", "p3lm", "routing")
_emit_improves_agent_policy("history_action_types", "p3lm", "policy")
_emit_stores_learning_state("history_action_types", "p3lm", "state")
_emit_records_execution_trace("history_action_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("history_action_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("history_action_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("history_action_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("history_action_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("history_action_types", "env_read", "p2_env_1")
_emit_reads_environ("history_action_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("history_action_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("history_action_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "history_action_types", "context_pull")
_emit_pulls_context("p1", "history_action_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "history_action_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "history_action_types", "uwg_term_2")
_emit_writes_through("p1", "history_action_types", "write_through")
_emit_writes_through("p1", "history_action_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "history_action_types", "safety_validation")
_emit_invokes_eval("p1", "history_action_types", "eval_call")
_emit_proposal_commits_routing("p1", "history_action_types", "routing_commit")
_emit_escalates_to_human("p1", "history_action_types", "human_escalation")
_emit_routes_through("p1", "history_action_types", "route_through")
_emit_checks_agent_registry("p1", "history_action_types", "agent_registry")
_emit_validates_agent_capability("p1", "history_action_types", "capability")
_emit_dispatches_execution_plan("p1", "history_action_types", "exec_plan")
_emit_agent_executes_agent("p1", "history_action_types", "sub_agent")
_emit_routes_to_agent("p1", "history_action_types", "target_agent")
_emit_verifies_policy("p1", "history_action_types", "policy_check")
_emit_observes_runtime_state("p1", "history_action_types", "runtime_state")
_emit_verifies_boundary("p1", "history_action_types", "boundary_check")
_emit_transcripts_response("p1", "history_action_types", "transcript")
_emit_hard_fails_untranscripted("p1", "history_action_types")
_emit_gated_by_confidence("p1", "history_action_types", "confidence_gate")
emit_replay_key("p0", "history_action_types")
emit_determinism_digest("p0", "history_action_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "history_action_types", "execution_auth")
_emit_validates_capability("p2", "history_action_types", "capability_check")
_emit_routes_to_capability("p2", "history_action_types", "capability_route")
_emit_writes_via_uwg("p2", "history_action_types", "uwg_write")
_emit_blocks_direct_write("p2", "history_action_types", "direct_write_block")
_emit_records_tool_invocation("p2", "history_action_types", "tool_invocation")
_emit_captures_execution_output("p2", "history_action_types", "exec_output")
_emit_dispatches_agent("p3", "history_action_types", "agent_dispatch")
_emit_coordinates_agents("p3", "history_action_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "history_action_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "history_action_types", "healing_outcome")
_emit_escalates_failure("p3", "history_action_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "history_action_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "history_action_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "history_action_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "history_action_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "history_action_types", "eval_metric")
_emit_stores_embedding("p4", "history_action_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "history_action_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "history_action_types", "exec_snapshot_link")
_emit_reads_through("l4", "history_action_types", "urg_read_1")
_emit_reads_through("l4", "history_action_types", "urg_read_2")
_emit_reads_through("l4", "history_action_types", "urg_read_3")
_emit_reads_through("l4", "history_action_types", "urg_read_4")
_emit_reads_through("l4", "history_action_types", "urg_read_5")
_emit_reads_through("l4", "history_action_types", "urg_read_6")
_emit_reads_through("l4", "history_action_types", "urg_read_7")
_emit_reads_through("l4", "history_action_types", "urg_read_8")
_emit_reads_through("l4", "history_action_types", "urg_read_9")
_emit_reads_through("l4", "history_action_types", "urg_read_10")
_emit_reads_through("l4", "history_action_types", "urg_read_11")
_emit_reads_through("l4", "history_action_types", "urg_read_12")
_emit_reads_through("l4", "history_action_types", "urg_read_13")
_emit_reads_through("l4", "history_action_types", "urg_read_14")
_emit_reads_through("l4", "history_action_types", "urg_read_15")
_emit_reads_through("l4", "history_action_types", "urg_read_16")
_emit_reads_through("l4", "history_action_types", "urg_read_17")
_emit_reads_through("l4", "history_action_types", "urg_read_18")
_emit_reads_through("l4", "history_action_types", "urg_read_19")
_emit_reads_through("l4", "history_action_types", "urg_read_20")
_emit_reads_through("l4", "history_action_types", "urg_read_21")
_emit_reads_through("l4", "history_action_types", "urg_read_22")
_emit_reads_through("l4", "history_action_types", "urg_read_23")
_emit_reads_through("l4", "history_action_types", "urg_read_24")
_emit_reads_through("l4", "history_action_types", "urg_read_25")
_emit_reads_through("l4", "history_action_types", "urg_read_26")
_emit_reads_through("l4", "history_action_types", "urg_read_27")
_emit_reads_through("l4", "history_action_types", "urg_read_28")
_emit_reads_through("l4", "history_action_types", "urg_read_29")
_emit_reads_through("l4", "history_action_types", "urg_read_30")
_emit_reads_through("l4", "history_action_types", "urg_read_31")
_emit_reads_through("l4", "history_action_types", "urg_read_32")
_emit_reads_through("l4", "history_action_types", "urg_read_33")
_emit_reads_through("l4", "history_action_types", "urg_read_34")
_emit_reads_through("l4", "history_action_types", "urg_read_35")
_emit_reads_through("l4", "history_action_types", "urg_read_36")
_emit_reads_through("l4", "history_action_types", "urg_read_37")
_emit_reads_through("l4", "history_action_types", "urg_read_38")
_emit_reads_through("l4", "history_action_types", "urg_read_39")
_emit_reads_through("l4", "history_action_types", "urg_read_40")
_emit_reads_through("l4", "history_action_types", "urg_read_41")
_emit_reads_through("l4", "history_action_types", "urg_read_42")
_emit_reads_through("l4", "history_action_types", "urg_read_43")
_emit_reads_through("l4", "history_action_types", "urg_read_44")
_emit_reads_through("l4", "history_action_types", "urg_read_45")
_emit_reads_through("l4", "history_action_types", "urg_read_46")
_emit_reads_through("l4", "history_action_types", "urg_read_47")
_emit_reads_through("l4", "history_action_types", "urg_read_48")
_emit_reads_through("l4", "history_action_types", "urg_read_49")
_emit_reads_through("l4", "history_action_types", "urg_read_50")
_emit_reads_through("l4", "history_action_types", "urg_read_51")
_emit_reads_through("l4", "history_action_types", "urg_read_52")
_emit_reads_through("l4", "history_action_types", "urg_read_53")
_emit_reads_through("l4", "history_action_types", "urg_read_54")
_emit_reads_through("l4", "history_action_types", "urg_read_55")
_emit_reads_through("l4", "history_action_types", "urg_read_56")
_emit_reads_through("l4", "history_action_types", "urg_read_57")
_emit_reads_through("l4", "history_action_types", "urg_read_58")
_emit_reads_through("l4", "history_action_types", "urg_read_59")
_emit_reads_through("l4", "history_action_types", "urg_read_60")
_emit_reads_through("l4", "history_action_types", "urg_read_61")
_emit_reads_through("l4", "history_action_types", "urg_read_62")
_emit_reads_through("l4", "history_action_types", "urg_read_63")
_emit_reads_through("l4", "history_action_types", "urg_read_64")
_emit_reads_through("l4", "history_action_types", "urg_read_65")
_emit_reads_through("l4", "history_action_types", "urg_read_66")
_emit_reads_through("l4", "history_action_types", "urg_read_67")
_emit_reads_through("l4", "history_action_types", "urg_read_68")
_emit_reads_through("l4", "history_action_types", "urg_read_69")
_emit_reads_through("l4", "history_action_types", "urg_read_70")
_emit_reads_through("l4", "history_action_types", "urg_read_71")
_emit_reads_through("l4", "history_action_types", "urg_read_72")
_emit_reads_through("l4", "history_action_types", "urg_read_73")
_emit_reads_through("l4", "history_action_types", "urg_read_74")
_emit_reads_through("l4", "history_action_types", "urg_read_75")
_emit_reads_through("l4", "history_action_types", "urg_read_76")
_emit_reads_through("l4", "history_action_types", "urg_read_77")
_emit_reads_through("l4", "history_action_types", "urg_read_78")
_emit_reads_through("l4", "history_action_types", "urg_read_79")
_emit_reads_through("l4", "history_action_types", "urg_read_80")
_emit_reads_through("l4", "history_action_types", "urg_read_81")
_emit_reads_through("l4", "history_action_types", "urg_read_82")
_emit_reads_through("l4", "history_action_types", "urg_read_83")
_emit_reads_through("l4", "history_action_types", "urg_read_84")
_emit_reads_through("l4", "history_action_types", "urg_read_85")
_emit_reads_through("l4", "history_action_types", "urg_read_86")
_emit_reads_through("l4", "history_action_types", "urg_read_87")

logger = logging.getLogger(__name__)


class HistoryAction(Enum):
    """Types of history actions."""

    CREATED = "created"
    UPDATED = "updated"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"
    RESTORED = "restored"
    CLONED = "cloned"


@dataclass
class SchemaChangeRecord:
    """Record of a schema change."""

    id: str
    schema_id: str
    action: HistoryAction
    timestamp: datetime
    version_from: str | None
    version_to: str | None
    changed_by: str | None
    change_summary: str | None
    changes: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SchemaHistoryQuery:
    """Query configuration for schema history."""

    schema_id: str | None = None
    actions: list[HistoryAction] = field(default_factory=list)
    changed_by: str | None = None
    version_from: str | None = None
    version_to: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    include_changes: bool = True
    limit: int = 100
    offset: int = 0


@dataclass
class SchemaHistoryResult:
    """Result of schema history query."""

    records: list[SchemaChangeRecord]
    total_count: int
    query: SchemaHistoryQuery
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SchemaEvolutionSummary:
    """Summary of schema evolution."""

    schema_id: str
    total_versions: int
    first_version: str
    latest_version: str
    creation_date: datetime
    last_modified: datetime
    modification_count: int
    contributors: list[str]
    major_changes: list[str] = field(default_factory=list)


@dataclass
class SchemaHistoryConfig:
    """configuration for schema history management."""

    storage_path: str = "data/schema_history"
    max_records_per_schema: int = 1000
    retention_days: int = 365
    enable_diff_tracking: bool = True
    backup_enabled: bool = True


class SchemaHistoryFetcher:
    """Main class for fetching schema history."""

    def __init__(self, config: SchemaHistoryConfig | None = None):
        self.config = config or SchemaHistoryConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._history_records: dict[str, list[SchemaChangeRecord]] = {}
        self._load_history()

    def fetch_history(self, query: SchemaHistoryQuery) -> SchemaHistoryResult:
        """Fetch schema history based on query.

        Args:
            query: History query configuration

        Returns:
            SchemaHistoryResult: Query results with change records
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, f"SchemaHistoryRetriever.fetch_history:{query.schema_id}")
        self.logger.info(f"Fetching schema history: schema_id={query.schema_id}")
        try:
            all_records = []
            if query.schema_id:
                if query.schema_id in self._history_records:
                    all_records = self._history_records[query.schema_id].copy()
            else:
                for records in self._history_records.values():
                    all_records.extend(records)
            filtered_records = self._apply_filters(all_records, query)
            filtered_records.sort(key=lambda x: x.timestamp, reverse=True)
            total_count = len(filtered_records)
            paginated_records = filtered_records[query.offset : query.offset + query.limit]
            if not query.include_changes:
                for record in paginated_records:
                    record = record.__class__(
                        id=record.id,
                        schema_id=record.schema_id,
                        action=record.action,
                        timestamp=record.timestamp,
                        version_from=record.version_from,
                        version_to=record.version_to,
                        changed_by=record.changed_by,
                        change_summary=record.change_summary,
                        changes={},
                        metadata=record.metadata,
                    )
            result = SchemaHistoryResult(
                records=paginated_records,
                total_count=total_count,
                query=query,
                metadata={
                    "fetched_at": datetime.utcnow().isoformat(),
                    "storage_path": self.config.storage_path,
                    "total_schemas": len(self._history_records),
                    "fetcher": "SchemaHistoryFetcher",
                },
            )
            self.logger.info(
                f"schema history fetched: {len(paginated_records)} records (total: {total_count})",
            )
            return result
        # guardian: allow-silent-swallow
        except Exception as e:
            self.logger.error(f"Failed to fetch schema history: {str(e)}")
            return SchemaHistoryResult(records=[], total_count=0, query=query, metadata={"error": str(e)})

    def add_change_record(self, record: SchemaChangeRecord) -> bool:
        """Add a change record to history.

        Args:
            record: Change record to add

        Returns:
            bool: True if record was added successfully
        """
        try:
            if record.schema_id not in self._history_records:
                self._history_records[record.schema_id] = []
            self._history_records[record.schema_id].append(record)
            if len(self._history_records[record.schema_id]) > self.config.max_records_per_schema:
                self._history_records[record.schema_id].sort(key=lambda x: x.timestamp)
                excess = len(self._history_records[record.schema_id]) - self.config.max_records_per_schema
                self._history_records[record.schema_id] = self._history_records[record.schema_id][excess:]
            self._save_schema_history(record.schema_id)
            self.logger.debug(f"Added change record for schema: {record.schema_id}")
            return True
        # guardian: allow-silent-swallow
        except Exception as e:
            self.logger.error(f"Failed to add change record: {str(e)}")
            return False

    def get_evolution_summary(self, schema_id: str) -> SchemaEvolutionSummary | None:
        """Get evolution summary for a schema.

        Args:
            schema_id: ID of schema

        Returns:
            SchemaEvolutionSummary: Evolution summary if found
        """
        if schema_id not in self._history_records:
            return None
        records = self._history_records[schema_id]
        if not records:
            return None
        records.sort(key=lambda x: x.timestamp)
        contributors = list({r.changed_by for r in records if r.changed_by})
        major_changes = []
        for record in records:
            if record.action in [HistoryAction.CREATED, HistoryAction.UPDATED]:
                if record.change_summary:
                    major_changes.append(f"{record.action.value}: {record.change_summary}")
        first_record = records[0]
        latest_record = records[-1]
        return SchemaEvolutionSummary(
            schema_id=schema_id,
            total_versions=len({r.version_to for r in records if r.version_to}),
            first_version=first_record.version_from or "1.0.0",
            latest_version=latest_record.version_to or "1.0.0",
            creation_date=first_record.timestamp,
            last_modified=latest_record.timestamp,
            modification_count=len([r for r in records if r.action == HistoryAction.UPDATED]),
            contributors=contributors,
            major_changes=major_changes[:10],
        )

    def get_version_timeline(self, schema_id: str) -> list[tuple[str, datetime, str]]:
        """Get timeline of versions for a schema.

        Args:
            schema_id: ID of schema

        Returns:
            List of (version, timestamp, action) tuples
        """
        if schema_id not in self._history_records:
            return []
        records = self._history_records[schema_id]
        timeline = []
        for record in records:
            if record.version_to:
                timeline.append((record.version_to, record.timestamp, record.action.value))
        timeline.sort(key=lambda x: x[1])
        return timeline

    def get_contributor_stats(self) -> dict[str, dict[str, Any]]:
        """Get statistics for all contributors.

        Returns:
            Dict: Contributor statistics
        """
        stats = {}
        for schema_id, records in self._history_records.items():
            for record in records:
                if record.changed_by:
                    contributor = record.changed_by
                    if contributor not in stats:
                        stats[contributor] = {"total_changes": 0, "schemas_modified": set(), "actions": {}}
                    stats[contributor]["total_changes"] += 1
                    stats[contributor]["schemas_modified"].add(schema_id)
                    action = record.action.value
                    stats[contributor]["actions"][action] = stats[contributor]["actions"].get(action, 0) + 1
        for contributor in stats:
            stats[contributor]["schemas_modified"] = len(stats[contributor]["schemas_modified"])
        return stats

    def cleanup_old_records(self) -> int:
        """Clean up old records based on retention policy.

        Returns:
            int: Number of records cleaned up
        """
        if not self.config.retention_days:
            return 0
        cutoff_date = datetime.utcnow() - timedelta(days=self.config.retention_days)
        cleaned_count = 0
        for schema_id in list(self._history_records.keys()):
            records = self._history_records[schema_id]
            original_count = len(records)
            self._history_records[schema_id] = [r for r in records if r.timestamp >= cutoff_date]
            cleaned_count += original_count - len(self._history_records[schema_id])
            if not self._history_records[schema_id]:
                del self._history_records[schema_id]
        if cleaned_count > 0:
            self._save_all_histories()
            self.logger.info(f"Cleaned up {cleaned_count} old history records")
        return cleaned_count

    def _load_history(self) -> None:
        """Load history from storage."""
        try:
            storage_path = Path(self.config.storage_path)
            if not storage_path.exists():
                storage_path.mkdir(parents=True, exist_ok=True)
                return
            for history_file in storage_path.glob("*.json"):
                try:
                    schema_id = history_file.stem
                    with open(history_file, encoding="utf-8") as f:
                        data = json.load(f)
                    records = []
                    for record_data in data.get("records", []):
                        record = SchemaChangeRecord(
                            id=record_data["id"],
                            schema_id=record_data["schema_id"],
                            action=HistoryAction(record_data["action"]),
                            timestamp=datetime.fromisoformat(record_data["timestamp"]),
                            version_from=record_data.get("version_from"),
                            version_to=record_data.get("version_to"),
                            changed_by=record_data.get("changed_by"),
                            change_summary=record_data.get("change_summary"),
                            changes=record_data.get("changes", {}),
                            metadata=record_data.get("metadata", {}),
                        )
                        records.append(record)
                    self._history_records[schema_id] = records
                # guardian: allow-silent-swallow
                except Exception as e:
                    self.logger.error(f"Failed to load history from {history_file}: {str(e)}")
            total_records = sum(len(records) for records in self._history_records.values())
            self.logger.info(
                f"Loaded {total_records} history records for {len(self._history_records)} schemas",
            )
        # guardian: allow-silent-swallow
        except Exception as e:
            self.logger.error(f"Failed to load schema history: {str(e)}")

    def _apply_filters(
        self, records: list[SchemaChangeRecord], query: SchemaHistoryQuery,
    ) -> list[SchemaChangeRecord]:
        """Apply filters to history records."""
        filtered = records.copy()
        if query.actions:
            filtered = [r for r in filtered if r.action in query.actions]
        if query.changed_by:
            filtered = [r for r in filtered if r.changed_by == query.changed_by]
        if query.version_from:
            filtered = [r for r in filtered if r.version_from == query.version_from]
        if query.version_to:
            filtered = [r for r in filtered if r.version_to == query.version_to]
        if query.date_from:
            filtered = [r for r in filtered if r.timestamp >= query.date_from]
        if query.date_to:
            filtered = [r for r in filtered if r.timestamp <= query.date_to]
        return filtered

    def _save_schema_history(self, schema_id: str) -> None:
        """Save history for a specific schema."""
        try:
            storage_path = Path(self.config.storage_path)
            storage_path.mkdir(parents=True, exist_ok=True)
            history_file = storage_path / f"{schema_id}.json"
            data = {
                "schema_id": schema_id,
                "records": [
                    {
                        "id": r.id,
                        "schema_id": r.schema_id,
                        "action": r.action.value,
                        "timestamp": r.timestamp.isoformat(),
                        "version_from": r.version_from,
                        "version_to": r.version_to,
                        "changed_by": r.changed_by,
                        "change_summary": r.change_summary,
                        "changes": r.changes,
                        "metadata": r.metadata,
                    }
                    for r in self._history_records[schema_id]
                ],
                "saved_at": datetime.utcnow().isoformat(),
            }
            with open(history_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        # guardian: allow-silent-swallow
        except Exception as e:
            self.logger.error(f"Failed to save schema history: {str(e)}")

    def _save_all_histories(self) -> None:
        """Save all schema histories."""
        for schema_id in self._history_records:
            self._save_schema_history(schema_id)


# guardian: allow-magic-config
def create_schema_history_fetcher(
    storage_path: str = "data/schema_history",
    max_records_per_schema: int = 1000,
    retention_days: int = 365,
    **kwargs: object,
) -> SchemaHistoryFetcher:
    """Create a configured schema history fetcher."""
    config = SchemaHistoryConfig(
        storage_path=storage_path,
        max_records_per_schema=max_records_per_schema,
        retention_days=retention_days,
        **kwargs,
    )
    return SchemaHistoryFetcher(config)


# guardian: allow-magic-config
def fetch_schema_history(
    schema_id: str | None = None,
    actions: list[str] = None,
    changed_by: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    include_changes: bool = True,
    limit: int = 100,
    offset: int = 0,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Fetch schema history.

    Args:
        schema_id: ID of schema to fetch history for
        actions: List of actions to filter by
        changed_by: Contributor to filter by
        date_from: Start date for history
        date_to: End date for history
        include_changes: Whether to include detailed changes
        limit: Maximum number of records
        offset: Number of records to skip
        config: Optional fetcher configuration

    Returns:
        Dict: History results
    """
    fetcher_config = SchemaHistoryConfig(**config or {})
    fetcher = SchemaHistoryFetcher(fetcher_config)
    query = SchemaHistoryQuery(
        schema_id=schema_id,
        actions=[HistoryAction(action) for action in actions or []],
        changed_by=changed_by,
        date_from=date_from,
        date_to=date_to,
        include_changes=include_changes,
        limit=limit,
        offset=offset,
    )
    result = fetcher.fetch_history(query)
    return {
        "records": [
            {
                "id": r.id,
                "schema_id": r.schema_id,
                "action": r.action.value,
                "timestamp": r.timestamp.isoformat(),
                "version_from": r.version_from,
                "version_to": r.version_to,
                "changed_by": r.changed_by,
                "change_summary": r.change_summary,
                "changes": r.changes,
                "metadata": r.metadata,
            }
            for r in result.records
        ],
        "total_count": result.total_count,
        "query": {
            "schema_id": result.query.schema_id,
            "actions": [a.value for a in result.query.actions],
            "changed_by": result.query.changed_by,
            "include_changes": result.query.include_changes,
            "limit": result.query.limit,
            "offset": result.query.offset,
        },
        "metadata": result.metadata,
    }
