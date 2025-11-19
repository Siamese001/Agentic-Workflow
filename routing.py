# FILE: routing.py
"""
Model Routing & Prompt Invocation Layer (v10_9) — PURE META LAYER

This module implements the model-routing and prompt-building logic for
the v10_9 agentic workflow. It is strictly META — above L1–L5 — and
must not perform:

    • L1 cognition (no planning)
    • L2 execution (no tools/LLMs)
    • L3 orchestration (no DAG or state transitions)
    • L4 state mutation (no apply_patch)
    • L5 safety decisions (only reads L5 routing hints)

Routing responsibilities:

    • Build RoutingCriteria from PlanObject + state
    • Ask L5.ModelRouter for routing decision (which model/endpoint)
    • Build a PromptEnvelope using prompt.System
    • Prepare structured payload for L3 or provider layer
    • Simulated model invocation (invoke_model) for deterministic testing

All model execution here is **simulated** and no provider/SDK code is
loaded. Real model invocation should be performed by provider-layer
client modules outside L1–L5.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from models import PlanObject
from l4 import get_prompt_context_view
from prompt import System as PromptSystem
from l5 import RoutingCriteria, ModelRouter


# ============================================================================
# 1. LOW-LEVEL MODEL INVOCATION STUB
# ============================================================================

def invoke_model(prompt: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deterministic model invocation stub.

    In production:
        • replaced by provider-layer LLMClient (Anthropic/Gemini/OpenAI)
        • uses model, endpoint, route metadata

    Here:
        • returns a synthetic response for deterministic tests
    """
    return {
        "output": (
            f"[SIMULATED RESPONSE model={config.get('model')} "
            f"endpoint={config.get('endpoint')}]\\n{prompt}"
        ),
        "usage": {
            "prompt_tokens": len(str(prompt).split()),
            "completion_tokens": 0,
        },
        "metadata": {
            "endpoint": config.get("endpoint"),
            "route": config.get("route"),
        },
    }


# ============================================================================
# 2. ROUTING CONFIGURATION
# ============================================================================

@dataclass
class RoutingConfig:
    """
    High-level routing configuration for model invocation.

    These are META-level controls — they do not affect L1–L5 behavior.
    """
    default_latency_ms: int = 2000
    default_cost_usd: float = 0.05
    risk_level: str = "normal"
    model_available: bool = True


def _build_routing_criteria(
    plan: Dict[str, Any],
    state: Dict[str, Any],
    cfg: RoutingConfig
) -> RoutingCriteria:
    """
    Derive RoutingCriteria from PlanObject + state + RoutingConfig.

    L5.ModelRouter uses this to choose model + endpoint.
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


# ============================================================================
# 3. PROMPT CONSTRUCTION HELPERS
# ============================================================================

def _format_context(context: Dict[str, Any], plan: Dict[str, Any]) -> str:
    """
    Build a compact context string from state + plan information.
    """
    parts: List[str] = []

    objective = plan.get("objective")
    if objective:
        parts.append(f"Objective: {objective}")

    # recent messages (last 3)
    messages = context.get("messages") or []
    if messages:
        parts.append("Recent messages:")
        for msg in messages[-3:]:
            if isinstance(msg, dict):
                role = msg.get("role", "")
                content = msg.get("content", "")
                parts.append(f"{role}: {content}")

    # summary
    summary = context.get("summary")
    if summary:
        parts.append(f"Summary: {summary}")

    # RAG hints
    rag = context.get("rag_history") or []
    if rag:
        parts.append(f"RAG items: {len(rag)}")

    return "\n".join(parts)


def _format_reasoning(plan: Dict[str, Any]) -> str:
    """
    Construct textual reasoning scaffolding based on plan metadata.
    """
    lines: List[str] = []

    inj = plan.get("injection_reasoning") or {}
    if inj.get("reason_then_answer"):
        lines.append("First, reason step-by-step; then produce a final answer.")
    if inj.get("failure_anticipation_enabled"):
        fm = plan.get("top_failure_modes") or []
        if fm:
            lines.append("Potential failure modes:")
            for m in fm:
                lines.append(f"- {m}")
    if inj.get("self_consistency_enabled"):
        lines.append("Perform self-consistency checks before finalizing your answer.")
    if inj.get("error_simulation_enabled"):
        lines.append("Consider common errors and guard against them.")

    return "\n".join(lines)


def _format_instructions(plan: Dict[str, Any]) -> str:
    """
    Construct instruction block from plan's mode and handoff.
    """
    mode = str(plan.get("mode", "unknown"))
    handoff = plan.get("handoff") or {}
    expected = handoff.get("expected_deliverables") or []

    lines: List[str] = [
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
    Extract textual output schema from plan; fallback to generic structured output directive.
    """
    schema = plan.get("output_schema")
    if isinstance(schema, str):
        return schema
    if isinstance(schema, dict):
        return str(schema)
    return (
        "Respond with a concise, structured answer aligned with "
        "the plan's deliverables. Use JSON when appropriate."
    )


def _build_prompt_bundle(plan: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build the rendered prompt and associated metadata needed to invoke
    a model or stub model.

    Output:
        {
            "prompt": "<string>",
            "context": {...},
            "runtime_context": {...},
        }
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

    # Render the prompt using PromptEnvelope
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


# ============================================================================
# 4. PUBLIC API
# ============================================================================

def run_model_for_plan(
    plan: PlanObject | Dict[str, Any],
    state: Dict[str, Any],
    routing: Optional[RoutingConfig] = None,
) -> Dict[str, Any]:
    """
    High-level helper for executing a *single* PlanObject against a model.

    Inputs:
        • plan:
            PlanObject OR dict (PlanObject is preferred).

        • state:
            Current orchestration state (READ ONLY).

        • routing:
            Optional RoutingConfig (latency, cost, risk).

    Returns:
        {
            "prompt":          <rendered prompt>,
            "runtime_context": {...},
            "model_output":    { ... simulated or actual model response ... },
            "routing": {
                "selected_model": ...,
                "endpoint": ...,
                "rationale": ...,
                "task_type": ...,
                "complexity": ...,
                "risk_level": ...,
            },
        }

    This function:
        • DOES NOT mutate state.
        • DOES NOT call L1–L5 logic (beyond ModelRouter).
        • DOES NOT perform LLM/SDK calls except through invoke_model stub.
    """

    # Normalize plan
    if isinstance(plan, PlanObject):
        plan_dict = plan.to_dict()
    else:
        plan_dict = dict(plan)

    routing_cfg = routing or RoutingConfig()

    # Build prompt & runtime context
    prompt_bundle = _build_prompt_bundle(plan_dict, state)

    # Build routing criteria + ask L5 model router
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

    # Simulated model invocation
    model_output = invoke_model(prompt_bundle["prompt"], model_config)

    return {
        "prompt": prompt_bundle["prompt"],
        "runtime_context": prompt_bundle["runtime_context"],
        "model_output": model_output,
        "routing": routing_info,
    }
