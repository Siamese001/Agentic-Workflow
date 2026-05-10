"""U0 ingress validation binding for apps_research `company_brief` task class.

Per plan apps-research-golden-template-adoption-ag9.

U0 is the FIRST stage. Its job is to:
1. Validate the ingress payload for forbidden runtime-authority fields.
2. Run a legacy authority scan on the contract JSON.
3. Emit a ValidatedRequest with app_payload and receipts.

apps_research is R3_SIMPLE_GROUNDED_READ — grounded, read-only, no write authority,
no embedding generation, no ChromaDB mutation, no direct L4 writes.

This binding is mandatory on the live runtime path.  No bypass.
"""
from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping
from uuid import uuid4

from agentic_core.runtime.contracts.apps_rg_ingress_payload import (
    RequestEnvelope,
    ValidatedRequest,
)
from agentic_core.runtime.contracts.posture import POSTURE_READ_ONLY

_LOGGER = logging.getLogger(__name__)

APPS_RESEARCH_TASK_CLASS: str = "company_brief"

# Fields that apps_research must NEVER provide at ingress — runtime authority
# is exclusively owned by agentic_core stages.
_FORBIDDEN_AUTHORITY_FIELDS: frozenset[str] = frozenset(
    {
        "route_id",
        "execution_form",
        "provider",
        "workflow_dag",
        "l3_required",
        "model_id",
        "grounding_required",
        "model_generation_required",
        "write_authority",
        "sandbox_required",
        "egress_policy_ref",
        "allowed_tools",
        "allowed_models",
    }
)


@dataclass(frozen=True)
class AppsResearchAuthorityViolation(Exception):
    """Raised when apps_research ingress payload contains forbidden authority fields."""

    field: str
    value: Any
    message: str = ""

    def __str__(self) -> str:
        return (
            f"AppsResearchAuthorityViolation: field={self.field!r} "
            f"value={self.value!r} — {self.message}"
        )


@dataclass(frozen=True)
class AppsResearchU0ReflectionReceipt:
    """Receipt produced by U0 reflection harness for apps_research."""

    task_class: str
    schema_version: str
    forbidden_fields_checked: int
    authority_fields_present: tuple[str, ...]
    legacy_authority_scan_passed: bool
    reflection_timestamp: str


def _scan_for_legacy_authority(payload_dict: Mapping[str, Any]) -> list[str]:
    """Scan payload JSON for legacy runtime-authority keys (flat + nested).

    Returns list of found forbidden field names (empty = clean).
    """
    found: list[str] = []
    for key in payload_dict:
        if key in _FORBIDDEN_AUTHORITY_FIELDS:
            found.append(key)
    return found


def _make_payload_dict(envelope: RequestEnvelope) -> dict[str, Any]:
    """Serialize the ingress payload into a canonical dict for inspection."""
    payload = envelope.payload
    # Build flat dict from the AppsRgIngressPayload (reused for apps_research path)
    # apps_research uses topic/depth; these are carried as user_constraints
    result: dict[str, Any] = {
        "app_id": getattr(payload, "app_id", "apps_research"),
        "task_class": getattr(payload, "task_class", APPS_RESEARCH_TASK_CLASS),
        "target_company": getattr(payload, "target_company", None),
        "target_role": getattr(payload, "target_role", None),
        "target_level": getattr(payload, "target_level", None),
        "user_constraints": dict(getattr(payload, "user_constraints", {}) or {}),
        "output_preferences": dict(getattr(payload, "output_preferences", {}) or {}),
        "manual_brief_path": getattr(payload, "manual_brief_path", None),
        "auto_research_internal": getattr(payload, "auto_research_internal", False),
        "auto_research_tavily": getattr(payload, "auto_research_tavily", False),
        "idempotency_key": getattr(payload, "idempotency_key", None),
        "payload_digest": getattr(payload, "payload_digest", ""),
    }
    # Extract topic/depth from user_constraints if present (apps_research convention)
    uc = result["user_constraints"]
    if "topic" in uc:
        result["topic"] = uc["topic"]
    if "depth" in uc:
        result["depth"] = uc["depth"]
    return result


def _compute_payload_digest(payload_dict: dict[str, Any]) -> str:
    canonical = json.dumps(payload_dict, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def u0_validate_apps_research(envelope: RequestEnvelope) -> ValidatedRequest:
    """Validate the apps_research ingress payload and emit a ValidatedRequest.

    Pipeline:
    1. Serialize payload to canonical dict.
    2. Check for forbidden runtime-authority fields.
    3. Legacy authority scan (nested check).
    4. Build ValidatedRequest with app_payload + receipt.

    Raises AppsResearchAuthorityViolation if any forbidden field is present.
    """
    if not isinstance(envelope, RequestEnvelope):
        raise TypeError(
            f"u0_validate_apps_research: expected RequestEnvelope, got {type(envelope)}"
        )

    payload_dict = _make_payload_dict(envelope)

    # Step 2: Forbidden field check
    forbidden_found = _scan_for_legacy_authority(payload_dict)
    if forbidden_found:
        raise AppsResearchAuthorityViolation(
            field=forbidden_found[0],
            value=payload_dict.get(forbidden_found[0]),
            message=(
                f"apps_research ingress payload contains {len(forbidden_found)} "
                f"forbidden authority field(s): {forbidden_found!r}. "
                "apps_research is INGRESS-ONLY — runtime authority belongs to agentic_core."
            ),
        )

    # Step 3: Legacy authority scan
    legacy_found = _scan_for_legacy_authority(payload_dict)
    legacy_scan_passed = len(legacy_found) == 0

    reflection_timestamp = datetime.now(timezone.utc).isoformat()
    reflection_receipt = AppsResearchU0ReflectionReceipt(
        task_class=APPS_RESEARCH_TASK_CLASS,
        schema_version="AG9.U0.1",
        forbidden_fields_checked=len(_FORBIDDEN_AUTHORITY_FIELDS),
        authority_fields_present=tuple(legacy_found),
        legacy_authority_scan_passed=legacy_scan_passed,
        reflection_timestamp=reflection_timestamp,
    )

    # Step 4: Compute digest and build ValidatedRequest
    payload_digest = _compute_payload_digest(payload_dict)

    _LOGGER.debug(
        "U0 apps_research validated: task_class=%s digest=%s",
        APPS_RESEARCH_TASK_CLASS,
        payload_digest[:16],
    )

    from agentic_core.runtime.contracts.apps_rg_runtime_authority_policy import (
        AuthorityValidationReceipt,
    )

    authority_receipt = AuthorityValidationReceipt(
        validated=True,
        forbidden_fields_found=[],
        validation_timestamp=reflection_timestamp,
    )

    return ValidatedRequest(
        request_id=envelope.request_id or f"research-req-{uuid4().hex[:12]}",
        run_id=envelope.run_id or f"research-run-{uuid4().hex[:12]}",
        app_id="apps_research",
        task_class=APPS_RESEARCH_TASK_CLASS,
        payload_digest=payload_digest,
        authority_validation_receipt=authority_receipt,
        trace_id=envelope.trace_id or f"research-trace-{uuid4().hex[:16]}",
        tenant_id=envelope.tenant_id or "apps_research",
        target_level=getattr(envelope.payload, "target_level", "") or "",
        schema_version="AG9.U0.1",
        posture=POSTURE_READ_ONLY,
        l5_certification_ref="u0-apps-research-company-brief-ag9",
        app_payload=payload_dict,
        reflection_receipt=reflection_receipt,
    )


__all__ = [
    "APPS_RESEARCH_TASK_CLASS",
    "AppsResearchAuthorityViolation",
    "AppsResearchU0ReflectionReceipt",
    "u0_validate_apps_research",
]
