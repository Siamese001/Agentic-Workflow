"""
Core dataclasses for prompt assembly runtime.

Defines CompiledPromptArtifact with HMAC-SHA256 signing,
AuthoritySlot for the S0/I0/D0/C0/U0 taxonomy, and supporting types.
"""

import hashlib
import hmac
import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import Enum, auto
from typing import Any


class AuthorityLevel(Enum):
    """Authority gradient from ABSOLUTE (highest) to ZERO (lowest)."""

    ABSOLUTE = auto()  # S0 - Constitutions/Invariants (e.g., "Layer gravity")
    GOVERNED = auto()  # I0 - Identity/Mixins (e.g., HealMixin, ValidateMixin)
    BINDING = auto()  # D0 - Semantic Fences (e.g., "Max file: 10KB")
    INFO = auto()  # C0 - Grounding/RAG (e.g., AST snapshots)
    ZERO = auto()  # U0 - Raw Intent (e.g., "Fix module X")

    @classmethod
    def from_slot_code(cls, code: str) -> "AuthorityLevel":
        """Map slot code (S0, I0, D0, C0, U0) to AuthorityLevel."""
        mapping = {
            "S0": cls.ABSOLUTE,
            "I0": cls.GOVERNED,
            "D0": cls.BINDING,
            "C0": cls.INFO,
            "U0": cls.ZERO,
        }
        return mapping.get(code.upper(), cls.ZERO)


@dataclass(frozen=True)
class AuthoritySlot:
    """
    A single authority slot in the prompt assembly.

    Slots carry authority level but NOT route_mode, safety_threshold,
    execution_tier, or auth_token fields (per taxonomy invariant).
    """

    slot_type: str  # S0|I0|D0|C0|U0
    content: str
    authority_level: AuthorityLevel
    source_layer: str  # L0-L6 layer that provided this slot
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Validate slot_type matches authority_level
        expected_level = AuthorityLevel.from_slot_code(self.slot_type)
        if self.authority_level != expected_level:
            raise ValueError(
                f"Slot type {self.slot_type} does not match authority level {self.authority_level}"
            )
        # Security invariant: no routing/safety fields in C0/U0
        if self.slot_type in ("C0", "U0"):
            forbidden = ["route_mode", "safety_threshold", "execution_tier", "auth_token"]
            for key in forbidden:
                if key in self.metadata:
                    raise ValueError(f"Slot type {self.slot_type} cannot carry {key} per taxonomy invariant")

    @property
    def slot_code(self) -> str:
        """Return the slot code (S0, I0, etc.)."""
        return self.slot_type.upper()


@dataclass(frozen=True)
class CompiledPromptArtifact:
    """
    The final compiled prompt with HMAC-SHA256 signature.

    This is the output of SlotAssemblyEngine and input to SovereignLLMGateway.
    """

    trace_id: str
    system_version_hash: str
    final_system_string: str
    final_user_string: str
    allowed_tools_schema: list[dict[str, Any]]
    tokens: int
    slots_used: list[str]  # Ordered list of slot codes (should be S0,I0,D0,C0,U0)
    signature: str  # HMAC-SHA256 hex digest
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)

    # Core data contracts per taxonomy
    prompt_bom: dict[str, Any] = field(default_factory=dict)
    template_manifest: dict[str, Any] = field(default_factory=dict)
    injection_scan_result: dict[str, Any] | None = None
    routing_decision: dict[str, Any] | None = None

    def verify_signature(self, secret_key: bytes) -> bool:
        """Verify the HMAC-SHA256 signature of this artifact."""
        computed = self._compute_signature(secret_key)
        return hmac.compare_digest(computed, self.signature)

    def _compute_signature(self, secret_key: bytes) -> str:
        """Compute HMAC-SHA256 signature over artifact contents."""
        # Create deterministic payload (exclude signature itself)
        payload = {
            "trace_id": self.trace_id,
            "system_version_hash": self.system_version_hash,
            "final_system_string": self.final_system_string,
            "final_user_string": self.final_user_string,
            "allowed_tools_schema": self.allowed_tools_schema,
            "tokens": self.tokens,
            "slots_used": self.slots_used,
            "timestamp": self.timestamp,
        }
        payload_bytes = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
        return hmac.new(secret_key, payload_bytes, hashlib.sha256).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        """Serialize artifact to dictionary (for logging/telemetry)."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CompiledPromptArtifact":
        """Deserialize artifact from dictionary."""
        # Remove computed fields
        clean_data = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        return cls(**clean_data)


@dataclass
class PromptBOM:
    """
    Bill of Materials for prompt assembly.

    Captures inputs needed for slot assembly.
    """

    trace_id: str
    system_version_hash: str
    mixins_required: list[str]
    raw_u0: str  # Raw user intent (U0 slot content)
    raw_c0: str  # Context retrieved via RAG (C0 slot content)
    template_args: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TemplateManifest:
    """
    Manifest for a prompt template.

    Captures template metadata including version and required variables.
    """

    template_id: str
    version: str
    git_commit_hash: str
    required_variables: list[str]
    schema_version: str = "1.0"
    category: str = ""  # PromptCategory value
    authority_slot: str = ""  # S0|I0|D0|C0|U0

    def validate(self, provided_vars: dict[str, Any]) -> list[str]:
        """Validate that all required variables are provided."""
        missing = []
        for var in self.required_variables:
            if var not in provided_vars:
                missing.append(var)
        return missing


@dataclass
class RoutingDecision:
    """Routing decision from L0 classifier."""

    path: str  # A|B|C|D
    risk: str  # H|M|L|N (High/Med/Low/Novel)
    rationale: str
    confidence: float


@dataclass
class InjectionScanResult:
    """Result of concurrent injection scan during assembly."""

    detected: bool
    override_attempts: list[str]
    risk_score: float
    blocked: bool
