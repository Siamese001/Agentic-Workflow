"""Architecture Governor Validator Agent - Backward compatibility shim.

DEPRECATED: This agent has been converted to a utility script.
Use agentic_core.L5_safety.utils.architecture_governor_validator_util instead.

This module maintains backward compatibility by delegating to the utility.
Will be removed in a future release.
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any

from agentic_core.L5_safety.utils.architecture_governor_validator_util import (
    CHECK_ID,
    GovernanceValidationResult,
)
from agentic_core.L5_safety.utils.architecture_governor_validator_util import (
    ArchitectureGovernorValidator as _ArchitectureGovernorValidator,
)


class ArchitectureGovernorValidatorAgent:
    """
    DEPRECATED: Architecture Governor Validator Agent - now delegates to
    architecture_governor_validator_util.

    This class is maintained for backward compatibility only.
    New code should use agentic_core.L5_safety.utils.architecture_governor_validator_util directly.
    """

    CHECK_ID = CHECK_ID

    def __init__(self, project_root: Path) -> None:
        """Initialize ArchitectureGovernorValidatorAgent (deprecated, use utility instead)."""
        warnings.warn(
            "ArchitectureGovernorValidatorAgent is deprecated. Use agentic_core.L5_safety.utils.architecture_governor_validator_util instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        self.project_root = Path(project_root).resolve()
        self._validator = _ArchitectureGovernorValidator(self.project_root)

    def scan(self, target_territory: str | None = None) -> dict[str, Any]:
        """Run ArchitectureGovernorAgent.heal_repository in dry-run mode."""
        return self._validator.scan(target_territory)

    def to_check_dict(self, target_territory: str | None = None) -> dict[str, Any]:
        """Return structured check dict for _invoke_healer dispatch."""
        return self._validator.to_check_dict(target_territory)

    def run(self, target_territory: str | None = None) -> dict[str, Any]:
        """Alias for to_check_dict for orchestrator compatibility."""
        return self._validator.run(target_territory)

    def validate(self, target_territory: str | None = None) -> GovernanceValidationResult:
        """Validate architecture governance."""
        return self._validator.validate(target_territory)
