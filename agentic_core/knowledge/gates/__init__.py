"""Gates Module.

Pipeline C Phase C2: Pre-retrieval gates with filtering and security.
"""

from .preretrieval_gate import PreRetrievalGate, FilterResult, AccessDecision
from .scope_metadata_resolver import ScopeMetadataResolver, ScopeMetadata

__all__ = [
    "PreRetrievalGate",
    "FilterResult",
    "AccessDecision",
    "ScopeMetadataResolver",
    "ScopeMetadata",
]
