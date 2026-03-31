"""Composite parser that aggregates all report parsers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .base_parser import BaseReportParser
from .boundary_parser import BoundaryReportParser
from .closure_parser import ClosureReportParser
from .determinism_parser import DeterminismReportParser
from .edge_parser import EdgeReportParser
from .layer_parser import LayerReportParser
from .mutation_parser import MutationReportParser
from .provenance_parser import ProvenanceReportParser


class CompositeReportParser:
    """Composite parser that loads and parses all ADG reports.

    This class provides a unified interface for extracting deficiencies
    from all available ADG report types.

    Usage:
        parser = CompositeReportParser(
            adg_dir=Path("artifacts/adg"),
            timestamp="03122026_0512"
        )
        all_deficiencies = parser.extract_all_deficiencies()
    """

    def __init__(self, adg_dir: Path, timestamp: str):
        """Initialize the composite parser.

        Args:
            adg_dir: Directory containing ADG artifacts
            timestamp: ADG timestamp (MMDDYYYY_HHMM format)
        """
        self.adg_dir = Path(adg_dir)
        self.timestamp = timestamp

        # Initialize all individual parsers
        self.parsers: list[BaseReportParser] = [
            ClosureReportParser(adg_dir, timestamp),
            LayerReportParser(adg_dir, timestamp),
            EdgeReportParser(adg_dir, timestamp),
            ProvenanceReportParser(adg_dir, timestamp),
            DeterminismReportParser(adg_dir, timestamp),
            BoundaryReportParser(adg_dir, timestamp),
            MutationReportParser(adg_dir, timestamp),
        ]

    def load_all(self) -> dict[str, dict[str, Any] | None]:
        """Load all available reports.

        Returns:
            Dictionary mapping report names to loaded data
        """
        results = {}

        for parser in self.parsers:
            data = parser.load()
            if data is not None:
                results[parser.report_name] = data

        return results

    def extract_all_deficiencies(self) -> list[dict[str, Any]]:
        """Extract deficiencies from all available reports.

        Returns:
            Combined list of all deficiencies from all reports
        """
        all_deficiencies = []

        for parser in self.parsers:
            try:
                deficiencies = parser.extract_deficiencies()
                all_deficiencies.extend(deficiencies)
            except Exception as e:
                print(f"[{parser.report_name}] Failed to extract deficiencies: {e}")

        return all_deficiencies

    def get_summary(self) -> dict[str, Any]:
        """Get a summary of all report parsing.

        Returns:
            Dictionary with summary information
        """
        summaries = {}
        available_count = 0

        for parser in self.parsers:
            summary = parser.get_summary()
            summaries[parser.report_name] = summary
            if summary.get("available", False):
                available_count += 1

        return {
            "timestamp": self.timestamp,
            "adg_dir": str(self.adg_dir),
            "total_reports": len(self.parsers),
            "available_reports": available_count,
            "report_summaries": summaries,
        }

    def get_deficiency_counts_by_category(self) -> dict[str, int]:
        """Get counts of deficiencies by category.

        Returns:
            Dictionary mapping category to count
        """
        deficiencies = self.extract_all_deficiencies()

        counts = {
            "auto_fix": 0,
            "suggest_fix": 0,
            "block_fix": 0,
        }

        for deficiency in deficiencies:
            category = deficiency.get("category", "suggest_fix")
            if category in counts:
                counts[category] += 1

        return counts
