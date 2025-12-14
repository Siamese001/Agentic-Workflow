"""Dataclass models for retrieve_schema_similarity."""
import logging


# from .retrieve_schema_similarity_enums import *  # Star import removed

@dataclass
class SchemaSimilarityRequest:
    """Request for schema similarity computation."""
    source_schema: Dict[str, Any]
    target_schema: Dict[str, Any]
    method: SimilarityMethod = SimilarityMethod.STRUCTURAL
    include_field_details: bool = False
    weight_structural: float = 0.4
    weight_semantic: float = 0.3
    weight_overlap: float = 0.3

@dataclass
class FieldMatch:
    """Field-level match information."""
    field_name: str
    source_type: str
    target_type: str
    type_match: bool
    semantic_similarity: float = 0.0
    confidence: float = 0.0

@dataclass
class SchemaSimilarityResult:
    """Result of schema similarity computation."""
    similarity_score: float
    compatibility_level: CompatibilityLevel
    field_matches: List[FieldMatch] = field(default_factory=list)
    missing_fields: List[str] = field(default_factory=list)
    extra_fields: List[str] = field(default_factory=list)
    type_conflicts: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SchemaSimilarityConfig:
    """Configuration for schema similarity operations."""
    default_method: SimilarityMethod = SimilarityMethod.HYBRID
    type_compatibility_matrix: Dict[str,
        Set[str]] = field(default_factory=lambda: {'string': {'string',
        'text'},
        'integer': {'integer',
        'number'},
        'number': {'integer',
        'number',
        'float'},
        'boolean': {'boolean'},
        'array': {'array',
        'list'},
        'object': {'object',
        'dict'},
        'null': {'null',
        'any'}})
    similarity_thresholds: Dict[str,
        float] = field(default_factory=lambda: {'identical': 0.95,
        'compatible': 0.7,
        'partially_compatible': 0.4})
