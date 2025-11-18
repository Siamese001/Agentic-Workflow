# FILE: v10_9_clean/simulation.py
"""
Unified Simulation System (v10_9)

Namespace-organized consolidation of ALL simulation logic:

    • Engine     – orchestrates scenario execution
    • Scenarios  – synthetic L1→L3 test workflows
    • Registry   – maps scenario names to scenario coroutines
    • CLI        – allows running all scenarios from command line

This replaces:
    simulation_engine.py
    simulation_scenarios.py

Pure test/dev utilities:
    • NOT part of runtime
    • Integrates with main_v10_9 via run_workflow_v10_9
"""

from __future__ import annotations
import asyncio
from typing import Any, Dict, Callable, Awaitable

from main_v10_9 import run_workflow_v10_9


# ============================================================================
# SCENARIO DEFINITIONS
# ============================================================================

class Scenarios:
    """
    Houses all simulation scenarios used for synthetic, deterministic testing.
    """

    @staticmethod
    async def strategy() -> Dict[str, Any]:
        """Strategy simulation."""
        state = {
            "objective": "create high-level plan for improving resume",
            "messages": [{"role": "user", "content": "Help me plan my resume rewrite."}],
        }
        return await run_workflow_v10_9(state)

    @staticmethod
    async def rag() -> Dict[str, Any]:
        """RAG simulation."""
        state = {
            "objective": "retrieve evidence for leadership experience",
            "messages": [{"role": "user", "content": "What evidence supports my leadership roles?"}],
            "job": {"title": "Engineering Manager", "company": "TechCorp", "skills": ["leadership", "team management"]},
            "resume": {"master_resume": {"summary": "Led teams.", "professional_experience": []}},
        }
        return await run_workflow_v10_9(state)

    @staticmethod
    async def bullets() -> Dict[str, Any]:
        """Bullets simulation."""
        state = {
            "objective": "generate resume bullets",
            "messages": [{"role": "user", "content": "Make bullets for my last job."}],
            "resume": {
                "master_resume": {
                    "professional_experience": [
                        {"title": "Manager", "company": "ABC Corp", "impact_summary": "Increased sales by 20%."}
                    ]
                }
            },
        }
        return await run_workflow_v10_9(state)

    @staticmethod
    async def draft() -> Dict[str, Any]:
        """Draft simulation."""
        state = {
            "objective": "draft a professional summary",
            "tone": "Professional",
            "audience": "general",
            "messages": [{"role": "user", "content": "Draft my summary."}],
        }
        return await run_workflow_v10_9(state)

    @staticmethod
    async def qa() -> Dict[str, Any]:
        """QA simulation."""
        state = {
            "objective": "qa validated content",
            "messages": [{"role": "user", "content": "Validate the quality of this text."}],
            "draft_result": {"draft": ["This is a clean, logically structured sentence."]},
        }
        return await run_workflow_v10_9(state)

    @staticmethod
    async def safety() -> Dict[str, Any]:
        """Safety simulation."""
        state = {
            "objective": "safety check",
            "messages": [{"role": "user", "content": "Sanitize the content."}],
            "draft_result": {"draft": ["This contains explicit adult language."]},
            "audience": "general",
        }
        return await run_workflow_v10_9(state)


# Scenario registry
SCENARIOS: Dict[str, Callable[[], Awaitable[Dict[str, Any]]]] = {
    "strategy": Scenarios.strategy,
    "rag": Scenarios.rag,
    "bullets": Scenarios.bullets,
    "draft": Scenarios.draft,
    "qa": Scenarios.qa,
    "safety": Scenarios.safety,
}


# ============================================================================
# SIMULATION ENGINE
# ============================================================================

class Engine:
    """
    Simulation execution engine.
    Provides:
        - run(name)
        - run_all()
        - list()
        - sync wrappers
    """

    @staticmethod
    async def run(name: str, overrides: Dict[str, Any] | None = None) -> Dict[str, Any]:
        if name not in SCENARIOS:
            raise ValueError(f"Unknown simulation scenario: {name}")
        base = await SCENARIOS[name]()
        if overrides:
            base.update(overrides)
        return base

    @staticmethod
    async def run_all() -> Dict[str, Dict[str, Any]]:
        results: Dict[str, Dict[str, Any]] = {}
        for name, fn in SCENARIOS.items():
            results[name] = await fn()
        return results

    @staticmethod
    def list() -> Dict[str, str]:
        return {name: fn.__doc__ or "" for name, fn in SCENARIOS.items()}

    @staticmethod
    def run_sync(name: str, overrides: Dict[str, Any] | None = None) -> Dict[str, Any]:
        return asyncio.run(Engine.run(name, overrides))

    @staticmethod
    def run_all_sync() -> Dict[str, Dict[str, Any]]:
        return asyncio.run(Engine.run_all())


# ============================================================================
# OPTIONAL CLI SUPPORT
# ============================================================================

if __name__ == "__main__":
    print("=== Available Simulations ===")
    for name, desc in Engine.list().items():
        print(f"- {name}: {desc.strip()}")

    print("\n=== Running All Simulations ===")
    output = Engine.run_all_sync()
    for name, result in output.items():
        print(f"\n[{name.upper()} RESULT]")
        print(result)
