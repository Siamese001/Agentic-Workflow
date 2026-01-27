# Local Ephemeral Vector Store (For Testing/Dev)
# Strategy: Naive Cosine Similarity in Python (slow but correct for unit tests)

import math
from typing import List
from agentic_core.semantic_memory.interfaces import BaseVectorStore
from agentic_core.semantic_memory.models import MemoryItem, MemoryQuery

class InMemoryVectorStore(BaseVectorStore):
    def __init__(self):
        self._storage: dict[str, MemoryItem] = {}

    async def initialize(self) -> None:
        self._storage.clear()

    async def upsert(self, items: List[MemoryItem]) -> bool:
        for item in items:
            self._storage[str(item.id)] = item
        return True

    async def delete(self, item_ids: List[str]) -> bool:
        for uid in item_ids:
            self._storage.pop(uid, None)
        return True

    async def query(self, query: MemoryQuery) -> List[MemoryItem]:
        """
        Naive implementation of cosine similarity search.
        O(N) complexity - do not use in production.
        """
        results = []
        q_vec = query.vector
        q_mag = math.sqrt(sum(x*x for x in q_vec))

        for item in self._storage.values():
            # 1. Metadata Filter check
            if query.filter_metadata:
                match = True
                for k, v in query.filter_metadata.items():
                    if item.metadata.get(k) != v:
                        match = False
                        break
                if not match:
                    continue

            # 2. Cosine Similarity Calculation
            d_vec = item.embedding
            dot_product = sum(a*b for a, b in zip(q_vec, d_vec))
            d_mag = math.sqrt(sum(x*x for x in d_vec))
            
            if d_mag * q_mag == 0:
                similarity = 0.0
            else:
                similarity = dot_product / (d_mag * q_mag)
            
            # Create copy with score
            item_copy = item.model_copy()
            item_copy.score = similarity
            results.append(item_copy)

        # Sort desc by score and slice top_k
        results.sort(key=lambda x: x.score or 0.0, reverse=True)
        return results[:query.top_k]
