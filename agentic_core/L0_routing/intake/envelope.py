"""
Raw ingress envelope and supporting manifests.

Captures the request shell BEFORE any interpretation:
- who/what appears to be calling
- which transport carried the packet
- what raw payload arrived
- attachments / URLs / callbacks / job metadata
- tenant / workspace claim
- trace / session / request identifiers

Spec section: U0 HOW PATRONS CONTACT US (lines 28-72).

INVARIANT: This struct is purely descriptive. No semantic field ever resolves
the user's intent. Intake reads `body_text` and attachment metadata only to
validate shape and run safe normalization — never to interpret.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class AttachmentManifestEntry:
    """Single attachment descriptor — metadata only, contents are by reference.

    Intake never reads file content. It captures size, MIME, filename, and a
    storage reference. Downstream stages may inspect content under their own
    governed paths (C0 grounding, L2 execution).
    """

    filename: str
    mime_type: str
    size_bytes: int
    ref: str  # opaque storage reference (URL, blob id, content-addressed hash)
    declared_modality: str = "unknown"  # text|image|audio|video|file|unknown


@dataclass(frozen=True)
class AttachmentManifestShell:
    """Pre-validation manifest captured at U0/E1."""

    entries: tuple[AttachmentManifestEntry, ...] = ()
    total_bytes: int = 0

    @property
    def count(self) -> int:
        return len(self.entries)


@dataclass(frozen=True)
class ModalityManifest:
    """Declared + observed modalities (E4 output, line 354)."""

    declared: tuple[str, ...] = ()
    observed: tuple[str, ...] = ()


@dataclass(frozen=True)
class RawIngressEnvelope:
    """Pre-intake envelope.

    Intake receives this struct from a transport adapter. The adapter is
    responsible for capturing transport-level facts (headers, parser output,
    raw body pointer). Intake then runs E1..E6 against this struct.

    Required fields are minimal; everything else is a Mapping[str, Any] so
    transport adapters can attach their own context without polluting the
    intake contract.
    """

    # --- transport facts ---
    transport: str  # e.g. "chat", "ui", "api", "batch", "webhook", "queue", "alert"
    method: str = ""  # HTTP verb or transport equivalent; "" if N/A
    content_type: str = ""
    source_channel: str = ""  # human-readable channel hint (e.g. "slack", "rest_v2")

    # --- caller signal ---
    claimed_tenant_id: str | None = None
    claimed_workspace_id: str | None = None
    claimed_user_id: str | None = None
    claimed_service_id: str | None = None
    auth_credential: Mapping[str, Any] = field(default_factory=dict)
    # auth_credential keys may include: kind ("api_key"|"oauth"|"mtls"|"session"),
    # token, issuer, expires_at_unix, scopes, mfa, ...

    # --- payload ---
    body_text: str | None = None  # raw request body text (chat / API JSON string)
    body_json: Mapping[str, Any] | None = None  # parsed body if transport pre-parsed
    body_parser_failed: bool = False
    raw_payload_ref: str = ""  # storage handle for raw bytes

    # --- attachments ---
    attachments: AttachmentManifestShell = field(default_factory=AttachmentManifestShell)

    # --- batch / webhook / alert metadata ---
    batch_id: str | None = None
    job_id: str | None = None
    webhook_delivery_id: str | None = None
    alert_id: str | None = None
    idempotency_key: str | None = None

    # --- correlation ---
    upstream_traceparent: str | None = None
    session_id_hint: str | None = None
    request_id_hint: str | None = None

    # --- network / locale ---
    source_ip: str | None = None
    region: str | None = None
    locale: str | None = None
    timezone: str | None = None
    client_version: str | None = None
    platform: str | None = None

    # --- declared modality (caller-supplied; E4 verifies) ---
    declared_modalities: Sequence[str] = ()

    # --- escape hatch for transport-specific extras ---
    extras: Mapping[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Convenience predicates used by E1/E4. These are SHAPE checks only —
    # they NEVER inspect the meaning of body_text / body_json.
    # ------------------------------------------------------------------

    def has_payload(self) -> bool:
        """True if any body_text, body_json, or attachment exists."""
        if self.body_text and self.body_text.strip():
            return True
        if self.body_json:
            return True
        if self.attachments.count > 0:
            return True
        return False

    def has_credential(self) -> bool:
        return bool(self.auth_credential)


__all__ = [
    "AttachmentManifestEntry",
    "AttachmentManifestShell",
    "ModalityManifest",
    "RawIngressEnvelope",
]
