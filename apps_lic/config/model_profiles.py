"""apps_lic model-profile resolver (W1.1 model SSOT).

``config/domain_contract/model_profiles.yaml`` is the single source of truth for
which model each apps_lic surface uses. This module loads it and resolves the
effective values, honouring the documented environment overrides declared in the
YAML (precedence env > yaml; first matching env var wins). Environment variables
are overrides for ops/local deployment, never the source of truth.
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


class ModelProfileSSOTError(RuntimeError):
    """Raised when apps_lic model profile SSOT cannot be loaded."""


@lru_cache(maxsize=1)
def load_model_profiles() -> Mapping[str, Any]:
    """Load the model-profile SSOT YAML (cached, fail-closed)."""
    try:
        with _MODEL_PROFILES_PATH.open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
    except FileNotFoundError as exc:
        raise ModelProfileSSOTError(
            f"Missing apps_lic model profile SSOT: {_MODEL_PROFILES_PATH}"
        ) from exc
    except yaml.YAMLError as exc:
        raise ModelProfileSSOTError(
            f"Malformed apps_lic model profile SSOT: {_MODEL_PROFILES_PATH}"
        ) from exc
    except OSError as exc:
        raise ModelProfileSSOTError(
            f"Unreadable apps_lic model profile SSOT: {_MODEL_PROFILES_PATH}"
        ) from exc
    if not isinstance(data, Mapping):
        raise ModelProfileSSOTError(
            f"apps_lic model profile SSOT root must be a mapping: {_MODEL_PROFILES_PATH}"
        )
    return data


def _section(name: str) -> Mapping[str, Any]:
    section = load_model_profiles().get(name)
    if not isinstance(section, Mapping):
        raise ModelProfileSSOTError(f"Missing apps_lic model profile section: {name}")
    return section


def _required(section_name: str, value_key: str) -> str:
    value = _section(section_name).get(value_key)
    if not str(value or "").strip():
        raise ModelProfileSSOTError(
            f"Missing apps_lic model profile key: {section_name}.{value_key}"
        )
    return str(value).strip()


def _first_env_override(keys: Any) -> str:
    if not isinstance(keys, (list, tuple)):
        return ""
    for key in keys:
        value = os.environ.get(str(key))
        if value:
            return value
    return ""


def _resolve(section_name: str, value_key: str, override_key: str) -> str:
    override = _first_env_override(_section(section_name).get(override_key))
    if override:
        return override
    return _required(section_name, value_key)


# Canonical provider profile constants consumed by runtime policy.
FRONTIER_GENERATOR_PROVIDER_PROFILE = _required("generator", "provider_profile")
GPT_X1D_PROVIDER_PROFILE = _required("x1d_judge", "provider_profile")
# Backward-compatible import name for older tests; value is now GPT, not Claude.
CLAUDE_X1D_PROVIDER_PROFILE = GPT_X1D_PROVIDER_PROFILE


def resolve_generator_model() -> str:
    """Effective generator display model (env override > yaml)."""
    return _resolve("generator", "model", "model_env_overrides")


def resolve_generator_transport_model_id() -> str:
    """Effective generator transport model id (env override > yaml)."""
    return _resolve(
        "generator",
        "transport_model_id",
        "transport_model_id_env_overrides",
    )


def resolve_generator_base_url() -> str:
    """Deprecated compatibility shim; apps_lic generation no longer uses base URLs."""
    return ""


def resolve_generator_provider() -> str:
    """Effective generator provider token."""
    return _required("generator", "provider")


def resolve_generator_provider_profile() -> str:
    """Effective generator provider profile."""
    return _required("generator", "provider_profile")


def resolve_x1d_judge_provider_profile() -> str:
    """Effective independent X1D judge provider profile."""
    return _required("x1d_judge", "provider_profile")


def resolve_x1d_judge_provider() -> str:
    """Effective independent X1D judge provider token."""
    return _required("x1d_judge", "provider")


def resolve_x1d_judge_model() -> str:
    """Effective independent X1D judge model label."""
    return _required("x1d_judge", "model")


def resolve_x1d_judge_transport_model_id() -> str:
    """Effective X1D judge transport model id (env override > yaml)."""
    return _resolve(
        "x1d_judge",
        "transport_model_id",
        "transport_model_id_env_overrides",
    )


__all__ = [
    "CLAUDE_X1D_PROVIDER_PROFILE",
    "FRONTIER_GENERATOR_PROVIDER_PROFILE",
    "GPT_X1D_PROVIDER_PROFILE",
    "ModelProfileSSOTError",
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
