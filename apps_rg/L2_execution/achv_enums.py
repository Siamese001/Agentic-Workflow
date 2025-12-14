"""Enum types for achv_bullet_synthesizer_types."""
import logging



logger = logging.getLogger(__name__)
class BulletFormat(Enum):
    """TODO: Add docstring."""

    UNIFY = 'UNIFY'
    IBM = 'IBM'

    """TODO: Add docstring."""

class ProvenanceType(Enum):
    """TODO: Add docstring."""
    VERB = 'V'
    TECH = 'T'
    SOFT = 'S'
