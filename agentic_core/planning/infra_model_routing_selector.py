"""
Model selection orchestration for résumé processing workflows.

Coordinates policy evaluation and caching for optimal résumé improvement performance.
"""

from typing import Optional

from archives.legacy_root_folders.core.models.models import ExecutionProfile

from agentic_core.shared.cache import get_cached_choice, set_cached_choice
from shared.models import ModelChoice, RoutingContext
from archives.legacy_root_folders.infra.model_routing.policies import choose_provider_and_model, enforce_budget


def select_model(
    ctx: RoutingContext,
    *,
    requested_model: Optional[str] = None,
    execution_profile: Optional[ExecutionProfile] = None,
) -> ModelChoice:
    """
    Selects optimal model for résumé processing workflows with caching.

    Ensures efficient model choice and budget enforcement for comprehensive résumé enhancement.
    """

    cached = get_cached_choice(ctx)
    if cached is not None and requested_model is None:
        return cached

    base_choice = choose_provider_and_model(ctx, requested_model=requested_model)
    final_choice = enforce_budget(base_choice, execution_profile or ctx.execution_profile)

    if requested_model is None:
        set_cached_choice(ctx, final_choice)

    return final_choice



