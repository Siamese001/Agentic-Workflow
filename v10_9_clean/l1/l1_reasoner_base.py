"""
L1 — Core Reasoner Base

Defines an abstract interface for cognition-layer planners. Implementations
should supply planning logic elsewhere while keeping this layer focused on
contracts only.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Any

from utils_types import PlanObject


class Reasoner(ABC):
    """Abstract base class for L1 planners."""

    @abstractmethod
    def plan(self, state: Dict[str, Any]) -> PlanObject:
        """Return a plan object derived from the current orchestration state."""
        raise NotImplementedError
