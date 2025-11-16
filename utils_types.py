"""
Utilities — Types

Defines shared type aliases and protocol scaffolds across layers.
These types are intentionally lightweight to avoid entangling the
architecture with concrete implementations during early phases.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Protocol


class PlanObject(Dict[str, Any]):
    """Lightweight plan container used by L1 planners.

    The structure remains intentionally flexible while preserving
    mapping semantics for deterministic patch generation at L2+.
    """


class StatePatch(Dict[str, Any]):
    """Patch structure applied to the mutable orchestration state."""


class Message(Dict[str, Any]):
    """Generic message payload used by memory management."""


@dataclass
class BudgetConfig:
    """Configuration for context budgeting heuristics."""

    max_messages: int = 50
    max_rag_items: int = 20
    max_summary_chars: int = 4000


class Phase(str, Enum):
    """Enumerated lifecycle phases for the deterministic state machine."""

    INIT = "init"
    PLANNING = "planning"
    EXECUTING = "executing"
    REVIEWING = "reviewing"
    COMPLETE = "complete"
    FAILED = "failed"


class ReasonerProtocol(Protocol):
    """Protocol for L1 planners."""

    def plan(self, state: Dict[str, Any]) -> PlanObject:
        ...


class ExecutionAgentProtocol(Protocol):
    """Protocol for L2 execution agents."""

    def execute(self, plan: PlanObject, state: Dict[str, Any]) -> StatePatch:
        ...
