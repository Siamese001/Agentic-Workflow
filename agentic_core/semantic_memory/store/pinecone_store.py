from __future__ import annotations

from pinecone import Pinecone, ServerlessSpec

"""Brief description of functionality and purpose."""

"Brief description of functionality and purpose."
import os
import time
from typing import Any


class PineconeVectorStore:
    """
    Sovereign wrapper for Pinecone vector database.
    """

    def __init__(self, index_name: str = "sovereign-rag"):
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise ValueError("PINECONE_API_KEY not set")
        self.pc = Pinecone(api_key=api_key)
        self.index_name = index_name
        # HARDENING: Do not assume 768. Default to 384 (legacy) but allow override.
        # Warning: Changing this on an existing DB will break retrieval.
        self.dimension = int(os.getenv("EMBEDDING_DIMENSION", "384"))

        if index_name not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=index_name,
                dimension=self.dimension,  # Safe creation
                metric="cosine",  # Corrected casing for SDK compatibility
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )
        else:
            # HARDENING: Runtime dimension check
            existing_index = self.pc.describe_index(index_name)
            actual_dim = getattr(existing_index, "dimension", self.dimension)
            if actual_dim != self.dimension:
                print(
                    f"[CRITICAL] DIMENSION MISMATCH: Configured {self.dimension}, "
                    f"but Index '{index_name}' has {actual_dim}. "
                    f"Forcing fallback to {actual_dim} to prevent crash."
                )
                self.dimension = actual_dim

        self.index = self.pc.Index(index_name)

    def upsert(
        self, vectors: list[tuple[str, list[float], dict]], namespace: str = "sovereign-core"
    ) -> None:
        """
        Upsert vectors with defensive batching (max 100 per call) to prevent payload errors.
        """
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i : i + batch_size]
            try:
                self.index.upsert(vectors=batch, namespace=namespace)
            except Exception as e:
                print(f"[CRITICAL] Pinecone batch upsert failed at index {i}: {e}")
                raise

    def query(
        self, query_embedding: list[float], top_k: int = 15, namespace: str = "sovereign-core"
    ) -> list[dict]:
        """
        Query similar vectors with P95 latency telemetry.
        """
        start_time = time.perf_counter()
        try:
            results: Any = self.index.query(
                vector=query_embedding, top_k=top_k, include_metadata=True, namespace=namespace
            )
            latency_ms = (time.perf_counter() - start_time) * 1000

            if latency_ms > 500:
                print(f"[WARN] Retrieval Latency High: {latency_ms:.2f}ms")

            return [
                {"id": match["id"], "score": match["score"], "metadata": match["metadata"]}
                for match in results.get("matches", [])
            ]
        except Exception as e:
            print(f"[ERROR] Pinecone query failed: {e}")
            return []

    def delete_all(self) -> None:
        """Clear index — use with caution."""
        self.index.delete(delete_all=True)


def get_pinecone_store() -> PineconeVectorStore:
    """Brief description of functionality and purpose."""
    return PineconeVectorStore()
