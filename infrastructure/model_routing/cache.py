"""
Model routing cache for résumé processing workflows.

Provides efficient model choice caching to optimize résumé improvement performance.
"""

from typing import Dict, Tuple

from .models import ModelChoice, RoutingContext


_CACHE: Dict[Tuple[str, str, str], ModelChoice] = {}


def _key(ctx: RoutingContext) -> Tuple[str, str, str]:
    """
    Generates cache key for résumé processing model routing.

    Ensures consistent cache indexing for optimal résumé improvement performance.
    """
    profile_name = ctx.execution_profile.name if ctx.execution_profile else "default"
    return (ctx.agent_id, ctx.task_type, profile_name)


def get_cached_choice(ctx: RoutingContext) -> ModelChoice | None:
    """
    Retrieves cached model choice for résumé processing workflows.

    Optimizes performance by avoiding redundant routing decisions for résumé improvement.
    """
    return _CACHE.get(_key(ctx))


def set_cached_choice(ctx: RoutingContext, choice: ModelChoice) -> None:
    """
    Caches model choice for résumé processing workflows.

    Ensures efficient routing for subsequent résumé improvement operations.
    """
    _CACHE[_key(ctx)] = choice



