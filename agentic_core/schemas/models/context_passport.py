"""
DEPRECATED – Zero-Loss Migration Complete (Phase 2B/Phase 4 – Dec 26, 2025)
All models have been canonically centralized in:
AgenticCore/schemas/models/core_contracts.py

Imports below preserve backward compatibility. 
New code MUST import directly from core_contracts.py
"""
from AgenticCore.schemas.models.core_contracts import (
    ThermalProfile,
    HardState,
    SoftState,
    ThermalConfig,
    SignedClaim,
    SignalContext
)

__all__ = [
    "ThermalProfile", "HardState", "SoftState", 
    "ThermalConfig", "SignedClaim", "SignalContext"
]
