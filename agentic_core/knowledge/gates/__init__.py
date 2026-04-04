"""Gates Module.

Pipeline C Phase C2: Pre-retrieval gates with filtering and security.
"""

from .preretrieval_gate import AccessDecision, FilterResult, PreRetrievalGate
from .scope_metadata_resolver import ScopeMetadata, ScopeMetadataResolver

__all__ = [
    "PreRetrievalGate",
    "FilterResult",
    "AccessDecision",
    "ScopeMetadataResolver",
    "ScopeMetadata",
]
