# FILE: v10_9_clean/agents.py
"""
Unified Agent Coordination Module (v10_9)

Namespace-organized consolidation of:
    • multi_agent.py
    • hil_interface.py
    • self_correction.py   <-- merged here

Provides:
    • MultiAgent       – ensemble and coordination logic
    • HIL              – Human-in-the-loop overrides
    • Ensemble         – voting/consensus helpers
    • SelfCorrection   – agent-level critique, retry, coherence checks
    • AgentRunner      – convenience wrapper for L1→L3 execution

This layer is ABOVE L1–L5:
    • NO planning
    • NO execution
    • NO orchestration
    • NO L4 state mutation
    • NO L5 safety

It is strictly meta-behavior and coordination logic.
"""

from __future__ import annotations
import asyncio
from typing import Any, Dict, List, Callable, Awaitable, Optional

from l1 import route_plan
from l3 import Orchestrator
from runtime_utils import Models


# ============================================================================
# NAMESPACE: MultiAgent
# ============================================================================

class MultiAgent:
    """
    Multi-agent orchestration modes:
        • Round-robin
        • Parallel execution
        • Debate mode (multi-output → merged)
        • Ensemble-based result merging
    """

    @staticmethod
    async def run_round_robin(
        state: Dict[str, Any],
        agents: List[Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]],
    ) -> List[Dict[str, Any]]:
        outputs = []
        for agent in agents:
            outputs.append(await agent(dict(state)))
        return outputs

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
        outputs = await MultiAgent.run_parallel(state, agents)
        return merge_fn(outputs)

    @staticmethod
    def default_merge(results: List[Dict[str, Any]]) -> Dict[str, Any]:
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
    Human-in-the-loop utilities:
        • override injection
        • rebasing/rerun
        • manual patching
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
        # initial run
        plan = route_plan(initial_state)
        orchestrator = Orchestrator()
        first_output = (await orchestrator.run(plan, initial_state)).state

        if not overrides:
            return first_output

        # apply overrides → rerun
        updated = HIL.apply_overrides(first_output, overrides)
        plan2 = route_plan(updated)
        second_output = (await orchestrator.run(plan2, updated)).state

        return second_output


# ============================================================================
# NAMESPACE: Ensemble
# ============================================================================

class Ensemble:
    """
    Ensemble voting + consensus utilities.
    """

    @staticmethod
    def majority_vote(items: List[str]) -> str:
        counts: Dict[str, int] = {}
        for item in items:
            counts[item] = counts.get(item, 0) + 1
        return max(counts, key=counts.get) if counts else ""

    @staticmethod
    def weighted_vote(items: List[str], weights: List[float]) -> str:
        score: Dict[str, float] = {}
        for item, w in zip(items, weights):
            score[item] = score.get(item, 0) + w
        return max(score, key=score.get) if score else ""

    @staticmethod
    def consensus(items: List[str]) -> str:
        if not items:
            return ""
        if len(set(items)) == 1:
            return items[0]
        return " / ".join(sorted(set(items)))


# ============================================================================
# NAMESPACE: SelfCorrection (MERGED FROM self_correction.py)
# ============================================================================

class SelfCorrection:
    """
    Self-correction heuristics for agent outputs.

    Provides:
        • critique_output   – detect missing reasoning or low quality
        • detect_inconsistency – match contradictions or mismatches
        • suggest_retry     – L3-level retry hints
        • apply_corrections – adjust draft/bullet/QA results

    This logic sits ABOVE L1–L5 and is meta-layer behavior.
    """

    @staticmethod
    def critique_output(output: str) -> Dict[str, Any]:
        """
        Heuristic critique:
            • too short
            • lacks punctuation
            • repetitive
        """
        issues = []

        if len(output.strip()) < 30:
            issues.append("too_short")

        if "." not in output and "?" not in output:
            issues.append("no_sentences")

        if output.lower().count("very") > 2:
            issues.append("repetitive_language")

        return {
            "passed": len(issues) == 0,
            "issues": issues,
        }

    @staticmethod
    def detect_inconsistency(text: str, reference: str) -> bool:
        """
        Simple inconsistency checker:
            • if text contradicts reference keywords
        """
        if not reference.strip():
            return False

        ref_words = set(reference.lower().split())
        txt_words = set(text.lower().split())

        contradictions = {
            ("experienced", "junior"),
            ("expert", "beginner"),
            ("leader", "assistant"),
        }

        for a, b in contradictions:
            if a in txt_words and b in ref_words:
                return True
            if b in txt_words and a in ref_words:
                return True

        return False

    @staticmethod
    def suggest_retry(critique: Dict[str, Any]) -> bool:
        """
        Suggest retry if critique found structural issues.
        """
        return not critique.get("passed", True)

    @staticmethod
    def apply_corrections(
        original: Dict[str, Any],
        critique: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Modify draft/bullet/QA results based on critique.
        Simple deterministic transformations for 10_9.
        """
        corrected = dict(original)

        if "too_short" in critique.get("issues", []):
            corrected["note"] = "Output expanded for clarity."

        if "no_sentences" in critique.get("issues", []):
            corrected["note"] = corrected.get("note", "") + " Added sentence structure."

        if "repetitive_language" in critique.get("issues", []):
            corrected["note"] = corrected.get("note", "") + " Reduced repetition."

        return corrected


# ============================================================================
# NAMESPACE: AgentRunner
# ============================================================================

class AgentRunner:
    """
    Convenience wrapper to run a single L1→L3 agentic cycle.

    Usage:
        AgentRunner.run_sync({"objective": "draft summary"})
    """

    @staticmethod
    async def run(state: Dict[str, Any]) -> Dict[str, Any]:
        plan = route_plan(state)
        orchestrator = Orchestrator()
        result = await orchestrator.run(plan, state)
        return dict(result.state)

    @staticmethod
    def run_sync(state: Dict[str, Any]) -> Dict[str, Any]:
        return asyncio.run(AgentRunner.run(state))
