"""Native Persistent Cache for L2 Semantic Cache Layer

Implements spec-compliant L2 Semantic Cache using SQLite (scalar) and ChromaDB (vector)
with BGE-M3 embeddings via ChromaDB's built-in embedding function and zero-token return protocols. No GPTCache dependency.
"""

from __future__ import annotations

import datetime
import hashlib
import json as _json
import logging
import sqlite3
import time
from pathlib import Path
from typing import Any

import chromadb
from tqdm import tqdm

Logger = logging.getLogger(__name__)


class NativePersistentCacheClient:
    """Native persistent semantic cache for L2 layer.

    Implements spec-compliant semantic caching with:
    - SQLite scalar store (query, response, metadata)
    - ChromaDB vector store (embeddings)
    - Cosine similarity > 0.95 threshold
    - LRU eviction (via last_access_at)
    - Zero-token return on cache hit
    """

    def __init__(
        self,
        cache_dir: str = "artifacts/gptcache",
        similarity_threshold: float = 0.95,
        max_entries: int = 10000,
        embedding_provider: str = "chromadb-default",
        embedding_model: str = "BAAI/bge-m3",
    ):
        """Initialize native persistent cache client.

        Args:
            cache_dir: Directory for cache storage
            similarity_threshold: Similarity threshold for cache hits (default 0.95)
            max_entries: Maximum cache entries (LRU eviction)
            embedding_provider: Provider for embeddings (chromadb-default)
            embedding_model: Model name for embeddings (ChromaDB default)
        """
        self.cache_dir = Path(cache_dir)
        self.similarity_threshold = similarity_threshold
        self.max_entries = max_entries
        self.embedding_provider = embedding_provider
        self.embedding_model = embedding_model

        self._hit_count = 0
        self._miss_count = 0
        self._token_savings = 0
        self._cache = None

        self._init_cache()

    def _init_cache(self) -> None:
        """Initialize SQLite scalar store and ChromaDB vector store with built-in embeddings."""
        try:
            # Create cache directory
            self.cache_dir.mkdir(parents=True, exist_ok=True)

            # Initialize SQLite scalar store (Phase B: schema-complete via _init_sqlite)
            sqlite_path = self.cache_dir / "l2_cache.db"
            self._init_sqlite(sqlite_path)

            # Initialize ChromaDB vector store (persistent) with BGE-M3 embedding function
            chroma_path = self.cache_dir / "chroma"
            self._chroma_client = chromadb.PersistentClient(path=str(chroma_path))
            self._chroma_collection = self._get_or_create_bgem3_collection()

            self._cache = "real"
            Logger.info(
                f"Native L2 cache initialized at {self.cache_dir} with SQLite + ChromaDB (built-in embeddings)"
            )

        except ImportError as e:
            Logger.warning(f"ChromaDB not installed: {e}, using mock implementation")
            self._cache = "mock"
        except (OSError, RuntimeError) as e:
            Logger.error(f"Failed to initialize native L2 cache: {e}, using mock")
            self._cache = "mock"

    def _get_or_create_bgem3_collection(self) -> Any:
        """Get or create l2_semantic_cache with BGE-M3 EF; drops collection if dim-incompatible."""
        col_name = "l2_semantic_cache"
        _expected_dim = 1024

        try:
            from chromadb.utils.embedding_functions import (
                SentenceTransformerEmbeddingFunction as _STEF,
            )

            _ef: Any = _STEF(model_name=self.embedding_model)
        except (ImportError, AttributeError, OSError, RuntimeError, ValueError) as exc:
            Logger.warning(
                "L2_CACHE: SentenceTransformerEmbeddingFunction unavailable (%s) — using ChromaDB default EF",
                exc,
            )
            _ef = None

        # Migration guard: drop any collection with incompatible stored dimension.
        # NotFoundError on first run is expected — collection is created below.
        try:
            _chroma_errors = __import__("chromadb.errors", fromlist=["NotFoundError"])
            _NotFoundError: type[BaseException] = getattr(_chroma_errors, "NotFoundError", RuntimeError)
        except ImportError:
            _NotFoundError = RuntimeError
        try:
            existing = self._chroma_client.get_collection(col_name)
            sample = existing.get(limit=1, include=["embeddings"])
            _raw_emb = sample.get("embeddings")
            embeddings = _raw_emb if _raw_emb is not None else []
            if len(embeddings) > 0 and len(embeddings[0]) != _expected_dim:
                Logger.warning(
                    "L2_CACHE_MIGRATION: dropping 'l2_semantic_cache' — stored dim=%d incompatible "
                    "with BGE-M3 dim=%d; existing cache data is invalidated",
                    len(embeddings[0]),
                    _expected_dim,
                )
                self._chroma_client.delete_collection(col_name)
        except _NotFoundError:  # guardian: allow-silent-swallow -- NotFoundError is the expected cache-miss sentinel on first run; collection is created by get_or_create_collection below
            pass  # First-run path: collection does not yet exist, created below.
        except (  # guardian: allow-silent-swallow -- cache cleanup: non-fatal, collection deletion failures ignored on shutdown
            AttributeError,
            KeyError,
            TypeError,
            ValueError,
            RuntimeError,
            OSError,
        ):
            pass  # Migration probe failed — fall through to get_or_create below

        kwargs: dict[str, Any] = {"name": col_name, "metadata": {"hnsw:space": "cosine"}}
        if _ef is not None:
            kwargs["embedding_function"] = _ef
        return self._chroma_client.get_or_create_collection(**kwargs)

    def _init_sqlite(self, sqlite_path: Path) -> None:
        """Initialize SQLite schema (Phase B: schema-complete) and apply safe migrations."""
        self._sqlite_conn = sqlite3.connect(str(sqlite_path), check_same_thread=False)
        self._sqlite_conn.execute(
            """
            CREATE TABLE IF NOT EXISTS l2_cache (
                id TEXT PRIMARY KEY,
                query TEXT NOT NULL,
                response TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_access_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                tenant_id TEXT NOT NULL DEFAULT '',
                embedding_model_id TEXT NOT NULL DEFAULT '',
                corpus_version TEXT NOT NULL DEFAULT '',
                evidence_ids TEXT DEFAULT '[]',
                grounding_complete INTEGER DEFAULT 0,
                policy_version TEXT DEFAULT '',
                ttl_seconds INTEGER DEFAULT 86400,
                expires_at DATETIME,
                entry_schema_version INTEGER DEFAULT 1
            )
            """,
        )
        self._sqlite_conn.commit()
        self._migrate_sqlite_schema()

    def _migrate_sqlite_schema(self) -> None:
        """Add Phase B columns to an existing l2_cache table if they are absent."""
        cursor = self._sqlite_conn.cursor()
        cursor.execute("PRAGMA table_info(l2_cache)")
        existing = {row[1] for row in cursor.fetchall()}
        migrations = [
            ("tenant_id", "TEXT DEFAULT ''"),
            ("embedding_model_id", "TEXT DEFAULT ''"),
            ("corpus_version", "TEXT DEFAULT ''"),
            ("evidence_ids", "TEXT DEFAULT '[]'"),
            ("grounding_complete", "INTEGER DEFAULT 0"),
            ("policy_version", "TEXT DEFAULT ''"),
            ("ttl_seconds", "INTEGER DEFAULT 86400"),
            ("expires_at", "DATETIME"),
            ("entry_schema_version", "INTEGER DEFAULT 1"),
        ]
        for col, defn in migrations:
            if col not in existing:
                self._sqlite_conn.execute(f"ALTER TABLE l2_cache ADD COLUMN {col} {defn}")
        self._sqlite_conn.commit()

    def _get_id(self, query: str) -> str:
        """Generate deterministic ID from query (SHA256)."""
        return hashlib.sha256(query.encode()).hexdigest()

    def _evict_if_needed(self) -> None:
        """Evict least-recently-accessed entries if over max_entries."""
        max_retries = 2
        for attempt in tqdm(range(max_retries), desc="Processing", unit="item"):
            try:
                cursor = self._sqlite_conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM l2_cache")
                count = cursor.fetchone()[0]

                if count > self.max_entries:
                    evict_count = count - self.max_entries
                    # Get least recently accessed entries
                    cursor.execute(
                        """
                        SELECT id FROM l2_cache
                        ORDER BY last_access_at ASC
                        LIMIT ?
                        """,
                        (evict_count,),
                    )
                    ids_to_evict = [row[0] for row in cursor.fetchall()]

                    # Delete from SQLite
                    placeholders = ",".join("?" * len(ids_to_evict))
                    cursor.execute(
                        f"DELETE FROM l2_cache WHERE id IN ({placeholders})",
                        ids_to_evict,
                    )
                    self._sqlite_conn.commit()

                    # Delete from ChromaDB
                    if ids_to_evict:
                        self._chroma_collection.delete(ids=ids_to_evict)

                    Logger.info(f"Evicted {evict_count} entries from L2 cache")
                    try:
                        from agentic_core.runtime.contracts.lifecycle_trace_contract import (  # noqa: PLC0415
                            _record_semantic_cache_prom_event as _prom_evict,
                        )

                        _prom_evict("eviction", "")
                    except ImportError:  # guardian: allow-silent-swallow -- prometheus optional: metric emission skipped, eviction continues
                        pass
                return  # Success, exit retry loop
            except (OSError, sqlite3.Error, RuntimeError) as e:
                if attempt == max_retries - 1:
                    Logger.error(f"Eviction failed after {max_retries} retries: {e}")
                else:
                    Logger.warning(f"Eviction attempt {attempt + 1} failed: {e}, retrying...")

    def get(
        self,
        query: str,
        *,
        tenant_id: str = "",
        embedding_model_id: str = "",
    ) -> str | None:
        """Get cached response for query.

        Args:
            query: User query string
            tenant_id: Reject entries whose tenant_id does not match (Phase B)
            embedding_model_id: Reject entries from a different embedding model (Phase B)

        Returns:
            Cached response if semantic match > 0.95 and contract fields match, else None
            Returns None on error but logs distinct error message
        """
        if self._cache == "mock":
            return self._mock_get(query)

        _t0 = time.monotonic()
        try:
            # Empty-collection guard — ChromaDB raises InternalError
            # ("Error creating hnsw segment reader: Nothing found on disk")
            # when .query() runs against a collection with zero entries.
            # Skip the query entirely in that case; miss is the correct result.
            try:
                _coll_count = self._chroma_collection.count()
            except (
                AttributeError,
                RuntimeError,
            ):  # guardian: allow-log-and-swallow -- count() unavailable treated as "unknown, try query"
                _coll_count = -1
            if _coll_count == 0:
                self._miss_count += 1
                Logger.debug("[L2Cache] l2_get_miss empty_collection query_prefix=%r", query[:40])
                return None
            # Search ChromaDB for similar entries (ChromaDB handles embeddings automatically)
            results = self._chroma_collection.query(
                query_texts=[query],
                n_results=1,
            )

            if results["ids"] and results["ids"][0]:
                top_id = results["ids"][0][0]
                distance = results["distances"][0][0] if results["distances"] else 1.0

                # Convert distance to similarity (cosine: 1 - distance)
                similarity = 1.0 - distance

                if similarity >= self.similarity_threshold:
                    # Fetch response and Phase B contract columns from SQLite
                    cursor = self._sqlite_conn.cursor()
                    cursor.execute(
                        "SELECT response, created_at, tenant_id, embedding_model_id, expires_at"
                        " FROM l2_cache WHERE id = ?",
                        (top_id,),
                    )
                    row = cursor.fetchone()

                    if row:
                        row_response, row_created_at, row_tenant, row_model, row_expires = (
                            row[0],
                            row[1],
                            row[2] or "",
                            row[3] or "",
                            row[4],
                        )
                        # Phase B: tenant isolation
                        if tenant_id and row_tenant != tenant_id:
                            self._miss_count += 1
                            Logger.debug(f"[L2Cache] l2_get_miss tenant_mismatch entry_id={top_id[:8]}")
                            return None
                        # Phase B: embedding model isolation
                        if embedding_model_id and row_model != embedding_model_id:
                            self._miss_count += 1
                            Logger.debug(f"[L2Cache] l2_get_miss model_mismatch entry_id={top_id[:8]}")
                            return None
                        # Phase C: hard TTL enforcement — evict and return None
                        if row_expires:
                            try:
                                exp = datetime.datetime.fromisoformat(row_expires)
                                if exp < datetime.datetime.utcnow():
                                    self._hard_evict_entry(cursor, top_id)
                                    self._miss_count += 1
                                    Logger.debug(f"[L2Cache] l2_hard_evict_expired entry_id={top_id[:8]}")
                                    return None
                            except (  # guardian: allow-silent-swallow -- TTL parse: malformed expires_at treated as no expiry, non-fatal
                                ValueError,
                                TypeError,
                            ):
                                pass  # malformed expires_at: treat as no expiry

                        # Update last_access_at
                        cursor.execute(
                            "UPDATE l2_cache SET last_access_at = CURRENT_TIMESTAMP WHERE id = ?",
                            (top_id,),
                        )
                        self._sqlite_conn.commit()

                        self._hit_count += 1
                        self._token_savings += len(query.split()) * 2
                        _elapsed_ms = (time.monotonic() - _t0) * 1000
                        Logger.debug(
                            f"[L2Cache] l2_get_hit entry_id={top_id[:8]} "
                            f"similarity={similarity:.4f} created_at={row_created_at} "
                            f"elapsed_ms={_elapsed_ms:.1f}"
                        )
                        return row_response

            self._miss_count += 1
            _elapsed_ms = (time.monotonic() - _t0) * 1000
            Logger.debug(f"[L2Cache] l2_get_miss elapsed_ms={_elapsed_ms:.1f} query_prefix={query[:40]!r}")
            return None

        except (
            OSError,
            sqlite3.Error,
            RuntimeError,
        ) as e:  # guardian: allow-return-none-swallow -- cache get: I/O failure returns None (treated as miss), non-fatal
            Logger.error(f"L2 cache get error (returning None): {e}")
            self._miss_count += 1  # Count as miss to avoid silent failure
            return None  # guardian: allow-return-none-swallow -- cache get: non-fatal, caller treats None as cache miss

    def set(
        self,
        query: str,
        response: str,
        *,
        tenant_id: str = "",
        embedding_model_id: str = "",
        corpus_version: str = "",
        evidence_ids: list[str] | None = None,
        grounding_complete: bool = False,
        policy_version: str = "",
        ttl_seconds: int = 86400,
        entry_schema_version: int = 1,
    ) -> None:
        """Cache response for query with full Phase B contract payload.

        Args:
            query: User query string
            response: Response to cache
            tenant_id: Tenant identifier for isolation
            embedding_model_id: Embedding model used to produce this entry
            corpus_version: 64-char hex hash of the corpus version
            evidence_ids: Source document IDs supporting this response
            grounding_complete: Whether response is fully grounded
            policy_version: Policy version active at write time
            ttl_seconds: Time-to-live in seconds (default 86400)
            entry_schema_version: Schema version for forward compatibility
        """
        if self._cache == "mock":
            self._mock_set(query, response)
            return

        try:
            query_id = self._get_id(query)
            evidence_ids_json = _json.dumps(evidence_ids or [])
            expires_at_str = (
                datetime.datetime.utcnow() + datetime.timedelta(seconds=ttl_seconds)
            ).isoformat()

            # Upsert to ChromaDB with Phase B contract metadata
            self._chroma_collection.upsert(
                ids=[query_id],
                documents=[query],
                metadatas=[
                    {
                        "tenant_id": tenant_id,
                        "embedding_model_id": embedding_model_id,
                        "corpus_version": corpus_version,
                        "entry_schema_version": str(entry_schema_version),
                        "expires_at": expires_at_str,
                        "created_at": "now",
                    }
                ],
            )

            # Upsert to SQLite with full Phase B contract payload
            self._sqlite_conn.execute(
                """
                INSERT OR REPLACE INTO l2_cache (
                    id, query, response,
                    tenant_id, embedding_model_id, corpus_version,
                    evidence_ids, grounding_complete, policy_version,
                    ttl_seconds, expires_at, entry_schema_version
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    query_id,
                    query,
                    response,
                    tenant_id,
                    embedding_model_id,
                    corpus_version,
                    evidence_ids_json,
                    int(grounding_complete),
                    policy_version,
                    ttl_seconds,
                    expires_at_str,
                    entry_schema_version,
                ),
            )
            self._sqlite_conn.commit()

            # Evict if over max_entries
            self._evict_if_needed()

            Logger.debug(f"[L2Cache] l2_write entry_id={query_id[:8]} query_prefix={query[:40]!r}")

        except (OSError, sqlite3.Error, RuntimeError) as e:
            Logger.error(f"L2 cache set error (data may be lost): {e}")
            # Re-raise to alert caller of data loss risk
            raise

    def _mock_get(self, query: str) -> str | None:
        """Mock cache get for testing/development."""
        self._miss_count += 1
        return None

    def _mock_set(self, query: str, response: str) -> None:
        """Mock cache set for testing/development."""
        pass

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        total = self._hit_count + self._miss_count
        hit_rate = self._hit_count / total if total > 0 else 0.0

        return {
            "layer": "L2_Semantic_Cache_Native",
            "hit_count": self._hit_count,
            "miss_count": self._miss_count,
            "hit_rate": hit_rate,
            "similarity_threshold": self.similarity_threshold,
            "token_savings_estimate": self._token_savings,
            "max_entries": self.max_entries,
            "provider": self.embedding_provider,
            "model": self.embedding_model,
        }

    def clear(self) -> None:
        """Clear all cached entries."""
        if self._cache == "mock":
            return

        try:
            # Clear ChromaDB collection
            self._chroma_client.delete_collection("l2_semantic_cache")
            self._chroma_collection = self._chroma_client.get_or_create_collection(
                name="l2_semantic_cache",
            )

            # Clear SQLite table
            self._sqlite_conn.execute("DELETE FROM l2_cache")
            self._sqlite_conn.commit()

            Logger.info("Native L2 cache cleared")
        except (
            OSError,
            sqlite3.Error,
            RuntimeError,
        ) as e:  # guardian: allow-log-and-swallow -- cache clear: non-fatal, stale entries may linger
            Logger.error(f"Failed to clear native L2 cache: {e}")

    def search_similar(
        self,
        query_text: str,
        threshold: float | None = None,
        *,
        tenant_id: str = "",
        embedding_model_id: str = "",
    ) -> list[dict[str, Any]]:
        """Search for semantically similar entries.

        Compatibility method for SemanticCacheManager integration.
        Returns list of results with 'score' and 'metadata' metadata.

        Args:
            query_text: Query text to search for
            threshold: Override similarity threshold (defaults to instance threshold)
            tenant_id: Filter results to this tenant only (Phase B)
            embedding_model_id: Filter results to this embedding model only (Phase B)

        Returns:
            List of dicts with keys: {'score': float, 'metadata': dict}
        """
        if self._cache == "mock":
            self._miss_count += 1
            return []

        try:
            # Use instance threshold if not overridden
            effective_threshold = threshold if threshold is not None else self.similarity_threshold

            # Phase B: build Chroma metadata filter
            _conditions: list[dict[str, Any]] = []
            if tenant_id:
                _conditions.append({"tenant_id": {"$eq": tenant_id}})
            if embedding_model_id:
                _conditions.append({"embedding_model_id": {"$eq": embedding_model_id}})
            _where: dict[str, Any] | None = None
            if len(_conditions) == 1:
                _where = _conditions[0]
            elif len(_conditions) > 1:
                _where = {"$and": _conditions}

            # Search ChromaDB (ChromaDB handles embeddings automatically via query_texts)
            _query_kwargs: dict[str, Any] = {"query_texts": [query_text], "n_results": 5}
            if _where is not None:
                _query_kwargs["where"] = _where
            results = self._chroma_collection.query(**_query_kwargs)

            formatted_results = []
            if results["ids"] and results["ids"][0]:
                for i, entry_id in tqdm(enumerate(results["ids"][0]), desc="Processing", unit="item"):
                    distance = results["distances"][0][i] if results["distances"] else 1.0
                    similarity = 1.0 - distance

                    if similarity >= effective_threshold:
                        # Fetch response + expires_at from SQLite (Phase C: expiry filter)
                        cursor = self._sqlite_conn.cursor()
                        cursor.execute(
                            "SELECT response, expires_at FROM l2_cache WHERE id = ?",
                            (entry_id,),
                        )
                        row = cursor.fetchone()

                        if row:
                            row_resp, row_exp = row[0], row[1]
                            # Phase C: skip and evict expired candidates
                            if row_exp:
                                try:
                                    exp = datetime.datetime.fromisoformat(row_exp)
                                    if exp < datetime.datetime.utcnow():
                                        self._hard_evict_entry(cursor, entry_id)
                                        Logger.debug(
                                            f"[L2Cache] l2_search_evict_expired entry_id={entry_id[:8]}"
                                        )
                                        continue
                                except (
                                    ValueError,
                                    TypeError,
                                ):  # guardian: allow-silent-swallow -- malformed TTL: treat as no-expiry, non-fatal
                                    pass
                            formatted_results.append(
                                {
                                    "score": similarity,
                                    "metadata": {"payload": row_resp},
                                }
                            )

            if formatted_results:
                self._hit_count += 1
                Logger.debug(
                    f"[L2Cache] l2_similarity_score={formatted_results[0]['score']:.4f} "
                    f"l2_candidate_count={len(formatted_results)}"
                )
            else:
                self._miss_count += 1
                Logger.debug(
                    f"[L2Cache] l2_similarity_score=none l2_candidate_count=0 "
                    f"query_prefix={query_text[:40]!r}"
                )

            return formatted_results

        except (OSError, sqlite3.Error, RuntimeError) as e:
            Logger.error(f"L2 cache search_similar error: {e}")
            self._miss_count += 1
            return []

    def _hard_evict_entry(self, cursor: sqlite3.Cursor, entry_id: str) -> None:
        """Delete a single entry from SQLite and ChromaDB (Phase C)."""
        try:
            cursor.execute("DELETE FROM l2_cache WHERE id = ?", (entry_id,))
            self._sqlite_conn.commit()
        except sqlite3.Error as e:  # guardian: allow-log-and-swallow -- evict: SQLite failure logged, chroma evict still attempted
            Logger.warning(f"[L2Cache] SQLite evict error for {entry_id[:8]}: {e}")
        try:
            self._chroma_collection.delete(ids=[entry_id])
        except RuntimeError as e:  # guardian: allow-log-and-swallow -- evict: chroma failure logged, entry will be naturally evicted later
            Logger.warning(f"[L2Cache] Chroma evict error for {entry_id[:8]}: {e}")
        try:
            from agentic_core.runtime.contracts.lifecycle_trace_contract import (  # noqa: PLC0415
                _record_semantic_cache_prom_event as _prom_evict,
            )

            _prom_evict("eviction", "")
        except (
            ImportError
        ):  # guardian: allow-silent-swallow -- lifecycle trace optional dependency, non-fatal
            pass

    def cleanup_expired(self) -> int:
        """Delete all expired entries from SQLite and ChromaDB.

        Safe to call repeatedly. Returns the number of entries evicted.
        """
        if self._cache == "mock":
            return 0

        evicted = 0
        try:
            cursor = self._sqlite_conn.cursor()
            now_iso = datetime.datetime.utcnow().isoformat()
            cursor.execute(
                "SELECT id FROM l2_cache WHERE expires_at IS NOT NULL AND expires_at < ?",
                (now_iso,),
            )
            expired_ids = [row[0] for row in cursor.fetchall()]
            if expired_ids:
                placeholders = ",".join("?" * len(expired_ids))
                cursor.execute(
                    f"DELETE FROM l2_cache WHERE id IN ({placeholders})",
                    expired_ids,
                )
                self._sqlite_conn.commit()
                try:
                    self._chroma_collection.delete(ids=expired_ids)
                except RuntimeError as e:  # guardian: allow-log-and-swallow -- chroma bulk evict: non-fatal, SQLite eviction already committed
                    Logger.warning(f"[L2Cache] Chroma bulk evict error: {e}")
                evicted = len(expired_ids)
                Logger.info(f"[L2Cache] cleanup_expired evicted={evicted}")
        except (
            OSError,
            sqlite3.Error,
        ) as e:  # guardian: allow-log-and-swallow -- cleanup_expired: non-fatal, expired entries will be evicted on next run
            Logger.error(f"[L2Cache] cleanup_expired error: {e}")
        return evicted

    def invalidate_by(
        self,
        *,
        tenant_id: str | None = None,
        corpus_version: str | None = None,
        embedding_model_id: str | None = None,
    ) -> int:
        """Delete all cache entries matching the given scope parameters.

        At least one parameter must be non-None. Raises ValueError otherwise.
        Returns the number of entries invalidated.
        """
        if tenant_id is None and corpus_version is None and embedding_model_id is None:
            raise ValueError(
                "invalidate_by() requires at least one of: tenant_id, corpus_version, embedding_model_id"
            )
        if self._cache == "mock":
            return 0

        clauses: list[str] = []
        params: list[str] = []
        if tenant_id is not None:
            clauses.append("tenant_id = ?")
            params.append(tenant_id)
        if corpus_version is not None:
            clauses.append("corpus_version = ?")
            params.append(corpus_version)
        if embedding_model_id is not None:
            clauses.append("embedding_model_id = ?")
            params.append(embedding_model_id)

        where_sql = " AND ".join(clauses)
        invalidated = 0
        try:
            cursor = self._sqlite_conn.cursor()
            cursor.execute(f"SELECT id FROM l2_cache WHERE {where_sql}", params)
            target_ids = [row[0] for row in cursor.fetchall()]
            if target_ids:
                placeholders = ",".join("?" * len(target_ids))
                cursor.execute(
                    f"DELETE FROM l2_cache WHERE id IN ({placeholders})",
                    target_ids,
                )
                self._sqlite_conn.commit()
                try:
                    self._chroma_collection.delete(ids=target_ids)
                except RuntimeError as e:  # guardian: allow-log-and-swallow -- chroma invalidate: non-fatal, SQLite invalidation already committed
                    Logger.warning(f"[L2Cache] Chroma invalidate error: {e}")
                invalidated = len(target_ids)
            scope = ", ".join(
                f"{k}={v!r}"
                for k, v in [
                    ("tenant_id", tenant_id),
                    ("corpus_version", corpus_version),
                    ("embedding_model_id", embedding_model_id),
                ]
                if v is not None
            )
            Logger.info(f"[L2Cache] invalidate_by scope=({scope}) invalidated={invalidated}")
        except (
            OSError,
            sqlite3.Error,
        ) as e:
            Logger.error(f"[L2Cache] invalidate_by error: {e}")
            raise
        return invalidated

    def close(self) -> None:
        """Close database connections."""
        if self._cache == "mock":
            return

        try:
            if hasattr(self, "_sqlite_conn"):
                self._sqlite_conn.close()
            if hasattr(self, "_chroma_client"):
                self._chroma_client.close()
            Logger.info("Native L2 cache connections closed")
        except (
            OSError,
            RuntimeError,
        ) as e:  # guardian: allow-log-and-swallow -- close: connection teardown failure logged, process exits anyway
            Logger.error(f"Failed to close native L2 cache: {e}")


# Global instance
_global_l2_cache: NativePersistentCacheClient | None = None


def get_global_l2_cache() -> NativePersistentCacheClient:
    """Get or create global L2 cache client."""
    global _global_l2_cache
    if _global_l2_cache is None:
        _global_l2_cache = NativePersistentCacheClient()
    return _global_l2_cache


def get_cached_response(query: str) -> str | None:
    """Convenience function to get cached response."""
    return get_global_l2_cache().get(query)


def cache_response(query: str, response: str) -> None:
    """Convenience function to cache response."""
    return get_global_l2_cache().set(query, response)


# Backward compatibility aliases
GPTCacheClient = NativePersistentCacheClient
get_global_gptcache = get_global_l2_cache
