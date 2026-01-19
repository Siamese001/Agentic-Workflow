"""
Mission Strategies for UnifiedOrchestratorAgent

This package contains strategy implementations for the unified orchestration engine.
Each strategy encapsulates the specific logic of what agents to run and in what order.

Available Strategies:
    - HealingStrategy: Tiered healing execution (Pre-Flight, Structural, etc.)
"""
from archives.void_violations.healing_strategy import HealingStrategy

__all__ = [
    "HealingStrategy",
]
