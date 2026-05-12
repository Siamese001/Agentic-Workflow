"""
Runtime Profile Resolver

Generic profile resolution for app-owned runtime configuration.

This module provides fail-closed profile resolution for runtime components.
It contains NO app-specific literals and branches only on generic profile_type,
never on app_id values.

Constitutional Compliance:
- No hardcoded app names (e.g., apps_*, org_*, tenant_*)
- No app-specific branching logic
- Fail-closed on missing, invalid, or unknown profiles
- Core generic infrastructure only
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

import yaml


class ProfileResolutionError(Exception):
    """Base exception for profile resolution failures."""
    pass


class UnknownAppError(ProfileResolutionError):
    """Raised when requested app has no profile defined."""
    pass


class InvalidProfileError(ProfileResolutionError):
    """Raised when profile exists but fails schema validation."""
    pass


class MissingProfileError(ProfileResolutionError):
    """Raised when profile file is missing."""
    pass


@runtime_checkable
class ProfileValidator(Protocol):
    """Protocol for profile validators."""
    
    def validate(self, profile_data: dict[str, Any], schema_path: Path) -> bool:
        """Validate profile data against schema."""
        ...


@dataclass(frozen=True)
class ProfileKey:
    """Composite key for profile lookup."""
    app_id: str
    profile_type: str
    
    def __post_init__(self) -> None:
        if not self.app_id or not self.profile_type:
            raise ValueError("app_id and profile_type are required")


@dataclass
class ResolvedProfile:
    """Result of successful profile resolution."""
    key: ProfileKey
    raw_data: dict[str, Any]
    source_path: Path
    schema_version: str
    # App-specific typed payload extracted by caller
    typed_payload: dict[str, Any] = field(default_factory=dict)


class RuntimeProfileResolver:
    """
    Generic profile resolver for runtime configuration.
    
    Design principles:
    - App-agnostic: Never branches on specific app_id values
    - Fail-closed: Raises typed exceptions on any resolution failure
    - Schema-driven: Validates all profiles against declared schemas
    - Path-convention: Locates profiles via convention, not hardcoded paths
    
    Profile path convention:
        {profile_root}/{app_id}/{profile_type}.yaml
        
    Example:
        ~/.config/agentic/profiles/{app_id}/{profile_type}.yaml
        
    Usage:
        resolver = RuntimeProfileResolver()
        try:
            profile = resolver.resolve(app_id, profile_type)
            # Use profile.typed_payload for app-specific config
        except UnknownAppError:
            # Handle unknown app - fail closed
            raise
    """
    
    # Schema registry: profile_type -> schema file path (relative to schema_root)
    SCHEMA_REGISTRY: dict[str, str] = {
        "u0_validation": "u0_validation_profile.schema.yaml",
        "u0_adapter": "u0_adapter_profile.schema.yaml",
        "pipeline_defaults": "pipeline_defaults.schema.yaml",
        "l6_learning": "l6_learning_profile.schema.yaml",
        "l6_writeback": "l6_writeback_profile.schema.yaml",
        "c0_substrate": "c0_substrate_profile.schema.yaml",
        "u0_payload_defaults": "u0_payload_defaults.schema.yaml",
    }
    
    def __init__(
        self,
        profile_root: Path | str | None = None,
        schema_root: Path | str | None = None,
        validator: ProfileValidator | None = None,
        strict_mode: bool = True,
    ) -> None:
        """
        Initialize resolver.
        
        Args:
            profile_root: Root directory for profile storage.
                         Default: {REPO_ROOT}/config/profiles/
            schema_root: Root directory for schema files.
                        Default: {REPO_ROOT}/.windsurf/schemas/
            validator: Optional custom validator. If None, uses schema-aware validation.
            strict_mode: If True (default), fail closed on any validation issue.
        """
        self._strict_mode = strict_mode
        self._validator = validator
        
        # Determine roots via convention or environment
        if profile_root is None:
            profile_root = self._discover_profile_root()
        if schema_root is None:
            schema_root = self._discover_schema_root()
            
        self._profile_root = Path(profile_root)
        self._schema_root = Path(schema_root)
        
        # Runtime cache (non-persistent, per-instance)
        self._cache: dict[ProfileKey, ResolvedProfile] = {}
    
    def _discover_profile_root(self) -> Path:
        """Discover profile root via convention."""
        # Convention: profiles live in config/profiles/ relative to repo root
        repo_root = self._discover_repo_root()
        return repo_root / "config" / "profiles"
    
    def _discover_schema_root(self) -> Path:
        """Discover schema root via convention."""
        repo_root = self._discover_repo_root()
        return repo_root / ".windsurf" / "schemas"
    
    def _discover_repo_root(self) -> Path:
        """Discover repository root via marker file."""
        # Walk up from current file looking for pyproject.toml
        # We need to go up 4 levels: profiles/ -> runtime/ -> agentic_core/ -> repo_root
        current = Path(__file__).resolve().parent
        for parent in list(current.parents):
            if (parent / "pyproject.toml").exists():
                return parent
        # Fallback: assume standard structure
        return current.parent.parent.parent.parent
    
    def resolve(self, app_id: str, profile_type: str) -> ResolvedProfile:
        """
        Resolve profile for given app and type.
        
        Args:
            app_id: Application identifier (e.g., "apps_*", "org_*", "tenant_*")
            profile_type: Type of profile to resolve (must be in SCHEMA_REGISTRY)
            
        Returns:
            ResolvedProfile with validated configuration
            
        Raises:
            UnknownAppError: If app profile directory doesn't exist
            MissingProfileError: If profile file doesn't exist
            InvalidProfileError: If profile fails schema validation
            ProfileResolutionError: For other resolution failures
        """
        key = ProfileKey(app_id=app_id, profile_type=profile_type)
        
        # Check cache
        if key in self._cache:
            return self._cache[key]
        
        # Validate profile_type is known
        if profile_type not in self.SCHEMA_REGISTRY:
            raise ProfileResolutionError(
                f"Unknown profile_type: {profile_type}. "
                f"Known types: {list(self.SCHEMA_REGISTRY.keys())}"
            )
        
        # Locate app profile directory
        app_profile_dir = self._profile_root / app_id
        if not app_profile_dir.exists():
            raise UnknownAppError(
                f"No profile directory for app: {app_id}. "
                f"Expected: {app_profile_dir}"
            )
        
        # Locate profile file
        profile_path = app_profile_dir / f"{profile_type}.yaml"
        if not profile_path.exists():
            raise MissingProfileError(
                f"Profile not found: {profile_path} "
                f"for app={app_id}, type={profile_type}"
            )
        
        # Load and validate
        try:
            with open(profile_path, "r", encoding="utf-8") as f:
                raw_data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise InvalidProfileError(
                f"YAML parsing failed for {profile_path}: {e}"
            ) from e
        
        if raw_data is None:
            raise InvalidProfileError(f"Empty profile file: {profile_path}")
        
        # Schema validation
        schema_path = self._schema_root / self.SCHEMA_REGISTRY[profile_type]
        self._validate_profile(raw_data, schema_path, profile_path)
        
        # Extract version
        schema_version = raw_data.get("schema_version", "unknown")
        
        # Build typed payload (app-agnostic extraction of common fields)
        typed_payload = self._extract_typed_payload(raw_data, profile_type)
        
        # Construct result
        result = ResolvedProfile(
            key=key,
            raw_data=raw_data,
            source_path=profile_path,
            schema_version=schema_version,
            typed_payload=typed_payload,
        )
        
        # Cache and return
        self._cache[key] = result
        return result
    
    def _validate_profile(
        self, 
        profile_data: dict[str, Any], 
        schema_path: Path,
        profile_path: Path
    ) -> None:
        """
        Validate profile against its schema.
        
        Raises InvalidProfileError on validation failure.
        """
        if not schema_path.exists():
            if self._strict_mode:
                raise InvalidProfileError(
                    f"Schema not found: {schema_path} for profile {profile_path}"
                )
            return  # Non-strict: skip validation if schema missing
        
        # Load schema
        try:
            with open(schema_path, "r", encoding="utf-8") as f:
                schema = yaml.safe_load(f)
        except Exception as e:
            if self._strict_mode:
                raise InvalidProfileError(
                    f"Failed to load schema {schema_path}: {e}"
                ) from e
            return
        
        # Perform validation
        validation_errors = self._validate_against_schema(profile_data, schema)
        
        if validation_errors:
            raise InvalidProfileError(
                f"Profile validation failed for {profile_path}: "
                f"{'; '.join(validation_errors)}"
            )
    
    def _validate_against_schema(
        self, 
        data: dict[str, Any], 
        schema: dict[str, Any]
    ) -> list[str]:
        """
        Validate data against schema.
        
        Returns list of validation error messages (empty if valid).
        """
        errors: list[str] = []
        
        # Check required fields
        required_fields = schema.get("required_fields", [])
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        # Check fields structure if defined
        fields_spec = schema.get("fields", {})
        for field_name, field_spec in fields_spec.items():
            if field_name in data:
                field_value = data[field_name]
                field_type = field_spec.get("type")
                
                # Type checking
                if field_type == "string" and not isinstance(field_value, str):
                    errors.append(f"Field {field_name} must be string, got {type(field_value).__name__}")
                elif field_type == "boolean" and not isinstance(field_value, bool):
                    errors.append(f"Field {field_name} must be boolean, got {type(field_value).__name__}")
                elif field_type == "integer" and not isinstance(field_value, int):
                    errors.append(f"Field {field_name} must be integer, got {type(field_value).__name__}")
                elif field_type == "array" and not isinstance(field_value, list):
                    errors.append(f"Field {field_name} must be array, got {type(field_value).__name__}")
                elif field_type == "object" and not isinstance(field_value, dict):
                    errors.append(f"Field {field_name} must be object, got {type(field_value).__name__}")
                
                # Pattern checking for strings
                pattern = field_spec.get("pattern")
                if pattern and isinstance(field_value, str):
                    import re
                    if not re.match(pattern, field_value):
                        errors.append(f"Field {field_name} value '{field_value}' doesn't match pattern {pattern}")
                
                # Enum checking
                enum_values = field_spec.get("enum")
                if enum_values and field_value not in enum_values:
                    errors.append(f"Field {field_name} must be one of {enum_values}, got {field_value}")
        
        return errors
    
    def _extract_typed_payload(
        self, 
        raw_data: dict[str, Any], 
        profile_type: str
    ) -> dict[str, Any]:
        """
        Extract app-agnostic typed payload from raw profile data.
        
        This method is generic - it extracts common structure without
        app-specific knowledge. Apps interpret their own profile fields.
        """
        # Generic extraction of common fields
        payload: dict[str, Any] = {
            "app_id": raw_data.get("app_id"),
            "schema_version": raw_data.get("schema_version"),
            "profile_type": profile_type,
        }
        
        # Include validation behavior (critical for fail-closed)
        validation = raw_data.get("validation_behavior", {})
        payload["validation_behavior"] = validation
        
        # Include the app-specific config as opaque blob
        # Core doesn't interpret this - generic components pass it through
        config_keys = [
            "validation_rules", "adapter_config", "pipeline_config",
            "writeback_config", "learning_policy", "substrate_config",
            "payload_defaults", "synthesis_config", "source_filtering",
            "orchestration_config", "store_mapping", "identity_mapping",
            "cache_policies", "namespace_defaults", "routing_hints",
            "writeback_filter", "cross_app_behavior", "app_specific_handlers",
        ]
        
        for key in config_keys:
            if key in raw_data:
                payload[key] = raw_data[key]
        
        return payload
    
    def list_available_profiles(self, app_id: str) -> list[str]:
        """
        List available profile types for an app.
        
        Args:
            app_id: Application identifier
            
        Returns:
            List of available profile type strings
            
        Raises:
            UnknownAppError: If app profile directory doesn't exist
        """
        app_profile_dir = self._profile_root / app_id
        if not app_profile_dir.exists():
            raise UnknownAppError(f"No profile directory for app: {app_id}")
        
        available: list[str] = []
        for profile_type in self.SCHEMA_REGISTRY.keys():
            profile_path = app_profile_dir / f"{profile_type}.yaml"
            if profile_path.exists():
                available.append(profile_type)
        
        return available
    
    def clear_cache(self) -> None:
        """Clear the resolution cache."""
        self._cache.clear()
    
    def get_schema_path(self, profile_type: str) -> Path:
        """Get schema path for a profile type."""
        if profile_type not in self.SCHEMA_REGISTRY:
            raise ProfileResolutionError(f"Unknown profile_type: {profile_type}")
        return self._schema_root / self.SCHEMA_REGISTRY[profile_type]


def resolve_runtime_profile(app_id: str, profile_type: str) -> ResolvedProfile:
    """
    Convenience function for one-shot profile resolution.
    
    Uses default resolver configuration.
    
    Raises:
        UnknownAppError: If app unknown
        MissingProfileError: If profile missing
        InvalidProfileError: If profile invalid
    """
    resolver = RuntimeProfileResolver()
    return resolver.resolve(app_id, profile_type)
