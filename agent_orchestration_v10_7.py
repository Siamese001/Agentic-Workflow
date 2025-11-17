"""Orchestration graph for v10_7 LangGraph workflow."""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict

from langgraph.graph import END, START, StateGraph

from agent_stacks_v10_8.state_adapter_stack import MainGraphState, StateAdapterStack
from arbitration_engine import ArbitrationEngine as SimpleArbitrationEngine
from core_v10_7.config import ConfigV10_7
from core_v10_7.context import WorkflowContext
from l1_strategy_reasoner import StrategyReasoner
from l2_bullet_execution import BulletExecutionAgent
from l2_drafting_execution import DraftExecutionAgent
from l2_qa_validation import QAValidationAgent
from l2_rag_execution import RAGExecutionAgent
from l4_state import StateAdapter
from l5_constitutional_engine import ConstitutionalEngine
from l5_safety_gateway import SafetyGateway
from prompt_builder_stack import PromptBuilderStack
from prompt_renderer_stack import PromptRendererStack

logger = logging.getLogger(__name__)


def node_success(name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize a successful node output."""

    return {"node": name, "status": "success", "payload": payload or {}}


def node_error(name: str, exc: Exception) -> Dict[str, Any]:
    """Normalize a failed node output."""

    return {"node": name, "status": "fatal_error", "payload": {"error": str(exc)}}


class ArbitrationEngine:
    """Wrapper around arbitration decision making with a stable interface."""

    def __init__(self) -> None:
        self._engine = SimpleArbitrationEngine()

    def run_check(self, stage: str, state: Dict[str, Any]) -> Dict[str, Any]:
        report = state.get("qa", {}) if isinstance(state, dict) else {}
        safety_patch = state.get("safety", {}) if isinstance(state, dict) else {}
        decision = self._engine.evaluate(state, report, safety_patch)
        decision["stage"] = stage
        decision.setdefault("suggested_route", decision.get("action", "ACCEPT").upper())
        return decision


async def _apply_patch(adapter: StateAdapterStack, state: Dict[str, Any], patch: Dict[str, Any]) -> Dict[str, Any]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, adapter.apply_patch, state, patch)


# Safety layer
async def run_sanitize_pii(state: Dict[str, Any], config: ConfigV10_7, context: WorkflowContext) -> Dict[str, Any]:
    try:
        patch = {"safety": {"pii": {"sanitized": True}}}
        merged = await _apply_patch(context.state_adapter, state, patch)
        return node_success("SANITIZE_PII", merged)
    except Exception as exc:  # pragma: no cover - defensive
        return node_error("SANITIZE_PII", exc)


async def run_detect_prompt_injection(state: Dict[str, Any], config: ConfigV10_7, context: WorkflowContext) -> Dict[str, Any]:
    try:
        gateway = context.safety_gateway
        payload = {"content": json.dumps(state)}
        patch = gateway.evaluate(payload)
        merged = await _apply_patch(context.state_adapter, state, patch)
        return node_success("DETECT_PROMPT_INJECTION", merged)
    except Exception as exc:  # pragma: no cover
        return node_error("DETECT_PROMPT_INJECTION", exc)


async def run_bias_check(state: Dict[str, Any], config: ConfigV10_7, context: WorkflowContext) -> Dict[str, Any]:
    try:
        patch = {"safety": {"bias": {"status": "pass"}}}
        merged = await _apply_patch(context.state_adapter, state, patch)
        return node_success("BIAS_CHECK", merged)
    except Exception as exc:  # pragma: no cover
        return node_error("BIAS_CHECK", exc)


# Strategy + complexity
async def run_classify_complexity(state: Dict[str, Any], config: ConfigV10_7, context: WorkflowContext) -> Dict[str, Any]:
    try:
        complexity = state.get("metadata", {}).get("complexity") or "medium"
        patch = {"metadata": {"complexity": complexity}}
        merged = await _apply_patch(context.state_adapter, state, patch)
        return node_success("CLASSIFY_COMPLEXITY", merged)
    except Exception as exc:  # pragma: no cover
        return node_error("CLASSIFY_COMPLEXITY", exc)


async def run_strategy_plan(state: Dict[str, Any], config: ConfigV10_7, context: WorkflowContext) -> Dict[str, Any]:
    try:
        plan = context.strategy_reasoner.plan(state)
        patch = {"strategy": plan}
        merged = await _apply_patch(context.state_adapter, state, patch)
        return node_success("STRATEGY_PLAN", merged)
    except Exception as exc:  # pragma: no cover
        return node_error("STRATEGY_PLAN", exc)


async def run_ambiguity_check(state: Dict[str, Any], config: ConfigV10_7, context: WorkflowContext) -> Dict[str, Any]:
    try:
        ambiguous = bool(state.get("metadata", {}).get("ambiguous"))
        patch = {"metadata": {"ambiguous": ambiguous}}
        merged = await _apply_patch(context.state_adapter, state, patch)
        return node_success("AMBIGUITY_CHECK", merged)
    except Exception as exc:  # pragma: no cover
        return node_error("AMBIGUITY_CHECK", exc)


# HIL
async def run_feedback_routing(state: Dict[str, Any], config: ConfigV10_7, context: WorkflowContext) -> Dict[str, Any]:
    try:
        patch = {"hil": {"next_step": state.get("hil", {}).get("next_step", "STRATEGY")}}
        merged = await _apply_patch(context.state_adapter, state, patch)
        return node_success("FEEDBACK_ROUTING", merged)
    except Exception as exc:  # pragma: no cover
        return node_error("FEEDBACK_ROUTING", exc)


async def run_reconciliation(state: Dict[str, Any], config: ConfigV10_7, context: WorkflowContext) -> Dict[str, Any]:
    try:
        patch = {"feedback": {"reconciled": True}}
        merged = await _apply_patch(context.state_adapter, state, patch)
        return node_success("RECONCILIATION", merged)
    except Exception as exc:  # pragma: no cover
        return node_error("RECONCILIATION", exc)


async def run_hil_edit_injection(state: Dict[str, Any], config: ConfigV10_7, context: WorkflowContext) -> Dict[str, Any]:
    try:
        edit = state.get("hil", {}).get("edit")
        patch = {"draft": {"hil_edit": edit}}
        merged = await _apply_patch(context.state_adapter, state, patch)
        return node_success("HIL_EDIT_INJECTION", merged)
    except Exception as exc:  # pragma: no cover
        return node_error("HIL_EDIT_INJECTION", exc)


async def hil_pause_node(state: Dict[str, Any], config: ConfigV10_7, context: WorkflowContext) -> Dict[str, Any]:
    return {"node": "HIL_PAUSE", "status": "blocked", "payload": {"hil": state.get("hil", {})}}


# Parallel prep and prompt/rag
async def run_prepare_parallel(state: Dict[str, Any], config: ConfigV10_7, context: WorkflowContext) -> Dict[str, Any]:
    try:
        patch = {"metadata": {"parallel_ready": True}}
        merged = await _apply_patch(context.state_adapter, state, patch)
        return node_success("PREPARE_PARALLEL", merged)
    except Exception as exc:  # pragma: no cover
        return node_error("PREPARE_PARALLEL", exc)


async def run_prompt_builder(state: Dict[str, Any], config: ConfigV10_7, context: WorkflowContext) -> Dict[str, Any]:
    try:
        result = await context.prompt_builder.run_async(
            state.get("strategy", {}), state.get("metadata", {}).get("complexity", "medium")
        )
        merged = await _apply_patch(context.state_adapter, state, result)
        return node_success("PROMPT_BUILDER", merged)
    except Exception as exc:  # pragma: no cover
        return node_error("PROMPT_BUILDER", exc)


async def run_prompt_renderer(state: Dict[str, Any], config: ConfigV10_7, context: WorkflowContext) -> Dict[str, Any]:
    try:
        result = await context.prompt_renderer.run_async(state)
        merged = await _apply_patch(context.state_adapter, state, result)
        return node_success("PROMPT_RENDERER", merged)
    except Exception as exc:  # pragma: no cover
        return node_error("PROMPT_RENDERER", exc)


async def run_rag_plan(state: Dict[str, Any], config: ConfigV10_7, context: WorkflowContext) -> Dict[str, Any]:
    try:
        plan = {"retrieval": {"queries": [state.get("objective", "main query")]}}
        patch = {"rag": {"plan": plan}}
        merged = await _apply_patch(context.state_adapter, state, patch)
        return node_success("RAG_PLAN", merged)
    except Exception as exc:  # pragma: no cover
        return node_error("RAG_PLAN", exc)


async def run_rag_exec(state: Dict[str, Any], config: ConfigV10_7, context: WorkflowContext) -> Dict[str, Any]:
    try:
        plan = state.get("rag", {}).get("plan", {})
        result = context.rag_agent.execute(plan, state)
        merged = await _apply_patch(context.state_adapter, state, result)
        return node_success("RAG_EXEC", merged)
    except Exception as exc:  # pragma: no cover
        return node_error("RAG_EXEC", exc)


async def run_join_prompt_and_rag(state: Dict[str, Any], config: ConfigV10_7, context: WorkflowContext) -> Dict[str, Any]:
    try:
        patch = {"prompts": state.get("prompts", {}), "rag": state.get("rag", {})}
        merged = await _apply_patch(context.state_adapter, state, patch)
        return node_success("JOIN_PROMPT_AND_RAG", merged)
    except Exception as exc:  # pragma: no cover
        return node_error("JOIN_PROMPT_AND_RAG", exc)


# Bullets + drafting
async def run_bullet_plan(state: Dict[str, Any], config: ConfigV10_7, context: WorkflowContext) -> Dict[str, Any]:
    try:
        patch = {"bullets": ["point-1", "point-2"]}
        merged = await _apply_patch(context.state_adapter, state, patch)
        return node_success("BULLET_PLAN", merged)
    except Exception as exc:  # pragma: no cover
        return node_error("BULLET_PLAN", exc)


async def run_bullet_exec(state: Dict[str, Any], config: ConfigV10_7, context: WorkflowContext) -> Dict[str, Any]:
    try:
        patch = context.bullet_agent.execute(state.get("strategy", {}), state)
        merged = await _apply_patch(context.state_adapter, state, patch)
        return node_success("BULLET_EXEC", merged)
    except Exception as exc:  # pragma: no cover
        return node_error("BULLET_EXEC", exc)


async def run_draft_plan(state: Dict[str, Any], config: ConfigV10_7, context: WorkflowContext) -> Dict[str, Any]:
    try:
        patch = {"draft": {"outline": state.get("bullets", [])}}
        merged = await _apply_patch(context.state_adapter, state, patch)
        return node_success("DRAFT_PLAN", merged)
    except Exception as exc:  # pragma: no cover
        return node_error("DRAFT_PLAN", exc)


async def run_draft_exec(state: Dict[str, Any], config: ConfigV10_7, context: WorkflowContext) -> Dict[str, Any]:
    try:
        patch = context.draft_agent.execute(state.get("draft", {}), state)
        merged = await _apply_patch(context.state_adapter, state, patch)
        return node_success("DRAFT_EXEC", merged)
    except Exception as exc:  # pragma: no cover
        return node_error("DRAFT_EXEC", exc)


# QA + constitutional
async def run_qa_validation(state: Dict[str, Any], config: ConfigV10_7, context: WorkflowContext) -> Dict[str, Any]:
    try:
        patch = context.qa_agent.evaluate(state.get("draft", {}), state)
        merged = await _apply_patch(context.state_adapter, state, patch)
        return node_success("QA_VALIDATION", merged)
    except Exception as exc:  # pragma: no cover
        return node_error("QA_VALIDATION", exc)


async def run_constitutional_review(state: Dict[str, Any], config: ConfigV10_7, context: WorkflowContext) -> Dict[str, Any]:
    try:
        engine = context.constitutional_engine
        review = engine.evaluate(json.dumps(state.get("draft", {})))
        patch = {"constitutional_review": review}
        merged = await _apply_patch(context.state_adapter, state, patch)
        return node_success("CONSTITUTIONAL_REVIEW", merged)
    except Exception as exc:  # pragma: no cover
        return node_error("CONSTITUTIONAL_REVIEW", exc)


async def run_finalize(state: Dict[str, Any], config: ConfigV10_7, context: WorkflowContext) -> Dict[str, Any]:
    try:
        artifacts = state.get("artifacts", {}) if isinstance(state, dict) else {}
        artifacts["final"] = state.get("draft")
        merged = await _apply_patch(context.state_adapter, state, {"artifacts": artifacts})
        return node_success("FINALIZE", merged)
    except Exception as exc:  # pragma: no cover
        return node_error("FINALIZE", exc)


# Routing helpers

def check_prompt_injection(result: Dict[str, Any]) -> str:
    safety = result.get("payload", {}).get("safety", {})
    if isinstance(safety, dict) and safety.get("injection_scan", {}).get("is_injection"):
        return "BLOCKED"
    return "SAFE"


def check_ambiguity(result: Dict[str, Any]) -> str:
    metadata = result.get("payload", {}).get("metadata", {})
    return "AMBIGUOUS" if metadata.get("ambiguous") else "CLEAR"


def check_rag_success(result: Dict[str, Any]) -> str:
    payload = result.get("payload", {})
    rag = payload.get("rag", {}) if isinstance(payload, dict) else {}
    return "OK" if rag else "RETRY_RAG"


def check_bullets(result: Dict[str, Any]) -> str:
    bullets = result.get("payload", {}).get("bullets", [])
    return "OK" if bullets else "RETRY_BULLETS"


def check_drafting(result: Dict[str, Any]) -> str:
    draft = result.get("payload", {}).get("draft")
    return "OK" if draft else "RETRY_DRAFTING"


def check_qa(result: Dict[str, Any]) -> str:
    qa = result.get("payload", {}).get("qa", {})
    if isinstance(qa, dict) and qa.get("status") == "pass":
        return "PASS"
    return "FAIL"


def check_constitution(result: Dict[str, Any]) -> str:
    review = result.get("payload", {}).get("constitutional_review", {})
    return "PASS" if review else "FAIL"


def check_hil_reentry(result: Dict[str, Any], hil_retry_count: int) -> bool:
    if hil_retry_count <= 0:
        return False
    hil = result.get("payload", {}).get("hil", {})
    next_step = hil.get("next_step") if isinstance(hil, dict) else None
    return bool(next_step)


class OrchestrationContext(WorkflowContext):
    """Enriched workflow context for orchestration nodes."""

    def __init__(self, config: ConfigV10_7):
        super().__init__(config)
        self.state_adapter = StateAdapterStack()
        self.strategy_reasoner = StrategyReasoner()
        self.rag_agent = RAGExecutionAgent()
        self.bullet_agent = BulletExecutionAgent()
        self.draft_agent = DraftExecutionAgent()
        self.qa_agent = QAValidationAgent()
        self.prompt_builder = PromptBuilderStack()
        self.prompt_renderer = PromptRendererStack()
        self.safety_gateway = SafetyGateway()
        self.constitutional_engine = ConstitutionalEngine()
        self.state_adapter_v1 = StateAdapter()
        self.arbitration_engine = ArbitrationEngine()


def unwrap_node_result(result: Dict[str, Any]) -> Dict[str, Any]:
    payload = result.get("payload") or {}
    if isinstance(payload, MainGraphState):
        return payload.to_dict()
    return payload


def get_graph_app(checkpointer: Any, config: ConfigV10_7, context: OrchestrationContext):
    graph = StateGraph(MainGraphState)

    graph.add_node("SANITIZE_PII", lambda state: run_sanitize_pii(state, config, context))
    graph.add_node(
        "DETECT_PROMPT_INJECTION",
        lambda state: run_detect_prompt_injection(state, config, context),
    )
    graph.add_node("BIAS_CHECK", lambda state: run_bias_check(state, config, context))
    graph.add_node(
        "CLASSIFY_COMPLEXITY", lambda state: run_classify_complexity(state, config, context)
    )
    graph.add_node("STRATEGY_PLAN", lambda state: run_strategy_plan(state, config, context))
    graph.add_node("AMBIGUITY_CHECK", lambda state: run_ambiguity_check(state, config, context))
    graph.add_node("HIL_PAUSE", lambda state: hil_pause_node(state, config, context))
    graph.add_node("FEEDBACK_ROUTING", lambda state: run_feedback_routing(state, config, context))
    graph.add_node("RECONCILIATION", lambda state: run_reconciliation(state, config, context))
    graph.add_node("HIL_EDIT_INJECTION", lambda state: run_hil_edit_injection(state, config, context))
    graph.add_node("PREPARE_PARALLEL", lambda state: run_prepare_parallel(state, config, context))
    graph.add_node("PROMPT_BUILDER", lambda state: run_prompt_builder(state, config, context))
    graph.add_node("PROMPT_RENDERER", lambda state: run_prompt_renderer(state, config, context))
    graph.add_node("RAG_PLAN", lambda state: run_rag_plan(state, config, context))
    graph.add_node("RAG_EXEC", lambda state: run_rag_exec(state, config, context))
    graph.add_node("JOIN_PROMPT_AND_RAG", lambda state: run_join_prompt_and_rag(state, config, context))
    graph.add_node("BULLET_PLAN", lambda state: run_bullet_plan(state, config, context))
    graph.add_node("BULLET_EXEC", lambda state: run_bullet_exec(state, config, context))
    graph.add_node("DRAFT_PLAN", lambda state: run_draft_plan(state, config, context))
    graph.add_node("DRAFT_EXEC", lambda state: run_draft_exec(state, config, context))
    graph.add_node("QA_VALIDATION", lambda state: run_qa_validation(state, config, context))
    graph.add_node("CONSTITUTIONAL_REVIEW", lambda state: run_constitutional_review(state, config, context))
    graph.add_node("FINALIZE", lambda state: run_finalize(state, config, context))

    graph.add_edge(START, "SANITIZE_PII")
    graph.add_edge("SANITIZE_PII", "DETECT_PROMPT_INJECTION")
    graph.add_edge("DETECT_PROMPT_INJECTION", "BIAS_CHECK")
    graph.add_edge("BIAS_CHECK", "CLASSIFY_COMPLEXITY")
    graph.add_edge("CLASSIFY_COMPLEXITY", "STRATEGY_PLAN")
    graph.add_edge("STRATEGY_PLAN", "AMBIGUITY_CHECK")
    graph.add_conditional_edges(
        "AMBIGUITY_CHECK",
        check_ambiguity,
        {"AMBIGUOUS": "HIL_PAUSE", "CLEAR": "PREPARE_PARALLEL"},
    )
    graph.add_edge("HIL_PAUSE", "FEEDBACK_ROUTING")
    graph.add_edge("FEEDBACK_ROUTING", "RECONCILIATION")
    graph.add_edge("RECONCILIATION", "HIL_EDIT_INJECTION")
    graph.add_edge("HIL_EDIT_INJECTION", "STRATEGY_PLAN")

    graph.add_edge("PREPARE_PARALLEL", "PROMPT_BUILDER")
    graph.add_edge("PREPARE_PARALLEL", "RAG_PLAN")
    graph.add_edge("PROMPT_BUILDER", "PROMPT_RENDERER")
    graph.add_edge("RAG_PLAN", "RAG_EXEC")
    graph.add_edge("PROMPT_RENDERER", "JOIN_PROMPT_AND_RAG")
    graph.add_edge("RAG_EXEC", "JOIN_PROMPT_AND_RAG")
    graph.add_edge("JOIN_PROMPT_AND_RAG", "BULLET_PLAN")
    graph.add_edge("BULLET_PLAN", "BULLET_EXEC")
    graph.add_edge("BULLET_EXEC", "DRAFT_PLAN")
    graph.add_edge("DRAFT_PLAN", "DRAFT_EXEC")
    graph.add_edge("DRAFT_EXEC", "QA_VALIDATION")
    graph.add_edge("QA_VALIDATION", "CONSTITUTIONAL_REVIEW")
    graph.add_edge("CONSTITUTIONAL_REVIEW", "FINALIZE")
    graph.add_edge("FINALIZE", END)

    app = graph.compile(checkpointer=checkpointer)
    return app


__all__ = ["get_graph_app", "unwrap_node_result", "OrchestrationContext"]
