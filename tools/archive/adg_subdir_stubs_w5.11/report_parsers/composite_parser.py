"""Composite parser that aggregates all ADG report parsers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.adg.repair.types import FixCategory

from .base_parser import BaseReportParser
from .boundary_parser import BoundaryReportParser
from .closure_parser import ClosureReportParser
from .determinism_parser import DeterminismReportParser
from .edge_parser import EdgeReportParser
from .layer_parser import LayerReportParser
from .mutation_parser import MutationReportParser
from .provenance_parser import ProvenanceReportParser


class CompositeReportParser(BaseReportParser):
    """Composite parser that extracts deficiencies from all report types.

    Aggregates all individual report parsers to provide a unified interface
    for deficiency extraction across all ADG reports.
    """

    report_name = "Composite ADG Report"
    report_filename_pattern = "*_report_*.json"

    def __init__(self, adg_dir: Path, timestamp: str):
        """Initialize the composite parser.

        Args:
            adg_dir: Directory containing ADG artifacts
            timestamp: ADG timestamp (MMDDYYYY_HHMM format)
        """
        super().__init__(adg_dir, timestamp)

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

    def _get_report_path(self) -> Path | None:
        """Composite parser doesn't have a single report path."""
        return None

    def is_available(self) -> bool:
        """Check if any reports are available."""
        return any(p.is_available() for p in self.parsers)

    def get_summary(self) -> dict[str, Any]:
        """Get summary from all available parsers.

        Returns:
            Dictionary with composite summary
        """
        available = sum(1 for p in self.parsers if p.is_available())

        summaries = {}
        for parser in self.parsers:
            if parser.is_available():
                summaries[parser.report_name] = parser.get_summary()

        return {
            "report_name": self.report_name,
            "available": available > 0,
            "total_reports": len(self.parsers),
            "available_reports": available,
            "individual_summaries": summaries,
        }

    def extract_deficiencies(self) -> list[dict[str, Any]]:
        """Extract deficiencies from all available reports.

        Returns:
            Combined list of all deficiencies
        """
        all_deficiencies: list[dict[str, Any]] = []

        for parser in self.parsers:
            if parser.is_available():
                try:
                    deficiencies = parser.extract_deficiencies()
                    all_deficiencies.extend(deficiencies)
                except Exception as e:
                    # Log error but continue with other parsers
                    print(f"[CompositeParser] Error from {parser.report_name}: {e}")

        return all_deficiencies

    def extract_all_deficiencies(self) -> list[dict[str, Any]]:
        """Alias for extract_deficiencies()."""
        return self.extract_deficiencies()

    def get_deficiency_counts_by_category(self) -> dict[str, int]:
        """Count deficiencies by category.

        Returns:
            Dictionary with counts for each FixCategory
        """
        deficiencies = self.extract_deficiencies()

        counts = {
            "auto_fix": 0,
            "suggest_fix": 0,
            "block_fix": 0,
        }

        for d in deficiencies:
            cat = d.get("category", FixCategory.SUGGEST_FIX)
            if hasattr(cat, "value"):
                cat = cat.value

            if cat == "auto_fix" or str(cat).endswith("AUTO_FIX"):
                counts["auto_fix"] += 1
            elif cat == "suggest_fix" or str(cat).endswith("SUGGEST_FIX"):
                counts["suggest_fix"] += 1
            elif cat == "block_fix" or str(cat).endswith("BLOCK_FIX"):
                counts["block_fix"] += 1

        return counts
