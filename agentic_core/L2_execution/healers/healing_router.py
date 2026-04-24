"""C3 Healing Router - Tier-based routing.

10C-REQ-137: Route to Local Agent, Qwen_vLLM, or Gemini_2.5_Pro based on confidence.

Wave 2 (plans/routing-unification-qwen-abe735.md) extensions:
  - `route()` now accepts an optional `RoutingContext` and applies
    Gate 0-4 overrides via `routing_gates.apply_routing_gates`.
  - `RoutingDecision` carries the gate_applied label for audit trail.
  - New `dispatch_to_executor()` seam calls `AppsQwenGateway` for MEDIUM
    and returns sentinel results for HIGH/LOW/HITL.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from agentic_core.L0_routing.config.model_registry import (  # guardian: allow-layer-violation -- L2 healer reads model-ID constants from L0 SSOT
    DETERMINISTIC_MODEL_SENTINEL,
    GEMINI_FLASH_MODEL_ID,
    GEMINI_PRO_MODEL_ID,
    QWEN_LOCAL_MODEL_ID,
)

from agentic_core.L6_observability.heal_router_otel import (  # guardian: allow-layer-violation -- L2 healer emits observability span through L6 OTel emitter
    get_default_emitter as _get_default_heal_router_emitter,
)

from .confidence_scorer import ConfidenceScore, HealTier
from .failure_signal import FailureSignal
from .routing_gates import RoutingContext, apply_routing_gates


# Wave 5 P5.1 (2026-04-21): Gate names that demand GEMINI_PRO (high-reasoning).
# Any other LOW-tier decision routes to GEMINI_FLASH (cheaper / faster).
# Source-of-truth split without adding new HealTier enum values (backward-compat).
_PRO_REQUIRED_GATES: frozenset[str] = frozenset(
    {
        "GATE_1_RETRY_OVERRIDE",
        "GATE_1_RETRY_OVERRIDE_HITL",
        "GATE_2_STRUCTURAL_NO_DET_COV",
        "GATE_2_STRUCTURAL_HITL",
        "GATE_4_HARD_OVERRIDE",
        "GATE_4_HARD_OVERRIDE_HITL",
        "QWEN_DISALLOWED",
        "QWEN_DISALLOWED_HITL",
    },
)

# Wave 6 P6.2 (2026-04-21): Cost-weighted demotion thresholds (USD).
# When `RoutingContext.cost_budget_remaining_usd` is below these, the router
# demotes to cheaper tiers:
#   below COST_DEMOTE_PRO_USD   → Gemini Pro  demoted to Gemini Flash
#   below COST_DEMOTE_FLASH_USD → Gemini Flash demoted to Qwen local (free)
# Gated by None (default) so cost demotion is strictly opt-in.
COST_DEMOTE_PRO_USD: float = float(os.getenv("ROUTING_COST_DEMOTE_PRO_USD", "10.0"))
COST_DEMOTE_FLASH_USD: float = float(os.getenv("ROUTING_COST_DEMOTE_FLASH_USD", "1.0"))


@dataclass
class RoutingDecision:
    """Healing routing decision."""

    tier: HealTier
    target_model: str
    timeout_seconds: int
    max_tokens: int
    requires_sandbox: bool
    reasoning: str
    gate_applied: str = "NO_OVERRIDE"
    gemini_subtier: str = ""  # "" | "FLASH" | "PRO" — populated for LOW tier only
    cost_demoted: bool = False  # Wave 6 P6.2: True when budget pressure forced a tier downgrade


class HealingRouter:
    """C3 Healing router based on confidence tiers.

    10C-REQ-137: High->Local Agent Medium->Qwen_vLLM Low->Gemini_2.5_Pro.

    **HITL DECISION REQUIRED**: Model assignments and resource limits.
    """

    # HITL-10C-003: Model assignments require stakeholder approval
    # Model IDs sourced from L0 model_registry SSOT (env-var overridable).
    TIER_CONFIG: dict[HealTier, dict[str, Any]] = {
        HealTier.HIGH: {
            "model": DETERMINISTIC_MODEL_SENTINEL,
            "timeout": 5,
            "max_tokens": 1000,
            "sandbox": False,
        },
        HealTier.MEDIUM: {
            "model": QWEN_LOCAL_MODEL_ID,
            "timeout": 30,
            "max_tokens": 4000,
            "sandbox": True,
        },
        HealTier.LOW: {
            "model": GEMINI_PRO_MODEL_ID,
            "timeout": 60,
            "max_tokens": 8000,
            "sandbox": True,
        },
        HealTier.HITL: {
            "model": "human_review",
            "timeout": 86400,  # 24 hours
            "max_tokens": 0,
            "sandbox": False,
        },
    }

    def __init__(self) -> None:
        self._tier_stats: dict[HealTier, int] = {tier: 0 for tier in HealTier}

    def route(
        self,
        score: ConfidenceScore,
        signal: FailureSignal,
        context: RoutingContext | None = None,
    ) -> RoutingDecision:
        """Route healing to appropriate tier.

        Args:
            score: ConfidenceScore produced by ConfidenceScorer.
            signal: FailureSignal being routed.
            context: Optional routing metadata (replay, playbook match,
                provider availability, structural failure type). When None,
                only the tier from `score` drives routing — no overrides.

        Returns:
            RoutingDecision with gate_applied populated ("NO_OVERRIDE" when
            no gate fired).
        """
        final_tier, gate_applied = apply_routing_gates(score.tier, signal, context)
        config = self.TIER_CONFIG.get(final_tier, self.TIER_CONFIG[HealTier.HITL])

        self._tier_stats[final_tier] += 1

        # Wave 5 P5.1: for LOW tier, split into Flash vs Pro based on gate name.
        # Gates encoding structural/retry/hard-override complexity → Pro.
        # Confidence-based LOW (NO_OVERRIDE, GEMINI_UNAVAILABLE_HITL) → Flash.
        target_model = config["model"]
        gemini_subtier = ""
        if final_tier == HealTier.LOW:
            if gate_applied in _PRO_REQUIRED_GATES:
                gemini_subtier = "PRO"
                target_model = GEMINI_PRO_MODEL_ID
            else:
                gemini_subtier = "FLASH"
                target_model = GEMINI_FLASH_MODEL_ID

        # Wave 6 P6.2: Cost-weighted demotion — applied AFTER gate/subtier
        # selection so the demotion decision is observable in cost_demoted.
        # Only runs when caller provides `cost_budget_remaining_usd`.
        cost_demoted = False
        demotion_reason = ""
        budget = context.cost_budget_remaining_usd if context is not None else None
        if budget is not None and context is not None:
            if gemini_subtier == "PRO" and budget < COST_DEMOTE_PRO_USD:
                # Pro → Flash
                gemini_subtier = "FLASH"
                target_model = GEMINI_FLASH_MODEL_ID
                cost_demoted = True
                demotion_reason = f"cost_demote_pro_to_flash(budget={budget:.2f}<{COST_DEMOTE_PRO_USD:.2f})"
            if gemini_subtier == "FLASH" and budget < COST_DEMOTE_FLASH_USD:
                # Flash → Qwen local (free). Only demote if Qwen is available.
                if not context.provider_prohibited_qwen:
                    final_tier = HealTier.MEDIUM
                    gemini_subtier = ""
                    target_model = QWEN_LOCAL_MODEL_ID
                    qwen_cfg = self.TIER_CONFIG[HealTier.MEDIUM]
                    config = qwen_cfg
                    cost_demoted = True
                    demotion_reason = (
                        f"cost_demote_flash_to_qwen(budget={budget:.2f}<{COST_DEMOTE_FLASH_USD:.2f})"
                    )

        reasoning = (
            score.reasoning
            if gate_applied == "NO_OVERRIDE" and not cost_demoted
            else f"{score.reasoning} | gate:{gate_applied}"
            + (f" | {demotion_reason}" if cost_demoted else "")
        )

        decision = RoutingDecision(
            tier=final_tier,
            target_model=target_model,
            timeout_seconds=config["timeout"],
            max_tokens=config["max_tokens"],
            requires_sandbox=config["sandbox"],
            reasoning=reasoning,
            gate_applied=gate_applied,
            gemini_subtier=gemini_subtier,
            cost_demoted=cost_demoted,
        )

        # Wave F2 M2 (ADR-025): emit unified heal_router.v1.route span.
        # Best-effort — emitter failure must never break routing.
        try:
            _get_default_heal_router_emitter().emit_route_span(
                decision=decision,
                confidence_score=getattr(score, "score", None),
                app_name="healing_router",
                cost_budget_remaining_usd=budget,
            )
        except (
            AttributeError,
            TypeError,
            RuntimeError,
        ):  # guardian: allow-silent-swallow -- telemetry emission is best-effort; must never break the heal-router hot path
            pass

        return decision

    def dispatch_to_executor(
        self,
        decision: RoutingDecision,
        prompt: str,
        app_name: str = "healing_router",
    ) -> dict[str, Any]:
        """Dispatch a routing decision to its executor.

        Synchronous facade over the tier-specific backends. Returns a uniform
        shape regardless of tier:

            {
                "tier": "HIGH"|"MEDIUM"|"LOW"|"HITL",
                "executor": "deterministic"|"qwen_vllm"|"gemini_pro"|"hitl",
                "success": bool,
                "response": str | None,
                "model_used": str,
                "error": str | None,
            }

        MEDIUM tier calls `AppsQwenGateway.infer()` synchronously (via
        asyncio.run). HIGH returns a sentinel for the caller to run
        deterministic rules. LOW returns a sentinel identifying the Gemini
        client the caller should use (full wiring is Wave 5). HITL returns a
        sentinel instructing caller to raise an `ask_user_question`.
        """
        base: dict[str, Any] = {
            "tier": decision.tier.name,
            "success": False,
            "response": None,
            "model_used": decision.target_model,
            "error": None,
        }

        if decision.tier == HealTier.HIGH:
            base["executor"] = "deterministic"
            base["success"] = True
            return base

        if decision.tier == HealTier.MEDIUM:
            return {**base, **self._dispatch_qwen(prompt, app_name, decision)}

        if decision.tier == HealTier.LOW:
            return {**base, **self._dispatch_gemini(prompt, app_name, decision)}

        # HITL
        base["executor"] = "hitl"
        base["error"] = "human_review_required"
        return base

    def _dispatch_qwen(
        self,
        prompt: str,
        app_name: str,
        decision: RoutingDecision,
    ) -> dict[str, Any]:
        """Call QwenInferenceGateway.infer synchronously via the singleton.

        Wave B Phase B3 (qwen-adoption-waves-a7f3c2): switched from per-call
        ``AppsQwenGateway()`` instantiation to the process singleton
        ``get_qwen_inference_gateway()``. Per-call instantiation lost the
        connection pool and response cache on every heal; the singleton keeps
        them warm across the MEDIUM-tier heal queue.

        Uses ``asyncio.run()`` which owns the loop lifecycle. The singleton
        deliberately does NOT close on each call — it stays warm until
        ``close_qwen_inference_gateway()`` is invoked at process shutdown.
        """
        try:
            import asyncio  # noqa: PLC0415

            from agentic_core.L3_orchestration.inference.qwen_vllm.reasoning.qwen_inference_gateway import (  # noqa: PLC0415
                QwenInferenceRequest,
                get_qwen_inference_gateway,
            )

            request = QwenInferenceRequest(
                app_name=app_name,
                prompt=prompt,
                max_tokens=decision.max_tokens,
                temperature=0.1,
            )

            async def _run() -> Any:
                gw = await get_qwen_inference_gateway()
                return await gw.infer(request)

            response = asyncio.run(_run())

            return {
                "executor": "qwen_vllm",
                "success": bool(getattr(response, "success", False)),
                "response": getattr(response, "response", None),
                "model_used": getattr(response, "model_used", decision.target_model),
                "error": getattr(response, "error_message", None),
            }
        except (ImportError, RuntimeError, ValueError, OSError) as exc:
            return {
                "executor": "qwen_vllm",
                "success": False,
                "response": None,
                "model_used": decision.target_model,
                "error": f"qwen_dispatch_error: {type(exc).__name__}: {exc}",
            }

    def _dispatch_gemini(
        self,
        prompt: str,
        app_name: str,
        decision: RoutingDecision,
    ) -> dict[str, Any]:
        """Dispatch LOW-tier routing to Gemini Flash or Pro.

        Model is already resolved in `decision.target_model` (Flash for
        confidence-based LOW, Pro for structural/retry/hard-override gates —
        see `_PRO_REQUIRED_GATES`).

        Attempts a real call through `SovereignLLMGateway`. If the gateway is
        not provisioned (requires `secret_key`, provider registration), the
        call is skipped and the decision is returned as a dry-plan result.
        Callers that need the actual HTTP call must pass a pre-provisioned
        gateway via `self._gemini_gateway` (defaults to None).
        """
        executor = f"gemini_{decision.gemini_subtier.lower()}" if decision.gemini_subtier else "gemini"

        gateway = getattr(self, "_gemini_gateway", None)
        if gateway is None:
            # Dry-plan mode: gateway not provisioned. Return structured
            # decision so callers can dispatch externally.
            return {
                "executor": executor,
                "success": False,
                "response": None,
                "model_used": decision.target_model,
                "error": "gemini_gateway_not_provisioned",
                "dry_plan": True,
                "gemini_subtier": decision.gemini_subtier,
            }

        try:
            import asyncio  # noqa: PLC0415

            from agentic_core.interfaces.gateway import (  # noqa: PLC0415
                GenerationRequest,
            )

            request = GenerationRequest(
                prompt=prompt,
                agent_id=f"healing_router:{app_name}",
                provider="google",
                model=decision.target_model,
                max_tokens=decision.max_tokens,
            )

            async def _run() -> Any:
                return await gateway.route_generation(request)

            response = asyncio.run(_run())
            content = getattr(response, "content", None)

            return {
                "executor": executor,
                "success": content is not None,
                "response": content,
                "model_used": getattr(response, "model", decision.target_model),
                "error": None if content is not None else "gemini_empty_response",
                "gemini_subtier": decision.gemini_subtier,
            }
        except (ImportError, RuntimeError, ValueError, OSError, AttributeError) as exc:
            return {
                "executor": executor,
                "success": False,
                "response": None,
                "model_used": decision.target_model,
                "error": f"gemini_dispatch_error: {type(exc).__name__}: {exc}",
                "gemini_subtier": decision.gemini_subtier,
            }

    def get_tier_stats(self) -> dict[str, int]:
        """Get routing statistics by tier."""
        return {tier.name: count for tier, count in self._tier_stats.items()}

    def update_tier_config(
        self,
        tier: HealTier,
        model: str | None = None,
        timeout: int | None = None,
        max_tokens: int | None = None,
    ) -> None:
        """Update tier configuration.

        HITL-10C-003: Changes require approval.
        """
        if model:
            self.TIER_CONFIG[tier]["model"] = model
        if timeout:
            self.TIER_CONFIG[tier]["timeout"] = timeout
        if max_tokens:
            self.TIER_CONFIG[tier]["max_tokens"] = max_tokens
