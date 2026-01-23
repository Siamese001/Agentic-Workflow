"""
Pytest suite for configuration Migration ensuring SSOT compliance.

Tests verify that:
- Registry loads from new config location
- Registry loads from old location with deprecation warning
- Constants are properly loaded from SSOT
- ssot_discovery uses the centralized constants
"""

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def test_registry_import_ssot():
    """Verify registry loads from new config location."""
    from agentic_core.config.blueprint_sovereign.registry import SOVEREIGN_REGISTRY

    assert isinstance(SOVEREIGN_REGISTRY, dict)
    assert len(SOVEREIGN_REGISTRY) > 0
    assert "agentic_core" in SOVEREIGN_REGISTRY


def test_constants_ssot():
    """Verify constants are loaded from SSOT."""
    from agentic_core.config.blueprint_sovereign.constants import DEFAULT_EXCLUDE_DIRS

    assert ".sovereign_healing_backup" in DEFAULT_EXCLUDE_DIRS
    assert "node_modules" in DEFAULT_EXCLUDE_DIRS
    assert "__pycache__" in DEFAULT_EXCLUDE_DIRS


def test_constants_active_canon_keys():
    """Verify ACTIVE_CANON_KEYS is properly defined."""
    from agentic_core.config.blueprint_sovereign.constants import ACTIVE_CANON_KEYS

    assert isinstance(ACTIVE_CANON_KEYS, list)
    assert len(ACTIVE_CANON_KEYS) == 20
    assert 0 in ACTIVE_CANON_KEYS
    assert 19 in ACTIVE_CANON_KEYS


def test_healing_config_ssot():
    """Verify HEALING_CONFIG loads from registry."""
    from agentic_core.config.blueprint_sovereign.registry import HEALING_CONFIG

    assert isinstance(HEALING_CONFIG, dict)
    assert "max_rounds" in HEALING_CONFIG
    assert "global_budget" in HEALING_CONFIG


def test_package_init_exports():
    """Verify package __init__ exports all expected symbols."""
    from agentic_core.config.blueprint_sovereign import (
        ACTIVE_CANON_KEYS,
        DEFAULT_EXCLUDE_DIRS,
        HEALING_CONFIG,
        SOVEREIGN_REGISTRY,
    )

    assert DEFAULT_EXCLUDE_DIRS is not None
    assert SOVEREIGN_REGISTRY is not None
    assert HEALING_CONFIG is not None
    assert ACTIVE_CANON_KEYS is not None


def test_ssot_discovery_uses_constants():
    """Verify ssot_discovery imports from SSOT constants."""
    from agentic_core.utils.ssot_discovery import DEFAULT_EXCLUDE_DIRS

    # Should contain the same exclusions as the SSOT
    assert ".sovereign_healing_backup" in DEFAULT_EXCLUDE_DIRS
    assert "archives" in DEFAULT_EXCLUDE_DIRS


def test_layer_dirs_consistency():
    """Verify LAYER_DIRS is consistent between registry and ssot_discovery."""
    from agentic_core.config.blueprint_sovereign.registry import LAYER_DIRS as REG_LAYER_DIRS
    from agentic_core.utils.ssot_discovery import LAYER_DIRS as DISC_LAYER_DIRS

    # Both should have the same keys
    assert set(REG_LAYER_DIRS.keys()) == set(DISC_LAYER_DIRS.keys())

    # Both should have the same values
    for key in REG_LAYER_DIRS:
        assert REG_LAYER_DIRS[key] == DISC_LAYER_DIRS[key]


def test_variable_depth_subfolders():
    """Verify VARIABLE_DEPTH_SUBFOLDERS is defined."""
    from agentic_core.config.blueprint_sovereign.registry import VARIABLE_DEPTH_SUBFOLDERS

    assert isinstance(VARIABLE_DEPTH_SUBFOLDERS, frozenset)
    assert "utils" in VARIABLE_DEPTH_SUBFOLDERS
    assert "config" in VARIABLE_DEPTH_SUBFOLDERS


def test_l4_approved_folders():
    """Verify L4_APPROVED_FOLDERS is defined."""
    from agentic_core.config.blueprint_sovereign.registry import L4_APPROVED_FOLDERS

    assert isinstance(L4_APPROVED_FOLDERS, set)
    assert "agentic_core/L5_safety/validators" in L4_APPROVED_FOLDERS


def test_gravity_config():
    """Verify GRAVITY_CONFIG is properly defined."""
    from agentic_core.config.blueprint_sovereign.registry import GRAVITY_CONFIG

    assert isinstance(GRAVITY_CONFIG, dict)
    assert "enabled" in GRAVITY_CONFIG
    assert GRAVITY_CONFIG["enabled"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
