"""
L1 — Core Reasoner Base

Defines an abstract interface for cognition-layer planners. Implementations
should supply planning logic elsewhere while keeping this layer focused on
contracts only.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, object

# from archives.legacy_resume_gen.Agentic-Workflow-10_8_core.utils_types import PlanObject  # INVALID: Cannot import from path with hyphens


class Reasoner(ABC):
    """Abstract base class for L1 planners."""

    @abstractmethod
    def plan(self, state: Dict[str, object]) -> PlanObject:
        """Return a plan object derived from the current orchestration state."""
        raise NotImplementedError
