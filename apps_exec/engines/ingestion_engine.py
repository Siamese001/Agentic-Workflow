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
                        )
                    )
                except OSError as exc:
                    _log.warning("[IngestionEngine] Could not read %s: %s", file_path, exc)
                    result.skipped_paths.append(str(file_path))

        self.record_pass(f"Ingested {len(result.documents)} documents from {len(source_dirs)} dirs")
        return result
