"""State adapter for deterministic state updates."""
from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Dict, List

from .models import MainGraphState, StatePatch


@dataclass
class MemoryState:
    messages: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class EphemeralState:
    scratch: Dict[str, Any] = field(default_factory=dict)


class StateAdapterStack:
    def __init__(self) -> None:
        self.memory_state = MemoryState()
        self.ephemeral_state = EphemeralState()
        self._graph_state = MainGraphState()

    @property
    def state(self) -> Dict[str, Any]:
        return copy.deepcopy(self._graph_state.__dict__)

    def apply_patch(self, patch: StatePatch) -> Dict[str, Any]:
        for key, value in patch.items():
            setattr(self._graph_state, key, value)
        return self.state


__all__ = ["MemoryState", "EphemeralState", "StateAdapterStack"]
