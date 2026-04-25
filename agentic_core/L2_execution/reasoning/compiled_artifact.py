"""
Core dataclasses for prompt assembly runtime.

Defines CompiledPromptArtifact with HMAC-SHA256 signing,
AuthoritySlot for the S0/I0/D0/C0/U0 taxonomy, and supporting types.
"""

import hashlib
import hmac
import json
import logging
import os
import uuid
from dataclasses import asdict, dataclass, field
from datetime import UTC, date, datetime
from enum import Enum, auto
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from agentic_core.L2_execution.reasoning.prompt_messages import PromptMessages


_LOG = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# EQ-6 — replay-verifier shim hardening (ADR-PROMPT-ASSEMBLY-002 §9).
#
# The v1 (pre-EQ1) HMAC scheme excludes ``idempotency_nonce``. ``EQ-1`` shipped
# the v2 scheme + a verify-time shim that accepts both. EQ-6 adds:
#
#   1. **Sunset enforcement** — after ``_SHIM_SUNSET_DATE`` the v1 path is
#      disabled at runtime. Old artifacts must be re-signed by then.
#   2. **Deprecation telemetry** — a counter ``_v1_verifications`` plus a
#      one-shot warning per process so we can monitor remaining v1 traffic
#      without log spam.
#   3. **Schema classifier** — :func:`classify_artifact_dict` reports
#      ``1`` or ``2`` from a serialized artifact dict so replay tooling
#      can route without first instantiating the dataclass.
#   4. **Override hook** — the ``EQ6_SHIM_FORCE_ACTIVE=1`` env var keeps
#      the shim active past the sunset date (incident escape hatch only).
# ---------------------------------------------------------------------------

_SHIM_SUNSET_DATE = date(2026, 7, 23)
_SHIM_OVERRIDE_ENV = "EQ6_SHIM_FORCE_ACTIVE"


def _shim_active(today: date | None = None) -> bool:
    """Return True iff the v1 verification shim is still honored.

    The shim auto-retires on ``_SHIM_SUNSET_DATE``. Setting
    ``EQ6_SHIM_FORCE_ACTIVE=1`` keeps it active past sunset (intended only
    for break-glass incident response, never as a steady state).
    """
    if os.getenv(_SHIM_OVERRIDE_ENV, "").lower() in {"1", "true", "yes", "on"}:
        return True
    return (today or datetime.now(UTC).date()) < _SHIM_SUNSET_DATE


# Mutable counter for EQ-6 telemetry. Reset by tests via the helper below.
_v1_verifications: int = 0
_v1_warning_emitted: bool = False


def _record_v1_verification() -> None:
    """Bump the v1 telemetry counter and emit a one-shot deprecation log."""
    global _v1_verifications, _v1_warning_emitted
    _v1_verifications += 1
    if not _v1_warning_emitted:
        _LOG.warning(
            "CompiledPromptArtifact v1 signature shim active (sunset=%s). "
            "Re-sign artifacts with v2 before sunset to retain verifiability.",
            _SHIM_SUNSET_DATE.isoformat(),
        )
        _v1_warning_emitted = True


def get_v1_verification_count() -> int:
    """Return how many v1-signature verifications have happened this process."""
    return _v1_verifications


def reset_v1_verification_count() -> None:
    """Reset the v1 telemetry counter (test helper, not for production use)."""
    global _v1_verifications, _v1_warning_emitted
    _v1_verifications = 0
    _v1_warning_emitted = False


def classify_artifact_dict(artifact_dict: dict[str, Any]) -> int:
    """Classify a serialized artifact dict as schema v1 or v2.

    Reports ``2`` when the dict carries an ``idempotency_nonce`` OR an
    explicit ``schema_version >= 2``. Reports ``1`` otherwise. Use this
    helper from replay tooling to pick the right verification path
    without round-tripping through the dataclass constructor.
    """
    declared = artifact_dict.get("schema_version")
    if isinstance(declared, int) and declared >= 2:
        return 2
    if "idempotency_nonce" in artifact_dict and artifact_dict["idempotency_nonce"]:
        return 2
    return 1


class AuthorityLevel(Enum):
    """Authority gradient from ABSOLUTE (highest) to ZERO (lowest).

    Extended in W3 with three informational slots between grounding (C0) and
    raw intent (U0):
      EXEMPLAR       E0 — few-shot examples (Anthropic/OpenAI best practice)
      META_COGNITIVE M0 — thinking-approach guidance (chain-of-thought, o1-style)
      HEALING        H0 — recovery / re-entry context after failure
    All three carry INFO-equivalent authority — lower than BINDING (D0) but
    higher than raw user intent (U0).
    """

    ABSOLUTE = auto()  # S0 - Constitutions/Invariants (e.g., "Layer gravity")
    GOVERNED = auto()  # I0 - Identity/Mixins (e.g., HealMixin, ValidateMixin)
    BINDING = auto()  # D0 - Semantic Fences (e.g., "Max file: 10KB")
    INFO = auto()  # C0 - Grounding/RAG (e.g., AST snapshots)
    EXEMPLAR = auto()  # E0 - Few-shot examples
    META_COGNITIVE = auto()  # M0 - Thinking-approach / CoT guidance
    HEALING = auto()  # H0 - Recovery / re-entry context
    META_LEARNING = auto()  # Y0 - Meta-learning adjustments (EQ-17)
    SCHEMA = auto()  # R0 - Output format / response schema constraints
    ZERO = auto()  # U0 - Raw Intent (e.g., "Fix module X")

    @classmethod
    def from_slot_code(cls, code: str) -> "AuthorityLevel":
        """Map slot code (S0, I0, D0, C0, E0, M0, H0, Y0, U0) to AuthorityLevel."""
        mapping = {
            "S0": cls.ABSOLUTE,
            "I0": cls.GOVERNED,
            "D0": cls.BINDING,
            "C0": cls.INFO,
            "Y0": cls.META_LEARNING,
            "E0": cls.EXEMPLAR,
            "M0": cls.META_COGNITIVE,
            "H0": cls.HEALING,
            "R0": cls.SCHEMA,
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
                f"Slot type {self.slot_type} does not match authority level {self.authority_level}",
            )
        # Security invariant: no routing/safety fields in C0/U0/E0/M0/H0/Y0 (all informational).
        if self.slot_type in ("C0", "U0", "E0", "M0", "H0", "Y0", "R0"):
            forbidden = ["route_mode", "safety_threshold", "execution_tier", "auth_token"]
            for key in forbidden:
                if key in self.metadata:
                    raise ValueError(f"Slot type {self.slot_type} cannot carry {key} per taxonomy invariant")

    @property
    def slot_code(self) -> str:
        """Return the slot code (S0, I0, etc.)."""
        return self.slot_type.upper()


def _canonicalize_structured_slots(
    slots: dict[str, "AuthoritySlot"],
) -> dict[str, dict[str, Any]]:
    """Render ``structured_slots`` into a hash-stable canonical dict.

    EQ-1 helper. Keys are slot codes upper-cased and sorted. Each value is a
    dict with ``content``, ``authority_level`` (enum name), ``source_layer``,
    and sorted ``metadata`` pairs. ``AuthoritySlot`` is already frozen, so
    mutation after artifact construction is impossible; this helper just
    guarantees a canonical serialization shape for ``json.dumps``.
    """
    canonical: dict[str, dict[str, Any]] = {}
    for code in sorted(slots):
        slot = slots[code]
        canonical[code.upper()] = {
            "content": slot.content,
            "authority_level": slot.authority_level.name,
            "source_layer": slot.source_layer,
            "metadata": dict(sorted(slot.metadata.items())),
        }
    return canonical


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

    # EQ-1 (ADR-PROMPT-ASSEMBLY-002 §9, §10): idempotency nonce and
    # structured-slot carrier. ``idempotency_nonce`` is excluded from
    # ``manifest_hash`` but INCLUDED in HMAC signature inputs, so two
    # dispatches with identical logical content produce identical
    # ``manifest_hash`` but distinct signatures — letting the gateway
    # distinguish a legitimate retry from a replay/forgery attempt.
    # ``structured_slots`` lets provider adapters render per-vendor without
    # re-parsing the flattened strings; unset means legacy flat-only path.
    # ``schema_version`` gates the HMAC scheme: v2 includes the nonce,
    # v1 (pre-EQ1) does not. The ``verify_signature`` shim accepts both
    # during the 90-day back-compat window (sunset 2026-07-23).
    idempotency_nonce: str = field(default_factory=lambda: uuid.uuid4().hex)
    structured_slots: dict[str, "AuthoritySlot"] | None = None
    schema_version: int = 2
    # EQ-5 (ADR-PROMPT-ASSEMBLY-001 Q4): optional JSON Schema describing
    # the desired response shape. Threaded through to provider adapters via
    # ``SovereignLLMGateway`` -> ``ProviderMessageAdapter.render`` and
    # surfaced on ``ProviderPayload.extra`` in provider-idiomatic form.
    # Defaults to None (no structured output forced). Intentionally NOT
    # part of the HMAC signature: response_schema is request metadata, not
    # prompt content, and must not change the artifact's manifest_hash.
    response_schema: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        """Validate artifact invariants on construction.

        Restored in PRF1.A1 (plan ``prompt-reception-followups-a7b3c4``)
        after the RH2B.2 narrow→rich SSOT merge (commit ``09a47e9ea7``)
        dropped the pre-merge validators. These two checks protect
        downstream consumers (``SovereignLLMGateway``, telemetry sinks,
        replay-key derivers) that treat ``trace_id`` as non-empty and
        ``tokens`` as non-negative.
        """
        if not self.trace_id:
            raise ValueError("trace_id must not be empty")
        if self.tokens < 0:
            raise ValueError(f"tokens must be >= 0, got {self.tokens}")

    @property
    def manifest_hash(self) -> str:
        """SHA-256 over canonical slot payload. EXCLUDES ``idempotency_nonce``.

        Two artifacts with identical logical content but different nonces
        share the same ``manifest_hash`` — this is the property the gateway
        uses to detect retries vs. fresh requests. Inclusion of
        ``schema_version`` means v1 and v2 artifacts with otherwise-identical
        content get distinct hashes, preventing silent cross-version cache
        collisions during the shim window.

        Introduced in EQ-1 (ADR-PROMPT-ASSEMBLY-002 §9). When
        ``structured_slots`` is set, the hash is taken over the canonicalized
        slot map; otherwise it falls back to hashing the flat strings for
        back-compat.
        """
        if self.structured_slots is not None:
            slots_payload: Any = _canonicalize_structured_slots(self.structured_slots)
        else:
            slots_payload = {
                "flat_system": self.final_system_string,
                "flat_user": self.final_user_string,
            }
        payload = {
            "trace_id": self.trace_id,
            "system_version_hash": self.system_version_hash,
            "slots": slots_payload,
            "allowed_tools_schema": self.allowed_tools_schema,
            # EQ-9 (ADR-PROMPT-ASSEMBLY-002 §10): sort slots_used so
            # manifest_hash is invariant under insertion order of the
            # structured_slots dict. json.dumps(sort_keys=True) only
            # sorts dict keys, not list elements, so without this sort
            # the hash would leak the caller's dict construction order.
            "slots_used": sorted(self.slots_used),
            "schema_version": self.schema_version,
        }
        payload_bytes = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
        return hashlib.sha256(payload_bytes).hexdigest()

    def verify_signature(self, secret_key: bytes) -> bool:
        """Verify the HMAC-SHA256 signature of this artifact.

        Accepts both v2 (EQ-1, nonce-bearing) and v1 (pre-EQ1, legacy)
        signatures during the 90-day shim window. EQ-6 adds:

        - **Sunset enforcement** via :func:`_shim_active`. After
          ``_SHIM_SUNSET_DATE`` the v1 branch is skipped entirely; only
          v2 signatures verify. The ``EQ6_SHIM_FORCE_ACTIVE`` env var
          re-enables the shim for break-glass incident response.
        - **Telemetry** via :func:`_record_v1_verification`. Operators
          can call :func:`get_v1_verification_count` to monitor how many
          legacy artifacts are still in flight as the sunset approaches.
        """
        v2 = self._compute_signature(secret_key)
        if hmac.compare_digest(v2, self.signature):
            return True
        if not _shim_active():
            return False
        v1 = self._compute_signature_v1(secret_key)
        if hmac.compare_digest(v1, self.signature):
            _record_v1_verification()
            return True
        return False

    def _compute_signature(self, secret_key: bytes) -> str:
        """Compute HMAC-SHA256 signature (v2 — includes idempotency_nonce).

        Signature is taken over (manifest_hash, idempotency_nonce, timestamp)
        rather than the full payload — the manifest hash already encodes the
        logical content, so including it keeps signature inputs compact while
        binding the nonce to the signed artifact.
        """
        payload = {
            "manifest_hash": self.manifest_hash,
            "idempotency_nonce": self.idempotency_nonce,
            "timestamp": self.timestamp,
            "schema_version": self.schema_version,
        }
        payload_bytes = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
        return hmac.new(secret_key, payload_bytes, hashlib.sha256).hexdigest()

    def _compute_signature_v1(self, secret_key: bytes) -> str:
        """Legacy HMAC-SHA256 signature (pre-EQ1 scheme, no nonce).

        Retained for the 90-day back-compat window so historical artifacts
        minted before 2026-04-23 still verify. Scheduled for removal on
        2026-07-23 per EQ-1 sunset plan.
        """
        # TODO(2026-07-23): remove EQ-1 shim when back-compat window closes.
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

    def to_prompt_messages(
        self,
        slots: "dict[str, AuthoritySlot] | None" = None,
        provider_hint: str | None = None,
    ) -> "PromptMessages":
        """Project this artifact to the ``PromptMessages`` IR.

        Phase RH2B.3 of plan ``prompt-reception-followups-a7b3c4``. Non-breaking
        — the artifact still carries flat ``final_system_string`` /
        ``final_user_string`` for legacy passthrough. Adapters that upgrade
        consume ``PromptMessages`` directly via this method.

        Parameters
        ----------
        slots
            Optional per-slot-code -> ``AuthoritySlot`` map. Enables multi-slot
            rendering (S0/I0/D0/C0/E0/M0/H0/U0). When omitted, the IR falls
            back to a two-entry (``SYSTEM``/``USER``) map.
        provider_hint
            Optional provider identifier consumed by adapters.
        """
        # Local import to avoid circularity at module load.
        from agentic_core.L2_execution.reasoning.prompt_messages import (
            PromptMessages,
        )

        return PromptMessages.from_artifact(
            artifact=self,
            slots=slots,
            provider_hint=provider_hint,
        )


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
