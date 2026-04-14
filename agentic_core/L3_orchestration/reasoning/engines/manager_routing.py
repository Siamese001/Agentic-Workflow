"""Manager routing shim with deterministic route normalization."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any


_ALLOWED_ROUTES = {"fallback", "semantic", "structural", "hybrid", "action", "rag"}


def _normalize_route(value: Any, default: str) -> str:
    route = str(value or default).strip().lower() or default
    return route if route in _ALLOWED_ROUTES else default


@dataclass
class ManagerRouting:
    """Small placeholder object used by import-and-contract tests."""

    state: dict[str, Any] = field(default_factory=dict)
    default_route: str = "fallback"

    def run(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        normalized = dict(payload or {})
        route = _normalize_route(
            normalized.get("route", self.state.get("route", self.default_route)), self.default_route
        )
        normalized["route"] = route
        metadata = normalized.get("metadata")
        if metadata is not None and not isinstance(metadata, dict):
            normalized["metadata"] = {"value": metadata}
        self.state.update(normalized)
        return deepcopy(self.state)

    def current_route(self) -> str:
        return _normalize_route(self.state.get("route", self.default_route), self.default_route)

    def reset(self) -> None:
        self.state.clear()
        self.state["route"] = self.default_route


def validate_manager_routing() -> bool:
    probe = ManagerRouting()
    state = probe.run({"route": "semantic"})
    return state.get("route") == "semantic" and probe.current_route() == "semantic"


__all__ = ["ManagerRouting", "validate_manager_routing"]
