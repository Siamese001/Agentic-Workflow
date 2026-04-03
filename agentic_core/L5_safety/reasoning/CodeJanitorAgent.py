"""Code Janitor Agent - Backward compatibility shim.

DEPRECATED: This agent has been converted to a utility script.
Use agentic_core.L5_safety.utils.code_janitor_util instead.

This module maintains backward compatibility by delegating to the utility.
Will be removed in a future release.
"""

from __future__ import annotations

import warnings
from pathlib import Path

from agentic_core.L5_safety.validators.CanonBaseAgent import CanonBaseAgent
from agentic_core.L5_safety.utils.code_janitor_util import (
    CodeJanitor as _CodeJanitor,
    validate_syntax as _validate_syntax,
    validate_indentation as _validate_indentation,
    JanitorViolation,
)


class CodeJanitorAgent(CanonBaseAgent):
    """
    DEPRECATED: Code Janitor Agent - now delegates to code_janitor_util.

    This class is maintained for backward compatibility only.
    New code should use agentic_core.L5_safety.utils.code_janitor_util directly.
    """

    def __init__(self):
        """Initialize CodeJanitorAgent (deprecated, use code_janitor_util instead)."""
        super().__init__(name="CodeJanitorAgent")

        warnings.warn(
            "CodeJanitorAgent is deprecated. Use agentic_core.L5_safety.utils.code_janitor_util instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        self._janitor = _CodeJanitor()

    def validate_syntax(self, file_path: str) -> list[JanitorViolation]:
        """Validate Python syntax."""
        return _validate_syntax(file_path)

    def validate_indentation(self, file_path: str) -> list[JanitorViolation]:
        """Validate indentation consistency."""
        return _validate_indentation(file_path)

    def validate_file(self, file_path: Path) -> list[JanitorViolation]:
        """Run all janitor validations on a file."""
        return self._janitor.validate_file(file_path)
