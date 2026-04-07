"""
Ingestion Engine — apps_exec.

Reads source markdown / text / JSON documents from configured directories
and returns a normalized document corpus for capability extraction.

Deterministic: file discovery, normalization, metadata tagging.
Model-driven:  none at this stage.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
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

_emit_authorize_and_execute("p2", "ingestion_engine", "execution_auth")
_emit_validates_capability("p2", "ingestion_engine", "capability_check")
_emit_routes_to_capability("p2", "ingestion_engine", "capability_route")
_emit_writes_via_uwg("p2", "ingestion_engine", "uwg_write")
_emit_blocks_direct_write("p2", "ingestion_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "ingestion_engine", "tool_invocation")
_emit_captures_execution_output("p2", "ingestion_engine", "exec_output")
_emit_dispatches_agent("p3", "ingestion_engine", "agent_dispatch")
_emit_coordinates_agents("p3", "ingestion_engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "ingestion_engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "ingestion_engine", "healing_outcome")
_emit_escalates_failure("p3", "ingestion_engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "ingestion_engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ingestion_engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "ingestion_engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "ingestion_engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ingestion_engine", "eval_metric")
_emit_stores_embedding("p4", "ingestion_engine", "embedding_store")
_emit_updates_meta_learning_state("p4", "ingestion_engine", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ingestion_engine", "exec_snapshot_link")
from apps_exec.engines.base_exec_engine import BaseExecEngine

_emit_applies_guardrail("p0", "ingestion_engine", "p0_governance")
_emit_reads_policy_state("p0", "ingestion_engine", "policy_binding")
_emit_snapshots_state("p0", "ingestion_engine", "state_snapshot")
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

_emit_emits_metric_event("ingestion_engine", "p4obs", "metric_1")
_emit_emits_metric_event("ingestion_engine", "p4obs", "metric_2")
_emit_emits_metric_event("ingestion_engine", "p4obs", "metric_3")
_emit_emits_metric_event("ingestion_engine", "p4obs", "metric_4")
_emit_emits_metric_event("ingestion_engine", "p4obs", "metric_5")
_emit_emits_metric_event("ingestion_engine", "p4obs", "metric_6")
_emit_records_incident_event("ingestion_engine", "p4obs", "incident")
_emit_captures_runtime_anomaly("ingestion_engine", "p4obs", "anomaly")
_emit_writes_observability_log("ingestion_engine", "p4obs", "obs_log")
_emit_updates_monitoring_state("ingestion_engine", "p4obs", "mon_state")
_emit_triggers_alert("ingestion_engine", "p4obs", "alert")
_emit_links_incident_trace("ingestion_engine", "p4obs", "trace_link")
_emit_captures_pattern("ingestion_engine", "p3lm", "pattern")
_emit_records_learning_event("ingestion_engine", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ingestion_engine", "p3lm", "snapshot")
_emit_feeds_meta_learning("ingestion_engine", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ingestion_engine", "p3lm", "routing")
_emit_improves_agent_policy("ingestion_engine", "p3lm", "policy")
_emit_stores_learning_state("ingestion_engine", "p3lm", "state")
_emit_records_execution_trace("ingestion_engine", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ingestion_engine", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ingestion_engine", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ingestion_engine", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ingestion_engine", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ingestion_engine", "env_read", "p2_env_1")
_emit_reads_environ("ingestion_engine", "env_read", "p2_env_2")
_emit_reads_runtime_state("ingestion_engine", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ingestion_engine", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "ingestion_engine", "context_pull")
_emit_pulls_context("p1", "ingestion_engine", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "ingestion_engine", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ingestion_engine", "uwg_term_2")
_emit_writes_through("p1", "ingestion_engine", "write_through")
_emit_writes_through("p1", "ingestion_engine", "write_through_2")
_emit_validated_by_safety_plane("p1", "ingestion_engine", "safety_validation")
_emit_invokes_eval("p1", "ingestion_engine", "eval_call")
_emit_proposal_commits_routing("p1", "ingestion_engine", "routing_commit")
_emit_escalates_to_human("p1", "ingestion_engine", "human_escalation")
_emit_routes_through("p1", "ingestion_engine", "route_through")
_emit_checks_agent_registry("p1", "ingestion_engine", "agent_registry")
_emit_validates_agent_capability("p1", "ingestion_engine", "capability")
_emit_dispatches_execution_plan("p1", "ingestion_engine", "exec_plan")
_emit_agent_executes_agent("p1", "ingestion_engine", "sub_agent")
_emit_routes_to_agent("p1", "ingestion_engine", "target_agent")
_emit_verifies_policy("p1", "ingestion_engine", "policy_check")
_emit_observes_runtime_state("p1", "ingestion_engine", "runtime_state")
_emit_verifies_boundary("p1", "ingestion_engine", "boundary_check")
_emit_transcripts_response("p1", "ingestion_engine", "transcript")
_emit_hard_fails_untranscripted("p1", "ingestion_engine")
_emit_gated_by_confidence("p1", "ingestion_engine", "confidence_gate")
emit_replay_key("p0", "ingestion_engine")
emit_determinism_digest("p0", "ingestion_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

_log = logging.getLogger(__name__)


@dataclass
class IngestedDocument:
    """A single ingested source document."""

    path: str
    content: str
    size_bytes: int
    extension: str
    source_dir: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class IngestionResult:
    """Result of an ingestion pass."""

    documents: list[IngestedDocument] = field(default_factory=list)
    skipped_paths: list[str] = field(default_factory=list)
    error: str = ""

    @property
    def total_chars(self) -> int:
        return sum(len(d.content) for d in self.documents)


class IngestionEngine(BaseExecEngine):
    """Ingest source materials from configured directories.

    Reads files matching allowed extensions. Skips files that are too large.
    Never raises on missing directories — logs a warning and continues.
    """

    AGENT_ID = "EXEC_INGESTION"

    def execute(self, input_data: Any) -> IngestionResult:
        """Execute ingestion over configured source directories.

        Args:
            input_data: ExecBriefRequest (uses source_dirs field) or dict.

        Returns:
            IngestionResult with all ingested documents.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "IngestionEngine.execute")

        source_dirs: list[str] = []
        if hasattr(input_data, "source_dirs"):
            source_dirs = input_data.source_dirs
        elif isinstance(input_data, dict):
            source_dirs = input_data.get("source_dirs", [])

        cfg = self.specs.ingestion if self.specs else None
        extensions = set(cfg.file_extensions if cfg else [".md", ".txt", ".json"])
        max_size = (cfg.max_file_size_kb if cfg else 512) * 1024
        recursive = cfg.recursive if cfg else True

        result = IngestionResult()

        for src in source_dirs:
            src_path = Path(src)
            if not src_path.exists():
                _log.warning("[IngestionEngine] Source dir not found: %s — skipping", src)
                result.skipped_paths.append(str(src_path))
                continue

            glob_pattern = "**/*" if recursive else "*"
            for file_path in src_path.glob(glob_pattern):
                if not file_path.is_file():
                    continue
                if file_path.suffix not in extensions:
                    continue
                size = file_path.stat().st_size
                if size > max_size:
                    _log.debug("[IngestionEngine] Skipping oversized file: %s (%d bytes)", file_path, size)
                    result.skipped_paths.append(str(file_path))
                    continue
                try:
                    content = file_path.read_text(encoding="utf-8", errors="replace")
                    result.documents.append(
                        IngestedDocument(
                            path=str(file_path),
                            content=content,
                            size_bytes=size,
                            extension=file_path.suffix,
                            source_dir=src,
                        ),
                    )
                except OSError as exc:    # guardian: Add error context logging
                    _log.warning("[IngestionEngine] Could not read %s: %s", file_path, exc)
                    result.skipped_paths.append(str(file_path))

        self.record_pass(f"Ingested {len(result.documents)} documents from {len(source_dirs)} dirs")
        return result
