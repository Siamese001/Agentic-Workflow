"""Anthropic prompt-caching helpers.

Transforms a flat (system_prompt, user_prompt) pair into Anthropic Messages-API
structured-content shape with `cache_control=ephemeral` markers applied to the
static prefix. Per Anthropic, cache reads cost ~10% of the equivalent input
tokens and cache writes cost ~125% — break-even at the first reuse.

Reference:
  https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching

Cache-boundary convention:
  - System prompt is ALWAYS cached when non-empty (it is static by definition).
  - The user turn is split at `cache_boundary_hint`:
      * prefix (0..boundary)          -> text block with cache_control
      * suffix (boundary..end)        -> text block, no cache_control
  - When `cache_boundary_hint == -1`, no boundary is applied and the whole
    user turn is uncached. Callers that produce prompts via
    `anthropic_prompt_renderer.render_anthropic_prompt` pass the renderer's
    `cache_boundary_hint` directly.

Cache TTL:
  - 5m (default) — cheaper, evicted faster
  - 1h — expensive write, survives slow multi-turn flows

Design invariants:
  - Pure functions. No I/O, no gateway calls. Caller ships the dict to
    Anthropic Messages API.
  - Minimum cacheable block: Anthropic requires ≥1024 tokens for Sonnet/Opus,
    ≥2048 for Haiku. We cannot verify token counts here (no tokenizer), so we
    apply a conservative character-count heuristic. Callers below the
    threshold get a WARNING-level log and the cache marker is stripped to
    avoid silent API errors.
  - cache_control markers use the `ephemeral` type. `persistent` caching is
    not yet supported by Anthropic for general-availability tenants.

This module intentionally does NOT know about PromptEnvelope — it operates
on already-rendered strings so it composes with any prompt-assembly path
(anthropic_prompt_renderer, legacy PromptTemplate, inline strings).
"""

from __future__ import annotations

import logging
from typing import Any, Literal

Logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# TTL constants
# ---------------------------------------------------------------------------

CACHE_TTL_5M: Literal["5m"] = "5m"
CACHE_TTL_1H: Literal["1h"] = "1h"

# Conservative minimum-chars threshold. Anthropic requires ≥1024 tokens for
# Sonnet/Opus. Using 4 chars/token rough ratio -> ~4096 chars. We pick 3500 as
# a safety margin above the boundary so callers slightly over the threshold
# still benefit.
_MIN_CACHEABLE_CHARS = 3500


def _cache_control(ttl: str) -> dict[str, str]:
    """Build a cache_control marker dict.

    5m is the implicit default in Anthropic's API; specifying it explicitly
    makes the request shape self-documenting.
    """
    if ttl == CACHE_TTL_1H:
        return {"type": "ephemeral", "ttl": "1h"}
    return {"type": "ephemeral"}


def _is_cacheable(text: str) -> bool:
    """Heuristic: is the block long enough to benefit from caching?

    Anthropic rejects cache_control on blocks below the minimum-token
    threshold with a 400 error. We skip the marker on small blocks rather
    than risk an API failure.
    """
    return len(text) >= _MIN_CACHEABLE_CHARS


def build_system_blocks(
    system_prompt: str,
    *,
    cache: bool = True,
    ttl: str = CACHE_TTL_5M,
) -> list[dict[str, Any]]:
    """Render a system prompt into Anthropic structured-content blocks.

    Parameters
    ----------
    system_prompt:
        The system prompt string. Empty/whitespace returns an empty list.
    cache:
        When True (default), marks the block with cache_control. When False,
        emits a plain text block (useful for testing / short prompts).
    ttl:
        Either CACHE_TTL_5M or CACHE_TTL_1H.

    Returns
    -------
    List of content blocks ready to assign to `system=...` on the Messages API.
    Empty list when system_prompt is empty (Anthropic accepts omitted system).
    """
    text = (system_prompt or "").strip()
    if not text:
        return []

    block: dict[str, Any] = {"type": "text", "text": text}
    if cache and _is_cacheable(text):
        block["cache_control"] = _cache_control(ttl)
    elif cache:
        Logger.debug(
            "System block (%d chars) below cacheable threshold %d; skipping cache_control",
            len(text),
            _MIN_CACHEABLE_CHARS,
        )
    return [block]


def build_user_content(
    prompt: str,
    *,
    cache_boundary_hint: int = -1,
    cache_prefix: bool = True,
    ttl: str = CACHE_TTL_5M,
) -> list[dict[str, Any]]:
    """Split a user-turn prompt at `cache_boundary_hint` with cache_control.

    Parameters
    ----------
    prompt:
        The full user-turn text. Typically the output of
        `render_anthropic_prompt(...)`.
    cache_boundary_hint:
        Byte offset at which to split. `-1` disables splitting (whole prompt
        uncached). `0` or `>= len(prompt)` also disable splitting.
    cache_prefix:
        When True (default) and boundary is valid, applies cache_control to
        the prefix block. When False, splits at the boundary but without any
        cache markers (useful for measuring latency without cache).
    ttl:
        Either CACHE_TTL_5M or CACHE_TTL_1H.

    Returns
    -------
    List of 1 or 2 content blocks:
      - 1 block when boundary is invalid/absent (whole prompt, no cache).
      - 2 blocks when boundary is valid (prefix + suffix).
    """
    if not prompt:
        return []

    # Invalid or no-op boundary: single uncached block
    if cache_boundary_hint <= 0 or cache_boundary_hint >= len(prompt):
        return [{"type": "text", "text": prompt}]

    prefix = prompt[:cache_boundary_hint]
    suffix = prompt[cache_boundary_hint:]

    # Never produce empty suffix blocks (Anthropic rejects them)
    if not suffix.strip():
        return [{"type": "text", "text": prompt}]

    prefix_block: dict[str, Any] = {"type": "text", "text": prefix}
    if cache_prefix and _is_cacheable(prefix):
        prefix_block["cache_control"] = _cache_control(ttl)
    elif cache_prefix:
        Logger.debug(
            "Prefix block (%d chars) below cacheable threshold %d; skipping cache_control",
            len(prefix),
            _MIN_CACHEABLE_CHARS,
        )

    return [prefix_block, {"type": "text", "text": suffix}]


def build_messages_payload(
    user_prompt: str,
    *,
    system_prompt: str = "",
    cache_boundary_hint: int = -1,
    ttl: str = CACHE_TTL_5M,
    cache_system: bool = True,
    cache_prefix: bool = True,
) -> dict[str, Any]:
    """Convenience composer: build the `system` + `messages` fields.

    Returns a dict suitable for spreading into `client.messages.create(...)`:

        payload = build_messages_payload(user_prompt=p, system_prompt=s, cache_boundary_hint=b)
        response = client.messages.create(model=m, max_tokens=k, **payload)

    The returned dict never contains a `model` or `max_tokens` key — the
    caller owns those; this helper only handles cache-aware content shaping.
    """
    system_blocks = build_system_blocks(system_prompt, cache=cache_system, ttl=ttl)
    user_content = build_user_content(
        user_prompt,
        cache_boundary_hint=cache_boundary_hint,
        cache_prefix=cache_prefix,
        ttl=ttl,
    )

    payload: dict[str, Any] = {
        "messages": [{"role": "user", "content": user_content}],
    }
    if system_blocks:
        payload["system"] = system_blocks
    return payload


def count_cache_markers(payload: dict[str, Any]) -> int:
    """Utility for tests/telemetry: count cache_control markers in a payload."""
    count = 0
    for block in payload.get("system", []) or []:
        if isinstance(block, dict) and "cache_control" in block:
            count += 1
    for msg in payload.get("messages", []) or []:
        for block in msg.get("content", []) or []:
            if isinstance(block, dict) and "cache_control" in block:
                count += 1
    return count


__all__ = [
    "CACHE_TTL_5M",
    "CACHE_TTL_1H",
    "build_messages_payload",
    "build_system_blocks",
    "build_user_content",
    "count_cache_markers",
]
