"""X3 Disposition — AG-RGGOV-W6 Core Contract

Canonical dataclass for Exit stage output.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Optional

from agentic_core.runtime.contracts.posture import RuntimePosture, POSTURE_WRITE_INTENT


@dataclass(frozen=True, slots=True)
class X3Disposition:
    """Exit disposition contract.

    Final output of the core consumption pipeline.
    Exactly one X3Disposition is emitted per request.
    """

    request_id: str
    run_id: str
    app_id: str
    trace_id: str

    # Disposition
    exit_status: str  # success, failure, abstain, error
    outcome_authorized: bool = False

    # Output
    final_output: Mapping[str, Any] = field(default_factory=dict)
    output_artifact_path: Optional[str] = None

    # Evaluation
    eval_score: Optional[float] = None
    eval_threshold_met: bool = False
    hitl_required: bool = False

    # Identity extension
    tenant_id: str = ""  # W1: threaded from SealedL2Artifact.tenant_id (D6)

    # Metadata
    exit_timestamp: str = ""
    schema_version: str = "W6.0"  # W5 P5.1: renamed from disposition_version (D8)

    # Chain provenance
    sealed_l2_digest: str = ""  # References SealedL2Artifact.compilation_hash

    # W4: observability + audit linkage (concern #9, D12=default-empty tuples)
    otel_span_refs: tuple[str, ...] = field(default_factory=tuple)
    audit_refs: tuple[str, ...] = field(default_factory=tuple)
    # W5 P5.2: HMAC-SHA256 integrity signature (D9, default-empty = unsigned)
    signature: str = ""
    # W6 P6.2: risk/side-effect posture (concern #7; exit may commit via UWG)
    posture: RuntimePosture = field(default_factory=lambda: POSTURE_WRITE_INTENT)
    # W6 P6.3: gate verdict refs (concern #3)
    gate_verdict_refs: tuple[str, ...] = field(default_factory=tuple)
    # W7 P7.1: replay/determinism (concern #4; D11=default-empty)
    replay_key: str = ""
    snapshot_refs: tuple[str, ...] = field(default_factory=tuple)
    # W8 P8.1: write/learning firewall (concern #10; default False — gateway enforces)
    is_uwg_write_authority: bool = False
    is_future_run_only: bool = False
    # W9 P9.1: L5 certification ref (concern #2; fail_closed per AG-W0-5)
    l5_certification_ref: str = ""

    def __post_init__(self) -> None:
        from agentic_core.L5_safety.contracts.verify import verify_certification_ref
        if not verify_certification_ref(self.l5_certification_ref):
            raise ValueError(
                f"X3Disposition: missing or invalid l5_certification_ref={self.l5_certification_ref!r} "
                "(AG-W0-5=fail_closed)"
            )
