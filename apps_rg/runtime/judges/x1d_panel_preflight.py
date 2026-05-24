"""apps_rg wrapper — core panel transport preflight from static provider profiles."""

from __future__ import annotations

from agentic_core.runtime.judges.panel.adapter_protocol import DeclaredTransportPolicy
from agentic_core.runtime.judges.panel.panel_types import TransportReceipt
from agentic_core.runtime.judges.panel.preflight import audit_provider_transport_profile
from apps_rg.runtime.judges.x1d_judge_transport_contract import (
    PROOF_JUDGE_PROVIDER_KEYS,
    ProviderTransportProfile,
    TransportViolation,
    build_provider_transport_profile,
)


def profile_to_transport_receipt(
    profile: ProviderTransportProfile,
    provider_key: str,
    *,
    contract_hash: str = "transport-preflight",
) -> TransportReceipt:
    json_lock = "responseSchema" if provider_key == "gemini_pro" else "json_object"
    if not profile.has_json_output_lock:
        json_lock = "none"
    return TransportReceipt(
        provider_key=provider_key,
        contract_hash=contract_hash,
        max_output_tokens=profile.max_output_tokens,
        temperature=0.1 if profile.temperature_is_low else None,
        json_output_lock=json_lock,
        finish_or_stop_reason="stop" if profile.checks_truncation_stop_reason else None,
        parse_status="ok" if profile.system_includes_score_schema else "missing_schema_anchor",
    )


def profile_to_declared_policy(profile: ProviderTransportProfile, provider_key: str) -> DeclaredTransportPolicy:
    json_lock = "responseSchema" if provider_key == "gemini_pro" else "json_object"
    if not profile.has_json_output_lock:
        json_lock = "none"
    return DeclaredTransportPolicy(
        max_output_tokens=profile.max_output_tokens,
        json_output_lock=json_lock,
        temperature=0.1 if profile.temperature_is_low else None,
        system_includes_score_schema=profile.system_includes_score_schema,
    )


def audit_provider_transport_preflight_core() -> list[TransportViolation]:
    """Core-backed transport preflight (replaces inspect.getsource transport audits)."""
    violations: list[TransportViolation] = []
    for key in PROOF_JUDGE_PROVIDER_KEYS:
        profile = build_provider_transport_profile(key)
        declared = profile_to_declared_policy(profile, key)
        observed = profile_to_transport_receipt(profile, key)
        for cv in audit_provider_transport_profile(key, declared, observed):
            violations.append(
                TransportViolation(
                    code=cv.code,
                    detail=cv.detail,
                    path=cv.path or "apps_rg/runtime/judges/executive_summary_x1d.py",
                )
            )
    return violations


__all__ = [
    "audit_provider_transport_preflight_core",
    "profile_to_declared_policy",
    "profile_to_transport_receipt",
]
