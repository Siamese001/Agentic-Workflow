"""AnthropicContextGateway — minimal gateway adapter for ContextualChunkBuilder.

Implements the ``_GatewayProtocol`` declared in
``tools.ingestion.contextual_chunk_builder`` and routes through the
sovereignty-enforced ``SovereignLLMGateway`` via
``apps_rg.utils.providers_anthropic_client_util.run_llm_anthropic``.

Purpose
-------
Closes the G1-residual gap identified in
``.windsurf/plans/c0-context-assembly-best-practices-b7c3a1.md`` §2a:
``ContextualChunkBuilder`` was shipped by plan ``anthropic-rag-gaps-7f3c2a``
P1.1 but instantiated at production call sites with no gateway injected, so
``enabled`` always resolved to False and only the heuristic fallback ran.

V1 scope (this module)
----------------------
* Route each contextualization request through ``run_llm_anthropic``.
* Default model is the DEFAULT_MODEL exported by ``contextual_chunk_builder``
  (currently ``claude-haiku-4-5``), overridable by caller.
* Precise exception handling. On any transport failure, ``generate`` re-raises
  ``RuntimeError`` so ``ContextualChunkBuilder`` falls back to its heuristic
  path per its own contract (build() catches ImportError, RuntimeError,
  ValueError, OSError).

Out of scope (tracked as G11-residual in the plan)
--------------------------------------------------
* ``cache_control=ephemeral`` markers on the ``<document>`` prefix. The
  current ``GenerationRequest`` takes a flat ``prompt: str`` with no
  structured messages shape, so cache markers cannot be plumbed without a
  broader gateway change. V2 will either extend ``GenerationRequest`` with
  a ``cache_control_hint`` field or introduce a ``MessagesGenerationRequest``
  variant. Until then, per-chunk contextualization pays full input-token
  rate on the parent doc; cost is bounded by keeping Haiku as default.

Determinism
-----------
* Defaults ``temperature=0.0`` (overridable).
* Replay key emission is handled upstream by ``run_llm_anthropic`` via
  ``_clk.emit_replay_key`` and ``emit_determinism_digest``.

Failure mode
------------
* Missing ``ANTHROPIC_API_KEY`` env var: factory ``build_from_env`` returns
  ``None`` so callers can treat the absence as "no gateway" and the
  ``ContextualChunkBuilder`` falls back to heuristic.
* Import errors (SDK not installed in this environment): ``generate`` raises
  ``RuntimeError`` which the builder catches.
"""

from __future__ import annotations

import logging
import os

Logger = logging.getLogger(__name__)


class AnthropicContextGateway:
    """Minimal ``_GatewayProtocol`` adapter routing through SovereignLLMGateway.

    Thread-safety: ``run_llm_anthropic`` creates a new asyncio event loop per
    call; concurrent ``generate`` invocations across threads are safe because
    each spawns its own loop.
    """

    def __init__(self, *, default_model: str | None = None) -> None:
        self._default_model = default_model

    def generate(
        self,
        prompt: str,
        *,
        model: str,
        max_tokens: int,
        temperature: float,
        timeout_s: int,
    ) -> str:
        """Generate a completion for ``prompt`` via the sovereign gateway.

        Args:
            prompt: Flat prompt string. ``ContextualChunkBuilder`` inlines the
                ``<document>`` / ``<chunk>`` tags into this string.
            model: Anthropic model id. Caller passes the
                ``ContextualChunkBuilder._model`` (Haiku default) unless
                overridden at the builder level.
            max_tokens: Upper bound on the generated context. Builder
                default is 150; sufficient for 50-100 token context targets.
            temperature: Sampling temperature. Builder passes 0.0 for
                determinism; adapter forwards as-is.
            timeout_s: Per-call timeout. Forwarded to the gateway where
                supported.

        Returns:
            Generated text. Empty string on model refusal or empty response.

        Raises:
            RuntimeError: Any transport / import / gateway failure. Caller
                (``ContextualChunkBuilder.build``) catches this and falls
                back to the heuristic path.
        """
        effective_model = model or self._default_model
        if not effective_model:
            raise RuntimeError(
                "AnthropicContextGateway.generate called with no model and no default_model configured"
            )

        try:
            # Import inside method: providers_anthropic_client_util emits
            # lifecycle-trace calls at import time; importing lazily keeps
            # ingestion processes that never contextualize free of that cost.
            from apps_rg.utils.providers_anthropic_client_util import run_llm_anthropic
        except ImportError as exc:
            raise RuntimeError(f"AnthropicContextGateway could not import run_llm_anthropic: {exc}") from exc

        try:
            return run_llm_anthropic(
                effective_model,
                prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout_s=timeout_s,
            )
        except (RuntimeError, ValueError, OSError) as exc:
            Logger.warning(
                "AnthropicContextGateway.generate failed (model=%s): %s",
                effective_model,
                exc,
            )
            raise RuntimeError(f"Anthropic gateway generation failed: {exc}") from exc


def build_from_env() -> AnthropicContextGateway | None:
    """Construct a gateway iff ``ANTHROPIC_API_KEY`` is present, else ``None``.

    Canonical way for ingestion scripts to opt into gateway-backed
    contextualization:

        from tools.ingestion.anthropic_context_gateway import build_from_env
        from tools.ingestion.contextual_chunk_builder import ContextualChunkBuilder

        builder = ContextualChunkBuilder(gateway=build_from_env())

    When the env var is absent, ``build_from_env`` returns ``None``;
    ``ContextualChunkBuilder`` then decides its own ``enabled`` state based on
    whether a gateway was injected.
    """
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    return AnthropicContextGateway()


__all__ = ["AnthropicContextGateway", "build_from_env"]


# Note: _GatewayProtocol in contextual_chunk_builder is a structural Protocol
# (not @runtime_checkable), so isinstance() is not available. Static type
# compatibility is verified by mypy on the generate() signature. Unit tests in
# tests/unit/tools/ingestion/test_anthropic_context_gateway.py exercise the
# builder path with this adapter injected.
