"""State Management Agent - Backward compatibility shim.

DEPRECATED: This agent has been converted to a utility script.
Use agentic_core.L3_orchestration.utils.state_management_util instead.

This module maintains backward compatibility by delegating to the utility.
Will be removed in a future release.
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L3_orchestration.utils.state_management_util import (
    StateManager as _StateManager,
    StateEntry,
    IntegrityReport,
)


class StateManagementAgent(SovereignBaseAgent):
    """
    DEPRECATED: State Management Agent - now delegates to state_management_util.

    This class is maintained for backward compatibility only.
    New code should use agentic_core.L3_orchestration.utils.state_management_util directly.
    """

    def __init__(self, memory_root: Path | None = None, namespace: str = "default"):
        """Initialize StateManagementAgent (deprecated, use state_management_util instead)."""
        super().__init__(name="StateManagementAgent", layer="L3")

        warnings.warn(
            "StateManagementAgent is deprecated. Use agentic_core.L3_orchestration.utils.state_management_util instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        self._manager = _StateManager(memory_root=memory_root or Path(".canon_memory"))
        self.namespace = namespace

    def set_state(self, key: str, value: Any, metadata: dict[str, Any] | None = None) -> bool:
        """Set a state value."""
        return self._manager.set_state(key, value, metadata)

    def get_state(self, key: str) -> Any:
        """Get a state value."""
        return self._manager.get_state(key)

    def has_state(self, key: str) -> bool:
        """Check if a state key exists."""
        return self._manager.has_state(key)

    def delete_state(self, key: str) -> bool:
        """Delete a state value."""
        return self._manager.delete_state(key)

    def list_keys(self) -> list[str]:
        """List all state keys."""
        return self._manager.list_keys()

    def get_manifest(self) -> dict[str, Any]:
        """Get the state manifest."""
        return self._manager.get_manifest()

    def verify_integrity(self) -> IntegrityReport:
        """Verify state integrity."""
        return self._manager.verify_integrity()

    def clear_all(self) -> bool:
        """Clear all state."""
        return self._manager.clear_all()
