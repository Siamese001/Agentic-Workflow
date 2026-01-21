"""
Pytest suite for Phase 4 Import Optimizations.

Tests verify that:
- Unified agents can be imported from clean paths
- Config constants are accessible via clean imports
- Facade pattern works correctly
"""
import inspect
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def test_unified_api_exports():
    """Verify cleaner import paths for Agents."""
    # New clean import
    # Old deep import
    from agentic_core.L5_safety.unified.UnifiedCodeValidatorAgent import (
        UnifiedCodeValidatorAgent as Original,
    )
    from agentic_core.unified import UnifiedCodeValidatorAgent

    assert UnifiedCodeValidatorAgent is Original
    assert inspect.isclass(UnifiedCodeValidatorAgent)


def test_unified_structure_validator_export():
    """Verify UnifiedStructureValidatorAgent is exported."""
    from agentic_core.L5_safety.unified.UnifiedStructureValidatorAgent import (
        UnifiedStructureValidatorAgent as Original,
    )
    from agentic_core.unified import UnifiedStructureValidatorAgent

    assert UnifiedStructureValidatorAgent is Original
    assert inspect.isclass(UnifiedStructureValidatorAgent)


def test_unified_code_enforcer_export():
    """Verify UnifiedCodeEnforcerAgent is exported."""
    from agentic_core.L5_safety.unified.UnifiedCodeEnforcerAgent import (
        UnifiedCodeEnforcerAgent as Original,
    )
    from agentic_core.unified import UnifiedCodeEnforcerAgent

    assert UnifiedCodeEnforcerAgent is Original


def test_unified_resource_manager_export():
    """Verify UnifiedResourceManagerAgent is exported."""
    from agentic_core.L5_safety.unified.UnifiedResourceManagerAgent import (
        UnifiedResourceManagerAgent as Original,
    )
    from agentic_core.unified import UnifiedResourceManagerAgent

    assert UnifiedResourceManagerAgent is Original


def test_config_api_exports():
    """Verify cleaner import paths for Config."""
    from agentic_core.config import DEFAULT_EXCLUDE_DIRS, SOVEREIGN_REGISTRY

    assert isinstance(SOVEREIGN_REGISTRY, dict)
    assert isinstance(DEFAULT_EXCLUDE_DIRS, frozenset)
    assert ".git" in DEFAULT_EXCLUDE_DIRS


def test_config_sovereign_registry_keys():
    """Verify SOVEREIGN_REGISTRY contains expected keys."""
    from agentic_core.config import SOVEREIGN_REGISTRY

    expected_keys = ['agentic_core', 'apps_rg', 'apps_lic', 'apps_shared', 'tests']
    for key in expected_keys:
        assert key in SOVEREIGN_REGISTRY, f"Missing key: {key}"


def test_config_healing_config():
    """Verify HEALING_CONFIG is accessible."""
    from agentic_core.config import HEALING_CONFIG

    assert isinstance(HEALING_CONFIG, dict)
    assert 'max_rounds' in HEALING_CONFIG
    assert 'global_budget' in HEALING_CONFIG


def test_config_active_canon_keys():
    """Verify ACTIVE_CANON_KEYS is accessible."""
    from agentic_core.config import ACTIVE_CANON_KEYS

    assert isinstance(ACTIVE_CANON_KEYS, list)
    assert len(ACTIVE_CANON_KEYS) == 20


def test_unified_validation_types():
    """Verify validation types are exported from unified."""
    from agentic_core.unified import (
        RuleSet,
        StructureViolation,
        StructureViolationType,
        ValidationReport,
        Violation,
        ViolationType,
    )

    # All should be importable
    assert RuleSet is not None
    assert ValidationReport is not None
    assert Violation is not None
    assert ViolationType is not None
    assert StructureViolation is not None
    assert StructureViolationType is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
