"""Bundled prompt-governance I0 mixins."""

from __future__ import annotations

import hashlib


class MixinNotFoundError(KeyError):
    """Raised when a requested bundled mixin id is not registered."""


_BUNDLED_MIXINS: dict[str, str] = {
    "agentic_persistence": (
        "# Mixin: agentic_persistence\n\n"
        "Continue until the requested objective is either complete or blocked by a concrete "
        "external dependency. Preserve evidence for every material decision and do not stop "
        "at analysis when execution is requested.\n"
    ),
    "tool_first": (
        "# Mixin: tool_first\n\n"
        "Use the repo-approved tool surface for observable work. Prefer direct verification "
        "over inference, capture the command or tool result, and keep external assumptions "
        "out of the final answer unless they were checked.\n"
    ),
    "plan_then_act": (
        "# Mixin: plan_then_act\n\n"
        "For multi-file or cross-layer work, state the planned edits and verification path "
        "before changing files. Once approved, execute the plan and update it only when new "
        "evidence changes the scope.\n"
    ),
}

BUNDLED_MIXIN_IDS: tuple[str, ...] = tuple(_BUNDLED_MIXINS)


def get_bundled_mixin(mixin_id: str) -> str:
    try:
        return _BUNDLED_MIXINS[mixin_id]
    except KeyError as exc:
        raise MixinNotFoundError(mixin_id) from exc


def is_bundled_mixin(mixin_id: str) -> bool:
    return mixin_id in _BUNDLED_MIXINS


def bundled_mixin_content_hash(mixin_id: str) -> str:
    content = get_bundled_mixin(mixin_id)
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


__all__ = [
    "BUNDLED_MIXIN_IDS",
    "MixinNotFoundError",
    "bundled_mixin_content_hash",
    "get_bundled_mixin",
    "is_bundled_mixin",
]
