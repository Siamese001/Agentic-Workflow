"""ADG Artifact — canonical artifact builder and deterministic serializer.

Produces and validates the full ADG canonical artifact (schema v3) from a
ScanResult, including:
- Module entities with layer labels and identity kinds
- Symbol entities with confidence labels
- Unresolved import report (explicit, never silent)
- Identity health section
- Structural metrics (blast-radius candidates, cycles, orphans, violations)
- Deterministic SHA256 artifact digest
"""

from agentic_core.adg.artifact.builder import (
    ADGArtifactBuilder,
    ADGArtifact,
    build_artifact,
)
from agentic_core.adg.artifact.serializer import (
    serialize_artifact,
    diff_artifacts,
)

__all__ = [
    "ADGArtifactBuilder",
    "ADGArtifact",
    "build_artifact",
    "serialize_artifact",
    "diff_artifacts",
]
