"""META layer package (v10_10).

Provides retrieval, metacognition, and other META-only utilities.
"""

# Re-export public META modules for convenience.
from archives.legacy_root_folders.retrievers.retrieval import retrieval
from . import metacognition as metacognition  # noqa: F401

__all__ = ["retrieval", "metacognition"]



