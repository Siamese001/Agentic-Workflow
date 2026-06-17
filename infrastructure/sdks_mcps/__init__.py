"""Production SDK wrappers package.

Package root is a thin re-export surface. Canonical implementation lives in
``infrastructure.sdks_mcps.client_wrappers`` so both package-root and explicit
module imports stay consistent.
"""

from __future__ import annotations

from .client_wrappers import (
    AnthropicClient,
    AnthropicConfig,
    OpenAIClient,
    OpenAIConfig,
    VertexClient,
    VertexConfig,
    create_anthropic_client,
    create_gemini_model,
    create_openai_client,
    create_openai_sync_client,
    create_vertex_client,
)

__all__ = [
    "create_openai_client",
    "create_openai_sync_client",
    "create_anthropic_client",
    "create_vertex_client",
    "create_gemini_model",
    "OpenAIClient",
    "AnthropicClient",
    "VertexClient",
    "OpenAIConfig",
    "AnthropicConfig",
    "VertexConfig",
]

__version__ = "1.0.0"
__description__ = "Production SDK wrappers for OpenAI, Anthropic, and Google Vertex AI"
