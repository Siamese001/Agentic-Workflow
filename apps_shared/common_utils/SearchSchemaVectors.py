"""Schema Vector Searcher - Search operations for schema vectors.

This module provides vector search capabilities for schema operations,
including semantic search, similarity matching, and schema-aware retrieval.
Follows the functional component pattern with proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Tuple
import logging
import numpy as np
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class SchemaSearchMode(Enum):
    """Search modes for schema vector operations."""
    SEMANTIC = "semantic"
    STRUCTURAL = "structural"
    HYBRID = "hybrid"
    FIELD_BASED = "field_based"


class SchemaSimilarityType(Enum):
    """Types of schema similarity."""
    STRUCTURAL = "structural"
    SEMANTIC = "semantic"
    FIELD_OVERLAP = "field_overlap"
    TYPE_COMPATIBILITY = "type_compatibility"


@dataclass
class SchemaVectorEntry:
    """Entry in the schema vector store."""
    schema_id: str
    schema_name: str
    vector: List[float]
    field_vectors: Dict[str, List[float]] = field(default_factory=dict)
    schema_type: str = "json"
    field_count: int = 0
    complexity_score: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SchemaSearchQuery:
    """Search query for schema vectors."""
    query_text: Optional[str] = None
    query_schema: Optional[Dict[str, Any]] = None
    query_vector: Optional[List[float]] = None
    search_mode: SchemaSearchMode = SchemaSearchMode.SEMANTIC
    similarity_type: SchemaSimilarityType = SchemaSimilarityType.SEMANTIC
    top_k: int = 10
    threshold: float = 0.7
    schema_type_filter: Optional[str] = None
    min_field_overlap: int = 0
    include_field_matches: bool = False


@dataclass
class SchemaSearchResult:
    """Result of schema vector search."""
    entries: List[SchemaVectorEntry]
    scores: List[float]
    field_matches: Optional[List[Dict[str, Any]]] = None
    search_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SchemaVectorConfig:
    """Configuration for schema vector operations."""
    dimension: int = 1536
    enable_field_vectors: bool = True
    similarity_threshold: float = 0.7
    max_entries: int = 10000
    index_type: str = "hnsw"


class SchemaVectorSearcher:
    """Main class for schema vector search operations."""

    def __init__(self, config: Optional[SchemaVectorConfig] = None):
        self.config = config or SchemaVectorConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._schema_vectors: Dict[str, SchemaVectorEntry] = {}
        self._vector_index: Dict[str, np.ndarray] = {}
        self._field_index: Dict[str, Dict[str, np.ndarray]] = {}

    def search_schema_vectors(self, query: SchemaSearchQuery) -> SchemaSearchResult:
        """Search schema vectors based on query.

        Args:
            query: Schema search query configuration

        Returns:
            SchemaSearchResult: Search results with similarity scores
        """
        self.logger.info(f"Searching schema vectors with mode: {query.search_mode.value}")

        start_time = datetime.utcnow()

        try:
            # Generate query vector if needed
            if query.query_vector is None:
                query.query_vector = self._generate_query_vector(query)

            # Filter entries
            filtered_entries = self._filter_entries(query)

            # Perform search based on mode
            if query.search_mode == SchemaSearchMode.SEMANTIC:
                results, scores = self._semantic_search(query, filtered_entries)
            elif query.search_mode == SchemaSearchMode.STRUCTURAL:
                results, scores = self._structural_search(query, filtered_entries)
            elif query.search_mode == SchemaSearchMode.HYBRID:
                results, scores = self._hybrid_search(query, filtered_entries)
            else:  # FIELD_BASED
                results, scores, field_matches = self._field_based_search(query, filtered_entries)

            # Calculate search time
            search_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            search_result = SchemaSearchResult(
                entries=results,
                scores=scores,
                field_matches=field_matches if query.search_mode == SchemaSearchMode.FIELD_BASED else None,
                search_time_ms=search_time,
                metadata={
                    "searched_at": datetime.utcnow().isoformat(),
                    "search_mode": query.search_mode.value,
                    "similarity_type": query.similarity_type.value,
                    "total_schemas": len(self._schema_vectors)
                }
            )

            self.logger.info(
                f"Schema vector search completed: {len(results)} results in {search_time:.2f}ms"
            )

            return search_result

        except Exception as e:
            self.logger.error(f"Schema vector search failed: {str(e)}")
            return SchemaSearchResult(
                entries=[],
                scores=[],
                search_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                metadata={"error": str(e)}
            )

    def add_schema_vector(self, schema_id: str, schema_name: str, schema: Dict[str, Any],
                         vector: Optional[List[float]] = None, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Add a schema vector to the store.

        Args:
            schema_id: Unique schema identifier
            schema_name: Name of the schema
            schema: Schema definition
            vector: Pre-computed vector (optional)
            metadata: Additional metadata

        Returns:
            bool: True if added successfully
        """
        try:
            # Generate vector if not provided
            if vector is None:
                vector = self._generate_schema_vector(schema)

            # Generate field vectors if enabled
            field_vectors = {}
            if self.config.enable_field_vectors:
                field_vectors = self._generate_field_vectors(schema)

            # Calculate complexity score
            complexity = self._calculate_complexity(schema)

            # Create entry
            entry = SchemaVectorEntry(
                schema_id=schema_id,
                schema_name=schema_name,
                vector=vector,
                field_vectors=field_vectors,
                schema_type=metadata.get("schema_type", "json") if metadata else "json",
                field_count=len(self._extract_fields(schema)),
                complexity_score=complexity,
                metadata=metadata or {}
            )

            # Add to store
            self._schema_vectors[schema_id] = entry
            self._vector_index[schema_id] = np.array(vector)

            if field_vectors:
                self._field_index[schema_id] = {
                    field: np.array(vec) for field, vec in field_vectors.items()
                }

            self.logger.debug(f"Added schema vector: {schema_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to add schema vector: {str(e)}")
            return False

    def find_similar_schemas(self, schema_id: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """Find schemas similar to a given schema.

        Args:
            schema_id: ID of reference schema
            top_k: Number of similar schemas to return

        Returns:
            List of (schema_id, similarity_score) tuples
        """
        if schema_id not in self._schema_vectors:
            return []

        reference_entry = self._schema_vectors[schema_id]
        query = SchemaSearchQuery(
            query_vector=reference_entry.vector,
            search_mode=SchemaSearchMode.SEMANTIC,
            top_k=top_k
        )

        results, scores = self._semantic_search(query, list(self._schema_vectors.values()))

        # Filter out the reference schema itself
        similar_schemas = [
            (entry.schema_id, score)
            for entry, score in zip(results, scores)
            if entry.schema_id != schema_id
        ]

        return similar_schemas[:top_k]

    def get_schema_statistics(self) -> Dict[str, Any]:
        """Get statistics about the schema vector store.

        Returns:
            Dict: Store statistics
        """
        if not self._schema_vectors:
            return {"total_schemas": 0}

        # Calculate statistics
        total_schemas = len(self._schema_vectors)
        schema_types = {}
        complexities = []
        field_counts = []

        for entry in self._schema_vectors.values():
            # Count by type
            schema_type = entry.schema_type
            schema_types[schema_type] = schema_types.get(schema_type, 0) + 1

            complexities.append(entry.complexity_score)
            field_counts.append(entry.field_count)

        return {
            "total_schemas": total_schemas,
            "schema_types": schema_types,
            "average_complexity": sum(complexities) / len(complexities) if complexities else 0,
            "max_complexity": max(complexities) if complexities else 0,
            "average_field_count": sum(field_counts) / len(field_counts) if field_counts else 0,
            "max_field_count": max(field_counts) if field_counts else 0,
            "has_field_vectors": len(self._field_index)
        }

    def _generate_query_vector(self, query: SchemaSearchQuery) -> List[float]:
        """Generate query vector from search criteria."""
        if query.query_text:
            # Generate from text
            return self._text_to_vector(query.query_text)
        elif query.query_schema:
            # Generate from schema
            return self._generate_schema_vector(query.query_schema)
        else:
            # Return zero vector
            return [0.0] * self.config.dimension

    def _generate_schema_vector(self, schema: Dict[str, Any]) -> List[float]:
        """Generate vector representation of a schema."""
        # Extract schema features
        fields = self._extract_fields(schema)
        schema_text = " ".join(fields)

        # Convert to vector
        return self._text_to_vector(schema_text)

    def _generate_field_vectors(self, schema: Dict[str, Any]) -> Dict[str, List[float]]:
        """Generate vectors for individual fields."""
        field_vectors = {}
        fields = self._extract_fields(schema)

        for field in fields:
            field_vectors[field] = self._text_to_vector(field)

        return field_vectors

    def _extract_fields(self, schema: Dict[str, Any]) -> List[str]:
        """Extract field names from schema."""
        fields = []

        def extract_recursive(obj: object, prefix: str = "") -> None:
            if isinstance(obj, dict):
                for key, value in obj.items():
                    field_name = f"{prefix}.{key}" if prefix else key
                    fields.append(field_name)

                    if key in ["properties", "fields"] and isinstance(value, dict):
                        extract_recursive(value, field_name)
                    elif isinstance(value, dict):
                        extract_recursive(value, field_name)

        extract_recursive(schema)
        return fields

    def _calculate_complexity(self, schema: Dict[str, Any]) -> float:
        """Calculate complexity score for a schema."""
        fields = self._extract_fields(schema)

        # Simple complexity based on field count and nesting
        field_count = len(fields)
        max_depth = max(f.count(".") for f in fields) if fields else 0

        # Normalize to 0-1 range
        complexity = min(1.0, (field_count / 100 + max_depth / 10) / 2)

        return complexity

    def _filter_entries(self, query: SchemaSearchQuery) -> List[SchemaVectorEntry]:
        """Filter schema entries based on query criteria."""
        filtered = list(self._schema_vectors.values())

        # Filter by schema type
        if query.schema_type_filter:
            filtered = [e for e in filtered if e.schema_type == query.schema_type_filter]

        # Filter by minimum field overlap
        if query.min_field_overlap > 0 and query.query_schema:
            query_fields = set(self._extract_fields(query.query_schema))
            filtered = [
                e for e in filtered
                if len(set(self._extract_fields({"fields": e.metadata})).intersection(query_fields)) >= query.min_field_overlap
            ]

        return filtered

    def _semantic_search(self, query: SchemaSearchQuery, entries: List[SchemaVectorEntry]) -> Tuple[List[SchemaVectorEntry], List[float]]:
        """Perform semantic search."""
        if not query.query_vector:
            return [], []

        query_vector = np.array(query.query_vector)
        scored_entries = []

        for entry in entries:
            if entry.schema_id in self._vector_index:
                vector = self._vector_index[entry.schema_id]
                similarity = np.dot(query_vector, vector) / (np.linalg.norm(query_vector) * np.linalg.norm(vector))

                if similarity >= query.threshold:
                    scored_entries.append((entry, similarity))

        # Sort by similarity
        scored_entries.sort(key=lambda x: x[1], reverse=True)

        # Return top results
        results = scored_entries[:query.top_k]
        entries = [e[0] for e in results]
        scores = [e[1] for e in results]

        return entries, scores

    def _structural_search(self, query: SchemaSearchQuery, entries: List[SchemaVectorEntry]) -> Tuple[List[SchemaVectorEntry], List[float]]:
        """Perform structural similarity search."""
        if not query.query_schema:
            return self._semantic_search(query, entries)

        query_fields = set(self._extract_fields(query.query_schema))
        scored_entries = []

        for entry in entries:
            entry_fields = set(self._extract_fields({"schema": entry.metadata}))

            # Calculate Jaccard similarity
            intersection = len(query_fields.intersection(entry_fields))
            union = len(query_fields.union(entry_fields))

            if union > 0:
                similarity = intersection / union

                if similarity >= query.threshold:
                    scored_entries.append((entry, similarity))

        # Sort by similarity
        scored_entries.sort(key=lambda x: x[1], reverse=True)

        # Return top results
        results = scored_entries[:query.top_k]
        entries = [e[0] for e in results]
        scores = [e[1] for e in results]

        return entries, scores

    def _hybrid_search(self, query: SchemaSearchQuery, entries: List[SchemaVectorEntry]) -> Tuple[List[SchemaVectorEntry], List[float]]:
        """Perform hybrid search combining semantic and structural."""
        # Get semantic results
        semantic_entries, semantic_scores = self._semantic_search(query, entries)

        # Get structural results
        structural_entries, structural_scores = self._structural_search(query, entries)

        # Combine results
        combined = {}

        # Add semantic results
        for entry, score in zip(semantic_entries, semantic_scores):
            combined[entry.schema_id] = (entry, score * 0.6)

        # Add structural results
        for entry, score in zip(structural_entries, structural_scores):
            if entry.schema_id in combined:
                # Boost existing score
                combined[entry.schema_id] = (entry, combined[entry.schema_id][1] + score * 0.4)
            else:
                combined[entry.schema_id] = (entry, score * 0.4)

        # Sort and return top results
        results = sorted(combined.values(), key=lambda x: x[1], reverse=True)[:query.top_k]

        entries = [e[0] for e in results]
        scores = [e[1] for e in results]

        return entries, scores

    def _field_based_search(self, query: SchemaSearchQuery, entries: List[SchemaVectorEntry]) -> Tuple[List[SchemaVectorEntry], List[float], List[Dict[str, Any]]]:
        """Perform field-based search."""
        if not query.query_schema or not self.config.enable_field_vectors:
            return self._semantic_search(query, entries), [], []

        query_fields = self._extract_fields(query.query_schema)
        query_field_vectors = {field: self._text_to_vector(field) for field in query_fields}

        scored_entries = []
        field_matches_list = []

        for entry in entries:
            if entry.schema_id not in self._field_index:
                continue

            field_matches = []
            total_similarity = 0
            match_count = 0

            for query_field, query_vector in query_field_vectors.items():
                for entry_field, entry_vector in self._field_index[entry.schema_id].items():
                    # Calculate field similarity
                    similarity = np.dot(query_vector, entry_vector) / (
                        np.linalg.norm(query_vector) * np.linalg.norm(entry_vector)
                    )

                    if similarity >= query.threshold:
                        field_matches.append({
                            "query_field": query_field,
                            "entry_field": entry_field,
                            "similarity": float(similarity)
                        })
                        total_similarity += similarity
                        match_count += 1

            if match_count > 0:
                avg_similarity = total_similarity / match_count
                scored_entries.append((entry, avg_similarity))
                field_matches_list.append(field_matches)

        # Sort by average similarity
        scored_entries.sort(key=lambda x: x[1], reverse=True)

        # Return top results
        results = scored_entries[:query.top_k]
        entries = [e[0] for e in results]
        scores = [e[1] for e in results]
        field_matches = field_matches_list[:query.top_k]

        return entries, scores, field_matches

    def _text_to_vector(self, text: str) -> List[float]:
        """Convert text to vector representation."""
        # Placeholder for actual text-to-vector conversion
        # In production, this would use an embedding model
        import hashlib
        hash_bytes = hashlib.md5(text.encode()).digest()
        vector = [float(b) / 255.0 for b in hash_bytes]

        # Pad or truncate to desired dimension
        if len(vector) < self.config.dimension:
            vector.extend([0.0] * (self.config.dimension - len(vector)))
        else:
            vector = vector[:self.config.dimension]

        return vector


# Factory function for easy instantiation
def create_schema_vector_searcher(
    dimension: int = 1536,
    enable_field_vectors: bool = True,
    similarity_threshold: float = 0.7,
    **kwargs: object
) -> SchemaVectorSearcher:
    """Create a configured schema vector searcher."""
    config = SchemaVectorConfig(
        dimension=dimension,
        enable_field_vectors=enable_field_vectors,
        similarity_threshold=similarity_threshold,
        **kwargs
    )
    return SchemaVectorSearcher(config)


# Convenience function for direct usage
def search_schema_vectors(
    query_text: Optional[str] = None,
    query_schema: Optional[Dict[str, Any]] = None,
    search_mode: str = "semantic",
    similarity_type: str = "semantic",
    top_k: int = 10,
    threshold: float = 0.7,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Search schema vectors.

    Args:
        query_text: Text query
        query_schema: Schema query
        search_mode: Search mode to use
        similarity_type: Type of similarity to compute
        top_k: Number of results to return
        threshold: Minimum similarity threshold
        config: Optional searcher configuration

    Returns:
        Dict: Search results
    """
    # Create searcher and execute search
    searcher_config = SchemaVectorConfig(**config or {})
    searcher = SchemaVectorSearcher(searcher_config)

    query = SchemaSearchQuery(
        query_text=query_text,
        query_schema=query_schema,
        search_mode=SchemaSearchMode(search_mode),
        similarity_type=SchemaSimilarityType(similarity_type),
        top_k=top_k,
        threshold=threshold
    )

    result = searcher.search_schema_vectors(query)

    # Convert results to dict for JSON serialization
    return {
        "entries": [
            {
                "schema_id": e.schema_id,
                "schema_name": e.schema_name,
                "schema_type": e.schema_type,
                "field_count": e.field_count,
                "complexity_score": e.complexity_score,
                "timestamp": e.timestamp.isoformat(),
                "metadata": e.metadata
            }
            for e in result.entries
        ],
        "scores": result.scores,
        "field_matches": result.field_matches,
        "search_time_ms": result.search_time_ms,
        "metadata": result.metadata
    }
