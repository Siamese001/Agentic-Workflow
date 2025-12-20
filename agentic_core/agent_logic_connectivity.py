import hashlib
import json
import logging
import os
import time
from typing import Any, Dict, Optional

# Local application imports
from connection_manager import ConnectionManager
from schemas_connectivity import CanonEntry, CanonMetadata

# Initialize a module-level logger
logger = logging.getLogger(__name__)


class CanonValidator:
    """
    The Gatekeeper logic that enforces the 'Subatomic' canon.
    Uses a 2-stage cache (L1 Redis Hot, L2 Pinecone Cold) to validate incoming patterns.
    HARDENED: Uses compound cache keys to prevent stale cache hits.
    """
    # Class constants for configuration
    REDIS_CACHE_EXPIRY_SECONDS = 3600  # 1 hour
    FAILURE_THRESHOLD = 0.5
    SUCCESS_THRESHOLD = 0.8
    MAX_PATTERNS = 1000

    def __init__(self, similarity_threshold: float = 0.75,
                 manifest_path: str = "active_manifest.json"):
        """
        Initializes the CanonValidator with connection managers and cache settings.

        Args:
            similarity_threshold (float): The minimum similarity score for an L2 match.
            manifest_path (str): Path to the active manifest JSON file.
        """
        self.cm = ConnectionManager()
        self.similarity_threshold = similarity_threshold
        self.manifest_path = manifest_path
        self.manifest_cache: Dict[str, Any] = {}
        # manifest_lookup maps file_path -> manifest_entry for quick access
        self.manifest_lookup: Dict[str, Dict[str, Any]] = {}
        self.last_manifest_load = 0

        # Initialize connections immediately
        self.redis_client = self.cm.get_redis_client()
        self.redis_index = self.cm.get_redis_index()
        self.pinecone_index = self.cm.get_pinecone_index()

        # Load manifest immediately to prime the hash cache
        self._refresh_manifest()
        self.embedding_fn = self.cm.get_embedding

    def _load_manifest_data(self) -> Dict[str, Any]:
        """Helper to load manifest data from file."""
        with open(self.manifest_path, 'r') as f:
            return json.load(f)

    def _build_manifest_lookup(self, manifest_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Builds a quick lookup dictionary from file path to its manifest entry.
        """
        lookup = {}
        for file_info in manifest_data.get("files", []):
            if isinstance(file_info, dict) and "absolute_path" in file_info:
                lookup[file_info["absolute_path"]] = file_info
        return lookup

    def _perform_manifest_update(self, new_mtime: float):
        """Helper to update manifest cache, lookup, and last load time."""
        self.manifest_cache = self._load_manifest_data()
        self.manifest_lookup = self._build_manifest_lookup(self.manifest_cache)
        self.last_manifest_load = new_mtime
        logger.debug("Manifest reloaded for cache coherence.")

    def _refresh_manifest(self):
        """
        Reloads the manifest if the file on disk has changed.
        Crucial for Phase B to see Phase A's updates.
        """
        try:
            current_mtime = os.path.getmtime(self.manifest_path)
        except FileNotFoundError:
            logger.warning("Manifest not found. Cache invalidation may be disabled.")
            self.manifest_cache = {}
            self.manifest_lookup = {}  # Clear lookup as well
            return
        except Exception as e:
            logger.error(f"Error refreshing manifest: {e}")
            self.manifest_cache = {}
            self.manifest_lookup = {}
            return

        # If we reached here, current_mtime was successfully retrieved.
        # Check if an update is needed.
        if current_mtime > self.last_manifest_load:
            self._perform_manifest_update(current_mtime)

    def _get_file_hash(self, file_path: str) -> str:
        """
        Retrieves the authoritative SHA256 hash for a file from the manifest.
        Returns a default string if file is not in manifest (handling non-file queries).
        """
        # Ensure we have the latest hashes
        self._refresh_manifest()

        # Use the pre-built lookup dictionary
        file_entry = self.manifest_lookup.get(file_path)

        if file_entry and isinstance(file_entry, dict):
            return file_entry.get('content_hash', 'unknown_hash')
        return "global_context"

    def _is_file_in_manifest(self, file_path: str) -> bool:
        """
        Checks if a given file path is present in the active manifest.
        """
        # Ensure manifest is up-to-date
        self._refresh_manifest()

        # Use the pre-built lookup dictionary
        return file_path in self.manifest_lookup

    def _generate_compound_key(self, query_content: str,
                               context_file_path: Optional[str] = None) -> str:
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
                entry.embedding = self.embedding_fn(entry.code_snippet)
            except Exception as e:
                logger.error(f"Embedding generation failed: {e}")
                return {"status": "error", "message": str(e)}

        # 2. Check L1: Exact AST/Hash Match (Hot Memory)
        l1_match = self._check_l1_cache(entry)
        if l1_match:
            # For L1, similarity is 1.0 (exact match)
            l1_match['similarity'] = 1.0
            return self._format_result(l1_match, "l1_exact_match", start_time)

        # 3. Check L2: Semantic Similarity (Cold Memory)
        l2_match = self._check_l2_cache(entry)
        if l2_match:
            return self._format_result(l2_match, "l2_semantic_match", start_time)

        # 4. No Match Found -> Ingest as New Canon
        return self._ingest_new_entry(entry, start_time)

    def check_and_learn(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Compatibility method for simulation script.
        Accepts raw string input and converts to CanonEntry.
        """
        # Generate embedding first to meet validation requirements
        try:
            embedding = self.embedding_fn(code)
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return {"status": "error", "message": str(e)}

        # Refactor to reduce nesting depth for CanonMetadata arguments
        project_context_val = "default"
        canon_rule_id_val = "unknown"
        file_path_val: Optional[str] = None

        if context:
            project_context_val = context.get("project_context", "default")
            canon_rule_id_val = context.get("type", "unknown")
            file_path_val = context.get("file_path")

        # Create CanonEntry from string input
        entry = CanonEntry(
            code_snippet=code,
            ast_structure={"type": "module"},  # Simple AST structure
            embedding=embedding,  # Now has valid embedding
            metadata=CanonMetadata(
                project_context=project_context_val,
                canon_rule_id=canon_rule_id_val,
                file_path=file_path_val  # Pass file_path to metadata
            )
        )

        # Delegate to process_entry
        result = self.process_entry(entry)

        # Convert status to expected format for simulation
        # The _format_result already sets 'status' to 'duplicate' or 'similar'
        # and 'is_valid' to True.
        # For 'ingested', we need to set 'is_valid' to True.
        if result.get("status") == "ingested":
            result["is_valid"] = True
            result["source"] = "no_match"  # Consistent with original logic

        # Ensure 'source' is set for all cases for the simulator
        if result.get("status") == "duplicate" and "source" not in result:
            result["source"] = "l1_match"
        elif result.get("status") == "similar" and "source" not in result:
            result["source"] = "l2_match"

        return result

    def _check_l1_cache(self, entry: CanonEntry) -> Optional[Dict[str, Any]]:
        """
        Checks Redis L1 cache using the hardened compound key.
        """
        # Extract metadata from the entry object
        query_content = entry.code_snippet
        file_path = entry.metadata.file_path if entry.metadata else None

        # Generate the version-aware key
        cache_key = self._generate_compound_key(query_content, file_path)

        cached_data = None
        try:
            cached_data = self.redis_client.get(cache_key)
        except Exception as e:
            logger.error(f"Redis lookup failed: {e}")
            logger.info("Reasoning cache miss due to Redis error.")
            return None

        if cached_data:
            logger.info(f"🟢 L1 Cache Hit for {file_path or 'global'}")
            return json.loads(cached_data)

        logger.info("Reasoning cache miss - Code version may have changed.")
        return None

    def upsert_l1_cache(self, entry: CanonEntry, result: Dict[str, Any]):
        """
        Stores result in L1 cache with the version-aware key.
        """
        query_content = entry.code_snippet
        file_path = entry.metadata.file_path if entry.metadata else None

        cache_key = self._generate_compound_key(query_content, file_path)

        try:
            # Set with expiration (e.g., 1 hour) to prevent stale build-up
            self.redis_client.setex(cache_key, self.REDIS_CACHE_EXPIRY_SECONDS,
                                    json.dumps(result))
        except Exception as e:
            logger.error(f"Redis upsert failed: {e}")

    def _process_pinecone_match(self, best_match: Dict[str, Any], score: float) -> Optional[Dict[str, Any]]:
        """
        Helper to process a Pinecone match, apply similarity threshold, and format the result.
        Reduces nesting depth in _check_l2_cache.
        """
        if score < self.similarity_threshold:
            return None

        # Access metadata safely
        metadata = best_match.get('metadata', {})

        return {
            "id": best_match['id'],
            "content": metadata.get('code_snippet', 'Content not in metadata'),
            "similarity": score,
            "metadata": metadata
        }

    def _check_l2_cache(self, entry: CanonEntry) -> Optional[Dict[str, Any]]:
        """
        Queries Pinecone for semantic similarity.
        """
        try:
            # query() expects a list of floats
            logger.info(
                f"Querying Pinecone with embedding dimension: {len(entry.embedding)}"
            )
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
                    f"Best match: ID={best_match['id']}, score={score}"
                )

                # Delegate to helper function to reduce nesting depth
                return self._process_pinecone_match(best_match, score)

        except Exception as e:
            logger.error(f"Pinecone query failed: {e}")

        return None

    def _ingest_new_entry(self, entry: CanonEntry, start_time: float) -> Dict[str, Any]:
        """
        Writes the new unique entry to both L1 (Redis) and L2 (Pinecone).
        Checks active_manifest.json to ensure we only index validated files.
        """
        file_path = entry.metadata.file_path if entry.metadata else None

        # Check if file is in active manifest before indexing
        if not (file_path and self._is_file_in_manifest(file_path)):
            logger.warning(
                f"[!]  Skipping indexing for non-manifest file: {file_path or 'N/A'}"
            )
            skipped_result = {
                "status": "skipped",
                "is_valid": False,
                "confidence": 0.0,
                "source": "not_in_manifest",
                "matched_pattern": None,
                "processing_time": time.time() - start_time,
                "message": "File not in active manifest - indexing skipped"
            }
            return skipped_result

        try:
            # 1. Get the authoritative hash for this file version
            current_hash = self._get_file_hash(file_path) if file_path else "unknown"

            # 2. Write to Redis (Hot)
            redis_data = entry.to_redis_dict()
            self.redis_index.load([redis_data])
            logger.info(f"[OK] Stored new pattern in Redis: {entry.id}")

            # 3. Write to Pinecone (Cold) with Version Tags
            pinecone_record = entry.to_pinecone_record()
            # [CRITICAL] Add content hash to metadata for filtering
            # Ensure metadata dictionary exists and get a reference to it
            metadata = pinecone_record.setdefault('metadata', {})
            metadata['content_hash'] = current_hash
            # Also add file_path to metadata for filtering
            metadata['file_path'] = file_path # Assign directly, can be None

            self.pinecone_index.upsert(vectors=[pinecone_record])
            logger.info(
                f"[OK] Indexed {file_path or 'unknown'} (Hash: {current_hash[:8]})"
            )

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
            logger.error(f"Ingestion failed: {e}")
            return {
                "status": "error",
                "is_valid": False,
                "confidence": 0.0,
                "message": f"Ingestion failed: {str(e)}",
                "query_time_ms": (time.time() - start_time) * 1000
            }

    def query_semantic_memory(self, query: str, context_file: Optional[str] = None,
                              top_k: int = 5) -> Optional[Dict[str, Any]]:
        """
        [HARDENED] Retrieval that ignores 'Ghost' vectors.
        """
        query_vector = self.embedding_fn(query)

        # Default Filter: None
        metadata_filter: Dict[str, Any] = {}

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
            logger.error(f"Semantic query failed: {e}")
            return None

    def update_learning(self, pattern_id: str, is_valid: bool):
        """
        Stub method for updating learning based on validation results.
        TODO: Implement actual learning mechanism.
        """
        logger.info(
            f"Learning update: Pattern {pattern_id} is {'valid' if is_valid else 'invalid'}"
        )

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
                "failure_threshold": self.FAILURE_THRESHOLD,
                "success_threshold": self.SUCCESS_THRESHOLD,
                "max_patterns": self.MAX_PATTERNS
            },
            "total_validations": 0,
            "valid_count": 0,
            "invalid_count": 0,
            "duplicate_count": 0,
            "error_count": 0
        }

    def _format_result(self, match: Dict[str, Any], source: str, start_time: float) -> Dict[str, Any]:
        """
        Helper to format a 'Duplicate Found' or 'Similar Found' response.
        """
        status = "duplicate" if source == "l1_exact_match" else "similar"

        # Ensure 'content' is retrieved correctly, assuming it's 'code_snippet' in metadata
        content = match.get('content') or match.get('metadata', {}).get('code_snippet', 'Content not available')

        return {
            "status": status,  # Crucial for the simulator to detect 'duplicate'
            "is_valid": True,  # It is valid logic, just redundant
            "confidence": match.get('similarity', 1.0 if source == "l1_exact_match" else 0.0),
            "source": source,
            "matched_pattern": match.get('id'),
            "ast_match": (source == "l1_exact_match"),
            "recommendation": "Use existing pattern",
            "metadata": match.get('metadata'),
            "query_time_ms": (time.time() - start_time) * 1000,
            "content": content  # Include content for better debugging/info
        }