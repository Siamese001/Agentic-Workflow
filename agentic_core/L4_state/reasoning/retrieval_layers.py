"""
Retrieval Layers Implementation for Vector DB Integration

Implements L1-L4 retrieval layers:
- L1: Exact Cache (Redis-backed exact match)
- L2: Semantic Cache (similarity-based caching)
- L3: Semantic RAG (vector search retrieval)
- L4: Agentic Actions (tool schema validation)
"""

import hashlib
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any

import chromadb
from openai import OpenAI

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from agentic_core.cache import get_hot_cache
from agentic_core.L4_state.config.memory_store_config import MemoryStoreConfig

Logger = logging.getLogger(__name__)


class L1ExactCache:
    """L1 Exact Cache - Redis-backed exact match caching."""

    def __init__(self, ttl_seconds: int = 3600):
        """Initialize L1 cache with Redis backend."""
        self.ttl_seconds = ttl_seconds
        self.cache = get_hot_cache()
        self.hit_count = 0
        self.miss_count = 0

    def get(self, query: str) -> str | None:
        """Get exact match from cache."""
        # Normalize query for exact matching
        normalized_query = self._normalize_query(query)
        cache_key = f"l1_exact:{hashlib.sha256(normalized_query.encode()).hexdigest()}"

        result = self.cache.get(cache_key)
        if result is not None:
            self.hit_count += 1
            Logger.debug(f"L1 cache HIT for query: {query[:50]}...")
            return result.decode('utf-8')

        self.miss_count += 1
        Logger.debug(f"L1 cache MISS for query: {query[:50]}...")
        return None

    def set(self, query: str, response: str) -> None:
        """Set exact match in cache."""
        normalized_query = self._normalize_query(query)
        cache_key = f"l1_exact:{hashlib.sha256(normalized_query.encode()).hexdigest()}"

        self.cache.set(cache_key, response.encode('utf-8'), ttl_seconds=self.ttl_seconds)
        Logger.debug(f"L1 cache SET for query: {query[:50]}...")

    def _normalize_query(self, query: str) -> str:
        """Normalize query for exact matching."""
        # Basic normalization: lowercase, strip whitespace
        return query.lower().strip()

    def get_hit_rate(self) -> float:
        """Get cache hit rate."""
        total = self.hit_count + self.miss_count
        if total == 0:
            return 0.0
        return self.hit_count / total

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        return {
            "layer": "L1_Exact_Cache",
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": self.get_hit_rate(),
            "ttl_seconds": self.ttl_seconds
        }


class L2SemanticCache:
    """L2 Semantic Cache - similarity-based caching with threshold."""

    def __init__(self, similarity_threshold: float = 0.95, ttl_seconds: int = 3600):
        """Initialize L2 semantic cache."""
        self.similarity_threshold = similarity_threshold
        self.ttl_seconds = ttl_seconds
        self.cache = get_hot_cache()
        self.hit_count = 0
        self.miss_count = 0

        # Initialize embedding generator
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.embedding_client = OpenAI(api_key=api_key)
            self.mock_embeddings = False
        else:
            Logger.warning("OPENAI_API_KEY not set, using mock embeddings")
            self.embedding_client = None
            self.mock_embeddings = True
            # For deterministic mock embeddings
            self.embedding_seed = 42

    def _get_embedding(self, text: str) -> list[float] | None:
        """Get embedding for text."""
        if self.mock_embeddings:
            # Generate deterministic mock embedding based on text hash
            import random
            # Ensure positive seed by using absolute value of hash
            random.seed(self.embedding_seed + abs(hash(text)))
            return [random.uniform(-1, 1) for _ in range(1536)]

        try:
            response = self.embedding_client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            Logger.error(f"Failed to generate embedding: {e}")
            return None

    def get(self, query: str) -> str | None:
        """Get semantically similar cached response."""
        query_embedding = self._get_embedding(query)
        if query_embedding is None:
            return None

        # For simplicity, we'll use a hash-based approach for semantic cache
        # In production, this would be optimized with vector indexing
        cache_key = f"l2_semantic:{hashlib.sha256(query.encode()).hexdigest()}"
        cached_data = self.cache.get(cache_key)

        if cached_data:
            try:
                data = json.loads(cached_data.decode('utf-8'))
                cached_embedding = data.get("embedding")
                cached_response = data.get("response")

                if cached_embedding and self._calculate_similarity(query_embedding, cached_embedding) >= self.similarity_threshold:
                    self.hit_count += 1
                    Logger.debug(f"L2 semantic cache HIT for query: {query[:50]}...")
                    return cached_response
            except (json.JSONDecodeError, KeyError):
                pass  # Continue to miss logic

        self.miss_count += 1
        Logger.debug(f"L2 semantic cache MISS for query: {query[:50]}...")
        return None

    def set(self, query: str, response: str) -> None:
        """Set response in semantic cache."""
        query_embedding = self._get_embedding(query)
        if query_embedding is None:
            return

        cache_key = f"l2_semantic:{hashlib.sha256(query.encode()).hexdigest()}"
        cache_data = {
            "embedding": query_embedding,
            "response": response,
            "timestamp": time.time()
        }

        self.cache.set(cache_key, json.dumps(cache_data).encode('utf-8'), ttl_seconds=self.ttl_seconds)
        Logger.debug(f"L2 semantic cache SET for query: {query[:50]}...")

    def _calculate_similarity(self, embedding1: list[float], embedding2: list[float]) -> float:
        """Calculate cosine similarity between embeddings."""
        import math

        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
        magnitude1 = math.sqrt(sum(a * a for a in embedding1))
        magnitude2 = math.sqrt(sum(b * b for b in embedding2))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    def get_hit_rate(self) -> float:
        """Get cache hit rate."""
        total = self.hit_count + self.miss_count
        if total == 0:
            return 0.0
        return self.hit_count / total

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        return {
            "layer": "L2_Semantic_Cache",
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": self.get_hit_rate(),
            "similarity_threshold": self.similarity_threshold,
            "ttl_seconds": self.ttl_seconds
        }


class L3SemanticRAG:
    """L3 Semantic RAG - vector search retrieval from ChromaDB."""

    def __init__(self, persist_directory: str = None):
        """Initialize L3 RAG with ChromaDB."""
        self.config = MemoryStoreConfig()

        # Initialize ChromaDB client with persistent storage
        if persist_directory:
            self.client = chromadb.PersistentClient(path=persist_directory)
        else:
            persist_dir = Path("artifacts/chromadb")
            persist_dir.mkdir(parents=True, exist_ok=True)
            self.client = chromadb.PersistentClient(path=str(persist_dir))

        # Get collections
        self.docs_collection = self.client.get_or_create_collection(name="docs")
        self.traces_collection = self.client.get_or_create_collection(name="traces")

        # Initialize embedding generator
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.embedding_client = OpenAI(api_key=api_key)
            self.mock_embeddings = False
        else:
            Logger.warning("OPENAI_API_KEY not set, using mock embeddings")
            self.embedding_client = None
            self.mock_embeddings = True
            # For deterministic mock embeddings
            self.embedding_seed = 42

        self.query_count = 0

    def query_docs(self, query: str, n_results: int = 5) -> list[dict[str, Any]]:
        """Query document collection."""
        return self._query_collection(self.docs_collection, query, n_results, "docs")

    def query_traces(self, query: str, n_results: int = 5) -> list[dict[str, Any]]:
        """Query traces collection."""
        return self._query_collection(self.traces_collection, query, n_results, "traces")

    def _query_collection(self, collection, query: str, n_results: int, collection_type: str) -> list[dict[str, Any]]:
        """Query a specific ChromaDB collection."""
        query_embedding = self._get_embedding(query)
        if query_embedding is None:
            return []

        try:
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )

            self.query_count += 1
            Logger.debug(f"L3 RAG query {self.query_count}: {query[:50]}... ({len(results['ids'][0])} results)")

            # Format results
            formatted_results = []
            for i, (doc_id, document, metadata) in enumerate(zip(results['ids'][0], results['documents'][0], results['metadatas'][0])):
                formatted_results.append({
                    "id": doc_id,
                    "content": document,
                    "metadata": metadata,
                    "collection": collection_type,
                    "rank": i + 1
                })

            return formatted_results

        except Exception as e:
            Logger.error(f"L3 RAG query failed: {e}")
            return []

    def _get_embedding(self, text: str) -> list[float] | None:
        """Get embedding for text."""
        if self.mock_embeddings:
            # Generate deterministic mock embedding based on text hash
            import random
            # Ensure positive seed by using absolute value of hash
            random.seed(self.embedding_seed + abs(hash(text)))
            return [random.uniform(-1, 1) for _ in range(1536)]

        try:
            response = self.embedding_client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            Logger.error(f"Failed to generate embedding: {e}")
            return None

    def get_stats(self) -> dict[str, Any]:
        """Get RAG statistics."""
        return {
            "layer": "L3_Semantic_RAG",
            "query_count": self.query_count,
            "docs_count": self.docs_collection.count(),
            "traces_count": self.traces_collection.count(),
            "vector_dimensions": self.config.VECTOR_DIMENSIONS,
            "vector_metric": self.config.VECTOR_METRIC
        }


class L4AgenticActions:
    """L4 Agentic Actions - tool schema validation and action routing."""

    def __init__(self):
        """Initialize L4 actions."""
        self.action_count = 0
        self.validation_failures = 0

        # Define tool schemas for domain-specific actions
        self.tool_schemas = {
            "search_docs": {
                "name": "search_docs",
                "description": "Search documentation for relevant information",
                "parameters": {
                    "query": {
                        "type": "string",
                        "description": "Search query for documentation"
                    },
                    "n_results": {
                        "type": "integer",
                        "description": "Number of results to return",
                        "default": 5
                    }
                },
                "required": ["query"]
            },
            "find_similar_traces": {
                "name": "find_similar_traces",
                "description": "Find similar execution traces",
                "parameters": {
                    "trace_id": {
                        "type": "string",
                        "description": "Reference trace ID"
                    },
                    "n_results": {
                        "type": "integer",
                        "description": "Number of similar traces to find",
                        "default": 5
                    }
                },
                "required": ["trace_id"]
            },
            "get_architecture_info": {
                "name": "get_architecture_info",
                "description": "Get architecture documentation",
                "parameters": {
                    "component": {
                        "type": "string",
                        "description": "Component name (e.g., ADG, L0, L1, etc.)"
                    }
                },
                "required": ["component"]
            }
        }

    def validate_action(self, action_name: str, parameters: dict[str, Any]) -> bool:
        """Validate action parameters against schema."""
        self.action_count += 1

        if action_name not in self.tool_schemas:
            self.validation_failures += 1
            Logger.error(f"L4 validation: Unknown action '{action_name}'")
            return False

        schema = self.tool_schemas[action_name]
        required_params = schema.get("required", [])

        # Check required parameters
        for param in required_params:
            if param not in parameters:
                self.validation_failures += 1
                Logger.error(f"L4 validation: Missing required parameter '{param}' for action '{action_name}'")
                return False

        Logger.debug(f"L4 validation: Action '{action_name}' passed validation")
        return True

    def get_tool_schema(self, action_name: str) -> dict[str, Any] | None:
        """Get tool schema for action."""
        return self.tool_schemas.get(action_name)

    def list_available_actions(self) -> list[str]:
        """List all available actions."""
        return list(self.tool_schemas.keys())

    def get_stats(self) -> dict[str, Any]:
        """Get action statistics."""
        return {
            "layer": "L4_Agentic_Actions",
            "action_count": self.action_count,
            "validation_failures": self.validation_failures,
            "success_rate": 1.0 - (self.validation_failures / max(self.action_count, 1)),
            "available_actions": len(self.tool_schemas)
        }


class RetrievalOrchestrator:
    """Orchestrates all retrieval layers (L1-L4)."""

    def __init__(self):
        """Initialize all retrieval layers."""
        self.l1_cache = L1ExactCache()
        self.l2_cache = L2SemanticCache()
        self.l3_rag = L3SemanticRAG()
        self.l4_actions = L4AgenticActions()

        Logger.info("Retrieval orchestrator initialized with L1-L4 layers")

    def retrieve(self, query: str, n_results: int = 5) -> dict[str, Any]:
        """Retrieve information using all layers."""
        results = {
            "query": query,
            "layers_used": [],
            "results": [],
            "stats": {}
        }

        # L1: Exact Cache
        cached_result = self.l1_cache.get(query)
        if cached_result:
            results["layers_used"].append("L1")
            results["results"].append({
                "layer": "L1_Exact_Cache",
                "content": cached_result,
                "metadata": {"cache_hit": True}
            })
            results["stats"]["l1"] = self.l1_cache.get_stats()
            return results

        # L2: Semantic Cache
        semantic_result = self.l2_cache.get(query)
        if semantic_result:
            results["layers_used"].append("L2")
            results["results"].append({
                "layer": "L2_Semantic_Cache",
                "content": semantic_result,
                "metadata": {"cache_hit": True}
            })
            results["stats"]["l2"] = self.l2_cache.get_stats()
            return results

        # L3: Semantic RAG
        docs_results = self.l3_rag.query_docs(query, n_results)
        traces_results = self.l3_rag.query_traces(query, n_results)

        if docs_results or traces_results:
            results["layers_used"].append("L3")
            results["results"].extend([
                {"layer": "L3_Docs", **result} for result in docs_results
            ])
            results["results"].extend([
                {"layer": "L3_Traces", **result} for result in traces_results
            ])
            results["stats"]["l3"] = self.l3_rag.get_stats()

        # L4: Action validation (if this is an action query)
        if self._is_action_query(query):
            action_name, params = self._parse_action_query(query)
            if self.l4_actions.validate_action(action_name, params):
                results["layers_used"].append("L4")
                results["results"].append({
                    "layer": "L4_Agentic_Actions",
                    "content": f"Action '{action_name}' validated successfully",
                    "metadata": {"action": action_name, "parameters": params}
                })
                results["stats"]["l4"] = self.l4_actions.get_stats()

        return results

    def _is_action_query(self, query: str) -> bool:
        """Check if query is an action request."""
        action_keywords = ["search", "find", "get", "execute", "run"]
        return any(keyword in query.lower() for keyword in action_keywords)

    def _parse_action_query(self, query: str) -> tuple[str, dict[str, Any]]:
        """Parse action query into action name and parameters."""
        query_lower = query.lower()

        # Simple parsing - in production, this would be more sophisticated
        if "search" in query_lower:
            # Extract search term if present
            search_term = query  # Use full query as search term for now
            return "search_docs", {"query": search_term, "n_results": 5}
        elif "trace" in query_lower:
            # Look for trace ID pattern
            import re
            trace_match = re.search(r'trace_\d+', query)
            trace_id = trace_match.group(0) if trace_match else "trace_000042"
            return "find_similar_traces", {"trace_id": trace_id, "n_results": 5}
        elif "architecture" in query_lower:
            # Extract component name if mentioned
            if "adg" in query_lower:
                component = "ADG"
            elif "l0" in query_lower:
                component = "L0"
            elif "l4" in query_lower:
                component = "L4"
            else:
                component = "ADG"  # Default
            return "get_architecture_info", {"component": component}
        else:
            return "unknown", {}

    def get_all_stats(self) -> dict[str, Any]:
        """Get statistics from all layers."""
        return {
            "l1": self.l1_cache.get_stats(),
            "l2": self.l2_cache.get_stats(),
            "l3": self.l3_rag.get_stats(),
            "l4": self.l4_actions.get_stats()
        }
