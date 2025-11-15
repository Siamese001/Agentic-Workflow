"""Placeholder state adapter stack for bridging v10.7 and v10.8 graph state."""

from __future__ import annotations

from typing import Any, Dict, Optional


class StateAdapterStack:
    """Stub that will translate workflow state between runtime versions."""

    def __init__(self, context: Optional[Any] = None) -> None:
        self.context = context

    def adapt_to_v10_8(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """TODO(v10.8): Normalize legacy state into layer-pure payloads."""

        return state

    def adapt_to_v10_7(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """TODO(v10.8): Emit compatibility patches for existing nodes."""

        return state
