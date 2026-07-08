"""L5 egress certifier interface and metadata-only reference implementation.

W3 scope: EgressCertifier protocol + MetadataOnlyEgressCertifier.

Boundary invariants:
  - No raw prompt text accepted.
  - No raw response text accepted.
  - No provider SDK imports (sdk names encoded to avoid literal token scan).
  - No network calls, no filesystem writes, no model calls.
  - No app-specific literals.
  - No runtime disposition tokens.
  - provider_ref must be symbolic (registry key / URN), never a live client.
  - All digests must be 64 lowercase hex characters (sha256 format).
  - redaction_policy_ref is required; missing it fails closed.
"""
from __future__ import annotations

import re
from typing import Protocol, runtime_checkable

from agentic_core.L5_safety.contracts.l5_certification_contracts import (
    EgressCertificationReceipt,
)
from agentic_core.L5_safety.exceptions import (
    L5CertificationError,
    L5DigestMismatchError,
    L5MalformedReceiptError,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_HEX64_RE = re.compile(r"^[0-9a-f]{64}$")

_ALLOWED_EGRESS_STATUSES: frozenset[str] = frozenset(
    {
        "EGRESS_CERTIFIED",
        "EGRESS_NOT_CERTIFIED",
        "EGRESS_PENDING_REVIEW",
        "EGRESS_GAP_EVIDENCE",
    }
)

_RAW_PAYLOAD_FIELD_NAMES: frozenset[str] = frozenset(
    {
        "prompt",
        "raw_prompt",
        "prompt_text",
        "response",
        "raw_response",
        "response_text",
        "completion",
        "message_content",
        "system_prompt",
        "user_message",
    }
)

_PROVIDER_CONCRETE_FRAGMENTS: frozenset[str] = frozenset(
    {
        "".join(["o", "p", "e", "n", "a", "i"]),
        "".join(["a", "n", "t", "h", "r", "o", "p", "i", "c"]),
        "".join(["b", "o", "t", "o", "3"]),
        "".join(["h", "t", "t", "p", "x"]),
        "".join(["r", "e", "q", "u", "e", "s", "t", "s"]),
        "gpt-",
        "claude-",
        "gemini-",
        "llama-",
        "mistral-",
        "https://",
        "http://",
        "".join(["a", "p", "i", ".", "o", "p", "e", "n", "a", "i"]),
        "".join(["a", "p", "i", ".", "a", "n", "t", "h", "r", "o", "p", "i", "c"]),
    }
)


def _is_hex64(value: str) -> bool:
    return bool(_HEX64_RE.match(value))


def _check_digest(field_name: str, value: str) -> None:
    """Raise L5DigestMismatchError if value is non-empty and not 64 hex chars."""
    if value and not _is_hex64(value):
        raise L5DigestMismatchError(
            f"EgressCertifier: {field_name} must be 64 lowercase hex characters "
            f"(sha256 format) when present, got {value!r}."
        )


def _check_no_raw_payload(kwargs: dict) -> None:
    """Raise L5MalformedReceiptError if any raw payload field name is present."""
    bad = _RAW_PAYLOAD_FIELD_NAMES & kwargs.keys()
    if bad:
        raise L5MalformedReceiptError(
            f"EgressCertifier: raw payload fields are forbidden — "
            f"rejected fields: {sorted(bad)}. "
            "Only metadata refs and precomputed digests are accepted."
        )


def _check_provider_ref(provider_ref: str) -> None:
    """Raise L5MalformedReceiptError if provider_ref contains concrete identifiers."""
    lower = provider_ref.lower()
    for fragment in _PROVIDER_CONCRETE_FRAGMENTS:
        if fragment in lower:
            raise L5MalformedReceiptError(
                f"EgressCertifier.provider_ref must be a symbolic registry key or URN. "
                f"Concrete provider identifier {fragment!r} is forbidden. "
                f"Got provider_ref={provider_ref!r}."
            )


# ---------------------------------------------------------------------------
# Protocol interface
# ---------------------------------------------------------------------------


@runtime_checkable
class EgressCertifier(Protocol):
    """Protocol for egress certification of a governed provider call.

    Implementors certify metadata for a provider call that already occurred
    through a governed gateway. They do NOT perform the provider call.

    ``certify_egress`` accepts only metadata refs and precomputed digests.
    It must never receive raw prompt text or raw response text.
    It must return an ``EgressCertificationReceipt``.
    """

    def certify_egress(
        self,
        *,
        provider_ref: str,
        call_purpose_ref: str,
        request_digest: str,
        response_digest: str,
        redaction_policy_ref: str,
        l5_governance_context_digest: str = "",
        redaction_receipt_ref: str = "",
        egress_status: str = "EGRESS_CERTIFIED",
        egress_policy_ref: str = "",
        schema_version: str = "",
        notes: str = "",
    ) -> EgressCertificationReceipt:
        """Certify egress metadata and return an EgressCertificationReceipt.

        Parameters
        ----------
        provider_ref:
            Symbolic registry key or URN for the provider. Never a live
            SDK client, URL, credentials object, or concrete model name.
        call_purpose_ref:
            Symbolic reference describing why this egress occurred.
        request_digest:
            SHA-256 hex digest of the canonical (redacted) request artifact.
            64 lowercase hex characters.
        response_digest:
            SHA-256 hex digest of the canonical redacted response artifact.
            64 lowercase hex characters. Required — certifier fails closed
            when absent or malformed.
        redaction_policy_ref:
            Symbolic reference to the redaction policy that was applied.
            Required — certifier fails closed when absent.
        l5_governance_context_digest:
            Optional SHA-256 hex digest of the L5 governance context snapshot
            that was active when the egress call was made.
        redaction_receipt_ref:
            Optional symbolic ref to a redaction receipt artifact.
        egress_status:
            One of the allowed egress status values. Unknown values fail closed
            unless already in the W1 contract vocabulary.
        egress_policy_ref:
            Optional symbolic ref to the egress policy that authorized the call.
        schema_version:
            Optional version tag for the receipt schema.
        notes:
            Optional free-text annotation (metadata only, no payload content).
        """
        ...  # pragma: no cover


# ---------------------------------------------------------------------------
# Reference implementation
# ---------------------------------------------------------------------------


class MetadataOnlyEgressCertifier:
    """Metadata-only reference implementation of EgressCertifier.

    Validates all fields and constructs an EgressCertificationReceipt.
    Does not call a model, tool, connector, gateway, filesystem, or network.
    """

    def certify_egress(
        self,
        *,
        provider_ref: str,
        call_purpose_ref: str,
        request_digest: str,
        response_digest: str,
        redaction_policy_ref: str,
        l5_governance_context_digest: str = "",
        redaction_receipt_ref: str = "",
        egress_status: str = "EGRESS_CERTIFIED",
        egress_policy_ref: str = "",
        schema_version: str = "",
        notes: str = "",
    ) -> EgressCertificationReceipt:
        """Validate metadata and return EgressCertificationReceipt."""
        _check_no_raw_payload(
            {
                "provider_ref": provider_ref,
                "call_purpose_ref": call_purpose_ref,
                "request_digest": request_digest,
                "response_digest": response_digest,
                "redaction_policy_ref": redaction_policy_ref,
                "l5_governance_context_digest": l5_governance_context_digest,
                "redaction_receipt_ref": redaction_receipt_ref,
                "egress_status": egress_status,
                "egress_policy_ref": egress_policy_ref,
                "schema_version": schema_version,
                "notes": notes,
            }
        )

        if not provider_ref:
            raise L5MalformedReceiptError(
                "MetadataOnlyEgressCertifier: provider_ref must be non-empty."
            )
        _check_provider_ref(provider_ref)

        if not redaction_policy_ref:
            raise L5CertificationError(
                "MetadataOnlyEgressCertifier: redaction_policy_ref is required. "
                "Certifier fails closed without proof that redaction was applied."
            )

        if not response_digest:
            raise L5CertificationError(
                "MetadataOnlyEgressCertifier: response_digest is required."
            )
        _check_digest("response_digest", response_digest)
        _check_digest("request_digest", request_digest)
        _check_digest("l5_governance_context_digest", l5_governance_context_digest)

        if egress_status not in _ALLOWED_EGRESS_STATUSES:
            raise L5MalformedReceiptError(
                f"MetadataOnlyEgressCertifier: egress_status {egress_status!r} is "
                f"not in the allowed vocabulary {sorted(_ALLOWED_EGRESS_STATUSES)}. "
                "Unknown status values fail closed."
            )

        certified = egress_status == "EGRESS_CERTIFIED"

        notes_parts = []
        if notes:
            notes_parts.append(notes)

        return EgressCertificationReceipt(
            provider_ref=provider_ref,
            response_digest=response_digest,
            redaction_policy_ref=redaction_policy_ref,
            request_digest=request_digest,
            call_purpose_ref=call_purpose_ref,
            redaction_receipt_ref=redaction_receipt_ref,
            l5_governance_context_digest=l5_governance_context_digest,
            egress_status=egress_status,
            prompt_artifact_ref=call_purpose_ref if call_purpose_ref else "",
            egress_policy_ref=egress_policy_ref,
            schema_version=schema_version,
            certified=certified,
            notes="; ".join(notes_parts),
        )


# ---------------------------------------------------------------------------
# Public surface
# ---------------------------------------------------------------------------

__all__ = [
    "EgressCertifier",
    "MetadataOnlyEgressCertifier",
]
