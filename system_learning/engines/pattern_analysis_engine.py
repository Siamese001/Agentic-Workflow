"""Pattern Analysis Engine - Deterministic semantic clustering for W3.

W3: Pattern Analysis Engine (Deterministic, Informational-Only).

Provides deterministic clustering of historical embeddings to detect
recurring failure motifs. All outputs are stable, hash-verifiable,
and bounded to C0 influence only.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Sequence


@dataclass(frozen=True)
class Cluster:
    """Deterministic cluster representation."""
    centroid: List[float]  # Rounded to fixed precision
    cluster_size: int
    representative_metadata_keys: List[str]  # Stable ordering


@dataclass(frozen=True)
class PatternSummary:
    """Summary of pattern analysis with deterministic digest."""
    clusters: List[Cluster]
    pattern_digest: str  # SHA-256 over canonical JSON


class PatternAnalysisEngine:
    """Deterministic pattern analysis engine for semantic clustering.

    Clusters historical embeddings to detect recurring failure motifs.
    All operations are deterministic with stable ordering and fixed
    precision rounding to ensure identical outputs across runs.
    """

    def __init__(self, *, precision: int = 6) -> None:
        """Initialize engine with deterministic precision.
        
        Args:
            precision: Decimal places for float rounding (default: 6)
        """
        self._precision = precision

    def analyze(
        self,
        historical_embeddings: List[List[float]],
        metadata: List[Dict[str, Any]],
        *,
        min_cluster_size: int,
    ) -> PatternSummary:
        """Analyze historical embeddings for deterministic patterns.
        
        Args:
            historical_embeddings: List of embedding vectors
            metadata: Corresponding metadata for each embedding
            min_cluster_size: Minimum cluster size to consider valid
            
        Returns:
            PatternSummary with deterministic clusters and digest
        """
        if len(historical_embeddings) != len(metadata):
            raise ValueError("Embeddings and metadata must have same length")
        
        if not historical_embeddings:
            return PatternSummary(clusters=[], pattern_digest=self._empty_digest())
        
        # Deterministic preprocessing
        processed_embeddings = [
            self._round_vector(emb) for emb in historical_embeddings
        ]
        
        # Deterministic clustering
        clusters = self._deterministic_cluster(
            processed_embeddings, metadata, min_cluster_size
        )
        
        # Generate deterministic digest
        digest = self._compute_digest(clusters)
        
        return PatternSummary(clusters=clusters, pattern_digest=digest)

    def _round_vector(self, vector: List[float]) -> List[float]:
        """Round vector to fixed precision for determinism."""
        return [round(x, self._precision) for x in vector]

    def _deterministic_cluster(
        self,
        embeddings: List[List[float]],
        metadata: List[Dict[str, Any]],
        min_cluster_size: int,
    ) -> List[Cluster]:
        """Perform deterministic clustering using distance threshold."""
        if not embeddings:
            return []
        
        # Sort by vector hash for deterministic order
        indexed_embeddings = list(enumerate(embeddings))
        indexed_embeddings.sort(key=lambda x: self._vector_hash(x[1]))
        
        # Simple deterministic clustering with fixed distance threshold
        distance_threshold = 0.5  # Fixed threshold for determinism
        clusters = []
        assigned = set()
        
        for idx, embedding in indexed_embeddings:
            if idx in assigned:
                continue
            
            # Find all embeddings within threshold distance
            cluster_indices = [idx]
            cluster_vectors = [embedding]
            
            for other_idx, other_embedding in indexed_embeddings:
                if other_idx != idx and other_idx not in assigned:
                    distance = self._euclidean_distance(embedding, other_embedding)
                    if distance <= distance_threshold:
                        cluster_indices.append(other_idx)
                        cluster_vectors.append(other_embedding)
                        assigned.add(other_idx)
            
            assigned.add(idx)
            
            # Only keep clusters meeting minimum size
            if len(cluster_indices) >= min_cluster_size:
                # Compute deterministic centroid
                centroid = self._compute_centroid(cluster_vectors)
                
                # Extract representative metadata keys with stable ordering
                metadata_keys = []
                for cluster_idx in sorted(cluster_indices):  # Stable order
                    if cluster_idx < len(metadata):
                        keys = list(metadata[cluster_idx].keys())
                        keys.sort()  # Stable ordering
                        metadata_keys.extend(keys)
                
                # Remove duplicates while preserving order
                seen = set()
                unique_keys = []
                for key in metadata_keys:
                    if key not in seen:
                        seen.add(key)
                        unique_keys.append(key)
                
                clusters.append(
                    Cluster(
                        centroid=centroid,
                        cluster_size=len(cluster_indices),
                        representative_metadata_keys=unique_keys[:10],  # Limit for stability
                    )
                )
        
        # Sort clusters by centroid hash for deterministic output
        clusters.sort(key=lambda c: self._vector_hash(c.centroid))
        
        return clusters

    def _euclidean_distance(self, v1: List[float], v2: List[float]) -> float:
        """Compute Euclidean distance between vectors."""
        if len(v1) != len(v2):
            return float('inf')
        
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))

    def _compute_centroid(self, vectors: List[List[float]]) -> List[float]:
        """Compute deterministic centroid of cluster."""
        if not vectors:
            return []
        
        dim = len(vectors[0])
        centroid = []
        
        for i in range(dim):
            mean_val = sum(v[i] for v in vectors) / len(vectors)
            centroid.append(round(mean_val, self._precision))
        
        return centroid

    def _vector_hash(self, vector: List[float]) -> str:
        """Compute deterministic hash of vector for sorting."""
        # Use fixed precision string representation
        vector_str = json.dumps(vector, separators=(',', ':'))
        return hashlib.sha256(vector_str.encode()).hexdigest()[:16]

    def _compute_digest(self, clusters: List[Cluster]) -> str:
        """Compute deterministic digest over all clusters."""
        # Convert to canonical JSON for deterministic hashing
        cluster_data = [asdict(cluster) for cluster in clusters]
        canonical_json = json.dumps(cluster_data, separators=(',', ':'), sort_keys=True)
        
        return hashlib.sha256(canonical_json.encode()).hexdigest()

    def _empty_digest(self) -> str:
        """Digest for empty input."""
        return hashlib.sha256(json.dumps([]).encode()).hexdigest()


# Export public interface
__all__ = [
    'PatternAnalysisEngine',
    'PatternSummary',
    'Cluster',
]
