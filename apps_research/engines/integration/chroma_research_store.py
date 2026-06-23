"""apps_research Chroma-backed research store — W6 real-embeddings upgrade.

W5N (no-core track) invariants enforced here:
  - App-owned integration layer only; does not edit agentic_core.
  - Does not write durable L4 state directly.
  - Does not call UWG.
  - Does not answer, route, or assemble prompts.
  - Does not execute graph traversal or call the traversal engine.
  - Does not claim live C0 integration.
  - Live runtime wiring is deferred (CONFIG_PREPARED_ONLY).
  - Uses embedding model BAAI/bge-m3 / 1024 dims.
  - Collection name: process_docs
  - Lazy factory pattern: SovereignChromaClient constructed only when a real
    chromadb_path is supplied; tests may inject a fake client via Protocol.

W6 upgrade:
  - _embed() now calls SentenceTransformer(BGE_M3_MODEL_ID) for real 1024-dim vectors.
  - Zero-vector stub removed from the ChromaResearchStore path.
  - If sentence-transformers is missing, raises ImportError with install hint.
  - Model is lazy-loaded (class-level cache) to keep import-time side-effects low.
  - InMemoryResearchStore (chromadb_path=None) is unchanged — test/dev path.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Protocol, runtime_checkable

from agentic_core.config.model_catalog import BGE_M3_MODEL_ID
from apps_research.engines.research_retrieval_engine import RetrievedResearch

_log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# W5N policy constants
# ---------------------------------------------------------------------------

COLLECTION_NAME: str = "process_docs"
EMBEDDING_MODEL: str = BGE_M3_MODEL_ID
EMBEDDING_DIMENSIONS: int = 1024

live_wiring_deferred: bool = True
_WIRING_GATE: str = "APPS_RESEARCH_CHROMA_RUNTIME_WIRING_REQUIRED"


def _resolve_embedding_device() -> str:
    """Resolve the BGE device for the real Chroma path only."""
    override = os.environ.get("APPS_RESEARCH_EMBEDDING_DEVICE", "").strip().lower()
    if override in {"cpu", "cuda", "mps"}:
        return override
    from agentic_core.embeddings.bge_runtime import _resolve_device

    return _resolve_device()


# ---------------------------------------------------------------------------
# Minimal ChromaDB client protocol (allows test injection without real Chroma)
# ---------------------------------------------------------------------------


@runtime_checkable
class ChromaCollectionProtocol(Protocol):
    """Minimal subset of chromadb.Collection used by ChromaResearchStore."""

    def add(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict[str, Any]],
    ) -> None: ...

    def query(
        self,
        query_embeddings: list[list[float]],
        n_results: int,
        where: dict[str, Any] | None = None,
    ) -> dict[str, Any]: ...

    def get(
        self,
        where: dict[str, Any] | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]: ...


@runtime_checkable
class ChromaClientProtocol(Protocol):
    """Minimal subset of chromadb.Client used by ChromaResearchStore."""

    def get_or_create_collection(
        self,
        name: str,
        metadata: dict[str, Any] | None = None,
    ) -> ChromaCollectionProtocol: ...


# ---------------------------------------------------------------------------
# ChromaResearchStore
# ---------------------------------------------------------------------------


class ChromaResearchStore:
    """Chroma-backed research store for apps_research (W5N — CONFIG_PREPARED_ONLY).

    W5N discipline:
      - Does not write durable L4 state directly.
      - Does not call UWG.
      - Does not answer, route, or assemble prompts.
      - Does not execute graph traversal.
      - Live C0 runtime wiring deferred (live_wiring_deferred=True).

    Usage::

        # Production: supply a real chromadb_path
        store = ChromaResearchStore(chromadb_path="/path/to/chroma")

        # Tests: inject a fake client conforming to ChromaClientProtocol
        store = ChromaResearchStore(client=FakeChromaClient())
    """

    live_wiring_deferred: bool = True
    collection_name: str = COLLECTION_NAME
    embedding_model: str = EMBEDDING_MODEL
    embedding_dimensions: int = EMBEDDING_DIMENSIONS

    def __init__(
        self,
        chromadb_path: str | None = None,
        client: ChromaClientProtocol | None = None,
    ) -> None:
        """Initialise the store.

        Args:
            chromadb_path: On-disk path for a persistent Chroma client.
                If None and no client is provided, operations raise RuntimeError
                (not silently degrading to mock embeddings in production path).
            client: Pre-built client conforming to ChromaClientProtocol.
                Takes precedence over chromadb_path. Used for test injection.
        """
        self._chromadb_path = chromadb_path
        self._client: ChromaClientProtocol | None = client
        self._collection: ChromaCollectionProtocol | None = None

    # ------------------------------------------------------------------
    # Lazy client / collection initialisation
    # ------------------------------------------------------------------

    def _get_collection(self) -> ChromaCollectionProtocol:
        if self._collection is not None:
            return self._collection

        if self._client is None:
            if self._chromadb_path is None:
                raise RuntimeError(
                    "ChromaResearchStore: chromadb_path or client required — "
                    "no mock embeddings in production Chroma path (W5N invariant)"
                )
            self._client = self._build_client(self._chromadb_path)

        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        return self._collection

    @staticmethod
    def _build_client(chromadb_path: str) -> ChromaClientProtocol:
        """Lazily import and construct a real Chroma PersistentClient.

        Import is deferred so that importing this module never triggers
        chromadb side effects in test environments.
        """
        try:
            import chromadb  # type: ignore[import]
        except ImportError as exc:
            raise RuntimeError(
                "ChromaResearchStore requires chromadb package — "
                "install with: pip install chromadb"
            ) from exc
        return chromadb.PersistentClient(path=chromadb_path)  # type: ignore[return-value]

    # ------------------------------------------------------------------
    # Embedding helper — BAAI/bge-m3 via sentence-transformers (W6)
    # ------------------------------------------------------------------

    _model: Any = None  # class-level lazy cache; shared across instances

    @classmethod
    def _get_model(cls) -> Any:
        """Lazy-load SentenceTransformer(BGE_M3_MODEL_ID).

        Raises ImportError with install hint if sentence-transformers is missing.
        """
        if cls._model is None:
            try:
                from sentence_transformers import SentenceTransformer  # type: ignore[import]
            except ImportError as exc:
                raise ImportError(
                    "ChromaResearchStore requires sentence-transformers for real embeddings. "
                    "Install with: pip install sentence-transformers>=2.2.0"
                ) from exc
            device = _resolve_embedding_device()
            _log.info(
                "[ChromaResearchStore] loading embedding_model=%s device=%s",
                EMBEDDING_MODEL,
                device,
            )
            cls._model = SentenceTransformer(EMBEDDING_MODEL, device=device)
        return cls._model

    def _embed(self, text: str) -> list[float]:
        """Produce a real BAAI/bge-m3 embedding vector for the given text.

        Returns a 1024-dimensional float list.
        Raises ImportError if sentence-transformers is not installed.
        Does NOT fall back to zero vectors — zero-vector fallback is removed
        from the ChromaResearchStore path (W6 invariant).
        """
        model = self._get_model()
        vector = model.encode(text, normalize_embeddings=True)
        return vector.tolist()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def add_research(
        self,
        research_id: str,
        research_data: dict[str, Any],
        metadata: dict[str, Any],
    ) -> bool:
        """Store a research artifact in the Chroma collection.

        Args:
            research_id: Unique identifier for this research artifact.
            research_data: Research content dict (must be JSON-serialisable).
            metadata: Flat dict of metadata fields (Chroma constraint: scalar values).

        Returns:
            True on success.
        """
        import json

        collection = self._get_collection()
        doc_text = json.dumps(research_data, sort_keys=True, default=str)
        embedding = self._embed(doc_text)

        safe_meta = {k: str(v) if not isinstance(v, (str, int, float, bool)) else v
                     for k, v in metadata.items()}

        collection.add(
            ids=[research_id],
            embeddings=[embedding],
            documents=[doc_text],
            metadatas=[safe_meta],
        )
        _log.debug("[ChromaResearchStore] added research_id=%s collection=%s", research_id, COLLECTION_NAME)
        return True

    def query_similar(
        self,
        query: dict[str, Any],
        n_results: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[RetrievedResearch]:
        """Query for similar research artifacts.

        Args:
            query: Query dict (encoded into embedding for similarity search).
            n_results: Maximum number of results to return.
            filters: Optional Chroma ``where`` filter dict.

        Returns:
            List of RetrievedResearch ordered by similarity descending.
        """
        import json

        collection = self._get_collection()
        query_text = json.dumps(query, sort_keys=True, default=str)
        query_emb = self._embed(query_text)

        raw = collection.query(
            query_embeddings=[query_emb],
            n_results=n_results,
            where=filters,
        )

        ids: list[str] = raw.get("ids", [[]])[0]
        distances: list[float] = raw.get("distances", [[]])[0]
        metadatas: list[dict[str, Any]] = raw.get("metadatas", [[]])[0]
        documents: list[str] = raw.get("documents", [[]])[0]

        results: list[RetrievedResearch] = []
        for res_id, dist, meta, doc in zip(ids, distances, metadatas, documents):
            try:
                data = json.loads(doc)
            except Exception:
                data = {}
            results.append(
                RetrievedResearch(
                    research_id=res_id,
                    topic=meta.get("topic", "unknown"),
                    artifact_mode=meta.get("artifact_mode", "brief"),
                    timestamp=meta.get("timestamp", ""),
                    content_preview=data.get("content", "")[:500],
                    quality_score=float(data.get("quality_score", 0.0)),
                    source_count=int(data.get("source_count", 0)),
                    claim_types=data.get("claim_types", {}),
                    metadata=meta,
                    similarity_score=max(0.0, 1.0 - float(dist)),
                )
            )
        return results

    def get_by_mode(self, mode: str, limit: int = 10) -> list[RetrievedResearch]:
        """Get research artifacts by artifact_mode.

        Args:
            mode: Artifact mode string to filter by.
            limit: Maximum number of results.

        Returns:
            List of RetrievedResearch sorted by timestamp descending.
        """
        import json

        collection = self._get_collection()
        raw = collection.get(
            where={"artifact_mode": mode},
            limit=limit,
        )

        ids: list[str] = raw.get("ids", [])
        metadatas: list[dict[str, Any]] = raw.get("metadatas", [])
        documents: list[str] = raw.get("documents", [])

        results: list[RetrievedResearch] = []
        for res_id, meta, doc in zip(ids, metadatas, documents):
            try:
                data = json.loads(doc)
            except Exception:
                data = {}
            results.append(
                RetrievedResearch(
                    research_id=res_id,
                    topic=meta.get("topic", ""),
                    artifact_mode=mode,
                    timestamp=meta.get("timestamp", ""),
                    content_preview=data.get("content", "")[:500],
                    quality_score=float(data.get("quality_score", 0.0)),
                    source_count=int(data.get("source_count", 0)),
                    claim_types=data.get("claim_types", {}),
                    metadata=meta,
                    similarity_score=1.0,
                )
            )
        return sorted(results, key=lambda x: x.timestamp, reverse=True)
