from __future__ import annotations

from typing import Dict, Tuple

from .models import ModelChoice, RoutingContext


_CACHE: Dict[Tuple[str, str, str], ModelChoice] = {}


def _key(ctx: RoutingContext) -> Tuple[str, str, str]:
    profile_name = ctx.execution_profile.name if ctx.execution_profile else "default"
    return (ctx.agent_id, ctx.task_type, profile_name)


def get_cached_choice(ctx: RoutingContext) -> ModelChoice | None:
    return _CACHE.get(_key(ctx))


def set_cached_choice(ctx: RoutingContext, choice: ModelChoice) -> None:
    _CACHE[_key(ctx)] = choice
