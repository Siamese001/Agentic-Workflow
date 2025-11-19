# FILE: routing.py
"""
Model Routing & Prompt Invocation Layer (v10_9) — ENTERPRISE MODULE

This module implements the meta-level model routing and prompt invocation
logic for the v10_9 agentic architecture.

Responsibilities (META layer, *outside* L1–L5):
    • Build routing criteria from PlanObject + state.
    • Use L5.ModelRouter to select model + endpoint.
    • Build a fully-rendered prompt using the Prompt system.
    • Invoke the selected model via a pluggable `invoke_model` hook.
    • Return a structured payload that L3/L4 can attach into state.

Non-responsibilities:
    • NO L1 cognition (no planning).
    • NO L2 domain execution (no RAG, drafting, QA logic).
    • NO L3 control flow (no DAG orchestration).
    • NO L4 state mutation (no direct state writes).
    • NO L5 safety/policy decisions (SafetyEngine/PolicyEngine handle that).

This module is designed to be called by:
    • L3 Orchestrators (for meta-model invocations).
    • Optional higher-level meta stacks (e.g., prompt-testing, meta-learning).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from models import PlanObject
from l4 import get_prompt_context_view
from prompt import System as PromptSystem
from l5 import RoutingCriteria, ModelRouter


# =============================================================================
# 1. LOW-LEVEL MODEL INVOCATION STUB
# =============================================================================


def invoke_model(prompt: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deterministic model invocation stub.

    In production, replace this with actual model client logic
    (e.g., OpenAI, Anthropic, Gemini, etc.), making use of:

        • config["model"]
        • config["endpoint"]
        • config["route"] (metadata)
        • any other settings you choose to add.

    The default implementation is CI-safe: it never calls a real model.
    """
    return {
        "output": f"[SIMULATED RESPONSE model={config.get('model')} endpoint={config.get('endpoint')}]\n{prompt}",
        "usage": {
            "prompt_tokens": len(str(prompt).split()),
            "completion_tokens": 0,
        },
        "metadata": {
            "endpoint": config.get("endpoint"),
            "route": config.get("route"),
        },
    }


# =============================================================================
# 2. ROUTING CONFIGURATION
# =============================================================================


@dataclass
class RoutingConfig:
    """
    High-level routing configuration.

    This is a meta-level configuration object. Callers can tweak latency
    and cost targets per invocation.

    Fields:
        • default_latency_ms: soft target latency in ms.
        • default_cost_usd: soft cost ceiling in USD.
        • risk_level: "normal" | "strict" | "high_safety".
        • model_available: whether the primary model is considered available.
    """

    default_latency_ms: int = 2000
    default_cost_usd: float = 0.05
    risk_level: str = "normal"
    model_available: bool = True


def _build_routing_criteria(plan: Dict[str, Any], state: Dict[str, Any], cfg: RoutingConfig) -> RoutingCriteria:
    """
    Derive RoutingCriteria from PlanObject + state + RoutingConfig.
    """
    mode = str(plan.get("mode", "unknown"))
    complexity = str(plan.get("complexity", "low"))

    safety_meta = plan.get("safety_metadata") or {}
    risk_level = str(safety_meta.get("sensitivity", cfg.risk_level))

    return RoutingCriteria(
        task_type=mode,
        complexity=complexity if complexity in ("low", "medium", "high") else "low",
        latency_target_ms=cfg.default_latency_ms,
        cost_ceiling_usd=cfg.default_cost_usd,
        risk_level=risk_level,
        model_available=cfg.model_available,
    )


# =============================================================================
# 3. PROMPT CONSTRUCTION
# =============================================================================


def _format_context(context: Dict[str, Any], plan: Dict[str, Any]) -> str:
    """
    Build a compact context string from state+plan:

        • Objective
        • Recent messages
        • Summary
        • RAG hints
    """
    parts: list[str] = []

    objective = plan.get("objective")
    if objective:
        parts.append(f"Objective: {objective}")

    messages = context.get("messages") or []
    if messages:
        parts.append("Recent messages:")
        for msg in messages[-3:]:
            if isinstance(msg, dict):
                role = msg.get("role", "")
                content = msg.get("content", "")
                parts.append(f"{role}: {content}")

    summary = context.get("summary")
    if summary:
        parts.append(f"Summary: {summary}")

    rag_history = context.get("rag_history") or []
    if rag_history:
        parts.append(f"RAG items: {len(rag_history)}")

    return "\n".join(parts)


def _format_reasoning(plan: Dict[str, Any]) -> str:
    """
    Turn L1 reasoning hints into a structured textual scaffold.
    """
    lines: list[str] = []

    inj = plan.get("injection_reasoning") or {}
    if inj.get("reason_then_answer"):
        lines.append("First, reason step-by-step; then produce a final answer.")
    if inj.get("failure_anticipation_enabled"):
        failure_modes = plan.get("top_failure_modes") or []
        if failure_modes:
            lines.append("Potential failure modes:")
            for m in failure_modes:
                lines.append(f"- {m}")
    if inj.get("self_consistency_enabled"):
        lines.append("Perform internal consistency checks before finalizing your answer.")
    if inj.get("error_simulation_enabled"):
        lines.append("If helpful, imagine common errors and guard against them.")

    return "\n".join(lines)


def _format_instructions(plan: Dict[str, Any]) -> str:
    """
    Construct high-level instructions from the plan's mode and handoff.
    """
    mode = str(plan.get("mode", "unknown"))
    handoff = plan.get("handoff") or {}
    expected = handoff.get("expected_deliverables") or []

    lines: list[str] = [
        f"You are executing a '{mode}' task.",
        "Follow the plan's intent precisely and do not change its objective.",
    ]
    if expected:
        lines.append("Expected deliverables:")
        for item in expected:
            lines.append(f"- {item}")
    return "\n".join(lines)


def _format_output_schema(plan: Dict[str, Any]) -> str:
    """
    Extract a textual description of the expected output schema from the plan,
    if any; otherwise, provide a generic structured-output directive.
    """
    schema = plan.get("output_schema")
    if isinstance(schema, str):
        return schema
    if isinstance(schema, dict):
        return str(schema)
    return (
        "Respond with a concise, structured answer that aligns with the "
        "plan's expected deliverables. Use JSON where appropriate."
    )


def _build_prompt_bundle(plan: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build the rendered prompt and associated metadata (context, runtime_context).
    """
    context_view = get_prompt_context_view(state)

    framing = plan.get("injection_framing", {}).get("global_goal", "")
    context_text = _format_context(context_view, plan)
    reasoning_text = _format_reasoning(plan)
    instructions_text = _format_instructions(plan)
    safety_ctx = plan.get("safety_metadata", {}) or {}
    tool_ctx = plan.get("tool_context", {}) or {}
    output_schema = _format_output_schema(plan)

    runtime_context = {
        "objective": plan.get("objective", ""),
        "mode": plan.get("mode", ""),
        "workflow_id": state.get("workflow_id", ""),
    }

    prompt_str = PromptSystem.make_prompt(
        framing=framing,
        context=context_text,
        reasoning=reasoning_text,
        instructions=instructions_text,
        safety_ctx=safety_ctx,
        tool_ctx=tool_ctx,
        output_schema=output_schema,
        runtime_context=runtime_context,
    )

    return {
        "prompt": prompt_str,
        "context": context_view,
        "runtime_context": runtime_context,
    }


# =============================================================================
# 4. PUBLIC API
# =============================================================================


def run_model_for_plan(
    plan: PlanObject | Dict[str, Any],
    state: Dict[str, Any],
    routing: Optional[RoutingConfig] = None,
) -> Dict[str, Any]:
    """
    High-level helper for executing a single PlanObject against a model.

    Inputs:
        • plan:
            PlanObject or dict produced by L1 (StrategyReasoner, RAGReasoner,
            DraftingReasoner, etc.).

        • state:
            The current orchestration state (dict). Only read, never mutated.

        • routing:
            Optional RoutingConfig to adjust latency/cost/risk targets.

    Returns:
        dict:
            {
                "prompt": "<rendered prompt>",
                "runtime_context": {...},
                "model_output": { ... simulated or real model response ... },
                "routing": {
                    "selected_model": ...,
                    "endpoint": ...,
                    "rationale": ...,
                    "task_type": ...,
                    "complexity": ...,
                    "risk_level": ...,
                },
            }

    This function does NOT mutate L4 state. L3/L4 callers are responsible
    for applying any returned data into state via StateAdapter + StatePatch.
    """
    # Normalize plan -> dict
    if isinstance(plan, PlanObject):
        plan_dict = plan.to_dict()
    else:
        plan_dict = dict(plan)

    routing_cfg = routing or RoutingConfig()

    # Build prompt + runtime context
    prompt_bundle = _build_prompt_bundle(plan_dict, state)

    # Build routing criteria and select a model/endpoint
    criteria = _build_routing_criteria(plan_dict, state, routing_cfg)
    router = ModelRouter()
    decision = router.select(criteria)

    routing_info = {
        "selected_model": decision.model,
        "endpoint": decision.endpoint,
        "rationale": decision.rationale,
        "task_type": criteria.task_type,
        "complexity": criteria.complexity,
        "risk_level": criteria.risk_level,
    }

    model_config = {
        "model": decision.model,
        "endpoint": decision.endpoint,
        "route": routing_info,
    }

    # Invoke the model (simulated by default)
    model_output = invoke_model(prompt_bundle["prompt"], model_config)

    return {
        "prompt": prompt_bundle["prompt"],
        "runtime_context": prompt_bundle["runtime_context"],
        "model_output": model_output,
        "routing": routing_info,
    }
