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
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
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
