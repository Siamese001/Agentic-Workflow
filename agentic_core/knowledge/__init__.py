"""Knowledge plane (L_PG) — stable public import surface for non-L_PG callers.

Subpackages retain their own ``__init__.py`` contracts; this root barrel exists
so L0 ingress (``package_driven_l0_binding``) can anchor ADG reachability without
importing internal module paths.
"""

from __future__ import annotations

from .enrichment import SemanticEnricher
from .gates import AccessDecision, GateDecision, PreRetrievalGate, check_access
from .retrieval import (
    EvidenceContract,
    EvidenceContractBuilder,
    PromptEnvelope,
    PromptEnvelopeFactory,
    query_sparse_lexical_lane,
)

__all__ = [
    "AccessDecision",
    "GateDecision",
    "PreRetrievalGate",
    "check_access",
    "EvidenceContract",
    "EvidenceContractBuilder",
    "PromptEnvelope",
    "PromptEnvelopeFactory",
    "query_sparse_lexical_lane",
    "SemanticEnricher",
]
