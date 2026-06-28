"""Credential preflight for IBM narrative clean X3 ALLOW attempts (apps_rg-only).

Fails fast **before** PROVIDER_MODEL narrative generation when model-backed X1D is requested and a
required judge provider has no usable API credential configured.

Live provider rate-limit / transient errors are discoverable only at judge-call time unless
operators set ``APPS_RG_IBM_NARRATIVE_JUDGE_PREFLIGHT_FORCE_BLOCK`` for drilldown/tests.
"""

from __future__ import annotations

import os
from typing import Any, Mapping

from apps_rg.runtime.judges.executive_summary_x1d import PROVIDERS, resolve_x1d_provider_credentials

_FORCE_ENV = "APPS_RG_IBM_NARRATIVE_JUDGE_PREFLIGHT_FORCE_BLOCK"


def _forced_block_keys(environ: Mapping[str, str]) -> set[str]:
    raw = str(environ.get(_FORCE_ENV) or "").strip()
    if not raw:
        return set()
    return {p.strip().lower() for p in raw.split(",") if p.strip()}


def run_ibm_narrative_judge_credentials_preflight(
    judge_keys: list[str],
    environ: Mapping[str, str],
) -> dict[str, Any]:
    """Return structured preflight artifact fields (plus internal blockers list)."""
    forced = _forced_block_keys(environ)
    rows: dict[str, Any] = {}
    blockers: list[str] = []

    norm_keys = [j.strip() for j in judge_keys if j.strip()]
    for key in norm_keys:
        lk = key.lower()
        if key not in PROVIDERS:
            rows[key] = {
                "provider_key": key,
                "status": "unknown_provider",
                "detail": f"judge provider key not in PROVIDERS map: {key!r}",
            }
            blockers.append(f"unknown judge provider key: {key}")
            continue

        if lk in forced or key in forced:
            rows[key] = {
                "provider_key": key,
                "status": "preflight_blocked",
                "detail": (
                    "Simulated unavailable/blocked judge via "
                    f"{_FORCE_ENV} (drilldown or contract test)."
                ),
            }
            blockers.append(
                f"required judge provider {key} unavailable/blocked "
                f"(configured by {_FORCE_ENV})"
            )
            continue

        api_key, consulted = resolve_x1d_provider_credentials(key, environ)
        if not api_key:
            gemini_hint = (
                "(Gemini expects GOOGLE_API_KEY; GEMINI_API_KEY is deprecated alias.)"
                if key == "gemini_pro"
                else ""
            )
            detail = (
                f"No usable API credential after checking {consulted}; {gemini_hint}".strip()
            )
            rows[key] = {
                "provider_key": key,
                "status": "missing_credentials",
                "env_vars_consulted": consulted,
                "detail": detail,
            }
            blockers.append(f"required judge provider {key} missing credentials ({detail})")
        else:
            rows[key] = {
                "provider_key": key,
                "status": "credential_present",
                "env_vars_consulted_in_order": consulted,
                "detail": "non-empty credential resolved via resolve_x1d_provider_credentials",
            }

    return {
        "required_judges": norm_keys,
        "provider_preflight_status_by_judge": rows,
        "all_required_available": not blockers,
        "preflight_blocked": bool(blockers),
        "preflight_decisive_blockers": blockers,
        "preflight_force_block_env": _FORCE_ENV,
    }


__all__ = ["run_ibm_narrative_judge_credentials_preflight"]
