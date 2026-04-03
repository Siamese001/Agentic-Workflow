"""Complexity Analyzer Agent - Backward compatibility shim.

DEPRECATED: This agent has been converted to a utility script.
Use agentic_core.L5_safety.utils.complexity_analyzer_util instead.

This module maintains backward compatibility by delegating to the utility.
Will be removed in a future release.
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L5_safety.utils.complexity_analyzer_util import (
    ComplexityAnalyzer as _ComplexityAnalyzer,
    ComplexityViolation,
    ComplexityConfig,
    calculate_cyclomatic_complexity as _calculate_cyclomatic_complexity,
)


class ComplexityAnalyzerAgent(SovereignBaseAgent):
    """
    DEPRECATED: Complexity Analyzer Agent - now delegates to complexity_analyzer_util.

    This class is maintained for backward compatibility only.
    New code should use agentic_core.L5_safety.utils.complexity_analyzer_util directly.
    """

    def __init__(self, config: ComplexityConfig | None = None) -> None:
        """Initialize ComplexityAnalyzerAgent (deprecated, use complexity_analyzer_util instead)."""
        super().__init__(name="ComplexityAnalyzerAgent", layer="L5")

        warnings.warn(
            "ComplexityAnalyzerAgent is deprecated. Use agentic_core.L5_safety.utils.complexity_analyzer_util instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        self._config = config or ComplexityConfig()
        self._analyzer = _ComplexityAnalyzer(self._config)
        self.project_root = self._config.project_root or Path.cwd()

    def analyze_repository(self, target_path: Path | None = None) -> dict[str, Any]:
        """Entry point for full scan."""
        report = self._analyzer.analyze_repository(target_path)
        return report.to_dict()

    def analyze_file(self, file_path: Path) -> list[ComplexityViolation]:
        """Analyze a single file for complexity metrics."""
        return self._analyzer.analyze_file(file_path)

    def _calculate_complexity(self, node: Any) -> int:
        """Computes McCabe Cyclomatic Complexity."""
        import ast
        if isinstance(node, ast.AST):
            return _calculate_cyclomatic_complexity(node)
        return 1

    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Sovereign Interface - report complexity issues."""
        return self._analyzer.heal_repository(dry_run, execute, **kwargs)

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """Heal complexity violations."""
        return self._analyzer.heal(violation)
