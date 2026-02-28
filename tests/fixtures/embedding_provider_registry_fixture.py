"""Single registry fixture for embedding provider constants.

All invariant tests must import provider/model details from here.
No test file may hard-code provider names, model IDs, or dimensions directly.
"""

from __future__ import annotations

DEFAULT_PROVIDER_ID: str = "factory-default"
DEFAULT_MODEL_ID: str = "registry-canonical-v1"
DEFAULT_DIMENSIONS: int = 1024

_SUPPORTED_PROVIDERS: tuple[str, ...] = (
    "factory-default",
    "bge",
    "openai",
    "cohere",
)


def list_supported_providers() -> tuple[str, ...]:
    """Return tuple of all supported provider IDs."""
    return _SUPPORTED_PROVIDERS


def get_default_dimensions() -> int:
    """Return canonical embedding dimension from registry."""
    return DEFAULT_DIMENSIONS


def get_default_model_id() -> str:
    """Return canonical model ID from registry."""
    return DEFAULT_MODEL_ID


def get_default_provider_id() -> str:
    """Return canonical provider ID from registry."""
    return DEFAULT_PROVIDER_ID
