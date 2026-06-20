"""L1 planning evidence — validation receipt + ambiguity register (W3)."""

from __future__ import annotations

import hashlib
import uuid
from typing import Any, Mapping

__all__ = [
    "build_ambiguity_register",
    "build_validation_receipt_id",
]


def build_validation_receipt_id(
    *,
    request_id: str,
    profile_manifest_digest: str,
    planning_profile_digest: str,
) -> str:
    """Stable validation receipt id for L1 plan path (REQ-L1-PLAN-VALIDATION-001)."""

    canonical = "|".join(
        (
            request_id,
            profile_manifest_digest,
            planning_profile_digest,
        )
    )
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]
    return f"l1val-{request_id[:8]}-{digest}"


def build_ambiguity_register(app_payload: Mapping[str, Any]) -> dict[str, Any]:
    """Optional ambiguity register when ingress/planning signals are incomplete."""

    entries: list[dict[str, str]] = []
    target_company = str(app_payload.get("target_company") or "").strip()
    target_role = str(app_payload.get("target_role") or "").strip()
    target_level = str(app_payload.get("target_level") or "").strip()
    jd_text = str(
        app_payload.get("job_description_text") or app_payload.get("jd_text") or ""
    ).strip()
    source_resume = str(app_payload.get("source_resume_text") or "").strip()

    if target_company and not target_role:
        entries.append(
            {
                "code": "TARGET_ROLE_MISSING",
                "field": "target_role",
                "severity": "medium",
                "note": "Company provided without explicit role title",
            }
        )
    if target_role and not target_company:
        entries.append(
            {
                "code": "TARGET_COMPANY_MISSING",
                "field": "target_company",
                "severity": "low",
                "note": "Role provided without company name",
            }
        )
    if not target_level:
        entries.append(
            {
                "code": "TARGET_LEVEL_UNSPECIFIED",
                "field": "target_level",
                "severity": "low",
                "note": "Default L0 profile selection may apply",
            }
        )
    if not jd_text:
        entries.append(
            {
                "code": "JOB_DESCRIPTION_EMPTY",
                "field": "job_description_text",
                "severity": "high",
                "note": "Grounding and tailoring quality may degrade",
            }
        )
    if not source_resume:
        entries.append(
            {
                "code": "SOURCE_RESUME_EMPTY",
                "field": "source_resume_text",
                "severity": "high",
                "note": "Resume body missing at U0 handoff",
            }
        )

    if not entries:
        return {}

    return {
        "schema_version": "apps_rg_ambiguity_register_v1",
        "register_id": f"amb-{uuid.uuid4().hex[:12]}",
        "entries": entries,
    }
