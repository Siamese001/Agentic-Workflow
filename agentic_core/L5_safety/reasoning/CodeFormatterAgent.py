"""Code Formatter Agent - Backward compatibility shim.

DEPRECATED: This agent has been converted to a utility script.
Use agentic_core.L5_safety.utils.code_formatter_util instead.

This module maintains backward compatibility by delegating to the utility.
Will be removed in a future release.

AGENT-DELETION-AUTHORIZED: 2026-04-24 (W3.1 of agent-deprecation-migration-d7a3f2)
Authorization date: 2026-04-24
Archive-eligible date: 2026-07-23 (90-day cooling per constitutional \u00a73)
Consumers at authorization: 0 (verified via w3_verify_zero_consumers.py grep of
`from agentic_core.L5_safety.reasoning.CodeFormatterAgent import` and `import agentic_core.L5_safety.reasoning.CodeFormatterAgent` across live code,
excluding self and archives/ paths — zero hits).
Unique logic: none (pure delegation to agentic_core.L5_safety.utils.code_formatter_util per DEPRECATED docstring above).
Target archive path on or after eligibility date:
  archives/agents/2026-07-23/agentic_core__L5_safety__reasoning__CodeFormatterAgent.py
Cooling-timer artifact: artifacts/agent_deprecation/w3_CodeFormatterAgent.json
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
