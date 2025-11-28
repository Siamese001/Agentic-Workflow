"""Simulation runner utilities."""

import asyncio
from typing import Any, Dict, List

from simulations.models import (
    DraftSimRequest,
    RAGSimRequest,
    SafetySimRequest,
    SimulationBatchResult,
    SimulationResult,
    StrategySimRequest,
)
from simulations.registry import get_simulator


REQUEST_MODEL_MAP = {
    "strategy": StrategySimRequest,
    "rag": RAGSimRequest,
    "draft": DraftSimRequest,
    "safety": SafetySimRequest,
}


async def run_simulation(sim_type: str, payload: Dict[str, Any]) -> SimulationResult:
    """Run a single simulation request."""

    simulator = get_simulator(sim_type)
    if not simulator:
        raise ValueError(f"Unknown simulation type: {sim_type}")
    request_model = REQUEST_MODEL_MAP.get(sim_type)
    if not request_model:
        raise ValueError(f"No request model registered for simulation type: {sim_type}")
    request = request_model(**payload)
    return await simulator.run(request)


async def run_batch(sim_requests: List[Dict[str, Any]]) -> SimulationBatchResult:
    """Run a batch of simulations sequentially."""

    results = []
    for req in sim_requests:
        sim_type = req.get("sim_type")
        payload = req.get("payload", {})
        if not sim_type:
            raise ValueError("Each batch request must include 'sim_type'")
        results.append(await run_simulation(sim_type, payload))
    return SimulationBatchResult(results=results)


def run_simulation_sync(sim_type: str, payload: Dict[str, Any]) -> SimulationResult:
    """Convenience synchronous wrapper."""

    return asyncio.run(run_simulation(sim_type, payload))
