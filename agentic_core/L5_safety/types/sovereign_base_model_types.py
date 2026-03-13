from __future__ import annotations

"\nBase Sovereign Schemas\n======================\nDefines the root models and structural entities for the Sovereign system.\nAll primary system entities should inherit from SovereignBaseModel to\nensure strict validation and immutability.\n"
from pydantic import BaseModel, ConfigDict, model_validator


class SovereignBaseModel(BaseModel):
    """
    Base model for all Sovereign entities.
    Enforces strict type checking and immutability (frozen) to ensure
    data integrity across agent handoffs and state transitions.
    """

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    @model_validator(mode="after")
    def validate_invariants(self) -> SovereignBaseModel:
        """Cross-field validation hook for shared invariants."""
        return self


class Territory(SovereignBaseModel):
    """
    Represents a logical or physical boundary within the system.
    Used for mapping organizational depth and canonical paths.
    """

    name: str
    depth: int
    path: str
    canon_key: int | None = None
