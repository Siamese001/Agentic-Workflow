"""Known Anthropic-limit preflight routing for apps_rg whole-run generation.

This module intentionally does not probe Anthropic. It consumes an explicit
preflight signal that a caller already established, then routes whole-run
Claude-backed generation lanes directly to the OpenAI backup provider.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

from apps_rg.runtime.providers.provider_gateway import ProviderProfile

ANTHROPIC_LIMIT_PREFLIGHT_ENV = "APPS_RG_ANTHROPIC_LIMIT_PREFLIGHT"
ANTHROPIC_LIMIT_PREFLIGHT_RECEIPT_ENV = "APPS_RG_ANTHROPIC_LIMIT_PREFLIGHT_RECEIPT"
ANTHROPIC_LIMIT_PREFLIGHT_OPENAI_BACKUP_SOURCE = "ANTHROPIC_LIMIT_PREFLIGHT_OPENAI_BACKUP"

_FALSEY = frozenset({"", "0", "false", "no", "n", "off", "none", "pass", "unlimited"})
_LIMIT_MARKERS = (
    "provider_throttling_failure",
    "rate limit",
    "rate_limit",
    "rate-limited",
    "ratelimit",
    "throttl",
    "usage limit",
    "quota",
    "credit",
    "exhausted",
    "429",
)
_KNOWN_LIMIT_KEYS = frozenset(
    {
        "anthropic_limit_known",
        "anthropic_limited",
        "known_anthropic_limit",
        "limit_known",
        "rate_limited",
    }
)


@dataclass(frozen=True, slots=True)
class AnthropicLimitPreflightRoute:
    """Auditable route decision derived from a known Anthropic-limit signal."""

    active: bool
    source: str
    reason_category: str = ""
    requested_provider: str = ProviderProfile.EXTERNAL_CLAUDE.value
    routed_provider: str = ProviderProfile.EXTERNAL_OPENAI.value
    primary_attempt_skipped: bool = False
    receipt_path: str = ""
    receipt_sha256: str = ""
    evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "policy": "apps_rg_anthropic_limit_preflight_to_openai_backup",
            "scope": "apps_rg_whole_run_phase1_generation",
            "active": self.active,
            "source": self.source,
            "reason_category": self.reason_category,
            "requested_provider": self.requested_provider,
            "routed_provider": self.routed_provider,
            "primary_attempt_skipped": self.primary_attempt_skipped,
            "receipt_path": self.receipt_path,
            "receipt_sha256": self.receipt_sha256,
            "evidence": dict(self.evidence),
        }


def _value_indicates_known_limit(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    raw = str(value or "").strip().lower()
    if raw in _FALSEY:
        return False
    return any(marker in raw for marker in _LIMIT_MARKERS) or raw in {"1", "true", "yes", "y", "on", "limited"}


def _reason_category_from_signal(value: Any) -> str:
    raw = str(value or "").strip()
    if raw.lower() in {"1", "true", "yes", "y", "on", "limited"}:
        return "provider_throttling_failure"
    return raw


def _receipt_indicates_known_limit(payload: Any) -> tuple[bool, str, dict[str, Any]]:
    if not isinstance(payload, dict):
        return False, "", {}

    for key in _KNOWN_LIMIT_KEYS:
        if key in payload and _value_indicates_known_limit(payload.get(key)):
            return True, str(payload.get("reason_category") or "provider_throttling_failure"), {key: payload.get(key)}

    evidence_keys = (
        "reason_category",
        "fallback_allowed_reason_category",
        "fallback_reason",
        "provider_status",
        "provider_health_status",
        "exact_provider_error",
        "initial_exact_provider_error",
        "decisive_reason",
    )
    evidence: dict[str, Any] = {}
    for key in evidence_keys:
        value = payload.get(key)
        if value is None:
            continue
        evidence[key] = value
        if _value_indicates_known_limit(value):
            return True, str(payload.get("reason_category") or value), evidence

    nested = payload.get("apps_rg_availability_fallback")
    if isinstance(nested, dict):
        active, reason, nested_evidence = _receipt_indicates_known_limit(nested)
        if active:
            return True, reason, {"apps_rg_availability_fallback": nested_evidence}

    return False, "", evidence


def _route_from_receipt(path_ref: str) -> AnthropicLimitPreflightRoute:
    p = Path(path_ref)
    if not p.is_file():
        return AnthropicLimitPreflightRoute(
            active=False,
            source=f"{ANTHROPIC_LIMIT_PREFLIGHT_RECEIPT_ENV}:missing",
            receipt_path=path_ref,
        )
    try:
        raw = p.read_text(encoding="utf-8")
        payload = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        return AnthropicLimitPreflightRoute(
            active=False,
            source=f"{ANTHROPIC_LIMIT_PREFLIGHT_RECEIPT_ENV}:unreadable",
            receipt_path=str(p),
            evidence={"error": f"{type(exc).__name__}: {exc}"},
        )

    active, reason, evidence = _receipt_indicates_known_limit(payload)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return AnthropicLimitPreflightRoute(
        active=active,
        source=ANTHROPIC_LIMIT_PREFLIGHT_RECEIPT_ENV,
        reason_category=reason if active else "",
        primary_attempt_skipped=active,
        receipt_path=str(p),
        receipt_sha256=digest,
        evidence=evidence,
    )


def resolve_anthropic_limit_preflight_route(
    environ: Mapping[str, str] | None = None,
) -> AnthropicLimitPreflightRoute:
    """Resolve an explicit known-limit signal without attempting Anthropic."""
    env = os.environ if environ is None else environ
    raw = str(env.get(ANTHROPIC_LIMIT_PREFLIGHT_ENV) or "").strip()
    if raw:
        active = _value_indicates_known_limit(raw)
        return AnthropicLimitPreflightRoute(
            active=active,
            source=ANTHROPIC_LIMIT_PREFLIGHT_ENV,
            reason_category=_reason_category_from_signal(raw) if active else "",
            primary_attempt_skipped=active,
            evidence={ANTHROPIC_LIMIT_PREFLIGHT_ENV: raw},
        )

    receipt_ref = str(env.get(ANTHROPIC_LIMIT_PREFLIGHT_RECEIPT_ENV) or "").strip()
    if receipt_ref:
        return _route_from_receipt(receipt_ref)

    return AnthropicLimitPreflightRoute(active=False, source="not_configured")


def route_whole_run_provider_for_known_anthropic_limit(
    provider: str,
    resolution_source: str,
    *,
    section_id: str,
    environ: Mapping[str, str] | None = None,
) -> tuple[str, str, AnthropicLimitPreflightRoute]:
    """Route Claude-backed whole-run lanes to OpenAI when preflight already knows limits."""
    route = resolve_anthropic_limit_preflight_route(environ)
    normalized = str(provider or "").strip().lower()
    if route.active:
        evidence = dict(route.evidence)
        evidence.update(
            {
                "section_id": str(section_id or ""),
                "original_provider": normalized,
                "original_resolution_source": str(resolution_source or ""),
            }
        )
        if normalized != ProviderProfile.EXTERNAL_CLAUDE.value:
            evidence["route_applied"] = False
            return (
                provider,
                resolution_source,
                AnthropicLimitPreflightRoute(
                    active=True,
                    source=route.source,
                    reason_category=route.reason_category,
                    requested_provider=normalized,
                    routed_provider=normalized,
                    primary_attempt_skipped=False,
                    receipt_path=route.receipt_path,
                    receipt_sha256=route.receipt_sha256,
                    evidence=evidence,
                ),
            )
        evidence["route_applied"] = True
        routed = AnthropicLimitPreflightRoute(
            active=True,
            source=route.source,
            reason_category=route.reason_category,
            primary_attempt_skipped=True,
            receipt_path=route.receipt_path,
            receipt_sha256=route.receipt_sha256,
            evidence=evidence,
        )
        return (
            ProviderProfile.EXTERNAL_OPENAI.value,
            ANTHROPIC_LIMIT_PREFLIGHT_OPENAI_BACKUP_SOURCE,
            routed,
        )
    return provider, resolution_source, route


__all__ = [
    "ANTHROPIC_LIMIT_PREFLIGHT_ENV",
    "ANTHROPIC_LIMIT_PREFLIGHT_OPENAI_BACKUP_SOURCE",
    "ANTHROPIC_LIMIT_PREFLIGHT_RECEIPT_ENV",
    "AnthropicLimitPreflightRoute",
    "resolve_anthropic_limit_preflight_route",
    "route_whole_run_provider_for_known_anthropic_limit",
]
