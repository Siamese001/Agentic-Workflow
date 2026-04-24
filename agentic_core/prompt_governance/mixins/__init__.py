"""I0 mixin bank — EQ-10 (ADR-PROMPT-ASSEMBLY-002 §3, §4, §5).

Three bundled I0 mixins aligned with Anthropic / OpenAI / Google agentic
guidance:

- ``agentic_persistence``: keep going until the request is fully resolved
- ``tool_first``: prefer a tool call over an assumption
- ``plan_then_act``: write a short ordered plan before side-effecting

The mixins are opt-in per ``AgentSpec.mixins_required``. Nothing in this
package is registered by default — callers must explicitly request a
mixin ID to include its content in the rendered prompt.

Design:
- Content lives in sibling ``<mixin_id>.md`` files so it is reviewable
  in code review as prose, not string literals.
- :func:`get_bundled_mixin` reads and caches content at first access.
- :data:`BUNDLED_MIXIN_IDS` is the canonical registry — iterating it is
  how consumers discover which mixins are available without touching
  disk.
- :func:`bundled_mixin_content_hash` gives a stable SHA-256 of each
  mixin body so regression tests can detect accidental rewrites.
"""

from __future__ import annotations

import hashlib
from functools import lru_cache
from pathlib import Path

_HERE = Path(__file__).resolve().parent


BUNDLED_MIXIN_IDS: tuple[str, ...] = (
    "agentic_persistence",
    "tool_first",
    "plan_then_act",
)


class MixinNotFoundError(KeyError):
    """Raised when a requested mixin ID is not in the bundled bank."""


def _mixin_path(mixin_id: str) -> Path:
    return _HERE / f"{mixin_id}.md"


@lru_cache(maxsize=len(BUNDLED_MIXIN_IDS) * 2)
def get_bundled_mixin(mixin_id: str) -> str:
    """Return the bundled content for ``mixin_id``.

    Raises :class:`MixinNotFoundError` when ``mixin_id`` is not a
    recognized bundled mixin. Content is cached after first read so
    hot paths do not hit disk repeatedly.
    """
    if mixin_id not in BUNDLED_MIXIN_IDS:
        raise MixinNotFoundError(
            f"{mixin_id!r} is not a bundled mixin; known: {BUNDLED_MIXIN_IDS}"
        )
    path = _mixin_path(mixin_id)
    return path.read_text(encoding="utf-8")


def bundled_mixin_content_hash(mixin_id: str) -> str:
    """Return SHA-256 of the bundled mixin body.

    Useful for regression tests that want to detect accidental content
    drift without re-inlining the full mixin text in the test fixture.
    """
    content = get_bundled_mixin(mixin_id)
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def is_bundled_mixin(mixin_id: str) -> bool:
    """Cheap membership test; avoids disk IO."""
    return mixin_id in BUNDLED_MIXIN_IDS


__all__ = [
    "BUNDLED_MIXIN_IDS",
    "MixinNotFoundError",
    "get_bundled_mixin",
    "bundled_mixin_content_hash",
    "is_bundled_mixin",
]
