"""UWG durable write gateway surface."""

from agentic_core.L4_state.uwg.durable_write_gateway import (
    ALLOWED_OPERATIONS,
    DurableWriteGateway,
    NON_AUTHORIZED_SOURCES,
    UWGAuthorityError,
    UWGContentionError,
    get_default_gateway,
    reset_default_gateway,
)
from agentic_core.L4_state.uwg.write_class_severity import (
    AliasAtomicityViolationError,
    AliasManifest,
    InvalidationCoverageGate,
    InvalidationProposal,
    WriteClass,
    alias_swap_atomicity_proof,
    classify_write,
    requires_second_judge,
)

__all__ = [
    "ALLOWED_OPERATIONS",
    "DurableWriteGateway",
    "NON_AUTHORIZED_SOURCES",
    "UWGAuthorityError",
    "UWGContentionError",
    "get_default_gateway",
    "reset_default_gateway",
    "AliasAtomicityViolationError",
    "AliasManifest",
    "InvalidationCoverageGate",
    "InvalidationProposal",
    "WriteClass",
    "alias_swap_atomicity_proof",
    "classify_write",
    "requires_second_judge",
]
