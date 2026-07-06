"""Sealed L2 Artifact — AG-RGGOV-W6 Core Contract

Canonical dataclass for L2 execution output.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from agentic_core.runtime.contracts.origin import Origin
from agentic_core.runtime.contracts.posture import RuntimePosture, POSTURE_WRITE_INTENT


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
    # W6 P6.2: risk/side-effect posture (concern #7; L2 may write via UWG)
    posture: RuntimePosture = field(default_factory=lambda: POSTURE_WRITE_INTENT)
    # W6 P6.3: gate verdict refs (concern #3)
    gate_verdict_refs: tuple[str, ...] = field(default_factory=tuple)
    # W7 P7.1: replay/determinism (concern #4; D11=default-empty)
    replay_key: str = ""
    snapshot_refs: tuple[str, ...] = field(default_factory=tuple)
    # W8 P8.1: write/learning firewall (concern #10; default False — gateway enforces)
    is_uwg_write_authority: bool = False
    is_future_run_only: bool = False
    l5_certification_ref: str = ""
    l5_certification_packet_ref: str = ""
    l5_certification_packet_digest: str = ""
    l5_certification_status: str = ""
    l5_egress_receipt_refs: tuple[str, ...] = field(default_factory=tuple)
    l5_egress_receipt_digests: tuple[str, ...] = field(default_factory=tuple)
    l5_egress_receipts: tuple[Any, ...] = field(default_factory=tuple)

    # ====================================================================
    # AG-4 W7: opaque-ref carrier fields preserved through L2 seal.
    # All additive with safe defaults so pre-AG-4 callers compile unchanged.
    # Plan: ag4-evidence-contract-carrier-repair-d2f9a3
    # ====================================================================

    #: Refs to evidence rows L2 consumed (forwarded from PA's
    #: ``component_hash_map`` so Exit can verify provenance without
    #: re-reading the FEC).
    evidence_refs: tuple[str, ...] = field(default_factory=tuple)
    #: Refs to PA prompt rows the seal covers (compiled prompt + slot
    #: lineage + replay manifest pointer).
    prompt_refs: tuple[str, ...] = field(default_factory=tuple)
    #: Refs to tool-call receipts produced during L2 execution.
    tool_call_refs: tuple[str, ...] = field(default_factory=tuple)
    #: Refs to model-call receipts produced during L2 execution.
    model_call_refs: tuple[str, ...] = field(default_factory=tuple)
    #: Provider receipts (vLLM / OpenAI / Anthropic / …).
    provider_receipts: tuple[str, ...] = field(default_factory=tuple)
    #: Pointer to the replay manifest record (per-run determinism receipts).
    replay_manifest: str = ""
    #: Pointer to the audit manifest record covering this seal.
    audit_manifest_ref: str = ""

    # Provenance

    def __post_init__(self) -> None:
        from agentic_core.L5_safety.contracts.verify import verify_certification_ref
        if not verify_certification_ref(self.l5_certification_ref):
            raise ValueError(
                f"SealedL2Artifact: missing or invalid l5_certification_ref={self.l5_certification_ref!r} "
                "(AG-W0-5=fail_closed)"
            )
