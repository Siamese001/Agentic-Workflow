# FILE: simulation.py
"""
Unified Simulation System (v10_9) — DEVELOPER / CI HARNESS (FULL OVERWRITE)

This module provides a deterministic simulation harness for the v10_9
agentic workflow. It is NOT part of the production runtime and is intended
for:

    • Developer smoke tests
    • CI/automation sanity checks
    • Scenario-based regression testing

It exercises the full L1 → L5 stack via main_v10_9.run_workflow_v10_9.

Scenarios included:
    • strategy   – high-level strategy planning
    • rag        – retrieval (RAG) pipeline
    • bullets    – bullet generation from resume
    • drafting   – summary drafting
    • qa         – QA validation over a draft
    • safety     – safety/PII/forbidden content review

Each scenario returns a structured result:

    {
      "scenario": "<name>",
      "workflow_id": "...",
      "phase": "complete|failed|...",
      "phase_history": [...],
      "run_summary": {...},
      "state_snapshot": {...},   # trimmed, stable subset of state
    }
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, Callable, Awaitable

from main_v10_9 import run_workflow_v10_9


# ============================================================================
# SCENARIO DEFINITIONS
# ============================================================================

def _state_snapshot(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Trim the full state down to the core parts that are relevant for
    simulation output and stable enough to be compared in CI.

    We avoid returning the entire state to prevent noisy diffs.
    """
    return {
        "strategy_result": state.get("strategy_result"),
        "rag_result": state.get("rag_result"),
        "bullet_result": state.get("bullet_result"),
        "draft_result": state.get("draft_result"),
        "qa_result": state.get("qa_result"),
        "safety_result": state.get("safety_result"),
        "summary": state.get("summary"),
    }


class Scenarios:
    """
    Houses all simulation scenarios used for deterministic testing.
    """

    @staticmethod
    async def strategy() -> Dict[str, Any]:
        """
        Strategy simulation:
        - Objective: plan how to improve resume for a leadership role
        - Exercises: L1 StrategyReasoner, L2 StrategyExecutor, L3 Orchestrator
        """
        state = {
            "objective": "create high-level plan for improving resume for a VP role",
            "messages": [
                {"role": "user", "content": "Help me plan my resume rewrite for a VP-level job."}
            ],
            "job": {
                "job_title": "Vice President, Growth & Strategic Partnerships",
                "company": "Neo4j",
                "summary": "Executive role driving growth and partnerships.",
                "top_requirements": [
                    "strategic partnerships",
                    "M&A experience",
                    "enterprise SaaS",
                ],
            },
        }
        result = await run_workflow_v10_9(state)
        wf_state = result["state"]
        return {
            "scenario": "strategy",
            "workflow_id": result["workflow_id"],
            "phase": result["phase"],
            "phase_history": result["phase_metadata"].get("history", [result["phase"]]),
            "run_summary": result["run_summary"],
            "state_snapshot": _state_snapshot(wf_state),
        }

    @staticmethod
    async def rag() -> Dict[str, Any]:
        """
        RAG simulation:
        - Objective: retrieve evidence for leadership experience
        - Exercises: L1 RAGReasoner, L2 RAGExecutor, L3 Orchestrator
        """
        state = {
            "objective": "retrieve evidence for leadership experience at scale",
            "messages": [
                {"role": "user", "content": "What evidence from my resume supports my leadership roles?"}
            ],
            "job": {
                "job_title": "Engineering Manager",
                "company": "TechCorp",
                "skills": ["leadership", "team management", "cloud architecture"],
            },
            "resume": {
                "master_resume": {
                    "summary": "Led multiple engineering teams delivering cloud products.",
                    "professional_experience": [
                        {
                            "title": "Engineering Manager",
                            "company": "TechCorp",
                            "impact_summary": "Led a team of 10 engineers to deliver a SaaS platform.",
                        },
                        {
                            "title": "Tech Lead",
                            "company": "DataWorks",
                            "impact_summary": "Architected a data pipeline serving 50M events per day.",
                        },
                    ],
                }
            },
        }
        result = await run_workflow_v10_9(state)
        wf_state = result["state"]
        return {
            "scenario": "rag",
            "workflow_id": result["workflow_id"],
            "phase": result["phase"],
            "phase_history": result["phase_metadata"].get("history", [result["phase"]]),
            "run_summary": result["run_summary"],
            "state_snapshot": _state_snapshot(wf_state),
        }

    @staticmethod
    async def bullets() -> Dict[str, Any]:
        """
        Bullets simulation:
        - Objective: generate high-impact bullets from resume experience
        - Exercises: L1 BulletReasoner, L2 BulletExecutor, L3 Orchestrator
        """
        state = {
            "objective": "generate resume bullets",
            "messages": [
                {"role": "user", "content": "Generate bullets for my last two roles."}
            ],
            "resume": {
                "master_resume": {
                    "professional_experience": [
                        {
                            "title": "Chief AI Officer",
                            "company": "Unify Consulting",
                            "impact_summary": "Led AI practice and strategic partnerships.",
                            "bullet_pool": [
                                "Built LLM-based automation that reduced manual workflow by 40%.",
                                "Scaled AI consulting team from 5 to 18 engineers.",
                            ],
                        },
                        {
                            "title": "Lead Client Partner",
                            "company": "IBM",
                            "impact_summary": "Drove cloud and AI transformations for Fortune 500 clients.",
                            "bullet_pool": [
                                "Delivered $34M transformation via cloud risk analytics.",
                                "Standardized AI workflows for global banking clients.",
                            ],
                        },
                    ]
                }
            },
        }
        result = await run_workflow_v10_9(state)
        wf_state = result["state"]
        return {
            "scenario": "bullets",
            "workflow_id": result["workflow_id"],
            "phase": result["phase"],
            "phase_history": result["phase_metadata"].get("history", [result["phase"]]),
            "run_summary": result["run_summary"],
            "state_snapshot": _state_snapshot(wf_state),
        }

    @staticmethod
    async def drafting() -> Dict[str, Any]:
        """
        Drafting simulation:
        - Objective: draft a professional resume summary
        - Exercises: L1 DraftingReasoner, L2 DraftingExecutor, L3 Orchestrator
        """
        state = {
            "objective": "draft a professional summary",
            "tone": "Professional",
            "audience": "recruiter",
            "messages": [
                {"role": "user", "content": "Draft my executive summary for a VP growth role."}
            ],
            "job": {
                "job_title": "VP, Growth & Strategic Partnerships",
                "company": "Neo4j",
                "top_requirements": [
                    "strategic partnerships",
                    "M&A experience",
                    "graph database ecosystem",
                ],
            },
            "resume": {
                "master_resume": {
                    "summary": "AI and partnerships leader driving enterprise value at scale.",
                    "professional_experience": [],
                }
            },
        }
        result = await run_workflow_v10_9(state)
        wf_state = result["state"]
        return {
            "scenario": "drafting",
            "workflow_id": result["workflow_id"],
            "phase": result["phase"],
            "phase_history": result["phase_metadata"].get("history", [result["phase"]]),
            "run_summary": result["run_summary"],
            "state_snapshot": _state_snapshot(wf_state),
        }

    @staticmethod
    async def qa() -> Dict[str, Any]:
        """
        QA simulation:
        - Objective: run QA over an existing draft_result
        - Exercises: L1 QACoordinatorPlanner, L2 QAExecutor, L3 Orchestrator
        """
        state = {
            "objective": "qa validate content",
            "audience": "general",
            "messages": [
                {"role": "user", "content": "Validate the quality and structure of this draft."}
            ],
            "draft_result": {
                "draft": [
                    "This is a professionally written summary that is clear, concise, and aligned with the job requirements."
                ]
            },
        }
        result = await run_workflow_v10_9(state)
        wf_state = result["state"]
        return {
            "scenario": "qa",
            "workflow_id": result["workflow_id"],
            "phase": result["phase"],
            "phase_history": result["phase_metadata"].get("history", [result["phase"]]),
            "run_summary": result["run_summary"],
            "state_snapshot": _state_snapshot(wf_state),
        }

    @staticmethod
    async def safety() -> Dict[str, Any]:
        """
        Safety simulation:
        - Objective: run safety review over content with PII and forbidden terms
        - Exercises: L1 SafetyPlanner, L2 SafetyExecutor, L3 Orchestrator, L5 SafetyEngine/Policy/Arbitration
        """
        state = {
            "objective": "safety check",
            "audience": "general",
            "messages": [
                {"role": "user", "content": "Review this content for safety and PII issues."}
            ],
            "draft_result": {
                "draft": [
                    "Contact me at person@example.com for more explicit details!!!"
                ]
            },
        }
        result = await run_workflow_v10_9(state)
        wf_state = result["state"]
        return {
            "scenario": "safety",
            "workflow_id": result["workflow_id"],
            "phase": result["phase"],
            "phase_history": result["phase_metadata"].get("history", [result["phase"]]),
            "run_summary": result["run_summary"],
            "state_snapshot": _state_snapshot(wf_state),
        }


# Scenario registry
SCENARIOS: Dict[str, Callable[[], Awaitable[Dict[str, Any]]]] = {
    "strategy": Scenarios.strategy,
    "rag": Scenarios.rag,
    "bullets": Scenarios.bullets,
    "draft": Scenarios.drafting,
    "drafting": Scenarios.drafting,
    "qa": Scenarios.qa,
    "safety": Scenarios.safety,
}


# ============================================================================
#  SIMULATION ENGINE
# ============================================================================

class Engine:
    """
    Simulation execution engine.

    Provides:
        - run(name, overrides=None)
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
            # Shallow merge: override top-level keys in the result dict
            result = dict(base)
            result.update(overrides)
            return result
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
#  CLI SUPPORT
# ============================================================================

if __name__ == "__main__":
    print("=== v10_9 Simulation Harness ===\n")
    print("Available Scenarios:")
    for name, desc in Engine.list().items():
        print(f"  - {name}: {desc.strip() or '(no description)'}")

    print("\n=== Running All Scenarios ===")
    results = Engine.run_all_sync()

    for name, result in results.items():
        print(f"\n[{name.upper()} RESULT]")
        print(f"Workflow ID: {result.get('workflow_id')}")
        print(f"Phase      : {result.get('phase')}")
        print(f"Issues     : {result.get('run_summary', {}).get('issues', {})}")
        print("State Snapshot:")
        print(result.get("state_snapshot"))
