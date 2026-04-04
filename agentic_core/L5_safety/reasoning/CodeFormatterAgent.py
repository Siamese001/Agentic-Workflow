"""Code Formatter Agent - Backward compatibility shim.

DEPRECATED: This agent has been converted to a utility script.
Use agentic_core.L5_safety.utils.code_formatter_util instead.

This module maintains backward compatibility by delegating to the utility.
Will be removed in a future release.
"""

from __future__ import annotations

import warnings
from pathlib import Path

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L5_safety.utils.code_formatter_util import (
    CodeFormatter as _CodeFormatter,
)
from agentic_core.L5_safety.utils.code_formatter_util import (
    FormatResult,
)
from agentic_core.L5_safety.utils.code_formatter_util import (
    format_file as _format_file,
)
from agentic_core.L5_safety.utils.code_formatter_util import (
    format_files as _format_files,
)


class CodeFormatterAgent(SovereignBaseAgent):
    """
    DEPRECATED: Code Formatter Agent - now delegates to code_formatter_util.

    This class is maintained for backward compatibility only.
    New code should use agentic_core.L5_safety.utils.code_formatter_util directly.
    """

    def __init__(self):
        """Initialize CodeFormatterAgent (deprecated, use code_formatter_util instead)."""
        super().__init__(name="CodeFormatterAgent", layer="L5")

        warnings.warn(
            "CodeFormatterAgent is deprecated. Use agentic_core.L5_safety.utils.code_formatter_util instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        self._formatter = _CodeFormatter()

    def format_file(self, file_path: Path | str) -> FormatResult:
        """Format a single file."""
        return _format_file(file_path)

    def format_files(self, file_paths: list[Path | str]) -> list[FormatResult]:
        """Format multiple files."""
        return _format_files(file_paths)
