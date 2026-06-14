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
  - Minimum cacheable block is MODEL-SPECIFIC (Opus 4.x / Haiku 4.5 = 4096
    tokens; Fable 5 / Sonnet 4.6 = 2048; Sonnet 4.5 and earlier = 1024). A
    block below its model's floor is silently NOT cached by Anthropic
    (cache_creation_input_tokens stays 0, no error). We cannot verify token
    counts here (no tokenizer — this module is pure/no-I/O), so callers pass a
    model id and we apply a per-model character heuristic (~4 chars/token);
    below the floor the cache marker is stripped and a DEBUG log is emitted.
    Pass no model to keep the legacy conservative default. See
    ``min_cacheable_chars`` / ``MODEL_CACHE_FLOOR_TOKENS``.
  - cache_control markers use the `ephemeral` type. `persistent` caching is
    not yet supported by Anthropic for general-availability tenants.

This module intentionally does NOT know about PromptEnvelope — it operates
on already-rendered strings so it composes with any prompt-assembly path
(anthropic_prompt_renderer, legacy PromptTemplate, inline strings).
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Any, Literal, Sequence

Logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# TTL constants
# ---------------------------------------------------------------------------

CACHE_TTL_5M: Literal["5m"] = "5m"
CACHE_TTL_1H: Literal["1h"] = "1h"

# ---------------------------------------------------------------------------
# Model-aware minimum cacheable size (P3 — plan prompt-cache-anthropic-best-practice-c7a1e9 W2)
# ---------------------------------------------------------------------------
#
# Anthropic's minimum cacheable PREFIX is model-specific. A block shorter than
# its model's floor is silently NOT cached (cache_creation_input_tokens == 0,
# no error). Authoritative minimums (claude-api prompt-caching reference):
#
#   Opus 4.8 / 4.7 / 4.6 / 4.5, Haiku 4.5 ........ 4096 tokens
#   Fable 5, Sonnet 4.6, Haiku 3.5 / 3 ........... 2048 tokens
#   Sonnet 4.5 / 4.1 / 4 / 3.7 ................... 1024 tokens
#
# This module is pure (no tokenizer / no I/O by contract), so we convert the
# token floor to characters at ~4 chars/token. Callers needing exactness can
# pre-check with ``client.messages.count_tokens(...)`` and skip caching.
_CHARS_PER_TOKEN = 4

# Floor when the model is unknown (model=None). Preserves the pre-W2 behavior
# (3500-char / ~875-token boundary) so existing callers are unaffected. NOTE:
# 875 tokens is below EVERY current model's real floor — the model-aware path
# (pass a model id) is what actually fixes the silent non-caching.
_DEFAULT_MIN_CACHEABLE_CHARS = 3500

# (model-id substring, min cacheable tokens), most-specific FIRST so e.g.
# ``claude-haiku-4-5`` resolves to 4096 before the generic ``claude-haiku``
# (2048), and ``claude-sonnet-4-6`` (2048) before ``claude-sonnet`` (1024).
MODEL_CACHE_FLOOR_TOKENS: tuple[tuple[str, int], ...] = (
    ("claude-haiku-4-5", 4096),
    ("claude-opus", 4096),
    ("claude-sonnet-4-6", 2048),
    ("claude-fable", 2048),
    ("claude-haiku", 2048),
    ("claude-sonnet", 1024),
)


def floor_tokens_for_model(model: str | None) -> int | None:
    """Anthropic minimum cacheable prefix (tokens) for a model id.

    Substring match, most-specific-first. Returns None when ``model`` is None
    or unrecognized (caller falls back to the legacy char default).
    """
    if not model:
        return None
    needle = model.lower()
    for prefix, floor in MODEL_CACHE_FLOOR_TOKENS:
        if prefix in needle:
            return floor
    return None


def min_cacheable_chars(model: str | None = None) -> int:
    """Minimum cacheable block size in CHARACTERS for ``model``.

    Model-aware when ``model`` is a recognized Anthropic id (token floor x
    ~4 chars/token); the legacy conservative default otherwise. Heuristic —
    for exactness pre-check with ``messages.count_tokens``.
    """
    floor_tokens = floor_tokens_for_model(model)
    if floor_tokens is None:
        return _DEFAULT_MIN_CACHEABLE_CHARS
    return floor_tokens * _CHARS_PER_TOKEN


# Anthropic allows at most 4 cache_control breakpoints per request.
_MAX_CACHE_MARKERS = 4


class CacheStrategy(str, Enum):
    """Workload class gating whether the volatile per-query/documents tier is
    worth a cache marker (P2 — workload-aware caching).

    Stable tiers (system, pinned corpus) are always cached when above the model
    floor; only the most volatile cacheable tier is gated:

      - ``ONE_SHOT``   distinct one-shot RAG — do NOT mark the documents tier
                       (every request differs, so a marker only pays the write
                       surcharge for zero reads). Default — conservative.
      - ``MULTI_TURN`` same documents reused across turns — mark the docs tier.
      - ``HOT``        repeated/hot identical query — mark everything cacheable.
    """

    ONE_SHOT = "one_shot"
    MULTI_TURN = "multi_turn"
    HOT = "hot"


def caches_query_tier(strategy: "CacheStrategy | str") -> bool:
    """Whether ``strategy`` caches the volatile per-query/documents tier."""
    return strategy in (CacheStrategy.MULTI_TURN, CacheStrategy.HOT, "multi_turn", "hot")


def _cache_control(ttl: str) -> dict[str, str]:
    """Build a cache_control marker dict.

    5m is the implicit default in Anthropic's API; specifying it explicitly
    makes the request shape self-documenting.
    """
    if ttl == CACHE_TTL_1H:
        return {"type": "ephemeral", "ttl": "1h"}
    return {"type": "ephemeral"}


def _is_cacheable(text: str, model: str | None = None) -> bool:
    """Heuristic: is the block long enough to cache under ``model``'s floor?

    A block below its model's minimum cacheable size is silently NOT cached by
    Anthropic (no error, cache_creation stays 0), so we strip the marker rather
    than emit one that never takes effect. ``model=None`` uses the legacy
    conservative default.
    """
    return len(text) >= min_cacheable_chars(model)


def build_system_blocks(
    system_prompt: str,
    *,
    cache: bool = True,
    ttl: str = CACHE_TTL_5M,
    model: str | None = None,
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
    model:
        Target model id. When given, the cache marker is stripped if the block
        is below that model's token floor (see ``MODEL_CACHE_FLOOR_TOKENS``).
        ``None`` uses the legacy conservative default.

    Returns
    -------
    List of content blocks ready to assign to `system=...` on the Messages API.
    Empty list when system_prompt is empty (Anthropic accepts omitted system).
    """
    text = (system_prompt or "").strip()
    if not text:
        return []

    block: dict[str, Any] = {"type": "text", "text": text}
    if cache and _is_cacheable(text, model):
        block["cache_control"] = _cache_control(ttl)
    elif cache:
        Logger.debug(
            "System block (%d chars) below cacheable threshold %d (model=%s); skipping cache_control",
            len(text),
            min_cacheable_chars(model),
            model or "default",
        )
    return [block]


def _valid_hints(hints: "Sequence[int] | None", prompt_len: int) -> list[int]:
    """Sorted, de-duplicated boundary offsets strictly inside ``(0, prompt_len)``."""
    if not hints:
        return []
    return sorted({h for h in hints if 0 < h < prompt_len})


def _build_tier_blocks(
    prompt: str,
    hints: list[int],
    *,
    cache_prefix: bool,
    cache_query_tier: bool,
    ttl: str,
    model: str | None,
) -> list[dict[str, Any]]:
    """Split ``prompt`` into one block per stability tier + a volatile tail.

    ``hints`` are sorted, distinct, strictly-interior offsets. Produces up to
    ``len(hints) + 1`` segments: the first ``len(hints)`` are cacheable tiers,
    the last is the never-marked volatile tail. The LAST cacheable tier is the
    per-query/documents tier — its marker is suppressed when
    ``cache_query_tier`` is False (the workload-aware gate, P2). A tier below
    its model floor is left unmarked.
    """
    boundaries = [0, *hints, len(prompt)]
    n_tiers = len(hints)
    blocks: list[dict[str, Any]] = []
    for i in range(len(boundaries) - 1):
        seg = prompt[boundaries[i] : boundaries[i + 1]]
        if not seg:
            continue
        block: dict[str, Any] = {"type": "text", "text": seg}
        is_tier = i < n_tiers
        if cache_prefix and is_tier and seg.strip():
            should_mark = _is_cacheable(seg, model)
            if i == n_tiers - 1 and not cache_query_tier:
                should_mark = False  # workload-aware: leave the volatile tier unmarked
            if should_mark:
                block["cache_control"] = _cache_control(ttl)
        blocks.append(block)
    return blocks


def build_user_content(
    prompt: str,
    *,
    cache_boundary_hint: int = -1,
    cache_boundary_hints: "Sequence[int] | None" = None,
    cache_prefix: bool = True,
    cache_query_tier: bool = True,
    ttl: str = CACHE_TTL_5M,
    model: str | None = None,
) -> list[dict[str, Any]]:
    """Split a user-turn prompt into cache-aware content blocks.

    Two modes:
      - **Single boundary** (default / back-compat): split once at
        ``cache_boundary_hint`` into prefix (cached when above the model floor)
        + suffix (uncached).
      - **Multi-breakpoint** (P1): when ``cache_boundary_hints`` carries >=2
        valid offsets, split into one block per STABILITY TIER plus a volatile
        tail. Each tier block gets its own ``cache_control`` marker (subject to
        the model floor); the tail (``prompt[hints[-1]:]``) is never marked.
        ``cache_query_tier=False`` additionally suppresses the marker on the
        LAST (most volatile) cacheable tier — the workload-aware gate (P2).

    Parameters
    ----------
    prompt:
        The full user-turn text. Typically ``render_anthropic_prompt(...).text``.
    cache_boundary_hint:
        Single split offset. `-1` / `0` / `>= len(prompt)` disable splitting.
    cache_boundary_hints:
        Ordered cumulative tier offsets (e.g. ``RenderedPrompt.cache_boundary_hints``).
        Activates multi-breakpoint mode when >=2 are valid; a lone valid hint
        falls back to the single-boundary path.
    cache_prefix:
        When False, split but emit no markers.
    cache_query_tier:
        Multi-breakpoint only — when False, the last cacheable tier is left
        unmarked (one-shot RAG).
    ttl:
        Either CACHE_TTL_5M or CACHE_TTL_1H.
    model:
        Target model id for per-model floor resolution (see ``MODEL_CACHE_FLOOR_TOKENS``).

    Returns
    -------
    List of content blocks. Single-boundary mode returns 1 or 2 blocks;
    multi-breakpoint mode returns up to ``len(valid_hints) + 1`` blocks.
    """
    if not prompt:
        return []

    valid = _valid_hints(cache_boundary_hints, len(prompt))
    if len(valid) >= 2:
        return _build_tier_blocks(
            prompt,
            valid,
            cache_prefix=cache_prefix,
            cache_query_tier=cache_query_tier,
            ttl=ttl,
            model=model,
        )

    # Single-boundary fallback (back-compat): prefer a lone valid hint, else the scalar.
    boundary = valid[0] if valid else cache_boundary_hint

    # Invalid or no-op boundary: single uncached block
    if boundary <= 0 or boundary >= len(prompt):
        return [{"type": "text", "text": prompt}]

    prefix = prompt[:boundary]
    suffix = prompt[boundary:]

    # Never produce empty suffix blocks (Anthropic rejects them)
    if not suffix.strip():
        return [{"type": "text", "text": prompt}]

    prefix_block: dict[str, Any] = {"type": "text", "text": prefix}
    if cache_prefix and _is_cacheable(prefix, model):
        prefix_block["cache_control"] = _cache_control(ttl)
    elif cache_prefix:
        Logger.debug(
            "Prefix block (%d chars) below cacheable threshold %d (model=%s); skipping cache_control",
            len(prefix),
            min_cacheable_chars(model),
            model or "default",
        )

    return [prefix_block, {"type": "text", "text": suffix}]


def _enforce_marker_cap(payload: dict[str, Any], *, max_markers: int = _MAX_CACHE_MARKERS) -> None:
    """Keep at most ``max_markers`` ``cache_control`` markers in the request.

    Anthropic allows 4 breakpoints/request. When more are present, drop the
    lowest-value (smallest by char count) markers first — they save the least.
    Mutates ``payload`` in place.
    """
    marked: list[dict[str, Any]] = []
    for block in payload.get("system", []) or []:
        if isinstance(block, dict) and "cache_control" in block:
            marked.append(block)
    for msg in payload.get("messages", []) or []:
        for block in msg.get("content", []) or []:
            if isinstance(block, dict) and "cache_control" in block:
                marked.append(block)
    while len(marked) > max_markers:
        victim = min(marked, key=lambda b: len(b.get("text", "")))
        del victim["cache_control"]
        marked.remove(victim)


def build_messages_payload(
    user_prompt: str,
    *,
    system_prompt: str = "",
    cache_boundary_hint: int = -1,
    cache_boundary_hints: "Sequence[int] | None" = None,
    ttl: str = CACHE_TTL_5M,
    cache_system: bool = True,
    cache_prefix: bool = True,
    cache_strategy: "CacheStrategy | str" = CacheStrategy.ONE_SHOT,
    model: str | None = None,
) -> dict[str, Any]:
    """Convenience composer: build the `system` + `messages` fields.

    Returns a dict suitable for spreading into `client.messages.create(...)`:

        payload = build_messages_payload(user_prompt=p, system_prompt=s, cache_boundary_hint=b)
        response = client.messages.create(model=m, max_tokens=k, **payload)

    The returned dict never contains a `model` or `max_tokens` key — the
    caller owns those; this helper only handles cache-aware content shaping.
    The ``model`` arg is used ONLY to resolve the per-model cache floor (so
    below-floor blocks are not marked); it is NOT written into the payload.

    Multi-breakpoint (P1): pass ``cache_boundary_hints`` (from
    ``RenderedPrompt.cache_boundary_hints``) to mark each stability tier as its
    own cached block. ``cache_strategy`` (P2) gates the volatile per-query tier
    — default ``ONE_SHOT`` leaves it unmarked to avoid write-waste. At most 4
    ``cache_control`` markers are emitted (Anthropic's cap); the lowest-value
    (smallest) marked block is dropped if exceeded.
    """
    system_blocks = build_system_blocks(system_prompt, cache=cache_system, ttl=ttl, model=model)
    user_content = build_user_content(
        user_prompt,
        cache_boundary_hint=cache_boundary_hint,
        cache_boundary_hints=cache_boundary_hints,
        cache_prefix=cache_prefix,
        cache_query_tier=caches_query_tier(cache_strategy),
        ttl=ttl,
        model=model,
    )

    payload: dict[str, Any] = {
        "messages": [{"role": "user", "content": user_content}],
    }
    if system_blocks:
        payload["system"] = system_blocks

    _enforce_marker_cap(payload)
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
    "CacheStrategy",
    "MODEL_CACHE_FLOOR_TOKENS",
    "build_messages_payload",
    "build_system_blocks",
    "build_user_content",
    "caches_query_tier",
    "count_cache_markers",
    "floor_tokens_for_model",
    "min_cacheable_chars",
]
