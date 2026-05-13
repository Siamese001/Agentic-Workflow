"""Compiled Prompt Artifact — AG-RGGOV-W6 Core Contract

Canonical dataclass for Prompt Assembly output.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Optional

from agentic_core.runtime.contracts.origin import Origin, OriginTaggedContent
from agentic_core.runtime.contracts.posture import RuntimePosture, POSTURE_GENERATION


@dataclass(frozen=True, slots=True)
class PromptBlock:
    """Single prompt block with role and content."""

    role: str  # system, user, assistant
    content: str
    block_index: int = 0
    # W3 P3.2: origin/data-boundary tagging (concern #6, D7=Origin enum)
    # user blocks carry USER_INTENT; system blocks are SYSTEM_INTERNAL
    origin: Origin = Origin.SYSTEM_INTERNAL


@dataclass(frozen=True, slots=True)
class CompiledPromptArtifact:
    """Prompt assembly output contract.

    Contains compiled prompt for L2 execution.
    """

    request_id: str
    run_id: str
    app_id: str
    trace_id: str

    # Compiled prompt
    prompt_blocks: tuple[PromptBlock, ...] = field(default_factory=tuple)
    system_preamble: str = ""
    user_instruction: str = ""

    # Assembly metadata
    assembly_timestamp: str = ""
    schema_version: str = "W6.0"  # W5 P5.1: renamed from assembly_version (D8)

    # Model routing
    target_model: str = ""  # e.g., "Qwen/Qwen2.5-32B-Instruct-AWQ"
    target_provider: str = ""  # e.g., "vllm"

    # Provenance
    evidence_digest: str = ""  # References FinalEvidenceContract.compilation_hash
    compilation_hash: str = ""  # Digest of this artifact (== prompt_hash)

    # AG-2 (apps-rg-app-payload-consumption-wiring-b3a449): prompt-envelope
    # provenance — slot lineage, per-component hashes, and replay manifest.
    # Defaults are empty so non-apps_rg PA producers are unaffected.
    #   - slot_lineage_map: per-block lineage (e.g. {"system": "PA-authored",
    #     "user": "USER_INTENT|EVIDENCE", "evidence": "C0:fec.compilation_hash"})
    #   - component_hash_map: per-component sha256 (style_profile, evidence,
    #     l1_plan, app_payload, route)
    #   - replay_manifest_ref: pointer to the replay key + snapshot tuple that
    #     reproduces this prompt deterministically
    slot_lineage_map: Mapping[str, str] = field(default_factory=dict)
    component_hash_map: Mapping[str, str] = field(default_factory=dict)
    replay_manifest_ref: str = ""

    # Per-input hash map — distinct SHA-256 digests keyed by input name.
    # Populated by apps_rg PA binding from ValidatedRequest.app_payload so
    # Exit G24 can use real per-input hashes instead of an aggregate digest.
    # Keys used by apps_rg: "jd_hash", "resume_hash", "target_role_spec_hash".
    # Default empty dict — non-apps_rg producers are unaffected.
    per_input_hash_map: Mapping[str, str] = field(default_factory=dict)

    # Identity extension
    tenant_id: str = ""  # W1: threaded from FinalEvidenceContract.tenant_id (D6)

    # W2: Capability / sandbox / egress allowlists (concern #8, D11=default-empty)
    sandbox_required: bool = False
    egress_policy_ref: str = ""
    allowed_tools: tuple[str, ...] = field(default_factory=tuple)
    allowed_models: tuple[str, ...] = field(default_factory=tuple)
    allowed_networks: tuple[str, ...] = field(default_factory=tuple)
    allowed_file_roots: tuple[str, ...] = field(default_factory=tuple)

    # Constraints
    max_tokens: int = 4096
    temperature: float = 0.7
    # W4: observability + audit linkage (concern #9, D12=default-empty tuples)
    otel_span_refs: tuple[str, ...] = field(default_factory=tuple)
    audit_refs: tuple[str, ...] = field(default_factory=tuple)
    # W5 P5.2: HMAC-SHA256 integrity signature (D9, default-empty = unsigned)
    signature: str = ""
    # W6 P6.2: risk/side-effect posture (concern #7; generation = external_call)
    posture: RuntimePosture = field(default_factory=lambda: POSTURE_GENERATION)
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
                f"CompiledPromptArtifact: missing or invalid l5_certification_ref={self.l5_certification_ref!r} "
                "(AG-W0-5=fail_closed)"
            )
