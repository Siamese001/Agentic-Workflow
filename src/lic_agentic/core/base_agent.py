"""Shared LIC agent base wired into the dependency graph."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - convenience for type-checkers only
    from .dependency_injection import LICCoreContext


class LICBaseAgent:
    """Base agent that resolves all DI-managed dependencies."""

    def __init__(self, context: "LICCoreContext") -> None:
        self.context = context
        self.metrics = context.resolve("metrics_tracker")
        self.policy = context.resolve("policy_controller")
        self.registry = context.resolve("tool_registry")
        self.content_store = context.resolve("content_store")
        self.evidence_registry = context.resolve("evidence_registry")
        self.conductor = context.resolve("conductor")

    # Optional hook for future logging integrations.
    def log(self, message: str) -> None:  # pragma: no cover - placeholder
        _ = message
        return None
