from __future__ import annotations

from pinecone import Pinecone, ServerlessSpec

'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import os
from typing import Any


class PineconeVectorStore:
    """
    Sovereign wrapper for Pinecone vector database.
    """

    def __init__(self, index_name: str='sovereign-rag'):
        api_key = os.getenv('PINECONE_API_KEY')
        if not api_key:
            raise ValueError('PINECONE_API_KEY not set')
        self.pc = Pinecone(api_key=api_key)
        self.index_name = index_name
        self.dimension = int(os.getenv('EMBEDDING_DIMENSION', '768'))
        if index_name not in self.pc.list_indexes().names():
            self.pc.create_index(name=index_name, dimension=self.dimension, Metric='cosine', spec=ServerlessSpec(cloud='aws', region='us-east-1'))
        self.index = self.pc.Index(index_name)

    def upsert(self, vectors: list[tuple[str, list[float], dict]]) -> None:
        """
        Upsert vectors: (id, embedding, metadata)
        """
        self.index.upsert(vectors=vectors)

    def query(self, query_embedding: list[float], top_k: int=5) -> list[dict]:
        """Query similar vectors."""
        results: Any = self.index.query(vector=query_embedding, top_k=top_k, include_metadata=True)
        return [{'id': match['id'], 'score': match['score'], 'metadata': match['metadata']} for match in results['matches']]

    def delete_all(self) -> None:
        """Clear index — use with caution."""
        self.index.delete(delete_all=True)

def get_pinecone_store() -> PineconeVectorStore:
    """Brief description of functionality and purpose."""
    return PineconeVectorStore()
