# FILE: v10_9_clean/agents.py
"""
Unified Agent Coordination Module (v10_9)

Namespace-organized consolidation of:
    • multi_agent.py
    • hil_interface.py

Provides:
    • MultiAgent orchestration (ensemble voting, parallel runs, debate mode)
    • Human-In-The-Loop (HIL) overrides
    • Agent collaboration utilities
    • Result merging utilities
    • Deterministic fallback logic

Pure coordination layer:
    • NO planning (L1)
    • NO execution (L2)
    • NO orchestration (L3)
    • NO state mutation (L4)
    • NO safety/policy enforcement (L5)

This file is optional and not required for core runtime.
"""

from __future__ import annotations
import asyncio
from typing import Any, Dict, List, Callable, Optional

from l1 import route_plan
from l3 import Orchestrator
from runtime_utils import Models


# ============================================================================
# NAMESPACE: MultiAgent
# ============================================================================

class MultiAgent:
    """
    Provides multi-agent orchestration modes:
        • Round-robin
        • Parallel execution
        • Debate-style (multi-output → merge)
        • Ensemble voting for next actions

    Agents are defined as async callables:
        state → ExecutionResult payloads → merged output
    """

    @staticmethod
    async def run_round_robin(
        state: Dict[str, Any],
        agents: List[Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]],
    ) -> List[Dict[str, Any]]:
        results = []
        for agent in agents:
            results.append(await agent(dict(state)))
        return results

    @staticmethod
    async def run_parallel(
        state: Dict[str, Any],
        agents: List[Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]],
    ) -> List[Dict[str, Any]]:
        tasks = [agent(dict(state)) for agent in agents]
        return await asyncio.gather(*tasks)

    @staticmethod
    async def debate_mode(
        state: Dict[str, Any],
        agents: List[Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]],
        merge_fn: Callable[[List[Dict[str, Any]]], Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Agents produce independent outputs → merged by merge_fn
        """
        outputs = await MultiAgent.run_parallel(state, agents)
        return merge_fn(outputs)

    @staticmethod
    def default_merge(results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Simple deterministic merge:
            • merges all keys
            • last non-null value wins
            • aggregates lists
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
# NAMESPACE: HIL (Human-In-The-Loop)
# ============================================================================

class HIL:
    """
    Provides Human-in-the-Loop override handling:
        • manual patch injection
        • override-based reruns
        • user confirmation
        • return-to-orchestrator hooks
    """

    @staticmethod
    def apply_overrides(state: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
        """
        Shallow state override used when user provides corrections.
        """
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
        Run workflow once, apply overrides if provided, rerun if needed.
        """
        state = dict(initial_state)

        # Initial run
        plan = route_plan(state)
        orchestrator = Orchestrator()
        result_state = (await orchestrator.run(plan, state)).state

        if not overrides:
            return result_state

        # Apply overrides → rerun
        updated_state = HIL.apply_overrides(result_state, overrides)
        plan2 = route_plan(updated_state)
        result_state_2 = (await orchestrator.run(plan2, updated_state)).state

        return result_state_2


# ============================================================================
# NAMESPACE: Ensemble
# ============================================================================

class Ensemble:
    """
    Provides ensemble reasoning (majority vote, weighted vote, consensus).

    Useful for:
        • multi-agent drafting
        • multi-agent bullet generation
        • multi-agent QA
        • arbitration-style validation
    """

    @staticmethod
    def majority_vote(items: List[str]) -> str:
        counts: Dict[str, int] = {}
        for i in items:
            counts[i] = counts.get(i, 0) + 1
        return max(counts, key=counts.get) if counts else ""

    @staticmethod
    def weighted_vote(items: List[str], weights: List[float]) -> str:
        score: Dict[str, float] = {}
        for item, w in zip(items, weights):
            score[item] = score.get(item, 0.0) + w
        return max(score, key=score.get) if score else ""

    @staticmethod
    def consensus(items: List[str]) -> str:
        """
        Return a unified consensus string.
        """
        if not items:
            return ""
        if len(set(items)) == 1:
            return items[0]
        return " / ".join(sorted(set(items)))


# ============================================================================
# NAMESPACE: AgentRunner (Simple L1→L3 wrapper)
# ============================================================================

class AgentRunner:
    """
    Convenience API:
        AgentRunner.run(state)
    Runs:
        • L1: plan routing
        • L3: orchestrator execution
    """

    @staticmethod
    async def run(state: Dict[str, Any]) -> Dict[str, Any]:
        plan = route_plan(state)
        orchestrator = Orchestrator()
        out = await orchestrator.run(plan, state)
        return dict(out.state)

    @staticmethod
    def run_sync(state: Dict[str, Any]) -> Dict[str, Any]:
        return asyncio.run(AgentRunner.run(state))
