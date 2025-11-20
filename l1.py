# FILE: l1.py
"""
Unified L1 Cognition Layer (v10_10) — COGNITIVE DIRECTOR

This module implements Pillar 1 (Layering Model).
It is responsible for determining "What to do" (Planning) but not "How to do it" (Execution).

Responsibilities:
    1. Context Synthesis: Aggregates Job, Resume, and User Messages.
    2. Agent Delegation: Tasks `StrategyLLMAgent` with complex reasoning.
    3. Contract Generation: Outputs strict `PlanObject` models for L3.

Refactor Highlights (v10_10):
    • Uses `cognitive_agents.py` instead of raw Gateway calls.
    • Removes heuristic logic; relies on Semantic Planning.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List

from models import (
    PlanObject, 
    PlanStep, 
    ReasoningStrategy,
    SelfCorrectionSurface
)
from cognitive_agents import StrategyLLMAgent
from meta_profile import get_planning_bias, get_routing_bias

# =============================================================================
# PLANNER ENGINE
# =============================================================================

class L1Planner:
    """
    The architect of the workflow.
    Converts Intent -> Plan.
    """

    def __init__(self):
        # The Specialist Agent for Planning
        self.strategy_agent = StrategyLLMAgent()

    async def plan(
        self,
        mode: str,
        state: Dict[str, Any],
        workflow_id: str
    ) -> PlanObject:
        """
        Main entry point. Routes to specific planning logic based on mode.
        """
        mode = mode.lower()
        context = self._extract_context(state)
        
        # Apply Meta-Biases (Pillar 5)
        complexity = self._determine_complexity(context)
        reasoning_strat = self._determine_reasoning(complexity)

        if mode == "strategy":
            return await self._plan_strategy(context, workflow_id, complexity, reasoning_strat)
        
        elif mode == "rag":
            return self._plan_rag(context, workflow_id, complexity)
        
        elif mode == "drafting":
            return self._plan_drafting(context, workflow_id)
        
        elif mode == "qa":
            return self._plan_qa(context, workflow_id)
        
        elif mode == "safety":
            return self._plan_safety(context, workflow_id)

        # Fallback
        return self._build_default_plan(mode, context["objective"], workflow_id)

    # =========================================================================
    # MODE-SPECIFIC LOGIC
    # =========================================================================

    async def _plan_strategy(
        self, 
        context: Dict[str, Any], 
        workflow_id: str,
        complexity: str,
        strategy: ReasoningStrategy
    ) -> PlanObject:
        """
        Uses the StrategyLLMAgent to generate a semantic plan.
        """
        # Delegate Cognition to the Agent (Pillar 2)
        # The Agent handles the ToT prompt, Gateway routing, and Parsing.
        payload = await self.strategy_agent.generate_plan(
            objective=context["objective"],
            context=context["summary_text"],
            complexity=complexity
        )

        # Convert the Agent's payload into a Workflow Plan
        # The PlanObject instructs L3/L2 on what to execute next.
        return PlanObject(
            workflow_id=workflow_id,
            objective=context["objective"],
            mode="strategy",
            complexity=complexity,
            reasoning_strategy=strategy,
            steps=[
                PlanStep(
                    step_id="execute_strategy", 
                    description="Execute the selected strategic branch",
                    config={"selected_branch": payload.selected_branch_id}
                )
            ],
            # Pass the agent's reasoning trace to the context for downstream L2s
            context_pointers={"strategy_rationale": payload.reasoning_trace}
        )

    def _plan_rag(self, context: Dict[str, Any], wid: str, complexity: str) -> PlanObject:
        """
        Deterministic RAG planning based on routing bias.
        """
        routing = get_routing_bias()
        
        # If "Robust Retrieval" is biased on, we double the query count
        count = 5 if routing.get("prefer_robust_retrieval") else 3
        
        return PlanObject(
            workflow_id=wid,
            objective=context["objective"],
            mode="rag",
            complexity=complexity,
            reasoning_strategy=ReasoningStrategy.DIRECT,
            steps=[
                PlanStep(step_id="query_gen", description=f"Generate {count} queries", config={"count": count}),
                PlanStep(step_id="retrieval", description="Execute search and fusion")
            ]
        )

    def _plan_drafting(self, context: Dict[str, Any], wid: str) -> PlanObject:
        return PlanObject(
            workflow_id=wid,
            objective=context["objective"],
            mode="drafting",
            complexity="medium",
            reasoning_strategy=ReasoningStrategy.COT, # Drafting benefits from CoT
            steps=[
                PlanStep(step_id="draft_section", description="Draft content based on strategy")
            ]
        )

    def _plan_qa(self, context: Dict[str, Any], wid: str) -> PlanObject:
        planning_bias = get_planning_bias()
        
        # If conservative, we might add a "Cross-Check" step
        steps = [PlanStep(step_id="semantic_review", description="Check accuracy against evidence")]
        
        if planning_bias.get("conservative"):
            steps.append(PlanStep(step_id="tone_check", description="Verify professional tone"))

        return PlanObject(
            workflow_id=wid,
            objective="Validate content quality",
            mode="qa",
            complexity="high",
            reasoning_strategy=ReasoningStrategy.REFLEXION, # QA is self-reflective
            steps=steps
        )

    def _plan_safety(self, context: Dict[str, Any], wid: str) -> PlanObject:
        return PlanObject(
            workflow_id=wid,
            objective="Ensure policy compliance",
            mode="safety",
            complexity="high",
            reasoning_strategy=ReasoningStrategy.DIRECT,
            steps=[PlanStep(step_id="constitutional_check", description="Evaluate against safety policy")]
        )

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _extract_context(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize state into a prompt-ready summary."""
        objective = state.get("objective", "Unknown Objective")
        
        # Simple flattening of history
        msgs = state.get("messages", [])
        last_user_msg = next((m["content"] for m in reversed(msgs) if m.get("role") == "user"), "")
        
        return {
            "objective": objective,
            "summary_text": f"User Request: {last_user_msg}\nGlobal Objective: {objective}",
        }

    def _determine_complexity(self, context: Dict[str, Any]) -> str:
        """Heuristic complexity estimator."""
        if len(context["summary_text"]) > 500:
            return "high"
        return "medium"

    def _determine_reasoning(self, complexity: str) -> ReasoningStrategy:
        """Selects strategy based on complexity and bias."""
        bias = get_planning_bias()
        
        if bias.get("conservative") or complexity == "high":
            return ReasoningStrategy.TOT
        if bias.get("exploratory"):
            return ReasoningStrategy.COT
        return ReasoningStrategy.DIRECT

    def _build_default_plan(self, mode: str, obj: str, wid: str) -> PlanObject:
        return PlanObject(
            workflow_id=wid,
            objective=obj,
            mode=mode,
            complexity="low",
            reasoning_strategy=ReasoningStrategy.DIRECT,
            steps=[PlanStep(step_id="default_execute", description="Execute standard logic")]
        )

# Singleton
PLANNER = L1Planner()
