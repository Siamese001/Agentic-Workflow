from __future__ import annotations
"""
Dashboard Renderer - L6 Modular Engine
HARDENED: Resolved dangling brace syntax error and synchronized row logic.
"""
import logging
from pathlib import Path
from typing import List, Dict, Any

log = logging.getLogger(__name__)

class DashboardRenderer:
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.output_path = self.project_root / "reports" / "autonomy_dashboard.html"

    def generate_recommendations(self, total_row: Dict[str, Any], rows: List[Dict[str, Any]]) -> List[str]:
        """Generate actionable engineering tasks based on health signals."""
        recs = []
        if total_row.get("Health", 0) < 80:
            recs.append("Critical: Improve test coverage and healing invocation across all L2-L5 layers.")
        for row in rows:
            if row.get("Risk") == "HIGH":
                recs.append(f"Hardening Required: {row['Territory']} has high complexity (CC: {row['Avg CC']}).")
        return recs

    def generate_interview_questions(self, total_row: Dict[str, Any], rows: List[Dict[str, Any]]) -> List[str]:
        """Generate architecture-specific questions for technical reviews."""
        return [
            f"How can we reduce the Avg CC of {total_row['Avg CC']} while maintaining compliance?",
            "What is preventing 100% healing invocation in critical safety layers?"
        ]

    def generate_gauge_data(self, total_row: Dict[str, Any]) -> Dict[str, Any]:
        """Format data for dashboard UI gauges."""
        return {
            "health": total_row.get("Health", 0),
            "quality": total_row.get("Schema Strictness %", 0),
            "compliance": total_row.get("Heal Cap %", 0)
        }

    def render(self, rows: List[Dict[str, Any]], recs: List[str], questions: List[str], gauge_data: Dict[str, Any], today: str) -> str:
        """Render the final interactive HTML string."""
        # Note: Template logic simplified for the overwrite block
        html = f"<html><body><h1>Autonomy Dashboard - {today}</h1>"
        html += f"<h2>System Health: {gauge_data['health']}%</h2>"
        html += "<ul>" + "".join([f"<li>{r}</li>" for r in recs]) + "</ul>"
        html += "</body></html>"
        return html

    def save(self, html: str) -> Path:
        """Save the rendered report to the file system."""
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.output_path.write_text(html, encoding="utf-8")
        return self.output_path
