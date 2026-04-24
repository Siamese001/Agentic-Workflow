"""Provider-aware token counter — EQ-7 (ADR-PROMPT-ASSEMBLY-002 §6).

Gives callers a single entry point (:func:`count_tokens`) that dispatches to
the best available tokenizer per provider and falls back to a deterministic
heuristic when the provider's SDK is not installed.

Design constraints
------------------
- **Never raises.** Tokenization failures return the heuristic estimate so
  callers (assembly, budget enforcement, token ledger) don't crash on a
  missing optional dependency.
- **Pure function.** No module-level state beyond a memoized encoder cache,
  which is rebuilt lazily per interpreter.
- **Deterministic floor.** The heuristic path is stable: the same input
  always produces the same token count so replay / idempotency guarantees
  upstream of this module are preserved.
- **No network calls.** Anthropic's hosted ``/v1/messages/count_tokens``
  endpoint is NOT used here — it would introduce a latency and failure
  mode inconsistent with the "never raises" contract. If a caller wants
  that precision they can invoke the Anthropic client directly.

Provider dispatch table
-----------------------

| Provider prefix | Preferred backend          | Fallback    |
|-----------------|-----------------------------|-------------|
| ``openai``      | ``tiktoken`` (model-aware)  | heuristic   |
| ``anthropic``   | heuristic-claude            | heuristic   |
| ``gemini``      | heuristic                   | heuristic   |
| unknown         | heuristic                   | heuristic   |

The two heuristics differ slightly:

- **heuristic** (default, OpenAI family): ``len(text) / 4`` rounded up.
  Widely cited for GPT-4 class tokenizers.
- **heuristic-claude**: ``len(text) / 3.5`` rounded up. Anthropic's
  tokenizer packs ~15% denser than GPT-4 on English text.
"""

from __future__ import annotations

import math
from functools import lru_cache
from typing import Any

# Public factor constants — exported so budget enforcers and tests can
# pin expectations without re-deriving the math.
HEURISTIC_CHARS_PER_TOKEN_OPENAI: float = 4.0
HEURISTIC_CHARS_PER_TOKEN_CLAUDE: float = 3.5
HEURISTIC_CHARS_PER_TOKEN_GEMINI: float = 4.0

# Sentinel returned on empty input so divisions downstream stay defined.
_EMPTY_TOKENS: int = 0


# ---------------------------------------------------------------------------
# Heuristic fallback.
# ---------------------------------------------------------------------------


def _heuristic_tokens(text: str, chars_per_token: float) -> int:
    """Deterministic char/chars_per_token estimator, rounded up."""
    if not text:
        return _EMPTY_TOKENS
    return max(1, math.ceil(len(text) / chars_per_token))


# ---------------------------------------------------------------------------
# OpenAI — tiktoken (model-aware), else heuristic.
# ---------------------------------------------------------------------------


@lru_cache(maxsize=32)
def _tiktoken_encoder(model: str | None) -> Any:
    """Return a cached tiktoken encoder for ``model``, or ``None`` if unavailable.

    Cached so the encoding lookup happens once per model per process. The
    cache size is bounded so a caller that rotates through many model IDs
    cannot exhaust memory.
    """
    try:
        import tiktoken  # type: ignore[import-not-found]
    except ImportError:  # guardian: allow-return-none-swallow -- tiktoken is optional; caller uses byte-length heuristic when None
        return None
    try:
        if model:
            return tiktoken.encoding_for_model(model)
    except (KeyError, ValueError):  # guardian: allow-silent-swallow -- unknown model name: intentional fall-through to the generic cl100k_base encoding below
        # Unknown model name — fall through to the generic encoding.
        pass
    try:
        return tiktoken.get_encoding("cl100k_base")
    except (KeyError, ValueError):  # guardian: allow-return-none-swallow -- tiktoken encoding lookup fail: None tells caller to fall back to byte-length counting
        return None


def _openai_tokens(text: str, model: str | None) -> int:
    encoder = _tiktoken_encoder(model)
    if encoder is None:
        return _heuristic_tokens(text, HEURISTIC_CHARS_PER_TOKEN_OPENAI)
    try:
        return len(encoder.encode(text))
    except (TypeError, ValueError):
        # tiktoken raises on non-string inputs or malformed sequences.
        # Surface the heuristic rather than crashing the caller.
        return _heuristic_tokens(text, HEURISTIC_CHARS_PER_TOKEN_OPENAI)


# ---------------------------------------------------------------------------
# Provider dispatch.
# ---------------------------------------------------------------------------


def _normalize_provider(provider: str) -> str:
    """Collapse provider names to their canonical prefix."""
    key = (provider or "").strip().lower()
    if not key:
        return "unknown"
    if key.startswith("openai") or key in {"azure_openai", "azure-openai"}:
        return "openai"
    if key.startswith("anthropic") or key.startswith("claude"):
        return "anthropic"
    if key.startswith("gemini") or key.startswith("vertex") or key.startswith("google"):
        return "gemini"
    return key


def count_tokens(
    text: str,
    provider: str,
    model: str | None = None,
) -> int:
    """Count tokens in ``text`` using the best available tokenizer for ``provider``.

    Args:
        text: The input string to tokenize. Empty string returns 0.
        provider: Provider identifier. Case-insensitive. Recognized prefixes:
            ``openai``, ``azure_openai``, ``anthropic``, ``claude``,
            ``gemini``, ``vertex``, ``google``. Unknown providers fall back
            to the OpenAI-family heuristic.
        model: Optional model identifier for providers with model-specific
            tokenizers (OpenAI via ``tiktoken``). Ignored by heuristic paths.

    Returns:
        Non-negative integer token count. Never raises.
    """
    if text is None:
        return _EMPTY_TOKENS
    canonical = _normalize_provider(provider)
    if canonical == "openai":
        return _openai_tokens(text, model)
    if canonical == "anthropic":
        return _heuristic_tokens(text, HEURISTIC_CHARS_PER_TOKEN_CLAUDE)
    if canonical == "gemini":
        return _heuristic_tokens(text, HEURISTIC_CHARS_PER_TOKEN_GEMINI)
    return _heuristic_tokens(text, HEURISTIC_CHARS_PER_TOKEN_OPENAI)


def count_tokens_for_messages(
    messages: list[dict[str, str]],
    provider: str,
    model: str | None = None,
) -> int:
    """Sum token counts across a messages array.

    Convenience wrapper for gateway callers that already have the OpenAI-
    style ``[{"role": ..., "content": ...}]`` shape. Only the ``content``
    field is counted — role names are provider-specific overhead that
    downstream billing typically absorbs elsewhere.
    """
    total = 0
    for message in messages:
        content = message.get("content") if isinstance(message, dict) else None
        if isinstance(content, str):
            total += count_tokens(content, provider, model)
    return total


__all__ = [
    "HEURISTIC_CHARS_PER_TOKEN_OPENAI",
    "HEURISTIC_CHARS_PER_TOKEN_CLAUDE",
    "HEURISTIC_CHARS_PER_TOKEN_GEMINI",
    "count_tokens",
    "count_tokens_for_messages",
]
