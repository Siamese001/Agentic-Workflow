# FILE: 10_10/simulation.py
"""
Unified Simulation System (v10_10) — PURE META LAYER / CI HARNESS
=================================================================

This is the v10_10 refactor of the v10_9 simulation harness.

Key changes vs v10_9:
    • Calls main_v10_10.run_workflow_v10_10() instead of main_v10_9.
    • Operates on the v10_10 result shape:
          {
            "workflow_id": ...,
            "state_patch": {...},
            "safety_passed": bool,
            "corrected": bool,
            "l2_results": {
               "strategy": {...},
               "rag": {...},
               "drafting": {...},
               "qa": {...},
               "safety": {...}
            }
          }
    • Removes all references to:
          - WorkflowPhase
          - phase_history
          - run_summary
          - multi_agent / meta_learning / HIL-specific payloads

Strict Layer Boundaries:
    • NO L1 planning
    • NO L2 execution / cognition
    • NO L3 orchestration
    • NO L4 state mutation
    • NO L5 safety decisions
    • NO provider calls

This module is META-ONLY. It is safe to use in CI and regression tests.

Each scenario:
    • Builds an initial_state dict (v10_9-style).
    • Invokes run_workflow_v10_10(initial_state).
    • Returns:

        {
          "scenario": <name>,
          "workflow_id": <id>,
          "safety_passed": bool,
          "corrected": bool,
          "state_snapshot": {...},
          "l2_results": {...}    # trimmed for stability
        }
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, Callable, Awaitable

from main_v10_10 import run_workflow_v10_10


# ============================================================================
# 1. STATE SNAPSHOT HELPERS (v10_10)
# ============================================================================


def _state_snapshot(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build a stable, trimmed snapshot from a v10_10 workflow result.

    v10_10 result shape (from main_v10_10.run_workflow_v10_10):

        {
          "workflow_id": ...,
          "state_patch": {
             "strategy_text": ...,
             "rag_evidence": [...],
             "drafted_sections": [...],
             "qa_findings": [...],
             "safety_findings": [...],
             "correction_signals": [...],
             "safety_passed": bool
          },
          "safety_passed": bool,
          "corrected": bool,
          "l2_results": {
             "strategy": {...},
             "rag": {...},
             "drafting": {...},
             "qa": {...},
             "safety": {...}
          }
        }

    For CI, we keep only the state_patch and a trimmed view of the L2 results.
    """
    patch = result.get("state_patch") or {}
    l2 = result.get("l2_results") or {}

    return {
        # L4 patch (already trimmed by design)
        "state_patch": {
            "strategy_text": patch.get("strategy_text"),
            "rag_evidence": patch.get("rag_evidence"),
            "drafted_sections": patch.get("drafted_sections"),
            "qa_findings": patch.get("qa_findings"),
            "safety_findings": patch.get("safety_findings"),
            "correction_signals": patch.get("correction_signals"),
            "safety_passed": patch.get("safety_passed"),
        },
        # Minimal L2 view to allow regression checks
        "l2_results": {
            "strategy": l2.get("strategy"),
            "rag": l2.get("rag"),
            "drafting": l2.get("drafting"),
            "qa": l2.get("qa"),
            "safety": l2.get("safety"),
        },
    }


# ============================================================================
# 2. SCENARIO DEFINITIONS (v10_10)
# ============================================================================


class Scenarios:
    """
    Houses all simulation scenarios for deterministic CI testing (v10_10).

    Each scenario:
        • Builds an initial_state dict.
        • Invokes run_workflow_v10_10(initial_state).
        • Returns a high-level summary and a trimmed state snapshot.
    """

    # ----------------------------------------------------------------------
    # STRATEGY
    # ----------------------------------------------------------------------
    @staticmethod
    async def strategy() -> Dict[str, Any]:
        """
        Strategy planning scenario:
            - Exercises L1 strategy planning (via main bridge)
            - Exercises StrategyLLMAgent + full DAG
        """
        state: Dict[str, Any] = {
            "objective": "Create a high-level plan for improving my VP-level resume.",
            "messages": [
                {"role": "user", "content": "Help me plan my resume rewrite for a VP-level job."}
            ],
            "job_title": "Vice President, Product",
            "role_type": "product",
            "seniority": "VP",
            "requirements": [
                "executive leadership",
                "enterprise SaaS",
                "strategic partnerships",
            ],
        }

        result = await run_workflow_v10_10(
            state,
            compat_mode=None,
            debug_mode=False,
            stream_callback=None,
        )

        snapshot = _state_snapshot(result)

        return {
            "scenario": "strategy",
            "workflow_id": result.get("workflow_id"),
            "safety_passed": result.get("safety_passed"),
            "corrected": result.get("corrected"),
            "state_snapshot": snapshot,
        }

    # ----------------------------------------------------------------------
    # RAG
    # ----------------------------------------------------------------------
    @staticmethod
    async def rag() -> Dict[str, Any]:
        """
        Retrieval scenario:
            - Exercises RAG plan (queries from L1)
            - Exercises deterministic RAG + ranking in L2
        """
        state: Dict[str, Any] = {
            "objective": "Retrieve evidence for my leadership experience.",
            "messages": [
                {"role": "user", "content": "What evidence supports my leadership background?"}
            ],
            "job_title": "Engineering Manager",
            "role_type": "engineering",
            "seniority": "Manager",
            "requirements": ["leadership", "team scaling", "cloud"],
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

        result = await run_workflow_v10_10(
            state,
            compat_mode=None,
            debug_mode=False,
            stream_callback=None,
        )

        snapshot = _state_snapshot(result)

        return {
            "scenario": "rag",
            "workflow_id": result.get("workflow_id"),
            "safety_passed": result.get("safety_passed"),
            "corrected": result.get("corrected"),
            "state_snapshot": snapshot,
        }

    # ----------------------------------------------------------------------
    # DRAFTING
    # ----------------------------------------------------------------------
    @staticmethod
    async def drafting() -> Dict[str, Any]:
        """
        Drafting scenario:
            - Exercises drafting plan (sections/tone) via L1 bridge
            - Exercises DraftingGuild + full DAG
        """
        state: Dict[str, Any] = {
            "objective": "Draft a professional summary for a VP of Growth.",
            "messages": [
                {"role": "user", "content": "Draft my executive summary for a VP Growth role."}
            ],
            "job_title": "VP, Growth & Strategic Partnerships",
            "role_type": "growth",
            "seniority": "VP",
            "requirements": ["strategic partnerships", "M&A experience"],
            "resume": {
                "master_resume": {
                    "summary": "Enterprise leader driving AI and growth strategy.",
                    "professional_experience": [],
                }
            },
        }

        result = await run_workflow_v10_10(
            state,
            compat_mode=None,
            debug_mode=False,
            stream_callback=None,
        )

        snapshot = _state_snapshot(result)

        return {
            "scenario": "drafting",
            "workflow_id": result.get("workflow_id"),
            "safety_passed": result.get("safety_passed"),
            "corrected": result.get("corrected"),
            "state_snapshot": snapshot,
        }

    # ----------------------------------------------------------------------
    # QA
    # ----------------------------------------------------------------------
    @staticmethod
    async def qa() -> Dict[str, Any]:
        """
        QA scenario:
            - Exercises QA plan and SemanticQAAgent via full DAG.
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

        result = await run_workflow_v10_10(
            state,
            compat_mode=None,
            debug_mode=False,
            stream_callback=None,
        )

        snapshot = _state_snapshot(result)

        return {
            "scenario": "qa",
            "workflow_id": result.get("workflow_id"),
            "safety_passed": result.get("safety_passed"),
            "corrected": result.get("corrected"),
            "state_snapshot": snapshot,
        }

    # ----------------------------------------------------------------------
    # SAFETY
    # ----------------------------------------------------------------------
    @staticmethod
    async def safety() -> Dict[str, Any]:
        """
        Safety scenario:
            - Exercises SafetyPlan + ConstitutionalSafetyAgent + L5 gate.
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

        result = await run_workflow_v10_10(
            state,
            compat_mode=None,
            debug_mode=False,
            stream_callback=None,
        )

        snapshot = _state_snapshot(result)

        return {
            "scenario": "safety",
            "workflow_id": result.get("workflow_id"),
            "safety_passed": result.get("safety_passed"),
            "corrected": result.get("corrected"),
            "state_snapshot": snapshot,
        }


# ============================================================================
# 3. SIMULATION ENGINE
# ============================================================================

SCENARIOS: Dict[str, Callable[[], Awaitable[Dict[str, Any]]]] = {
    "strategy": Scenarios.strategy,
    "rag": Scenarios.rag,
    "drafting": Scenarios.drafting,
    "qa": Scenarios.qa,
    "safety": Scenarios.safety,
}


class Engine:
    """
    Simulation execution engine for v10_10.

    Provides:
        • run(name, overrides=None)
        • run_all()
        • list()
        • sync wrappers
    """

    @staticmethod
    async def run(name: str, overrides: Dict[str, Any] | None = None) -> Dict[str, Any]:
        if name not in SCENARIOS:
            raise ValueError(f"Unknown simulation scenario: {name!r}")
        base = await SCENARIOS[name]()
        if overrides:
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
        """
        Return mapping scenario_name → docstring (1-line description).
        """
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
    print("=== v10_10 Simulation Harness (META) ===")
    print("Available Scenarios:")
    for name, desc in Engine.list().items():
        print(f"  - {name}: {desc or '(no description)'}")

    print("\n=== Running All Scenarios ===")
    results = Engine.run_all_sync()

    for name, result in results.items():
        print(f"\n[SCENARIO: {name.upper()}]")
        print(f"Workflow ID : {result.get('workflow_id')}")
        print(f"Safety Pass : {result.get('safety_passed')}")
        print(f"Corrected   : {result.get('corrected')}")
        print("State Snapshot:")
        print(result.get("state_snapshot"))
