from __future__ import annotations

from typing import Optional

from models import ExecutionProfile

from .models import ModelChoice, RoutingContext


def _infer_provider_from_model(model: str) -> str:
    m = (model or "").lower()
    if "claude" in m:
        return "anthropic"
    if "gemini" in m or "google" in m:
        return "google"
    return "openai"


def choose_provider_and_model(
    ctx: RoutingContext,
    requested_model: Optional[str] = None,
) -> ModelChoice:
    """Select provider/model for a given routing context.

    Current implementation is conservative: if a concrete model is
    provided, we honor it and only infer the provider. If not, we fall
    back to a simple heuristic based on task_type.
    """

    model = requested_model or "gpt-4.1-mini"
    provider = _infer_provider_from_model(model)

    cost_tier = "medium"
    latency_ms = 800

    task = ctx.task_type
    if task in {"retrieval", "qa", "safety"}:
        cost_tier = "medium"
        latency_ms = 700
    if task in {"drafting", "deep_reasoning"}:
        cost_tier = "high"
        latency_ms = 1200
    if task in {"metadata", "classifier"}:
        cost_tier = "low"
        latency_ms = 400

    estimated_cost = {"low": 0.001, "medium": 0.002, "high": 0.004}[cost_tier]

    return ModelChoice(
        provider=provider,
        model_name=model,
        cost_tier=cost_tier,
        estimated_cost=estimated_cost,
        latency_ms=latency_ms,
    )


def enforce_budget(choice: ModelChoice, profile: Optional[ExecutionProfile]) -> ModelChoice:
    """Clamp cost tier based on execution profile, if provided.

    The ExecutionProfile.metadata may include a "max_cost_tier" key with
    values like "low" | "medium" | "high". If the chosen tier exceeds
    this, we downgrade to the allowed tier.
    """

    if profile is None:
        return choice

    max_tier = (profile.metadata or {}).get("max_cost_tier")
    if not max_tier:
        return choice

    order = {"low": 0, "medium": 1, "high": 2}
    current = order.get(choice.cost_tier, 1)
    allowed = order.get(max_tier, current)

    if current <= allowed:
        return choice

    # Downgrade to allowed tier by adjusting cost/latency; we keep
    # provider/model_name untouched for compatibility.
    if allowed == order["low"]:
        cost_tier = "low"
        estimated_cost = 0.001
        latency_ms = max(200, int(choice.latency_ms * 0.6))
    else:
        cost_tier = "medium"
        estimated_cost = 0.002
        latency_ms = max(400, int(choice.latency_ms * 0.8))

    return ModelChoice(
        provider=choice.provider,
        model_name=choice.model_name,
        cost_tier=cost_tier,
        estimated_cost=estimated_cost,
        latency_ms=latency_ms,
    )


def fallback_chain(choice: ModelChoice) -> list[ModelChoice]:
    """Return a simple deterministic fallback chain for the given choice."""

    fallbacks: list[ModelChoice] = [choice]

    if choice.provider == "openai":
        fallbacks.append(
            ModelChoice(
                provider="anthropic",
                model_name=choice.model_name,
                cost_tier=choice.cost_tier,
                estimated_cost=choice.estimated_cost,
                latency_ms=choice.latency_ms + 200,
            )
        )
    elif choice.provider == "anthropic":
        fallbacks.append(
            ModelChoice(
                provider="openai",
                model_name=choice.model_name,
                cost_tier=choice.cost_tier,
                estimated_cost=choice.estimated_cost,
                latency_ms=choice.latency_ms + 200,
            )
        )

    return fallbacks


def choose_model(ctx: RoutingContext) -> ModelChoice:
    """Phase-3 wrapper returning a ModelChoice for a RoutingContext.

    This delegates to the existing choose_provider_and_model helper while
    keeping a minimal, ExecutionProfile-free signature as requested by the
    new safety/observability/cost layer.
    """

    return choose_provider_and_model(ctx, requested_model=None)


def enforce_cost_budget(choice: ModelChoice, profile: Optional[ExecutionProfile]) -> ModelChoice:
    """Phase-3 wrapper over enforce_budget to match the new API surface."""

    return enforce_budget(choice, profile)
