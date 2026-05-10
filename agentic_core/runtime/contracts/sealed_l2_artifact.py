"""Sealed L2 Artifact — AG-RGGOV-W6 Core Contract

Canonical dataclass for L2 execution output.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Optional

from agentic_core.runtime.contracts.origin import Origin, OriginTaggedContent


@dataclass(frozen=True, slots=True)
class SealedL2Artifact:
    """L2 execution output contract.

    Contains generated content and execution metadata.
    """

    request_id: str
    run_id: str
    app_id: str
    trace_id: str

    # Execution status
    execution_status: str  # completed, failed, aborted

    # Generated content
    generated_content: str = ""
    # W3 P3.2: origin of generated_content (concern #6, D7=Origin enum)
    # MODEL_GENERATION until HITL-cleared; then HUMAN_REVIEW_DATA
    generated_content_origin: Origin = Origin.MODEL_GENERATION

    # State diff (for apps_rg: resume artifact)
    proposed_state_diff: Mapping[str, Any] = field(default_factory=dict)
    state_diff_authorized: bool = False

    # Execution metadata
    execution_timestamp: str = ""
    execution_duration_ms: int = 0
    sovereign_execution_receipt: str = ""

    # Identity extension
    tenant_id: str = ""  # W1: threaded from CompiledPromptArtifact.tenant_id (D6)

    # W2: Capability / sandbox / egress allowlists (concern #8, D11=default-empty)
    sandbox_required: bool = False
    egress_policy_ref: str = ""
    allowed_tools: tuple[str, ...] = field(default_factory=tuple)
    allowed_models: tuple[str, ...] = field(default_factory=tuple)
    allowed_networks: tuple[str, ...] = field(default_factory=tuple)
    allowed_file_roots: tuple[str, ...] = field(default_factory=tuple)

    # Digest for downstream referencing
    prompt_artifact_digest: str = ""
    schema_version: str = "W6.0"  # W5 P5.1: renamed from contract_version (D8)

    # Digest for downstream referencing
    compilation_hash: str = ""
    # W4: observability + audit linkage (concern #9, D12=default-empty tuples)
    otel_span_refs: tuple[str, ...] = field(default_factory=tuple)
    audit_refs: tuple[str, ...] = field(default_factory=tuple)
    # W5 P5.2: HMAC-SHA256 integrity signature (D9, default-empty = unsigned)
    signature: str = ""
    l5_certification_ref: str = ""

    # Provenance

    def __post_init__(self) -> None:
        from agentic_core.L5_safety.contracts.verify import verify_certification_ref
        if not verify_certification_ref(self.l5_certification_ref):
            raise ValueError(
                f"SealedL2Artifact: missing or invalid l5_certification_ref={self.l5_certification_ref!r} "
                "(AG-W0-5=fail_closed)"
            )
