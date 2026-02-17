from __future__ import annotations

# ruff: noqa: E501, E402
"""
LocationAgent — DEPRECATED backward-compatibility shim (LCD+ Phase 0.3).

[DEPRECATED 2026-02-07] This shim exists ONLY for backward compatibility.
New code MUST import from canonical modules directly:

    - LocationValidatorAgent: Validation (run, validate_file_location, enforce_void_compliance)
    - LocationHealerAgent: Healing (heal, heal_violations, heal_repository, cleanup_violations)
    - location_path_util: Utilities (is_path_compliant, get_location_agent singleton)

DO NOT add new logic here. This file will be removed once all 80+ references
are migrated to the canonical agents above.
"""
import warnings
from pathlib import Path

from agentic_core.L5_safety.reasoning.LocationHealerAgent import (
    LocationHealerAgent,
)
from agentic_core.L5_safety.utils.location_path_util import (  # noqa: F401
    get_location_agent,
    is_path_compliant,
)


class LocationAgent(LocationHealerAgent):
    """DEPRECATED backward-compatibility shim — inherits all behavior from LocationHealerAgent.

    [DEPRECATED 2026-02-07] Import LocationHealerAgent or LocationValidatorAgent directly.
    This shim will be removed once all 80+ references are migrated.
    """

    def __post_init__(self):
        warnings.warn(
            "LocationAgent is deprecated. Use LocationHealerAgent or LocationValidatorAgent directly.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__post_init__()

    # guardian: allow-type-erasure
    def run(self, files: list[Path] | None = None) -> dict:
        """Delegate validation scan to LocationValidatorAgent."""
        from agentic_core.L5_safety.reasoning.LocationValidatorAgent import (
            LocationValidatorAgent,
        )

        validator = LocationValidatorAgent(project_root=self.project_root)
        return validator.run(files)

    def validate_file_location(self, file_path: Path) -> tuple[bool, str]:
        """Delegate to LocationValidatorAgent."""
        from agentic_core.L5_safety.reasoning.LocationValidatorAgent import (
            LocationValidatorAgent,
        )

        validator = LocationValidatorAgent(project_root=self.project_root)
        return validator.validate_file_location(file_path)

    def validate_sovereign_roots(self) -> list[tuple[Path, str]]:
        """Delegate to LocationValidatorAgent."""
        from agentic_core.L5_safety.reasoning.LocationValidatorAgent import (
            LocationValidatorAgent,
        )

        validator = LocationValidatorAgent(project_root=self.project_root)
        return validator.validate_sovereign_roots()

    def heal(self, violation, **kwargs):
        return super().heal(violation, **kwargs)


    # guardian: allow-type-erasure
    def heal_repository(self, *args, **kwargs) -> dict:
        """heal_repository() not implemented for LocationAgent."""
        raise NotImplementedError("heal_repository() not implemented for LocationAgent")
