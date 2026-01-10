from __future__ import annotations
import google.generativeai as genai
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
from typing import Any, List
import os

class GeminiEmbedder:
    """
    Sovereign wrapper for Gemini embedding model.
    Uses configured GEMINI_MODEL and GOOGLE_API_KEY.
    """

    def __init__(self):
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError('GOOGLE_API_KEY not set')
        genai.configure(api_key=api_key)
        self.model = os.getenv('GEMINI_EMBEDDING_MODEL', 'models/embedding-001')

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for list of text chunks.

        Args:
            texts: List of strings (paragraphs/documents)

        Returns:
            List of embedding vectors
        """
        try:
            result: Any = genai.embed_content(model=self.model, content=texts)
            return result['embedding']
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
