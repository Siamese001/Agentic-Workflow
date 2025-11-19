# FILE: simulation.py
"""
Unified Simulation System (v10_9) — PURE META LAYER / CI HARNESS

This module provides a deterministic simulation harness for the v10_9
agentic workflow.

All logic here is META-ONLY and therefore:

    • NO planning (L1)
    • NO execution (L2)
    • NO orchestration (L3)
    • NO state mutation (L4)
    • NO safety decisions (L5)
    • NO provider calls (Anthropic/Gemini/OpenAI/etc.)

It ONLY calls:
    • main_v10_9.run_workflow_v10_9()
    • constructs synthetic initial states
    • returns structured results for CI/regression testing.

Scenarios:
    • strategy
    • rag
    • bullets
    • drafting
    • qa
    • safety
    • hil
    • meta_learning

Each scenario returns:

    {
      "scenario": <name>,
      "workflow_id": ...,
      "phase": ...,
      "phase_history": [...],
      "run_summary": {...},
      "state_snapshot": {...},
    }

All scenarios are deterministic and safe for CI.
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, Callable, Awaitable

from main_v10_9 import run_workflow_v10_9


# ============================================================================
# 1. STATE SNAPSHOT HELPERS
# ============================================================================

def _state_snapshot(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Trim the full state to a stable subset suitable for deterministic testing.

    Includes:
        • strategy_result
        • rag_result
        • bullet_result
        • draft_result
        • qa_result
        • safety_result
        • hil_result
        • meta_learning_result
        • summary
        • phase
        • phase_history

    Excludes volatile fields (telemetry, multi_agent, etc.)
    """
    return {
        "strategy_result": state.get("strategy_result"),
        "rag_result": state.get("rag_result"),
        "bullet_result": state.get("bullet_result"),
        "draft_result": state.get("draft_result"),
        "qa_result": state.get("qa_result"),
        "safety_result": state.get("safety_result"),
        "hil_result": state.get("hil_result"),
        "meta_learning_result": state.get("meta_learning_result"),
        "summary": state.get("summary"),
        "phase": state.get("phase"),
        "phase_history": (state.get("phase_metadata") or {}).get("history"),
    }


# ============================================================================
# 2. SCENARIO DEFINITIONS
# ============================================================================

class Scenarios:
    """
    Houses all simulation scenarios used for deterministic CI testing.

    Each scenario:
        • Builds an initial state dict
        • Calls run_workflow_v10_9(initial_state)
        • Extracts a stable snapshot via _state_snapshot()
    """

    # ----------------------------------------------------------------------
    # STRATEGY
    # ----------------------------------------------------------------------
    @staticmethod
    async def strategy() -> Dict[str, Any]:
        state = {
            "task_mode": "strategy",
            "objective": "create high-level plan for improving resume for a VP role",
            "messages": [
                {"role": "user", "content": "Help me plan my resume rewrite for a VP-level job."}
            ],
            "job": {
                "job_title": "Vice President, Product",
                "company": "AcmeCorp",
                "summary": "Executive leadership role driving product strategy.",
                "top_requirements": [
                    "leadership",
                    "enterprise SaaS",
                    "strategic partnerships",
                ],
            },
        }

        result = await run_workflow_v10_9(state)
        wf_state = result["state"]

        return {
            "scenario": "strategy",
            "workflow_id": result["workflow_id"],
            "phase": result["phase"],
            "phase_history": result["phase_metadata"].get("history"),
            "run_summary": result["run_summary"],
            "state_snapshot": _state_snapshot(wf_state),
        }

    # ----------------------------------------------------------------------
    # RAG
    # ----------------------------------------------------------------------
    @staticmethod
    async def rag() -> Dict[str, Any]:
        state = {
            "task_mode": "rag",
            "objective": "retrieve evidence for leadership experience",
            "messages": [
                {"role": "user", "content": "What evidence supports my leadership background?"}
            ],
            "job": {
                "job_title": "Engineering Manager",
                "company": "TechCorp",
                "skills": ["leadership", "team scaling", "cloud"],
            },
            "resume": {
                "master_resume": {
                    "summary": "Led teams building cloud-native systems.",
                    "professional_experience": [
                        {
                            "title": "Engineering Manager",
                            "company": "TechCorp",
                            "impact_summary": "Led team of 10 delivering multi-region SaaS.",
                        },
                        {
                            "title": "Tech Lead",
                            "company": "DataWorks",
                            "impact_summary": "Architected real-time data platform.",
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
            "phase_history": result["phase_metadata"].get("history"),
            "run_summary": result["run_summary"],
            "state_snapshot": _state_snapshot(wf_state),
        }

    # ----------------------------------------------------------------------
    # BULLETS
    # ----------------------------------------------------------------------
    @staticmethod
    async def bullets() -> Dict[str, Any]:
        state = {
            "task_mode": "strategy",  # Bullet planning is folded into drafting strategy
            "objective": "generate high-impact bullets for my last two roles",
            "messages": [
                {"role": "user", "content": "Create resume bullets for my past leadership roles."}
            ],
            "resume": {
                "master_resume": {
                    "professional_experience": [
                        {
                            "title": "Chief AI Officer",
                            "company": "Unify Consulting",
                            "impact_summary": "Led AI practice & GTM partnerships.",
                            "bullet_pool": [
                                "Built AI automation reducing costs 40%.",
                                "Scaled AI team from 5 to 20 engineers.",
                            ],
                        },
                        {
                            "title": "Lead Client Partner",
                            "company": "IBM",
                            "impact_summary": "Drove cloud/AI transformations.",
                            "bullet_pool": [
                                "Delivered $30M analytics transformation.",
                                "Standardized global AI workflows.",
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
            "phase_history": result["phase_metadata"].get("history"),
            "run_summary": result["run_summary"],
            "state_snapshot": _state_snapshot(wf_state),
        }

    # ----------------------------------------------------------------------
    # DRAFTING
    # ----------------------------------------------------------------------
    @staticmethod
    async def drafting() -> Dict[str, Any]:
        state = {
            "task_mode": "drafting",
            "objective": "draft a professional summary",
            "tone": "Professional",
            "audience": "recruiter",
            "messages": [
                {"role": "user", "content": "Draft my executive summary for a VP growth role."}
            ],
            "job": {
                "job_title": "VP, Growth & Strategic Partnerships",
                "company": "Neo4j",
                "top_requirements": ["strategic partnerships", "M&A experience"],
            },
            "resume": {
                "master_resume": {
                    "summary": "Enterprise leader driving AI and growth strategy.",
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
            "phase_history": result["phase_metadata"].get("history"),
            "run_summary": result["run_summary"],
            "state_snapshot": _state_snapshot(wf_state),
        }

    # ----------------------------------------------------------------------
    # QA
    # ----------------------------------------------------------------------
    @staticmethod
    async def qa() -> Dict[str, Any]:
        state = {
            "task_mode": "qa",
            "objective": "qa validate content",
            "audience": "general",
            "messages": [
                {"role": "user", "content": "Validate quality of this content."}
            ],
            "draft_result": {
                "draft": [
                    "This is a polished summary aligned with job requirements."
                ]
            },
        }

        result = await run_workflow_v10_9(state)
        wf_state = result["state"]

        return {
            "scenario": "qa",
            "workflow_id": result["workflow_id"],
            "phase": result["phase"],
            "phase_history": result["phase_metadata"].get("history"),
            "run_summary": result["run_summary"],
            "state_snapshot": _state_snapshot(wf_state),
        }

    # ----------------------------------------------------------------------
    # SAFETY
    # ----------------------------------------------------------------------
    @staticmethod
    async def safety() -> Dict[str, Any]:
        state = {
            "task_mode": "safety",
            "objective": "safety check",
            "audience": "general",
            "messages": [
                {"role": "user", "content": "Review this content for safety issues."}
            ],
            "draft_result": {
                "draft": [
                    "Contact me at person@example.com for more details!"
                ]
            },
        }

        result = await run_workflow_v10_9(state)
        wf_state = result["state"]

        return {
            "scenario": "safety",
            "workflow_id": result["workflow_id"],
            "phase": result["phase"],
            "phase_history": result["phase_metadata"].get("history"),
            "run_summary": result["run_summary"],
            "state_snapshot": _state_snapshot(wf_state),
        }

    # ----------------------------------------------------------------------
    # HIL
    # ----------------------------------------------------------------------
    @staticmethod
    async def hil() -> Dict[str, Any]:
        state = {
            "task_mode": "hil",
            "objective": "perform hil review",
            "messages": [
                {"role": "user", "content": "Please have a human review this before sending."}
            ],
            "draft_result": {
                "draft": [
                    "This is a critical executive summary that will be sent to the board."
                ]
            },
            "qa_result": {
                "report": {
                    "issues": ["tone_mismatch", "missing_metric"]
                }
            },
        }

        result = await run_workflow_v10_9(state)
        wf_state = result["state"]

        return {
            "scenario": "hil",
            "workflow_id": result["workflow_id"],
            "phase": result["phase"],
            "phase_history": result["phase_metadata"].get("history"),
            "run_summary": result["run_summary"],
            "state_snapshot": _state_snapshot(wf_state),
        }

    # ----------------------------------------------------------------------
    # META-LEARNING
    # ----------------------------------------------------------------------
    @staticmethod
    async def meta_learning() -> Dict[str, Any]:
        state = {
            "task_mode": "meta_learning",
            "objective": "run meta learning over prior QA & Safety results",
            "messages": [
                {"role": "system", "content": "Trigger a meta-learning pass."}
            ],
            "qa_result": {
                "report": {
                    "issues": ["inconsistent_narrative"],
                    "passed": False,
                }
            },
            "safety_result": {
                "report": {
                    "issues": ["pii_redacted", "forbidden:explicit"],
                    "passed": False,
                }
            },
        }

        result = await run_workflow_v10_9(state)
        wf_state = result["state"]

        return {
            "scenario": "meta_learning",
            "workflow_id": result["workflow_id"],
            "phase": result["phase"],
            "phase_history": result["phase_metadata"].get("history"),
            "run_summary": result["run_summary"],
            "state_snapshot": _state_snapshot(wf_state),
        }


# ============================================================================
# 3. SIMULATION ENGINE
# ============================================================================

SCENARIOS: Dict[str, Callable[[], Awaitable[Dict[str, Any]]]] = {
    "strategy": Scenarios.strategy,
    "rag": Scenarios.rag,
    "bullets": Scenarios.bullets,
    "draft": Scenarios.drafting,
    "drafting": Scenarios.drafting,
    "qa": Scenarios.qa,
    "safety": Scenarios.safety,
    "hil": Scenarios.hil,
    "meta_learning": Scenarios.meta_learning,
}


class Engine:
    """
    Simulation execution engine.

    Provides:
        - run(name, overrides=None)
        - run_all()
        - list()
        - sync wrappers

    The Engine is purely a meta-level toolkit for CI or smoke testing.
    """

    @staticmethod
    async def run(name: str, overrides: Dict[str, Any] | None = None) -> Dict[str, Any]:
        if name not in SCENARIOS:
            raise ValueError(f"Unknown simulation scenario: {name}")

        base = await SCENARIOS[name]()
        if overrides:
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
        """Mapping of scenario → docstring (1-line description)."""
        return {name: (fn.__doc__ or "").strip() for name, fn in SCENARIOS.items()}

    @staticmethod
    def run_sync(name: str, overrides: Dict[str, Any] | None = None) -> Dict[str, Any]:
        return asyncio.run(Engine.run(name, overrides))

    @staticmethod
    def run_all_sync() -> Dict[str, Dict[str, Any]]:
        return asyncio.run(Engine.run_all())


# ============================================================================
# 4. CLI SUPPORT
# ============================================================================

if __name__ == "__main__":
    print("=== v10_9 Simulation Harness ===")
    print("Available Scenarios:")
    for name, desc in Engine.list().items():
        print(f"  - {name}: {desc or '(no description)'}")

    print("\n=== Running All Scenarios ===")
    results = Engine.run_all_sync()

    for name, result in results.items():
        print(f"\n[{name.upper()}]")
        print(f"Workflow ID: {result.get('workflow_id')}")
        print(f"Phase      : {result.get('phase')}")
        print(f"Issues     : {result.get('run_summary', {}).get('issues', {})}")
        print("State Snapshot:")
        print(result.get("state_snapshot"))
