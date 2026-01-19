from __future__ import annotations
"""
DEPRECATED – Phase 5 Comprehensive Enforcement Sweep (Dec 26, 2025)
All models have been migrated to the Sovereign SSOT:
agentic_core/schemas/models/core_contracts.py

This file now serves as a backward-compatible import proxy.
New code MUST import directly from core_contracts.py
"""
from agentic_core.schemas.models.core_contracts import (
    RouteConditions,
    RouteConstraints,
    RouteConfig,
    ArchetoneConfig,
    TemperatureConfig,
)

__all__ = [
    "RouteConditions",
    "RouteConstraints",
    "RouteConfig",
    "ArchetoneConfig",
    "TemperatureConfig",
]
