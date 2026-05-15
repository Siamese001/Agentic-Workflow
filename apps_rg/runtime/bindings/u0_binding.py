"""apps_rg U0 binding — cert reference, task class, and ingress validator.

All symbols defined here are re-exported by the legacy shim at
agentic_core.runtime.entry.u0_apps_rg_binding. Do NOT import from
agentic_core here — this module must remain import-cycle free.
"""
from __future__ import annotations

from typing import Any

__all__ = [
    "APPS_RG_U0_CERT_REF",
    "APPS_RG_TASK_CLASS",
    "u0_validate_apps_rg",
]

APPS_RG_U0_CERT_REF: str = "u0-apps-rg-resume-generation-w2"
APPS_RG_TASK_CLASS: str = "resume_generation"

_REQUIRED_APP_PAYLOAD_KEYS: frozenset[str] = frozenset(
    {
        "target_company",
        "target_role",
    }
)


def u0_validate_apps_rg(envelope: Any) -> Any:
    """Validate a RequestEnvelope and return a ValidatedRequest.

    Raises
    ------
    ValueError
        If the envelope is missing required app_payload keys.
    TypeError
        If the envelope is not a RequestEnvelope.

    Returns
    -------
    ValidatedRequest
        A fully validated request ready for the L1 planning stage.
    """
    from agentic_core.runtime.contracts.apps_rg_ingress_payload import (
        RequestEnvelope,
        ValidatedRequest,
    )

    if not isinstance(envelope, RequestEnvelope):
        raise TypeError(
            f"u0_validate_apps_rg: expected RequestEnvelope, got {type(envelope).__name__}"
        )

    app_payload: dict[str, Any] = envelope.app_payload or {}
    missing = _REQUIRED_APP_PAYLOAD_KEYS - set(app_payload.keys())
    if missing:
        raise ValueError(
            f"u0_validate_apps_rg: app_payload missing required keys: {sorted(missing)}"
        )

    import hashlib

    target_company: str = app_payload.get("target_company", "")
    target_role: str = app_payload.get("target_role", "")
    target_level: str = app_payload.get("target_level", "")
    source_resume_text: str = app_payload.get("source_resume_text", "")
    jd_text: str = app_payload.get("job_description_text", "")
    generation_mode: str = app_payload.get("generation_mode", "strategic_tailor")

    resume_hash = hashlib.sha256(source_resume_text.encode("utf-8")).hexdigest()
    jd_hash = hashlib.sha256(jd_text.encode("utf-8")).hexdigest()

    idempotency_key = app_payload.get("idempotency_key") or (
        f"{target_company}:{target_role}:{resume_hash[:16]}:{jd_hash[:16]}::v1"
    )

    validated_app_payload: dict[str, Any] = {
        **app_payload,
        "generation_mode": generation_mode,
        "target_company": target_company,
        "target_role": target_role,
        "target_level": target_level,
        "resume_hash": resume_hash,
        "jd_hash": jd_hash,
        "task_class": APPS_RG_TASK_CLASS,
        "cert_ref": APPS_RG_U0_CERT_REF,
    }

    return ValidatedRequest(
        app_id=envelope.app_id,
        task_class=APPS_RG_TASK_CLASS,
        replay_key=idempotency_key,
        app_payload=validated_app_payload,
        cert_ref=APPS_RG_U0_CERT_REF,
    )
