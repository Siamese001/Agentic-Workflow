"""Provider-neutral section model limits and identity for apps_rg generation.

The generator model identity and runtime context budget are read from
``apps_rg/config/provider_profiles.yaml``. Environment variables may provide
credentials and endpoints, but they do not select apps_rg generator models or
runtime LLM budgets.
"""
from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any, Final

# Provider-profile SSOT path (apps_rg/config/provider_profiles.yaml). This module
# lives at apps_rg/runtime/, so parents[1] == apps_rg.
_PROVIDER_PROFILES_PATH: Final[Path] = (
    Path(__file__).resolve().parents[1] / "config" / "provider_profiles.yaml"
)


class SectionModelSSOTError(RuntimeError):
    """Raised when apps_rg generation model SSOT cannot be loaded."""


def _provider_config() -> dict[str, Any]:
    try:
        import yaml  # noqa: PLC0415

        data = yaml.safe_load(_PROVIDER_PROFILES_PATH.read_text(encoding="utf-8"))
    except Exception as exc:  # guardian: strict SSOT load; caller must see the broken source
        raise SectionModelSSOTError(f"Cannot load apps_rg provider profile SSOT: {_PROVIDER_PROFILES_PATH}") from exc
    if not isinstance(data, dict):
        raise SectionModelSSOTError(f"Invalid apps_rg provider profile SSOT: {_PROVIDER_PROFILES_PATH}")
    return data


def _provider_profiles() -> dict:
    data = _provider_config()
    profiles = (data or {}).get("profiles") or {}
    if not isinstance(profiles, dict):
        raise SectionModelSSOTError(f"Missing profiles block in apps_rg provider profile SSOT: {_PROVIDER_PROFILES_PATH}")
    return profiles


def _runtime_limits() -> dict[str, Any]:
    data = _provider_config()
    limits = data.get("runtime_limits") or {}
    if not isinstance(limits, dict):
        raise SectionModelSSOTError(f"Missing runtime_limits block in apps_rg provider profile SSOT: {_PROVIDER_PROFILES_PATH}")
    return limits


def _runtime_limit_value(path: str) -> Any:
    current: Any = _runtime_limits()
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            raise SectionModelSSOTError(f"Missing runtime_limits.{path} in {_PROVIDER_PROFILES_PATH}")
        current = current[part]
    return current


def runtime_limit_int(path: str) -> int:
    value = _runtime_limit_value(path)
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise SectionModelSSOTError(f"runtime_limits.{path} must be an int in {_PROVIDER_PROFILES_PATH}") from exc


def runtime_limit_float(path: str) -> float:
    value = _runtime_limit_value(path)
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise SectionModelSSOTError(f"runtime_limits.{path} must be a float in {_PROVIDER_PROFILES_PATH}") from exc


def runtime_limit_str(path: str) -> str:
    value = _runtime_limit_value(path)
    if not isinstance(value, str) or not value.strip():
        raise SectionModelSSOTError(f"runtime_limits.{path} must be a non-empty string in {_PROVIDER_PROFILES_PATH}")
    return value.strip()


SECTION_MODEL_MAX_MODEL_LEN: Final[int] = runtime_limit_int("section_context_window")


def _ssot_default_model(profile_key: str = "external_claude_generator") -> str:
    """Return ``profiles.<profile_key>.default_model`` from provider_profiles.yaml."""
    profiles = _provider_profiles()
    model = (profiles.get(profile_key) or {}).get("default_model")
    if not isinstance(model, str) or not model.strip():
        raise SectionModelSSOTError(f"Missing default_model for profiles.{profile_key}: {_PROVIDER_PROFILES_PATH}")
    return model.strip()


def _ssot_model_by_section() -> dict[str, str]:
    """Per-section model overrides from the provider-profiles SSOT
    (``external_claude_generator.model_by_section``)."""
    profiles = _provider_profiles()
    raw = (profiles.get("external_claude_generator") or {}).get("model_by_section") or {}
    if not isinstance(raw, dict):
        return {}
    return {
        str(k).strip().lower(): str(v).strip()
        for k, v in raw.items()
        if str(k).strip() and str(v).strip()
    }


def resolve_section_generation_model(
    section_id: str | None,
    environ: Mapping[str, str] | None = None,
) -> str:
    """THE single resolver for the apps_rg per-section generator model (SSOT-backed).

    Every apps_rg generation dispatch MUST route the model through this function so the
    provider request carries the per-section model and no other source can win.

    Precedence:
      1. ``provider_profiles.yaml`` ``external_claude_generator.model_by_section[section]``
      2. ``provider_profiles.yaml`` ``external_claude_generator.default_model``
    """
    _ = environ
    sid = str(section_id or "").strip().lower()
    if sid:
        by_section = _ssot_model_by_section()
        if sid in by_section:
            return by_section[sid]
    return _ssot_default_model("external_claude_generator")


def external_claude_generation_model(environ: Mapping[str, str] | None = None) -> str:
    """Section-agnostic default generator model (no per-section override).

    Equivalent to ``resolve_section_generation_model(None)``. Callers that know their section MUST prefer
    :func:`resolve_section_generation_model` so the per-section tier applies.
    """
    return resolve_section_generation_model(None, environ)


def external_openai_generation_model(environ: Mapping[str, str] | None = None) -> str:
    """Section-agnostic OpenAI generator model from apps_rg provider_profiles.yaml."""
    _ = environ
    return _ssot_default_model("external_openai_generator")


def external_openai_generation_model_from_ssot() -> str:
    """Compatibility alias for provider fallback code during the SSOT migration."""
    return external_openai_generation_model()


# Canonical generation model identity for apps_rg sections — resolved from the external
# Claude generation profile (``provider_profiles.yaml`` -> external_claude_generator) so the
# X2 ``x2_model_name_allowed`` proof and prompt-render manifests reference the real provider model.
SECTION_MODEL_ID: Final[str] = external_claude_generation_model()
DEFAULT_EXTERNAL_CLAUDE_MODEL: Final[str] = _ssot_default_model("external_claude_generator")
DEFAULT_EXTERNAL_OPENAI_MODEL: Final[str] = _ssot_default_model("external_openai_generator")

__all__ = [
    "DEFAULT_EXTERNAL_CLAUDE_MODEL",
    "DEFAULT_EXTERNAL_OPENAI_MODEL",
    "SECTION_MODEL_ID",
    "SECTION_MODEL_MAX_MODEL_LEN",
    "SectionModelSSOTError",
    "external_claude_generation_model",
    "external_openai_generation_model",
    "resolve_section_generation_model",
    "runtime_limit_float",
    "runtime_limit_int",
    "runtime_limit_str",
]
