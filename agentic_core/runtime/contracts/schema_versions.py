"""Central registry of schema versions for every runtime spine contract.

Each contract module declares its own ``*_SCHEMA_VERSION`` constant. This
module re-exports and pins them so:

    1. Verifiers can assert exact version matches in one place.
    2. Drift across contracts is visible at a glance.
    3. A bump in any contract's schema_version triggers a deliberate
       update here, surfacing the change in code review.

Convention: the registry MUST always be in lockstep with the contract
modules it cites. If a contract bumps to v2.0, this registry MUST be
edited in the same change.
"""

from __future__ import annotations

from agentic_core.runtime.contracts.c0_bypass_receipt import (
    C0_BYPASS_RECEIPT_SCHEMA_VERSION,
)
from agentic_core.runtime.contracts.identity import (
    IDENTITY_ENVELOPE_SCHEMA_VERSION,
)
from agentic_core.runtime.contracts.l3_bypass_receipt import (
    L3_BYPASS_RECEIPT_SCHEMA_VERSION,
)
from agentic_core.runtime.contracts.prompt_assembly_bypass_receipt import (
    PA_BYPASS_RECEIPT_SCHEMA_VERSION,
)

# The R1B-pass spine bundle protocol version. Bumped together with any
# breaking change to the spine_proof_bundle.py field shape.
SPINE_PROOF_SCHEMA_VERSION = "1.0"
HARNESS_SCHEMA_VERSION = "w2.r1b.1.0"

# All known schema versions, by contract module. Used by
# ``verify_spine_proof_bundle.py`` for cross-checking and by future
# verifiers that want to assert an exact runtime contract baseline.
SCHEMA_VERSION_REGISTRY: dict[str, str] = {
    "RuntimeIdentityEnvelope": IDENTITY_ENVELOPE_SCHEMA_VERSION,
    "L3BypassReceipt": L3_BYPASS_RECEIPT_SCHEMA_VERSION,
    "C0BypassReceipt": C0_BYPASS_RECEIPT_SCHEMA_VERSION,
    "PromptAssemblyBypassReceipt": PA_BYPASS_RECEIPT_SCHEMA_VERSION,
    "SpineProofBundle": SPINE_PROOF_SCHEMA_VERSION,
    "Harness": HARNESS_SCHEMA_VERSION,
}


__all__ = [
    "HARNESS_SCHEMA_VERSION",
    "SCHEMA_VERSION_REGISTRY",
    "SPINE_PROOF_SCHEMA_VERSION",
]
