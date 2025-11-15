"""Layer-4 state adapter responsible for applying typed patches."""

from __future__ import annotations

import copy
from dataclasses import asdict, is_dataclass
from typing import Any, Dict, Mapping, MutableMapping

from core_v10_7 import MainGraphState


class StateAdapterStack:
    """L4 Memory & State: the ONLY component allowed to mutate workflow state."""

    def __init__(self, context: Any, debug_mode: bool = False) -> None:
        self.context = context
        self.debug_mode = debug_mode

    def apply_patch(self, state_dict: Dict[str, Any], patch: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a schema-validated patch to the workflow state."""

        if not isinstance(state_dict, MutableMapping):
            state_dict = {}
        if not isinstance(patch, Mapping):
            return copy.deepcopy(state_dict)

        typed_state = MainGraphState.from_dict(copy.deepcopy(state_dict))
        normalized_patch = self._normalize_patch(patch)
        merged_dict = self._deep_merge(typed_state.to_dict(), normalized_patch)

        validated_state = MainGraphState.from_dict(merged_dict)
        return validated_state.to_dict()

    def _normalize_patch(self, value: Any) -> Any:
        if isinstance(value, Mapping):
            return {k: self._normalize_patch(v) for k, v in value.items()}
        if isinstance(value, list):
            return [self._normalize_patch(v) for v in value]
        if hasattr(value, "model_dump") and callable(value.model_dump):
            return self._normalize_patch(value.model_dump())
        if is_dataclass(value):
            return self._normalize_patch(asdict(value))
        return copy.deepcopy(value)

    def _deep_merge(self, base: Dict[str, Any], patch: Dict[str, Any]) -> Dict[str, Any]:
        for key, patch_value in patch.items():
            if isinstance(patch_value, Mapping):
                existing = base.get(key)
                if not isinstance(existing, Mapping):
                    existing = {}
                base[key] = self._deep_merge(dict(existing), dict(patch_value))
            elif isinstance(patch_value, list):
                base[key] = copy.deepcopy(patch_value)
            else:
                base[key] = patch_value
        return base
