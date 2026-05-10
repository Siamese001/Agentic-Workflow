"""Compiled Prompt Artifact — AG-RGGOV-W6 Core Contract

Canonical dataclass for Prompt Assembly output.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Optional

from agentic_core.runtime.contracts.origin import Origin, OriginTaggedContent


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
    assembly_version: str = "W6.0"

    # Model routing
    target_model: str = ""  # e.g., "Qwen/Qwen2.5-32B-Instruct-AWQ"
    target_provider: str = ""  # e.g., "vllm"

    # Provenance
    evidence_digest: str = ""  # References FinalEvidenceContract.compilation_hash
    compilation_hash: str = ""  # Digest of this artifact

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
    l5_certification_ref: str = ""

    def __post_init__(self) -> None:
        from agentic_core.L5_safety.contracts.verify import verify_certification_ref
        if not verify_certification_ref(self.l5_certification_ref):
            raise ValueError(
                f"CompiledPromptArtifact: missing or invalid l5_certification_ref={self.l5_certification_ref!r} "
                "(AG-W0-5=fail_closed)"
            )
