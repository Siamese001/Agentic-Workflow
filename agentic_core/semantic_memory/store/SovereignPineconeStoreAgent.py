from __future__ import annotations
"""
Pinecone Vector Store Implementation – Sovereign Primary (Serverless)
SSOT-aligned integration using SovereignConfig.
"""
import time
from typing import List, Optional, Dict, Any
from pinecone import Pinecone, ServerlessSpec, PineconeApiException
from agentic_core.config.blueprint_sovereign.sovereign_config import config

# NAMING FIXED: SovereignPineconeStoreAgent → SovereignPineconeStoreAgent
class SovereignPineconeStoreAgent(HealerMixin, MCPHardenedMixin):
    """Sovereign wrapper for Pinecone serverless index."""
    
    DEFAULT_INDEX_NAME = "sovereign-territory-index"

    def __init__(
        self,
        index_name: str = DEFAULT_INDEX_NAME,
        dimension: int = config.DEFAULT_EMBEDDING_DIM,
        Metric: str = "cosine",
    ):
        # Validate config immediately
        config.validate()
        
        self.api_key = config.PINECONE_API_KEY
        self.pc = Pinecone(api_key=self.api_key)
        self.index_name = index_name
        self.dimension = dimension
        self.Metric = Metric

        self._ensure_index()
        self.index = self.pc.Index(self.index_name)

    def _ensure_index(self) -> None:
        """Idempotent index creation using Config SSOT values."""
        if not self.pc.has_index(self.index_name):
            try:
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    Metric=self.Metric,
                    spec=ServerlessSpec(cloud=config.PINECONE_CLOUD, region=config.PINECONE_ENV),
                    deletion_protection="disabled",
                )
                time.sleep(1)
            except PineconeApiException as e:
                if "ALREADY_EXISTS" not in str(e):
                    raise e

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

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
