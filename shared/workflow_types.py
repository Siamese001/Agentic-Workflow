# Ownership: shared
# Layer: shared
# Agent: all
# -*- coding: utf-8 -*-
"""
Workflow status and checkpoint types.

EXTRACTED FROM: apps_rg/L3_orchestration/orchestrate_resume_generation.py
CANON COMPLIANCE: Sub-atomic split for line limit enforcement
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, Optional


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = auto()
    OPEN = auto()
    HALF_OPEN = auto()


class HopStatus(Enum):
    """Status of a workflow hop/step."""

    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    SKIPPED = auto()


class GateDecision(Enum):
    """Decision from a workflow gate."""

    PROCEED = auto()
    BLOCK = auto()
    RETRY = auto()
    ESCALATE = auto()


@dataclass
class HopCheckpoint:
    """Checkpoint data for a workflow hop."""

    hop_id: str
    status: HopStatus
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
    output: Optional[Dict[str, Any]] = None
