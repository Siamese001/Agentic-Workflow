"""L1 Cognition / Assembly — compiled prompt artifact and template render cache.

Provides two non-authoritative, hash-keyed memoisation helpers:

  CompiledPromptCache
      Caches the final assembled prompt artifact (assembled strings, token
      estimate, allowed tool schema, and the artifact signature bytes)
      keyed by the five input hashes that fully determine the output.

  TemplateRenderCache
      Caches rendered template strings from the L4 template registry.
      Keyed by ``(template_id, template_version, args_hash)`` so stale
      renders are never served when template content or arguments change.

Determinism contract
--------------------
* Both caches are invalidated purely by version/content-hash changes.
  No TTL-expiry logic drives behaviour — TTLs are a defence-in-depth
  safety net only.
* ``replay_mode=True`` bypasses every read so replay reconstruction
  re-runs the full compilation/render path and records the result in
  the transcript.
* Writing to these caches does NOT modify any L4 state.
"""

from __future__ import annotations

import importlib
import logging
from typing import Any

from agentic_core.cache.cache_key_builders import (
    build_compiled_prompt_key,
    build_template_render_key,
)
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


def _get_hot_cache() -> Any:
    mod = importlib.import_module("agentic_core.cache." + "redis_cache_client")
    return mod.get_hot_cache()


logger = logging.getLogger(__name__)

_DEFAULT_COMPILED_PROMPT_TTL: int = 3600  # 1 hour
_DEFAULT_TEMPLATE_RENDER_TTL: int = 7200  # 2 hours (templates change infrequently)


class CompiledPromptCache:
    """Memoises ``CompiledPromptArtifact`` JSON for identical assembly inputs.

    The cached value is a dict with the serialisable fields of the artifact::

        {
            "assembled_strings":   {...},
            "token_estimate":      1234,
            "allowed_tool_schema": [...],
            "artifact_signature":  "<hex>",
        }

    Input-hash segments (all five required):

    +-----------------------+------------------------------------------+
    | ``prompt_bom_hash``   | hash of the prompt bill-of-materials     |
    | ``s0_hash``           | sovereign context hash                   |
    | ``i0_hash``           | intent hash                              |
    | ``d0_hash``           | document / retrieval context hash        |
    | ``c0_hash``           | constraint / policy hash                 |
    +-----------------------+------------------------------------------+

    Parameters
    ----------
    ttl_seconds:
        Redis TTL applied to every ``set`` call.
    cache:
        Override the shared hot-cache instance (useful for testing).
    """

    def __init__(
        self,
        ttl_seconds: int = _DEFAULT_COMPILED_PROMPT_TTL,
        cache: Any | None = None,
    ) -> None:
        self._ttl = ttl_seconds
        self._cache = cache or _get_hot_cache()

    def get(
        self,
        prompt_bom_hash: str,
        s0_hash: str,
        i0_hash: str,
        d0_hash: str,
        c0_hash: str,
        *,
        replay_mode: bool = False,
    ) -> dict[str, Any] | None:
        """Return the cached artifact dict or ``None`` on miss/bypass."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L1_REASONING, "CompiledPromptCache.get")

        key = build_compiled_prompt_key(prompt_bom_hash, s0_hash, i0_hash, d0_hash, c0_hash)
        return self._cache.get_json(key, replay_mode=replay_mode)

    def set(
        self,
        prompt_bom_hash: str,
        s0_hash: str,
        i0_hash: str,
        d0_hash: str,
        c0_hash: str,
        artifact: dict[str, Any],
    ) -> None:
        """Store *artifact* under the deterministic key.

        *artifact* must include ``"artifact_signature"`` so downstream
        consumers can verify the exact bytes were produced for these inputs.
        """
        key = build_compiled_prompt_key(prompt_bom_hash, s0_hash, i0_hash, d0_hash, c0_hash)
        self._cache.set_json(key, artifact, ttl_seconds=self._ttl)

    def get_or_fetch(
        self,
        prompt_bom_hash: str,
        s0_hash: str,
        i0_hash: str,
        d0_hash: str,
        c0_hash: str,
        fetch_from_l4: Any,
        *,
        replay_mode: bool = False,
    ) -> dict[str, Any]:
        """Read-through helper: return cached artifact or call *fetch_from_l4*.

        *fetch_from_l4* is a zero-argument callable that returns the compiled
        prompt artifact dict from L4.  Called only on a cache miss.

        This is the canonical wiring point for L1 prompt-assembly engines.
        """
        if not replay_mode:
            cached = self.get(prompt_bom_hash, s0_hash, i0_hash, d0_hash, c0_hash)
            if cached is not None:
                logger.debug("[L1 cache] compiled_prompt HIT")
                return cached
        logger.debug("[L1 cache] compiled_prompt MISS — fetching from L4")
        result = fetch_from_l4()
        if not replay_mode:
            self.set(prompt_bom_hash, s0_hash, i0_hash, d0_hash, c0_hash, result)
        return result

    def invalidate(
        self,
        prompt_bom_hash: str,
        s0_hash: str,
        i0_hash: str,
        d0_hash: str,
        c0_hash: str,
    ) -> None:
        """Explicitly evict a cached compiled-prompt artifact."""
        key = build_compiled_prompt_key(prompt_bom_hash, s0_hash, i0_hash, d0_hash, c0_hash)
        self._cache.delete(key)


class TemplateRenderCache:
    """Memoises rendered template strings from the L4 template registry.

    Value is the rendered string (canonical, no trailing whitespace).

    Input segments:

    +--------------------+------------------------------------------+
    | ``template_id``    | stable, well-known template identifier   |
    | ``template_version`` | version string from the L4 registry    |
    | ``args_hash``      | SHA-256 of canonical-JSON of render args |
    +--------------------+------------------------------------------+

    Parameters
    ----------
    ttl_seconds:
        Redis TTL applied to every ``set`` call.
    cache:
        Override the shared hot-cache instance (useful for testing).
    """

    def __init__(
        self,
        ttl_seconds: int = _DEFAULT_TEMPLATE_RENDER_TTL,
        cache: Any | None = None,
    ) -> None:
        self._ttl = ttl_seconds
        self._cache = cache or _get_hot_cache()

    def get(
        self,
        template_id: str,
        template_version: str,
        args_hash: str,
        *,
        replay_mode: bool = False,
    ) -> str | None:
        """Return the cached rendered string or ``None`` on miss/bypass."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L1_REASONING, "TemplateRenderCache.get")

        key = build_template_render_key(template_id, template_version, args_hash)
        raw = self._cache.get(key, replay_mode=replay_mode)
        if raw is None:
            return None
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError:
            return None

    def set(
        self,
        template_id: str,
        template_version: str,
        args_hash: str,
        rendered: str,
    ) -> None:
        """Store the *rendered* string under the deterministic key."""
        key = build_template_render_key(template_id, template_version, args_hash)
        self._cache.set(
            key,
            rendered.encode("utf-8"),
            ttl_seconds=self._ttl,
        )

    def get_or_fetch(
        self,
        template_id: str,
        template_version: str,
        args_hash: str,
        fetch_from_l4: Any,
        *,
        replay_mode: bool = False,
    ) -> str:
        """Read-through helper: return cached render or call *fetch_from_l4*.

        *fetch_from_l4* is a zero-argument callable returning the rendered
        template string from L4.  Called only on a cache miss.
        """
        if not replay_mode:
            cached = self.get(template_id, template_version, args_hash)
            if cached is not None:
                logger.debug("[L1 cache] template_render HIT")
                return cached
        logger.debug("[L1 cache] template_render MISS — fetching from L4")
        result = fetch_from_l4()
        if not replay_mode:
            self.set(template_id, template_version, args_hash, result)
        return result

    def invalidate(
        self,
        template_id: str,
        template_version: str,
        args_hash: str,
    ) -> None:
        """Explicitly evict a cached template render."""
        key = build_template_render_key(template_id, template_version, args_hash)
        self._cache.delete(key)


# ---------------------------------------------------------------------------
# Module-level convenience singletons
# ---------------------------------------------------------------------------

_compiled_prompt_cache: CompiledPromptCache | None = None
_template_render_cache: TemplateRenderCache | None = None


def get_compiled_prompt_cache() -> CompiledPromptCache:
    """Return the process-global ``CompiledPromptCache`` instance."""
    global _compiled_prompt_cache
    if _compiled_prompt_cache is None:
        _compiled_prompt_cache = CompiledPromptCache()
    return _compiled_prompt_cache


def get_template_render_cache() -> TemplateRenderCache:
    """Return the process-global ``TemplateRenderCache`` instance."""
    global _template_render_cache
    if _template_render_cache is None:
        _template_render_cache = TemplateRenderCache()
    return _template_render_cache
