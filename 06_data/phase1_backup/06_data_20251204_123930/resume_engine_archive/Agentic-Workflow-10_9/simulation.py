# FILE: simulation.py
"""
Unified Simulation System (v10_9) — PURE META LAYER / CI HARNESS (REFINED)

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

Scenarios (deterministic, end-to-end):

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
      "workflow_id": <id>,
      "phase": <final phase>,
      "phase_history": [...],
      "run_summary": {...},
      "state_snapshot": {...},   # stable, trimmed L4 state
    }

All scenarios are safe for CI and regression tests.
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
    Trim the full L4 state to a stable subset suitable for deterministic testing.

    We purposely include only the main L2 outputs and a few key
    high-level fields. Volatile or heavy telemetry (e.g., route_trace,
    patch_log, correction_journal) is omitted from the snapshot.

    Snapshot shape:
        {
          "strategy_result": ...,
          "rag_result": ...,
          "bullet_result": ...,
          "draft_result": ...,
          "qa_result": ...,
          "safety_result": ...,
          "hil_result": ...,
          "meta_learning_result": ...,
          "multi_agent": ...,
          "self_correction": ...,
          "summary": ...,
        }
    """
    return {
        "strategy_result": state.get("strategy_result"),
        "rag_result": state.get("rag_history") or state.get("rag_result"),
        "bullet_result": state.get("bullet_result"),
        "draft_result": state.get("draft_result"),
        "qa_result": state.get("qa_result"),
        "safety_result": state.get("safety_result"),
        "hil_result": state.get("hil_result"),
        "meta_learning_result": state.get("meta_learning_result"),
        "multi_agent": state.get("multi_agent"),
        "self_correction": state.get("self_correction"),
        "summary": state.get("summary"),
    }


# ============================================================================
# 2. SCENARIO DEFINITIONS
# ============================================================================


class Scenarios:
    """
    Houses all simulation scenarios used for deterministic CI testing.

    Each scenario:
        • Builds an initial_state dict.
        • Invokes run_workflow_v10_9(initial_state).
        • Returns an object with top-level fields + trimmed state snapshot.
    """

    # ----------------------------------------------------------------------
    # STRATEGY
    # ----------------------------------------------------------------------
    @staticmethod
    async def strategy() -> Dict[str, Any]:
        """
        Strategy planning scenario:
            - Exercises L1 strategy planner
            - Ensures L2.StrategyExecutor + L3/L4 integration
        """
        state: Dict[str, Any] = {
            "objective": "Create a high-level plan for improving my VP-level resume.",
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
            "phase_history": result.get("phase_metadata", {}).get("history"),
            "run_summary": result.get("run_summary", {}),
            "state_snapshot": _state_snapshot(wf_state),
        }

    # ----------------------------------------------------------------------
    # RAG
    # ----------------------------------------------------------------------
    @staticmethod
    async def rag() -> Dict[str, Any]:
        """
        Retrieval scenario:
            - Exercises L1 RAG planning (multi-query)
            - Exercises L2.RAGExecutor + retrieval/ranking/RAGUtils
        """
        state: Dict[str, Any] = {
            "objective": "Retrieve evidence for my leadership experience.",
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
                            "impact_summary": "Led a team of 10 delivering multi-region SaaS.",
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
            "phase_history": result.get("phase_metadata", {}).get("history"),
            "run_summary": result.get("run_summary", {}),
            "state_snapshot": _state_snapshot(wf_state),
        }

    # ----------------------------------------------------------------------
    # BULLETS
    # ----------------------------------------------------------------------
    @staticmethod
    async def bullets() -> Dict[str, Any]:
        """
        Bullet-generation scenario:
            - Exercises L1 bullet framework planning
            - Exercises L2.BulletExecutor + RAG interactions (via state)
        """
        state: Dict[str, Any] = {
            "objective": "Generate high-impact bullets for my last two roles.",
            "messages": [
                {"role": "user", "content": "Create resume bullets for my past leadership roles."}
            ],
            "resume": {
                "master_resume": {
                    "summary": "Senior leader with multi-role leadership experience.",
                    "professional_experience": [
                        {
                            "title": "Chief AI Officer",
                            "company": "Unify Consulting",
                            "impact_summary": "Led AI practice & GTM partnerships.",
                            "bullet_pool": [
                                "Built AI automation reducing costs 40%.",
                                "Scaled AI practice from 5 to 20 engineers.",
                            ],
                        },
                        {
                            "title": "Lead Client Partner",
                            "company": "IBM",
                            "impact_summary": "Drove cloud/AI transformations.",
                            "bullet_pool": [
                                "Delivered $30M analytics transformation.",
                                "Standardized global AI workflows across 5 regions.",
                            ],
                        },
                    ],
                }
            },
        }

        result = await run_workflow_v10_9(state)
        wf_state = result["state"]

        return {
            "scenario": "bullets",
            "workflow_id": result["workflow_id"],
            "phase": result["phase"],
            "phase_history": result.get("phase_metadata", {}).get("history"),
            "run_summary": result.get("run_summary", {}),
            "state_snapshot": _state_snapshot(wf_state),
        }

    # ----------------------------------------------------------------------
    # DRAFTING
    # ----------------------------------------------------------------------
    @staticmethod
    async def drafting() -> Dict[str, Any]:
        """
        Drafting scenario:
            - Exercises L1 drafting planning (sections/tone)
            - Exercises L2.DraftingExecutor + RAG evidence usage
        """
        state: Dict[str, Any] = {
            "objective": "Draft a professional summary for a VP of Growth.",
            "tone": "professional",
            "audience": "recruiter",
            "messages": [
                {"role": "user", "content": "Draft my executive summary for a VP Growth role."}
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
            "phase_history": result.get("phase_metadata", {}).get("history"),
            "run_summary": result.get("run_summary", {}),
            "state_snapshot": _state_snapshot(wf_state),
        }

    # ----------------------------------------------------------------------
    # QA
    # ----------------------------------------------------------------------
    @staticmethod
    async def qa() -> Dict[str, Any]:
        """
        QA scenario:
            - Exercises L1 QA planning (checks, hints)
            - Exercises L2.QAExecutor over a simple content block
        """
        state: Dict[str, Any] = {
            "objective": "Validate the quality of a drafted summary.",
            "messages": [
                {"role": "user", "content": "Validate the quality of this content."}
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
            "phase_history": result.get("phase_metadata", {}).get("history"),
            "run_summary": result.get("run_summary", {}),
            "state_snapshot": _state_snapshot(wf_state),
        }

    # ----------------------------------------------------------------------
    # SAFETY
    # ----------------------------------------------------------------------
    @staticmethod
    async def safety() -> Dict[str, Any]:
        """
        Safety scenario:
            - Exercises L1 safety planning
            - Exercises L2.SafetyExecutor and L5.SafetyEngine
        """
        state: Dict[str, Any] = {
            "objective": "Safety check content that contains PII.",
            "messages": [
                {"role": "user", "content": "Please review this for safety issues."}
            ],
            "draft_result": {
                "draft": [
                    "Contact me at person@example.com or +1-555-123-4567 for details."
                ]
            },
        }

        result = await run_workflow_v10_9(state)
        wf_state = result["state"]

        return {
            "scenario": "safety",
            "workflow_id": result["workflow_id"],
            "phase": result["phase"],
            "phase_history": result.get("phase_metadata", {}).get("history"),
            "run_summary": result.get("run_summary", {}),
            "state_snapshot": _state_snapshot(wf_state),
        }

    # ----------------------------------------------------------------------
    # HIL
    # ----------------------------------------------------------------------
    @staticmethod
    async def hil() -> Dict[str, Any]:
        """
        HIL scenario:
            - Exercises HIL planning + L2.HILExecutor
            - Ensures HIL prompts and responses are wired correctly
        """
        state: Dict[str, Any] = {
            "objective": "Perform a human review of critical content.",
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
                    "issues": ["tone_mismatch", "missing_metric"],
                    "passed": False,
                }
            },
        }

        result = await run_workflow_v10_9(state)
        wf_state = result["state"]

        return {
            "scenario": "hil",
            "workflow_id": result["workflow_id"],
            "phase": result["phase"],
            "phase_history": result.get("phase_metadata", {}).get("history"),
            "run_summary": result.get("run_summary", {}),
            "state_snapshot": _state_snapshot(wf_state),
        }

    # ----------------------------------------------------------------------
    # META-LEARNING
    # ----------------------------------------------------------------------
    @staticmethod
    async def meta_learning() -> Dict[str, Any]:
        """
        Meta-learning scenario:
            - Exercises L1 meta-learning planning
            - Exercises L2.MetaLearningExecutor and state snapshot wiring
        """
        state: Dict[str, Any] = {
            "objective": "Analyze recent QA + Safety outcomes for meta-learning.",
            "messages": [
                {"role": "system", "content": "Trigger a meta-learning pass over recent runs."}
            ],
            "qa_result": {
                "report": {
                    "issues": ["inconsistent_narrative", "weak_evidence_linkage"],
                    "passed": False,
                }
            },
            "safety_result": {
                "report": {
                    "issues": [
                        {"issue_id": "pii_redacted", "category": "pii", "message": "Found email address."}
                    ],
                    "blocked": False,
                }
            },
        }

        result = await run_workflow_v10_9(state)
        wf_state = result["state"]

        return {
            "scenario": "meta_learning",
            "workflow_id": result["workflow_id"],
            "phase": result["phase"],
            "phase_history": result.get("phase_metadata", {}).get("history"),
            "run_summary": result.get("run_summary", {}),
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
        • run(name, overrides=None)
        • run_all()
        • list()
        • sync wrappers

    This is a META-level test harness for CI and regression scenarios.
    """

    @staticmethod
    async def run(name: str, overrides: Dict[str, Any] | None = None) -> Dict[str, Any]:
        if name not in SCENARIOS:
            raise ValueError(f"Unknown simulation scenario: {name!r}")
        base = await SCENARIOS[name]()
        if overrides:
            # Non-destructive merge: overrides only top-level keys of the result.
            merged = dict(base)
            merged.update(overrides)
            return merged
        return base

    @staticmethod
    async def run_all() -> Dict[str, Dict[str, Any]]:
        results: Dict[str, Dict[str, Any]] = {}
        for name, fn in SCENARIOS.items():
            results[name] = await fn()
        return results

    @staticmethod
    def list() -> Dict[str, str]:
        """Return a mapping of scenario_name → docstring (1-line description)."""
        return {name: (fn.__doc__ or "").strip() for name, fn in SCENARIOS.items()}

    @staticmethod
    def run_sync(name: str, overrides: Dict[str, Any] | None = None) -> Dict[str, Any]:
        return asyncio.run(Engine.run(name, overrides))

    @staticmethod
    def run_all_sync() -> Dict[str, Dict[str, Any]]:
        return asyncio.run(Engine.run_all())


# ============================================================================
# 4. CLI ENTRYPOINT
# ============================================================================

if __name__ == "__main__":
    print("=== v10_9 Simulation Harness (META) ===")
    print("Available Scenarios:")
    for name, desc in Engine.list().items():
        print(f"  - {name}: {desc or '(no description)'}")

    print("\n=== Running All Scenarios ===")
    results = Engine.run_all_sync()

    for name, result in results.items():
        print(f"\n[SCENARIO: {name.upper()}]")
        print(f"Workflow ID: {result.get('workflow_id')}")
        print(f"Phase      : {result.get('phase')}")
        print(f"Phase Hist.: {result.get('phase_history')}")
        print(f"Issues     : {result.get('run_summary', {}).get('issues', {})}")
        print("State Snapshot:")
        print(result.get("state_snapshot"))
