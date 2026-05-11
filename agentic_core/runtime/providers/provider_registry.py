"""Provider registry — loads and resolves provider profiles.

RB13: apps-rg-zip-based-full-spine-runtime-restoration-v1

Generic registry for provider profile resolution.
No hardcoded provider names. No app-specific code.
"""

from __future__ import annotations

import hashlib
import logging
import os
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

import yaml

from agentic_core.runtime.providers.provider_types import (
    ProviderKind,
    ProviderProfile,
    ProviderProfileNotFoundError,
)
from agentic_core.L0_routing.config.model_registry import (
    ANTHROPIC_MODEL_ID,
    GEMINI_PRO_MODEL_ID,
    OPENAI_MODEL_ID,
    QWEN_LOCAL_MODEL_ID,
)

_LOGGER = logging.getLogger(__name__)


class ProviderRegistry:
    """Registry for loading and caching provider profiles.
    
    Loads from YAML files at app config paths.
    Supports hot-reload for development.
    """
    
    def __init__(self) -> None:
        self._profiles: Dict[str, ProviderProfile] = {}
        self._registry_paths: Dict[str, Path] = {}
        self._loaded_at: Optional[float] = None
    
    def load_from_yaml(
        self,
        yaml_path: Path,
        app_id: Optional[str] = None,
    ) -> int:
        """Load all profiles from a provider_profiles.yaml file.
        
        Args:
            yaml_path: Path to the YAML file
            app_id: Optional app_id for namespacing
            
        Returns:
            Number of profiles loaded
            
        Raises:
            ProviderProfileNotFoundError: If file doesn't exist
        """
        if not yaml_path.exists():
            raise ProviderProfileNotFoundError(
                f"Provider profile file not found: {yaml_path}"
            )
        
        try:
            raw_bytes = yaml_path.read_bytes()
            data = yaml.safe_load(raw_bytes.decode("utf-8")) or {}
        except Exception as exc:
            raise ProviderProfileNotFoundError(
                f"Failed to parse provider profile YAML: {exc}"
            ) from exc
        
        registry_id = data.get("provider_profile_registry_id", "")
        profiles_data = data.get("profiles", {})
        
        count = 0
        for profile_key, profile_data in profiles_data.items():
            profile = self._parse_profile(profile_key, profile_data)
            # Store by both short key and full profile_id
            self._profiles[profile_key] = profile
            self._profiles[profile.profile_id] = profile
            self._registry_paths[profile.profile_id] = yaml_path
            count += 1
        
        _LOGGER.info(
            "Loaded %d provider profiles from %s (registry_id=%s)",
            count,
            yaml_path,
            registry_id,
        )
        return count
    
    def _parse_profile(
        self,
        profile_key: str,
        data: Mapping[str, Any],
    ) -> ProviderProfile:
        """Parse a profile dict into ProviderProfile."""
        
        # Resolve endpoint URL from env var if specified
        endpoint_url = data.get("endpoint_url")
        endpoint_env_var = data.get("endpoint_env_var")
        if endpoint_env_var and not endpoint_url:
            endpoint_url = os.environ.get(endpoint_env_var)
            if endpoint_url:
                _LOGGER.debug(
                    "Resolved endpoint for %s from %s",
                    profile_key,
                    endpoint_env_var,
                )
        
        # Default endpoint fallback
        default_endpoint = data.get("default_endpoint")
        if not endpoint_url and default_endpoint:
            endpoint_url = default_endpoint
        
        vendor = data.get("provider_vendor", "")
        raw_model_id = data.get("model_id")
        model_id = self._resolve_model_id(raw_model_id, vendor)

        return ProviderProfile(
            profile_id=data.get("profile_id", profile_key),
            provider_kind=ProviderKind(data.get("provider_class", "stub")),
            model_id=model_id,
            endpoint_url=endpoint_url,
            endpoint_env_var=endpoint_env_var,
            api_key_env_var=data.get("api_key_env_var"),
            capabilities=tuple(data.get("capabilities", [])),
            max_tokens=data.get("max_tokens", 4096),
            timeout_seconds=data.get("timeout_seconds", 60),
            temperature_range=tuple(
                data.get("temperature_range", [0.0, 1.0])
            ),
            requires_network=data.get("requires_network", False),
            sandbox_safe=data.get("sandbox_safe", True),
            activation_env_var=data.get("activation_env_var"),
            vendor=vendor,
        )

    def _resolve_model_id(self, raw_model_id: Optional[str], vendor: str) -> Optional[str]:
        """Resolve model_id through model_registry env-var constants.

        YAML value acts as fallback default; env var (already baked into the
        model_registry constants) takes precedence. Mapping:
          anthropic      -> ANTHROPIC_MODEL_ID  (env: ANTHROPIC_MODEL)
          openai         -> OPENAI_MODEL_ID     (env: OPENAI_MODEL)
          google_gemini  -> GEMINI_PRO_MODEL_ID (env: GEMINI_PRO_MODEL)
          local_vllm     -> QWEN_LOCAL_MODEL_ID (env: VLLM_MODEL_NAME)
          other / null   -> raw_model_id as-is
        """
        if vendor == "anthropic":
            return ANTHROPIC_MODEL_ID
        if vendor == "openai":
            return OPENAI_MODEL_ID
        if vendor == "google_gemini":
            return GEMINI_PRO_MODEL_ID
        # local_vllm profiles: prefer env-resolved constant over YAML string
        if raw_model_id and "qwen" in raw_model_id.lower():
            return QWEN_LOCAL_MODEL_ID
        return raw_model_id
    
    def get_profile(self, profile_ref: str) -> ProviderProfile:
        """Get a provider profile by reference.
        
        Args:
            profile_ref: Profile ID or short key
            
        Returns:
            ProviderProfile instance
            
        Raises:
            ProviderProfileNotFoundError: If profile not found
        """
        if profile_ref in self._profiles:
            return self._profiles[profile_ref]
        
        # Try to load if not cached
        raise ProviderProfileNotFoundError(
            f"Provider profile not found: {profile_ref}. "
            f"Available: {list(self._profiles.keys())[:10]}..."
        )
    
    def list_profiles(
        self,
        provider_kind: Optional[ProviderKind] = None,
    ) -> list[str]:
        """List available provider profiles.
        
        Args:
            provider_kind: Optional filter by kind
            
        Returns:
            List of profile IDs
        """
        if provider_kind is None:
            return list(self._profiles.keys())
        
        return [
            pid for pid, prof in self._profiles.items()
            if prof.provider_kind == provider_kind
        ]
    
    def clear(self) -> None:
        """Clear all loaded profiles."""
        self._profiles.clear()
        self._registry_paths.clear()
        self._loaded_at = None
    
    def is_stub_profile(self, profile_ref: str) -> bool:
        """Check if a profile is a stub provider.
        
        Args:
            profile_ref: Profile ID or key
            
        Returns:
            True if stub provider
        """
        try:
            profile = self.get_profile(profile_ref)
            return profile.provider_kind == ProviderKind.STUB
        except ProviderProfileNotFoundError:
            return False
    
    def check_external_credentials(self, profile_ref: str) -> bool:
        """Check if external provider credentials are available.
        
        Args:
            profile_ref: Profile ID or key
            
        Returns:
            True if credentials available or not required
        """
        try:
            profile = self.get_profile(profile_ref)
            
            # Non-external providers don't need API keys
            if profile.provider_kind not in (ProviderKind.EXTERNAL_API,):
                return True
            
            # Check API key env var
            if profile.api_key_env_var:
                return os.environ.get(profile.api_key_env_var) is not None
            
            return True
        except ProviderProfileNotFoundError:
            return False


# Global singleton registry instance
_global_registry: Optional[ProviderRegistry] = None


def get_provider_registry() -> ProviderRegistry:
    """Get the global provider registry instance."""
    global _global_registry
    if _global_registry is None:
        _global_registry = ProviderRegistry()
    return _global_registry


def reset_provider_registry() -> None:
    """Reset the global registry (mainly for tests)."""
    global _global_registry
    _global_registry = None


__all__ = [
    "ProviderRegistry",
    "get_provider_registry",
    "reset_provider_registry",
]
