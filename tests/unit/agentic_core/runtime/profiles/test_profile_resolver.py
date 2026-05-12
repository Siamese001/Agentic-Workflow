"""
Tests for RuntimeProfileResolver

Verifies W9 P3 safety gate requirements:
1. Missing profile fails closed (UnknownAppError/MissingProfileError)
2. Invalid profile fails closed (InvalidProfileError)
3. Unknown app fails closed (UnknownAppError)
4. Adding new app requires profile only, not core edit
5. No app literals in new core components
6. Schema validation works

Constitutional §16: Zero app-specific literals in core.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest
import yaml

from agentic_core.runtime.profiles import (
    InvalidProfileError,
    MissingProfileError,
    ProfileKey,
    ProfileResolutionError,
    ResolvedProfile,
    RuntimeProfileResolver,
    UnknownAppError,
    resolve_runtime_profile,
)


class TestResolverInitialization:
    """Test resolver discovery and initialization."""
    
    def test_resolver_discovers_paths_via_convention(self):
        """Resolver discovers repo root and schema/profile paths automatically."""
        resolver = RuntimeProfileResolver()
        
        # Paths should be discovered
        assert resolver._profile_root.exists() or resolver._profile_root.parent.exists()
        assert resolver._schema_root.exists()
    
    def test_resolver_accepts_explicit_paths(self, tmp_path: Path):
        """Resolver accepts explicit profile and schema roots."""
        profile_root = tmp_path / "profiles"
        schema_root = tmp_path / "schemas"
        profile_root.mkdir()
        schema_root.mkdir()
        
        resolver = RuntimeProfileResolver(
            profile_root=profile_root,
            schema_root=schema_root,
        )
        
        assert resolver._profile_root == profile_root
        assert resolver._schema_root == schema_root
    
    def test_schema_registry_contains_all_w9_types(self):
        """SCHEMA_REGISTRY contains all 7 W9 profile types."""
        expected_types = {
            "u0_validation",
            "u0_adapter",
            "pipeline_defaults",
            "l6_learning",
            "l6_writeback",
            "c0_substrate",
            "u0_payload_defaults",
        }
        
        registry_keys = set(RuntimeProfileResolver.SCHEMA_REGISTRY.keys())
        assert expected_types == registry_keys, f"Missing types: {expected_types - registry_keys}"


class TestProfileResolutionSuccess:
    """Test successful profile resolution."""
    
    def test_resolve_valid_profile(self, tmp_path: Path):
        """Can resolve a valid profile."""
        # Setup
        profile_root = tmp_path / "profiles"
        schema_root = tmp_path / "schemas"
        profile_root.mkdir()
        schema_root.mkdir()
        
        # Create minimal schema
        schema = {
            "schema_version": "1.0",
            "profile_type": "test_profile",
            "required_fields": ["app_id", "config"],
            "fields": {
                "app_id": {"type": "string"},
                "config": {"type": "object"},
            },
        }
        with open(schema_root / "test_profile.schema.yaml", "w") as f:
            yaml.dump(schema, f)
        
        # Monkey-patch registry for test
        original_registry = RuntimeProfileResolver.SCHEMA_REGISTRY.copy()
        RuntimeProfileResolver.SCHEMA_REGISTRY["test_profile"] = "test_profile.schema.yaml"
        
        try:
            # Create app profile
            app_dir = profile_root / "apps_test"
            app_dir.mkdir()
            profile = {
                "schema_version": "1.0",
                "profile_type": "test_profile",
                "app_id": "apps_test",
                "config": {"key": "value"},
            }
            with open(app_dir / "test_profile.yaml", "w") as f:
                yaml.dump(profile, f)
            
            resolver = RuntimeProfileResolver(
                profile_root=profile_root,
                schema_root=schema_root,
            )
            
            result = resolver.resolve("apps_test", "test_profile")
            
            assert isinstance(result, ResolvedProfile)
            assert result.key.app_id == "apps_test"
            assert result.key.profile_type == "test_profile"
            assert result.schema_version == "1.0"
            assert result.source_path.exists()
        finally:
            RuntimeProfileResolver.SCHEMA_REGISTRY = original_registry
    
    def test_resolve_uses_cache(self, tmp_path: Path):
        """Resolver caches results and returns cached on second call."""
        profile_root = tmp_path / "profiles"
        schema_root = tmp_path / "schemas"
        profile_root.mkdir()
        schema_root.mkdir()
        
        # Minimal schema
        schema = {
            "schema_version": "1.0",
            "profile_type": "cached_test",
            "required_fields": ["app_id"],
            "fields": {"app_id": {"type": "string"}},
        }
        with open(schema_root / "cached_test.schema.yaml", "w") as f:
            yaml.dump(schema, f)
        
        original_registry = RuntimeProfileResolver.SCHEMA_REGISTRY.copy()
        RuntimeProfileResolver.SCHEMA_REGISTRY["cached_test"] = "cached_test.schema.yaml"
        
        try:
            app_dir = profile_root / "apps_cached"
            app_dir.mkdir()
            profile = {
                "schema_version": "1.0",
                "profile_type": "cached_test",
                "app_id": "apps_cached",
            }
            with open(app_dir / "cached_test.yaml", "w") as f:
                yaml.dump(profile, f)
            
            resolver = RuntimeProfileResolver(
                profile_root=profile_root,
                schema_root=schema_root,
            )
            
            # First call
            result1 = resolver.resolve("apps_cached", "cached_test")
            # Second call should return cached
            result2 = resolver.resolve("apps_cached", "cached_test")
            
            # Same object (cached)
            assert result1 is result2
        finally:
            RuntimeProfileResolver.SCHEMA_REGISTRY = original_registry
    
    def test_clear_cache(self, tmp_path: Path):
        """Cache can be cleared."""
        resolver = RuntimeProfileResolver()
        resolver._cache[ProfileKey("test", "test")] = None  # type: ignore
        
        resolver.clear_cache()
        
        assert len(resolver._cache) == 0


class TestFailClosedMissingProfile:
    """Test 1: Missing profile fails closed."""
    
    def test_missing_app_directory_raises_unknown_app(self, tmp_path: Path):
        """Unknown app directory raises UnknownAppError."""
        profile_root = tmp_path / "profiles"
        schema_root = tmp_path / "schemas"
        profile_root.mkdir()
        schema_root.mkdir()
        
        resolver = RuntimeProfileResolver(
            profile_root=profile_root,
            schema_root=schema_root,
        )
        
        with pytest.raises(UnknownAppError) as exc_info:
            resolver.resolve("apps_nonexistent", "u0_validation")
        
        assert "apps_nonexistent" in str(exc_info.value)
        assert "No profile directory" in str(exc_info.value)
    
    def test_missing_profile_file_raises_missing_profile(self, tmp_path: Path):
        """Missing profile file raises MissingProfileError."""
        profile_root = tmp_path / "profiles"
        schema_root = tmp_path / "schemas"
        profile_root.mkdir()
        schema_root.mkdir()
        
        # Create app dir but not the profile
        app_dir = profile_root / "apps_partial"
        app_dir.mkdir()
        
        resolver = RuntimeProfileResolver(
            profile_root=profile_root,
            schema_root=schema_root,
        )
        
        # Monkey-patch registry to have entry
        original_registry = RuntimeProfileResolver.SCHEMA_REGISTRY.copy()
        RuntimeProfileResolver.SCHEMA_REGISTRY["missing_test"] = "missing_test.schema.yaml"
        
        try:
            with pytest.raises(MissingProfileError) as exc_info:
                resolver.resolve("apps_partial", "missing_test")
            
            assert "missing_test.yaml" in str(exc_info.value)
        finally:
            RuntimeProfileResolver.SCHEMA_REGISTRY = original_registry
    
    def test_missing_profile_type_in_registry_raises_resolution_error(self, tmp_path: Path):
        """Unknown profile type raises ProfileResolutionError."""
        profile_root = tmp_path / "profiles"
        schema_root = tmp_path / "schemas"
        profile_root.mkdir()
        schema_root.mkdir()
        
        app_dir = profile_root / "apps_test"
        app_dir.mkdir()
        
        resolver = RuntimeProfileResolver(
            profile_root=profile_root,
            schema_root=schema_root,
        )
        
        with pytest.raises(ProfileResolutionError) as exc_info:
            resolver.resolve("apps_test", "unknown_type_xyz")
        
        assert "unknown_type_xyz" in str(exc_info.value)


class TestFailClosedInvalidProfile:
    """Test 2: Invalid profile fails closed."""
    
    def test_invalid_yaml_raises_invalid_profile(self, tmp_path: Path):
        """Invalid YAML raises InvalidProfileError."""
        profile_root = tmp_path / "profiles"
        schema_root = tmp_path / "schemas"
        profile_root.mkdir()
        schema_root.mkdir()
        
        # Minimal schema
        schema = {
            "schema_version": "1.0",
            "profile_type": "invalid_test",
            "required_fields": ["app_id"],
            "fields": {"app_id": {"type": "string"}},
        }
        with open(schema_root / "invalid_test.schema.yaml", "w") as f:
            yaml.dump(schema, f)
        
        original_registry = RuntimeProfileResolver.SCHEMA_REGISTRY.copy()
        RuntimeProfileResolver.SCHEMA_REGISTRY["invalid_test"] = "invalid_test.schema.yaml"
        
        try:
            app_dir = profile_root / "apps_invalid"
            app_dir.mkdir()
            # Write invalid YAML
            with open(app_dir / "invalid_test.yaml", "w") as f:
                f.write("invalid: yaml: content: [")
            
            resolver = RuntimeProfileResolver(
                profile_root=profile_root,
                schema_root=schema_root,
            )
            
            with pytest.raises(InvalidProfileError) as exc_info:
                resolver.resolve("apps_invalid", "invalid_test")
            
            assert "YAML parsing failed" in str(exc_info.value)
        finally:
            RuntimeProfileResolver.SCHEMA_REGISTRY = original_registry
    
    def test_empty_profile_raises_invalid_profile(self, tmp_path: Path):
        """Empty profile file raises InvalidProfileError."""
        profile_root = tmp_path / "profiles"
        schema_root = tmp_path / "schemas"
        profile_root.mkdir()
        schema_root.mkdir()
        
        schema = {
            "schema_version": "1.0",
            "profile_type": "empty_test",
            "required_fields": ["app_id"],
            "fields": {"app_id": {"type": "string"}},
        }
        with open(schema_root / "empty_test.schema.yaml", "w") as f:
            yaml.dump(schema, f)
        
        original_registry = RuntimeProfileResolver.SCHEMA_REGISTRY.copy()
        RuntimeProfileResolver.SCHEMA_REGISTRY["empty_test"] = "empty_test.schema.yaml"
        
        try:
            app_dir = profile_root / "apps_empty"
            app_dir.mkdir()
            # Empty file
            with open(app_dir / "empty_test.yaml", "w") as f:
                f.write("")
            
            resolver = RuntimeProfileResolver(
                profile_root=profile_root,
                schema_root=schema_root,
            )
            
            with pytest.raises(InvalidProfileError) as exc_info:
                resolver.resolve("apps_empty", "empty_test")
            
            assert "Empty profile file" in str(exc_info.value)
        finally:
            RuntimeProfileResolver.SCHEMA_REGISTRY = original_registry
    
    def test_missing_required_field_raises_invalid_profile(self, tmp_path: Path):
        """Profile missing required field raises InvalidProfileError."""
        profile_root = tmp_path / "profiles"
        schema_root = tmp_path / "schemas"
        profile_root.mkdir()
        schema_root.mkdir()
        
        schema = {
            "schema_version": "1.0",
            "profile_type": "required_test",
            "required_fields": ["app_id", "mandatory_field"],
            "fields": {
                "app_id": {"type": "string"},
                "mandatory_field": {"type": "string"},
            },
        }
        with open(schema_root / "required_test.schema.yaml", "w") as f:
            yaml.dump(schema, f)
        
        original_registry = RuntimeProfileResolver.SCHEMA_REGISTRY.copy()
        RuntimeProfileResolver.SCHEMA_REGISTRY["required_test"] = "required_test.schema.yaml"
        
        try:
            app_dir = profile_root / "apps_required"
            app_dir.mkdir()
            profile = {
                "schema_version": "1.0",
                "profile_type": "required_test",
                "app_id": "apps_required",
                # Missing mandatory_field
            }
            with open(app_dir / "required_test.yaml", "w") as f:
                yaml.dump(profile, f)
            
            resolver = RuntimeProfileResolver(
                profile_root=profile_root,
                schema_root=schema_root,
            )
            
            with pytest.raises(InvalidProfileError) as exc_info:
                resolver.resolve("apps_required", "required_test")
            
            assert "Missing required field: mandatory_field" in str(exc_info.value)
        finally:
            RuntimeProfileResolver.SCHEMA_REGISTRY = original_registry
    
    def test_wrong_field_type_raises_invalid_profile(self, tmp_path: Path):
        """Profile with wrong field type raises InvalidProfileError."""
        profile_root = tmp_path / "profiles"
        schema_root = tmp_path / "schemas"
        profile_root.mkdir()
        schema_root.mkdir()
        
        schema = {
            "schema_version": "1.0",
            "profile_type": "type_test",
            "required_fields": ["app_id", "count"],
            "fields": {
                "app_id": {"type": "string"},
                "count": {"type": "integer"},
            },
        }
        with open(schema_root / "type_test.schema.yaml", "w") as f:
            yaml.dump(schema, f)
        
        original_registry = RuntimeProfileResolver.SCHEMA_REGISTRY.copy()
        RuntimeProfileResolver.SCHEMA_REGISTRY["type_test"] = "type_test.schema.yaml"
        
        try:
            app_dir = profile_root / "apps_type"
            app_dir.mkdir()
            profile = {
                "schema_version": "1.0",
                "profile_type": "type_test",
                "app_id": "apps_type",
                "count": "not_an_integer",  # Wrong type
            }
            with open(app_dir / "type_test.yaml", "w") as f:
                yaml.dump(profile, f)
            
            resolver = RuntimeProfileResolver(
                profile_root=profile_root,
                schema_root=schema_root,
            )
            
            with pytest.raises(InvalidProfileError) as exc_info:
                resolver.resolve("apps_type", "type_test")
            
            assert "must be integer" in str(exc_info.value)
        finally:
            RuntimeProfileResolver.SCHEMA_REGISTRY = original_registry


class TestFailClosedUnknownApp:
    """Test 3: Unknown app fails closed."""
    
    def test_nonexistent_app_raises_unknown_app(self, tmp_path: Path):
        """Request for nonexistent app raises UnknownAppError."""
        profile_root = tmp_path / "profiles"
        schema_root = tmp_path / "schemas"
        profile_root.mkdir()
        schema_root.mkdir()
        
        resolver = RuntimeProfileResolver(
            profile_root=profile_root,
            schema_root=schema_root,
        )
        
        # Try various nonexistent app names
        for app_id in ["apps_unknown", "apps_new", "my_app", "test_123"]:
            with pytest.raises(UnknownAppError):
                resolver.resolve(app_id, "u0_validation")
    
    def test_list_available_profiles_raises_for_unknown_app(self, tmp_path: Path):
        """list_available_profiles raises UnknownAppError for unknown app."""
        profile_root = tmp_path / "profiles"
        schema_root = tmp_path / "schemas"
        profile_root.mkdir()
        schema_root.mkdir()
        
        resolver = RuntimeProfileResolver(
            profile_root=profile_root,
            schema_root=schema_root,
        )
        
        with pytest.raises(UnknownAppError):
            resolver.list_available_profiles("apps_nonexistent")


class TestNewAppRequiresProfileOnly:
    """Test 4: Adding new app requires profile only, not core edit."""
    
    def test_new_app_can_be_added_via_profile_only(self, tmp_path: Path):
        """New app can be added by creating profile directory and files only."""
        profile_root = tmp_path / "profiles"
        schema_root = tmp_path / "schemas"
        profile_root.mkdir()
        schema_root.mkdir()
        
        # Setup schema with pipeline_config instead of config
        schema = {
            "schema_version": "1.0",
            "profile_type": "new_app_test",
            "required_fields": ["app_id", "pipeline_config"],
            "fields": {
                "app_id": {"type": "string", "pattern": "^apps_[a-z_]+$"},
                "pipeline_config": {"type": "object"},
            },
        }
        with open(schema_root / "new_app_test.schema.yaml", "w") as f:
            yaml.dump(schema, f)
        
        original_registry = RuntimeProfileResolver.SCHEMA_REGISTRY.copy()
        RuntimeProfileResolver.SCHEMA_REGISTRY["new_app_test"] = "new_app_test.schema.yaml"
        
        try:
            # Create a BRAND NEW app via profiles only
            new_app_id = "apps_brand_new"
            new_app_dir = profile_root / new_app_id
            new_app_dir.mkdir()
            
            profile = {
                "schema_version": "1.0",
                "profile_type": "new_app_test",
                "app_id": new_app_id,
                "pipeline_config": {"custom": "value"},  # Use valid extraction key
            }
            with open(new_app_dir / "new_app_test.yaml", "w") as f:
                yaml.dump(profile, f)
            
            # Resolve WITHOUT any code changes to core
            resolver = RuntimeProfileResolver(
                profile_root=profile_root,
                schema_root=schema_root,
            )
            
            result = resolver.resolve(new_app_id, "new_app_test")
            
            assert result.key.app_id == new_app_id
            assert result.typed_payload["pipeline_config"]["custom"] == "value"
        finally:
            RuntimeProfileResolver.SCHEMA_REGISTRY = original_registry


class TestNoAppLiteralsInCore:
    """Test 5: No app literals in new core components."""
    
    def test_resolver_source_no_hardcoded_app_names(self):
        """Resolver source code contains no hardcoded app names."""
        import agentic_core.runtime.profiles.profile_resolver as resolver_module
        
        source_path = Path(resolver_module.__file__)
        source_code = source_path.read_text()
        
        # Forbidden patterns
        forbidden_patterns = [
            "apps_rg",
            "apps_lic",
            "apps_research",
            "apps_qna",
            "apps_exec",
            "apps_rfp",
            "apps_underwriting_ai",
            "apps_eval",
            "apps_architect",
            "apps_repo_brief",
            "apps_shared",
        ]
        
        for pattern in forbidden_patterns:
            assert pattern not in source_code, (
                f"Forbidden app literal '{pattern}' found in resolver source. "
                "Core must be app-agnostic."
            )
    
    def test_resolver_init_no_app_literals(self):
        """Resolver __init__.py contains no app literals."""
        import agentic_core.runtime.profiles as profiles_pkg
        
        init_path = Path(profiles_pkg.__file__)
        init_code = init_path.read_text()
        
        forbidden_patterns = [
            "apps_rg",
            "apps_lic",
            "apps_research",
        ]
        
        for pattern in forbidden_patterns:
            assert pattern not in init_code, (
                f"App literal '{pattern}' found in __init__.py"
            )


class TestSchemaValidation:
    """Test 6: Schema validation works."""
    
    def test_valid_profile_passes_validation(self, tmp_path: Path):
        """Valid profile passes schema validation."""
        profile_root = tmp_path / "profiles"
        schema_root = tmp_path / "schemas"
        profile_root.mkdir()
        schema_root.mkdir()
        
        schema = {
            "schema_version": "1.0",
            "profile_type": "valid_test",
            "required_fields": ["app_id"],
            "fields": {"app_id": {"type": "string"}},
        }
        with open(schema_root / "valid_test.schema.yaml", "w") as f:
            yaml.dump(schema, f)
        
        original_registry = RuntimeProfileResolver.SCHEMA_REGISTRY.copy()
        RuntimeProfileResolver.SCHEMA_REGISTRY["valid_test"] = "valid_test.schema.yaml"
        
        try:
            app_dir = profile_root / "apps_valid"
            app_dir.mkdir()
            profile = {
                "schema_version": "1.0",
                "profile_type": "valid_test",
                "app_id": "apps_valid",
            }
            with open(app_dir / "valid_test.yaml", "w") as f:
                yaml.dump(profile, f)
            
            resolver = RuntimeProfileResolver(
                profile_root=profile_root,
                schema_root=schema_root,
            )
            
            # Should not raise
            result = resolver.resolve("apps_valid", "valid_test")
            assert result is not None
        finally:
            RuntimeProfileResolver.SCHEMA_REGISTRY = original_registry
    
    def test_enum_validation_works(self, tmp_path: Path):
        """Enum field validation works."""
        profile_root = tmp_path / "profiles"
        schema_root = tmp_path / "schemas"
        profile_root.mkdir()
        schema_root.mkdir()
        
        schema = {
            "schema_version": "1.0",
            "profile_type": "enum_test",
            "required_fields": ["app_id", "mode"],
            "fields": {
                "app_id": {"type": "string"},
                "mode": {"type": "string", "enum": ["strict", "permissive"]},
            },
        }
        with open(schema_root / "enum_test.schema.yaml", "w") as f:
            yaml.dump(schema, f)
        
        original_registry = RuntimeProfileResolver.SCHEMA_REGISTRY.copy()
        RuntimeProfileResolver.SCHEMA_REGISTRY["enum_test"] = "enum_test.schema.yaml"
        
        try:
            app_dir = profile_root / "apps_enum"
            app_dir.mkdir()
            # Invalid enum value
            profile = {
                "schema_version": "1.0",
                "profile_type": "enum_test",
                "app_id": "apps_enum",
                "mode": "invalid_mode",
            }
            with open(app_dir / "enum_test.yaml", "w") as f:
                yaml.dump(profile, f)
            
            resolver = RuntimeProfileResolver(
                profile_root=profile_root,
                schema_root=schema_root,
            )
            
            with pytest.raises(InvalidProfileError) as exc_info:
                resolver.resolve("apps_enum", "enum_test")
            
            assert "must be one of" in str(exc_info.value)
        finally:
            RuntimeProfileResolver.SCHEMA_REGISTRY = original_registry
    
    def test_pattern_validation_works(self, tmp_path: Path):
        """Pattern field validation works."""
        profile_root = tmp_path / "profiles"
        schema_root = tmp_path / "schemas"
        profile_root.mkdir()
        schema_root.mkdir()
        
        schema = {
            "schema_version": "1.0",
            "profile_type": "pattern_test",
            "required_fields": ["app_id"],
            "fields": {
                "app_id": {"type": "string", "pattern": "^apps_[a-z_]+$"},
            },
        }
        with open(schema_root / "pattern_test.schema.yaml", "w") as f:
            yaml.dump(schema, f)
        
        original_registry = RuntimeProfileResolver.SCHEMA_REGISTRY.copy()
        RuntimeProfileResolver.SCHEMA_REGISTRY["pattern_test"] = "pattern_test.schema.yaml"
        
        try:
            app_dir = profile_root / "apps_pattern"
            app_dir.mkdir()
            # Invalid pattern
            profile = {
                "schema_version": "1.0",
                "profile_type": "pattern_test",
                "app_id": "INVALID_APP_ID",
            }
            with open(app_dir / "pattern_test.yaml", "w") as f:
                yaml.dump(profile, f)
            
            resolver = RuntimeProfileResolver(
                profile_root=profile_root,
                schema_root=schema_root,
            )
            
            with pytest.raises(InvalidProfileError) as exc_info:
                resolver.resolve("apps_pattern", "pattern_test")
            
            assert "doesn't match pattern" in str(exc_info.value)
        finally:
            RuntimeProfileResolver.SCHEMA_REGISTRY = original_registry


class TestConvenienceFunction:
    """Test convenience function resolve_runtime_profile."""
    
    def test_convenience_function_exists(self):
        """Convenience function is importable."""
        from agentic_core.runtime.profiles import resolve_runtime_profile
        assert callable(resolve_runtime_profile)


class TestTypedPayloadExtraction:
    """Test typed payload extraction."""
    
    def test_typed_payload_contains_expected_fields(self, tmp_path: Path):
        """Typed payload contains expected structure."""
        profile_root = tmp_path / "profiles"
        schema_root = tmp_path / "schemas"
        profile_root.mkdir()
        schema_root.mkdir()
        
        schema = {
            "schema_version": "1.0",
            "profile_type": "payload_test",
            "required_fields": ["app_id", "validation_rules"],
            "fields": {
                "app_id": {"type": "string"},
                "validation_rules": {"type": "object"},
            },
        }
        with open(schema_root / "payload_test.schema.yaml", "w") as f:
            yaml.dump(schema, f)
        
        original_registry = RuntimeProfileResolver.SCHEMA_REGISTRY.copy()
        RuntimeProfileResolver.SCHEMA_REGISTRY["payload_test"] = "payload_test.schema.yaml"
        
        try:
            app_dir = profile_root / "apps_payload"
            app_dir.mkdir()
            profile = {
                "schema_version": "1.0",
                "profile_type": "payload_test",
                "app_id": "apps_payload",
                "validation_rules": {
                    "required_fields": ["tenant_id"],
                    "max_size": 1000,
                },
            }
            with open(app_dir / "payload_test.yaml", "w") as f:
                yaml.dump(profile, f)
            
            resolver = RuntimeProfileResolver(
                profile_root=profile_root,
                schema_root=schema_root,
            )
            
            result = resolver.resolve("apps_payload", "payload_test")
            
            # Typed payload should have extracted fields
            assert "app_id" in result.typed_payload
            assert "schema_version" in result.typed_payload
            assert "profile_type" in result.typed_payload
            assert "validation_rules" in result.typed_payload
            assert result.typed_payload["validation_rules"]["max_size"] == 1000
        finally:
            RuntimeProfileResolver.SCHEMA_REGISTRY = original_registry


class TestListAvailableProfiles:
    """Test list_available_profiles functionality."""
    
    def test_list_available_profiles_returns_existing(self, tmp_path: Path):
        """Returns only profiles that exist on disk."""
        profile_root = tmp_path / "profiles"
        schema_root = tmp_path / "schemas"
        profile_root.mkdir()
        schema_root.mkdir()
        
        # Create multiple schemas
        for profile_type in ["type_a", "type_b", "type_c"]:
            schema = {
                "schema_version": "1.0",
                "profile_type": profile_type,
                "required_fields": ["app_id"],
                "fields": {"app_id": {"type": "string"}},
            }
            with open(schema_root / f"{profile_type}.schema.yaml", "w") as f:
                yaml.dump(schema, f)
        
        original_registry = RuntimeProfileResolver.SCHEMA_REGISTRY.copy()
        for pt in ["type_a", "type_b", "type_c"]:
            RuntimeProfileResolver.SCHEMA_REGISTRY[pt] = f"{pt}.schema.yaml"
        
        try:
            app_dir = profile_root / "apps_multi"
            app_dir.mkdir()
            
            # Create only type_a and type_c profiles
            for pt in ["type_a", "type_c"]:
                profile = {
                    "schema_version": "1.0",
                    "profile_type": pt,
                    "app_id": "apps_multi",
                }
                with open(app_dir / f"{pt}.yaml", "w") as f:
                    yaml.dump(profile, f)
            
            resolver = RuntimeProfileResolver(
                profile_root=profile_root,
                schema_root=schema_root,
            )
            
            available = resolver.list_available_profiles("apps_multi")
            
            assert "type_a" in available
            assert "type_b" not in available  # Not created
            assert "type_c" in available
        finally:
            RuntimeProfileResolver.SCHEMA_REGISTRY = original_registry


class TestProfileKey:
    """Test ProfileKey dataclass."""
    
    def test_profile_key_creation(self):
        """ProfileKey can be created with app_id and profile_type."""
        key = ProfileKey(app_id="apps_test", profile_type="u0_validation")
        assert key.app_id == "apps_test"
        assert key.profile_type == "u0_validation"
    
    def test_profile_key_requires_non_empty(self):
        """ProfileKey requires non-empty values."""
        with pytest.raises(ValueError):
            ProfileKey(app_id="", profile_type="test")
        
        with pytest.raises(ValueError):
            ProfileKey(app_id="test", profile_type="")


class TestExceptionHierarchy:
    """Test exception class hierarchy."""
    
    def test_exceptions_inherit_from_base(self):
        """All exceptions inherit from ProfileResolutionError."""
        assert issubclass(UnknownAppError, ProfileResolutionError)
        assert issubclass(InvalidProfileError, ProfileResolutionError)
        assert issubclass(MissingProfileError, ProfileResolutionError)
