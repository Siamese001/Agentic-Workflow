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


def get_simulator(name: str):
    """Return a simulator instance by name."""

    return SIMULATION_REGISTRY.get(name)
