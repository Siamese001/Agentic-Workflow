# FILE: v10_9_clean/simulation_scenarios.py
"""
Simulation Scenarios (v10_9)

This module defines deterministic simulation scenarios for:
    • strategy
    • rag
    • bullets
    • drafting
    • qa
    • safety

Each scenario:
    1. Constructs a minimal synthetic initial state
    2. Executes full L1 → L3 workflow via run_workflow_v10_9
    3. Returns the final orchestration state for inspection

These can be used by:
    • simulation_engine.py
    • pytest tests/simulations
    • manual debugging
    • CI pipelines
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict

from main_v10_9 import run_workflow_v10_9


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _run(initial_state: Dict[str, Any]) -> Dict[str, Any]:
    """Wrapper to run a simulation state through the full v10_9 workflow."""
    return await run_workflow_v10_9(initial_state)


# ---------------------------------------------------------------------------
# Strategy Scenario
# ---------------------------------------------------------------------------

async def strategy_scenario() -> Dict[str, Any]:
    """
    Strategy simulation:
    Generates a top-level strategic decomposition and next actions.
    """
    state = {
        "objective": "create high-level plan for improving resume",
        "messages": [{"role": "user", "content": "Help me plan my resume rewrite."}],
    }
    return await _run(state)


# ---------------------------------------------------------------------------
# RAG Scenario
# ---------------------------------------------------------------------------

async def rag_scenario() -> Dict[str, Any]:
    """
    RAG simulation:
    Runs retrieval planning, execution, ranking, and fusion stubs.
    """
    state = {
        "objective": "retrieve evidence for leadership experience",
        "messages": [{"role": "user", "content": "What evidence supports my leadership roles?"}],
        "job": {"title": "Engineering Manager", "company": "TechCorp", "skills": ["leadership", "team management"]},
        "resume": {"master_resume": {"summary": "Led teams and improved efficiency.", "professional_experience": []}},
    }
    return await _run(state)


# ---------------------------------------------------------------------------
# Bullet Scenario
# ---------------------------------------------------------------------------

async def bullets_scenario() -> Dict[str, Any]:
    """
    Bullets simulation:
    Generates bullet points from experience signals.
    """
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
    return await _run(state)


# ---------------------------------------------------------------------------
# Draft Scenario
# ---------------------------------------------------------------------------

async def draft_scenario() -> Dict[str, Any]:
    """
    Draft simulation:
    Generates narrative/paragraph draft aligned to tone and audience.
    """
    state = {
        "objective": "draft a professional summary",
        "tone": "Professional",
        "audience": "general",
        "messages": [{"role": "user", "content": "Draft my summary."}],
    }
    return await _run(state)


# ---------------------------------------------------------------------------
# QA Scenario
# ---------------------------------------------------------------------------

async def qa_scenario() -> Dict[str, Any]:
    """
    QA simulation:
    Validates outputs logically and stylistically using deterministic rules.
    """
    state = {
        "objective": "qa validated content",
        "messages": [{"role": "user", "content": "Validate the quality of this text."}],
        "draft_result": {"draft": ["This is a well-structured sentence."]},
    }
    return await _run(state)


# ---------------------------------------------------------------------------
# Safety Scenario
# ---------------------------------------------------------------------------

async def safety_scenario() -> Dict[str, Any]:
    """
    Safety simulation:
    Runs sanitization + safety checks and returns violations if any.
    """
    state = {
        "objective": "safety check",
        "messages": [{"role": "user", "content": "Sanitize the content."}],
        "draft_result": {"draft": ["This includes explicit terms and adult content."]},
        "audience": "general"
    }
    return await _run(state)


# ---------------------------------------------------------------------------
# Scenario registry
# ---------------------------------------------------------------------------

SCENARIOS = {
    "strategy": strategy_scenario,
    "rag": rag_scenario,
    "bullets": bullets_scenario,
    "draft": draft_scenario,
    "qa": qa_scenario,
    "safety": safety_scenario,
}
