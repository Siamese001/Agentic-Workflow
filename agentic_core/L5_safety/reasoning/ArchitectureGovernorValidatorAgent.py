"""Architecture Governor Validator Agent - Backward compatibility shim.

DEPRECATED: This agent has been converted to a utility script.
Use agentic_core.L5_safety.utils.architecture_governor_validator_util instead.

This module maintains backward compatibility by delegating to the utility.
Will be removed in a future release.

AGENT-DELETION-AUTHORIZED: 2026-04-24 (W3.1 of agent-deprecation-migration-d7a3f2)
Authorization date: 2026-04-24
Archive-eligible date: 2026-07-23 (90-day cooling per constitutional \u00a73)
Consumers at authorization: 0 (verified via w3_verify_zero_consumers.py grep of
`from agentic_core.L5_safety.reasoning.ArchitectureGovernorValidatorAgent import` and `import agentic_core.L5_safety.reasoning.ArchitectureGovernorValidatorAgent` across live code,
excluding self and archives/ paths — zero hits).
Unique logic: none (pure delegation to agentic_core.L5_safety.utils.architecture_governor_validator_util per DEPRECATED docstring above).
Target archive path on or after eligibility date:
  archives/agents/2026-07-23/agentic_core__L5_safety__reasoning__ArchitectureGovernorValidatorAgent.py
Cooling-timer artifact: artifacts/agent_deprecation/w3_ArchitectureGovernorValidatorAgent.json
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
