# FILE: v10_9_clean/simulation_engine.py
"""
Simulation Engine (v10_9)

This engine provides a clean, minimal simulation subsystem for test frameworks.

It supports:
    • running named simulation scenarios
    • printing deterministic results
    • async + sync execution
    • integration with run_workflow_v10_9
    • pytest-compatible design (tests/simulations)

Scenarios are defined in:
    simulation_scenarios.py

This file contains:
    • run_simulation(name, overrides)
    • list_simulations()
    • run_all_simulations()
    • CLI-style sync wrapper
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, Callable, Awaitable

from simulation_scenarios import SCENARIOS  # registry of scenario_name -> coroutine


# ---------------------------------------------------------------------------
# Scenario execution
# ---------------------------------------------------------------------------

async def run_simulation(
    scenario_name: str,
    overrides: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Run a single simulation scenario by name.

    Args:
        scenario_name: registered name of the scenario to execute
        overrides: optional dict to override parts of the scenario's base state

    Returns:
        dict: final state after executing the scenario
    """
    if scenario_name not in SCENARIOS:
        raise ValueError(f"Unknown simulation scenario: {scenario_name}")

    base_fn = SCENARIOS[scenario_name]
    base_state = await base_fn()

    if overrides:
        base_state.update(overrides)

    return base_state


# ---------------------------------------------------------------------------
# Bulk execution helpers
# ---------------------------------------------------------------------------

def list_simulations() -> Dict[str, str]:
    """
    Return a dict of all available scenarios.
    Useful for UI, CLI, or debugging.
    """
    return {name: fn.__doc__ or "" for name, fn in SCENARIOS.items()}


async def run_all_simulations() -> Dict[str, Dict[str, Any]]:
    """
    Run all registered simulations and return results keyed by name.
    Designed for pytest / CI pipelines.
    """
    results: Dict[str, Dict[str, Any]] = {}

    for name, fn in SCENARIOS.items():
        base_state = await fn()
        results[name] = base_state

    return results


# ---------------------------------------------------------------------------
# Sync wrapper
# ---------------------------------------------------------------------------

def run_simulation_sync(
    scenario_name: str,
    overrides: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Synchronous wrapper around run_simulation()."""
    return asyncio.run(run_simulation(scenario_name, overrides))


def run_all_simulations_sync() -> Dict[str, Dict[str, Any]]:
    """Synchronous wrapper around run_all_simulations()."""
    return asyncio.run(run_all_simulations())


# ---------------------------------------------------------------------------
# Optional CLI runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Print available simulations
    print("=== Available Simulations ===")
    for name, desc in list_simulations().items():
        print(f"- {name}: {desc.strip()}")

    print("\n=== Running All Simulations ===")
    out = run_all_simulations_sync()
    for name, result in out.items():
        print(f"\n[{name} RESULT]")
        print(result)
