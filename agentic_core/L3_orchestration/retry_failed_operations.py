"""
01_agentic_core/L3_orchestration/P3_aggregate/execute_actions/routing/retry.py
AUTO-HARDENED BY ZERO-LOSS MERGE ENGINE
L5 CANONICAL — WINDSURF Ω — 2025-12-07
MERKLE-INTENDED: ed54bc2a5b1899525e3ab9d8ee09a0bc8b5569eae38526b2970b2fb2587448c4
"""
# Retry operations for failed orchestration tasks

"""Simulation registry to look up simulator instances."""


from simulations.engines import (
    DraftSimulator,
    RAGSimulator,
    SafetySimulator,
    StrategySimulator,
)


SIMULATION_REGISTRY = {
    "strategy": StrategySimulator(),
    "rag": RAGSimulator(),
    "draft": DraftSimulator(),
    "safety": SafetySimulator(),
}


def get_simulator(name: str) -> any:
    """Return a simulator instance by name."""

    return SIMULATION_REGISTRY.get(name)