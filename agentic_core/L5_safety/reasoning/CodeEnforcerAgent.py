"""Code Enforcer Agent - Backward compatibility shim.

DEPRECATED: This agent has been converted to a utility script.
Use agentic_core.L5_safety.utils.code_enforcer_util instead.

This module maintains backward compatibility by delegating to the utility.
Will be removed in a future release.
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L5_safety.utils.code_enforcer_util import (
    CodeEnforcer as _CodeEnforcer,
)


class CodeEnforcerAgent(SovereignBaseAgent):
    """
    DEPRECATED: Code Enforcer Agent - now delegates to code_enforcer_util.

    This class is maintained for backward compatibility only.
    New code should use agentic_core.L5_safety.utils.code_enforcer_util directly.
    """

    def __init__(self):
        """Initialize CodeEnforcerAgent (deprecated, use code_enforcer_util instead)."""
        super().__init__(name="CodeEnforcerAgent", layer="L5")

        warnings.warn(
            "CodeEnforcerAgent is deprecated. Use agentic_core.L5_safety.utils.code_enforcer_util instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        self._enforcer = _CodeEnforcer()

    def validate_file(self, file_path: Path) -> list[Any]:
        """Validate a file for code violations."""
        return self._enforcer.validate_file(file_path)

    def enforce_standards(self, file_path: Path) -> dict[str, Any]:
        """Enforce code standards on a file."""
        return self._enforcer.enforce_standards(file_path)
