"""X3 Disposition — AG-RGGOV-W6 Core Contract

Canonical dataclass for Exit stage output.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Optional


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
    disposition_version: str = "W6.0"

    # Chain provenance
    sealed_l2_digest: str = ""  # References SealedL2Artifact.compilation_hash

    # W4: observability + audit linkage (concern #9, D12=default-empty tuples)
    otel_span_refs: tuple[str, ...] = field(default_factory=tuple)
    audit_refs: tuple[str, ...] = field(default_factory=tuple)
