class Index:
    """Sovereign Stub for Pinecone Indexing."""
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
