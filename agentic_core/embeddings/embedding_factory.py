"""Embedding Factory - Single Embedding Seam for Sovereign Access

[PHASE 7] Canonical embedding factory providing:
- Single seam for all embedding operations
- EMBEDDING_ENABLED kill-switch (fail-closed)
- Runtime guard against direct SDK instantiation
- Deterministic artifact binding
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from typing import Any, Literal, Protocol, runtime_checkable

from agentic_core.embeddings.embedding_input_guard import GuardedText
from agentic_core.replay.replay_envelope import create_deterministic_cache_key
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

logger = logging.getLogger(__name__)


def is_enabled() -> bool:
    """Dynamically check the embedding kill-switch from environment.

    Returns:
        True if embeddings are enabled, False otherwise.
    """
    return os.environ.get("EMBEDDING_ENABLED", "true").lower() == "true"


# For module-level logging, check once at import time.
EMBEDDING_ENABLED = is_enabled()


class EmbeddingDisabledError(RuntimeError):
    """Raised when embedding operations are attempted while disabled."""

    pass


class EmbeddingSovereigntyViolationError(RuntimeError):
    """Raised when embedding client is instantiated outside factory."""

    pass


@runtime_checkable
class EmbeddingClient(Protocol):
    """Protocol for embedding clients to ensure type safety."""

    async def get_embedding(self, guarded_text: GuardedText) -> list[float]:
        """Get embedding for a single guarded text."""
        ...

    async def get_embeddings_batch(self, guarded_texts: list[GuardedText]) -> list[list[float]]:
        """Get embeddings for multiple guarded texts."""
        ...


# Registry for tracking embedding client instances
_embedding_client_registry: dict[str, Any] = {}


def register_embedding_client(name: str, client: EmbeddingClient) -> None:
    """Register an embedding client instance for tracking."""
    if not is_enabled():
        raise EmbeddingDisabledError("EMBEDDING_ENABLED=false: Cannot register embedding clients")

    _embedding_client_registry[name] = client
    logger.info(f"Registered embedding client: {name}")


def get_embedding_client(name: str = "default") -> EmbeddingClient:
    """Get a registered embedding client."""
    if not is_enabled():
        raise EmbeddingDisabledError("EMBEDDING_ENABLED=false: Embedding operations are disabled")

    if name not in _embedding_client_registry:
        raise ValueError(f"Embedding client '{name}' not registered")

    return _embedding_client_registry[name]


def create_embedding_client(
    provider: Literal["openai", "gemini", "anthropic"],
    model: str | None = None,
    **kwargs: Any,
) -> EmbeddingClient:
    """
    Create an embedding client through the factory.

    This is the ONLY allowed way to create embedding clients.
    Direct instantiation of embedding SDK clients outside this factory
    will raise EmbeddingSovereigntyViolationError.
    """
    if not is_enabled():
        raise EmbeddingDisabledError("EMBEDDING_ENABLED=false: Cannot create embedding clients")

    # Import through client wrappers (allowed seam)
    from data.sdks_mcps.client_wrappers import (
        create_openai_client,
        create_vertex_client,
    )

    client_name = f"{provider}_{model or 'default'}"

    if provider == "openai":
        raw_client = create_openai_client()

        # Wrap to provide embedding interface
        class OpenAIEmbeddingClient:
            def __init__(self, model: str, dimensions: int | None = None):
                self.model = model
                self.dimensions = dimensions
                self.observed_dimension: int | None = None
                self._cache: dict[str, list[float]] = {}
                # Compute pack hash for replay key
                pack_hash_str = f"openai_{model}_{dimensions or 'default'}"
                self.pack_hash = hashlib.sha256(pack_hash_str.encode("utf-8")).hexdigest()[:16]

                # W11: Embedder identity for deterministic cache keys
                self.embedder_identity = {
                    "provider": "openai",
                    "model": self.model,
                    "dimensions": self.dimensions,
                    "normalization_policy": "l2",
                    "chunking_policy": "none",
                }

            async def get_embedding(self, guarded_text: GuardedText) -> list[float]:
                import uuid as _uuid  # noqa: PLC0415
                _trace_id = str(_uuid.uuid4())
                _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "OpenAIEmbeddingClient.get_embedding")

                # W11: Use deterministic cache key with embedder identity
                cache_key = create_deterministic_cache_key(guarded_text.redacted_text, self.embedder_identity)
                if cache_key in self._cache:
                    return self._cache[cache_key]

                kwargs = {"model": self.model, "input": guarded_text.redacted_text}
                if self.dimensions:
                    kwargs["dimensions"] = self.dimensions
                response = await raw_client.embeddings.create(**kwargs)
                embedding = response.data[0].embedding

                # W11: Stable float32 casting for determinism
                embedding = [float(x) for x in embedding]

                if self.observed_dimension is None:
                    self.observed_dimension = len(embedding)

                self._cache[cache_key] = embedding
                return embedding

            async def get_embeddings_batch(self, guarded_texts: list[GuardedText]) -> list[list[float]]:
                results: list[list[float] | None] = [None] * len(guarded_texts)
                texts_to_embed: list[tuple[int, GuardedText]] = []

                for i, guarded_text in enumerate(guarded_texts):
                    # W11: Use deterministic cache key with embedder identity
                    cache_key = create_deterministic_cache_key(
                        guarded_text.redacted_text, self.embedder_identity
                    )
                    if cache_key in self._cache:
                        results[i] = self._cache[cache_key]
                    else:
                        texts_to_embed.append((i, guarded_text))

                if not texts_to_embed:
                    return [r for r in results if r is not None]

                kwargs = {"model": self.model, "input": [gt.redacted_text for _, gt in texts_to_embed]}
                if self.dimensions:
                    kwargs["dimensions"] = self.dimensions

                response = await raw_client.embeddings.create(**kwargs)
                embeddings = [item.embedding for item in response.data]

                # W11: Stable float32 casting for determinism
                embeddings = [[float(x) for x in emb] for emb in embeddings]

                if self.observed_dimension is None and embeddings:
                    self.observed_dimension = len(embeddings[0])

                for i, embedding in enumerate(embeddings):
                    original_index, guarded_text = texts_to_embed[i]
                    # W11: Use deterministic cache key
                    cache_key = create_deterministic_cache_key(
                        guarded_text.redacted_text, self.embedder_identity
                    )
                    self._cache[cache_key] = embedding
                    results[original_index] = embedding

                return [r for r in results if r is not None]

            def get_replay_metadata(self) -> dict[str, Any]:
                """Get embedder metadata for replay key surface."""
                return {
                    "provider": "openai",
                    "model": self.model,
                    "pack_hash": self.pack_hash,
                    "embedding_dimension": self.observed_dimension or self.dimensions or 1536,
                    "distance_metric": "cosine",
                    "tokenization_policy_version": "cl100k_base_v1",
                    "normalization_policy": "l2",
                    "chunking_policy": "none",
                    "hs_injection_surface_version": "1.0",
                }

        client = OpenAIEmbeddingClient(model or "text-embedding-3-large", dimensions=kwargs.get("dimensions"))

    elif provider == "gemini":
        raw_client = create_vertex_client()
        # Note: Vertex AI embeddings implementation would go here
        # For now, raise NotImplementedError
        raise NotImplementedError("Gemini embeddings not yet implemented through factory")

    elif provider == "anthropic":
        # Anthropic doesn't provide embeddings, but we keep the interface
        raise NotImplementedError("Anthropic does not provide embedding models")

    else:
        raise ValueError(f"Unsupported embedding provider: {provider}")

    # Register and return
    register_embedding_client(client_name, client)
    return client


def guard_embedding_instantiation(module_name: str, class_name: str) -> None:
    """
    Runtime guard to prevent direct embedding SDK instantiation.

    Call this from any module that might be tempted to instantiate
    embedding clients directly.
    """
    # Allowlist of modules that can instantiate embedding clients
    allowed_modules = {
        "agentic_core.embeddings.embedding_factory",
        "data.sdks_mcps.client_wrappers",
        "agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent",
        "system_learning.engines.embedding_service_factory",
    }

    if module_name not in allowed_modules:
        raise EmbeddingSovereigntyViolationError(
            f"EMBEDDING_SOVEREIGNTY_VIOLATION: {module_name}.{class_name} "
            f"attempted to instantiate embedding client outside factory. "
            f"Use agentic_core.embeddings.embedding_factory.create_embedding_client() instead."
        )


def compute_w7_sovereignty_digest() -> str:
    """
    Compute W7-EMBEDDING-SOVEREIGNTY-DIGEST.

    Hash over canonical JSON of embedding sovereignty state.
    """
    # Get fingerprint of this module
    module_path = __file__
    with open(module_path, "rb") as f:
        module_hash = hashlib.sha256(f.read()).hexdigest()

    # Build canonical state
    state = {
        "embedding_enabled": is_enabled(),
        "factory_module_hash": module_hash,
        "registered_clients": sorted(_embedding_client_registry.keys()),
        "allowed_providers": ["openai", "gemini", "anthropic"],
        "kill_switch_default": "true",
        "factory_path": "agentic_core/embeddings/embedding_factory.py",
    }

    # Compute deterministic hash
    canonical_json = json.dumps(state, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


# Module initialization
if EMBEDDING_ENABLED:
    logger.info("EmbeddingFactory: EMBEDDING_ENABLED=true - embeddings allowed")
else:
    logger.warning("EmbeddingFactory: EMBEDDING_ENABLED=false - embeddings disabled (fail-closed)")
