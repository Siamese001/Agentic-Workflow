"""L1 Plan Contract — AG-RGGOV-W6 Core Contract

Canonical dataclass for L1 planning output.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from agentic_core.runtime.contracts.posture import RuntimePosture, POSTURE_READ_ONLY


@dataclass(frozen=True, slots=True)
class L1PlanContract:
    """L1 planning output contract.

    Contains planning decisions, routing requirements, and execution prerequisites.
    """

    request_id: str
    run_id: str
    app_id: str
    trace_id: str

    # Planning decisions
    task_plan: tuple[str, ...] = field(default_factory=tuple)
    required_capabilities: tuple[str, ...] = field(default_factory=tuple)

    # Execution prerequisites (determine routing)
    grounding_required: bool = False  # C0 evidence collection needed
    model_generation_required: bool = False  # L2 model execution needed
    write_authority_present: bool = False  # State modification required

    # Identity extension
    tenant_id: str = ""  # W1: threaded from U0 ValidatedRequest.tenant_id (D6)

    # Profile binding
    profile_manifest_digest: str = ""

    # W2: target level for L0 variant routing (DS-3 executive vs default)
    target_level: str = ""  # "SENIOR" | "STAFF" | "EXECUTIVE" | ""

    # Receipt
    planning_timestamp: str = ""
    schema_version: str = "W6.0"  # W5 P5.1: renamed from plan_version (D8)
    # W4: observability + audit linkage (concern #9, D12=default-empty tuples)
    otel_span_refs: tuple[str, ...] = field(default_factory=tuple)
    audit_refs: tuple[str, ...] = field(default_factory=tuple)
    # W5 P5.2: HMAC-SHA256 integrity signature (D9, default-empty = unsigned)
    signature: str = ""
    # W6 P6.2: risk/side-effect posture (concern #7, D7=RuntimePosture struct)
    posture: RuntimePosture = field(default_factory=lambda: POSTURE_READ_ONLY)
    # W6 P6.3: gate verdict refs (concern #3, reuse CommitRequest shape)
    gate_verdict_refs: tuple[str, ...] = field(default_factory=tuple)
    # W7 P7.1: replay/determinism (concern #4; D11=default-empty)
    replay_key: str = ""
    snapshot_refs: tuple[str, ...] = field(default_factory=tuple)
    l5_certification_ref: str = ""

    def __post_init__(self) -> None:
        from agentic_core.L5_safety.contracts.verify import verify_certification_ref
        if not verify_certification_ref(self.l5_certification_ref):
            raise ValueError(
                f"L1PlanContract: missing or invalid l5_certification_ref={self.l5_certification_ref!r} "
                "(AG-W0-5=fail_closed)"
            )
