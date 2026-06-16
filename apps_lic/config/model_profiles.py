"""apps_lic model-profile resolver (W1.1 model SSOT).

Plan: apps-lic-completeness-graph-grounding-ssot-e7b2c4.

``config/domain_contract/model_profiles.yaml`` is the single source of truth for
which model each apps_lic surface uses. This module loads it and resolves the
effective values, honouring the documented environment overrides declared in the
YAML (precedence env > yaml; first matching env var wins). Environment variables
are overrides for ops/local deployment, never the source of truth.

Two surfaces resolve through here:

* the Claude Opus generator (HOP5 ``generation_engine``); and
* the independent GPT-5.5 X1D judge provider profile.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

import yaml

_MODEL_PROFILES_PATH = (
    Path(__file__).resolve().parent / "domain_contract" / "model_profiles.yaml"
)

# Hard fallbacks mirror the YAML so a missing/garbled file never silently breaks
# resolution; the YAML remains authoritative when present.
_GENERATOR_FALLBACK = {
    "provider": "claude",
    "provider_profile": "claude_opus_4_8_primary",
    "model": "Claude Opus 4.8",
    "transport_model_id": "claude-opus-4-8",
}
_X1D_JUDGE_FALLBACK = {
    "provider": "openai",
    "provider_profile": "gpt_5_5_x1d",
    "model": "GPT-5.5",
    "transport_model_id": "gpt-5.5",
}

# Canonical provider profile constants consumed by runtime policy.
FRONTIER_GENERATOR_PROVIDER_PROFILE = str(_GENERATOR_FALLBACK["provider_profile"])
GPT_X1D_PROVIDER_PROFILE = str(_X1D_JUDGE_FALLBACK["provider_profile"])
# Backward-compatible import name for older tests; value is now GPT, not Claude.
CLAUDE_X1D_PROVIDER_PROFILE = GPT_X1D_PROVIDER_PROFILE


@lru_cache(maxsize=1)
def load_model_profiles() -> Mapping[str, Any]:
    """Load the model-profile SSOT YAML (cached)."""
    try:
        with _MODEL_PROFILES_PATH.open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
    except FileNotFoundError:
        return {}
    return data if isinstance(data, Mapping) else {}


def _section(name: str) -> Mapping[str, Any]:
    section = load_model_profiles().get(name)
    return section if isinstance(section, Mapping) else {}


def _first_env_override(keys: Any) -> str:
    if not isinstance(keys, (list, tuple)):
        return ""
    for key in keys:
        value = os.environ.get(str(key))
        if value:
            return value
    return ""


def _resolve(section_name: str, value_key: str, override_key: str, fallback: Mapping[str, Any]) -> str:
    section = _section(section_name)
    override = _first_env_override(section.get(override_key))
    if override:
        return override
    yaml_value = section.get(value_key)
    if yaml_value:
        return str(yaml_value)
    return str(fallback.get(value_key, ""))


def resolve_generator_model() -> str:
    """Effective generator display model (env override > yaml > fallback)."""
    return _resolve("generator", "model", "model_env_overrides", _GENERATOR_FALLBACK)


def resolve_generator_transport_model_id() -> str:
    """Effective generator transport model id (env override > yaml > fallback)."""
    return _resolve(
        "generator",
        "transport_model_id",
        "transport_model_id_env_overrides",
        _GENERATOR_FALLBACK,
    )


def resolve_generator_base_url() -> str:
    """Deprecated compatibility shim; apps_lic generation no longer uses base URLs."""
    return ""


def resolve_generator_provider() -> str:
    """Effective generator provider token."""
    section = _section("generator")
    return str(section.get("provider") or _GENERATOR_FALLBACK["provider"])


def resolve_generator_provider_profile() -> str:
    """Effective generator provider profile."""
    section = _section("generator")
    return str(section.get("provider_profile") or _GENERATOR_FALLBACK["provider_profile"])


def resolve_x1d_judge_provider_profile() -> str:
    """Effective independent X1D judge provider profile."""
    section = _section("x1d_judge")
    return str(section.get("provider_profile") or _X1D_JUDGE_FALLBACK["provider_profile"])


def resolve_x1d_judge_provider() -> str:
    """Effective independent X1D judge provider token."""
    section = _section("x1d_judge")
    return str(section.get("provider") or _X1D_JUDGE_FALLBACK["provider"])


def resolve_x1d_judge_model() -> str:
    """Effective independent X1D judge model label."""
    section = _section("x1d_judge")
    return str(section.get("model") or _X1D_JUDGE_FALLBACK["model"])


def resolve_x1d_judge_transport_model_id() -> str:
    """Effective X1D judge transport model id (env override > yaml > fallback)."""
    return _resolve(
        "x1d_judge",
        "transport_model_id",
        "transport_model_id_env_overrides",
        _X1D_JUDGE_FALLBACK,
    )


__all__ = [
    "CLAUDE_X1D_PROVIDER_PROFILE",
    "FRONTIER_GENERATOR_PROVIDER_PROFILE",
    "GPT_X1D_PROVIDER_PROFILE",
    "load_model_profiles",
    "resolve_generator_base_url",
    "resolve_generator_model",
    "resolve_generator_provider",
    "resolve_generator_provider_profile",
    "resolve_generator_transport_model_id",
    "resolve_x1d_judge_model",
    "resolve_x1d_judge_provider",
    "resolve_x1d_judge_provider_profile",
    "resolve_x1d_judge_transport_model_id",
]
