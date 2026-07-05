"""L1 planning evidence — validation receipt + ambiguity register (W3)."""

from __future__ import annotations

import hashlib
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


def build_ambiguity_register(
    app_payload: Mapping[str, Any],
    *,
    ambiguity_rules: tuple[Mapping[str, Any], ...] | None = None,
    request_id: str = "",
    planning_profile_digest: str = "",
) -> dict[str, Any]:
    """Deterministic ambiguity register when ingress/planning signals are incomplete."""

    from apps_rg.runtime.bindings.l1_planning_capsule import stable_ambiguity_register

    rules = ambiguity_rules or (
        {
            "code": "TARGET_ROLE_MISSING",
            "field": "target_role",
            "severity": "medium",
            "blocks_progress": False,
        },
        {
            "code": "TARGET_COMPANY_MISSING",
            "field": "target_company",
            "severity": "low",
            "blocks_progress": False,
        },
        {
            "code": "TARGET_LEVEL_UNSPECIFIED",
            "field": "target_level",
            "severity": "low",
            "blocks_progress": False,
        },
        {
            "code": "JOB_DESCRIPTION_EMPTY",
            "field": "job_description_text",
            "severity": "high",
            "blocks_progress": True,
        },
        {
            "code": "SOURCE_RESUME_EMPTY",
            "field": "source_resume_text",
            "severity": "high",
            "blocks_progress": True,
        },
    )
    return stable_ambiguity_register(
        app_payload=app_payload,
        ambiguity_rules=rules,
        request_id=request_id,
        planning_profile_digest=planning_profile_digest,
    )
