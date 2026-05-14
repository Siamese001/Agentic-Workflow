# apps_rg Prompt Assembly Contracts
# Typed artifacts for local compile/validation path
# NO agentic_core imports — self-contained for apps_rg local use

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Optional


class SlotAuthority(Enum):
    """Authority classes per ADR-023 8-slot model."""
    SYSTEM_AUTHORITY = auto()           # S0 - Immutable governance
    BINDING_AUTHORITY = auto()          # D0 - Security fences
    GOVERNED_AUTHORITY = auto()         # I0 - Domain instructions
    EXAMPLE_AUTHORITY = auto()          # E0 - Approved examples
    INFORMATIONAL_AUTHORITY = auto()    # C0 - Evidence data
    PROVIDER_RENDER_CONTROL = auto()    # M0 - Model/token control
    ZERO_AUTHORITY = auto()             # U0 - User intent only
    REPAIR_HINTS = auto()              # H0 - Healing guidance
    SCHEMA_AUTHORITY = auto()           # R0 - Output contract
    STYLE_AUTHORITY = auto()            # Y0 - Synthesis preferences


class SlotName(Enum):
    """Canonical slot identifiers."""
    S0 = "S0_SYSTEM_PREAMBLE"
    D0 = "D0_ORIGIN_BOUNDARY"
    I0 = "I0_INSTRUCTIONS"
    E0 = "E0_APPROVED_EXAMPLES"
    C0 = "C0_EVIDENCE_DATA"
    M0 = "M0_PROVIDER_CONTROL"
    U0 = "U0_USER_TASK"
    H0 = "H0_HEALING_PROPOSAL"
    R0 = "R0_RESPONSE_SCHEMA"
    Y0 = "Y0_STYLE_PREFERENCES"


# Authority ordering: higher authority MUST precede lower in compiled prompt
AUTHORITY_PRECEDENCE: dict[SlotAuthority, int] = {
    SlotAuthority.SYSTEM_AUTHORITY: 10,      # S0
    SlotAuthority.BINDING_AUTHORITY: 9,    # D0
    SlotAuthority.GOVERNED_AUTHORITY: 8,   # I0
    SlotAuthority.INFORMATIONAL_AUTHORITY: 7,  # C0
    SlotAuthority.EXAMPLE_AUTHORITY: 6,    # E0
    SlotAuthority.STYLE_AUTHORITY: 5,      # Y0
    SlotAuthority.ZERO_AUTHORITY: 4,         # U0
    SlotAuthority.REPAIR_HINTS: 3,           # H0
    SlotAuthority.PROVIDER_RENDER_CONTROL: 2,  # M0
    SlotAuthority.SCHEMA_AUTHORITY: 1,     # R0
}


@dataclass
class PromptAssemblyError(Exception):
    """Fail-closed error for PA validation/compilation failures."""
    code: str
    message: str
    slot_id: Optional[str] = None
    context: dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        base = f"[{self.code}] {self.message}"
        if self.slot_id:
            base += f" (slot={self.slot_id})"
        return base


@dataclass(frozen=True)
class PromptSlotPayload:
    """Individual slot content with provenance."""
    slot_id: str  # S0, I0, C0, etc.
    slot_name: str
    authority_class: SlotAuthority
    content: str
    content_hash: str
    source_tag: Optional[str] = None  # e.g., <candidate_facts>
    
    def __post_init__(self):
        # Validate hash matches content
        computed = hashlib.sha256(self.content.encode()).hexdigest()[:16]
        if computed != self.content_hash:
            raise PromptAssemblyError(
                code="HASH_MISMATCH",
                message=f"Content hash mismatch: expected {computed}, got {self.content_hash}",
                slot_id=self.slot_id
            )


@dataclass
class EvidenceSource:
    """C0 source-separated evidence container."""
    source_type: str  # candidate_facts, jd_requirements, company_brief, alignment_map
    content: str
    confidence: float = 1.0
    source_tag: str = ""  # XML-style tag for fencing
    
    def to_tagged(self) -> str:
        """Render as tagged content block."""
        tag = self.source_tag or f"{self.source_type}"
        return f"<{tag} confidence=\"{self.confidence}\">\n{self.content}\n</{tag}>"


@dataclass
class PromptAssemblyInput:
    """Input to PA compilation — all slots populated from external sources."""
    # Required identification
    template_id: str
    request_id: str
    run_id: str
    trace_root: str
    
    # Required slots
    s0_system_preamble: str
    i0_instructions: str
    c0_candidate_facts: EvidenceSource
    c0_jd_requirements: EvidenceSource
    u0_user_task: str
    r0_response_schema: str  # JSON schema content or ref
    
    # Render context
    render_context: dict[str, Any] = field(default_factory=dict)
    
    # Optional slots
    d0_fences: Optional[str] = None
    e0_examples: Optional[str] = None
    y0_style_preferences: Optional[str] = None
    h0_healing_hints: Optional[str] = None
    m0_provider_control: Optional[str] = None
    
    # Additional C0 sources
    c0_company_brief: Optional[EvidenceSource] = None
    c0_alignment_map: Optional[EvidenceSource] = None
    
    # Compilation metadata
    target_role: str = ""
    target_company: str = ""
    seniority_band: str = ""
    
    def __post_init__(self):
        # Validate S0 contains no-fabrication oath
        if "NO FABRICATION" not in self.s0_system_preamble:
            raise PromptAssemblyError(
                code="MISSING_NO_FABRICATION_OATH",
                message="S0 must contain explicit NO FABRICATION oath",
                slot_id="S0"
            )
        
        # Validate C0 sources are separated
        if not self.c0_candidate_facts.source_tag:
            raise PromptAssemblyError(
                code="C0_MISSING_SOURCE_TAG",
                message="candidate_facts must have source_tag",
                slot_id="C0"
            )
        if not self.c0_jd_requirements.source_tag:
            raise PromptAssemblyError(
                code="C0_MISSING_SOURCE_TAG",
                message="jd_requirements must have source_tag",
                slot_id="C0"
            )


@dataclass
class ComponentHashMap:
    """Deterministic hash of each slot for replay/verification."""
    s0_hash: str
    i0_hash: str
    c0_candidate_hash: str
    c0_jd_hash: str
    u0_hash: str
    r0_hash: str
    d0_hash: Optional[str] = None
    e0_hash: Optional[str] = None
    y0_hash: Optional[str] = None
    template_hash: str = ""
    
    def to_dict(self) -> dict[str, str]:
        """Convert to dictionary for serialization."""
        result = {
            "S0": self.s0_hash,
            "I0": self.i0_hash,
            "C0_candidate": self.c0_candidate_hash,
            "C0_jd": self.c0_jd_hash,
            "U0": self.u0_hash,
            "R0": self.r0_hash,
            "template": self.template_hash,
        }
        if self.d0_hash:
            result["D0"] = self.d0_hash
        if self.e0_hash:
            result["E0"] = self.e0_hash
        if self.y0_hash:
            result["Y0"] = self.y0_hash
        return result


@dataclass
class CompiledPromptArtifact:
    """Ready-to-render PA artifact with full provenance."""
    # Content
    messages: list[dict[str, str]] = field(default_factory=list)  # [{"role": "system", "content": ...}]
    system_prompt: str = ""  # Full compiled S0+D0+I0+...
    
    # Slot ordering and payloads
    canonical_slot_order: list[str] = field(default_factory=list)
    slot_payloads: list[PromptSlotPayload] = field(default_factory=list)
    slot_lineage_map: dict[str, str] = field(default_factory=dict)
    
    # Provenance
    template_id: str = ""
    template_version: str = ""
    component_hash_map: ComponentHashMap = field(default_factory=lambda: ComponentHashMap(
        s0_hash="", i0_hash="", c0_candidate_hash="", c0_jd_hash="", u0_hash="", r0_hash=""
    ))
    prompt_hash: str = ""  # SHA256 of canonical serialized form
    
    # Schema and render manifests
    response_schema_ref: str = ""  # R0 schema reference
    provider_render_manifest: dict[str, Any] = field(default_factory=dict)
    replay_manifest: dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    compiled_at: datetime = field(default_factory=datetime.utcnow)
    slot_count: int = 0
    token_estimate: int = 0
    
    # Validation flags
    has_no_fabrication_oath: bool = False
    has_source_separation: bool = False
    has_schema_reference: bool = False
    
    def to_json(self) -> str:
        """Serialize to canonical JSON for hash verification."""
        data = {
            "template_id": self.template_id,
            "template_version": self.template_version,
            "component_hash_map": self.component_hash_map.to_dict(),
            "system_prompt": self.system_prompt,
            "slot_count": self.slot_count,
        }
        return json.dumps(data, sort_keys=True, separators=(',', ':'))
    
    def verify_hash(self) -> bool:
        """Verify prompt_hash matches recomputed hash."""
        computed = hashlib.sha256(self.to_json().encode()).hexdigest()[:32]
        return computed == self.prompt_hash
