"""
EmbeddingMixin - Unified Embedding Access for Agents

[PHASE 4 MIGRATION] Provides single interface to embedding operations.
"""

from typing import Any, Literal

# from agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent import (
#     get_embedding_gateway,
#     EmbeddingSovereignAgent,
# )

EmbeddingProvider = Literal["gemini", "openai"]


class EmbeddingMixin:
    """
    Mixin providing unified embedding gateway access.

    [PHASE 4 MIGRATION] Replaces direct embedding implementations.

    Usage:
        class MyAgent(EmbeddingMixin, SovereignBaseAgent):
            async def process(self, text: str):
                embedding = await self.get_embedding(text)
                return embedding
    """

    _embedding_gateway: Any | None = None

    @property
    def embedding_gateway(self) -> Any:
        """Lazy-load embedding gateway singleton."""
        if self._embedding_gateway is None:
            try:
                from agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent import (
                    get_embedding_gateway,
                )

                self._embedding_gateway = get_embedding_gateway()
            except ImportError:
                raise NotImplementedError(
                    "EmbeddingMixin: Embedding gateway is not available. "
                    "Install the required dependencies or configure "
                    "agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent."
                )
        return self._embedding_gateway

    async def get_embedding(
        self,
        content: str,
        provider: EmbeddingProvider = "gemini",
        use_cache: bool = True,
    ) -> list[float]:
        """Get embedding through gateway."""
        return await self.embedding_gateway.get_embedding(content, provider, use_cache)

    async def get_embeddings_batch(
        self,
        contents: list[str],
        provider: EmbeddingProvider = "gemini",
    ) -> list[list[float]]:
        """Get batch embeddings through gateway."""
        return await self.embedding_gateway.get_embeddings_batch(contents, provider)
