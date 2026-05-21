"""apps_lic U0 shim — bridges adapter contract to AppIngressRunner calling convention.

W4 remediation (bundle-c1-blocker-remediation-a4f9e2).

Problem:
    AppIngressRunner._run_profile_stages calls:
        validated = u0_fn(envelope)   # envelope is RequestEnvelope; expects ValidatedRequest

    But apps_lic_u0_adapt has contract:
        apps_lic_u0_adapt(raw_json: Mapping, *, request_id, run_id)
            -> tuple[ValidatedRequest, AppsLicU0ReflectionReceipt]

Two mismatches:
    1. Input type: RequestEnvelope vs Mapping[str, Any]
    2. Return type: tuple vs ValidatedRequest

This shim:
    - Accepts RequestEnvelope from the runner
    - Extracts raw_json from envelope.payload (or falls back to body_json/body_text)
    - Forwards request_id and run_id from the envelope
    - Calls apps_lic_u0_adapt
    - Returns only the ValidatedRequest (discards receipt — it has been threaded
      into validated_request.reflection_receipt by the adapter)

The AppsLicU0ReflectionReceipt is NOT discarded: the adapter attaches it to
ValidatedRequest.reflection_receipt via dataclasses.replace() before returning
(adapter line 703-704). Downstream stages access it via validated_request.reflection_receipt.
"""
from __future__ import annotations

import json
from typing import Any

from apps_lic.runtime.u0.adapter import apps_lic_u0_adapt
from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest


def _envelope_to_raw_dict(envelope: Any) -> dict[str, Any]:
    """Extract a raw dict from a RequestEnvelope for apps_lic_u0_adapt.

    Priority:
    1. envelope.payload (AppsLicIngressContractV1-shaped dict or dataclass)
    2. envelope.body_json
    3. envelope.body_text (parsed as JSON)
    4. empty dict (fails closed inside adapter with a validation error)
    """
    payload = getattr(envelope, "payload", None)
    if payload is not None:
        if isinstance(payload, dict):
            return payload
        if hasattr(payload, "__dict__"):
            return {k: v for k, v in payload.__dict__.items() if not k.startswith("_")}
        if hasattr(payload, "model_dump"):
            return payload.model_dump()

    body_json = getattr(envelope, "body_json", None)
    if isinstance(body_json, dict):
        return body_json

    body_text = getattr(envelope, "body_text", None)
    if isinstance(body_text, str) and body_text.strip():
        try:
            parsed = json.loads(body_text)
            if isinstance(parsed, dict):
                return parsed
        except (json.JSONDecodeError, ValueError):  # guardian: allow-silent-swallow -- P2 burndown: fail-soft optional boundary
            pass

    return {}


def u0_lic_shim(envelope: Any) -> ValidatedRequest:
    """Shim U0 callable for AppIngressRunner profile path.

    Called as: u0_fn(envelope) -> ValidatedRequest

    Bridges RequestEnvelope → apps_lic_u0_adapt → ValidatedRequest.
    Receipt is retained inside validated_request.reflection_receipt.
    """
    raw_json = _envelope_to_raw_dict(envelope)
    request_id = getattr(envelope, "request_id", None)
    run_id = getattr(envelope, "run_id", None)

    validated_request, _receipt = apps_lic_u0_adapt(
        raw_json,
        request_id=request_id,
        run_id=run_id,
    )
    return validated_request


__all__ = ["u0_lic_shim", "_envelope_to_raw_dict"]
