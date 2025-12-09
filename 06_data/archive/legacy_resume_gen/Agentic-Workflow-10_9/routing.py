# FILE: routing.py
"""
Routing & Prompt Invocation Layer (v10_9) — META LAYER ONLY (REFINED)

This module is a strictly META-layer component. It:

    • Builds routing criteria (complexity, cost, latency, risk)
    • Integrates meta_profile biases (routing/planning/safety)
    • Builds PromptEnvelope-compatible prompts
    • Calls L5.ModelRouter for model selection
    • Simulates model invocation (no provider calls)
    • Returns structured routing + prompt + simulated output

Agentic Guardrails (14/14):
    ❌ NO L1 planning
    ❌ NO L2 execution
    ❌ NO L3 orchestration
    ❌ NO L4 state mutation
    ❌ NO L5 decisions directly
    ❌ NO provider SDKs
    ✔  PURE META (safe)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional, List

from core.models.models import PlanObject
from prompt import System as PromptSystem
from core.l5 import ModelRouter, RoutingCriteria
from meta_profile import (
    get_routing_bias,
    get_planning_bias,
    get_safety_bias,
)


# ============================================================================
# 1. SAFE READ-ONLY CONTEXT VIEW (META-LAYER LOCAL HELPER)
# ============================================================================

def get_prompt_context_view(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    META-layer is allowed to read state (NOT mutate it).
    This helper extracts only the fields needed for prompt construction.

    This avoids importing from L4 and avoids layer violations.
    """
    return {
        "messages": state.get("messages", []),
        "summary": state.get("summary", ""),
        "rag_history": state.get("rag_history", []),
    }


# ============================================================================
# 2. DETERMINISTIC MODEL INVOCATION STUB (NO PROVIDER CALLS)
# ============================================================================

def invoke_model(prompt: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deterministic stub — simulates model invocation.
    Never calls real LLM providers.
    """
    return {
        "output": (
            f"[SIMULATED model={config.get('model')} endpoint={config.get('endpoint')}]"
            f"\n{prompt}"
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
# 3. ROUTING CONFIG (META ONLY)
# ============================================================================

@dataclass
class RoutingConfig:
    default_latency_ms: int = 2000
    default_cost_usd: float = 0.05
    base_risk_level: str = "normal"
    model_available: bool = True


# ============================================================================
# 4. META-AWARE ROUTING CRITERIA BUILDERS
# ============================================================================

def _derive_complexity(plan: Dict[str, Any]) -> str:
    c = str(plan.get("complexity", "")).lower()
    if c in ("low", "simple"):
        return "low"
    if c in ("moderate", "medium"):
        return "medium"
    if c in ("complex", "high"):
        return "high"
    return "low"


def _derive_risk_level(plan: Dict[str, Any], routing_cfg: RoutingConfig) -> str:
    safety = get_safety_bias()
    safety_meta = plan.get("safety_metadata") or {}

    if safety.get("heightened_caution"):
        return "high_safety"
    if safety.get("human_review_important"):
        return "strict"

    return str(safety_meta.get("sensitivity", routing_cfg.base_risk_level))


def _apply_meta_biases(criteria: RoutingCriteria) -> RoutingCriteria:
    routing = get_routing_bias()
    planning = get_planning_bias()
    safety = get_safety_bias()

    c = RoutingCriteria(
        task_type=criteria.task_type,
        complexity=criteria.complexity,
        latency_target_ms=criteria.latency_target_ms,
        cost_ceiling_usd=criteria.cost_ceiling_usd,
        risk_level=criteria.risk_level,
        model_available=criteria.model_available,
    )

    # prefer_fast → low-latency routing
    if routing.get("prefer_fast"):
        c.latency_target_ms = min(c.latency_target_ms, 800)

    # robust retrieval → high-accuracy path
    if routing.get("prefer_robust_retrieval"):
        c.latency_target_ms = max(c.latency_target_ms, 1500)
        c.risk_level = "strict"

    # long-context preference
    if routing.get("prefer_long_context"):
        c.complexity = "high"

    # conservative planning
    if planning.get("conservative"):
        c.complexity = "high"
        c.risk_level = "strict"

    # heightened safety
    if safety.get("heightened_caution"):
        c.risk_level = "high_safety"

    return c


def _build_routing_criteria(
    plan: Dict[str, Any],
    state: Dict[str, Any],
    routing_cfg: RoutingConfig,
) -> RoutingCriteria:

    criteria = RoutingCriteria(
        task_type=str(plan.get("mode", "unknown")),
        complexity=_derive_complexity(plan),
        latency_target_ms=routing_cfg.default_latency_ms,
        cost_ceiling_usd=routing_cfg.default_cost_usd,
        risk_level=_derive_risk_level(plan, routing_cfg),
        model_available=routing_cfg.model_available,
    )
    return _apply_meta_biases(criteria)


# ============================================================================
# 5. PROMPT CONSTRUCTION (PromptEnvelope)
# ============================================================================

def _format_context(context: Dict[str, Any], plan: Dict[str, Any]) -> str:
    lines: List[str] = []
    if plan.get("objective"):
        lines.append(f"Objective: {plan['objective']}")
    msgs = context.get("messages") or []
    if msgs:
        lines.append("Recent messages:")
        for m in msgs[-3:]:
            if isinstance(m, dict):
                lines.append(f"{m.get('role')}: {m.get('content')}")
    if context.get("summary"):
        lines.append(f"Summary: {context['summary']}")
    if context.get("rag_history"):
        lines.append(f"RAG items: {len(context['rag_history'])}")
    return "\n".join(lines)


def _format_reasoning(plan: Dict[str, Any]) -> str:
    inj = plan.get("injection_reasoning", {}) or {}
    out: List[str] = []
    if inj.get("reason_then_answer"):
        out.append("Reason step-by-step, then answer.")
    if inj.get("failure_anticipation_enabled"):
        fms = plan.get("top_failure_modes") or []
        for m in fms:
            out.append(f"- {m}")
    if inj.get("self_consistency_enabled"):
        out.append("Perform self-consistency checks.")
    if inj.get("error_simulation_enabled"):
        out.append("Anticipate common errors and guard against them.")
    return "\n".join(out)


def _format_instructions(plan: Dict[str, Any]) -> str:
    lines = [
        f"You are executing a '{plan.get('mode')}' task.",
        "Follow the plan precisely.",
    ]
    expected = plan.get("handoff", {}).get("expected_deliverables") or []
    if expected:
        lines.append("Expected deliverables:")
        for e in expected:
            lines.append(f"- {e}")
    return "\n".join(lines)


def _format_output_schema(plan: Dict[str, Any]) -> str:
    schema = plan.get("output_schema")
    if isinstance(schema, str):
        return schema
    if isinstance(schema, dict):
        return str(schema)
    return "Respond using concise, structured output (JSON when appropriate)."


def _build_prompt_bundle(plan: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
    context_view = get_prompt_context_view(state)
    prompt = PromptSystem.make_prompt(
        framing=plan.get("injection_framing", {}).get("global_goal", ""),
        context=_format_context(context_view, plan),
        reasoning=_format_reasoning(plan),
        instructions=_format_instructions(plan),
        safety_ctx=plan.get("safety_metadata", {}) or {},
        tool_ctx=plan.get("tool_context", {}) or {},
        output_schema=_format_output_schema(plan),
        runtime_context={
            "objective": plan.get("objective", ""),
            "mode": plan.get("mode", ""),
            "workflow_id": state.get("workflow_id", ""),
        },
    )

    return {
        "prompt": prompt,
        "context": context_view,
        "runtime_context": {
            "objective": plan.get("objective", ""),
            "mode": plan.get("mode", ""),
            "workflow_id": state.get("workflow_id", ""),
        },
    }


# ============================================================================
# 6. PUBLIC API — ROUTE + PROMPT + SIMULATED MODEL INVOCATION
# ============================================================================

def run_model_for_plan(
    plan: PlanObject | Dict[str, Any],
    state: Dict[str, Any],
    routing_cfg: Optional[RoutingConfig] = None,
) -> Dict[str, Any]:
    """
    End-to-end META routing pipeline:

        1. Normalize plan
        2. Build prompt envelope
        3. Construct RoutingCriteria (meta-aware)
        4. Ask L5.ModelRouter for model selection
        5. Simulate model invocation
        6. Return structured routing output

    DOES NOT mutate state.
    DOES NOT perform safety/policy.
    """
    plan_dict = plan.to_dict() if isinstance(plan, PlanObject) else dict(plan)

    # Build prompt
    prompt_bundle = _build_prompt_bundle(plan_dict, state)

    # Criteria
    cfg = routing_cfg or RoutingConfig()
    criteria = _build_routing_criteria(plan_dict, state, cfg)

    # L5 router
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

    # Simulated model
    model_output = invoke_model(prompt_bundle["prompt"], {
        "model": decision.model,
        "endpoint": decision.endpoint,
        "route": routing_info,
    })

    return {
        "prompt": prompt_bundle["prompt"],
        "runtime_context": prompt_bundle["runtime_context"],
        "model_output": model_output,
        "routing": routing_info,
    }
