"""Pinecone client wrapper for vector operations."""
from typing import Any, Dict, List, Optional, TypedDict
import os
import pinecone
from openai import OpenAI


class Vector(TypedDict):
    id: str
    values: List[float]
    metadata: Dict[str, Any]


class PineconeClient:
    """A client for interacting with Pinecone's vector database.
    
    This client provides a simple interface for common vector operations
    while abstracting away the underlying Pinecone SDK details.
    """
    
    def __init__(self, api_key: str, index_name: str):
        """Initialize the Pinecone client.
        
        Args:
            api_key: Pinecone API key
            index_name: Name of the Pinecone index to use
        """
        pinecone.init(api_key=api_key)
        self.index = pinecone.Index(index_name)
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def upsert(
        self, 
        namespace: str, 
        vectors: List[Vector],
        **kwargs
    ) -> None:
        """Upsert vectors into the specified namespace.
        
        Args:
            namespace: The namespace to upsert vectors into
            vectors: List of vector dictionaries with 'id', 'values', and 'metadata'
            **kwargs: Additional arguments to pass to Pinecone's upsert
        """
        self.index.upsert(
            vectors=vectors,
            namespace=namespace,
            **kwargs
        )
    
    def query(
        self,
        namespace: str,
        vector: List[float],
        top_k: int = 5,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Query the vector database for similar vectors.
        
        Args:
            namespace: The namespace to query
            vector: Query vector
            top_k: Number of results to return
            **kwargs: Additional query parameters
            
        Returns:
            List of matching vectors with scores and metadata
        """
        results = self.index.query(
            vector=vector,
            top_k=top_k,
            namespace=namespace,
            include_metadata=True,
            **kwargs
        )
        return results.get('matches', [])
    
    def delete(
        self,
        namespace: str,
        ids: List[str],
        **kwargs
    ) -> None:
        """Delete vectors by their IDs from the specified namespace.
        
        Args:
            namespace: The namespace to delete from
            ids: List of vector IDs to delete
            **kwargs: Additional delete parameters
        """
        self.index.delete(
            ids=ids,
            namespace=namespace,
            **kwargs
        )
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for the given text using OpenAI's text-embedding-3-small model.
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the text embedding
        """
        response = self.openai_client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        return response.data[0].embedding
