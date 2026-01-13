"""
CSV Document Loader - Pandas-based structured data loading for RAG.

Restored: 2026-01-13 | Version: 2.0.0
Original: archives/unmapped_drift/20260107/agentic_core/knowledge/document_loaders/csv_loader.py
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    pd = None


class CsvDocumentLoader:
    """Sovereign CSV loader using pandas for structured data."""

    @staticmethod
    def load(file_path: Path, **kwargs) -> List[Dict[str, Any]]:
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
        if not HAS_PANDAS:
            raise ImportError("pandas is required for CsvDocumentLoader")
        
        try:
            df: Any = pd.read_csv(file_path, **kwargs)
            records: List[Dict[str, Any]] = df.to_dict(orient='records')
            return records
        except Exception as e:
            raise ValueError(f'CSV loading failed for {file_path}: {e}')

    @staticmethod
    def load_as_dataframe(file_path: Path, **kwargs) -> Any:
        """Load as pandas DataFrame for advanced processing."""
        if not HAS_PANDAS:
            raise ImportError("pandas is required for CsvDocumentLoader")
        
        try:
            return pd.read_csv(file_path, **kwargs)
        except Exception as e:
            raise ValueError(f'CSV DataFrame load failed: {e}')

    @staticmethod
    def load_sample(file_path: Path, rows: int = 10, **kwargs) -> List[Dict[str, Any]]:
        """Load only first N rows for preview/sampling."""
        if not HAS_PANDAS:
            raise ImportError("pandas is required for CsvDocumentLoader")
        
        try:
            df: Any = pd.read_csv(file_path, nrows=rows, **kwargs)
            return df.to_dict(orient='records')
        except Exception as e:
            raise ValueError(f'CSV sample load failed: {e}')
