"""
Pinecone Core Stub - Vector Database Operations

PURPOSE:
    Stub implementations for Pinecone index operations.
    Provides in-memory vector storage for testing.

STATUS: Active - Used when Pinecone is unavailable
"""


class Index:
    """
    Sovereign Stub for Pinecone Indexing.
    
    Provides in-memory vector storage that mimics Pinecone API.
    Used for testing vector operations without network calls.
    """
    def __init__(self, name: str):
        self.name = name
        self.store = {}

    def upsert(self, vectors: list, **kwargs):
        for v in vectors: self.store[v['id']] = v
        return {"upserted_count": len(vectors)}

    def query(self, vector: list, top_k: int = 1, **kwargs):
        # Return a deterministic stub match
        return {"matches": [{"id": "stub_1", "score": 0.99, "metadata": {}}]}

def init(api_key: str = None, **kwargs): pass
class GRPCIndex(Index): pass
