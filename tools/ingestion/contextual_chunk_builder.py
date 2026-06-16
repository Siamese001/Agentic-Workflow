#!/usr/bin/env python3
"""Contextual Chunk Builder — Anthropic Contextual Retrieval preprocessor.

Generates a short (50-100 token) narrative context for each chunk, grounded in
the whole document, to be prepended before embedding + BM25 indexing. Per
Anthropic's research (https://www.anthropic.com/research/contextual-retrieval),
this reduces failed retrievals by 49% on top of hybrid BM25+dense, or 67% when
combined with reranking.

Gateway-mediated: all Anthropic calls route through SovereignLLMGateway per the
apps_rg contract. No direct Anthropic SDK access from this module.

Offline-safe: when the gateway is unavailable (missing ANTHROPIC_API_KEY, import
error, or explicit `--no-claude` flag), falls back to a deterministic
metadata-driven heuristic. Ingestion never hard-fails on missing API access.

Prompt shape follows the Anthropic cookbook:
    <document>{FULL_DOC}</document>                 <- cacheable (prompt caching at caller)
    <chunk>{CHUNK_TEXT}</chunk>
    Give a short succinct context to situate this chunk within the overall
    document for the purposes of improving search retrieval. Answer only with
    the succinct context and nothing else.

NOTE: `cache_control=ephemeral` marker on the <document> prefix is a Wave 2
(P2.1) concern — plumbing lives in HardenedanthropicexecutorStrategy. This
module emits the prompt; the gateway adapter applies the cache marker.
"""

from __future__ import annotations

from agentic_core.config.model_catalog import (
    ANTHROPIC_HAIKU_MODEL_ID,
)

import logging
import os
import re
from dataclasses import dataclass
from typing import Protocol

Logger = logging.getLogger(__name__)

# Target context length per Anthropic research: 50-100 tokens. We bound by
# character count as a proxy; tokenization happens at the gateway.
_CONTEXT_MIN_CHARS = 60
_CONTEXT_MAX_CHARS = 400
_PROMPT_TEMPLATE = (
    "<document>\n{document}\n</document>\n"
    "Here is the chunk we want to situate within the whole document:\n"
    "<chunk>\n{chunk}\n</chunk>\n"
    "Please give a short succinct context to situate this chunk within the "
    "overall document for the purposes of improving search retrieval of the "
    "chunk. Answer only with the succinct context and nothing else."
)

# Default model: Haiku tier is sufficient per Anthropic guidance — start cheap,
# earn upgrade via evals.
DEFAULT_MODEL = ANTHROPIC_HAIKU_MODEL_ID
DEFAULT_MAX_TOKENS = 150
DEFAULT_TEMPERATURE = 0.0
DEFAULT_TIMEOUT_S = 30


@dataclass(frozen=True)
class ContextualizationRequest:
    """Single chunk contextualization request."""

    document: str
    chunk: str
    metadata: dict | None = None


@dataclass(frozen=True)
class ContextualizationResult:
    """Result of contextualizing a chunk."""

    context: str
    source: str  # "gateway" | "heuristic" | "empty"
    model: str | None = None


class _GatewayProtocol(Protocol):
    """Structural type for a gateway capable of generating text."""

    def generate(
        self, prompt: str, *, model: str, max_tokens: int, temperature: float, timeout_s: int
    ) -> str: ...


class ContextualChunkBuilder:
    """Generates narrative context for chunks, with offline fallback.

    Thread-safety: gateway calls are blocking; caller coordinates concurrency.
    Determinism: temperature=0.0; same (document, chunk) pair yields the same
    context modulo gateway/model variance.
    """

    def __init__(
        self,
        *,
        gateway: _GatewayProtocol | None = None,
        model: str = DEFAULT_MODEL,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        enabled: bool | None = None,
    ) -> None:
        self._gateway = gateway
        self._model = model
        self._max_tokens = max_tokens
        # Explicit enabled flag overrides env/gateway detection for tests
        if enabled is None:
            self._enabled = bool(os.environ.get("ANTHROPIC_API_KEY")) and self._gateway_available()
        else:
            self._enabled = enabled

    def _gateway_available(self) -> bool:
        """Detect gateway availability.

        A gateway adapter must be explicitly injected via the `gateway`
        constructor argument. The canonical SovereignLLMGateway requires a
        CompiledPromptArtifact + secret_key, which is heavier than this
        preprocessor should carry — the W2.P2.1 phase wires a thin adapter
        that applies `cache_control=ephemeral` to the <document> prefix.
        """
        return self._gateway is not None

    def build(self, request: ContextualizationRequest) -> ContextualizationResult:
        """Generate a context string for one chunk.

        Returns heuristic result on gateway failure or disabled state. Never
        raises — ingestion must tolerate contextualization failures per
        Anthropic's guidance (context is an enhancement, not a hard dependency).
        """
        if not request.document.strip() or not request.chunk.strip():
            return ContextualizationResult(context="", source="empty")

        if self._enabled:
            try:
                context = self._call_gateway(request)
                if context:
                    return ContextualizationResult(context=context, source="gateway", model=self._model)
            except (ImportError, RuntimeError, ValueError, OSError) as exc:
                Logger.warning("Gateway contextualization failed; falling back to heuristic: %s", exc)

        heuristic = self._heuristic_context(request)
        return ContextualizationResult(context=heuristic, source="heuristic")

    def _call_gateway(self, request: ContextualizationRequest) -> str:
        """Route through an injected gateway adapter. Never called when disabled.

        The gateway adapter contract is intentionally narrow — a single
        `generate(prompt, *, model, max_tokens, temperature, timeout_s)`
        method returning a string. Callers wire a concrete adapter in
        W2.P2.1 (HardenedanthropicexecutorStrategy) that applies
        `cache_control=ephemeral` to the <document> prefix for cost reduction.
        """
        if self._gateway is None:
            # Guard: `_enabled` True without a gateway is a programming error
            raise RuntimeError("ContextualChunkBuilder enabled but no gateway adapter injected")

        prompt = _PROMPT_TEMPLATE.format(document=request.document, chunk=request.chunk)
        raw = self._gateway.generate(
            prompt,
            model=self._model,
            max_tokens=self._max_tokens,
            temperature=DEFAULT_TEMPERATURE,
            timeout_s=DEFAULT_TIMEOUT_S,
        )
        return self._trim(raw)

    @staticmethod
    def _trim(text: str) -> str:
        """Collapse whitespace and bound length (inclusive of ellipsis suffix)."""
        cleaned = re.sub(r"\s+", " ", text).strip()
        if len(cleaned) > _CONTEXT_MAX_CHARS:
            # Reserve 3 chars for the trailing ellipsis so the returned string
            # never exceeds _CONTEXT_MAX_CHARS.
            budget = _CONTEXT_MAX_CHARS - 3
            cleaned = cleaned[:budget].rsplit(" ", 1)[0] + "..."
        return cleaned

    @staticmethod
    def _heuristic_context(request: ContextualizationRequest) -> str:
        """Deterministic metadata-driven context for offline / fallback use.

        Uses whatever structural signals the chunk metadata carries. This is
        weaker than Claude-generated context but strictly better than no
        context at all, and preserves ingestion throughput when API is
        unavailable.
        """
        md = request.metadata or {}
        parts: list[str] = []

        title = md.get("title") or md.get("doc_type")
        if title:
            parts.append(f"From {title}.")

        heading = md.get("heading_path") or md.get("section")
        if heading:
            parts.append(f"Section: {heading}.")

        module = md.get("module")
        entity = md.get("name")
        entity_type = md.get("entity_type")
        if module and entity:
            kind = entity_type or "entity"
            parts.append(f"{kind.capitalize()} {entity} in module {module}.")
        elif module:
            parts.append(f"From module {module}.")

        file_path = md.get("file_path")
        if file_path and not module:
            parts.append(f"File: {file_path}.")

        doc_family = md.get("doc_family")
        topic = md.get("topic_bucket")
        if doc_family and topic:
            parts.append(f"{doc_family} on topic {topic}.")

        if not parts:
            # Absolute fallback: first sentence of chunk itself
            first_sentence = re.split(r"(?<=[.!?])\s+", request.chunk.strip(), maxsplit=1)[0]
            if first_sentence and len(first_sentence) <= _CONTEXT_MAX_CHARS:
                return first_sentence

        result = " ".join(parts)
        if len(result) < _CONTEXT_MIN_CHARS:
            # Pad with chunk preamble if heuristic is too thin
            preamble = request.chunk.strip()[: _CONTEXT_MAX_CHARS - len(result) - 1]
            preamble = preamble.split("\n", 1)[0]
            if preamble:
                result = (result + " " + preamble).strip()

        if len(result) > _CONTEXT_MAX_CHARS:
            budget = _CONTEXT_MAX_CHARS - 3
            result = result[:budget].rsplit(" ", 1)[0] + "..."

        return result


def prepend_context(chunk_text: str, context: str) -> str:
    """Prepend a context string to a chunk for embedding/BM25 indexing.

    Follows Anthropic's format: context as a prefix before the chunk content,
    separated by a blank line to preserve chunk semantics in retrieval.
    """
    if not context:
        return chunk_text
    return f"{context.strip()}\n\n{chunk_text}"


__all__ = [
    "ContextualChunkBuilder",
    "ContextualizationRequest",
    "ContextualizationResult",
    "prepend_context",
    "DEFAULT_MODEL",
]
