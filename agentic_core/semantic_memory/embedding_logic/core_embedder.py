"""
Core Embedding Logic - Sovereign Primary
Provides standardized embedding generation for semantic memory operations.
"""
import os
from typing import List, Optional
import openai

class CoreEmbedder:
    """
    Sovereign wrapper for OpenAI embeddings with fallback support.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "text-embedding-3-large"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable or api_key argument required")
        
        self.model = model
        openai.api_key = self.api_key
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for the given text.
        """
        try:
            response = openai.Embedding.create(
                model=self.model,
                input=text
            )
            return response['data'][0]['embedding']
        except Exception as e:
            print(f"[Error] Failed to generate embedding: {e}")
            # Return zero embedding as fallback
            return [0.0] * 1536  # Default dimension for text-embedding-3-large

# Global embedder instance
_embedder: Optional[CoreEmbedder] = None

def get_embedding(text: str) -> List[float]:
    """
    Convenience function to get embedding using the global embedder.
    """
    global _embedder
    if _embedder is None:
        _embedder = CoreEmbedder()
    return _embedder.get_embedding(text)
