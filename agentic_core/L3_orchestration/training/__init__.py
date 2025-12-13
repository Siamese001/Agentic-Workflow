"""Agent Training and Self-Evolution.

Phase 4 - Pillar 5: Capability Maturity (Self-Evolving System)
Agent Gym for offline simulation, benchmarking, and self-improvement.
"""

from .agent_gym import (
    AgentGym,
    TrainingScenario,
    BenchmarkResult,
    TrainingSession,
    create_agent_gym,
)

__all__ = [
    "AgentGym",
    "TrainingScenario",
    "BenchmarkResult",
    "TrainingSession",
    "create_agent_gym",
]
