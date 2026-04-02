"""ADG Static Analyzer — Static code analysis for ADG extraction."""

from __future__ import annotations

from pathlib import Path
from typing import Any


class StaticAnalyzer:
    """Analyzes Python source code statically."""

    def analyze_file(self, file_path: Path) -> dict[str, Any]:
        """Analyze a single file."""
        return {"file": str(file_path), "nodes": [], "edges": []}

    def analyze_directory(self, dir_path: Path) -> list[dict[str, Any]]:
        """Analyze all Python files in directory."""
        results = []
        for py_file in dir_path.rglob("*.py"):
            results.append(self.analyze_file(py_file))
        return results
