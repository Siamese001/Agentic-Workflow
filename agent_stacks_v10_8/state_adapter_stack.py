"""State adapter stack for controlled state mutations."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any, Dict


class StateAdapterStack:
    """Applies immutable patches to workflow state structures."""

    def __init__(self, context: Any | None = None, debug_mode: bool = False) -> None:
        self.context = context
        self.debug_mode = debug_mode

    def apply_patch(self, state: Dict[str, Any], patch: Dict[str, Any]) -> Dict[str, Any]:
        """Return a new state derived from *state* with *patch* merged in."""

        base = deepcopy(state)
        return self._merge(base, patch)

    def merge_patch(self, base_patch: Dict[str, Any], patch: Dict[str, Any]) -> Dict[str, Any]:
        """Merge *patch* into *base_patch* and return the combined patch."""

        base = deepcopy(base_patch)
        return self._merge(base, patch)

    def build_a2a_message_patch(
        self,
        *,
        sender: str,
        message_type: str,
        payload: Dict[str, Any],
        recipient: str = "ALL",
    ) -> Dict[str, Any]:
        """Construct an A2A message patch with a UTC timestamp."""

        return {
            "a2a": {
                "messages": [
                    {
                        "sender": sender,
                        "recipient": recipient,
                        "message_type": message_type,
                        "payload": payload,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                ]
            }
        }

    def _merge(self, target: Dict[str, Any], patch: Dict[str, Any]) -> Dict[str, Any]:
        for key, value in patch.items():
            if isinstance(value, dict):
                child = target.get(key)
                if not isinstance(child, dict):
                    child = {}
                target[key] = self._merge(deepcopy(child), value)
            elif isinstance(value, list):
                existing = target.get(key)
                if isinstance(existing, list):
                    target[key] = existing + list(value)
                else:
                    target[key] = list(value)
            else:
                target[key] = value
        return target
