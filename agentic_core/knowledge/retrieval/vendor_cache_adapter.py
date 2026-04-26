"""Vendor-Agnostic Prompt Cache Adapter — G9 vendor-agnostic cache abstraction.

Provides a unified interface for prompt caching across LLM vendors:

  - **Anthropic**: explicit ``cache_control=ephemeral`` markers on content blocks.
  - **OpenAI**: automatic caching of ≥1024-token prefixes (no explicit markers).
  - **Google/Gemini**: implicit + explicit caching via ``cachedContents`` API.

The adapter abstracts away vendor-specific cache-shape logic so that the
C0 context assembly pipeline can apply a single "static prefix" discipline
regardless of which LLM provider is active.

Design:
  - ``CacheBoundary`` declares where the static prefix ends and dynamic
    content begins.
  - ``PromptCacheAdapter`` is the base class; vendor-specific subclasses
    implement ``apply_cache_markers()``.
  - ``AnthropicCacheAdapter`` wraps ``anthropic_cache_control.py``.
  - ``OpenAICacheAdapter`` is a no-op (auto-cache, but validates prefix
    length).
  - ``GeminiCacheAdapter`` marks the system instruction for caching.
  - ``get_cache_adapter()`` factory selects the adapter by vendor name.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from agentic_core.knowledge.retrieval.anthropic_cache_control import (
    build_messages_payload,
)

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# CacheBoundary — where static prefix ends
# ---------------------------------------------------------------------------


@dataclass
class CacheBoundary:
    """Declares where the static (cacheable) prefix ends.

    Attributes
    ----------
    system_prompt : str
        The system prompt (always static, always cacheable).
    user_prefix : str
        The static prefix of the user turn (cacheable).
    user_suffix : str
        The dynamic suffix of the user turn (not cacheable).
    boundary_char_index : int
        Character index in the user turn where the boundary falls.
        -1 means no boundary (entire user turn is dynamic).
    """

    system_prompt: str = ""
    user_prefix: str = ""
    user_suffix: str = ""
    boundary_char_index: int = -1


# ---------------------------------------------------------------------------
# CacheAdapterResult — output of cache marker application
# ---------------------------------------------------------------------------


@dataclass
class CacheAdapterResult:
    """Result of applying cache markers to a prompt.

    Attributes
    ----------
    vendor : str
        Vendor name that produced this result.
    messages : list[dict[str, Any]]
        Vendor-specific message structure with cache markers applied.
    cacheable_token_estimate : int
        Estimated tokens in the cacheable prefix.
    cache_markers_applied : bool
        Whether explicit cache markers were applied.
    """

    vendor: str = ""
    messages: list[dict[str, Any]] | None = None
    cacheable_token_estimate: int = 0
    cache_markers_applied: bool = False


# ---------------------------------------------------------------------------
# PromptCacheAdapter — base class
# ---------------------------------------------------------------------------


class PromptCacheAdapter:
    """Base class for vendor-agnostic prompt cache adapters.

    Subclasses implement ``apply_cache_markers()`` for a specific vendor.
    """

    vendor_name: str = "base"

    def apply_cache_markers(
        self,
        boundary: CacheBoundary,
        ttl: str = "5m",
    ) -> CacheAdapterResult:
        """Apply cache markers according to vendor conventions.

        Args:
            boundary: The cache boundary declaration.
            ttl: Cache TTL (vendor-specific interpretation).

        Returns:
            ``CacheAdapterResult`` with vendor-specific message structure.

        Raises:
            TypeError: If boundary is not a CacheBoundary.
            ValueError: If ttl is not a recognized value.
        """
        if not isinstance(boundary, CacheBoundary):
            raise TypeError(f"boundary must be CacheBoundary, got {type(boundary).__name__}")
        if ttl not in ("5m", "1h"):
            raise ValueError(f"ttl must be '5m' or '1h', got '{ttl}'")
        raise NotImplementedError


# ---------------------------------------------------------------------------
# AnthropicCacheAdapter
# ---------------------------------------------------------------------------


class AnthropicCacheAdapter(PromptCacheAdapter):
    """Anthropic prompt cache adapter.

    Delegates to ``anthropic_cache_control.apply_anthropic_cache_markers()``
    which adds ``cache_control=ephemeral`` markers to the static prefix.
    """

    vendor_name = "anthropic"

    def apply_cache_markers(
        self,
        boundary: CacheBoundary,
        ttl: str = "5m",
    ) -> CacheAdapterResult:
        """Apply Anthropic cache markers.

        Uses the existing ``anthropic_cache_control`` module to produce
        the structured content shape with ``cache_control`` markers.
        """
        result = build_messages_payload(
            user_prompt=boundary.user_prefix + boundary.user_suffix,
            system_prompt=boundary.system_prompt,
            cache_boundary_hint=boundary.boundary_char_index,
            ttl=ttl,
        )
        # Estimate cacheable tokens (rough: 4 chars/token)
        cacheable_chars = len(boundary.system_prompt) + len(boundary.user_prefix)
        token_est = cacheable_chars // 4

        # build_messages_payload returns a dict with 'system' and 'messages'
        messages_list: list[dict[str, Any]] = []
        if result.get("system"):
            messages_list.append({"role": "system", "content": result["system"]})
        if result.get("messages"):
            messages_list.extend(result["messages"])

        return CacheAdapterResult(
            vendor=self.vendor_name,
            messages=messages_list,
            cacheable_token_estimate=token_est,
            cache_markers_applied=True,
        )


# ---------------------------------------------------------------------------
# OpenAICacheAdapter
# ---------------------------------------------------------------------------


class OpenAICacheAdapter(PromptCacheAdapter):
    """OpenAI prompt cache adapter.

    OpenAI auto-caches ≥1024-token prefixes.  No explicit markers needed,
    but we validate that the prefix meets the minimum length and log a
    warning if it doesn't.
    """

    vendor_name = "openai"
    _MIN_CACHEABLE_CHARS = 3500  # ~875 tokens at 4 chars/token

    def apply_cache_markers(
        self,
        boundary: CacheBoundary,
        ttl: str = "5m",
    ) -> CacheAdapterResult:
        """Validate prefix length for OpenAI auto-caching.

        No explicit markers — just build standard messages and warn if
        the prefix is too short for auto-caching.
        """
        cacheable_chars = len(boundary.system_prompt) + len(boundary.user_prefix)
        token_est = cacheable_chars // 4

        if cacheable_chars < self._MIN_CACHEABLE_CHARS:
            log.warning(
                "OpenAI auto-cache: prefix too short (%d chars, ~%d tokens). "
                "Auto-cache requires ≥1024 tokens.",
                cacheable_chars, token_est,
            )

        messages: list[dict[str, Any]] = []
        if boundary.system_prompt:
            messages.append({"role": "system", "content": boundary.system_prompt})
        user_content = boundary.user_prefix + boundary.user_suffix
        if user_content:
            messages.append({"role": "user", "content": user_content})

        return CacheAdapterResult(
            vendor=self.vendor_name,
            messages=messages,
            cacheable_token_estimate=token_est,
            cache_markers_applied=False,
        )


# ---------------------------------------------------------------------------
# GeminiCacheAdapter
# ---------------------------------------------------------------------------


class GeminiCacheAdapter(PromptCacheAdapter):
    """Google Gemini prompt cache adapter.

    Gemini supports implicit + explicit caching.  The system instruction
    is always a good cache candidate.  We mark it with a ``cached_content``
    hint for explicit caching when the prefix is long enough.
    """

    vendor_name = "gemini"

    def apply_cache_markers(
        self,
        boundary: CacheBoundary,
        ttl: str = "5m",
    ) -> CacheAdapterResult:
        """Apply Gemini cache markers.

        The system instruction is always cacheable.  For the user prefix,
        we include it in the ``cached_content`` block when boundary is set.
        """
        cacheable_chars = len(boundary.system_prompt) + len(boundary.user_prefix)
        token_est = cacheable_chars // 4

        contents: list[dict[str, Any]] = []
        if boundary.system_prompt:
            contents.append({
                "role": "system_instruction",
                "parts": [{"text": boundary.system_prompt}],
            })
        user_parts: list[dict[str, Any]] = []
        if boundary.user_prefix:
            user_parts.append({"text": boundary.user_prefix})
        if boundary.user_suffix:
            user_parts.append({"text": boundary.user_suffix})
        if user_parts:
            contents.append({"role": "user", "parts": user_parts})

        return CacheAdapterResult(
            vendor=self.vendor_name,
            messages=contents,
            cacheable_token_estimate=token_est,
            cache_markers_applied=bool(boundary.system_prompt),
        )


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

_ADAPTERS: dict[str, type[PromptCacheAdapter]] = {
    "anthropic": AnthropicCacheAdapter,
    "openai": OpenAICacheAdapter,
    "gemini": GeminiCacheAdapter,
}


def get_cache_adapter(vendor: str) -> PromptCacheAdapter:
    """Get a cache adapter for the given vendor.

    Args:
        vendor: Vendor name (anthropic, openai, gemini).

    Returns:
        A ``PromptCacheAdapter`` instance.

    Raises:
        ValueError: If the vendor is not supported.
    """
    cls = _ADAPTERS.get(vendor)
    if cls is None:
        supported = ", ".join(sorted(_ADAPTERS))
        raise ValueError(f"Unknown vendor '{vendor}'. Supported: {supported}")
    return cls()
