"""L2 Vector search execution layer."""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import os
from openai import OpenAI
from ..providers.pinecone_client import PineconeClient, Vector


@dataclass
class SearchResult:
    """Container for vector search results."""
    id: str
    score: float
    metadata: Dict[str, Any]


class VectorSearchExecutor:
    """Handles execution of vector search operations.
    
    This class is responsible for executing vector search operations using Pinecone
    and managing the embedding of text using OpenAI's embedding models.
    """
    
    def __init__(self, pinecone_client: PineconeClient):
        """Initialize with a Pinecone client.
        
        Args:
            pinecone_client: Configured PineconeClient instance
        """
        self.pinecone = pinecone_client
        self.openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for the given text.
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the text embedding
        """
        return self.pinecone.get_embedding(text)
    
    def upsert_text(
        self,
        namespace: str,
        id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Upsert a text document into the vector store.
        
        Args:
            namespace: Namespace in the vector store
            id: Unique identifier for the document
            text: Text content to store
            metadata: Optional metadata to store with the vector
        """
        if metadata is None:
            metadata = {}
            
        embedding = self.get_embedding(text)
        vector = Vector(
            id=id,
            values=embedding,
            metadata={"text": text, **metadata}
        )
        self.pinecone.upsert(namespace=namespace, vectors=[vector])
    
    def search(
        self,
        namespace: str,
        query_text: str,
        top_k: int = 5,
        **kwargs
    ) -> List[SearchResult]:
        """Search for similar vectors in the specified namespace.
        
        Args:
            namespace: Namespace to search in
            query_text: Query text to search for
            top_k: Number of results to return
            **kwargs: Additional search parameters
            
        Returns:
            List of SearchResult objects
        """
        query_embedding = self.get_embedding(query_text)
        results = self.pinecone.query(
            namespace=namespace,
            vector=query_embedding,
            top_k=top_k,
            **kwargs
        )
        
        return [
            SearchResult(
                id=result["id"],
                score=result["score"],
                metadata=result["metadata"]
            )
            for result in results
        ]
