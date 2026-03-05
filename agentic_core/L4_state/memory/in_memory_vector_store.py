# Local Ephemeral Vector Store (For Testing/Dev)
# Strategy: FAISS IndexFlatIP with L2-normalised vectors (cosine similarity) — primary path.
#           Pure-Python cosine is the fallback when faiss is not installed.
# Zero-Ambiguity Standard: Renamed from InMemoryVectorStore.py to InMemoryVectorStoreAdapter.py
# Category: ADAPTER (Adapts in-memory dict to VectorStore interface)

from __future__ import annotations

import importlib.util
import math

from agentic_core.semantic_memory.interfaces import BaseVectorStore
from agentic_core.semantic_memory.models import MemoryItem, MemoryQuery


def _faiss_available() -> bool:
    return importlib.util.find_spec("faiss") is not None


class InMemoryVectorStore(BaseVectorStore):
    def __init__(self):
        self._storage: dict[str, MemoryItem] = {}
        self._ordered_ids: list[str] = []
        self._faiss_index = None
        self._faiss_dim: int | None = None

    def _reset_faiss(self) -> None:
        self._faiss_index = None
        self._faiss_dim = None

    def _rebuild_faiss(self) -> None:
        if not _faiss_available() or not self._storage:
            self._faiss_index = None
            return
        import faiss
        import numpy as np

        items = [self._storage[uid] for uid in self._ordered_ids if uid in self._storage]
        if not items:
            self._faiss_index = None
            return
        dim = len(items[0].embedding)
        self._faiss_dim = dim
        arr = np.array([item.embedding for item in items], dtype=np.float32)
        faiss.normalize_L2(arr)
        index = faiss.IndexFlatIP(dim)
        index.add(arr)
        self._faiss_index = index

    async def initialize(self) -> None:
        self._storage.clear()
        self._ordered_ids.clear()
        self._reset_faiss()

    async def upsert(self, items: list[MemoryItem]) -> bool:
        for item in items:
            uid = str(item.id)
            if uid not in self._storage:
                self._ordered_ids.append(uid)
            self._storage[uid] = item
        self._rebuild_faiss()
        return True

    async def delete(self, item_ids: list[str]) -> bool:
        for uid in item_ids:
            self._storage.pop(uid, None)
        self._ordered_ids = [uid for uid in self._ordered_ids if uid in self._storage]
        self._rebuild_faiss()
        return True

    async def query(self, query: MemoryQuery) -> list[MemoryItem]:
        """
        Cosine similarity search.
        Primary path : FAISS IndexFlatIP with L2-normalised vectors.
        Fallback path: pure-Python cosine when faiss is not installed.
        """
        q_vec = query.vector

        candidate_ids: list[str] = list(self._ordered_ids)

        if _faiss_available() and self._faiss_index is not None:
            import faiss
            import numpy as np

            q_arr = np.array([q_vec], dtype=np.float32)
            faiss.normalize_L2(q_arr)
            k = min(query.top_k * 4 if query.filter_metadata else query.top_k, self._faiss_index.ntotal)
            if k == 0:
                return []
            scores_arr, indices_arr = self._faiss_index.search(q_arr, k)
            active_ids = [uid for uid in self._ordered_ids if uid in self._storage]
            results: list[MemoryItem] = []
            for score, idx in zip(scores_arr[0], indices_arr[0]):
                if idx < 0 or idx >= len(active_ids):
                    continue
                uid = active_ids[idx]
                item = self._storage.get(uid)
                if item is None:
                    continue
                if query.filter_metadata:
                    match = all(item.metadata.get(k) == v for k, v in query.filter_metadata.items())
                    if not match:
                        continue
                item_copy = item.model_copy()
                item_copy.score = float(score)
                results.append(item_copy)
            results.sort(key=lambda x: x.score or 0.0, reverse=True)
            return results[: query.top_k]

        # --- Pure-Python cosine fallback ---
        q_mag = math.sqrt(sum(x * x for x in q_vec))
        results = []
        for uid in candidate_ids:
            item = self._storage.get(uid)
            if item is None:
                continue
            if query.filter_metadata:
                match = all(item.metadata.get(k) == v for k, v in query.filter_metadata.items())
                if not match:
                    continue
            d_vec = item.embedding
            dot_product = sum(a * b for a, b in zip(q_vec, d_vec, strict=False))
            d_mag = math.sqrt(sum(x * x for x in d_vec))
            similarity = dot_product / (d_mag * q_mag) if d_mag * q_mag != 0 else 0.0
            item_copy = item.model_copy()
            item_copy.score = similarity
            results.append(item_copy)

        results.sort(key=lambda x: x.score or 0.0, reverse=True)
        return results[: query.top_k]
