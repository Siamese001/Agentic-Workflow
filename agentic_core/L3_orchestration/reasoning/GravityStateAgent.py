"""Gravity State Agent - Backward compatibility shim.

DEPRECATED: This agent has been converted to a utility script.
Use agentic_core.L3_orchestration.utils.gravity_state_util instead.

This module maintains backward compatibility by delegating to the utility.
Will be removed in a future release.

AGENT-DELETION-AUTHORIZED: 2026-04-24 (W3.2 of agent-deprecation-migration-d7a3f2)
Authorization date: 2026-04-24
Archive-eligible date: 2026-07-23 (90-day cooling per constitutional \u00a73)
Consumers at authorization: 0 (Only consumer was agentic_core/interfaces/state_agents.py (dead interface re-export with zero importers). W3.2 edit removed the GravityStateAgent entry + docstring note pointing callers at the gravity_state_util. Remaining live consumer count: 0.)
Unique logic: none (pure delegation to agentic_core.L3_orchestration.utils.gravity_state_util per DEPRECATED docstring above).
Target archive path on or after eligibility date:
  archives/agents/2026-07-23/agentic_core__L3_orchestration__reasoning__GravityStateAgent.py
Cooling-timer artifact: artifacts/agent_deprecation/w3_GravityStateAgent.json
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L3_orchestration.utils.gravity_state_util import (
    GravityStateManager as _GravityStateManager,
)
from agentic_core.L3_orchestration.utils.gravity_state_util import (
    load_state as _load_state,
)
from agentic_core.L3_orchestration.utils.gravity_state_util import (
    save_state as _save_state,
)


class GravityStateAgent(SovereignBaseAgent):
    """
    DEPRECATED: Gravity State Agent - now delegates to gravity_state_util.

    This class is maintained for backward compatibility only.
    New code should use agentic_core.L3_orchestration.utils.gravity_state_util directly.
    """

    def __init__(self, project_root: Path | None = None):
        """Initialize GravityStateAgent (deprecated, use gravity_state_util instead)."""
        super().__init__(name="GravityStateAgent", layer="L3")

        warnings.warn(
            "GravityStateAgent is deprecated. Use agentic_core.L3_orchestration.utils.gravity_state_util instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        self._manager = _GravityStateManager(project_root or Path.cwd())

    def record_healing(
        self,
        file_path: str,
        original_import: str,
        healed_import: str,
        violation_type: str,
        healing_strategy: str,
        **kwargs,
    ) -> bool:
        """Record a healing operation."""
        return self._manager.record_healing(
            file_path=file_path,
            original_import=original_import,
            healed_import=healed_import,
            violation_type=violation_type,
            healing_strategy=healing_strategy,
            **kwargs,
        )

    def get_healing_history(self, file_path: str | None = None) -> list[dict[str, Any]]:
        """Get healing history for a file or all files."""
        return self._manager.get_healing_history(file_path)

    def load_state(self) -> dict[str, Any]:
        """Load the current gravity state."""
        return _load_state(self._manager.project_root)

    def save_state(self, state: dict[str, Any]) -> bool:
        """Save the gravity state."""
        return _save_state(self._manager.project_root, state)

    def get_statistics(self) -> dict[str, Any]:
        """Get healing statistics."""
        return self._manager.get_statistics()

    def is_healed(self, file_path: str) -> bool:
        """Check if a file has been healed."""
        return self._manager.is_healed(file_path)
