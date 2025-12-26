"""
Pinecone Vector Store Implementation – Sovereign Primary (Serverless)
SSOT-aligned integration for semantic memory territory mapping and RAG context.
"""
import os
import time
from typing import List, Optional, Dict, Any
from pinecone import Pinecone, ServerlessSpec
from pinecone.exceptions import PineconeApiException

class SovereignPineconeStore:
    """
    Sovereign wrapper for Pinecone serverless index.
    Handles index creation (idempotent), upsert, query, and namespace management.
    """
    DEFAULT_INDEX_NAME = "sovereign-territory-index"
    DEFAULT_DIMENSION = 1536  # Standard for text-embedding-3-large
    DEFAULT_METRIC = "cosine"
    DEFAULT_CLOUD = "aws"
    DEFAULT_REGION = "us-east-1"

    def __init__(
        self,
        api_key: Optional[str] = None,
        index_name: str = DEFAULT_INDEX_NAME,
        dimension: int = DEFAULT_DIMENSION,
        metric: str = DEFAULT_METRIC,
        cloud: str = DEFAULT_CLOUD,
        region: str = DEFAULT_REGION,
    ):
        self.api_key = api_key or os.getenv("PINECONE_API_KEY")
        if not self.api_key:
            raise ValueError("PINECONE_API_KEY environment variable or api_key argument required")

        self.pc = Pinecone(api_key=self.api_key)
        self.index_name = index_name
        self.dimension = dimension
        self.metric = metric

        self._ensure_index(cloud=cloud, region=region)
        self.index = self.pc.Index(self.index_name)

    def _ensure_index(self, cloud: str, region: str) -> None:
        """Idempotent index creation – serverless only."""
        if not self.pc.has_index(self.index_name):
            try:
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric=self.metric,
                    spec=ServerlessSpec(cloud=cloud, region=region),
                    deletion_protection="disabled",  # Set to 'enabled' in production
                )
                # Brief sleep to ensure eventual consistency propagation
                time.sleep(1)
            except PineconeApiException as e:
                if "ALREADY_EXISTS" in str(e):
                    pass
                else:
                    raise e
        
        # Validation
        try:
            desc = self.pc.describe_index(self.index_name)
            if desc.dimension != self.dimension:
                raise ValueError(
                    f"Existing index dimension {desc.dimension} != requested {self.dimension}. "
                    "Manual intervention required to prevent data corruption."
                )
        except Exception as e:
             # Handle edge cases where description might fail temporarily
             print(f"[Warn] Could not validate index dimensions: {e}")

    def upsert(
        self,
        vectors: List[Dict[str, Any]],
        namespace: Optional[str] = None,
        batch_size: int = 100
    ) -> Any:
        """
        Batch upsert to handle limitations of gRPC message sizes.
        """
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i : i + batch_size]
            self.index.upsert(vectors=batch, namespace=namespace)

    def query(
        self,
        vector: List[float],
        top_k: int = 10,
        namespace: Optional[str] = None,
        filter: Optional[Dict] = None,
        include_metadata: bool = True,
    ) -> Any:
        return self.index.query(
            vector=vector,
            top_k=top_k,
            namespace=namespace,
            filter=filter,
            include_metadata=include_metadata,
        )

    def delete_namespace(self, namespace: str) -> None:
        self.index.delete(delete_all=True, namespace=namespace)
