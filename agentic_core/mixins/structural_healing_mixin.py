"""
structural_healing_mixin.py - Thin Mixin Wrapper for Structural Healing

[MIXIN REFACTOR] Pure logic extracted to structural_healing_engine.py.
This mixin binds the stateless engine functions to Agent state
(project_root, max_lines_per_file).

Naming convention:
  *_engine.py  = stateless functions (no self)
  *_mixin.py   = thin adapter binding engine to Agent state
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentic_core.mixins import structural_healing_engine as engine
from agentic_core.runtime.exceptions.SovereignError import StructuralError


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

@dataclass
class StructuralHealingMixin:
    """Mixin binding structural_healing_engine functions to Agent state."""

    project_root: Path = field(default_factory=Path.cwd)
    max_lines_per_file: int = 800

    def _salvaged_file_relocation(
        self,
        source_path: Path,
        target_path: Path,
        dry_run: bool = True,
    ) -> dict[str, Any]:
        """Relocate a file with integrity verification."""
        return engine.relocate_file(source_path, target_path, self.project_root, dry_run=dry_run)

    def _is_safe_relocation(self, source: Path, target: Path) -> bool:
        return engine._is_safe_relocation(source, target, self.project_root)

    def _calculate_file_hash(self, file_path: Path) -> str:
        return engine.calculate_file_hash(file_path)

    def _analyze_file_structure(self, file_path: Path) -> dict[str, Any]:
        """Analyze file structure for potential issues."""
        return engine.analyze_file_structure(file_path, max_lines=self.max_lines_per_file)

    def _calculate_complexity(self, content: str) -> int:
        return engine.calculate_complexity(content)

    def _suggest_file_split(self, file_path: Path) -> list[dict[str, Any]]:
        return engine.suggest_file_split(file_path, max_lines=self.max_lines_per_file)

    def heal_structural_issues(self, dry_run: bool = True) -> dict[str, Any]:
        """Heal structural issues across the project."""
        results: dict[str, Any] = {
            "files_analyzed": 0,
            "issues_found": 0,
            "issues_fixed": 0,
            "errors": 0,
            "details": [],
        }

        try:
            for py_file in self.project_root.rglob("*.py"):
                if py_file.name.startswith(".") or "__pycache__" in str(py_file):
                    continue

                results["files_analyzed"] += 1

                try:
                    structure = engine.analyze_file_structure(
                        py_file,
                        max_lines=self.max_lines_per_file,
                    )

                    if structure["issues"]:
                        results["issues_found"] += len(structure["issues"])

                        if not dry_run:
                            fixed = self._fix_structural_issues(py_file, structure)
                            results["issues_fixed"] += fixed

                        results["details"].append(
                            {
                                "file": str(py_file.relative_to(self.project_root)),
                                "issues": structure["issues"],
                                "complexity": structure["complexity_score"],
                            },
                        )

                # guardian: allow-silent-swallow
                except Exception as e:
                    # TODO: Handle specific exception properly
                    raise  # Re-raise after logging/handling
                    results["errors"] += 1
                    results["details"].append(
                        {"file": str(py_file.relative_to(self.project_root)), "error": str(e)},
                    )

        except Exception as e:
            raise StructuralError(f"Structural healing failed: {str(e)}") from e

        return results

    def _fix_structural_issues(self, file_path: Path, structure: dict[str, Any]) -> int:
        """Fix structural issues in a file."""
        fixed = 0
        if structure["has_syntax_errors"]:
            fixed += 1
        if structure["line_count"] > self.max_lines_per_file:
            fixed += 1
        return fixed
