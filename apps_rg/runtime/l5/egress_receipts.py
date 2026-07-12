"""apps_rg metadata-only L5 egress receipt helpers."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, is_dataclass
from typing import Any, Mapping

from agentic_core.L5_safety.certification.egress_certifier import (
    MetadataOnlyEgressCertifier,
)
from agentic_core.L5_safety.contracts.l5_certification_contracts import (
    EgressCertificationReceipt,
)

SYMBOLIC_APPS_RG_PROVIDER_REF = "urn:provider:governed-gateway:rg:v1"
DEFAULT_REDACTION_POLICY_REF = "urn:redaction:apps-rg:metadata-only:v1"


def _canonical_digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _canonical_response_content_digest(value: Any) -> str:
    """Bind the receipt to response content without storing response text."""

    text = str(value or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    try:
        parsed = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        canonical = text
    else:
        canonical = json.dumps(
            parsed, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _safe_mapping(value: Any) -> Mapping[str, Any]:
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, Mapping):
        return dict(value)
    return {}


def build_apps_rg_egress_receipt(
    *,
    request_metadata: Mapping[str, Any],
    response_metadata: Mapping[str, Any],
    call_purpose_ref: str,
    egress_policy_ref: str = "",
    redaction_policy_ref: str = DEFAULT_REDACTION_POLICY_REF,
    l5_governance_context_digest: str = "",
    egress_status: str = "EGRESS_CERTIFIED",
) -> EgressCertificationReceipt:
    """Build a metadata-only receipt over canonical request/response digests."""

    return MetadataOnlyEgressCertifier().certify_egress(
        provider_ref=SYMBOLIC_APPS_RG_PROVIDER_REF,
        call_purpose_ref=call_purpose_ref,
        request_digest=_canonical_digest(dict(request_metadata)),
        response_digest=_canonical_digest(dict(response_metadata)),
        redaction_policy_ref=redaction_policy_ref,
        l5_governance_context_digest=l5_governance_context_digest,
        redaction_receipt_ref=f"redaction:{_canonical_digest(dict(response_metadata))[:16]}",
        egress_status=egress_status,
        egress_policy_ref=egress_policy_ref,
        schema_version="apps_rg_l5_egress_receipt.v2",
    )


def receipt_ref(receipt: EgressCertificationReceipt) -> str:
    digest = _canonical_digest(asdict(receipt))
    return f"l5_egress:{digest}"


def receipt_digest(receipt: EgressCertificationReceipt) -> str:
    return _canonical_digest(asdict(receipt))


def receipt_from_provider_exchange(
    *,
    provider_profile: Any,
    provider_request: Any,
    provider_response: Any,
    latency_ms: float,
    call_purpose_ref: str,
    egress_policy_ref: str = "",
) -> EgressCertificationReceipt:
    """Convert a ProviderGateway exchange into a content-bound metadata receipt."""

    request_metadata = {
        "request_id": str(getattr(provider_request, "request_id", "") or ""),
        "run_id": str(getattr(provider_request, "run_id", "") or ""),
        "trace_root": str(getattr(provider_request, "trace_root", "") or ""),
        "node_id": str(getattr(provider_request, "node_id", "") or ""),
        "prompt_artifact_ref": str(
            getattr(provider_request, "prompt_artifact_ref", "") or ""
        ),
        "provider_profile_ref": str(getattr(provider_profile, "profile_id", "") or ""),
        "max_tokens": int(getattr(provider_request, "max_tokens", 0) or 0),
        "temperature": float(getattr(provider_request, "temperature", 0.0) or 0.0),
        "top_p": float(getattr(provider_request, "top_p", 0.0) or 0.0),
    }
    usage = getattr(getattr(provider_response, "receipt", None), "token_usage", None)
    response_metadata = {
        "success": bool(getattr(provider_response, "success", False)),
        "error_class": type(getattr(provider_response, "error_message", None)).__name__,
        "has_text": bool(str(getattr(provider_response, "text", "") or "")),
        "response_content_sha256": _canonical_response_content_digest(
            getattr(provider_response, "text", "")
        ),
        "latency_ms": round(float(latency_ms), 4),
        "token_total": int(getattr(usage, "total_tokens", 0) or 0),
    }
    status = (
        "EGRESS_CERTIFIED"
        if bool(getattr(provider_response, "success", False))
        else "EGRESS_NOT_CERTIFIED"
    )
    return build_apps_rg_egress_receipt(
        request_metadata=request_metadata,
        response_metadata=response_metadata,
        call_purpose_ref=call_purpose_ref,
        egress_policy_ref=egress_policy_ref,
        egress_status=status,
    )


__all__ = [
    "DEFAULT_REDACTION_POLICY_REF",
    "SYMBOLIC_APPS_RG_PROVIDER_REF",
    "build_apps_rg_egress_receipt",
    "receipt_digest",
    "receipt_from_provider_exchange",
    "receipt_ref",
]
