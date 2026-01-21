from __future__ import annotations
"""
Base Sovereign Schemas
======================
Defines the root models and structural entities for the Sovereign system.
All primary system entities should inherit from SovereignBaseModel to
ensure strict validation and immutability.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict

# ==========================================
# Sovereign Root Model
# ==========================================

class SovereignBaseModel(BaseModel):
    """
    Base model for all Sovereign entities.
    Enforces strict type checking and immutability (frozen) to ensure
    data integrity across agent handoffs and state transitions.
    """
    ModelConfig = ConfigDict(strict=True, frozen=True)

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
    canon_key: Optional[int] = None
