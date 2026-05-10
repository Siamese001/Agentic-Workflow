"""Route Contract — AG-RGGOV-W6 Core Contract

Canonical dataclass for L0 routing output.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(frozen=True, slots=True)
class RouteContract:
    """L0 routing output contract.

    Contains routing decision and execution path.
    """

    request_id: str
    run_id: str
    app_id: str
    trace_id: str

    # Routing decision
    route_id: str  # e.g., "R3_SIMPLE_GROUNDED_READ", "R5_MANAGED_WORKFLOW"
    l3_required: bool  # Whether L3 orchestration is needed

    # Execution path flags
    grounding_required: bool
    model_generation_required: bool
    write_authority_present: bool

    # Identity extension
    tenant_id: str = ""  # W1: threaded from L1PlanContract.tenant_id (D6)

    # W2: Capability / sandbox / egress allowlists (concern #8, D11=default-empty)
    sandbox_required: bool = False
    egress_policy_ref: str = ""
    allowed_tools: tuple[str, ...] = field(default_factory=tuple)
    allowed_models: tuple[str, ...] = field(default_factory=tuple)
    allowed_networks: tuple[str, ...] = field(default_factory=tuple)
    allowed_file_roots: tuple[str, ...] = field(default_factory=tuple)

    # Routing metadata
    reason_codes: tuple[str, ...] = field(default_factory=tuple)
    routing_timestamp: str = ""
    route_version: str = "W6.0"
    l5_certification_ref: str = ""

    def __post_init__(self) -> None:
        from agentic_core.L5_safety.contracts.verify import verify_certification_ref
        if not verify_certification_ref(self.l5_certification_ref):
            raise ValueError(
                f"RouteContract: missing or invalid l5_certification_ref={self.l5_certification_ref!r} "
                "(AG-W0-5=fail_closed)"
            )
