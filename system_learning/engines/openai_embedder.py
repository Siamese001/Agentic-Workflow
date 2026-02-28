"""OpenAI Embedder for Plan B Phase 5.

Production embedder using OpenAI's text-embedding-3-large model.
Direct OpenAI SDK wrapper — does NOT go through embedding_factory.
"""

from __future__ import annotations

import hashlib
import os

try:
    import openai as openai
    from openai import OpenAI
except ImportError:
    openai = None  # type: ignore[assignment]
    OpenAI = None  # type: ignore[assignment]

_MODEL_DIMENSIONS = {
    "text-embedding-3-large": 1536,
    "text-embedding-3-small": 1536,
    "text-embedding-ada-002": 1536,
}


class OpenAIEmbedder:
    """OpenAI embedder — direct SDK wrapper.

    Uses text-embedding-3-large model for production semantic embeddings.
    """

    def __init__(self, model: str = "text-embedding-3-large", dimensions: int | None = None):
        """Initialize the OpenAI embedder.

        Args:
            model: OpenAI model name to use.
            dimensions: Ignored — API determines output dimensions.

        Raises:
            ImportError: If the openai package is not installed.
            ValueError: If OPENAI_API_KEY environment variable is not set.
        """
        if openai is None:
            raise ImportError("openai package is required. Install with: pip install openai")

        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        self.model = model
        self._client = OpenAI(api_key=api_key)

    def embed_batch(self, texts: list[str], *, dimensions: int | None = None) -> list[list[float]]:
        """Embed a batch of texts using OpenAI.

        Args:
            texts: List of texts to embed.
            dimensions: Ignored — API determines output dimensions.

        Returns:
            List of embedding vectors as lists of floats.
        """
        normalized = [t.replace("\r\n", " ").replace("\n", " ").replace("\r", " ") for t in texts]
        response = self._client.embeddings.create(model=self.model, input=normalized)
        return [item.embedding for item in response.data]

    def get_model_info(self) -> dict:
        """Return model information including dimensions."""
        return {
            "model": self.model,
            "dimensions": _MODEL_DIMENSIONS.get(self.model, 1536),
        }

    def get_model_checksum(self) -> str:
        """Return a deterministic 16-char hex checksum for the model name."""
        return hashlib.sha256(self.model.encode()).hexdigest()[:16]


__all__ = ["OpenAIEmbedder"]
