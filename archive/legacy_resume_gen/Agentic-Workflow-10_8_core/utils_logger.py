"""
Utilities — Logger

Responsibilities:
    • Define logging scaffolds shared across agentic layers.
    • Provide structured logging hooks for orchestration, execution, and safety components.
    • Avoid coupling to specific frameworks until implementation phases.

This file is scaffolded for Priority 0; implementation comes later.
"""
from datetime import datetime
from typing import Any, Dict, List


SAFETY_LOG: List[Dict[str, Any]] = []


def log_safety_decision(payload: Dict[str, Any], patch: Dict[str, Any]) -> None:
    """Deterministic stub for logging safety gateway decisions."""

    SAFETY_LOG.append({"payload": payload, "patch": patch, "ts": datetime.utcnow().isoformat()})
