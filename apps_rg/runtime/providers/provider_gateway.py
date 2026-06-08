"""apps_rg ProviderGateway abstraction (Wave 10A).

This is the app-local provider selection surface. ``external_claude`` is the
default apps_rg E2E provider while ``qwen_vllm`` remains explicitly selectable
for local comparison runs.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Mapping, Protocol, runtime_checkable

from apps_rg.runtime.providers.provider_contract import ProviderResult

ENV_APPS_RG_PROVIDER_PROFILE = "APPS_RG_PROVIDER_PROFILE"
DEFAULT_PROVIDER_PROFILE = "external_claude"
CONFIG_PROVIDER_PROFILES = Path(__file__).resolve().parents[2] / "config" / "provider_profiles.yaml"


class ProviderGatewayError(RuntimeError):
    """Base error for apps_rg provider gateway configuration/runtime failures."""


class ProviderProfileNotRegisteredError(ProviderGatewayError):
    """Raised when a selected profile has no registered provider implementation."""


class ProviderProfile(str, Enum):
    """Provider profile selection.

    External Claude is the apps_rg E2E default; Qwen remains selectable.
    """

    QWEN_VLLM = "qwen_vllm"
    EXTERNAL_CLAUDE = "external_claude"
    EXTERNAL_OPENAI = "external_openai"
    EXTERNAL_DEFAULT = "external_default"


@runtime_checkable
class ModelProvider(Protocol):
    """Protocol for apps_rg model providers."""

    provider_profile: ProviderProfile

    def generate(
        self,
        compiled_prompt: Any,
        *,
        token_budget: int,
        temperature: float = 0.7,
    ) -> ProviderResult:
        """Generate model output for a compiled prompt-like object."""
        ...


@dataclass(frozen=True)
class ProviderProfileSelection:
    """Resolved provider profile and provenance."""

    profile: ProviderProfile
    source: str
    raw_value: str


def normalize_provider_profile(value: str | ProviderProfile | None) -> ProviderProfile:
    raw = str(value.value if isinstance(value, ProviderProfile) else value or "").strip().lower()
    if not raw:
        return ProviderProfile.EXTERNAL_CLAUDE
    aliases = {
        "local_qwen": ProviderProfile.QWEN_VLLM,
        "local_qwen_generator": ProviderProfile.QWEN_VLLM,
        "qwen": ProviderProfile.QWEN_VLLM,
        "qwen_vllm": ProviderProfile.QWEN_VLLM,
        "claude": ProviderProfile.EXTERNAL_CLAUDE,
        "external_claude": ProviderProfile.EXTERNAL_CLAUDE,
        "openai": ProviderProfile.EXTERNAL_OPENAI,
        "external_openai": ProviderProfile.EXTERNAL_OPENAI,
        "external_default": ProviderProfile.EXTERNAL_DEFAULT,
    }
    try:
        return aliases[raw]
    except KeyError as exc:
        allowed = ", ".join(p.value for p in ProviderProfile)
        raise ProviderGatewayError(f"Unknown apps_rg provider profile {raw!r}; expected one of {allowed}") from exc


def resolve_provider_profile(
    raw_value: str | None = None,
    *,
    environ: Mapping[str, str] | None = None,
) -> ProviderProfileSelection:
    """Resolve profile from explicit value, env, or Wave 10A default."""
    env = os.environ if environ is None else environ
    if raw_value is not None and str(raw_value).strip():
        return ProviderProfileSelection(
            profile=normalize_provider_profile(raw_value),
            source="explicit",
            raw_value=str(raw_value).strip(),
        )
    env_raw = str(env.get(ENV_APPS_RG_PROVIDER_PROFILE) or "").strip()
    if env_raw:
        return ProviderProfileSelection(
            profile=normalize_provider_profile(env_raw),
            source=ENV_APPS_RG_PROVIDER_PROFILE,
            raw_value=env_raw,
        )
    return ProviderProfileSelection(
        profile=ProviderProfile.EXTERNAL_CLAUDE,
        source="apps_rg_default_external_claude",
        raw_value=DEFAULT_PROVIDER_PROFILE,
    )


def load_provider_profiles_config(path: Path | None = None) -> dict[str, Any]:
    """Load the provider profile YAML used by Wave 10A selection tests."""
    p = path or CONFIG_PROVIDER_PROFILES
    if not p.is_file():
        raise ProviderGatewayError(f"Missing apps_rg provider profile config: {p}")
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover - repo test env includes PyYAML
        raise ProviderGatewayError("PyYAML is required to load apps_rg provider profiles") from exc
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ProviderGatewayError(f"Invalid apps_rg provider profile config: {p}")
    profiles = data.get("profiles")
    if not isinstance(profiles, dict):
        raise ProviderGatewayError(f"Invalid apps_rg provider profile config: missing profiles in {p}")
    return data


class ProviderGateway:
    """Gateway for apps_rg provider selection and execution."""

    def __init__(self, providers: Mapping[ProviderProfile, ModelProvider] | None = None) -> None:
        self._providers: dict[ProviderProfile, ModelProvider] = {}
        for profile, provider in (providers or {}).items():
            self.register_provider(profile, provider)

    def register_provider(self, profile: ProviderProfile | str, provider: ModelProvider) -> None:
        self._providers[normalize_provider_profile(profile)] = provider

    def registered_profiles(self) -> tuple[ProviderProfile, ...]:
        return tuple(self._providers)

    def generate(
        self,
        profile: ProviderProfile | str,
        compiled_prompt: Any,
        *,
        token_budget: int,
        temperature: float = 0.7,
    ) -> ProviderResult:
        selected = normalize_provider_profile(profile)
        provider = self._providers.get(selected)
        if provider is None and selected == ProviderProfile.EXTERNAL_DEFAULT:
            provider = self._providers.get(ProviderProfile.EXTERNAL_OPENAI) or self._providers.get(
                ProviderProfile.EXTERNAL_CLAUDE
            )
        if provider is None:
            raise ProviderProfileNotRegisteredError(f"Provider not registered: {selected.value}")
        return provider.generate(
            compiled_prompt,
            token_budget=token_budget,
            temperature=temperature,
        )


__all__ = [
    "CONFIG_PROVIDER_PROFILES",
    "DEFAULT_PROVIDER_PROFILE",
    "ENV_APPS_RG_PROVIDER_PROFILE",
    "ModelProvider",
    "ProviderGateway",
    "ProviderGatewayError",
    "ProviderProfile",
    "ProviderProfileNotRegisteredError",
    "ProviderProfileSelection",
    "load_provider_profiles_config",
    "normalize_provider_profile",
    "resolve_provider_profile",
]
