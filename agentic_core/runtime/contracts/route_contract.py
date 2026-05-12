"""Route Contract — AG-RGGOV-W6 Core Contract

Canonical dataclass for L0 routing output.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from agentic_core.runtime.contracts.posture import RuntimePosture, POSTURE_READ_ONLY
from typing import Any, Mapping, Optional, Tuple


@dataclass(frozen=True, slots=True)
class GraphTraversePolicy:
    """Generic graph traversal policy carried from L0 to C0.

    Populated by L0 when the selected route is a C0-grounded route (e.g. R3).
    Always None for terminal/cache routes (R1A, R1B hit, R5).

    Fields sourced from app-owned route profile ``graph_traverse:`` block.
    L0 does NOT call run_graph_traverse(); policy is forwarded to C0 for
    execution during the C0 grounding phase.

    W2: chroma-graphrag-core-wiring-gaps-b3f7a1
    """

    graph_expansion_allowed: bool = False
    max_hops: int = 0
    max_nodes: int = 0
    max_edges: int = 0
    allowed_relation_types: Tuple[str, ...] = field(default_factory=tuple)
    contradiction_scan_enabled: bool = False
    supersession_scan_enabled: bool = False
    graph_adapter_ref: str = ""
    live_wiring_deferred: bool = True
    wiring_gate: str = ""

    @property
    def is_active(self) -> bool:
        """True iff graph expansion is enabled and live wiring is not deferred."""
        return self.graph_expansion_allowed and not self.live_wiring_deferred


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

    # Managed workflow resolution (populated when execution_form="managed_workflow")
    workflow_ref: str = ""  # resolved workflow ID from registry; empty for single_step

    # W4: additional managed-workflow provenance fields (all default-empty for compat)
    workflow_manifest_ref: str = ""       # e.g. "wfm::apps_rg::resume_generation::v1"
    workflow_registry_ref: str = ""       # repo-relative path to the route_registry.yaml
    registry_resolution_receipt_ref: str = ""  # serialised WorkflowResolutionReceipt JSON

    # W4: route gate refs — G07/G08/G10/G20 placeholder refs (UNKNOWN when harness absent)
    route_gate_refs: tuple[str, ...] = field(default_factory=tuple)
    # W4: route policy ref — pointer to the route profile used
    route_policy_ref: str = ""

    # Cache lookup receipts (prove actual lookups completed before L3 entry)
    cache_lookup_r1a_receipt: str = ""  # serialized R1A lookup result (hit/miss + digest)
    cache_lookup_r1b_receipt: str = ""  # serialized R1B lookup result (hit/miss + digest)
    cache_lookup_r5_receipt: str = ""   # serialized R5 fallback result (hit/miss)

    # W4: aliased receipt fields (mirrors existing fields for explicit cache-read-order proof)
    r1a_lookup_receipt_ref: str = ""    # alias for cache_lookup_r1a_receipt
    r1b_lookup_receipt_ref: str = ""    # alias for cache_lookup_r1b_receipt
    r5_fallback_receipt_ref: str = ""   # alias for cache_lookup_r5_receipt

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
    # W2: graph traversal policy — populated for C0-grounded routes only (e.g. R3).
    # Terminal/cache routes (R1A, R1B hit, R5) MUST carry None.
    # L0 reads graph_traverse block from app route profile; does NOT call run_graph_traverse().
    # chroma-graphrag-core-wiring-gaps-b3f7a1 W2
    graph_traverse_policy: Optional["GraphTraversePolicy"] = None

    def __post_init__(self) -> None:
        from agentic_core.L5_safety.contracts.verify import verify_certification_ref
        if not verify_certification_ref(self.l5_certification_ref):
            raise ValueError(
                f"RouteContract: missing or invalid l5_certification_ref={self.l5_certification_ref!r} "
                "(AG-W0-5=fail_closed)"
            )
