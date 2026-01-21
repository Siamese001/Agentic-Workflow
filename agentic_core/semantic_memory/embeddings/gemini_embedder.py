from __future__ import annotations
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
from typing import Any, List
import os

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None
    types = None

class GeminiEmbedder:
    """
    Sovereign wrapper for Gemini embedding model.
    Uses configured GEMINI_MODEL and GOOGLE_API_KEY.
    Updated to use google.genai package (replaces deprecated google-generativeai).
    """

    def __init__(self):
        if not GENAI_AVAILABLE:
            raise RuntimeError('google-genai package not available. Install with: pip install google-genai')
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError('GOOGLE_API_KEY not set')
        self.client = genai.Client(api_key=api_key)
        self.model = os.getenv('GEMINI_EMBEDDING_MODEL', 'text-embedding-004')

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for list of text chunks.

        Args:
            texts: List of strings (paragraphs/documents)

        Returns:
            List of embedding vectors
        """
        try:
            embeddings = []
            for text in texts:
                result = self.client.models.embed_content(
                    model=self.model,
                    contents=text  # Fixed: 'contents' not 'content'
                )
                embeddings.append(result.embeddings[0].values)
            return embeddings
        except Exception as e:
            raise RuntimeError(f'Gemini embedding failed: {e}')

    def embed_query(self, query: str) -> List[float]:
        """
        Generates semantic vectors with built-in error handling.
        
        Args:
            query: Text string to embed
            
        Returns:
            List of float values representing the embedding vector, or None on failure
        """
        try:
            result = self.embed_texts([query])
            if result and len(result) > 0:
                return result[0]
            else:
                print(f"⚠️  Meta-Learning Error: Empty embedding result for query")
                return None
        except Exception as e:
            print(f"⚠️  Meta-Learning Error: Failed to generate embedding: {e}")
            return None

def get_gemini_embedder() -> GeminiEmbedder:
    """Brief description of functionality and purpose."""
    return GeminiEmbedder()
