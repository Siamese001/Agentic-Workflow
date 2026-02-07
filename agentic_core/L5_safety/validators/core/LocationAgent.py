from __future__ import annotations

# ruff: noqa: E501, E402
"""
LocationAgent — Backward-compatibility shim (LCD+ Phase 0.3).

This file formerly contained ~2,241 lines of facade code. All logic has been
salvaged into the canonical owners:

    - LocationValidatorAgent: Validation (run, validate_file_location, enforce_void_compliance)
    - LocationHealerAgent: Healing (heal, heal_violations, heal_repository, cleanup_violations)
    - location_path_util: Utilities (is_path_compliant, get_location_agent singleton)

This shim preserves backward compatibility for existing imports:
    from agentic_core.L5_safety.validators.core.LocationAgent import LocationAgent
    from agentic_core.L5_safety.validators.core.location_agent import LocationAgent  # Windows

All new code should import from the canonical modules directly.
"""
from pathlib import Path

from agentic_core.L5_safety.validators.core.LocationHealerAgent import (
    LocationHealerAgent,
)
from agentic_core.L5_safety.utils.location_path_util import (  # noqa: F401
    get_location_agent,
    is_path_compliant,
)


class LocationAgent(LocationHealerAgent):
    """Backward-compatibility shim — inherits all behavior from LocationHealerAgent.

    Validation methods delegate to LocationValidatorAgent.
    Healing methods are inherited from LocationHealerAgent.

    New code should import LocationHealerAgent or LocationValidatorAgent directly.
    """

    def run(self, files: list[Path] | None = None) -> dict:
        """Delegate validation scan to LocationValidatorAgent."""
        from agentic_core.L5_safety.validators.core.LocationValidatorAgent import (
            LocationValidatorAgent,
        )

        validator = LocationValidatorAgent(project_root=self.project_root)
        return validator.run(files)

    def validate_file_location(self, file_path: Path) -> tuple[bool, str]:
        """Delegate to LocationValidatorAgent."""
        from agentic_core.L5_safety.validators.core.LocationValidatorAgent import (
            LocationValidatorAgent,
        )

        validator = LocationValidatorAgent(project_root=self.project_root)
        return validator.validate_file_location(file_path)

    def validate_sovereign_roots(self) -> list[tuple[Path, str]]:
        """Delegate to LocationValidatorAgent."""
        from agentic_core.L5_safety.validators.core.LocationValidatorAgent import (
            LocationValidatorAgent,
        )

        validator = LocationValidatorAgent(project_root=self.project_root)
        return validator.validate_sovereign_roots()
