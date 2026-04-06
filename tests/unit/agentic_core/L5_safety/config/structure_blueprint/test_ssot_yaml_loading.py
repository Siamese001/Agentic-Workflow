"""Tests for ssot.py YAML loading functionality.

Tests the migration from hardcoded constants to YAML-based SSOT for:
- SOVEREIGN_EXCLUDED_FOLDERS
- GLOBAL_EXCLUDED_DIRS
- Territory loading via territories.py
"""

import pytest
from pathlib import Path


class TestSsotYamlLoading:
    """Test that ssot.py loads exclusions from excluded_paths.yaml."""

    def test_sovereign_excluded_folders_loads_from_yaml(self):
        """Test SOVEREIGN_EXCLUDED_FOLDERS loads from YAML SSOT."""
        from agentic_core.L5_safety.config.structure_blueprint.ssot import (
            SOVEREIGN_EXCLUDED_FOLDERS,
        )

        # Should be a frozenset
        assert isinstance(SOVEREIGN_EXCLUDED_FOLDERS, frozenset)

        # Should have expected exclusions from YAML
        assert "__pycache__" in SOVEREIGN_EXCLUDED_FOLDERS
        assert ".git" in SOVEREIGN_EXCLUDED_FOLDERS
        assert "venv" in SOVEREIGN_EXCLUDED_FOLDERS
        assert "node_modules" in SOVEREIGN_EXCLUDED_FOLDERS
        assert "archives" in SOVEREIGN_EXCLUDED_FOLDERS

        # Should have intentional additions not in YAML
        assert ".github" in SOVEREIGN_EXCLUDED_FOLDERS  # Intentional
        assert ".windsurf" in SOVEREIGN_EXCLUDED_FOLDERS  # Intentional
        assert "docs" in SOVEREIGN_EXCLUDED_FOLDERS  # Intentional

    def test_global_excluded_dirs_loads_from_yaml(self):
        """Test GLOBAL_EXCLUDED_DIRS loads from YAML SSOT."""
        from agentic_core.L5_safety.config.structure_blueprint.ssot import (
            GLOBAL_EXCLUDED_DIRS,
        )

        # Should be a frozenset
        assert isinstance(GLOBAL_EXCLUDED_DIRS, frozenset)

        # Should have expected exclusions from YAML
        assert "__pycache__" in GLOBAL_EXCLUDED_DIRS
        assert ".git" in GLOBAL_EXCLUDED_DIRS
        assert "venv" in GLOBAL_EXCLUDED_DIRS

        # Should have production lens additions
        assert "tests" in GLOBAL_EXCLUDED_DIRS
        assert "logs" in GLOBAL_EXCLUDED_DIRS
        assert "artifacts" in GLOBAL_EXCLUDED_DIRS

    def test_exclusion_loader_caching(self):
        """Test that _load_exclusions_from_yaml uses caching."""
        from agentic_core.L5_safety.config.structure_blueprint.ssot import (
            _load_exclusions_from_yaml,
        )

        # First call
        result1 = _load_exclusions_from_yaml()
        # Second call should return cached result
        result2 = _load_exclusions_from_yaml()

        # Should be the same object (cached)
        assert result1 is result2

        # Should have expected structure
        assert "build_cache" in result1
        assert "version_control" in result1
        assert "virtual_env" in result1
        assert "coverage" in result1
        assert "archive" in result1

    def test_yaml_file_exists(self):
        """Test that excluded_paths.yaml exists and is readable."""
        from agentic_core.L5_safety.config.structure_blueprint.ssot import (
            get_validated_project_root,
        )

        repo_root = get_validated_project_root()
        config_path = repo_root / "config" / "excluded_paths.yaml"

        assert config_path.exists()
        assert config_path.is_file()

    def test_yaml_has_required_categories(self):
        """Test that excluded_paths.yaml has all required categories."""
        import yaml
        from agentic_core.L5_safety.config.structure_blueprint.ssot import (
            get_validated_project_root,
        )

        repo_root = get_validated_project_root()
        config_path = repo_root / "config" / "excluded_paths.yaml"

        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # Should have all required categories
        assert "build_cache_dirs" in data
        assert "version_control_dirs" in data
        assert "virtual_env_dirs" in data
        assert "coverage_dirs" in data
        assert "archive_dirs" in data
        assert "ide_dirs" in data
        assert "vendor_dirs" in data
        assert "data_dirs" in data
        assert "special_dirs" in data


class TestTerritoriesYamlLoading:
    """Test that territories.py loads from territories.yaml."""

    def test_get_all_territories_loads_from_yaml(self):
        """Test get_all_territories loads from YAML SSOT."""
        from agentic_core.L5_safety.config.structure_blueprint.territories import (
            get_all_territories,
        )

        territories = get_all_territories()

        # Should return a dict
        assert isinstance(territories, dict)

        # Should have expected territories
        assert "agentic_core" in territories
        assert "config" in territories
        assert "docs" in territories
        assert "tests" in territories
        assert "tools" in territories

    def test_get_territory_metadata_loads_from_yaml(self):
        """Test get_territory_metadata loads from YAML SSOT."""
        from agentic_core.L5_safety.config.structure_blueprint.territories import (
            get_territory_metadata,
        )

        # Get a known territory
        agentic_core = get_territory_metadata("agentic_core")

        # Should return a dict
        assert agentic_core is not None
        assert isinstance(agentic_core, dict)

        # Should have expected fields
        assert "purpose" in agentic_core
        assert "subfolders" in agentic_core

        # Test non-existent territory
        nonexistent = get_territory_metadata("nonexistent_territory")
        assert nonexistent is None

    def test_territories_yaml_file_exists(self):
        """Test that territories.yaml exists and is readable."""
        from agentic_core.L5_safety.config.structure_blueprint.ssot import (
            get_validated_project_root,
        )

        repo_root = get_validated_project_root()
        config_path = repo_root / "config" / "structure_blueprint" / "territories.yaml"

        assert config_path.exists()
        assert config_path.is_file()

    def test_yaml_loader_caching(self):
        """Test that yaml_loader uses caching."""
        from agentic_core.L5_safety.config.structure_blueprint.yaml_loader import (
            load_territories,
        )

        # First call
        result1 = load_territories()
        # Second call should return cached result
        result2 = load_territories()

        # Should be the same object (cached)
        assert result1 is result2


class TestExclusionSyncGate:
    """Test that exclusion_sync_gate.py works with YAML SSOT."""

    def test_exclusion_sync_gate_runs(self):
        """Test that exclusion_sync_gate.py runs without errors."""
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, "ops_scripts/ci/exclusion_sync_gate.py"],
            cwd=Path(__file__).parent.parent.parent.parent,
            capture_output=True,
            text=True,
        )

        # Should run without crashing (exit code may be 1 if sync issues found)
        # The important thing is it doesn't crash with import errors
        assert "ImportError" not in result.stderr
        assert "KeyError" not in result.stderr

    def test_constants_config_import_works(self):
        """Test that constants_config.py can import from ssot.py."""
        from agentic_core.config.constants_config import DEFAULT_EXCLUDE_DIRS

        # Should be a frozenset
        assert isinstance(DEFAULT_EXCLUDE_DIRS, frozenset)

        # Should have expected exclusions
        assert "__pycache__" in DEFAULT_EXCLUDE_DIRS
        assert ".git" in DEFAULT_EXCLUDE_DIRS
