# Sovereign Gemini Embeddings Generator
# Territory: agentic_core/semantic_memory/embeddings
# Canon Key 9 - Vector embedding generation

import google.generativeai as genai
from typing import List
import os


class GeminiEmbedder:
    """
    Sovereign wrapper for Gemini embedding model.
    Uses configured GEMINI_MODEL and GOOGLE_API_KEY.
    """

    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not set")
        genai.configure(api_key=api_key)
        self.model = os.getenv("GEMINI_EMBEDDING_MODEL", "models/embedding-001")

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for list of text chunks.

        Args:
            texts: List of strings (paragraphs/documents)

        Returns:
            List of embedding vectors
        """
        try:
            result = genai.embed_content(
                model=self.model,
                content=texts,
                task_type="retrieval_document",
            )
            return result["embedding"]
        except Exception as e:
            raise RuntimeError(f"Gemini embedding failed: {e}")

    def embed_query(self, query: str) -> List[float]:
        """Embed single query string."""
        return self.embed_texts([query])[0]


# Factory
def get_gemini_embedder() -> GeminiEmbedder:
    return GeminiEmbedder()
