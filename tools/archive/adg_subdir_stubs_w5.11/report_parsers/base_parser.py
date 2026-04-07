"""Base class for ADG report parsers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class BaseReportParser(ABC):
    """Abstract base class for ADG report parsers.

    All report parsers must inherit from this class and implement
    the required abstract methods.

    Attributes:
        report_name: Human-readable report name
        report_filename_pattern: Pattern to match report filenames
    """

    report_name: str = "Base Report"
    report_filename_pattern: str = "*_report_*.json"

    def __init__(self, adg_dir: Path, timestamp: str):
        """Initialize the parser.

        Args:
            adg_dir: Directory containing ADG artifacts
            timestamp: ADG timestamp (MMDDYYYY_HHMM format)
        """
        self.adg_dir = Path(adg_dir)
        self.timestamp = timestamp
        self.report_path = self._get_report_path()
        self.report_data: dict[str, Any] | None = None

    def _get_report_path(self) -> Path | None:
        """Get the path to the report file.

        Returns:
            Path to report file, or None if not determinable
        """
        return None

    def load(self) -> dict[str, Any] | None:
        """Load and parse the report file.

        Returns:
            Parsed report data, or None if file doesn't exist or is invalid
        """
        import json

        if self.report_path is None:
            return None

        if not self.report_path.exists():
            return None

        try:
            with open(self.report_path, encoding="utf-8") as f:
                self.report_data = json.load(f)
            return self.report_data
        except (json.JSONDecodeError, OSError, UnicodeDecodeError) as e:
            print(f"[{self.report_name}] Failed to load report: {e}")
            return None

    @abstractmethod
    def extract_deficiencies(self) -> list[dict[str, Any]]:
        """Extract deficiencies from the loaded report.

        Returns:
            List of deficiency dictionaries with standardized fields:
            - id: Unique deficiency ID
            - category: FixCategory value
            - file_path: Affected file path
            - line_no: Line number (1-indexed) or None
            - issue_type: Machine-readable issue type
            - description: Human-readable description
            - confidence: Confidence score 0.0-1.0
            - metadata: Additional context
        """
        raise NotImplementedError

    def is_available(self) -> bool:
        """Check if the report is available for parsing.

        Returns:
            True if report file exists and can be loaded
        """
        if self.report_path is None:
            return False
        return self.report_path.exists()

    def get_summary(self) -> dict[str, Any]:
        """Get a summary of the report.

        Returns:
            Dictionary with report summary information
        """
        if self.report_data is None:
            self.load()

        if self.report_data is None:
            return {
                "report_name": self.report_name,
                "available": False,
                "error": "Report not loaded",
            }

        return {
            "report_name": self.report_name,
            "available": True,
            "timestamp": self.report_data.get("timestamp", self.timestamp),
            "schema_version": self.report_data.get("schema_version", "unknown"),
        }
