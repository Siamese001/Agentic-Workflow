"""ADG Identity — canonical identity normalization pipeline.

Responsibilities:
- Classify every imported name into a deterministic IdentityKind
- Map dot-notation module names to repo-relative file paths where resolvable
- Produce explicit unresolved entity channels (never silently collapse)
- Attach confidence labels and evidence kinds to every identity decision
"""

from agentic_core.adg.identity.normalizer import (
    IdentityKind,
    IdentityRecord,
    IdentityNormalizer,
    normalize_identity,
)

__all__ = [
    "IdentityKind",
    "IdentityRecord",
    "IdentityNormalizer",
    "normalize_identity",
]
