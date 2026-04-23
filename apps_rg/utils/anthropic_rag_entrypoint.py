"""Production-adoption seam for Anthropic RAG (W6.1, plan anthropic-rag-gaps-7f3c2a).

Composes the existing W1/W2 Anthropic RAG modules into a single caller-ready
function. Production callers in ``apps_rg`` (and the single Anthropic entry
point ``HardenedanthropicexecutorStrategy``) adopt the Anthropic-recommended
long-context + prompt-caching surface by calling
``build_anthropic_rag_payload``. No existing call sites are modified by this
module — it is opt-in.

Composition
-----------
1. ``render_anthropic_prompt(envelope, query)``  →  ``RenderedPrompt``
   (system + ``<document>`` blocks + ``<task>`` + ``<query>`` + grounding
   instruction, single string, with byte offset of the static-prefix boundary)
2. ``build_messages_payload(user_prompt=rendered.text, cache_boundary_hint=...)``
   →  dict suitable for ``client.messages.create(...)``

The rendered prompt intentionally inlines ``system_blocks`` at the head of
the user turn (per the renderer's contract). The cache boundary therefore
covers system + all documents, which is the entire static prefix — the
Anthropic-recommended cacheable surface.

When ``envelope.abstain_recommended`` is True, this function raises
``AbstainRecommendedError`` rather than returning a payload, because callers
MUST NOT send an abstain stub to the model.

Non-goals
---------
- Does NOT call the gateway. Callers own transport.
- Does NOT add ``citations`` yet — that is a separate adoption slice that
  composes with ``anthropic_citation_adapter`` at the response-parsing side.
- Does NOT override ``model`` or ``max_tokens`` — caller owns those.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agentic_core.knowledge.retrieval.anthropic_cache_control import (
    CACHE_TTL_5M,
    build_messages_payload,
    count_cache_markers,
)
from agentic_core.knowledge.retrieval.anthropic_prompt_renderer import (
    render_anthropic_prompt,
)
from agentic_core.knowledge.retrieval.prompt_envelope import PromptEnvelope


class AbstainRecommendedError(RuntimeError):
    """Raised when the envelope's evidence is too weak to generate a response.

    Callers MUST route to the HITL / refine path instead of calling Anthropic.
    """


@dataclass(frozen=True)
class AnthropicRagPayload:
    """Result of composing the RAG payload for an Anthropic Messages API call.

    Attributes:
        payload: The dict to spread into ``client.messages.create(...)``.
            Shape: ``{"messages": [...], "system": [...]}`` (system omitted
            when empty).
        document_block_count: Number of ``<document>`` blocks in the user turn
            (0 when the envelope had no verified chunks).
        cache_marker_count: Number of ``cache_control=ephemeral`` markers in
            the payload. 0 when ``use_cache`` is False or the static prefix
            was below the cacheable-size threshold.
        cache_boundary_hint: Byte offset of the static prefix boundary within
            the user turn text. ``-1`` when no cacheable prefix exists.
    """

    payload: dict[str, Any]
    document_block_count: int
    cache_marker_count: int
    cache_boundary_hint: int


def build_anthropic_rag_payload(
    envelope: PromptEnvelope,
    query: str,
    *,
    use_cache: bool = True,
    cache_ttl: str = CACHE_TTL_5M,
    include_grounding_instruction: bool = True,
) -> AnthropicRagPayload:
    """Build a caller-ready Anthropic Messages API payload from a PromptEnvelope.

    This is the single adoption seam for the Anthropic RAG surface. Callers
    opt in by replacing their current flat-string prompt assembly with this
    call.

    Args:
        envelope: Completed ``PromptEnvelope`` from ``PromptEnvelopeFactory``.
        query: End-user query string. Rendered last inside the user turn.
        use_cache: When True (default), apply ``cache_control=ephemeral``
            markers on the static prefix (system + documents). When False,
            the payload has no cache markers and each call is billed at full
            input-token rate.
        cache_ttl: ``"5m"`` (default) or ``"1h"``. Ignored when
            ``use_cache`` is False.
        include_grounding_instruction: When True (default), the renderer
            appends the quote-before-synthesize instruction.

    Returns:
        An ``AnthropicRagPayload`` carrying the dict for the Messages API
        plus provenance counters useful for eval / telemetry.

    Raises:
        AbstainRecommendedError: When ``envelope.abstain_recommended`` is
            True. Callers MUST route to the HITL / refine path.
    """
    if envelope.abstain_recommended:
        raise AbstainRecommendedError(
            f"PromptEnvelope {envelope.envelope_id} recommends abstain "
            f"(contradiction_status={envelope.contradiction_status!r}); "
            "MUST route to HITL / refine, not Anthropic."
        )

    rendered = render_anthropic_prompt(
        envelope,
        query,
        include_grounding_instruction=include_grounding_instruction,
    )

    boundary = rendered.cache_boundary_hint if use_cache else -1

    payload = build_messages_payload(
        user_prompt=rendered.text,
        system_prompt="",  # system_blocks are inlined at the head of rendered.text
        cache_boundary_hint=boundary,
        ttl=cache_ttl,
        cache_system=use_cache,
        cache_prefix=use_cache,
    )

    return AnthropicRagPayload(
        payload=payload,
        document_block_count=rendered.document_block_count,
        cache_marker_count=count_cache_markers(payload),
        cache_boundary_hint=rendered.cache_boundary_hint,
    )


__all__ = [
    "AbstainRecommendedError",
    "AnthropicRagPayload",
    "build_anthropic_rag_payload",
]
