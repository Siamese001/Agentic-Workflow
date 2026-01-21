"""
DashboardRenderer - Renders dashboard HTML from data.

Stub module for backwards compatibility.
"""
from typing import Dict, Any, Optional
from pathlib import Path


class DashboardRenderer:
    """Renders dashboard HTML from generated data."""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()

    def render(self, data: Dict[str, Any], output_path: Optional[Path] = None) -> str:
        """Render dashboard HTML from data."""
        return "<html><body>Dashboard</body></html>"

    def update_html(self, html_path: Path, data: Dict[str, Any]) -> bool:
        """Update existing HTML with new data."""
        return True


__all__ = ['DashboardRenderer']
