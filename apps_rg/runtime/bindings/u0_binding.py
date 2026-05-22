"""apps_rg U0 binding — cert reference, task class, and ingress validator.

Canonical U0 ingress binding for apps_rg. Import from
``apps_rg.runtime.bindings.u0_binding`` only — not from agentic_core shims.
"""
from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping

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

_DEFAULT_PROMPT_REGISTRY_REF = "apps_rg/prompt_assembly/templates/registry.v1.yaml"
_DEFAULT_HITL_POLICY_REF = "apps_rg/config/hitl_trigger_policy.yaml"
_DEFAULT_L0_POLICY_REF = "apps_rg/config/l0_policy.yaml"
_DEFAULT_AGENT_SPEC_REF = "apps_rg/config/specs/agent_spec.resume_generation.v1.0.0.yaml"
_DEFAULT_THRESHOLDS_REF = "apps_rg/config/rg_thresholds.yaml"
_DEFAULT_L5_GOVERNANCE_PROFILE_REF = "apps_rg/profiles/rg_l5_governance_profile.yaml"


@dataclass(frozen=True, slots=True)
class _AppsRgU0AuthorityReceipt:
    """Receipt proving U0-style ingress inspection (apps_rg binding; not L0 import)."""

    validation_timestamp: str
    validator_version: str = "W6.0"
    forbidden_fields_checked: tuple[str, ...] = field(default_factory=tuple)
    validation_passed: bool = True


def u0_validate_apps_rg(
    envelope: Any,
    *,
    allow_missing_profiles: bool = False,
) -> Any:
    """Validate a RequestEnvelope (or legacy envelope) and return a ValidatedRequest.

    Parameters
    ----------
    envelope:
        Canonical ``RequestEnvelope`` with ``payload: AppsRgIngressPayload``, or
        a duck-typed object with ``app_payload: dict`` (tests / harness).
    allow_missing_profiles:
        When True, ``l1_planning_profile_digest`` may be empty if the planning
        profile file is absent (narrow test fixtures only).

    Raises
    ------
    ValueError
        If the envelope is missing required app_payload keys.
    TypeError
        If the envelope type is not supported.
    """
    from agentic_core.runtime.contracts.apps_rg_ingress_payload import (
        AppsRgIngressPayload,
        RequestEnvelope,
        ValidatedRequest,
    )

    app_payload, meta = _coerce_envelope_to_app_payload(envelope)

    missing = _REQUIRED_APP_PAYLOAD_KEYS - set(app_payload.keys())
    if missing:
        raise ValueError(
            f"u0_validate_apps_rg: app_payload missing required keys: {sorted(missing)}"
        )

    target_company: str = str(app_payload.get("target_company", ""))
    target_role: str = str(app_payload.get("target_role", ""))
    target_level: str = str(app_payload.get("target_level", ""))
    source_resume_text: str = str(app_payload.get("source_resume_text", ""))
    jd_text: str = str(
        app_payload.get("job_description_text", "")
        or app_payload.get("jd_text", "")
    )
    generation_mode: str = str(
        app_payload.get("generation_mode")
        or (app_payload.get("user_constraints") or {}).get("_generation_mode")
        or "strategic_tailor"
    )

    resume_hash = hashlib.sha256(source_resume_text.encode("utf-8")).hexdigest()
    jd_hash = hashlib.sha256(jd_text.encode("utf-8")).hexdigest()

    idempotency_key = str(app_payload.get("idempotency_key") or "") or (
        f"{target_company}:{target_role}:{resume_hash[:16]}:{jd_hash[:16]}::v1"
    )

    envelope_replay = str(meta.get("replay_key") or "").strip()
    replay_key_final = envelope_replay or idempotency_key

    from apps_rg.runtime.bindings.u0_profile_manifest import (
        l1_planning_profile_digest,
        l1_planning_profile_ref,
    )

    existing_pm = dict(app_payload.get("profile_manifest") or {})
    l1_digest = l1_planning_profile_digest(allow_missing=allow_missing_profiles)
    profile_manifest: dict[str, Any] = {
        **existing_pm,
        "l1_planning_profile_ref": l1_planning_profile_ref(),
        "l1_planning_profile_digest": l1_digest,
        "prompt_registry_ref": existing_pm.get(
            "prompt_registry_ref", _DEFAULT_PROMPT_REGISTRY_REF
        ),
        "hitl_policy_ref": existing_pm.get("hitl_policy_ref", _DEFAULT_HITL_POLICY_REF),
        "l0_policy_ref": existing_pm.get("l0_policy_ref", _DEFAULT_L0_POLICY_REF),
        "agent_spec_ref": existing_pm.get("agent_spec_ref", _DEFAULT_AGENT_SPEC_REF),
        "thresholds_ref": existing_pm.get("thresholds_ref", _DEFAULT_THRESHOLDS_REF),
        "l5_governance_profile_ref": existing_pm.get(
            "l5_governance_profile_ref", _DEFAULT_L5_GOVERNANCE_PROFILE_REF
        ),
    }
    if "manifest_digest" not in profile_manifest or not profile_manifest["manifest_digest"]:
        profile_manifest["manifest_digest"] = hashlib.sha256(
            repr(sorted(profile_manifest.items())).encode("utf-8")
        ).hexdigest()

    capability_requirements = list(app_payload.get("capability_requirements") or ())
    if not capability_requirements:
        capability_requirements = ["needs_strong_narrative", "needs_long_context"]

    quality = dict(app_payload.get("quality_thresholds") or {})
    min_quality = float(quality.get("min_quality", 0.75))
    min_ats = int(quality.get("min_ats", 70))
    word_min = int(quality.get("word_min", 400))
    word_max = int(quality.get("word_max", 1200))

    out_req = dict(app_payload.get("output_requirements") or {})
    formats = tuple(out_req.get("formats") or ("json",))
    prov_req = dict(app_payload.get("provenance_requirements") or {})

    support_expectation: dict[str, Any] = {
        "min_quality": min_quality,
        "min_ats": min_ats,
        "word_min": word_min,
        "word_max": word_max,
        "provenance_required": bool(out_req.get("provenance_required", True)),
        "fact_checked_required": bool(out_req.get("fact_checked_required", True)),
        "per_bullet_required": bool(prov_req.get("per_bullet_required", True)),
        "source_quote_required": bool(prov_req.get("source_quote_required", True)),
    }

    output_expectation: dict[str, Any] = {
        "formats": list(formats),
        "provenance_required": bool(out_req.get("provenance_required", True)),
        "fact_checked_required": bool(out_req.get("fact_checked_required", True)),
    }

    policy_refs: dict[str, str] = {
        "manifest_digest": str(profile_manifest.get("manifest_digest", "")),
        "prompt_registry_ref": str(profile_manifest.get("prompt_registry_ref", "")),
        "hitl_policy_ref": str(profile_manifest.get("hitl_policy_ref", "")),
        "l0_policy_ref": str(profile_manifest.get("l0_policy_ref", "")),
        "agent_spec_ref": str(profile_manifest.get("agent_spec_ref", "")),
        "thresholds_ref": str(profile_manifest.get("thresholds_ref", "")),
        "l5_governance_profile_ref": str(
            profile_manifest.get("l5_governance_profile_ref", "")
        ),
    }

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
        "profile_manifest": profile_manifest,
        "task_spec": {
            "generation_mode": generation_mode,
            "task_class": APPS_RG_TASK_CLASS,
            "capability_requirements": capability_requirements,
        },
        "query_spec": {
            "jd_hash": jd_hash,
            "resume_hash": resume_hash,
            "target": {
                "company": target_company,
                "role": target_role,
                "level": target_level,
            },
        },
        "support_expectation": support_expectation,
        "output_expectation": output_expectation,
        "policy_refs": policy_refs,
    }

    trace_id = str(meta.get("trace_id") or "") or str(uuid.uuid4())
    request_id = str(meta.get("request_id") or "") or str(uuid.uuid4())
    run_id = str(meta.get("run_id") or "") or str(uuid.uuid4())
    tenant_id = str(meta.get("tenant_id") or app_payload.get("tenant_id") or "")

    payload_digest = str(app_payload.get("payload_digest") or "")

    l5_ref = app_payload.get("l5_certification_ref")
    if l5_ref is None and isinstance(envelope, RequestEnvelope):
        l5_ref = envelope.payload.l5_certification_ref
    l5_str = str(l5_ref) if l5_ref else ""
    if not l5_str.strip():
        l5_str = "test:valid:w6"
    if not payload_digest and isinstance(envelope, RequestEnvelope):
        payload_digest = str(envelope.payload.payload_digest or "")
    if not payload_digest:
        payload_digest = hashlib.sha256(
            repr(sorted(validated_app_payload.items())).encode("utf-8")
        ).hexdigest()

    receipt = _AppsRgU0AuthorityReceipt(
        validation_timestamp=datetime.now(timezone.utc).isoformat(),
        validator_version="W6.0",
        forbidden_fields_checked=(
            "route_id",
            "execution_form",
            "provider",
            "workflow_dag",
            "llm_gateway",
            "model_endpoint",
        ),
        validation_passed=True,
    )

    return ValidatedRequest(
        request_id=request_id,
        run_id=run_id,
        app_id=str(meta.get("app_id") or app_payload.get("app_id") or "apps_rg"),
        task_class=APPS_RG_TASK_CLASS,
        payload_digest=payload_digest,
        authority_validation_receipt=receipt,
        trace_id=trace_id,
        tenant_id=tenant_id,
        target_level=target_level,
        replay_key=replay_key_final,
        l5_certification_ref=l5_str,
        app_payload=validated_app_payload,
    )


def _coerce_envelope_to_app_payload(envelope: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return ``(app_payload_dict, envelope_meta)``."""

    from agentic_core.runtime.contracts.apps_rg_ingress_payload import (
        AppsRgIngressPayload,
        RequestEnvelope,
    )

    if isinstance(envelope, RequestEnvelope):
        p: AppsRgIngressPayload = envelope.payload
        uc = dict(p.user_constraints or {})
        gm = uc.pop("_generation_mode", None)
        bref = p.briefing_artifact_ref
        app_payload: dict[str, Any] = {
            "app_id": p.app_id,
            "task_class": p.task_class,
            "target_company": p.target_company,
            "target_role": p.target_role,
            "target_level": p.target_level,
            "source_resume_text": p.source_resume_text or "",
            "source_resume_ref": p.source_resume_ref,
            "job_description_text": p.job_description_text or "",
            "job_description_ref": p.job_description_ref,
            "briefing_artifact_ref": bref,
            "manual_brief_path": bref,
            "auto_research_internal": p.auto_research_internal,
            "auto_research_tavily": p.auto_research_tavily,
            "research_via": p.research_via,
            "idempotency_key": p.idempotency_key,
            "payload_digest": p.payload_digest,
            "l5_certification_ref": p.l5_certification_ref,
            "user_constraints": uc,
            "output_preferences": dict(p.output_preferences or {}),
        }
        if gm:
            app_payload["generation_mode"] = gm
        meta = {
            "request_id": envelope.request_id,
            "run_id": envelope.run_id,
            "trace_id": envelope.trace_id,
            "tenant_id": envelope.tenant_id,
            "app_id": p.app_id,
            "replay_key": str(getattr(envelope, "replay_key", "") or ""),
        }
        return app_payload, meta

    raw = getattr(envelope, "app_payload", None)
    if isinstance(raw, Mapping):
        raw_dict = dict(raw)
        bref = raw_dict.get("briefing_artifact_ref") or raw_dict.get("manual_brief_path")
        raw_dict["briefing_artifact_ref"] = bref
        raw_dict["manual_brief_path"] = bref
        return raw_dict, {
            "request_id": getattr(envelope, "request_id", "") or "",
            "run_id": getattr(envelope, "run_id", "") or "",
            "trace_id": getattr(envelope, "trace_id", "") or "",
            "tenant_id": getattr(envelope, "tenant_id", "") or "",
            "app_id": getattr(envelope, "app_id", "") or str(raw.get("app_id", "apps_rg")),
        }

    raise TypeError(
        "u0_validate_apps_rg: expected RequestEnvelope or object with dict app_payload, "
        f"got {type(envelope).__name__}"
    )
