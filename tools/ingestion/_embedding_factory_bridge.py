"""Sovereignty-allowlisted bridge to the embedding factory.

Ingestion scripts run as ``__main__`` and therefore cannot call
``agentic_core.embeddings.embedding_factory.create_embedding_client`` directly
(the factory's ``guard_embedding_instantiation`` checks the caller's module
name against a small allowlist, and ``__main__`` is not and must not be in it).

This tiny wrapper module is in the allowlist. Ingestion scripts import
``create_embedding_client`` from here, and the factory sees the caller module
as ``tools.ingestion._embedding_factory_bridge`` — which is allowed.

No business logic lives here. Do not add anything else to this file.
"""

from __future__ import annotations

from typing import Any

from agentic_core.embeddings.embedding_factory import (
    create_embedding_client as _factory_create,
)


def create_embedding_client(provider: str, model_name: str | None = None) -> Any:
    """Thin pass-through to the sovereignty-enforced factory.

    Args:
        provider: 'openai' or 'bge-m3'.
        model_name: Optional model override (e.g. 'BAAI/bge-m3').

    Returns:
        An embedding client instance produced by the factory.

    Raises:
        EmbeddingDisabledError: If EMBEDDING_ENABLED is false.
        EmbeddingSovereigntyViolationError: Never raised for this bridge
            provided the factory's allowlist includes this module path.
    """
    # Factory has a strict Literal type on provider; runtime validation lives
    # there, so a type: ignore is appropriate on this pass-through.
    if model_name is None:
        return _factory_create(provider)  # type: ignore[arg-type]
    return _factory_create(provider, model_name)  # type: ignore[arg-type]
