# FILE: simulation.py
"""
Unified Simulation System (v10_9) — ENTERPRISE / CI HARNESS (FULL OVERWRITE)

This module provides a deterministic simulation harness for the v10_9
agentic workflow. It is NOT part of the production runtime and is
intended for:

    • Developer smoke tests
    • CI/automation sanity checks
    • Scenario-based regression testing
    • Golden-state validation across L1–L5 and meta layers

It exercises the full stack via main_v10_9.run_workflow_v10_9.

Scenarios included:

    • strategy      – high-level job strategy planning
    • rag           – retrieval (RAG) pipeline
    • bullets       – bullet generation from resume
    • drafting      – summary drafting
    • qa            – QA validation of a draft
    • safety        – safety/PII/forbidden content review
    • hil           – human-in-the-loop review flow
    • meta_learning – offline meta-learning over synthetic prior results

Each scenario returns a structured result:

    {
      "scenario": "<name>",
      "workflow_id": "...",
      "phase": "complete|failed|...",
      "phase_history": [...],
      "run_summary": {...},
      "state_snapshot": {...},   # trimmed, stable subset of state
    }

All scenarios are fully deterministic (no external IO, no randomness)
to enable reliable regression testing.
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, Callable, Awaitable

from main_v10_9 import run_workflow_v10_9


# ============================================================================
# STATE SNAPSHOT HELPERS
# ============================================================================


def _state_snapshot(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Trim the full state down to the core parts that are relevant for
    simulation output and stable enough to be compared in CI.

    We avoid returning the entire state to prevent noisy diffs. Only
    include high-level result summaries and a small subset of metadata.
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
        "phase": state.get("phase"),
        "phase_history": (state.get("phase_metadata") or {}).get("history"),
        "summary": state.get("summary"),
    }


# ============================================================================
# SCENARIO DEFINITIONS
# ============================================================================


class Scenarios:
    """
    Houses all simulation scenarios used for deterministic testing.

    Each scenario constructs an initial_state dict and calls
    run_workflow_v10_9(initial_state). Scenarios are designed to:
        • Force a specific L1 task mode (via task_mode and objective).
        • Seed the minimal context required to exercise the pipeline.
    """

    @staticmethod
    async def strategy() -> Dict[str, Any]:
        """
        Strategy simulation:
        - task_mode: strategy
        - Objective: plan how to improve a resume for a leadership role
        - Exercises: L1 StrategyReasoner, L2 StrategyExecutor, L3 Orchestrator
        """
        state = {
            "task_mode": "strategy",
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
            "workflow_id": result["name"] if "name" in result else result["workflow_id"],
            "phase": result["phase"],
            "phase_history": result["phase_metadata"].get("history", [result["phase"]]),
            "run_summary": result["run_summary"],
            "state_snapshot": _ironed_out_state_snapshot(wf_state),
        }

    @staticmethod
    async def rag() -> Dict[str, Any]:
        """
        RAG simulation:
        - task_mode: rag
        - Objective: retrieve evidence for leadership experience
        - Exercises: L1 RAGReasoner, L2 RAGExecutor, L3 Orchestrator
        """
        state = {
            "task_mode": "rag",
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
            "state_snapshot": _ironed_out_state_snapshot(wf_state),
        }

    @staticmethod
    async def bullets() -> Dict[str, Any]:
        """
        Bullets simulation:
        - task_mode: strategy (to generate a strategy plan)
        - Uses existing resume; we mark objective to emphasize bullets
        - Exercises: L1 StrategyReasoner (with bullet focus), L2 BulletExecutor via
                     L3 orchestration path configured for bullets.
        Note: In this simple harness we still use the generic orchestrator,
        so the primary exercise is L1/L2 planning + execution.
        """
        state = {
            "task_mode": "strategy",  # Strategy -> BulletExecutor path via L3
            "objective": "generate high-impact resume bullets for my last two roles",
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
            "state_snapshot": _ironed_out_state_snapshot(wf_state),
        }

    @staticmethod
    async def drafting() -> Dict[str, Any]:
        """
        Drafting simulation:
        - task_mode: drafting
        - Objective: draft a professional summary
        - Exercises: L1 DraftingReasoner, L2 DraftingExecutor, L3 Orchestrator.
        """
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
            "state_snapshot": _ironed_out_state_snapshot(wf_state),
        }

    @staticmethod
    async def qa() -> Dict[str, Any]:
        """
        QA simulation:
        - task_mode: qa
        - Objective: run QA over an existing draft_result
        - Exercises: L1 QACoordinatorPlanner, L2 QAExecutor, L3 Orchestrator
        """
        state = {
            "task_mode": "qa",
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
            "state_snapshot": _ironed_out_state_snapshot(wf_state),
        }

    @staticmethod
    async def safety() -> Dict[str, Any]:
        """
        Safety simulation:
        - task_mode: safety
        - Objective: run safety review over content with PII and forbidden terms
        - Exercises: L1 SafetyPlanner, L2 SafetyExecutor, L3 Orchestrator, L5 SafetyEngine/Policy/Arbitration
        """
        state = {
            "task_mode": "safety",
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
            "state_snapshot": _ironed_out_state_snapshot(wf_state),
        }

    @staticmethod
    async def hil() -> Dict[str, Any]:
        """
        HIL (Human-in-the-loop) simulation:
        - task_mode: hil
        - Objective: perform a human review of a critical draft
        - Exercises: L1 HILPlanner, L2 HILExecutionPayload, L3 Orchestrator
        - Validates that the system can construct a HIL prompt and
          record a (placeholder) HIL response region.
        """
        state = {
            "task_mode": "hil",
            "objective": "perform hil review of high-impact executive summary",
            "messages": [
                {"role": "user", "content": "Please have a human review this final summary before sending."}
            ],
            "draft_result": {
                "draft": [
                    "This is a critical executive summary that will be sent to the board."
                ]
            },
            # Simulate a pre-existing QA result to give HIL some context.
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
            "phase_history": result["phase_metadata"].get("history", [result["phase"]]),
            "run_summary": result["run_summary"],
            "state_snapshot": _state_snapshot(wf_state),
        }

    @staticmethod
    async def meta_learning() -> Dict[str, Any]:
        """
        Meta-learning simulation:
        - task_mode: meta_learning
        - Objective: run offline meta-learning over pre-populated QA & Safety results.
        - Exercises: L1 MetaProfile/MetaPlanner, L2 meta-learning executor, L3 Orchestrator.
        - Seeds synthetic prior results into the initial state to simulate
          a post-hoc meta-learning pass.
        """
        state = {
            "task_mode": "meta_learning",
            "objective": "run meta learning over prior QA and Safety outcomes",
            "messages": [
                {"role": "system", "content": "Trigger a meta-learning pass over historical runs."}
            ],
            # Seed synthetic prior QA/Safety results to be consumed by the meta-learning planner.
            "qa_result": {
                "report": {
                    "issues": ["inconsistent_narrative", "missing_metric"],
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
            "Phase": result["phase"],
            "phase_history": result["phase_metadata"].get("history", [result["phase"]]),
            "run_summary": result["run_summary"],
            "state_snapshot": _state_snapshot(wf_state),
        }


# ============================================================================
#  SIMULATION ENGINE
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

    The Engine is purely a testing/diagnostics tool and does not
    participate in production orchestration.
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
        """Return a mapping of scenario_name -> short description (docstring)."""
        return {name: (fn.__doc__ or "").strip() for name, fn in SCENARIOS.items()}

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
    print("=== v10_9 Simulation Harness (Enterprise) ===\n")
    print("Available Scenarios:")
    for name, desc in Engine.list().items():
        print(f"  - {name}: {desc or '(no description)'}")

    print("\n=== Running All Scenarios ===")
    results = Engine.run_all_sync()

    for name, result in results.items():
        print(f"\n[{name.upper()} RESULT]")
        print(f"Workflow ID: {result.get('workflow_id')}")
        print(f"Phase      : {result.get('phase')}")
        print(f"Issues     : {result.get('run_summary', {}).get('issues', {})}")
        print("State Snapshot:")
        print(result.get("state_snapshot"))
