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

from agentic_core.adg.artifact.builder_types import (
    ADGArtifact,
    ADGArtifactBuilder,
    build_artifact,
)
from agentic_core.adg.artifact.serializer_util import (
    diff_artifacts,
    serialize_artifact,
)

__all__ = [
    "ADGArtifactBuilder",
    "ADGArtifact",
    "build_artifact",
    "serialize_artifact",
    "diff_artifacts",
]
