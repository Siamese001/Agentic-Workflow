"""ConfidenceAwareExecutor — primary-path confidence-driven LLM dispatch.

Closes the G1/G4 gap surfaced in
``docs/archive/windsurf/legacy-tree/plans/qwen-confidence-routing-hardening-d4e7b1.md``:

  - G1 ``HealingRouter.dispatch_to_executor`` had zero in-prod callers — the
    unified dispatch seam existed but no app actually wired through it.
  - G4 Apps imported ``AppsQwenGateway`` directly for primary execution,
    bypassing confidence-tier routing. Confidence routing was heal-path-
    only.

This module gives apps a single entry point — ``execute(prompt, confidence,
app_name)`` — that routes by confidence to the same Qwen→Flash→Pro tiers
as the heal path, with the same TTL-cached vLLM health probe and Wave 1
cascade fallback. The classification rules mirror the heal-path
``ConfidenceScorer.score_to_tier`` thresholds so primary execution and
healing share one routing model.

Adoption is opt-in through env var ``USE_CONFIDENCE_AWARE_EXECUTOR=1`` so
no existing app behavior changes until apps are migrated incrementally.

Plan ref: ``docs/archive/windsurf/legacy-tree/plans/qwen-confidence-routing-hardening-d4e7b1.md`` Wave 3.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any

from agentic_core.L0_routing.config.model_registry import (  # guardian: allow-layer-violation -- L2 healer reads infra constants from L0 SSOT
    QWEN_LOCAL_MAX_MODEL_LEN,
)
from agentic_core.L2_execution.healers.healing_cascade_registry import (
    GEMINI_FLASH_MODEL_ID,
    GEMINI_PRO_MODEL_ID,
    QWEN_LOCAL_MODEL_ID,
)

from .confidence_scorer import HealTier
from .healing_router import HealingRouter, RoutingDecision

_LOGGER = logging.getLogger(__name__)

# Confidence thresholds for primary-path tier selection. Mirror the
# heal-path semantics so healing and primary execution converge on the same
# routing model. Values are float in [0.0, 1.0]; intervals are half-open
# left-inclusive on each tier boundary.
PRIMARY_HIGH_THRESHOLD: float = float(os.getenv("PRIMARY_HIGH_CONFIDENCE", "0.90"))
PRIMARY_MEDIUM_THRESHOLD: float = float(os.getenv("PRIMARY_MEDIUM_CONFIDENCE", "0.65"))
PRIMARY_LOW_PRO_THRESHOLD: float = float(os.getenv("PRIMARY_LOW_PRO_CONFIDENCE", "0.30"))

# Opt-in adoption flag. When unset/false, ``ConfidenceAwareExecutor`` MUST
# NOT be invoked by app orchestrators — they continue using
# ``AppsQwenGateway`` directly. Apps migrate one at a time.
ADOPTION_ENV: str = "USE_CONFIDENCE_AWARE_EXECUTOR"


def is_adoption_enabled() -> bool:
    """Return True when apps should use the confidence-aware executor."""
    raw = (os.getenv(ADOPTION_ENV) or "").strip().lower()
    return raw in ("1", "true", "yes", "on")


@dataclass(frozen=True)
class ExecutionResult:
    """Result of a confidence-aware execution call.

    Attributes:
        success: True if a tier successfully produced a response.
        response: Raw model output, or None on failure.
        tier_attempted: First tier the executor tried ("HIGH"/"MEDIUM"/"LOW").
        tier_used: Tier that actually produced the result. Differs from
            ``tier_attempted`` when cascade fallback occurred (e.g. MEDIUM
            attempted, LOW used because vLLM was down).
        model_used: Concrete model id (or DETERMINISTIC sentinel for HIGH).
        fallback_reason: Empty when no fallback; otherwise a short tag like
            "qwen_health_probe_failed" or "qwen_dispatch_error:RuntimeError".
        confidence: The float confidence input that drove the decision.
        error: None on success; short string on failure.
    """

    success: bool
    response: str | None
    tier_attempted: str
    tier_used: str
    model_used: str
    fallback_reason: str
    confidence: float
    error: str | None = None


def confidence_to_tier(confidence: float) -> tuple[HealTier, str]:
    """Map a float confidence in [0,1] to a HealTier and Gemini sub-tier.

    Returns:
        ``(tier, gemini_subtier)`` where ``gemini_subtier`` is "FLASH",
        "PRO", or "" (empty for non-LOW tiers).

    Thresholds (env-overridable, defaults):
      - confidence ≥ 0.90 → HIGH (deterministic, no LLM call)
      - 0.65 ≤ confidence < 0.90 → MEDIUM (Qwen local)
      - 0.30 ≤ confidence < 0.65 → LOW + FLASH (cheap cloud)
      - confidence < 0.30 → LOW + PRO (expensive cloud, structural reasoning)
    """
    if confidence >= PRIMARY_HIGH_THRESHOLD:
        return HealTier.HIGH, ""
    if confidence >= PRIMARY_MEDIUM_THRESHOLD:
        return HealTier.MEDIUM, ""
    if confidence >= PRIMARY_LOW_PRO_THRESHOLD:
        return HealTier.LOW, "FLASH"
    return HealTier.LOW, "PRO"


class ConfidenceAwareExecutor:
    """Primary-path executor that dispatches by float confidence in [0,1].

    Wraps ``HealingRouter`` so primary execution and healing share the same
    cascade-fallback machinery: vLLM health preflight, automatic Qwen→Flash
    demotion on failure, structured ``tier_attempted``/``tier_used`` /
    ``fallback_reason`` telemetry.

    Apps adopt by replacing direct ``AppsQwenGateway.infer`` calls with::

        executor = ConfidenceAwareExecutor()
        result = executor.execute(
            prompt=user_prompt,
            confidence=my_confidence_estimate,
            app_name="my_app",
        )

    Default max_tokens budget is sourced from the L0 SSOT
    ``QWEN_LOCAL_MAX_MODEL_LEN`` minus a 1024-token completion margin so
    callers can't accidentally request more than the running 32B-AWQ
    server allows. Override via ``max_tokens=`` kwarg.
    """

    DEFAULT_HIGH_TIMEOUT: int = 5
    DEFAULT_MEDIUM_TIMEOUT: int = 30
    DEFAULT_LOW_TIMEOUT: int = 60
    # Conservative completion budget — server max_model_len minus a
    # generous 1024-token prompt allowance.
    DEFAULT_MAX_COMPLETION_TOKENS: int = max(256, QWEN_LOCAL_MAX_MODEL_LEN - 1024)

    def __init__(self, router: HealingRouter | None = None) -> None:
        self._router = router or HealingRouter()
        self._call_count: int = 0

    @property
    def call_count(self) -> int:
        """Number of execute() calls served (for test assertions)."""
        return self._call_count

    def execute(
        self,
        prompt: str,
        confidence: float,
        app_name: str = "primary_executor",
        max_tokens: int | None = None,
    ) -> ExecutionResult:
        """Route a primary-path request to the tier matching ``confidence``.

        Args:
            prompt: The full prompt to dispatch. The executor does NOT
                tokenise — caller is responsible for staying under the
                model's max_model_len.
            confidence: Float in [0.0, 1.0]. Out-of-range values are
                clamped to the nearest endpoint and logged.
            app_name: Tag stamped on the gateway request for telemetry.
            max_tokens: Override the default completion budget.

        Returns:
            An :class:`ExecutionResult` with cascade telemetry stamped.
            Never raises — failures are returned in the result envelope.
        """
        clamped = self._clamp_confidence(confidence)
        tier, gemini_subtier = confidence_to_tier(clamped)
        self._call_count += 1

        if tier == HealTier.HIGH:
            return self._dispatch_high(prompt, app_name, clamped)

        # MEDIUM / LOW share the underlying _dispatch_qwen / _dispatch_gemini
        # plumbing; we synthesise a RoutingDecision so both paths return the
        # same enriched envelope shape.
        decision = self._build_decision(
            tier=tier,
            gemini_subtier=gemini_subtier,
            max_tokens=max_tokens or self.DEFAULT_MAX_COMPLETION_TOKENS,
            confidence=clamped,
        )

        if tier == HealTier.MEDIUM:
            raw = self._router._dispatch_qwen(prompt, app_name, decision)  # noqa: SLF001 -- intentional facade reuse
        else:  # HealTier.LOW
            raw = self._router._dispatch_gemini(prompt, app_name, decision)  # noqa: SLF001
            # _dispatch_gemini does not stamp tier_attempted by itself when
            # called directly (only the cascade path stamps); fill in here.
            raw.setdefault("tier_attempted", "LOW")
            raw.setdefault("tier_used", "LOW")
            raw.setdefault("fallback_reason", "")

        return ExecutionResult(
            success=bool(raw.get("success", False)),
            response=raw.get("response"),
            tier_attempted=raw.get("tier_attempted", tier.name),
            tier_used=raw.get("tier_used", tier.name),
            model_used=raw.get("model_used", decision.target_model),
            fallback_reason=raw.get("fallback_reason", ""),
            confidence=clamped,
            error=raw.get("error"),
        )

    # ---------------------------------------------------------- helpers
    @staticmethod
    def _clamp_confidence(value: float) -> float:
        if value < 0.0:
            _LOGGER.warning("confidence %.3f < 0.0; clamping to 0.0", value)
            return 0.0
        if value > 1.0:
            _LOGGER.warning("confidence %.3f > 1.0; clamping to 1.0", value)
            return 1.0
        return value

    @staticmethod
    def _dispatch_high(prompt: str, app_name: str, confidence: float) -> ExecutionResult:
        # HIGH tier is deterministic — caller is expected to already have a
        # rule-based answer. The executor returns a sentinel so the caller
        # knows to run its deterministic path instead of asking an LLM.
        del prompt, app_name  # unused; HIGH is local-deterministic
        return ExecutionResult(
            success=True,
            response=None,
            tier_attempted="HIGH",
            tier_used="HIGH",
            model_used="local_deterministic",
            fallback_reason="",
            confidence=confidence,
            error=None,
        )

    @staticmethod
    def _build_decision(
        tier: HealTier,
        gemini_subtier: str,
        max_tokens: int,
        confidence: float,
    ) -> RoutingDecision:
        if tier == HealTier.MEDIUM:
            target = QWEN_LOCAL_MODEL_ID
            timeout = ConfidenceAwareExecutor.DEFAULT_MEDIUM_TIMEOUT
        else:  # LOW
            target = GEMINI_PRO_MODEL_ID if gemini_subtier == "PRO" else GEMINI_FLASH_MODEL_ID
            timeout = ConfidenceAwareExecutor.DEFAULT_LOW_TIMEOUT
        return RoutingDecision(
            tier=tier,
            target_model=target,
            timeout_seconds=timeout,
            max_tokens=max_tokens,
            requires_sandbox=True,
            reasoning=f"primary_path_confidence={confidence:.3f}",
            gate_applied="PRIMARY_PATH",
            gemini_subtier=gemini_subtier,
            cost_demoted=False,
        )


def execute(
    prompt: str,
    confidence: float,
    app_name: str = "primary_executor",
    max_tokens: int | None = None,
) -> ExecutionResult:
    """Module-level convenience for one-shot calls.

    Apps that don't want to manage an executor instance can call this; a
    process-wide singleton router is reused so the Qwen connection pool
    stays warm across requests.
    """
    return _shared_executor().execute(
        prompt=prompt,
        confidence=confidence,
        app_name=app_name,
        max_tokens=max_tokens,
    )


_SINGLETON: dict[str, Any] = {}


def _shared_executor() -> ConfidenceAwareExecutor:
    inst = _SINGLETON.get("instance")
    if inst is None:
        inst = ConfidenceAwareExecutor()
        _SINGLETON["instance"] = inst
    return inst


def reset_for_tests() -> None:
    """Drop the shared executor singleton so tests start clean."""
    _SINGLETON.clear()


__all__ = [
    "ADOPTION_ENV",
    "ConfidenceAwareExecutor",
    "ExecutionResult",
    "PRIMARY_HIGH_THRESHOLD",
    "PRIMARY_LOW_PRO_THRESHOLD",
    "PRIMARY_MEDIUM_THRESHOLD",
    "confidence_to_tier",
    "execute",
    "is_adoption_enabled",
    "reset_for_tests",
]
