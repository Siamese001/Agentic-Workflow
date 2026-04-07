"""
Scorecard Renderer — Renders evaluation scorecard as CSV/Markdown.

SVP Standards:
- Deterministic output
- Multiple format support
- Full provenance
"""

from __future__ import annotations

import csv
import io
import logging
from typing import Any

from apps_eval.types import ScorecardRow

_log = logging.getLogger(__name__)


class ScorecardRenderer:
    """Renderer for evaluation scorecards."""

    def render_csv(self, rows: list[ScorecardRow]) -> str:
        """Render scorecard as CSV."""
        if not rows:
            return "dimension_id,display_name,score,weight,weighted_score,verdict\n"

        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            "dimension_id", "display_name", "score", "weight",
            "weighted_score", "verdict",
        ])

        # Rows
        for row in rows:
            writer.writerow([
                row.dimension_id,
                row.display_name,
                f"{row.score:.4f}",
                f"{row.weight:.2f}",
                f"{row.weighted_score:.4f}",
                row.verdict,
            ])

        return output.getvalue()

    def render_markdown(self, rows: list[ScorecardRow]) -> str:
        """Render scorecard as Markdown table."""
        if not rows:
            return "No scorecard data available."

        lines = [
            "# Evaluation Scorecard",
            "",
            "| Dimension | Score | Weight | Weighted | Verdict |",
            "|-----------|-------|--------|----------|---------|",
        ]

        for row in rows:
            lines.append(
                f"| {row.display_name} | {row.score:.2%} | {row.weight:.2f} | "
                f"{row.weighted_score:.4f} | {row.verdict} |",
            )

        lines.append("")
        return "\n".join(lines)

    def render_summary(self, rows: list[ScorecardRow]) -> dict[str, Any]:
        """Render summary statistics."""
        if not rows:
            return {"total_dimensions": 0, "passed": 0, "failed": 0}

        passed = sum(1 for r in rows if r.verdict == "PASS")
        failed = sum(1 for r in rows if r.verdict == "FAIL")
        warnings = sum(1 for r in rows if r.verdict == "WARN")

        return {
            "total_dimensions": len(rows),
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "average_score": sum(r.score for r in rows) / len(rows),
        }
