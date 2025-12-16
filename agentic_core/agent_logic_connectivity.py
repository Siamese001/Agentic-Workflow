import json
import hashlib
import logging
import os
import time
from typing import Any, Dict, Optional

from redisvl.query import VectorQuery
from redisvl.query.filter import Tag

from connection_manager import ConnectionManager

# Import our hardened schemas and connection manager
from schemas_connectivity import CanonEntry

logger = logging.getLogger(__name__)


class CanonValidator:
    """
    The Gatekeeper logic that enforces the 'Subatomic' canon.
    Uses a 2-stage cache (L1 Redis Hot, L2 Pinecone Cold) to validate incoming patterns.
    HARDENED: Uses compound cache keys to prevent stale cache hits.
    """

    # Lowered to catch code vs comment similarities
    def __init__(self, similarity_threshold: float = 0.75, manifest_path="active_manifest.json"):
        self.cm = ConnectionManager()
        self.similarity_threshold = similarity_threshold
        self.manifest_path = manifest_path
        self.manifest_cache = {}
        self.last_manifest_load = 0
        self.logger = logging.getLogger("CanonValidator")

        # Initialize connections immediately
        self.redis_client = self.cm.get_redis_client()
        self.redis_index = self.cm.get_redis_index()
        self.pinecone_index = self.cm.get_pinecone_index()

        # Load manifest immediately to prime the hash cache
        self._refresh_manifest()
        self.embedding_fn = self.cm.get_embedding

    def _refresh_manifest(self):
        """
        Reloads the manifest if the file on disk has changed.
        Crucial for Phase B to see Phase A's updates.
        """
        try:
            current_mtime = os.path.getmtime(self.manifest_path)
            if current_mtime > self.last_manifest_load:
                with open(self.manifest_path, 'r') as f:
                    self.manifest_cache = json.load(f)
                self.last_manifest_load = current_mtime
                self.logger.debug("Manifest reloaded for cache coherence.")
        except FileNotFoundError:
pass
self.logger.warning("Manifest not found. Cache invalidation may be disabled.")
            self.manifest_cache = {}

    def _get_file_hash(self, file_path: str) -> str:
        """
        Retrieves the authoritative SHA256 hash for a file from the manifest.
        Returns a default string if file is not in manifest (handling non-file queries).
        """
        # Ensure we have the latest hashes
        self._refresh_manifest()

        # Look up file entry in manifest (assuming structure: {path: {hash: "..."}})
        file_entry = self.manifest_cache.get(file_path)

        if file_entry and isinstance(file_entry, dict):
            return file_entry.get('content_hash', 'unknown_hash')
        return "global_context"

    def _generate_compound_key(self, query_content: str, context_file_path: Optional[str] = None) -> str:
        """
        [HARDENED 6b] Generates a cache key that binds the query to the SPECIFIC file version.

        Key Structure:
        SHA256( Query_Content + Separator + File_Content_Hash )
        """
        if context_file_path:
            # Get the current hash of the code we are asking about
            code_version_hash = self._get_file_hash(context_file_path)
            raw_key = f"{query_content}||{code_version_hash}"
        else:
            # Global queries not tied to specific files
            raw_key = query_content

        return hashlib.sha256(raw_key.encode('utf-8')).hexdigest()

    def process_entry(self, entry: CanonEntry) -> Dict[str, Any]:
        """
        Main entry point.
        1. Checks L1 (Redis) for exact AST match.
        2. Checks L2 (Pinecone) for semantic similarity.
        3. Decides whether to Ingest, Reject, or Flag.
        """
        start_time = time.time()

        # 1. Generate Embedding if missing
        if not entry.embedding:
            try:
                entry.embedding = self.embedding_fn(entry.content)
            except Exception as e:
pass
logger.error(f"Embedding generation failed: {e}")
                return {"status": "error", "message": str(e)}

        # 2. Check L1: Exact AST/Hash Match (Hot Memory)
        l1_match = self._check_l1_cache(entry)
        if l1_match:
            return self._format_result(l1_match, "l1_exact_match", start_time)

        # 3. Check L2: Semantic Similarity (Cold Memory)
        l2_match = self._check_l2_cache(entry)
        if l2_match:
            return self._format_result(l2_match, "l2_semantic_match", start_time)

        # 4. No Match Found -> Ingest as New Canon
        return self._ingest_new_entry(entry, start_time)

    def check_and_learn(self, code: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Compatibility method for simulation script.
        Accepts raw string input and converts to CanonEntry.
        """
        from schemas_connectivity import CanonEntry, CanonMetadata

        # Generate embedding first to meet validation requirements
        try:
            embedding = self.embedding_fn(code)
        except Exception as e:
pass
logger.error(f"Embedding generation failed: {e}")
            return {"status": "error", "message": str(e)}

        # Create CanonEntry from string input
        entry = CanonEntry(
            code_snippet=code,
            ast_structure={"type": "module"},  # Simple AST structure
            embedding=embedding,  # Now has valid embedding
            metadata=CanonMetadata(
                project_context=context.get(
                    "project_context", "default") if context else "default",
                canon_rule_id=context.get(
                    "type", "unknown") if context else "unknown"
            )
        )

        # Delegate to process_entry
        result = self.process_entry(entry)

        # Convert status to expected format for simulation
        if result.get("status") == "duplicate":
            result["source"] = "l1_match"
        elif result.get("status") == "similar":
            result["source"] = "l2_match"
        elif result.get("status") == "ingested":
            result["source"] = "no_match"
            result["is_valid"] = True

        return result

    def _check_l1_cache(self, entry: CanonEntry) -> Optional[Dict[str, Any]]:
        """
        Checks Redis L1 cache using the hardened compound key.
        """
        # Extract metadata from the entry object
        query_content = entry.content
        file_path = getattr(entry, 'file_path', None) # specific file this entry relates to

        # Generate the version-aware key
        cache_key = self._generate_compound_key(query_content, file_path)

        # Query Redis
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                self.logger.info(f"🟢 L1 Cache Hit for {file_path or 'global'}")
                return json.loads(cached_data)
        except Exception as e:
pass
self.logger.error(f"Redis lookup failed: {e}")

        self.logger.info(f"Reasoning cache miss - Code version may have changed.")
        return None

    def upsert_l1_cache(self, entry: CanonEntry, result: Dict):
        """
        Stores result in L1 cache with the version-aware key.
        """
        query_content = entry.content
        file_path = getattr(entry, 'file_path', None)

        cache_key = self._generate_compound_key(query_content, file_path)

        try:
            # Set with expiration (e.g., 1 hour) to prevent stale build-up
            self.redis_client.setex(cache_key, 3600, json.dumps(result))
        except Exception as e:
pass
self.logger.error(f"Redis upsert failed: {e}")

    def _check_l2_cache(self, entry: CanonEntry) -> Optional[Dict[str, Any]]:
        """
        Queries Pinecone for semantic similarity.
        """
        try:
            # query() expects a list of floats
            logger.info(
                f"Querying Pinecone with embedding dimension: {len(entry.embedding)}")
            results = self.pinecone_index.query(
                vector=entry.embedding,
                top_k=1,
                include_metadata=True
            )

            logger.info(f"Pinecone raw response: {results}")

            if results and results['matches']:
                best_match = results['matches'][0]
                score = best_match['score']
                logger.info(
                    f"Best match: ID={best_match['id']}, score={score}")

                if score >= self.similarity_threshold:
                    # FIX: Access metadata safely
                    metadata = best_match.get('metadata', {})

                    return {
                        "id": best_match['id'],
                        "content": metadata.get('content', 'Content not in metadata'),
                        "similarity": score,
                        "metadata": metadata
                    }

        except Exception as e:
pass
logger.error(f"Pinecone query failed: {e}")

        return None

    def _ingest_new_entry(self, entry: CanonEntry, start_time: float) -> Dict[str, Any]:
        """
        Writes the new unique entry to both L1 (Redis) and L2 (Pinecone).
        Checks active_manifest.json to ensure we only index validated files.
        """
        # Check if file is in active manifest before indexing
        if hasattr(entry, 'file_path') and entry.file_path:
            manifest_path = "active_manifest.json"
            if os.path.exists(manifest_path):
                try:
                    with open(manifest_path, 'r') as f:
                        manifest = json.load(f)

                    # Check if file is in the active manifest
                    file_paths_in_manifest = {
                        file_info.get("absolute_path", "")
                        for file_info in manifest.get("files", [])
                    }

                    if entry.file_path not in file_paths_in_manifest:
                        logger.warning(f"⚠️  Skipping indexing for non-manifest file: {entry.file_path}")
                        return {
                            "status": "skipped",
                            "is_valid": False,
                            "confidence": 0.0,
                            "source": "not_in_manifest",
                            "matched_pattern": None,
                            "processing_time": time.time() - start_time,
                            "message": "File not in active manifest - indexing skipped"
                        }
                except Exception as e:
pass
logger.warning(f"⚠️  Failed to check manifest: {e}")

        try:
            # 1. Get the authoritative hash for this file version
            current_hash = self._get_file_hash(entry.file_path) if hasattr(entry, 'file_path') and entry.file_path else "unknown"

            # 2. Write to Redis (Hot)
            redis_data = entry.to_redis_dict()
            self.redis_index.load([redis_data])
            logger.info(f"✅ Stored new pattern in Redis: {entry.id}")

            # 3. Write to Pinecone (Cold) with Version Tags
            pinecone_record = entry.to_pinecone_record()
            # [CRITICAL] Add content hash to metadata for filtering
            if 'metadata' not in pinecone_record:
                pinecone_record['metadata'] = {}
            pinecone_record['metadata']['content_hash'] = current_hash

            self.pinecone_index.upsert(vectors=[pinecone_record])
            logger.info(f"✅ Indexed {getattr(entry, 'file_path', 'unknown')} (Hash: {current_hash[:8]})")

            return {
                "status": "ingested",
                "is_valid": True,
                "confidence": 1.0,
                "source": "no_match",
                "matched_pattern": None,
                "ast_match": False,
                "recommendation": "New code pattern - stored in Canon",
                "pattern_id": entry.id,
                "query_time_ms": (time.time() - start_time) * 1000
            }

        except Exception as e:
pass
logger.error(f"Ingestion failed: {e}")
            return {
                "status": "error",
                "is_valid": False,
                "confidence": 0.0,
                "message": f"Ingestion failed: {str(e)}",
                "query_time_ms": (time.time() - start_time) * 1000
            }

    def query_semantic_memory(self, query: str, context_file: str = None, top_k=5):
        """
        [HARDENED] Retrieval that ignores 'Ghost' vectors.
        """
        query_vector = self.embedding_fn(query)

        # Default Filter: None
        metadata_filter = {}

        # If we are asking about a specific file, ONLY show me memories
        # that match the CURRENT version of that file.
        if context_file:
            active_hash = self._get_file_hash(context_file)
            metadata_filter = {
                "file_path": context_file,
                "content_hash": active_hash  # <--- The Shield
            }

        try:
            results = self.pinecone_index.query(
                vector=query_vector,
                filter=metadata_filter,
                top_k=top_k,
                include_metadata=True
            )
            return results
        except Exception as e:
pass
self.logger.error(f"Semantic query failed: {e}")
            return None

    def update_learning(self, pattern_id: str, is_valid: bool):
        """
        Stub method for updating learning based on validation results.
        TODO: Implement actual learning mechanism.
        """
        self.logger.info(f"Learning update: Pattern {pattern_id} is {'valid' if is_valid else 'invalid'}")


    def get_stats(self) -> Dict[str, Any]:
        """
        Return validation statistics.
        TODO: Implement actual stats collection.
        """
        return {
            "redis_stats": {
                "total_checks": 0,
                "hits": 0,
                "misses": 0
            },
            "pinecone_stats": {
                "total_queries": 0,
                "matches_found": 0,
                "vectors_stored": 0
            },
            "thresholds": {
                "similarity_threshold": self.similarity_threshold,
                "failure_threshold": 0.5,
                "success_threshold": 0.8,
                "max_patterns": 1000
            },
            "total_validations": 0,
            "valid_count": 0,
            "invalid_count": 0,
            "duplicate_count": 0,
            "error_count": 0
        }

    def _format_result(self, match: Dict, source: str, start_time: float) -> Dict[str, Any]:
        """
        Helper to format a 'Duplicate Found' response.
        """
        status = "duplicate" if source == "l1_exact_match" else "similar"

        return {
            "status": status,  # Crucial for the simulator to detect 'duplicate'
            "is_valid": True,  # It is valid logic, just redundant
            "confidence": match['similarity'],
            "source": source,
            "matched_pattern": match['id'],
            "ast_match": (source == "l1_exact_match"),
            "recommendation": "Use existing pattern",
            "metadata": match.get('metadata'),
            "query_time_ms": (time.time() - start_time) * 1000
        }

