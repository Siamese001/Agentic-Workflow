from __future__ import annotations

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""
Base Sovereign Schemas
======================
Defines the root models and structural entities for the Sovereign system.
All primary system entities should inherit from SovereignBaseModel to
ensure strict validation and immutability.
"""


from pydantic import BaseModel, ConfigDict, model_validator

# ==========================================
# Sovereign Root Model
# ==========================================


class SovereignBaseModel(BaseModel):
    """
    Base model for all Sovereign entities.
    Enforces strict type checking and immutability (frozen) to ensure
    data integrity across agent handoffs and state transitions.
    """

    # [HARDENED] Enforcing SSOT immutability with frozen=True and extra="forbid"
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    @model_validator(mode="after")
    def validate_invariants(self) -> SovereignBaseModel:
        """Cross-field validation hook for shared invariants."""
        return self


# ==========================================
# Structural Entities
# ==========================================


class Territory(SovereignBaseModel):
    """
    Represents a logical or physical boundary within the system.
    Used for mapping organizational depth and canonical paths.
    """

    name: str
    depth: int
    path: str
    canon_key: int | None = None
