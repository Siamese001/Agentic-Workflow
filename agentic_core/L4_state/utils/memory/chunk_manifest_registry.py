"""L4D ChunkManifestRegistry - Ingest/Substrate Domain Registry

Implements spec-compliant ChunkManifest (L4D) from Agentic Retrieval Models v9:
- DOM: Ingest/Substrate
- KEY: chunk_id (SHA-256)
- DAT: [22] EnrichedManifest
- MEC: Payload integrity, Map struct to head, Exact knowledge retrieval

Provides persistent storage for enriched chunk manifests with:
- SQLite backend for metadata
- Content-addressable storage (SHA-256 keys)
- Versioning and lineage tracking
- ADG edge integration (reads_from, writes_to)
"""

from __future__ import annotations

import hashlib
import json
import logging
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_records_learning_event,
    _emit_stores_embedding,
)

Logger = logging.getLogger(__name__)


@dataclass
class EnrichedChunkManifest:
    """Enriched chunk manifest data contract [22].

    Contains the semantic enrichment output from Pipeline B Step 3.
    """

    chunk_id: str  # SHA-256 hash
    raw_content: str
    enriched_content: dict[str, Any]  # Structured Knowledge Object

    # Enrichment fields
    title: str = ""
    summary: str = ""
    key_concepts: list[str] = field(default_factory=list)
    agentic_patterns: list[str] = field(default_factory=list)
    execution_insight: str = ""
    query_expansion_terms: list[str] = field(default_factory=list)

    # Metadata
    source_file: str = ""
    doc_id: str = ""
    chunk_index: int = 0
    security_labels: list[str] = field(default_factory=list)
    adg_edges: list[dict[str, Any]] = field(default_factory=list)

    # Embedding
    fact_vec: list[float] | None = None
    fact_vec_hash: str = ""
    embedding_model: str = ""

    # Provenance
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    healer_used: str = ""
    success_status: bool = True
    trace_id: str = ""
    replay_key: str = ""

    # Versioning
    version: int = 1
    parent_chunk_id: str | None = None


class ChunkManifestRegistry:
    """L4D ChunkManifestRegistry - Ingest/Substrate Domain.

    Stores enriched chunk manifests with:
    - Content-addressable storage (SHA-256)
    - Metadata persistence
    - Versioning and lineage
    - ADG edge tracking
    """

    def __init__(self, db_path: str = "artifacts/l4d_manifests.sqlite"):
        """Initialize ChunkManifestRegistry.

        Args:
            db_path: SQLite database path
        """
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Initialize SQLite database."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chunk_manifests (
                chunk_id TEXT PRIMARY KEY,
                raw_content TEXT,
                enriched_content TEXT,  -- JSON
                title TEXT,
                summary TEXT,
                key_concepts TEXT,  -- JSON array
                agentic_patterns TEXT,  -- JSON array
                execution_insight TEXT,
                query_expansion_terms TEXT,  -- JSON array
                source_file TEXT,
                doc_id TEXT,
                chunk_index INTEGER,
                security_labels TEXT,  -- JSON array
                adg_edges TEXT,  -- JSON array
                fact_vec TEXT,  -- JSON array
                fact_vec_hash TEXT,
                embedding_model TEXT,
                created_at TEXT,
                healer_used TEXT,
                success_status INTEGER,
                trace_id TEXT,
                replay_key TEXT,
                version INTEGER DEFAULT 1,
                parent_chunk_id TEXT,
                FOREIGN KEY (parent_chunk_id) REFERENCES chunk_manifests(chunk_id)
            )
        """)

        # Indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_doc_id ON chunk_manifests(doc_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_source_file ON chunk_manifests(source_file)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at ON chunk_manifests(created_at)
        """)

        conn.commit()
        conn.close()

        Logger.info(f"Initialized ChunkManifestRegistry at {self.db_path}")

    def store_manifest(self, manifest: EnrichedChunkManifest) -> bool:
        """Store an enriched chunk manifest.

        Args:
            manifest: EnrichedChunkManifest to store

        Returns:
            True if stored successfully
        """
        _trace_id = f"l4d_store_{manifest.chunk_id[:16]}"
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L4_STATE,
            "ChunkManifestRegistry.store_manifest",
        )
        _emit_records_learning_event(
            _trace_id,
            "chunk_manifest_stored",
            f"doc:{manifest.doc_id}",
        )

        if manifest.fact_vec:
            _emit_stores_embedding(_trace_id, manifest.chunk_id, manifest.fact_vec_hash or "")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT OR REPLACE INTO chunk_manifests (
                    chunk_id, raw_content, enriched_content, title, summary,
                    key_concepts, agentic_patterns, execution_insight, query_expansion_terms,
                    source_file, doc_id, chunk_index, security_labels, adg_edges,
                    fact_vec, fact_vec_hash, embedding_model, created_at,
                    healer_used, success_status, trace_id, replay_key, version, parent_chunk_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    manifest.chunk_id,
                    manifest.raw_content,
                    json.dumps(manifest.enriched_content),
                    manifest.title,
                    manifest.summary,
                    json.dumps(manifest.key_concepts),
                    json.dumps(manifest.agentic_patterns),
                    manifest.execution_insight,
                    json.dumps(manifest.query_expansion_terms),
                    manifest.source_file,
                    manifest.doc_id,
                    manifest.chunk_index,
                    json.dumps(manifest.security_labels),
                    json.dumps(manifest.adg_edges),
                    json.dumps(manifest.fact_vec) if manifest.fact_vec else None,
                    manifest.fact_vec_hash,
                    manifest.embedding_model,
                    manifest.created_at,
                    manifest.healer_used,
                    1 if manifest.success_status else 0,
                    manifest.trace_id,
                    manifest.replay_key,
                    manifest.version,
                    manifest.parent_chunk_id,
                ),
            )

            conn.commit()
            Logger.info(f"Stored manifest: {manifest.chunk_id[:16]}...")
            return True

        except Exception as e:
            Logger.error(f"Failed to store manifest: {e}")
            return False
        finally:
            conn.close()

    def get_manifest(self, chunk_id: str) -> EnrichedChunkManifest | None:
        """Retrieve a chunk manifest by ID.

        Args:
            chunk_id: SHA-256 chunk identifier

        Returns:
            EnrichedChunkManifest if found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT * FROM chunk_manifests WHERE chunk_id = ?
            """,
                (chunk_id,),
            )

            row = cursor.fetchone()
            if row is None:
                return None

            return self._row_to_manifest(row, cursor)

        finally:
            conn.close()

    def get_manifests_by_doc(self, doc_id: str) -> list[EnrichedChunkManifest]:
        """Retrieve all manifests for a document.

        Args:
            doc_id: Document ID

        Returns:
            List of EnrichedChunkManifest
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT * FROM chunk_manifests WHERE doc_id = ? ORDER BY chunk_index
            """,
                (doc_id,),
            )

            rows = cursor.fetchall()
            return [self._row_to_manifest(row, cursor) for row in rows]

        finally:
            conn.close()

    def get_manifests_by_source(self, source_file: str) -> list[EnrichedChunkManifest]:
        """Retrieve all manifests for a source file.

        Args:
            source_file: Source file path

        Returns:
            List of EnrichedChunkManifest
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT * FROM chunk_manifests WHERE source_file = ?
            """,
                (source_file,),
            )

            rows = cursor.fetchall()
            return [self._row_to_manifest(row, cursor) for row in rows]

        finally:
            conn.close()

    def get_lineage(self, chunk_id: str) -> dict[str, Any]:
        """Get chunk lineage (parent and children).

        Args:
            chunk_id: Chunk ID to trace

        Returns:
            Lineage info with parent and children
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Get this chunk
            cursor.execute(
                """
                SELECT chunk_id, parent_chunk_id FROM chunk_manifests WHERE chunk_id = ?
            """,
                (chunk_id,),
            )

            row = cursor.fetchone()
            if row is None:
                return {"error": "Chunk not found"}

            parent_id = row[1]

            # Get children
            cursor.execute(
                """
                SELECT chunk_id FROM chunk_manifests WHERE parent_chunk_id = ?
            """,
                (chunk_id,),
            )

            children = [r[0] for r in cursor.fetchall()]

            return {
                "chunk_id": chunk_id,
                "parent_id": parent_id,
                "children_ids": children,
            }

        finally:
            conn.close()

    def search_by_concept(self, concept: str, limit: int = 100) -> list[EnrichedChunkManifest]:
        """Search manifests by key concept.

        Args:
            concept: Concept to search for
            limit: Maximum results

        Returns:
            List of matching manifests
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Simple LIKE search on key_concepts JSON
            pattern = f'%"{concept}"%'

            cursor.execute(
                """
                SELECT * FROM chunk_manifests WHERE key_concepts LIKE ? LIMIT ?
            """,
                (pattern, limit),
            )

            rows = cursor.fetchall()
            return [self._row_to_manifest(row, cursor) for row in rows]

        finally:
            conn.close()

    def get_stats(self) -> dict[str, Any]:
        """Get registry statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT COUNT(*) FROM chunk_manifests")
            total = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(DISTINCT doc_id) FROM chunk_manifests")
            unique_docs = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(DISTINCT source_file) FROM chunk_manifests")
            unique_sources = cursor.fetchone()[0]

            cursor.execute("SELECT AVG(version) FROM chunk_manifests")
            avg_version = cursor.fetchone()[0] or 0

            return {
                "total_manifests": total,
                "unique_documents": unique_docs,
                "unique_sources": unique_sources,
                "avg_version": avg_version,
                "db_path": self.db_path,
            }

        finally:
            conn.close()

    def check_drift(self, chroma_collection: Any) -> dict[str, list[str]]:
        """Check for drift between ChromaDB and SQLite manifest registry.

        Compares chunk IDs in ChromaDB vs. manifests in SQLite.
        Returns dict with 'missing_in_chroma' and 'missing_in_sqlite' lists.

        Args:
            chroma_collection: ChromaDB collection object (must support .get())

        Returns:
            Dict with keys 'missing_in_chroma' and 'missing_in_sqlite'
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Get all chunk_ids from SQLite
            cursor.execute("SELECT chunk_id FROM chunk_manifests")
            sqlite_ids = {row[0] for row in cursor.fetchall()}

            # Get all chunk_ids from ChromaDB
            try:
                if not hasattr(chroma_collection, "get"):
                    Logger.warning("chroma_collection missing get() method for drift check")
                    chroma_ids = set()
                else:
                    chroma_result = chroma_collection.get()
                    chroma_ids = set(chroma_result.get("ids", []))
            except Exception as e:
                Logger.warning(f"Failed to query ChromaDB for drift check: {e}")
                chroma_ids = set()

            # Identify drift
            missing_in_chroma = list(sqlite_ids - chroma_ids)
            missing_in_sqlite = list(chroma_ids - sqlite_ids)

            return {
                "missing_in_chroma": missing_in_chroma,
                "missing_in_sqlite": missing_in_sqlite,
            }

        finally:
            conn.close()

    def verify_fact_vec_hash(self, manifest: EnrichedChunkManifest) -> bool:
        """Verify fact_vec hash integrity for a manifest.

        Re-hashes the manifest's fact_vec and compares to stored fact_vec_hash.

        Args:
            manifest: EnrichedChunkManifest to verify

        Returns:
            True if hash matches, False otherwise
        """
        if not manifest.fact_vec:
            # No embedding to verify
            return True

        computed_hash = hashlib.sha256(
            json.dumps(manifest.fact_vec, sort_keys=True).encode(),
        ).hexdigest()[:16]

        return computed_hash == manifest.fact_vec_hash

    def _row_to_manifest(
        self,
        row: tuple,
        cursor: sqlite3.Cursor,
    ) -> EnrichedChunkManifest:
        """Convert database row to EnrichedChunkManifest."""
        columns = [desc[0] for desc in cursor.description]
        row_dict = dict(zip(columns, row))

        return EnrichedChunkManifest(
            chunk_id=row_dict["chunk_id"],
            raw_content=row_dict["raw_content"],
            enriched_content=json.loads(row_dict["enriched_content"] or "{}"),
            title=row_dict["title"],
            summary=row_dict["summary"],
            key_concepts=json.loads(row_dict["key_concepts"] or "[]"),
            agentic_patterns=json.loads(row_dict["agentic_patterns"] or "[]"),
            execution_insight=row_dict["execution_insight"],
            query_expansion_terms=json.loads(row_dict["query_expansion_terms"] or "[]"),
            source_file=row_dict["source_file"],
            doc_id=row_dict["doc_id"],
            chunk_index=row_dict["chunk_index"],
            security_labels=json.loads(row_dict["security_labels"] or "[]"),
            adg_edges=json.loads(row_dict["adg_edges"] or "[]"),
            fact_vec=json.loads(row_dict["fact_vec"]) if row_dict["fact_vec"] else None,
            fact_vec_hash=row_dict["fact_vec_hash"],
            embedding_model=row_dict["embedding_model"],
            created_at=row_dict["created_at"],
            healer_used=row_dict["healer_used"],
            success_status=bool(row_dict["success_status"]),
            trace_id=row_dict["trace_id"],
            replay_key=row_dict["replay_key"],
            version=row_dict["version"],
            parent_chunk_id=row_dict["parent_chunk_id"],
        )


# Global instance
_global_manifest_registry: ChunkManifestRegistry | None = None


def get_global_manifest_registry() -> ChunkManifestRegistry:
    """Get or create global manifest registry."""
    global _global_manifest_registry
    if _global_manifest_registry is None:
        _global_manifest_registry = ChunkManifestRegistry()
    return _global_manifest_registry


def store_manifest(manifest: EnrichedChunkManifest) -> bool:
    """Convenience function to store manifest."""
    return get_global_manifest_registry().store_manifest(manifest)


def get_manifest(chunk_id: str) -> EnrichedChunkManifest | None:
    """Convenience function to get manifest."""
    return get_global_manifest_registry().get_manifest(chunk_id)


def get_manifests_by_doc(doc_id: str) -> list[EnrichedChunkManifest]:
    """Convenience function to get manifests by doc."""
    return get_global_manifest_registry().get_manifests_by_doc(doc_id)
