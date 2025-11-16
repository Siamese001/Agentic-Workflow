"""
Utilities — Logger

Responsibilities:
    • Define logging scaffolds shared across agentic layers.
    • Provide structured logging hooks for orchestration, execution, and safety components.
    • Avoid coupling to specific frameworks until implementation phases.

This file is scaffolded for Priority 0; implementation comes later.
"""


def log_safety_decision(payload: dict, patch: dict) -> None:
    """Deterministic stub for logging safety gateway decisions."""

    # Placeholder: in future, route to structured logging sink.
    _ = payload, patch
