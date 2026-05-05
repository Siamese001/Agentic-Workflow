"""R1B semantic cache adapter for apps_rg.

Bridges apps_rg's ResumeGenerationIntent to L4 SemanticCacheManager.
Ensures intent vectors (not fact vectors) are used for cache keys.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Optional

from apps_rg.types.intent_payload import ResumeGenerationIntent
from apps_rg.utils.intent_builder import build_intent_from_request, derive_intent_hash

_logger = logging.getLogger(__name__)

# apps_rg-specific cache namespace
APPS_RG_CACHE_NAMESPACE = "apps_rg.resume_generation"

# Default similarity threshold — override via SEMANTIC_CACHE_THRESHOLD env var.
# Lower values are more permissive (more cache hits); higher values are stricter.
# Range: 0.0–1.0. Safe default 0.95 keeps false-positive hits low.
DEFAULT_SIMILARITY_THRESHOLD: float = 0.95

# Default TTL for semantic cache entries in seconds.
# Override via SEMANTIC_CACHE_TTL_SECONDS env var. 0 = no expiry (legacy behaviour).
# Default 86400 = 24 h.  Set to 0 to disable TTL enforcement.
DEFAULT_CACHE_TTL_SECONDS: int = 86400


def _get_similarity_threshold() -> float:
    """Read SEMANTIC_CACHE_THRESHOLD from env, fall back to DEFAULT.

    Out-of-range floats are clamped to [0.0, 1.0] with a warning.
    Non-numeric values fall back to DEFAULT with a warning.
    """
    raw = os.environ.get("SEMANTIC_CACHE_THRESHOLD", "")
    if raw:
        try:
            val = float(raw)
            if val < 0.0:
                _logger.warning(
                    "SEMANTIC_CACHE_THRESHOLD=%s below 0; clamping to 0.0", raw
                )
                return 0.0
            if val > 1.0:
                _logger.warning(
                    "SEMANTIC_CACHE_THRESHOLD=%s above 1; clamping to 1.0", raw
                )
                return 1.0
            return val
        except ValueError:
            _logger.warning(
                "SEMANTIC_CACHE_THRESHOLD=%s is not a float; using default %.2f",
                raw, DEFAULT_SIMILARITY_THRESHOLD,
            )
    return DEFAULT_SIMILARITY_THRESHOLD


def _get_cache_ttl_seconds() -> int:
    """Read SEMANTIC_CACHE_TTL_SECONDS from env, fall back to DEFAULT."""
    raw = os.environ.get("SEMANTIC_CACHE_TTL_SECONDS", "")
    if raw:
        try:
            val = int(raw)
            if val >= 0:
                return val
            _logger.warning(
                "SEMANTIC_CACHE_TTL_SECONDS=%s is negative; using default %d",
                raw, DEFAULT_CACHE_TTL_SECONDS,
            )
        except ValueError:
            _logger.warning(
                "SEMANTIC_CACHE_TTL_SECONDS=%s is not an int; using default %d",
                raw, DEFAULT_CACHE_TTL_SECONDS,
            )
    return DEFAULT_CACHE_TTL_SECONDS


class AppsRgR1BCacheAdapter:
    """Adapter for apps_rg R1B semantic cache operations."""

    def __init__(self, tenant_id: str = "default"):
        self.tenant_id = tenant_id
        self._cache = None  # Lazy init

    def _get_cache(self):
        """Lazy initialization of SemanticCacheManager."""
        if self._cache is None:
            try:
                from agentic_core.L4_state.utils.memory.semantic_cache_manager import (
                    SemanticCacheManager,
                )

                self._cache = SemanticCacheManager.get_instance()
            except ImportError as exc:
                _logger.warning("SemanticCacheManager unavailable: %s", exc)
                return None
        return self._cache

    def store_intent_and_output(
        self,
        intent: ResumeGenerationIntent,
        output_chunks: list[dict],
        run_context: dict,
    ) -> Optional[str]:
        """Store intent → output_chunks mapping in semantic cache.

        Called after successful apps_rg run (Exit cleared).
        Returns cache entry id on success, None on failure.
        """
        cache = self._get_cache()
        if cache is None:
            return None

        # Build the cache payload with full lineage
        intent_hash = derive_intent_hash(intent)
        cache_payload = {
            "intent_hash": intent_hash,
            "input_intent": intent.to_cache_key_dict(),
            "output_chunks": output_chunks,
            "lineage": {
                "source_run_id": run_context.get("run_id"),
                "source_request_id": intent.request_id,
                "source_input_intent_hash": intent_hash,
                "exit_disposition": run_context.get("exit_disposition"),
                "uwg_commit_receipt": run_context.get("uwg_commit_receipt"),
                "policy_hash": run_context.get("policy_hash"),
                "blueprint_hash": run_context.get("blueprint_hash"),
            },
        }

        # Use intent embedding text as cache context
        context = intent.to_embedding_text()

        try:
            # Store via SemanticCacheManager
            ttl = _get_cache_ttl_seconds()
            store_kwargs: dict = dict(
                context=context,
                response=json.dumps(cache_payload),
                namespace=APPS_RG_CACHE_NAMESPACE,
                tenant_id=self.tenant_id,
                metadata={
                    "intent_hash": cache_payload["intent_hash"],
                    "run_id": run_context.get("run_id"),
                    "policy_hash": run_context.get("policy_hash"),
                    "ttl_seconds": ttl,
                },
            )
            if ttl > 0:
                store_kwargs["ttl"] = ttl
            entry_id = cache.store(**store_kwargs)
            _logger.info("Stored R1B cache entry: %s", entry_id)
            return entry_id
        except Exception as exc:  # guardian: allow-broad-exception -- cache store is fail-soft
            _logger.warning("Failed to store R1B cache entry: %s", exc)
            return None

    def recall_output_for_intent(
        self,
        intent: ResumeGenerationIntent,
        policy_hash: str,
        blueprint_hash: str,
        similarity_threshold: float | None = None,
    ) -> Optional[dict]:
        """Recall cached output chunks for given intent.

        similarity_threshold defaults to ``_get_similarity_threshold()`` which
        reads ``SEMANTIC_CACHE_THRESHOLD`` env var at call time.  Pass an explicit
        value only in tests that need deterministic behaviour.
        Validates policy/blueprint compatibility and similarity before returning.
        """
        if similarity_threshold is None:
            similarity_threshold = _get_similarity_threshold()

        cache = self._get_cache()
        if cache is None:
            return None

        context = intent.to_embedding_text()

        try:
            hit = cache.recall(
                context=context,
                namespace=APPS_RG_CACHE_NAMESPACE,
                tenant_id=self.tenant_id,
            )

            if hit is None:
                return None

            # Parse and validate
            payload = json.loads(hit.get("response", "{}"))
            lineage = payload.get("lineage", {})

            # Validate policy compatibility
            if lineage.get("policy_hash") != policy_hash:
                _logger.info(
                    "R1B hit rejected: policy hash mismatch "
                    "(cached=%s, current=%s)",
                    lineage.get("policy_hash"),
                    policy_hash,
                )
                return None

            # Validate blueprint compatibility
            if lineage.get("blueprint_hash") != blueprint_hash:
                _logger.info(
                    "R1B hit rejected: blueprint hash mismatch "
                    "(cached=%s, current=%s)",
                    lineage.get("blueprint_hash"),
                    blueprint_hash,
                )
                return None

            # Validate similarity threshold
            similarity = hit.get("similarity", 0.0)
            if isinstance(similarity, (int, float)) and similarity < similarity_threshold:
                _logger.info(
                    "R1B hit rejected: similarity %.3f < threshold %.3f",
                    similarity,
                    similarity_threshold,
                )
                return None

            _logger.info("R1B cache hit validated: intent_hash=%s", payload.get("intent_hash"))
            return payload

        except Exception as exc:  # guardian: allow-broad-exception -- cache recall is fail-soft
            _logger.debug("R1B cache recall failed: %s", exc)
            return None


def check_r1b_for_apps_rg(
    candidate_profile_path: str,
    target_company: str,
    target_role: str,
    policy_hash: str,
    blueprint_hash: str,
    **kwargs,
) -> Optional[dict]:
    """High-level R1B check for apps_rg L0 routing.

    Returns cached output with lineage on valid hit, None otherwise.
    """
    intent = build_intent_from_request(
        candidate_profile_path=Path(candidate_profile_path),
        target_company=target_company,
        target_role=target_role,
        **kwargs,
    )

    adapter = AppsRgR1BCacheAdapter(tenant_id=kwargs.get("tenant_id", "default"))
    return adapter.recall_output_for_intent(
        intent=intent,
        policy_hash=policy_hash,
        blueprint_hash=blueprint_hash,
    )


__all__ = [
    "APPS_RG_CACHE_NAMESPACE",
    "DEFAULT_SIMILARITY_THRESHOLD",
    "DEFAULT_CACHE_TTL_SECONDS",
    "AppsRgR1BCacheAdapter",
    "check_r1b_for_apps_rg",
    "_get_similarity_threshold",
    "_get_cache_ttl_seconds",
]
