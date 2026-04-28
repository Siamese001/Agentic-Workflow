"""Gateways subpackage — sovereign LLM, write, and principal-aware adapters.

Aggregates the four gateway-shaped interfaces under a single namespace so
``apps_*`` and ``L*`` callers can import the seam they need from
``agentic_core.interfaces.gateways`` instead of four flat sibling modules
that read as if they're parent/child but aren't.

The flat module paths (``agentic_core.interfaces.gateway``,
``write_gateway``, ``principal_aware_write``, ``principal_aware_egress``)
remain as thin re-export shims for backward compatibility — production
consumers can migrate at their own pace.
"""

from __future__ import annotations

from agentic_core.interfaces.gateway import GenerationRequest, SovereignLLMGateway
from agentic_core.interfaces.principal_aware_egress import (
    EgressKind,
    PrincipalEgressEnvelope,
    attach_principal_to_egress,
    compute_egress_replay_key,
)
from agentic_core.interfaces.principal_aware_write import (
    PrincipalAttachedWrite,
    attach_principal_to_write,
    compute_principal_chain_digest,
    compute_principal_replay_key,
)
from agentic_core.interfaces.write_gateway import (
    InstructionPacket,
    UniversalWriteGateway,
    compute_replay_key,
    get_write_gateway,
)

__all__ = [
    # LLM gateway
    "SovereignLLMGateway",
    "GenerationRequest",
    # Write gateway
    "UniversalWriteGateway",
    "InstructionPacket",
    "get_write_gateway",
    "compute_replay_key",
    # Principal-aware write
    "PrincipalAttachedWrite",
    "attach_principal_to_write",
    "compute_principal_replay_key",
    "compute_principal_chain_digest",
    # Principal-aware egress
    "EgressKind",
    "PrincipalEgressEnvelope",
    "attach_principal_to_egress",
    "compute_egress_replay_key",
]
