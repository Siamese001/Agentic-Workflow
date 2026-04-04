"""Code Validator Agent - Backward compatibility shim.

DEPRECATED: This agent has been converted to a utility script.
Use agentic_core.L5_safety.utils.code_validator_util instead.

This module maintains backward compatibility by delegating to the utility.
Will be removed in a future release.
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L5_safety.utils.code_validator_util import (
    CodeValidator as _CodeValidator,
)
from agentic_core.L5_safety.utils.code_validator_util import (
    RuleSet,
    Violation,
)


class CodeValidatorAgent(SovereignBaseAgent):
    """
    DEPRECATED: Code Validator Agent - now delegates to code_validator_util.

    This class is maintained for backward compatibility only.
    New code should use agentic_core.L5_safety.utils.code_validator_util directly.
    """

    def __init__(self, ruleset: RuleSet | None = None, **kwargs: Any) -> None:
        """Initialize CodeValidatorAgent (deprecated, use code_validator_util instead)."""
        super().__init__(**kwargs)

        warnings.warn(
            "CodeValidatorAgent is deprecated. Use agentic_core.L5_safety.utils.code_validator_util instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        self.ruleset = ruleset or RuleSet()
        self._validator = _CodeValidator(self.ruleset)
        self._validation_results: list[Violation] = []

    def validate_syntax(self, file_path: Path) -> list[Violation]:
        """Validate Python syntax for a file."""
        return self._validator.validate_syntax(file_path)

    def validate_canon(self, file_path: Path) -> list[Violation]:
        """Validate canonical patterns for a file."""
        return self._validator.validate_canon(file_path)

    def validate_async(self, file_path: Path) -> list[Violation]:
        """Validate async/await usage for a file."""
        return self._validator.validate_async(file_path)

    def validate_prints(self, file_path: Path) -> list[Violation]:
        """Validate print statement usage for a file."""
        return self._validator.validate_prints(file_path)

    def validate_file(self, file_path: Path) -> list[Violation]:
        """Validate a single file for all code rules."""
        return self._validator.validate_file(file_path)

    def validate_directory(self, directory: Path) -> list[Violation]:
        """Validate all Python files in a directory."""
        report = self._validator.validate_directory(directory)
        return report.violations
