from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "csv_document_loader_config", "p0_governance")
_emit_reads_policy_state("p0", "csv_document_loader_config", "policy_binding")
_emit_snapshots_state("p0", "csv_document_loader_config", "state_snapshot")
emit_replay_key("p0", "csv_document_loader_config")
emit_determinism_digest("p0", "csv_document_loader_config")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
