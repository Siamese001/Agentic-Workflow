"""L5 Safety — policy-evaluation memoisation cache seam.

Provides ``SafetyEvalCache`` which stores the memoised result of a safety
evaluation for a given ``(compiled_prompt_hash, policy_hash, toolset_hash)``
triple.

Sovereignty contract
--------------------
* L5 remains the certifier.  Redis stores only the memoised *result* for
  identical inputs; it never overrides a live evaluation.
* Cache entries are invalidated purely by version-hash changes — when any
  of the three input hashes changes a fresh evaluation is performed.
* ``replay_mode=True`` bypasses the cache unconditionally so every replay
  re-runs the full evaluation and records the result in the transcript.
* Writing to this cache does NOT modify any L4 state.
"""

from __future__ import annotations

import logging
from typing import Any

from agentic_core.cache.cache_key_builders import build_safety_eval_key
from agentic_core.cache.redis_cache_client import (
    DeterministicRedisCache,
    get_hot_cache,
)
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace, _emit_signs_execution_trace

logger = logging.getLogger(__name__)

_DEFAULT_SAFETY_EVAL_TTL: int = 1800  # 30 minutes


class SafetyEvalCache:
    """Memoises L5 safety-evaluation results for identical compiled artifacts.

    The cached value is a dict with at least these fields::

        {
            "decision":          "allow" | "block",
            "compliance_hash":   "<64-char hex>",
            "remediation_hints": [...],
        }

    Callers must verify that all three hash inputs still match the current
    execution context before accepting a cached result.

    Parameters
    ----------
    ttl_seconds:
        Redis TTL applied to every ``set`` call.
    cache:
        Override the shared hot-cache instance (useful for testing).
    """

    def __init__(
        self,
        ttl_seconds: int = _DEFAULT_SAFETY_EVAL_TTL,
        cache: DeterministicRedisCache | None = None,
    ) -> None:
        self._ttl = ttl_seconds
        self._cache = cache or get_hot_cache()

    def get(
        self,
        compiled_prompt_hash: str,
        policy_hash: str,
        toolset_hash: str,
        *,
        replay_mode: bool = False,
    ) -> dict[str, Any] | None:
        """Return the cached evaluation dict or ``None`` on miss/bypass.

        Returns ``None`` (forcing a fresh L5 evaluation) when:
        - The key is not present.
        - Redis is unreachable and the fallback store has no entry.
        - ``replay_mode=True``.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "SafetyEvalCache.get")
        import hashlib as _hashlib  # noqa: PLC0415
        _seg_hash = _hashlib.sha256(f"{_trace_id}:SafetyEvalCache.get".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        key = build_safety_eval_key(compiled_prompt_hash, policy_hash, toolset_hash)
        return self._cache.get_json(key, replay_mode=replay_mode)

    def set(
        self,
        compiled_prompt_hash: str,
        policy_hash: str,
        toolset_hash: str,
        eval_result: dict[str, Any],
    ) -> None:
        """Store *eval_result* under the deterministic key.

        *eval_result* must contain at minimum ``"decision"`` (``"allow"``
        or ``"block"``) and ``"compliance_hash"`` (a 64-hex SHA-256
        produced by the L5 evaluator).  ``"remediation_hints"`` is
        optional but recommended for observability.
        """
        key = build_safety_eval_key(compiled_prompt_hash, policy_hash, toolset_hash)
        self._cache.set_json(key, eval_result, ttl_seconds=self._ttl)

    def get_or_fetch(
        self,
        compiled_prompt_hash: str,
        policy_hash: str,
        toolset_hash: str,
        fetch_from_l5: Any,
        *,
        replay_mode: bool = False,
    ) -> dict[str, Any]:
        """Read-through helper: return cached eval or call *fetch_from_l5*.

        *fetch_from_l5* is a zero-argument callable that runs the full L5
        safety evaluation and returns the result dict.  Called only on a
        cache miss.

        This is the canonical wiring point for L5 evaluator engines.  The
        evaluator should call this instead of running a live evaluation on
        every request.

        The returned dict must include at minimum ``"decision"`` and
        ``"compliance_hash"`` — the same contract as ``set()``.
        """
        if not replay_mode:
            cached = self.get(compiled_prompt_hash, policy_hash, toolset_hash)
            if cached is not None:
                logger.debug("[L5 cache] safety_eval HIT")
                return cached
        logger.debug("[L5 cache] safety_eval MISS — running live evaluation")
        result = fetch_from_l5()
        if not replay_mode:
            self.set(compiled_prompt_hash, policy_hash, toolset_hash, result)
        return result

    def invalidate(
        self,
        compiled_prompt_hash: str,
        policy_hash: str,
        toolset_hash: str,
    ) -> None:
        """Explicitly evict a safety-evaluation entry."""
        key = build_safety_eval_key(compiled_prompt_hash, policy_hash, toolset_hash)
        self._cache.delete(key)


# ---------------------------------------------------------------------------
# Module-level convenience singleton
# ---------------------------------------------------------------------------

_safety_eval_cache: SafetyEvalCache | None = None


def get_safety_eval_cache() -> SafetyEvalCache:
    """Return the process-global ``SafetyEvalCache`` instance."""
    global _safety_eval_cache
    if _safety_eval_cache is None:
        _safety_eval_cache = SafetyEvalCache()
    return _safety_eval_cache
