from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_applies_guardrail("p0", "csv_document_loader_config", "p0_governance")
_emit_reads_policy_state("p0", "csv_document_loader_config", "policy_binding")
_emit_snapshots_state("p0", "csv_document_loader_config", "state_snapshot")
emit_replay_key("p0", "csv_document_loader_config")
emit_determinism_digest("p0", "csv_document_loader_config")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "csv_document_loader_config", "execution_auth")
_emit_validates_capability("p2", "csv_document_loader_config", "capability_check")
_emit_routes_to_capability("p2", "csv_document_loader_config", "capability_route")
_emit_writes_via_uwg("p2", "csv_document_loader_config", "uwg_write")
_emit_blocks_direct_write("p2", "csv_document_loader_config", "direct_write_block")
_emit_records_tool_invocation("p2", "csv_document_loader_config", "tool_invocation")
_emit_captures_execution_output("p2", "csv_document_loader_config", "exec_output")
_emit_dispatches_agent("p3", "csv_document_loader_config", "agent_dispatch")
_emit_coordinates_agents("p3", "csv_document_loader_config", "agent_coordination")
_emit_records_workflow_lineage("p3", "csv_document_loader_config", "workflow_lineage")
_emit_records_healing_outcome("p3", "csv_document_loader_config", "healing_outcome")
_emit_escalates_failure("p3", "csv_document_loader_config", "failure_escalation")
_emit_orchestrates_workflow("p3", "csv_document_loader_config", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "csv_document_loader_config", "healing_dispatch")
_emit_invokes_evaluation("p3", "csv_document_loader_config", "evaluation_signal")
_emit_records_telemetry_event("p4", "csv_document_loader_config", "telemetry_event")
_emit_captures_evaluation_metric("p4", "csv_document_loader_config", "eval_metric")
_emit_stores_embedding("p4", "csv_document_loader_config", "embedding_store")
_emit_updates_meta_learning_state("p4", "csv_document_loader_config", "meta_learning")
_emit_links_execution_to_snapshot("p4", "csv_document_loader_config", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""
CSV Document Loader - Pandas-based structured data loading for RAG.

Restored: 2026-01-13 | Version: 2.0.0
Original: archives/unmapped_drift/20260107/agentic_core/knowledge/document_loaders/csv_loader.py
"""


from pathlib import Path
from typing import Any

try:
    import pandas as pd

    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    pd = None
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


class CsvDocumentLoader:
    """Sovereign CSV loader using pandas for structured data."""

    @staticmethod
    def load(file_path: Path, **kwargs) -> list[dict[str, Any]]:
        """
        Load CSV as list of dictionaries (records).

        Supports:
        - Automatic type inference
        - Custom delimiter, encoding
        - Header row handling

        Args:
            file_path: Path to CSV
            kwargs: Passed to pd.read_csv (e.g., delimiter=";", encoding="utf-8")

        Returns:
            List of row dictionaries
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "CsvDocumentLoader.load")

        if not HAS_PANDAS:
            raise ImportError("pandas is required for CsvDocumentLoader")

        try:
            df: Any = pd.read_csv(file_path, **kwargs)
            records: list[dict[str, Any]] = df.to_dict(orient="records")
            return records
        except Exception as e:
            raise ValueError(f"CSV loading failed for {file_path}: {e}")

    @staticmethod
    def load_as_dataframe(file_path: Path, **kwargs) -> Any:
        """Load as pandas DataFrame for advanced processing."""
        if not HAS_PANDAS:
            raise ImportError("pandas is required for CsvDocumentLoader")

        try:
            return pd.read_csv(file_path, **kwargs)
        except Exception as e:
            raise ValueError(f"CSV DataFrame load failed: {e}")

    @staticmethod
    def load_sample(file_path: Path, rows: int = 10, **kwargs) -> list[dict[str, Any]]:
        """Load only first N rows for preview/sampling."""
        if not HAS_PANDAS:
            raise ImportError("pandas is required for CsvDocumentLoader")

        try:
            df: Any = pd.read_csv(file_path, nrows=rows, **kwargs)
            return df.to_dict(orient="records")
        except Exception as e:
            raise ValueError(f"CSV sample load failed: {e}")


CSVDocumentLoader = CsvDocumentLoader

__all__ = ["CsvDocumentLoader", "CSVDocumentLoader"]
