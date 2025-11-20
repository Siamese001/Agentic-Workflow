# FILE: l2.py
"""
Unified L2 Execution Layer (v10_10) — COGNITIVE EXECUTION (REFACTORED)

This module implements the "Hands" of the agent (Pillar 1, 5).
It executes the strict `PlanObject` contracts produced by L1.

Responsibilities:
    1. Interpret Plans: Route specific steps to the right execution logic.
    2. Coordinate Resources: Call `LLMGateway` (Cognition) or `Sandbox` (Tools).
    3. Structure Output: Return strict `ExecutionResult[Payload]` objects.

Architecture Change (v10_10):
    • Logic stripped of HTTP/Tool details (delegated to Gateway/Sandbox).
    • Prompts removed (delegated to Registry).
    • "Fake" heuristics replaced with "Real" LLM calls.
"""

from __future__ import annotations

import json
import asyncio
from typing import Any, Dict, List, Type, TypeVar

from models import (
    PlanObject,
    ExecutionResult,
    StrategyExecutionPayload,
    RAGExecutionPayload,
    DraftExecutionPayload,
    BulletExecutionPayload,
    QAExecutionPayload,
    SafetyExecutionPayload,
    HILExecutionPayload,
    MetaLearningExecutionPayload,
    RAGDocument,
    SafetyReport,
    QAReport,
    SafetyIssue,
    SafetyMode,
    StrategyBranch
)
from llm_gateway import GATEWAY
from sandbox import SANDBOX
from registry import REGISTRY
from runtime_utils import ToolExecutionError, ValidationError

# Generic Type for Execution Payloads
T = TypeVar("T")


# =============================================================================
# BASE EXECUTOR
# =============================================================================

class BaseExecutor:
    """Base class for all domain executors."""
    
    async def execute(self, plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult:
        raise NotImplementedError()

    def _wrap_success(self, payload: Any, model: str = "unknown") -> ExecutionResult:
        return ExecutionResult(
            status="success",
            payload=payload,
            model=model
        )

    def _extract_last_user_msg(self, state: Dict[str, Any]) -> str:
        msgs = state.get("messages", [])
        if msgs:
            return msgs[-1].get("content", "")
        return ""


# =============================================================================
# 1. STRATEGY EXECUTOR
# =============================================================================

class StrategyExecutor(BaseExecutor):
    """
    Executes strategic reasoning.
    v10_9: Static dict manipulation.
    v10_10: Real LLM reasoning via Gateway.
    """
    async def execute(self, plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult[StrategyExecutionPayload]:
        # If L1 already did the heavy lifting (CoT/ToT), we might just parse the context.
        # However, L2 usually refines the raw plan into actionable branches.
        
        raw_plan = plan.context_profile.get("raw_plan", {})
        
        # If raw_plan is empty, we invoke the LLM to generate it (fallback/refinement)
        if not raw_plan.get("branches"):
            response = await GATEWAY.call_model(
                prompt_id="l1_strategy_planner", # Reusing prompt for refinement
                inputs={
                    "objective": plan.objective,
                    "context_summary": self._extract_last_user_msg(state),
                    "branch_count": 3
                },
                workflow_id=plan.workflow_id or "unknown",
                reasoning_strategy=plan.reasoning_strategy
            )
            # In prod: safe json parsing
            try:
                data = json.loads(response.content)
            except:
                data = {"branches": [], "aggregated_decision": "error"}
        else:
            data = raw_plan

        # Convert dicts to Pydantic Models (Validation happens here)
        branches = [StrategyBranch(**b) for b in data.get("branches", [])]
        
        payload = StrategyExecutionPayload(
            branches=branches,
            selected_branch=branches[0] if branches else None,
            aggregated_decision=data.get("aggregated_decision", "proceed"),
            aggregated_confidence=data.get("aggregated_confidence", 0.8),
            surfaces=plan.surfaces
        )

        return self._wrap_success(payload, model="gateway-routed")


# =============================================================================
# 2. RAG EXECUTOR
# =============================================================================

class RAGExecutor(BaseExecutor):
    """
    Executes Retrieval.
    Delegates to SANDBOX for 'web_search' or internal DB tools.
    """
    async def execute(self, plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult[RAGExecutionPayload]:
        queries = []
        documents = []
        
        # Extract queries from L1 steps
        target_count = 3
        for step in plan.steps:
            if step.get("id") == "query_generation":
                target_count = step.get("count", 3)

        # Execute Search via Sandbox (Pillar 14)
        # In a real app, this might call 3-5 different tools in parallel
        
        search_result = await SANDBOX.execute_tool(
            tool_id="web_search",
            arguments={"query": plan.objective},
            workflow_id=plan.workflow_id or "unknown"
        )
        
        # Parse output into RAG Documents
        # (Simplified mapping for demo)
        doc_content = str(search_result["output"])
        documents.append(RAGDocument(
            query=plan.objective,
            content=doc_content,
            source="web_search",
            rank=1,
            score=0.95
        ))

        payload = RAGExecutionPayload(
            queries=[plan.objective],
            documents=documents
        )
        
        return self._wrap_success(payload, model="web-search-tool")


# =============================================================================
# 3. DRAFTING EXECUTOR
# =============================================================================

class DraftingExecutor(BaseExecutor):
    """
    Generates content sections based on RAG evidence.
    """
    async def execute(self, plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult[DraftExecutionPayload]:
        # Retrieve Evidence from Context
        rag_payload = state.get("rag_result", {})
        # Handle both dict and Pydantic object in state
        if hasattr(rag_payload, "documents"):
            evidence_text = "\n".join([d.content for d in rag_payload.documents])
        else:
            evidence_text = "No structured evidence found."

        full_draft = []
        sections_out = []

        # L2 Cognitive Loop: Draft each section
        # In v10_9 this was a loop over hardcoded strings. 
        # In v10_10 we use the Registry prompt.
        sections_to_draft = ["Introduction", "Main Body", "Conclusion"]
        
        for section in sections_to_draft:
            response = await GATEWAY.call_model(
                prompt_id="l2_drafter",
                inputs={
                    "tone": "professional",
                    "section_name": section,
                    "rag_evidence": evidence_text[:2000] # budget clipping
                },
                workflow_id=plan.workflow_id or "unknown"
            )
            
            text = response.content
            full_draft.append(text)
            sections_out.append({"id": section.lower(), "text": text})

        payload = DraftExecutionPayload(
            sections=sections_out,
            full_text="\n\n".join(full_draft)
        )

        return self._wrap_success(payload, model="gateway-drafter")


# =============================================================================
# 4. QA & SAFETY EXECUTORS (Governance)
# =============================================================================

class QAExecutor(BaseExecutor):
    """
    Validates content quality.
    """
    async def execute(self, plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult[QAExecutionPayload]:
        # Placeholder for semantic QA logic
        # In prod: Use GATEWAY to critique the 'draft_result'
        payload = QAExecutionPayload(
            report=QAReport(passed=True, summary="QA Passed (Simulation)")
        )
        return self._wrap_success(payload)

class SafetyExecutor(BaseExecutor):
    """
    Validates content safety (Constitutional AI).
    """
    async def execute(self, plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult[SafetyExecutionPayload]:
        # Extract content to check
        draft_res = state.get("draft_result", {})
        content = getattr(draft_res, "full_text", str(draft_res))

        # Fetch Policy (Pillar 9)
        mode_enum = SafetyMode(plan.safety_profile.get("mode", "balanced"))
        policy = REGISTRY.get_policy(mode_enum)

        # Semantic Check via Gateway
        response = await GATEWAY.call_model(
            prompt_id="l5_constitutional_judge",
            inputs={
                "content": content[:3000],
                "policy_rules": "\n".join(policy.rules)
            },
            workflow_id=plan.workflow_id or "unknown"
        )

        # Parse result (Mocking parsing logic for reliability in this output)
        # In real impl, force JSON mode on LLM
        if "fail" in response.content.lower():
            issues = [SafetyIssue(issue_id="violation", severity="high", category="policy", message="Policy violation detected.")]
            blocked = True
        else:
            issues = []
            blocked = False

        payload = SafetyExecutionPayload(
            report=SafetyReport(
                issues=issues,
                blocked=blocked,
                summary=response.content,
                metadata={"policy_version": policy.version}
            )
        )
        return self._wrap_success(payload, model=response.model_used)


# =============================================================================
# ROUTER (The Dispatcher)
# =============================================================================

async def route_executor(plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult:
    """
    Main dispatch function used by L3.
    """
    executors: Dict[str, Type[BaseExecutor]] = {
        "strategy": StrategyExecutor,
        "rag": RAGExecutor,
        "drafting": DraftingExecutor,
        "qa": QAExecutor,
        "safety": SafetyExecutor,
        # Fallbacks for others using Base
        "bullets": BaseExecutor, # Placeholder
        "hil": BaseExecutor,     # Placeholder
        "meta_learning": BaseExecutor # Placeholder
    }

    executor_cls = executors.get(plan.mode)
    if not executor_cls:
        # Graceful fallback (Pillar 5)
        return ExecutionResult(status="error", errors=[f"No executor for mode {plan.mode}"])

    executor = executor_cls()
    
    try:
        return await executor.execute(plan, state)
    except Exception as e:
        return ExecutionResult(status="error", errors=[str(e)])
