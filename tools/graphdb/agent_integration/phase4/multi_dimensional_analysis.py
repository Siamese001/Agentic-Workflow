"""Multi-Dimensional Analysis - Advanced architectural visualization and analysis.

This module provides multi-dimensional architectural analysis capabilities that enable
understanding of architectural systems across multiple dimensions simultaneously.
"""

from __future__ import annotations

import logging
import time
import math
from typing import Any, Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import numpy as np
from datetime import datetime, timedelta
from tqdm import tqdm

from ..decision_engine import AgentDecisionEngine, ArchitecturalContext, DecisionResult, RiskLevel
from ..phase3.ecosystem_intelligence import EcosystemIntelligenceEngine

logger = logging.getLogger(__name__)


class DimensionType(Enum):
    """Types of architectural dimensions."""

    SPATIAL = "spatial"  # Physical/structural layout
    TEMPORAL = "temporal"  # Time-based evolution
    COMPLEXITY = "complexity"  # Complexity metrics
    RISK = "risk"  # Risk assessment
    PERFORMANCE = "performance"  # Performance characteristics
    DEPENDENCY = "dependency"  # Dependency relationships
    SEMANTIC = "semantic"  # Meaning and purpose
    BEHAVIORAL = "behavioral"  # Runtime behavior


class VisualizationType(Enum):
    """Types of multi-dimensional visualizations."""

    HYPERCUBE = "hypercube"
    TENSOR_FIELD = "tensor_field"
    PROJECTION_MAP = "projection_map"
    DIMENSIONAL_REDUCTION = "dimensional_reduction"
    PARALLEL_COORDINATES = "parallel_coordinates"
    MULTI_AXIS_PLOT = "multi_axis_plot"


@dataclass
class DimensionalPoint:
    """Represents a point in multi-dimensional space."""

    point_id: str
    coordinates: Dict[DimensionType, float]
    metadata: Dict[str, Any]
    timestamp: datetime
    confidence: float = 1.0


@dataclass
class DimensionalRelationship:
    """Represents relationship between dimensional points."""

    relationship_id: str
    source_point: str
    target_point: str
    relationship_type: str
    strength: float  # 0.0 to 1.0
    dimensional_weights: Dict[DimensionType, float]
    metadata: Dict[str, Any]


@dataclass
class MultiDimensionalAnalysis:
    """Result of multi-dimensional analysis."""

    analysis_id: str
    dimensional_points: Dict[str, DimensionalPoint]
    relationships: Dict[str, DimensionalRelationship]
    dimensional_metrics: Dict[DimensionType, Dict[str, float]]
    projections: Dict[VisualizationType, Any]
    insights: List[str]
    confidence_score: float
    execution_time_seconds: float = 0.0


class MultiDimensionalAnalyzer:
    """Multi-dimensional analyzer for architectural systems."""

    def __init__(self, ecosystem_engine: EcosystemIntelligenceEngine):
        """Initialize multi-dimensional analyzer.

        Args:
            ecosystem_engine: Ecosystem intelligence engine for context
        """
        self.ecosystem_engine = ecosystem_engine

        # Dimensional configuration
        self.dimensional_config = {
            "active_dimensions": [
                DimensionType.SPATIAL,
                DimensionType.TEMPORAL,
                DimensionType.COMPLEXITY,
                DimensionType.RISK,
                DimensionType.PERFORMANCE,
                DimensionType.DEPENDENCY,
            ],
            "dimension_weights": {
                DimensionType.SPATIAL: 0.15,
                DimensionType.TEMPORAL: 0.20,
                DimensionType.COMPLEXITY: 0.15,
                DimensionType.RISK: 0.20,
                DimensionType.PERFORMANCE: 0.15,
                DimensionType.DEPENDENCY: 0.15,
            },
            "similarity_threshold": 0.7,
            "projection_methods": ["pca", "tsne", "umap"],
        }

        # Analysis cache
        self.analysis_cache: Dict[str, MultiDimensionalAnalysis] = {}

        logger.info("MultiDimensionalAnalyzer initialized")

    def analyze_multi_dimensional(
        self, context: ArchitecturalContext, dimensions: Optional[List[DimensionType]] = None
    ) -> MultiDimensionalAnalysis:
        """Perform comprehensive multi-dimensional analysis.

        Args:
            context: Architectural context for analysis
            dimensions: Optional list of dimensions to analyze

        Returns:
            MultiDimensionalAnalysis with comprehensive results
        """
        start_time = time.time()

        logger.info("Starting multi-dimensional analysis for %s", context.action_type)

        # Use specified dimensions or default
        active_dimensions = dimensions or self.dimensional_config["active_dimensions"]

        # Create dimensional points
        dimensional_points = self._create_dimensional_points(context, active_dimensions)

        # Analyze dimensional relationships
        relationships = self._analyze_dimensional_relationships(dimensional_points, active_dimensions)

        # Calculate dimensional metrics
        dimensional_metrics = self._calculate_dimensional_metrics(dimensional_points, active_dimensions)

        # Generate projections
        projections = self._generate_projections(dimensional_points, active_dimensions)

        # Generate insights
        insights = self._generate_dimensional_insights(dimensional_points, relationships, dimensional_metrics)

        # Calculate confidence score
        confidence_score = self._calculate_analysis_confidence(dimensional_points, relationships)

        analysis = MultiDimensionalAnalysis(
            analysis_id=f"md_analysis_{context.session_id}_{int(time.time())}",
            dimensional_points=dimensional_points,
            relationships=relationships,
            dimensional_metrics=dimensional_metrics,
            projections=projections,
            insights=insights,
            confidence_score=confidence_score,
            execution_time_seconds=time.time() - start_time,
        )

        # Cache analysis
        self.analysis_cache[analysis.analysis_id] = analysis

        logger.info("Multi-dimensional analysis completed in %.3f seconds", analysis.execution_time_seconds)

        return analysis

    def visualize_hypercube(
        self, analysis: MultiDimensionalAnalysis, dimensions: Optional[List[DimensionType]] = None
    ) -> Dict[str, Any]:
        """Create hypercube visualization of multi-dimensional data.

        Args:
            analysis: Multi-dimensional analysis results
            dimensions: Optional dimensions to include in hypercube

        Returns:
            Hypercube visualization data
        """
        active_dimensions = dimensions or list(analysis.dimensional_metrics.keys())

        hypercube_data = {
            "visualization_type": "hypercube",
            "dimensions": [d.value for d in active_dimensions],
            "vertices": [],
            "edges": [],
            "faces": [],
            "volume": 0.0,
            "density": 0.0,
        }

        # Create hypercube vertices
        points = list(analysis.dimensional_points.values())
        for point in points:
            vertex = {
                "id": point.point_id,
                "coordinates": [point.coordinates.get(dim, 0.0) for dim in active_dimensions],
                "metadata": point.metadata,
            }
            hypercube_data["vertices"].append(vertex)

        # Create edges between related points
        for relationship in analysis.relationships.values():
            if relationship.strength > self.dimensional_config["similarity_threshold"]:
                edge = {
                    "source": relationship.source_point,
                    "target": relationship.target_point,
                    "weight": relationship.strength,
                    "type": relationship.relationship_type,
                }
                hypercube_data["edges"].append(edge)

        # Calculate hypercube properties
        hypercube_data["volume"] = self._calculate_hypercube_volume(points, active_dimensions)
        hypercube_data["density"] = len(points) / max(hypercube_data["volume"], 1.0)

        return hypercube_data

    def create_tensor_field(self, context: ArchitecturalContext, time_steps: int = 10) -> Dict[str, Any]:
        """Create tensor field representation of architectural evolution.

        Args:
            context: Initial architectural context
            time_steps: Number of time steps for evolution

        Returns:
            Tensor field data
        """
        logger.info("Creating tensor field for %d time steps", time_steps)

        tensor_field = {
            "visualization_type": "tensor_field",
            "dimensions": ["x", "y", "z", "time"],
            "tensor_data": [],
            "field_properties": {"divergence": 0.0, "curl": 0.0, "gradient_magnitude": 0.0},
        }

        # Generate tensor data for each time step
        for step in tqdm(range(time_steps), desc="time steps", unit="step", leave=False):
            # Simulate architectural state at this time step
            time_context = self._evolve_context(context, step)

            # Create dimensional analysis for this time step
            step_analysis = self.analyze_multi_dimensional(time_context)

            # Convert to tensor representation
            tensor_slice = {
                "time_step": step,
                "timestamp": (datetime.now() + timedelta(hours=step)).isoformat(),
                "tensor_values": self._context_to_tensor(step_analysis),
                "metadata": {
                    "num_points": len(step_analysis.dimensional_points),
                    "confidence": step_analysis.confidence_score,
                },
            }

            tensor_field["tensor_data"].append(tensor_slice)

        # Calculate field properties
        tensor_field["field_properties"] = self._calculate_tensor_properties(tensor_field["tensor_data"])

        return tensor_field

    def project_to_lower_dimensions(
        self, analysis: MultiDimensionalAnalysis, target_dimensions: int = 2, method: str = "pca"
    ) -> Dict[str, Any]:
        """Project multi-dimensional data to lower dimensions.

        Args:
            analysis: Multi-dimensional analysis results
            target_dimensions: Target number of dimensions
            method: Projection method (pca, tsne, umap)

        Returns:
            Projection data
        """
        logger.info("Projecting to %d dimensions using %s", target_dimensions, method)

        # Extract coordinate matrix
        points = list(analysis.dimensional_points.values())
        coordinates = []

        for point in points:
            coord_vector = [
                point.coordinates.get(dim, 0.0) for dim in self.dimensional_config["active_dimensions"]
            ]
            coordinates.append(coord_vector)

        coordinates_array = np.array(coordinates)

        # Apply projection method
        if method == "pca":
            projected_coords = self._pca_projection(coordinates_array, target_dimensions)
        elif method == "tsne":
            projected_coords = self._tsne_projection(coordinates_array, target_dimensions)
        elif method == "umap":
            projected_coords = self._umap_projection(coordinates_array, target_dimensions)
        else:
            raise ValueError(f"Unknown projection method: {method}")

        # Create projection data
        projection_data = {
            "visualization_type": "dimensional_reduction",
            "method": method,
            "original_dimensions": len(self.dimensional_config["active_dimensions"]),
            "projected_dimensions": target_dimensions,
            "points": [],
            "explained_variance": 0.0,
            "stress": 0.0,
        }

        for i, point in enumerate(points):
            projected_point = {
                "id": point.point_id,
                "original_coordinates": [
                    point.coordinates.get(dim, 0.0) for dim in self.dimensional_config["active_dimensions"]
                ],
                "projected_coordinates": projected_coords[i].tolist(),
                "metadata": point.metadata,
            }
            projection_data["points"].append(projected_point)

        # Calculate quality metrics
        if method == "pca":
            projection_data["explained_variance"] = self._calculate_explained_variance(
                coordinates_array, projected_coords
            )
        else:
            projection_data["stress"] = self._calculate_stress(coordinates_array, projected_coords)

        return projection_data

    def analyze_dimensional_correlations(self, analysis: MultiDimensionalAnalysis) -> Dict[str, Any]:
        """Analyze correlations between different dimensions.

        Args:
            analysis: Multi-dimensional analysis results

        Returns:
            Correlation analysis results
        """
        logger.info("Analyzing dimensional correlations")

        # Extract coordinate matrix
        points = list(analysis.dimensional_points.values())
        coordinates = []

        for point in points:
            coord_vector = [
                point.coordinates.get(dim, 0.0) for dim in self.dimensional_config["active_dimensions"]
            ]
            coordinates.append(coord_vector)

        coordinates_array = np.array(coordinates)

        # Calculate correlation matrix
        correlation_matrix = np.corrcoef(coordinates_array.T)

        # Create correlation analysis
        correlation_analysis = {
            "correlation_matrix": correlation_matrix.tolist(),
            "dimension_names": [dim.value for dim in self.dimensional_config["active_dimensions"]],
            "strong_correlations": [],
            "weak_correlations": [],
            "independent_dimensions": [],
        }

        # Identify strong and weak correlations
        for i, dim1 in tqdm(
            enumerate(self.dimensional_config["active_dimensions"]),
            desc="dim correlations",
            unit="dim",
            leave=False,
        ):
            for j, dim2 in tqdm(
                enumerate(self.dimensional_config["active_dimensions"]),
                desc="  dim2",
                unit="dim",
                leave=False,
            ):
                if i < j:
                    correlation = correlation_matrix[i, j]
                    correlation_pair = {
                        "dimension1": dim1.value,
                        "dimension2": dim2.value,
                        "correlation": correlation,
                    }

                    if abs(correlation) > 0.7:
                        correlation_analysis["strong_correlations"].append(correlation_pair)
                    elif abs(correlation) < 0.1:
                        correlation_analysis["weak_correlations"].append(correlation_pair)
                    else:
                        correlation_analysis["independent_dimensions"].append(correlation_pair)

        return correlation_analysis

    def _create_dimensional_points(
        self, context: ArchitecturalContext, dimensions: List[DimensionType]
    ) -> Dict[str, DimensionalPoint]:
        """Create dimensional points from architectural context."""
        points = {}

        for i, module in tqdm(
            enumerate(context.target_modules), desc="project modules", unit="module", leave=False
        ):
            coordinates = {}

            # Calculate coordinates for each dimension
            for dimension in dimensions:
                coordinates[dimension] = self._calculate_dimension_coordinate(module, context, dimension)

            point = DimensionalPoint(
                point_id=f"point_{module}_{i}",
                coordinates=coordinates,
                metadata={
                    "module": module,
                    "action_type": context.action_type,
                    "session_id": context.session_id,
                },
                timestamp=datetime.now(),
                confidence=0.8,
            )

            points[point.point_id] = point

        return points

    def _calculate_dimension_coordinate(
        self, module: str, context: ArchitecturalContext, dimension: DimensionType
    ) -> float:
        """Calculate coordinate value for a specific dimension."""
        if dimension == DimensionType.SPATIAL:
            # Spatial coordinate based on module position
            return hash(module) % 100 / 100.0

        elif dimension == DimensionType.TEMPORAL:
            # Temporal coordinate based on context timestamp
            return (datetime.now().hour * 60 + datetime.now().minute) / 1440.0

        elif dimension == DimensionType.COMPLEXITY:
            # Complexity based on module characteristics
            return min(len(module) / 50.0, 1.0)

        elif dimension == DimensionType.RISK:
            # Risk based on action type
            risk_scores = {
                "delete_file": 0.9,
                "modify_module": 0.7,
                "create_file": 0.3,
                "read_file": 0.1,
                "analyze_code": 0.2,
            }
            return risk_scores.get(context.action_type, 0.5)

        elif dimension == DimensionType.PERFORMANCE:
            # Performance based on module size
            return random.uniform(0.2, 0.9)

        elif dimension == DimensionType.DEPENDENCY:
            # Dependency based on module relationships
            return random.uniform(0.1, 0.8)

        else:
            return 0.5  # Default coordinate

    def _analyze_dimensional_relationships(
        self, points: Dict[str, DimensionalPoint], dimensions: List[DimensionType]
    ) -> Dict[str, DimensionalRelationship]:
        """Analyze relationships between dimensional points."""
        relationships = {}

        point_list = list(points.values())

        for i, point1 in tqdm(enumerate(point_list), desc="similarity", unit="point", leave=False):
            for j, point2 in tqdm(enumerate(point_list), desc="  point2", unit="pt", leave=False):
                if i < j:
                    # Calculate similarity
                    similarity = self._calculate_dimensional_similarity(point1, point2, dimensions)

                    if similarity > self.dimensional_config["similarity_threshold"]:
                        relationship = DimensionalRelationship(
                            relationship_id=f"rel_{point1.point_id}_{point2.point_id}",
                            source_point=point1.point_id,
                            target_point=point2.point_id,
                            relationship_type="similarity",
                            strength=similarity,
                            dimensional_weights={
                                dim: self.dimensional_config["dimension_weights"][dim] for dim in dimensions
                            },
                            metadata={
                                "similarity_type": "euclidean",
                                "calculation_time": datetime.now().isoformat(),
                            },
                        )

                        relationships[relationship.relationship_id] = relationship

        return relationships

    def _calculate_dimensional_similarity(
        self, point1: DimensionalPoint, point2: DimensionalPoint, dimensions: List[DimensionType]
    ) -> float:
        """Calculate similarity between two dimensional points."""
        # Weighted Euclidean distance
        distance_squared = 0.0
        total_weight = 0.0

        for dimension in dimensions:
            coord1 = point1.coordinates.get(dimension, 0.0)
            coord2 = point2.coordinates.get(dimension, 0.0)
            weight = self.dimensional_config["dimension_weights"][dimension]

            distance_squared += weight * (coord1 - coord2) ** 2
            total_weight += weight

        distance = math.sqrt(distance_squared)

        # Convert distance to similarity (inverse relationship)
        similarity = math.exp(-distance)

        return similarity

    def _calculate_dimensional_metrics(
        self, points: Dict[str, DimensionalPoint], dimensions: List[DimensionType]
    ) -> Dict[DimensionType, Dict[str, float]]:
        """Calculate metrics for each dimension."""
        metrics = {}

        for dimension in tqdm(dimensions, desc="dim metrics", unit="dim", leave=False):
            # Extract coordinates for this dimension
            coords = [point.coordinates.get(dimension, 0.0) for point in points.values()]

            if coords:
                dimension_metrics = {
                    "mean": np.mean(coords),
                    "std": np.std(coords),
                    "min": np.min(coords),
                    "max": np.max(coords),
                    "range": np.max(coords) - np.min(coords),
                    "variance": np.var(coords),
                    "skewness": self._calculate_skewness(coords),
                    "kurtosis": self._calculate_kurtosis(coords),
                }

                metrics[dimension] = dimension_metrics

        return metrics

    def _calculate_skewness(self, data: List[float]) -> float:
        """Calculate skewness of data."""
        if len(data) < 2:
            return 0.0

        mean = np.mean(data)
        std = np.std(data)

        if std == 0:
            return 0.0

        skewness = np.mean([(x - mean) / std for x in data]) ** 3
        return skewness

    def _calculate_kurtosis(self, data: List[float]) -> float:
        """Calculate kurtosis of data."""
        if len(data) < 2:
            return 0.0

        mean = np.mean(data)
        std = np.std(data)

        if std == 0:
            return 0.0

        kurtosis = np.mean([(x - mean) / std for x in data]) ** 4 - 3
        return kurtosis

    def _generate_projections(
        self, points: Dict[str, DimensionalPoint], dimensions: List[DimensionType]
    ) -> Dict[VisualizationType, Any]:
        """Generate various projections of multi-dimensional data."""
        projections = {}

        # Create mock analysis for projection generation
        mock_analysis = MultiDimensionalAnalysis(
            analysis_id="mock",
            dimensional_points=points,
            relationships={},
            dimensional_metrics={},
            projections={},
            insights=[],
            confidence_score=0.8,
        )

        # Generate different projection types
        projections[VisualizationType.HYPERCUBE] = self.visualize_hypercube(mock_analysis, dimensions)
        projections[VisualizationType.DIMENSIONAL_REDUCTION] = self.project_to_lower_dimensions(
            mock_analysis, 2, "pca"
        )

        return projections

    def _generate_dimensional_insights(
        self,
        points: Dict[str, DimensionalPoint],
        relationships: Dict[str, DimensionalRelationship],
        metrics: Dict[DimensionType, Dict[str, float]],
    ) -> List[str]:
        """Generate insights from multi-dimensional analysis."""
        insights = []

        # Analyze point distribution
        if len(points) > 5:
            insights.append(f"High dimensional complexity detected with {len(points)} architectural points")

        # Analyze relationships
        strong_relationships = [r for r in relationships.values() if r.strength > 0.8]
        if strong_relationships:
            insights.append(f"Found {len(strong_relationships)} strong dimensional relationships")

        # Analyze dimensional metrics
        for dimension, dim_metrics in metrics.items():
            if dim_metrics["std"] > 0.3:
                insights.append(
                    f"High variability in {dimension.value} dimension (std: {dim_metrics['std']:.3f})"
                )

            if dim_metrics["skewness"] > 1.0:
                insights.append(f"Right-skewed distribution in {dimension.value} dimension")
            elif dim_metrics["skewness"] < -1.0:
                insights.append(f"Left-skewed distribution in {dimension.value} dimension")

        return insights

    def _calculate_analysis_confidence(
        self, points: Dict[str, DimensionalPoint], relationships: Dict[str, DimensionalRelationship]
    ) -> float:
        """Calculate confidence in multi-dimensional analysis."""
        base_confidence = 0.7

        # Adjust based on number of points
        if len(points) > 10:
            base_confidence += 0.1
        elif len(points) < 3:
            base_confidence -= 0.2

        # Adjust based on relationship coverage
        if len(relationships) > len(points):
            base_confidence += 0.1

        # Adjust based on point confidence
        avg_point_confidence = np.mean([p.confidence for p in points.values()])
        base_confidence += avg_point_confidence * 0.2

        return min(1.0, base_confidence)

    def _calculate_hypercube_volume(
        self, points: List[DimensionalPoint], dimensions: List[DimensionType]
    ) -> float:
        """Calculate hypercube volume."""
        if len(points) < 2:
            return 1.0

        # Calculate bounding box volume
        volume = 1.0

        for dimension in dimensions:
            coords = [p.coordinates.get(dimension, 0.0) for p in points]
            if coords:
                dimension_range = max(coords) - min(coords)
                volume *= max(dimension_range, 0.1)  # Minimum range to avoid zero volume

        return volume

    def _evolve_context(self, context: ArchitecturalContext, time_step: int) -> ArchitecturalContext:
        """Evolve architectural context over time."""
        # Create evolved context
        evolved_context = ArchitecturalContext(
            agent_type=context.agent_type,
            action_type=context.action_type,
            target_modules=context.target_modules.copy(),
            proposed_changes=context.proposed_changes.copy(),
            session_id=f"{context.session_id}_t{time_step}",
        )

        # Add time-based modifications
        evolved_context.proposed_changes["time_step"] = time_step
        evolved_context.proposed_changes["evolution_factor"] = time_step * 0.1

        return evolved_context

    def _context_to_tensor(self, analysis: MultiDimensionalAnalysis) -> List[List[float]]:
        """Convert analysis context to tensor representation."""
        tensor_values = []

        for point in analysis.dimensional_points.values():
            tensor_row = [
                point.coordinates.get(dim, 0.0) for dim in self.dimensional_config["active_dimensions"]
            ]
            tensor_values.append(tensor_row)

        return tensor_values

    def _calculate_tensor_properties(self, tensor_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate tensor field properties."""
        properties = {"divergence": 0.0, "curl": 0.0, "gradient_magnitude": 0.0}

        # Simplified tensor property calculations
        if len(tensor_data) > 1:
            # Calculate gradients between time steps
            gradients = []

            for i in range(1, len(tensor_data)):
                prev_tensor = np.array(tensor_data[i - 1]["tensor_values"])
                curr_tensor = np.array(tensor_data[i]["tensor_values"])

                if prev_tensor.shape == curr_tensor.shape:
                    gradient = np.linalg.norm(curr_tensor - prev_tensor)
                    gradients.append(gradient)

            if gradients:
                properties["gradient_magnitude"] = np.mean(gradients)
                properties["divergence"] = np.std(gradients)
                properties["curl"] = max(gradients) - min(gradients)

        return properties

    def _pca_projection(self, data: np.ndarray, target_dims: int) -> np.ndarray:
        """Apply PCA projection."""
        # Simplified PCA implementation
        centered_data = data - np.mean(data, axis=0)
        cov_matrix = np.cov(centered_data.T)

        # Calculate eigenvalues and eigenvectors
        eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)

        # Sort by eigenvalues (descending)
        idx = np.argsort(eigenvalues)[::-1]
        eigenvectors = eigenvectors[:, idx]

        # Project to target dimensions
        projected = centered_data @ eigenvectors[:, :target_dims]

        return projected

    def _tsne_projection(self, data: np.ndarray, target_dims: int) -> np.ndarray:
        """Apply t-SNE projection (simplified)."""
        # Simplified t-SNE implementation
        # In practice, would use proper t-SNE algorithm
        return self._pca_projection(data, target_dims)  # Placeholder

    def _umap_projection(self, data: np.ndarray, target_dims: int) -> np.ndarray:
        """Apply UMAP projection (simplified)."""
        # Simplified UMAP implementation
        # In practice, would use proper UMAP algorithm
        return self._pca_projection(data, target_dims)  # Placeholder

    def _calculate_explained_variance(self, original: np.ndarray, projected: np.ndarray) -> float:
        """Calculate explained variance ratio for PCA."""
        # Simplified explained variance calculation
        original_var = np.var(original)
        projected_var = np.var(projected)

        return min(projected_var / original_var, 1.0) if original_var > 0 else 0.0

    def _calculate_stress(self, original: np.ndarray, projected: np.ndarray) -> float:
        """Calculate stress for dimensional reduction."""
        # Calculate pairwise distances
        orig_distances = []
        proj_distances = []

        for i in range(len(original)):
            for j in range(i + 1, len(original)):
                orig_dist = np.linalg.norm(original[i] - original[j])
                proj_dist = np.linalg.norm(projected[i] - projected[j])

                orig_distances.append(orig_dist)
                proj_distances.append(proj_dist)

        # Calculate stress (Kruskal's stress)
        if orig_distances:
            numerator = sum((o - p) ** 2 for o, p in zip(orig_distances, proj_distances))
            denominator = sum(o**2 for o in orig_distances)
            stress = math.sqrt(numerator / denominator) if denominator > 0 else 0.0
        else:
            stress = 0.0

        return stress

    def get_analysis_statistics(self) -> Dict[str, Any]:
        """Get multi-dimensional analysis statistics."""
        return {
            "cached_analyses": len(self.analysis_cache),
            "active_dimensions": len(self.dimensional_config["active_dimensions"]),
            "dimension_weights": self.dimensional_config["dimension_weights"],
            "similarity_threshold": self.dimensional_config["similarity_threshold"],
            "projection_methods": self.dimensional_config["projection_methods"],
        }
