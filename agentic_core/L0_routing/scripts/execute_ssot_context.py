"""HealContext module for execute_ssot - extracted during Wave 1 modularization.

This module contains the HealContext class which manages healing context state.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class HealContext:
    """Context for a healing operation, tracking state across all phases."""

    targets: Any
    phase_results: dict
    alignments: list
    registry: Any
    args: Any

    def __init__(self, targets, registry, args):
        self.targets = targets
        self.phase_results = {}
        self.alignments = []
        self.registry = registry
        self.args = args

    def record_phase_result(self, phase: str, result: Any) -> None:
        """Record the result of a phase execution."""
        self.phase_results[phase] = result

    def get_phase_result(self, phase: str) -> Any:
        """Get the result of a specific phase."""
        return self.phase_results.get(phase)

    def add_alignment(self, alignment: Any) -> None:
        """Add an alignment result to the context."""
        self.alignments.append(alignment)

    def is_valid(self) -> bool:
        """Check if the context has all required components."""
        return self.targets is not None and self.registry is not None
