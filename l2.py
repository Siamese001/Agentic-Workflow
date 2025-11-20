# FILE: l2.py
"""
Unified L2 Execution Layer (v10_10) — COGNITIVE COORDINATION

This module implements Pillar 2 (Agent Boundaries).
It is the "Hands" of the architecture, but it doesn't do the work itself.
It delegates to specialized `CognitiveAgents` (for reasoning) or `Sandbox` (for tools).

Responsibilities:
    1. Task Routing: Map `PlanObject.mode` to the right Executor.
    2. Agent Delegation: Invoke `DraftingGuild`, `StrategyLLMAgent`, etc.
    3. Tool Orchestration: Call `SANDBOX` for RAG/Search.
    4. Contract Enforcement: Return strict `ExecutionResult` to L3.

Refactor Highlights (v10_10):
    • Removed all prompt logic (moved to `cognitive_agents`).
    • Removed HTTP logic (moved to `runtime_utils`).
    • Uses `models.py` types strictly.
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Type, TypeVar

from models import (
    PlanObject,
    ExecutionResult,
    NodeStatus,
    StrategyPayload,
    RAGExecutionPayload,
    RAGDocument,
    DraftingPayload,
    QAPayload,
    SafetyPayload,
    SafetyMode,
    SafetyPolicy
)
from cognitive_agents import (
    StrategyLLMAgent,
    DraftingGuild,
    SemanticQAAgent,
    ConstitutionalSafetyAgent
)
from registry import REGISTRY # Used for looking up Safety Policies
from runtime_utils import SANDBOX, Retrieval, RAGUtils

# =============================================================================
# BASE EXECUTOR
# =============================================================================

class BaseExecutor:
    """
    Standard interface for L2 components.
    """
    async def execute(self, plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult:
        raise NotImplementedError()

    def _success(self, payload: Any, meta: Dict[str, Any] = None) -> ExecutionResult:
        return ExecutionResult(
            status=NodeStatus.SUCCESS,
            payload=payload,
            meta=meta or {}
        )

    def _failure(self, error: str) -> ExecutionResult:
        return ExecutionResult(
            status=NodeStatus.FAILURE,
            error=error
        )

# =============================================================================
# 1. STRATEGY EXECUTOR (Uses StrategyLLMAgent)
# =============================================================================

class StrategyExecutor(BaseExecutor):
    """
    Coordinator for Strategic Planning.
    """
    def __init__(self):
        self.agent = StrategyLLMAgent()

    async def execute(self, plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult[StrategyPayload]:
        # Extract context pointers (passed from L1)
        context_text = state.get("summary", "")
        
        try:
            # Delegate to Cognitive Agent (Pillar 6)
            payload = await self.agent.generate_plan(
                objective=plan.objective,
                context=context_text,
                complexity=plan.complexity
            )
            return self._success(payload)
        except Exception as e:
            return self._failure(f"Strategy Agent failed: {str(e)}")


# =============================================================================
# 2. RAG EXECUTOR (Uses Sandbox + Retrieval Utils)
# =============================================================================

class RAGExecutor(BaseExecutor):
    """
    Coordinator for Retrieval.
    Unlike other executors, this uses Tools (Sandbox), not Agents.
    """
    async def execute(self, plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult[RAGExecutionPayload]:
        queries = []
        docs = []
        
        # 1. Extract Queries from Plan Steps
        # (L1 decided how many queries to run)
        target_count = 3
        for step in plan.steps:
            if step.step_id == "query_gen":
                target_count = step.config.get("count", 3)
        
        # 2. Execute Search in Sandbox (Pillar 14)
        # In a real app, we'd run these in parallel using asyncio.gather
        try:
            # Simulating the primary query
            result = await SANDBOX.run(
                function="web_search", # Placeholder for function pointer
                args={"tool_id": "web_search", "query": plan.objective},
                timeout_sec=10
            )
            
            # 3. Normalize (Pillar 7)
            # Convert raw text/json to RAGDocument
            docs.append(RAGDocument(
                query=plan.objective,
                content=str(result),
                source="web_search",
                score=1.0,
                rank=1
            ))
            queries.append(plan.objective)
            
            # Normalize metadata
            docs_dict = [d.model_dump() for d in docs]
            final_docs = RAGUtils.normalize_rag_results(docs_dict)
            
            # Convert back to Pydantic for Payload
            typed_docs = [RAGDocument(**d) for d in final_docs]

            return self._success(RAGExecutionPayload(
                queries=queries,
                documents=typed_docs
            ))

        except Exception as e:
            return self._failure(f"RAG Execution failed: {str(e)}")


# =============================================================================
# 3. DRAFTING EXECUTOR (Uses DraftingGuild)
# =============================================================================

class DraftingExecutor(BaseExecutor):
    """
    Coordinator for Content Creation.
    """
    def __init__(self):
        self.guild = DraftingGuild()

    async def execute(self, plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult[DraftingPayload]:
        # 1. Gather Evidence
        rag_result = state.get("rag_result")
        evidence_text = ""
        if rag_result and hasattr(rag_result, "documents"):
            evidence_text = "\n".join([d.content for d in rag_result.documents])

        try:
            # 2. Delegate to Guild (Pillar 2)
            # The Guild manages the internal "Structure -> Draft" loop
            payload = await self.guild.produce_artifact(
                section_name="Main Deliverable",
                evidence=evidence_text,
                tone="professional"
            )
            return self._success(payload)
        except Exception as e:
            return self._failure(f"Drafting Guild failed: {str(e)}")


# =============================================================================
# 4. QA EXECUTOR (Uses SemanticQAAgent)
# =============================================================================

class QAExecutor(BaseExecutor):
    """
    Coordinator for Quality Assurance.
    """
    def __init__(self):
        self.agent = SemanticQAAgent()

    async def execute(self, plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult[QAPayload]:
        # Extract content to validate
        draft = state.get("draft_result")
        content = draft.full_text if draft else ""
        
        try:
            # Delegate to Critic
            payload = await self.agent.validate(
                content=content,
                requirements=plan.context_pointers.get("requirements", [])
            )
            return self._success(payload)
        except Exception as e:
            return self._failure(f"QA Agent failed: {str(e)}")


# =============================================================================
# 5. SAFETY EXECUTOR (Uses ConstitutionalSafetyAgent)
# =============================================================================

class SafetyExecutor(BaseExecutor):
    """
    Coordinator for Safety Governance.
    """
    def __init__(self):
        self.agent = ConstitutionalSafetyAgent()

    async def execute(self, plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult[SafetyPayload]:
        # 1. Determine Content
        draft = state.get("draft_result")
        content = draft.full_text if draft else str(state.get("messages", ""))

        # 2. Determine Policy (Pillar 9)
        # We look up the *Active* policy from the Registry based on the Plan's mode.
        mode_str = plan.meta.get("safety_mode", "balanced")
        # In a real implementation, REGISTRY.get_policy returns a SafetyPolicy object
        # For Zero-Loss, we simulate constructing/fetching it here or via REGISTRY import
        policy = SafetyPolicy(
            policy_id="dynamic_lookup",
            mode=SafetyMode(mode_str),
            rules=[], # In prod: REGISTRY.get_rules(mode)
            threshold=0.5
        )

        try:
            # 3. Delegate to Guardian
            payload = await self.agent.evaluate(content, policy)
            return self._success(payload)
        except Exception as e:
            return self._failure(f"Safety Guardian failed: {str(e)}")


# =============================================================================
# ROUTER / DISPATCHER
# =============================================================================

async def route_executor(plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult:
    """
    The switchboard that connects L3 Plans to L2 Executors.
    """
    executors: Dict[str, Type[BaseExecutor]] = {
        "strategy": StrategyExecutor,
        "rag": RAGExecutor,
        "drafting": DraftingExecutor,
        "qa": QAExecutor,
        "safety": SafetyExecutor
    }
    
    executor_cls = executors.get(plan.mode)
    if not executor_cls:
        return ExecutionResult(
            status=NodeStatus.FAILURE, 
            error=f"No executor found for mode: {plan.mode}"
        )
        
    executor = executor_cls()
    return await executor.execute(plan, state)
