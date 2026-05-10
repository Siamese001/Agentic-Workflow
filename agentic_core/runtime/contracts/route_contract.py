"""Route Contract — AG-RGGOV-W6 Core Contract

Canonical dataclass for L0 routing output.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from agentic_core.runtime.contracts.posture import RuntimePosture, POSTURE_READ_ONLY
from typing import Any, Mapping, Optional


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

    # AG-2 (apps-rg-app-payload-consumption-wiring-b3a449): app_payload-derived
    # routing semantics. L0 reads L1PlanContract projections (task_spec /
    # support_expectation / output_expectation) and surfaces the routing
    # decisions explicitly so downstream consumers (PA, Exit, audit) don't
    # re-derive them. Defaults are conservative empty so non-apps_rg routers
    # are unaffected.
    #   - route_family: high-level taxonomy (e.g. "evidence_grounded_generation",
    #     "ungrounded_generation", "validation_only"); orthogonal to route_id
    #     which carries variant detail.
    #   - execution_form: "single_step" | "multi_turn" | "managed_workflow"
    #   - cache_eligibility: per-cache booleans — r1a_exact, r1b_semantic,
    #     r3_grounded, r4_action; default-False marks the conservative path.
    #   - action_required: route involves state mutation / R4 action path.
    route_family: str = ""
    execution_form: str = ""
    cache_eligibility: Mapping[str, bool] = field(default_factory=dict)
    action_required: bool = False

    # Routing metadata
    reason_codes: tuple[str, ...] = field(default_factory=tuple)
    routing_timestamp: str = ""
    schema_version: str = "W6.0"  # W5 P5.1: renamed from route_version (D8)
    # W4: observability + audit linkage (concern #9, D12=default-empty tuples)
    otel_span_refs: tuple[str, ...] = field(default_factory=tuple)
    audit_refs: tuple[str, ...] = field(default_factory=tuple)
    # W5 P5.2: HMAC-SHA256 integrity signature (D9, default-empty = unsigned)
    signature: str = ""
    # W6 P6.2: risk/side-effect posture (concern #7)
    posture: RuntimePosture = field(default_factory=lambda: POSTURE_READ_ONLY)
    # W6 P6.3: gate verdict refs (concern #3)
    gate_verdict_refs: tuple[str, ...] = field(default_factory=tuple)
    # W7 P7.1: replay/determinism (concern #4; D11=default-empty)
    replay_key: str = ""
    snapshot_refs: tuple[str, ...] = field(default_factory=tuple)
    l5_certification_ref: str = ""

    def __post_init__(self) -> None:
        from agentic_core.L5_safety.contracts.verify import verify_certification_ref
        if not verify_certification_ref(self.l5_certification_ref):
            raise ValueError(
                f"RouteContract: missing or invalid l5_certification_ref={self.l5_certification_ref!r} "
                "(AG-W0-5=fail_closed)"
            )
