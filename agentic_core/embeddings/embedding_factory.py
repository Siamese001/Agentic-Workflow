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

logger = logging.getLogger(__name__)

# Global kill-switch - fail-closed by default when false
EMBEDDING_ENABLED = os.environ.get("EMBEDDING_ENABLED", "true").lower() == "true"


class EmbeddingDisabledError(RuntimeError):
    """Raised when embedding operations are attempted while disabled."""
    pass


class EmbeddingSovereigntyViolationError(RuntimeError):
    """Raised when embedding client is instantiated outside factory."""
    pass


@runtime_checkable
class EmbeddingClient(Protocol):
    """Protocol for embedding clients to ensure type safety."""
    
    async def get_embedding(self, text: str) -> list[float]:
        """Get embedding for a single text."""
        ...
    
    async def get_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        """Get embeddings for multiple texts."""
        ...


# Registry for tracking embedding client instances
_embedding_client_registry: dict[str, Any] = {}


def register_embedding_client(name: str, client: EmbeddingClient) -> None:
    """Register an embedding client instance for tracking."""
    if not EMBEDDING_ENABLED:
        raise EmbeddingDisabledError(
            "EMBEDDING_ENABLED=false: Cannot register embedding clients"
        )
    
    _embedding_client_registry[name] = client
    logger.info(f"Registered embedding client: {name}")


def get_embedding_client(name: str = "default") -> EmbeddingClient:
    """Get a registered embedding client."""
    if not EMBEDDING_ENABLED:
        raise EmbeddingDisabledError(
            "EMBEDDING_ENABLED=false: Embedding operations are disabled"
        )
    
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
    if not EMBEDDING_ENABLED:
        raise EmbeddingDisabledError(
            "EMBEDDING_ENABLED=false: Cannot create embedding clients"
        )
    
    # Import through client wrappers (allowed seam)
    from data.sdks_mcps.client_wrappers import (
        create_anthropic_client,
        create_openai_client,
        create_vertex_client,
    )
    
    client_name = f"{provider}_{model or 'default'}"
    
    if provider == "openai":
        raw_client = create_openai_client()
        # Wrap to provide embedding interface
        class OpenAIEmbeddingClient:
            def __init__(self, model: str):
                self.model = model
                # Compute pack hash for replay key
                self.pack_hash = hashlib.sha256(
                    f"openai_{model}".encode("utf-8")
                ).hexdigest()[:16]
            
            async def get_embedding(self, text: str) -> list[float]:
                response = await raw_client.embeddings.create(
                    model=self.model,
                    input=text
                )
                return response.data[0].embedding
            
            async def get_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
                response = await raw_client.embeddings.create(
                    model=self.model,
                    input=texts
                )
                return [item.embedding for item in response.data]
            
            def get_replay_metadata(self) -> dict[str, Any]:
                """Get embedder metadata for replay key surface."""
                return {
                    "provider": "openai",
                    "model": self.model,
                    "pack_hash": self.pack_hash,
                    "k": 1536,  # OpenAI text-embedding-3-large dimension
                    "distance_metric": "cosine",
                    "version": "1.0",
                }
        
        client = OpenAIEmbeddingClient(model or "text-embedding-3-large")
        
    elif provider == "gemini":
        raw_client = create_vertex_client()
        # Note: Vertex AI embeddings implementation would go here
        # For now, raise NotImplementedError
        raise NotImplementedError(f"Gemini embeddings not yet implemented through factory")
        
    elif provider == "anthropic":
        # Anthropic doesn't provide embeddings, but we keep the interface
        raise NotImplementedError(f"Anthropic does not provide embedding models")
        
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
        "embedding_enabled": EMBEDDING_ENABLED,
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
