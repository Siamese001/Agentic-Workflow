"""
DEPRECATED – Zero-Loss Migration Complete (Phase 2B/Phase 4 – Dec 26, 2025)
All models have been canonically centralized in:
agentic_core/schemas/models/core_contracts.py

Imports below preserve backward compatibility. 
New code MUST import directly from core_contracts.py
"""
from agentic_core.schemas.models.core_contracts import SafetyProfile

__all__ = ["SafetyProfile"]
