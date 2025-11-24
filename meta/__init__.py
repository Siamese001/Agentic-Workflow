"""META layer package (v10_10).

Provides retrieval, metacognition, and other META-only utilities.
"""

# Re-export public META modules for convenience.
from . import retrieval as retrieval  # noqa: F401
from . import metacognition as metacognition  # noqa: F401

__all__ = ["retrieval", "metacognition"]



