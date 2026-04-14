from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import sqlite3
from typing import Any, Iterable


@dataclass
class HybridSearchResult:
    chunk_id: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    combined_score: float = 0.0
    source: str = "hybrid"
    vector_score: float = 0.0
    lexical_score: float = 0.0


class HybridSearchEngine:
    """Minimal, deterministic hybrid-search shim with defensive guards.

    The implementation stays intentionally lightweight for offline regression tests,
    while still hardening the runtime path around malformed inputs, sqlite issues,
    and inconsistent Chroma-style payloads.
    """

    def __init__(self, chroma_client: Any | None = None, adg_db_path: str | None = None, top_k: int = 10):
        self.chroma_client = chroma_client
        self.adg_db_path = adg_db_path
        self.top_k = max(1, int(top_k))
        self._bge_model: Any | None = None
        self._adg_conn: sqlite3.Connection | None = None

    def __enter__(self) -> "HybridSearchEngine":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close_adg_connection()

    def __del__(self) -> None:
        try:
            self.close_adg_connection()
        except Exception:
            pass

    @staticmethod
    def _normalize_query(query: Any) -> str:
        if query is None:
            return ""
        return str(query).strip()

    @staticmethod
    def _ensure_mapping(value: Any) -> dict[str, Any]:
        return dict(value) if isinstance(value, dict) else {}

    def _ensure_adg_connection(self) -> sqlite3.Connection | None:
        if self._adg_conn is None and self.adg_db_path and Path(self.adg_db_path).exists():
            self._adg_conn = sqlite3.connect(self.adg_db_path)
            self._adg_conn.row_factory = sqlite3.Row
        return self._adg_conn

    def close_adg_connection(self) -> None:
        if self._adg_conn is not None:
            self._adg_conn.close()
            self._adg_conn = None

    def _fetch_rows(self, sql: str, params: tuple[Any, ...]) -> list[dict[str, Any]]:
        conn = self._ensure_adg_connection()
        if conn is None:
            return []
        try:
            cur = conn.execute(sql, params)
            return [dict(row) for row in cur.fetchall()]
        except sqlite3.Error:
            return []

    def get_node_by_id(self, node_id: int) -> dict[str, Any] | None:
        rows = self._fetch_rows("SELECT * FROM nodes WHERE id = ?", (node_id,))
        return rows[0] if rows else None

    def get_callers(self, node_id: int) -> list[dict[str, Any]]:
        return self._fetch_rows(
            "SELECT n.* FROM edges e JOIN nodes n ON n.id = e.src_id WHERE e.dst_id = ? AND e.relation_type = ?",
            (node_id, "calls"),
        )

    def get_callees(self, node_id: int) -> list[dict[str, Any]]:
        return self._fetch_rows(
            "SELECT n.* FROM edges e JOIN nodes n ON n.id = e.dst_id WHERE e.src_id = ? AND e.relation_type = ?",
            (node_id, "calls"),
        )

    def get_importers(self, node_id: int) -> list[dict[str, Any]]:
        return self._fetch_rows(
            "SELECT n.* FROM edges e JOIN nodes n ON n.id = e.src_id WHERE e.dst_id = ? AND e.relation_type = ?",
            (node_id, "imports"),
        )

    def get_imports(self, node_id: int) -> list[dict[str, Any]]:
        return self._fetch_rows(
            "SELECT n.* FROM edges e JOIN nodes n ON n.id = e.dst_id WHERE e.src_id = ? AND e.relation_type = ?",
            (node_id, "imports"),
        )

    def get_violations(self, node_id: int) -> list[dict[str, Any]]:
        conn = self._ensure_adg_connection()
        if conn is None:
            return []
        try:
            cur = conn.execute("SELECT * FROM violations WHERE node_id = ?", (node_id,))
            return [dict(row) for row in cur.fetchall()]
        except sqlite3.Error:
            return []

    def _apply_governance_filters(
        self,
        results: list[HybridSearchResult],
        governance_filter: dict[str, Any],
    ) -> list[HybridSearchResult]:
        if not governance_filter:
            return list(results)
        filtered = list(results)
        layers = governance_filter.get("layers")
        if layers:
            allowed_layers = set(layers)
            filtered = [result for result in filtered if result.metadata.get("layer") in allowed_layers]
        entity_types = governance_filter.get("entity_types")
        if entity_types:
            allowed_types = set(entity_types)
            filtered = [result for result in filtered if result.metadata.get("entity_type") in allowed_types]
        return filtered

    def enforce_context_budget(
        self,
        results: list[HybridSearchResult],
        max_tokens: int,
        avg_tokens_per_chunk: int = 100,
    ) -> list[HybridSearchResult]:
        if avg_tokens_per_chunk <= 0:
            raise ValueError("avg_tokens_per_chunk must be positive")
        if max_tokens <= 0:
            return []
        allowed = max_tokens // avg_tokens_per_chunk
        if allowed >= len(results):
            return list(results)
        return sorted(results, key=lambda result: result.combined_score, reverse=True)[:allowed]

    def expand_results_with_adg(
        self,
        results: list[HybridSearchResult],
        relation_types: list[str] | None = None,
        limit_per_relation: int = 3,
    ) -> list[HybridSearchResult]:
        return list(results)

    def expand_results_with_parent_child(
        self,
        results: list[HybridSearchResult],
        max_depth: int = 1,
    ) -> list[HybridSearchResult]:
        return list(results)

    def _generate_query_embedding(self, query: str) -> list[float] | None:
        if self._bge_model is None:
            try:
                from sentence_transformers import SentenceTransformer  # type: ignore
            except ImportError:
                return None
            self._bge_model = SentenceTransformer("BAAI/bge-m3")
        encoded = self._bge_model.encode(query)
        if hasattr(encoded, "tolist"):
            encoded = encoded.tolist()
        if encoded and isinstance(encoded[0], list):
            encoded = encoded[0]
        return [float(value) for value in encoded]

    @staticmethod
    def _coerce_query_payload(raw: Any, key: str) -> list[Any]:
        value = raw.get(key) if isinstance(raw, dict) else None
        if value is None:
            return []
        if value and isinstance(value[0], list):
            return list(value[0])
        if isinstance(value, list):
            return list(value)
        return []

    def _collection_query(
        self,
        collection: Any,
        query: str,
        query_embedding: list[float] | None,
    ) -> dict[str, Any]:
        try:
            return collection.query(
                query_embeddings=[query_embedding] if query_embedding is not None else None,
                query_texts=[query],
                n_results=self.top_k,
                include=["documents", "metadatas", "distances"],
            )
        except TypeError:
            return collection.query(query_texts=[query], n_results=self.top_k)

    def _vector_search(
        self,
        query: str,
        query_embedding: list[float] | None,
        collection_name: str,
        governance_filter: dict[str, Any] | None,
    ) -> list[HybridSearchResult] | dict:
        if self.chroma_client is None:
            return {}
        normalized_query = self._normalize_query(query)
        if query_embedding is None:
            query_embedding = self._generate_query_embedding(normalized_query)
        try:
            collection = self.chroma_client.get_collection(collection_name)
        except Exception:
            return []
        raw = self._collection_query(collection, normalized_query, query_embedding)
        ids = self._coerce_query_payload(raw, "ids")
        docs = self._coerce_query_payload(raw, "documents")
        metas = self._coerce_query_payload(raw, "metadatas")
        distances = self._coerce_query_payload(raw, "distances")

        results: list[HybridSearchResult] = []
        for idx, chunk_id in enumerate(ids):
            distance = float(distances[idx]) if idx < len(distances) else 1.0
            score = max(1e-9, 1.0 - distance)
            content = str(docs[idx]) if idx < len(docs) else ""
            metadata = self._ensure_mapping(metas[idx] if idx < len(metas) else {})
            results.append(
                HybridSearchResult(
                    chunk_id=str(chunk_id),
                    content=content,
                    metadata=metadata,
                    combined_score=score,
                    source="vector",
                    vector_score=score,
                    lexical_score=0.0,
                )
            )
        return self._apply_governance_filters(results, governance_filter or {})

    @staticmethod
    def _deduplicate_results(results: Iterable[HybridSearchResult]) -> list[HybridSearchResult]:
        by_id: dict[str, HybridSearchResult] = {}
        for result in results:
            current = by_id.get(result.chunk_id)
            if current is None or result.combined_score > current.combined_score:
                by_id[result.chunk_id] = result
        return list(by_id.values())

    def search(
        self,
        query: str,
        query_embedding: list[float] | None = None,
        collection_name: str = "code_chunks",
        governance_filter: dict[str, Any] | None = None,
    ) -> list[HybridSearchResult]:
        vector_results = self._vector_search(query, query_embedding, collection_name, governance_filter)
        if isinstance(vector_results, dict):
            return []
        deduped = self._deduplicate_results(vector_results)
        return sorted(
            deduped,
            key=lambda result: (result.combined_score, result.vector_score, result.lexical_score),
            reverse=True,
        )


_global_hybrid_engine: HybridSearchEngine | None = None


def get_global_hybrid_engine() -> HybridSearchEngine:
    global _global_hybrid_engine
    if _global_hybrid_engine is None:
        try:
            import chromadb

            client = chromadb.PersistentClient()
        except Exception:
            client = None
        _global_hybrid_engine = HybridSearchEngine(chroma_client=client)
    return _global_hybrid_engine


def hybrid_search(
    query: str,
    query_embedding: list[float] | None = None,
    collection_name: str = "code_chunks",
) -> list[HybridSearchResult]:
    return get_global_hybrid_engine().search(query, query_embedding, collection_name)
