"""Reasoning toggles for the LIC outreach stack."""
from __future__ import annotations

from pydantic import BaseModel, Field, ValidationError


class ReasoningToggles(BaseModel):
    """Configuration flags and bounds for reasoning behaviors."""

    cot: bool = Field(default=True, description="Enable chain-of-thought prompting.")
    tot_branches: int = Field(
        default=3,
        description="Maximum number of tree-of-thought branches to explore.",
    )
    min_tot_depth: int = Field(
        default=2,
        description="Minimum reasoning depth for tree-of-thought exploration.",
    )
    self_consistency: int = Field(
        default=3,
        description="Number of self-consistency samples to aggregate.",
    )
    reflexion: bool = Field(default=True, description="Enable reflexion feedback loop.")
    temperature_cap: float = Field(
        default=0.5,
        description="Upper bound for model sampling temperature.",
    )

    def __init__(self, **data):  # type: ignore[override]
        super().__init__(**data)
        self._normalize()
        self._validate()

    def _normalize(self) -> None:
        """Coerce numeric values to deterministic primitive types."""

        self.tot_branches = int(self.tot_branches)
        self.min_tot_depth = int(self.min_tot_depth)
        self.self_consistency = int(self.self_consistency)
        self.temperature_cap = float(self.temperature_cap)

    def _validate(self) -> None:
        if not 1 <= self.tot_branches <= 4:
            raise ValidationError("tot_branches must be between 1 and 4")
        if not 1 <= self.min_tot_depth <= 3:
            raise ValidationError("min_tot_depth must be between 1 and 3")
        if not 1 <= self.self_consistency <= 5:
            raise ValidationError("self_consistency must be between 1 and 5")
        if not 0.1 <= self.temperature_cap <= 0.9:
            raise ValidationError("temperature_cap must be between 0.1 and 0.9")
