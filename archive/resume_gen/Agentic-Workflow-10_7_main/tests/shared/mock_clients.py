from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from chromadb.utils import embedding_functions


class DeterministicEmbeddingFunction(embedding_functions.EmbeddingFunction):
    """Predictable embedding function leveraged by caching fixtures."""

    def __call__(self, prompts: List[str]) -> List[List[float]]:
        return [[float(len(prompt))] for prompt in prompts]


class DummyEmbeddingFunction:
    def __call__(self, prompts: List[str]) -> List[List[float]]:
        return [[float(len(p))] for p in prompts]


class FakeRedisClient:
    def __init__(self) -> None:
        self.store: Dict[str, Tuple[str, int]] = {}

    def setex(self, name: str, ttl: int, value: str) -> None:
        self.store[name] = (value, ttl)

    def get(self, name: str) -> str | None:
        return (self.store.get(name) or (None, 0))[0]

    def delete(self, name: str) -> None:
        self.store.pop(name, None)

    def ping(self) -> bool:
        return True


class InMemoryRedis:
    def __init__(self) -> None:
        self.store: Dict[str, str] = {}

    def setex(self, name: str, ttl: int, value: str) -> None:
        self.store[name] = value

    def get(self, name: str) -> str | None:
        return self.store.get(name)

    def ping(self) -> bool:
        return True


class FakeCollection:
    def __init__(self) -> None:
        self.records: Dict[str, Dict[str, Any]] = {}

    def add(
        self,
        *,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str],
        embeddings: Optional[List[List[float]]] = None,
        **_: Any,
    ) -> None:
        embeddings = embeddings or [[0.0] * 1 for _ in documents]
        for doc, metadata, record_id, embedding in zip(
            documents, metadatas, ids, embeddings
        ):
            self.records[record_id] = {
                "document": doc,
                "metadata": metadata,
                "embedding": embedding,
            }

    def query(
        self,
        *,
        query_texts: Optional[List[str]] = None,
        query_embeddings: Optional[List[List[float]]] = None,
        n_results: int,
        where: Dict[str, Any],
        **_: Any,
    ) -> Dict[str, Any]:
        matches: List[Dict[str, Any]] = []
        for record in self.records.values():
            metadata = record["metadata"]
            if all(metadata.get(k) == v for k, v in where.items()):
                matches.append(record)
        documents = [[rec["document"] for rec in matches[:n_results]]]
        metadatas = [[rec["metadata"] for rec in matches[:n_results]]]
        distances = [[0.0 for _ in range(len(documents[0]))]]
        return {"documents": documents, "metadatas": metadatas, "distances": distances}


class FakeChromaClient:
    def __init__(self, collection: FakeCollection) -> None:
        self.collection = collection

    def get_or_create_collection(self, name: str, embedding_function: Any) -> FakeCollection:
        return self.collection

    def get_collection(self, name: str, embedding_function: Any) -> FakeCollection:
        return self.collection


@dataclass
class TraceEvent:
    name: str
    payload: Dict[str, Any]


class TraceRecorder:
    """Simple in-memory telemetry recorder mimicking production logging."""

    def __init__(self) -> None:
        self._events: List[TraceEvent] = []

    def record(self, name: str, **payload: Any) -> None:
        self._events.append(TraceEvent(name=name, payload=payload))

    def find(self, name: str) -> List[TraceEvent]:
        return [event for event in self._events if event.name == name]

    def as_dicts(self) -> List[Dict[str, Any]]:
        return [dict(name=event.name, payload=event.payload) for event in self._events]


__all__ = [
    "DeterministicEmbeddingFunction",
    "DummyEmbeddingFunction",
    "FakeChromaClient",
    "FakeCollection",
    "FakeRedisClient",
    "InMemoryRedis",
    "TraceEvent",
    "TraceRecorder",
]
