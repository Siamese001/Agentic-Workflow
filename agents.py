# FILE: agents.py
"""
Unified Agent Coordination Module (v10_9) — FULL AGENTIC IMPLEMENTATION

This module provides all meta-agentic coordination used by v10_9:

SECTIONS:
    1. MultiAgent       – Parallel, round-robin, debate aggregation
    2. Ensemble         – Majority vote, weighted vote, consensus building
    3. SelfCorrection   – Heuristic critique + inconsistency checking
    4. HIL Interface    – Human-in-the-loop override simulation
    5. AgentRunner      – High-level L1→L3 helper for one-shot tasks

Layer boundary:
    • ABOVE L1–L5 (meta-level)
    • NO planning (L1)
    • NO model execution (L2)
    • NO orchestration (L3)
    • NO state mutation logic (L4)
    • NO safety decisions (L5)
"""

from __future__ import annotations
import asyncio
from typing import Any, Dict, List, Callable, Awaitable, Optional

from models import PlanObject
from l1 import route_plan
from l3 import Orchestrator


# ============================================================================
# 1. MULTI-AGENT COORDINATION
# ============================================================================

class MultiAgent:
    """
    Multi-agent coordination modes:
        • round_robin()
        • run_parallel()
        • debate_mode() — multi-output → merged
    """

    @staticmethod
    async def round_robin(
        state: Dict[str, Any],
        agents: List[Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]],
    ) -> List[Dict[str, Any]]:
        """
        Runs each agent sequentially on the same base state.
        Returns list of outputs.
        """
        outputs = []
        for agent in agents:
            try:
                outputs.append(await agent(dict(state)))
            except Exception as e:
                outputs.append({"error": str(e)})
        return outputs

    @staticmethod
    async def run_parallel(
        state: Dict[str, Any],
        agents: List[Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]],
    ) -> List[Dict[str, Any]]:
        """
        Runs all agents concurrently; gathers all results.
        """
        tasks = [agent(dict(state)) for agent in agents]
        return await asyncio.gather(*tasks, return_exceptions=False)

    @staticmethod
    async def debate_mode(
        state: Dict[str, Any],
        agents: List[Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]],
        merge_fn: Callable[[List[Dict[str, Any]]], Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Runs all agents in parallel and merges results via merge_fn().
        """
        outputs = await MultiAgent.run_parallel(state, agents)
        return merge_fn(outputs)

    @staticmethod
    def default_merge(results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Deterministic aggregation:
            - lists are extended
            - scalars override last-write-wins
        """
        merged: Dict[str, Any] = {}
        for res in results:
            for k, v in res.items():
                if isinstance(v, list):
                    merged.setdefault(k, []).extend(v)
                else:
                    merged[k] = v
        return merged


# ============================================================================
# 2. ENSEMBLE VOTING
# ============================================================================

class Ensemble:
    """
    Provides deterministic multi-agent voting utilities.
    """

    @staticmethod
    def majority_vote(items: List[str]) -> str:
        if not items:
            return ""
        counts: Dict[str, int] = {}
        for x in items:
            counts[x] = counts.get(x, 0) + 1
        return max(counts, key=counts.get)

    @staticmethod
    def weighted_vote(items: List[str], weights: List[float]) -> str:
        """
        Weighted voting for candidate options. 
        """
        if not items or not weights or len(items) != len(weights):
            return ""
        score: Dict[str, float] = {}
        for x, w in zip(items, weights):
            score[x] = score.get(x, 0) + w
        return max(score, key=score.get)

    @staticmethod
    def consensus(items: List[str]) -> str:
        """
        If unanimous → return that item.
        Else → return deterministic sorted join.
        """
        if not items:
            return ""
        if len(set(items)) == 1:
            return items[0]
        return " / ".join(sorted(set(items)))


# ============================================================================
# 3. SELF-CORRECTION ENGINE
# ============================================================================

class SelfCorrection:
    """
    Implements deterministic, rule-based critique and adjustment:

        • critique_output       – structural content heuristics
        • detect_inconsistency  – contradicting keywords
        • suggest_retry         – signals whether L2 should re-run
        • apply_corrections     – simple patch injection

    This avoids embedding unsafe generation in prompts, and provides
    predictable correction behavior.
    """

    @staticmethod
    def critique_output(text: str) -> Dict[str, Any]:
        issues = []

        stripped = text.strip()
        if len(stripped) < 30:
            issues.append("too_short")

        if "." not in stripped and "?" not in stripped:
            issues.append("no_sentence_structure")

        if stripped.lower().count("very") > 2:
            issues.append("repetitive_language")

        return {
            "passed": len(issues) == 0,
            "issues": issues,
        }

    @staticmethod
    def detect_inconsistency(text: str, reference: str) -> bool:
        """
        Simple contradiction detector using deterministic opposing keyword pairs.
        """
        if not reference:
            return False

        ref = set(reference.lower().split())
        txt = set(text.lower().split())

        contradictions = {
            ("experienced", "junior"),
            ("expert", "beginner"),
            ("leader", "assistant"),
        }

        for a, b in contradictions:
            if (a in txt and b in ref) or (b in txt and a in ref):
                return True

        return False

    @staticmethod
    def suggest_retry(crit: Dict[str, Any]) -> bool:
        """
        Retry L2 if structural issues (short / no sentences / repetitive language).
        """
        return not crit.get("passed", True)

    @staticmethod
    def apply_corrections(original: Dict[str, Any], critique: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply simple note-based corrections for downstream L2/L3 consumption.
        """
        corrected = dict(original)

        if "too_short" in critique.get("issues", []):
            corrected["note"] = corrected.get("note", "") + " Expanded for clarity."

        if "no_sentence_structure" in critique.get("issues", []):
            corrected["note"] = corrected.get("note", "") + " Added sentence punctuation."

        if "repetitive_language" in critique.get("issues", []):
            corrected["note"] = corrected.get("note", "") + " Reduced repetitive terms."

        return corrected


# ============================================================================
# 4. HUMAN-IN-THE-LOOP (HIL) INTERFACE
# ============================================================================

class HIL:
    """
    Provides deterministic simulation of Human-in-the-Loop overrides:

        • apply_overrides()
        • run_with_hil()

    This sits above L3 but below UI-level interactions.
    """

    @staticmethod
    def apply_overrides(state: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
        new_state = dict(state)
        for k, v in overrides.items():
            new_state[k] = v
        return new_state

    @staticmethod
    async def run_with_hil(
        initial_state: Dict[str, Any],
        overrides: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Executes a full L1→L3 cycle, then applies overrides (if any),
        then re-executes the pipeline.
        """
        # First pass
        plan1: PlanObject = route_plan(initial_state)
        orch1 = Orchestrator()
        first_state = (await orch1.run(plan1, initial_state)).state

        if not overrides:
            return first_state

        # Apply overrides
        updated = HIL.apply_overrides(first_state, overrides)

        # Re-run pipeline with updated state
        plan2: PlanObject = route_plan(updated)
        orch2 = Orchestrator()
        second_state = (await orch2.run(plan2, updated)).state

        return second_state


# ============================================================================
# 5. AGENT RUNNER — HIGH-LEVEL ENTRYPOINT
# ============================================================================

class AgentRunner:
    """
    Convenience API for executing a full L1→L3 agentic cycle or
    multi-step pipelines without requiring orchestrator setup.

    Use:
        AgentRunner.run_sync({"objective": "draft summary"})
    """

    @staticmethod
    async def run(state: Dict[str, Any]) -> Dict[str, Any]:
        plan = route_plan(state)
        orch = Orchestrator()
        result = await orch.run(plan, state)
        return dict(result.state)

    @staticmethod
    def run_sync(state: Dict[str, Any]) -> Dict[str, Any]:
        return asyncio.run(AgentRunner.run(state))
