"""Enum types for retrieve_schema_similarity."""
import logging



logger = logging.getLogger(__name__)
class SimilarityMethod(Enum):
    """Methods for computing schema similarity."""
    STRUCTURAL = 'structural'
    SEMANTIC = 'semantic'
    FIELD_OVERLAP = 'field_overlap'
    TYPE_COMPATIBILITY = 'type_compatibility'
    HYBRID = 'hybrid'

class CompatibilityLevel(Enum):
    """Levels of schema compatibility."""
    IDENTICAL = 'identical'
    COMPATIBLE = 'compatible'
    PARTIALLY_COMPATIBLE = 'partially_compatible'
    INCOMPATIBLE = 'incompatible'
