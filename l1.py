# FILE: l1.py
"""
Unified L1 Cognition Layer (v10_10) — COGNITIVE PLANNING (RESTORED)

This module implements the "Brain" of the agent. It is strictly
COGNITION-ONLY (Pillar 1).

Responsibilities:
    1. Analyze Context: Synthesize Job, Resume, and User Intent.
    2. Infer Strategy: Use LLM Gateway to determine seniority, tone, and focus.
    3. Generate Plans: Produce strict `PlanObject` contracts for L2/L3.
    4. Injection: Embed Framing, Safety, and Tooling profiles into plans.

Key Refactor (v10_10):
    • Removed heuristic/regex logic (hardcoded dictionaries).
    • Added `LLMGateway` integration for semantic planning.
    • strictly typed `PlanObject` outputs via Pydantic.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from models import (
    PlanObject,
    StrategyExecutionPayload,
    SelfCorrectionSurface,
    SafetyMode
)
from llm_gateway import GATEWAY
from meta_profile import (
    get_planning_bias,
    get_safety_bias,
    get_routing_bias
)

# =============================================================================
# 1. PLANNER ENGINE
# =============================================================================

class L1Planner:
    """
    The cognitive engine that converts intent into structured plans.
    """

    async def plan(
        self,
        mode: str,
        state: Dict[str, Any],
        workflow_id: str
    ) -> PlanObject:
        """
        Main entry point for all planning modes.
        """
        mode = mode.lower()
        
        # 1. Extract Context (Read-Only View)
        context = self._extract_context(state)
        
        # 2. Determine Meta-Biased Settings
        reasoning_strategy = self._determine_reasoning_strategy()
        complexity = self._estimate_complexity(context)

        # 3. Route to specific planner logic
        if mode == "strategy":
            return await self._plan_strategy(context, workflow_id, reasoning_strategy, complexity)
        elif mode == "rag":
            return await self._plan_rag(context, workflow_id, complexity)
        elif mode == "drafting":
            return await self._plan_drafting(context, workflow_id)
        elif mode == "qa":
            return await self._plan_qa(context, workflow_id)
        elif mode == "safety":
            return await self._plan_safety(context, workflow_id)
        
        # Fallback for simple modes
        return self._build_default_plan(mode, context)

    # =========================================================================
    # MODE-SPECIFIC PLANNERS
    # =========================================================================

    async def _plan_strategy(
        self, 
        context: Dict[str, Any], 
        workflow_id: str,
        strategy: str,
        complexity: str
    ) -> PlanObject:
        """
        Uses LLM to generate a multi-branch strategy.
        """
        # Pillar 6: Use LLM Gateway for reasoning
        response = await GATEWAY.call_model(
            prompt_id="l1_strategy_planner",
            inputs={
                "objective": context["objective"],
                "context_summary": context["summary_text"],
                "branch_count": 3 if complexity == "high" else 1
            },
            workflow_id=workflow_id,
            reasoning_strategy=strategy
        )

        # Parse JSON output (Simplified for v10_10 demo)
        # In prod, use Pydantic parser on response.content
        try:
            # We expect the LLM to return a JSON structure matching StrategyExecutionPayload
            # For resilience, we wrap this.
            plan_data = json.loads(response.content) if "{" in response.content else {}
        except:
            plan_data = {"branches": []}

        # Pillar 3: Typed Contract
        return PlanObject(
            mode="strategy",
            objective=context["objective"],
            workflow_id=workflow_id,
            steps=[
                {"id": "branch_generation", "desc": "Generate strategic options"},
                {"id": "branch_selection", "desc": "Select optimal path"}
            ],
            complexity=complexity,
            reasoning_strategy=strategy,
            # Pass explicit guidance to L2
            context_profile={"raw_plan": plan_data},
            surfaces=[SelfCorrectionSurface.STRATEGY_REPLAN]
        )

    async def _plan_rag(
        self, 
        context: Dict[str, Any], 
        workflow_id: str,
        complexity: str
    ) -> PlanObject:
        """
        Plans retrieval queries based on complexity.
        """
        routing = get_routing_bias()
        
        # Meta-aware query planning
        query_count = 5 if routing.get("prefer_robust_retrieval") else 3
        if complexity == "high":
            query_count += 2

        return PlanObject(
            mode="rag",
            objective=f"Retrieve {query_count} evidence items.",
            workflow_id=workflow_id,
            steps=[
                {"id": "query_generation", "count": query_count},
                {"id": "fusion", "method": "reciprocal_rank_fusion"}
            ],
            complexity=complexity,
            surfaces=[SelfCorrectionSurface.RAG_RETRY]
        )

    async def _plan_drafting(self, context: Dict[str, Any], workflow_id: str) -> PlanObject:
        return PlanObject(
            mode="drafting",
            objective="Draft content based on strategy and evidence.",
            workflow_id=workflow_id,
            steps=[{"id": "section_drafting"}],
            surfaces=[SelfCorrectionSurface.DRAFT_RETRY]
        )

    async def _plan_qa(self, context: Dict[str, Any], workflow_id: str) -> PlanObject:
        planning_bias = get_planning_bias()
        checks = ["completeness", "relevance"]
        
        if planning_bias.get("conservative"):
            checks.extend(["tone_consistency", "evidence_citation"])

        return PlanObject(
            mode="qa",
            objective="Validate artifacts against requirements.",
            workflow_id=workflow_id,
            context_profile={"required_checks": checks},
            surfaces=[SelfCorrectionSurface.QA_RECHECK]
        )

    async def _plan_safety(self, context: Dict[str, Any], workflow_id: str) -> PlanObject:
        safety_bias = get_safety_bias()
        mode = SafetyMode.STRICT if safety_bias.get("heightened_caution") else SafetyMode.BALANCED
        
        return PlanObject(
            mode="safety",
            objective="Review content for policy violations.",
            workflow_id=workflow_id,
            safety_profile={"mode": mode},
            surfaces=[SelfCorrectionSurface.SAFETY_RISK]
        )

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _extract_context(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize state inputs for the planner.
        """
        # Flatten job/resume/messages into a prompt-ready summary
        objective = state.get("objective", "Unknown Objective")
        messages = state.get("messages", [])
        last_msg = messages[-1].get("content") if messages else ""
        
        return {
            "objective": objective,
            "summary_text": f"User Request: {last_msg}\nObjective: {objective}",
            "job": state.get("job", {}),
            "resume": state.get("resume", {})
        }

    def _determine_reasoning_strategy(self) -> str:
        """
        Select CoT vs ToT based on Meta-Profile.
        """
        bias = get_planning_bias()
        if bias.get("conservative"):
            return "tot" # Tree of Thought for high stakes
        if bias.get("exploratory"):
            return "cot" # Chain of Thought for exploration
        return "direct"

    def _estimate_complexity(self, context: Dict[str, Any]) -> str:
        """
        Simple heuristic for complexity (can be upgraded to LLM classifier).
        """
        text_len = len(context.get("summary_text", ""))
        if text_len > 1000:
            return "high"
        if text_len > 200:
            return "moderate"
        return "low"

    def _build_default_plan(self, mode: str, context: Dict[str, Any]) -> PlanObject:
        return PlanObject(
            mode=mode,
            objective=context["objective"],
            steps=[{"id": "execute"}]
        )

# Singleton instance
PLANNER = L1Planner()
