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

import logging
import os
import time
import uuid
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

from .cascade_calibrator import (
    DecisionEvidence,
    brier_component,
    compute_decision_evidence,
    score_band_for,
)
from .confidence_scorer import ConfidenceScore, HealTier
from .failure_signal import FailureSignal
from .routing_gates import RoutingContext, apply_routing_gates
from .vllm_health_probe import is_qwen_available, probe as _vllm_probe

_LOGGER = logging.getLogger(__name__)

# Constitutional §29: closed-loop router enforcement marker name.
_ROUTER_LEDGER_NAME: str = "router_l2_cascade"

# Wave 1 (qwen-confidence-routing-hardening-d4e7b1): cascade-fallback toggle.
# When set to a truthy value, _dispatch_qwen will NOT fall through to Gemini
# Flash on Qwen unavailability — preserves prior behavior for callers that
# manage retries themselves.
_DISABLE_QWEN_FALLBACK_ENV: str = "DISABLE_QWEN_FALLBACK"


def _qwen_fallback_disabled() -> bool:
    """Read the env-var fallback opt-out (any truthy value disables fallback)."""
    raw = (os.getenv(_DISABLE_QWEN_FALLBACK_ENV) or "").strip().lower()
    return raw in ("1", "true", "yes", "on")


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
    """Healing routing decision.

    Constitutional §29 fields (W5.1 — l2-cascade-router-closed-loop-wiring):
      - ``decision_id`` is the canonical id binding a prediction row to its
        late-arriving outcome row in ``artifacts/ledgers/router_l2_cascade.sqlite``.
        Empty string when ledger emission was suppressed (bypass / write failed).
      - ``predicted_p_success`` is the calibrated prior the router used to
        choose this tier. Defaults to ``ConfidenceScore.score`` (the heuristic
        bootstrap prior) until a learned posterior replaces it.
      - ``eu_score`` is the Expected Utility used to break ties between tiers.
      - ``ledger_event_id`` is the deterministic SHA-256 prefix returned by the
        ledger writer; used by ``dispatch_to_executor`` to bind outcomes.
    """

    tier: HealTier
    target_model: str
    timeout_seconds: int
    max_tokens: int
    requires_sandbox: bool
    reasoning: str
    gate_applied: str = "NO_OVERRIDE"
    gemini_subtier: str = ""  # "" | "FLASH" | "PRO" — populated for LOW tier only
    cost_demoted: bool = False  # Wave 6 P6.2: True when budget pressure forced a tier downgrade
    # Constitutional §29 fields — all default to empty/zero so legacy callers
    # constructing `RoutingDecision` directly are unaffected.
    decision_id: str = ""
    predicted_p_success: float = 0.0
    eu_score: float = 0.0
    ledger_event_id: str = ""


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

        # Constitutional §29 — closed-loop router evidence. Compute the
        # decision evidence bundle BEFORE constructing RoutingDecision so the
        # decision can carry its own decision_id / predicted_p_success / eu_score.
        # Failure of the evidence path must NEVER break routing — fall back to
        # zero-valued fields so legacy callers continue to work.
        evidence: DecisionEvidence | None = None
        try:
            evidence = compute_decision_evidence(
                tier=final_tier,
                gemini_subtier=gemini_subtier,
                target_model=target_model,
                confidence_input=getattr(score, "score", 0.0),
                failure_class=getattr(getattr(signal, "failure_class", None), "name", "UNKNOWN"),
                source_layer=getattr(signal, "source_layer", "") or "unknown",
                error_code=getattr(signal, "error_code", "") or "unknown",
                retry_count=getattr(signal, "retry_count", 0),
            )
        except (
            AttributeError,
            TypeError,
            ValueError,
        ):  # guardian: allow-log-and-swallow -- evidence is best-effort; routing must never break
            _LOGGER.debug("cascade_calibrator.compute_decision_evidence failed", exc_info=True)
            evidence = None

        decision_id = uuid.uuid4().hex if evidence is not None else ""
        predicted_p = evidence.predicted_p_success if evidence is not None else 0.0
        eu_score = evidence.eu_score if evidence is not None else 0.0

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
            decision_id=decision_id,
            predicted_p_success=predicted_p,
            eu_score=eu_score,
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

        # Constitutional §29 — emit ROUTER_DECISION marker + ledger row.
        # Both calls are wrapped in fail-soft helpers below.
        if evidence is not None:
            ledger_event_id = self._emit_router_decision(
                decision=decision,
                evidence=evidence,
                signal=signal,
                cost_budget_remaining_usd=budget,
                app_name="healing_router",
            )
            decision.ledger_event_id = ledger_event_id

        return decision

    # ------------------------------------------------------------------ #
    # Constitutional §29 — closed-loop router emission helpers
    # ------------------------------------------------------------------ #
    def _emit_router_decision(
        self,
        *,
        decision: RoutingDecision,
        evidence: DecisionEvidence,
        signal: FailureSignal,
        cost_budget_remaining_usd: float | None,
        app_name: str,
    ) -> str:
        """Write the ``route_decision`` row + emit the ``ROUTER_DECISION:`` marker.

        Both operations are fail-soft: any error path returns an empty event_id
        and the routing continues. This satisfies the §29 contract:

            ROUTER_DECISION: layer=L2 router=cascade decision_id=<uuid>
                trace_id=<id> route_id=<id> selected=<model> tier=<TIER>
                provider=<provider> eu_score=<float> brier_score=<float>

        The Brier score on a *prediction-only* row is the best-case 0.0 — the
        true Brier is only computable once outcome is bound. We log a sentinel
        ``brier_score=pending`` until ``_bind_router_outcome`` updates the row.
        """
        # Optional vLLM probe state — best-effort only.
        vllm_healthy: bool | None = None
        try:
            if decision.tier == HealTier.MEDIUM:
                vllm_healthy = bool(_vllm_probe().is_healthy)
        except (RuntimeError, OSError):  # guardian: allow-log-and-swallow -- probe is best-effort; routing must not break on network errors
            vllm_healthy = None

        prediction = evidence.to_prediction_dict(
            decision_id=decision.decision_id,
            tier=decision.tier,
            target_model=decision.target_model,
            gate_applied=decision.gate_applied,
            gemini_subtier=decision.gemini_subtier,
            cost_demoted=decision.cost_demoted,
            confidence_input=evidence.predicted_p_success,
            cost_budget_remaining_usd=cost_budget_remaining_usd,
            app_name=app_name,
            vllm_healthy=vllm_healthy,
        )

        # Emit the §29 marker FIRST so the audit trail exists even if the
        # ledger write fails on this turn.
        _LOGGER.info(
            "ROUTER_DECISION: layer=L2 router=cascade decision_id=%s "
            "trace_id=%s route_id=%s selected=%s tier=%s provider=%s "
            "eu_score=%.4f brier_score=pending gate=%s confidence=%.4f",
            decision.decision_id,
            getattr(signal, "signal_hash", "") or decision.decision_id,
            app_name,
            decision.target_model,
            decision.tier.name,
            evidence.provider,
            evidence.eu_score,
            decision.gate_applied,
            evidence.predicted_p_success,
        )

        # Write the durable ledger row.
        try:
            from tools.ledgers.hook_helpers import emit_ledger_event  # noqa: PLC0415  # guardian: allow-layer-violation -- L2 healer writes to repo-level ledger SSOT (additive only)

            event_id = emit_ledger_event(
                ledger=_ROUTER_LEDGER_NAME,
                event_kind="route_decision",
                prediction=prediction,
                outcome=None,
                score_band="unbound",
                score_numeric=None,
                repo_area="agentic_core/L2_execution/healers/healing_router.py",
                metadata={
                    "router": "L2/cascade",
                    "constitutional_rule": "§29",
                    "signal_hash": getattr(signal, "signal_hash", ""),
                    "retry_count": int(getattr(signal, "retry_count", 0)),
                },
            )
            return event_id or ""
        except (
            ImportError,
            AttributeError,
            TypeError,
            ValueError,
            RuntimeError,
            OSError,
        ):  # guardian: allow-log-and-swallow -- ledger write is best-effort; routing must never break
            _LOGGER.debug("router_l2_cascade ledger emit failed", exc_info=True)
            return ""

    def _bind_router_outcome(
        self,
        decision: RoutingDecision,
        result: dict[str, Any],
        *,
        latency_ms: int,
    ) -> None:
        """Bind a dispatch result to its predicted ledger row.

        Computes Brier component and TP/FP/TN/FN band. Fail-soft: any error
        leaves the prediction row in ``status='predicted'`` for later sweeps.
        """
        if not decision.ledger_event_id:
            return
        success = bool(result.get("success", False))
        outcome = {
            "success": success,
            "tier_attempted": result.get("tier_attempted") or decision.tier.name,
            "tier_used": result.get("tier_used") or decision.tier.name,
            "fallback_reason": result.get("fallback_reason", "") or "",
            "model_used": result.get("model_used") or decision.target_model,
            "latency_ms": int(latency_ms),
            "cost_usd_observed": None,
            "error_code": result.get("error"),
            "response_len_bytes": (
                len(result["response"]) if isinstance(result.get("response"), str) else None
            ),
            "downstream_judge_score": None,
        }
        try:
            brier = brier_component(decision.predicted_p_success, success)
            band = score_band_for(decision.predicted_p_success, success)
        except (TypeError, ValueError):
            brier = None
            band = None

        try:
            from tools.ledgers.hook_helpers import bind_ledger_outcome  # noqa: PLC0415  # guardian: allow-layer-violation -- L2 healer binds outcome on repo-level ledger SSOT

            bind_ledger_outcome(
                ledger=_ROUTER_LEDGER_NAME,
                event_id=decision.ledger_event_id,
                outcome=outcome,
                score_band=band,
                score_numeric=brier,
                latency_ms=int(latency_ms),
            )
            _LOGGER.info(
                "ROUTER_OUTCOME: decision_id=%s success=%s band=%s brier=%s latency_ms=%d",
                decision.decision_id,
                success,
                band,
                f"{brier:.4f}" if brier is not None else "n/a",
                int(latency_ms),
            )
        except (
            ImportError,
            AttributeError,
            TypeError,
            ValueError,
            RuntimeError,
            OSError,
        ):  # guardian: allow-log-and-swallow -- outcome binding is best-effort; dispatch must not fail because of telemetry
            _LOGGER.debug("router_l2_cascade outcome bind failed", exc_info=True)

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

        # Constitutional §29: time the dispatch and bind the outcome row.
        t_start = time.time()

        if decision.tier == HealTier.HIGH:
            base["executor"] = "deterministic"
            base["success"] = True
            result = base
        elif decision.tier == HealTier.MEDIUM:
            result = {**base, **self._dispatch_qwen(prompt, app_name, decision)}
        elif decision.tier == HealTier.LOW:
            result = {**base, **self._dispatch_gemini(prompt, app_name, decision)}
        else:
            # HITL
            base["executor"] = "hitl"
            base["error"] = "human_review_required"
            result = base

        latency_ms = int((time.time() - t_start) * 1000)
        # Bind outcome row to its prediction. Fail-soft inside the helper.
        self._bind_router_outcome(decision, result, latency_ms=latency_ms)
        return result

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

        Wave 1 (qwen-confidence-routing-hardening-d4e7b1): now does a fast
        TTL-cached vLLM health preflight; on negative health (or on a real
        dispatch failure) it cascades to Gemini Flash unless the env var
        ``DISABLE_QWEN_FALLBACK`` is truthy. The result dict gains optional
        ``tier_attempted``, ``tier_used``, and ``fallback_reason`` fields so
        callers can observe and calibrate.
        """
        fallback_disabled = _qwen_fallback_disabled()

        # --- Preflight: fast cached health probe -----------------------------
        if not fallback_disabled and not is_qwen_available():
            return self._fallback_qwen_to_flash(
                prompt=prompt,
                app_name=app_name,
                decision=decision,
                fallback_reason="qwen_health_probe_failed",
            )

        # --- Live dispatch ---------------------------------------------------
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

            success = bool(getattr(response, "success", False))
            if not success and not fallback_disabled:
                # Live dispatch returned a non-success envelope; demote.
                err_msg = getattr(response, "error_message", None) or "qwen_unsuccessful"
                return self._fallback_qwen_to_flash(
                    prompt=prompt,
                    app_name=app_name,
                    decision=decision,
                    fallback_reason=f"qwen_unsuccessful:{err_msg}",
                )

            return {
                "executor": "qwen_vllm",
                "success": success,
                "response": getattr(response, "response", None),
                "model_used": getattr(response, "model_used", decision.target_model),
                "error": getattr(response, "error_message", None),
                "tier_attempted": "MEDIUM",
                "tier_used": "MEDIUM",
                "fallback_reason": "",
            }
        except (ImportError, RuntimeError, ValueError, OSError) as exc:
            if fallback_disabled:
                return {
                    "executor": "qwen_vllm",
                    "success": False,
                    "response": None,
                    "model_used": decision.target_model,
                    "error": f"qwen_dispatch_error: {type(exc).__name__}: {exc}",
                    "tier_attempted": "MEDIUM",
                    "tier_used": "MEDIUM",
                    "fallback_reason": "",
                }
            return self._fallback_qwen_to_flash(
                prompt=prompt,
                app_name=app_name,
                decision=decision,
                fallback_reason=f"qwen_dispatch_error:{type(exc).__name__}",
            )

    def _fallback_qwen_to_flash(
        self,
        prompt: str,
        app_name: str,
        decision: RoutingDecision,
        fallback_reason: str,
    ) -> dict[str, Any]:
        """Demote a MEDIUM-tier dispatch to Gemini Flash and stamp telemetry.

        Wave 1: synthetic LOW-tier decision constructed inline so we reuse
        the existing ``_dispatch_gemini`` plumbing and Provider enum without
        any code duplication. The synthetic decision carries
        ``gemini_subtier="FLASH"`` because cascade demotion always lands on
        Flash (Pro is reserved for structural-failure gates).
        """
        flash_decision = RoutingDecision(
            tier=HealTier.LOW,
            target_model=GEMINI_FLASH_MODEL_ID,
            timeout_seconds=self.TIER_CONFIG[HealTier.LOW]["timeout"],
            max_tokens=decision.max_tokens,
            requires_sandbox=True,
            reasoning=f"{decision.reasoning} | cascade:{fallback_reason}",
            gate_applied=decision.gate_applied,
            gemini_subtier="FLASH",
            cost_demoted=False,
        )
        result = self._dispatch_gemini(prompt, app_name, flash_decision)
        # Stamp cascade telemetry so callers can attribute the demotion.
        result["tier_attempted"] = "MEDIUM"
        result["tier_used"] = "LOW"
        result["fallback_reason"] = fallback_reason
        return result

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
