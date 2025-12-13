"""Scripts Logic Vector Search - Search operations for scripts logic vectors.

This module provides vector search capabilities for scripts logic operations,
including semantic search, similarity matching, and context retrieval.
Follows the functional component pattern with proper logging.
"""

from dataclasses import dataclass, field
import logging
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class SearchMode(Enum):
    """Search modes for vector operations."""
    SEMANTIC = "semantic"
    HYBRID = "hybrid"
    KEYWORD = "keyword"
    EXACT = "exact"

class VectorDistance(Enum):
    """Distance metrics for vector comparison."""
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    DOT_PRODUCT = "dot_product"
    MANHATTAN = "manhattan"

@dataclass
class SearchQuery:
    """Search query configuration."""
    query_text: str
    query_vector: Optional[List[float]] = None
    search_mode: SearchMode = SearchMode.SEMANTIC
    top_k: int = 10
    threshold: float = 0.7
    filters: Dict[str, Any] = field(default_factory=dict)
    include_metadata: bool = True

@dataclass
class SearchResult:
    """Individual search result."""
    id: str
    content: str
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    vector: Optional[List[float]] = None
    timestamp: Optional[datetime] = None

@dataclass
class SearchResults:
    """Collection of search results."""
    query: SearchQuery
    results: List[SearchResult] = field(default_factory=list)
    total_found: int = 0
    search_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class VectorIndexConfig:
    """Configuration for vector indexing."""
    index_name: str
    dimension: int
    distance_metric: VectorDistance = VectorDistance.COSINE
    index_type: str = "hnsw"
    ef_construction: int = 200
    m: int = 16
    max_elements: int = 10000

class ScriptsLogicVectorSearcher:
    """Main class for scripts logic vector search operations."""

    def __init__(self, config: Optional[VectorIndexConfig] = None):
        self.config = config or VectorIndexConfig(index_name="scripts_logic", dimension=1536)
        self.logger = logging.getLogger(self.__class__.__name__)
        self._index = {}
        self._vectors = {}
        self._metadata = {}

    def search_vectors(self, query: SearchQuery) -> SearchResults:
        """Search vectors based on query.

        Args:
            query: Search query configuration

        Returns:
            SearchResults: Search results with scores and metadata
        """
        self.logger.info(f"Searching vectors with mode: {query.search_mode.value}")

        start_time = datetime.utcnow()

        try:
            # Generate query vector if not provided
            if query.query_vector is None:
                query.query_vector = self._generate_query_vector(query.query_text)

            # Perform search based on mode
            if query.search_mode == SearchMode.SEMANTIC:
                results = self._semantic_search(query)
            elif query.search_mode == SearchMode.HYBRID:
                results = self._hybrid_search(query)
            elif query.search_mode == SearchMode.KEYWORD:
                results = self._keyword_search(query)
            else:  # EXACT
                results = self._exact_search(query)

            # Calculate search time
            search_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            search_results = SearchResults(
                query=query,
                results=results,
                total_found=len(results),
                search_time_ms=search_time,
                metadata={
                    "searched_at": datetime.utcnow().isoformat(),
                    "index_name": self.config.index_name,
                    "searcher": "ScriptsLogicVectorSearcher"
                }
            )

            self.logger.info(
                f"Vector search completed: found {len(results)} results in {search_time:.2f}ms"
            )

            return search_results

        except Exception as e:
            self.logger.error(f"Vector search failed: {str(e)}")
            return SearchResults(
                query=query,
                results=[],
                total_found=0,
                search_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                metadata={"error": str(e)}
            )

    def add_vector(self,
        vector_id: str,
        vector: List[float],
        content: str,
        metadata: Optional[Dict[str,
        Any]] = None) -> bool:
        """Add a vector to the index.

        Args:
            vector_id: Unique identifier for the vector
            vector: Vector embedding
            content: Content associated with the vector
            metadata: Optional metadata

        Returns:
            bool: True if vector was added successfully
        """
        try:
            # Validate vector dimension
            if len(vector) != self.config.dimension:
                raise ValueError(f"Vector dimension {len(vector)} != expected {self.config.dimension}")

            # Store vector and metadata
            self._vectors[vector_id] = np.array(vector)
            self._metadata[vector_id] = {
                "content": content,
                "timestamp": datetime.utcnow().isoformat(),
                **(metadata or {})
            }

            # Update index
            self._update_index()

            self.logger.debug(f"Added vector {vector_id} to index")
            return True

        except Exception as e:
            self.logger.error(f"Failed to add vector {vector_id}: {str(e)}")
            return False

    def delete_vector(self, vector_id: str) -> bool:
        """# SQL removed: Delete a vector from the index.

        Args:
            vector_id: ID of vector to delete

        Returns:
            bool: True if vector was deleted
        """
        if vector_id in self._vectors:
            del self._vectors[vector_id]
            del self._metadata[vector_id]
            self._update_index()
            self.logger.debug(f"Deleted vector {vector_id}")
            return True
        return False

    def get_vector(self, vector_id: str) -> Optional[Dict[str, Any]]:
        """Get vector and its metadata.

        Args:
            vector_id: ID of vector to retrieve

        Returns:
            Dict: Vector data or None if not found
        """
        if vector_id in self._vectors:
            return {
                "id": vector_id,
                "vector": self._vectors[vector_id].tolist(),
                "metadata": self._metadata[vector_id]
            }
        return None

    def _generate_query_vector(self, query_text: str) -> List[float]:
        """Generate vector embedding for query text.

        Args:
            query_text: Text to embed

        Returns:
            List[float]: Query vector embedding
        """
        # Placeholder for actual embedding generation
        # In production, this would call an embedding model
        return [0.0] * self.config.dimension

    def _semantic_search(self, query: SearchQuery) -> List[SearchResult]:
        """Perform semantic vector search."""
        results = []
        query_vector = np.array(query.query_vector)

        for vector_id, vector in self._vectors.items():
            # Calculate similarity
            similarity = self._calculate_similarity(query_vector,
                vector,
                self.config.distance_metric)

            if similarity >= query.threshold:
                result = SearchResult(
                    id=vector_id,
                    content=self._metadata[vector_id]["content"],
                    score=float(similarity),
                    metadata=self._metadata[vector_id] if query.include_metadata else {},
                    vector=vector.tolist() if query.include_metadata else None,
                    timestamp=datetime.fromisoformat(self._metadata[vector_id]["timestamp"])
                )
                results.append(result)

        # Sort by score and limit to top_k
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:query.top_k]

    def _hybrid_search(self, query: SearchQuery) -> List[SearchResult]:
        """Perform hybrid search combining semantic and keyword matching."""
        # Get semantic results
        semantic_results = self._semantic_search(query)

        # Get keyword results
        keyword_results = self._keyword_search(query)

        # Combine and deduplicate
        combined_results = {}

        # Add semantic results with higher weight
        for result in semantic_results:
            combined_results[result.id] = SearchResult(
                id=result.id,
                content=result.content,
                score=result.score * 0.7,  # Weight semantic results
                metadata=result.metadata,
                vector=result.vector,
                timestamp=result.timestamp
            )

        # Add keyword results
        for result in keyword_results:
            if result.id in combined_results:
                # Boost existing score
                combined_results[result.id].score += result.score * 0.3
            else:
                combined_results[result.id] = SearchResult(
                    id=result.id,
                    content=result.content,
                    score=result.score * 0.3,  # Weight keyword results
                    metadata=result.metadata,
                    vector=result.vector,
                    timestamp=result.timestamp
                )

        # Sort and return top results
        results = list(combined_results.values())
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:query.top_k]

    def _keyword_search(self, query: SearchQuery) -> List[SearchResult]:
        """Perform keyword-based search."""
        results = []
        query_terms = query.query_text.lower().split()

        for vector_id, metadata in self._metadata.items():
            content = metadata["content"].lower()

            # Calculate keyword match score
            matched_terms = sum(1 for term in query_terms if term in content)
            if matched_terms > 0:
                score = matched_terms / len(query_terms)

                if score >= query.threshold:
                    result = SearchResult(
                        id=vector_id,
                        content=metadata["content"],
                        score=score,
                        metadata=metadata if query.include_metadata else {},
                        vector=self._vectors[vector_id].tolist() if query.include_metadata else None,
                            
                        timestamp=datetime.fromisoformat(metadata["timestamp"])
                    )
                    results.append(result)

        results.sort(key=lambda x: x.score, reverse=True)
        return results[:query.top_k]

    def _exact_search(self, query: SearchQuery) -> List[SearchResult]:
        """Perform exact match search."""
        results = []
        query_text = query.query_text.lower()

        for vector_id, metadata in self._metadata.items():
            content = metadata["content"].lower()

            if query_text in content:
                result = SearchResult(
                    id=vector_id,
                    content=metadata["content"],
                    score=1.0,
                    metadata=metadata if query.include_metadata else {},
                    vector=self._vectors[vector_id].tolist() if query.include_metadata else None,
                    timestamp=datetime.fromisoformat(metadata["timestamp"])
                )
                results.append(result)

        return results[:query.top_k]

    def _calculate_similarity(self,
        vector1: np.ndarray,
        vector2: np.ndarray,
        metric: VectorDistance) -> float:
        """Calculate similarity between two vectors."""
        if metric == VectorDistance.COSINE:
            return np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))
        elif metric == VectorDistance.EUCLIDEAN:
            return 1 / (1 + np.linalg.norm(vector1 - vector2))
        elif metric == VectorDistance.DOT_PRODUCT:
            return np.dot(vector1, vector2)
        elif metric == VectorDistance.MANHATTAN:
            return 1 / (1 + np.sum(np.abs(vector1 - vector2)))
        else:
            return 0.0

    def _update_index(self) -> None:
        """# SQL removed: Update the internal index structure."""
        # Placeholder for index update logic
        # In production, this would update the vector index (e.g., HNSW)
        pass

    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector index.

        Returns:
            Dict: Index statistics
        """
        return {
            "index_name": self.config.index_name,
            "total_vectors": len(self._vectors),
            "dimension": self.config.dimension,
            "distance_metric": self.config.distance_metric.value,
            "index_type": self.config.index_type
        }

# Factory function for easy instantiation
def create_scripts_logic_vector_searcher(
    index_name: str = "scripts_logic",
    dimension: int = 1536,
    distance_metric: str = "cosine",
    **kwargs: Dict[str, object]) -> ScriptsLogicVectorSearcher:
    """Create a configured scripts logic vector searcher."""
    config = VectorIndexConfig(
        index_name=index_name,
        dimension=dimension,
        distance_metric=VectorDistance(distance_metric),
        **kwargs
    )
    return ScriptsLogicVectorSearcher(config)

# Convenience function for direct usage
def search_scripts_logic_vectors(
    query_text: str,
    search_mode: str = "semantic",
    top_k: int = 10,
    threshold: float = 0.7,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Search scripts logic vectors.

    Args:
        query_text: Text to search for
        search_mode: Search mode to use
        top_k: Number of results to return
        threshold: Minimum similarity threshold
        config: Optional searcher configuration

    Returns:
        Dict: Search results
    """
    # Create searcher and execute search
    searcher_config = VectorIndexConfig(**config or {})
    searcher = ScriptsLogicVectorSearcher(searcher_config)

    query = SearchQuery(
        query_text=query_text,
        search_mode=SearchMode(search_mode),
        top_k=top_k,
        threshold=threshold
    )

    results = searcher.search_vectors(query)

    # Convert results to dict for JSON serialization
    return {
        "query": {
            "text": results.query.query_text,
            "mode": results.query.search_mode.value,
            "top_k": results.query.top_k,
            "threshold": results.query.threshold
        },
        "results": [
            {
                "id": r.id,
                "content": r.content,
                "score": r.score,
                "metadata": r.metadata,
                "timestamp": r.timestamp.isoformat() if r.timestamp else None
            }
            for r in results.results
        ],
        "total_found": results.total_found,
        "search_time_ms": results.search_time_ms,
        "metadata": results.metadata
    }
