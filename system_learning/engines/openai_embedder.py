"""OpenAI Embedder for Plan B Phase 5.

Production embedder using OpenAI's text-embedding-3-large model.
"""

from __future__ import annotations

from agentic_core.embeddings.embedding_factory import EmbeddingClient, create_embedding_client
from agentic_core.embeddings.embedding_input_guard import EmbeddingInputGuard


class OpenAIEmbedder:
    """OpenAI embedder implementing the Embedder protocol.

    Uses text-embedding-3-large model for production semantic embeddings.
    """

    def __init__(self, model: str = "text-embedding-3-large", dimensions: int | None = 1536):
        """Initialize the OpenAI embedder using the embedding factory.

        Args:
            model: OpenAI model name to use.
            dimensions: The embedding dimensions.
        """
        self.model = model
        self.dimensions = dimensions
        self.client: EmbeddingClient = create_embedding_client(
            provider="openai", model=model, dimensions=dimensions
        )

    async def embed_batch(self, texts: list[str], *, dimensions: int | None = None) -> list[list[float]]:
        """Embed a batch of texts using OpenAI.

        Args:
            texts: List of texts to embed.
            dimensions: Optional dimension override (not used, API determines dimensions).

        Returns:
            List of embedding vectors as lists of floats.

        Raises:
            openai.APIError: If API call fails.
        """
        # Guard and batch texts
        guarded_texts = [EmbeddingInputGuard.guard(text, "rag_query") for text in texts]

        # The factory client handles batching internally, but we add retry logic here
        # for the build script context, which doesn't use the HardeningMixin.
        for attempt in range(8):
            try:
                return await self.client.get_embeddings_batch(guarded_texts)
            except Exception as e:
                if "429" in str(e) or "rate" in str(e).lower() or "quota" in str(e).lower():
                    wait = 2**attempt
                    print(f"  Rate limited, waiting {wait}s (attempt {attempt + 1}/8)...", flush=True)
                    import time as _time

                    _time.sleep(wait)
                else:
                    raise
        raise RuntimeError("Failed to embed batch after 8 retries")


__all__ = ["OpenAIEmbedder"]
