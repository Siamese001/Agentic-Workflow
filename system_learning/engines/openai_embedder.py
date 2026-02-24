"""OpenAI Embedder for Plan B Phase 5.

Production embedder using OpenAI's text-embedding-3-large model.
"""

from __future__ import annotations

import os
from typing import Any

try:
    import openai
    from openai import OpenAI
except ImportError:
    openai = None
    OpenAI = None


class OpenAIEmbedder:
    """OpenAI embedder implementing the Embedder protocol.
    
    Uses text-embedding-3-large model for production semantic embeddings.
    """

    def __init__(self, model: str = "text-embedding-3-large"):
        """Initialize the OpenAI embedder.
        
        Args:
            model: OpenAI model name to use.
            
        Raises:
            ImportError: If openai package not installed.
            ValueError: If OPENAI_API_KEY not found in environment.
        """
        if openai is None or OpenAI is None:
            raise ImportError(
                "openai package is required. Install with: pip install openai"
            )
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is required"
            )
        
        self.model = model
        self.client = OpenAI(api_key=api_key)

    def embed_batch(
        self, 
        texts: list[str], 
        *, 
        dimensions: int | None = None
    ) -> list[list[float]]:
        """Embed a batch of texts using OpenAI.
        
        Args:
            texts: List of texts to embed.
            dimensions: Optional dimension override (not used, API determines dimensions).
            
        Returns:
            List of embedding vectors as lists of floats.
            
        Raises:
            openai.APIError: If API call fails.
        """
        # Normalize input by replacing newlines with spaces
        normalized_texts = [text.replace("\r\n", " ").replace("\n", " ").replace("\r", " ") for text in texts]
        
        # Call OpenAI embeddings API
        response = self.client.embeddings.create(
            model=self.model,
            input=normalized_texts
        )
        
        # Extract and return vectors
        return [data.embedding for data in response.data]

    def get_model_info(self) -> dict[str, Any]:
        """Get information about the current model.
        
        Returns:
            Dictionary with model information.
        """
        # Embed a single text to get model dimensions
        test_embedding = self.embed_batch(["test"])
        
        return {
            "model": self.model,
            "dimensions": len(test_embedding[0]),
        }

    def get_model_checksum(self) -> str:
        """Generate checksum for model identification.
        
        Returns:
            Checksum string combining model and configuration.
        """
        import hashlib
        
        # Create checksum from model name and fixed config
        config_str = f"{self.model}:openai_embeddings_v1"
        return hashlib.sha256(config_str.encode()).hexdigest()[:16]


__all__ = ["OpenAIEmbedder"]
