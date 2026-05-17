"""Tests for L0_routing.config.path_constants module."""

from pathlib import Path
from unittest.mock import patch

import pytest

from agentic_core.L0_routing.config import path_constants


class TestPathConstants:
    """Test suite for path constants module."""

    def test_heal_confidence_defaults(self):
        """High / medium paired SSOT defaults satisfy ordering invariant."""
        from agentic_core.L2_execution.healers.routing_thresholds_ssot import (
            DEFAULT_HEAL_CONFIDENCE_HIGH,
            DEFAULT_HEAL_CONFIDENCE_MEDIUM,
        )

        assert DEFAULT_HEAL_CONFIDENCE_MEDIUM < DEFAULT_HEAL_CONFIDENCE_HIGH
        assert hasattr(path_constants, "SSOT_SCORE_THRESHOLD_DET")

    def test_ssot_score_thresholds(self):
        """Test SSOT score thresholds for routing."""
        assert path_constants.SSOT_SCORE_THRESHOLD_DET == 13
        assert path_constants.SSOT_SCORE_THRESHOLD_QWEN == 26

    def test_consensus_majority_threshold(self):
        """Test consensus majority threshold calculation."""
        # Test various juror counts
        assert path_constants.consensus_majority_threshold(3) == 2 / 3
        assert path_constants.consensus_majority_threshold(4) == 3 / 4
        assert path_constants.consensus_majority_threshold(5) == 3 / 5
        assert path_constants.consensus_majority_threshold(7) == 4 / 7

    def test_consensus_majority_threshold_invalid(self):
        """Test consensus majority threshold raises on invalid input."""
        with pytest.raises(ValueError, match="juror_count must be >= 1"):
            path_constants.consensus_majority_threshold(0)
        with pytest.raises(ValueError, match="juror_count must be >= 1"):
            path_constants.consensus_majority_threshold(-1)

    def test_agentic_core_layers(self):
        """Test AGENTIC_CORE_LAYERS constant."""
        expected_layers = [
            "L0_routing",
            "L1_cognition",
            "L2_execution",
            "L3_orchestration",
            "L4_state",
            "L5_safety",
            "L6_observability",
        ]
        assert path_constants.AGENTIC_CORE_LAYERS == expected_layers

    def test_apps_packages(self):
        """Test APPS_PACKAGES constant."""
        expected_apps = [
            "apps_lic",
            "apps_rg",
            "apps_eval",
            "apps_exec",
            "apps_research",
            "apps_rfp",
            "apps_shared",
            "apps_underwriting_ai",
        ]
        assert path_constants.APPS_PACKAGES == expected_apps

    def test_project_root_markers(self):
        """Test PROJECT_ROOT_MARKERS includes expected markers."""
        assert ".git" in path_constants.PROJECT_ROOT_MARKERS
        assert "pyproject.toml" in path_constants.PROJECT_ROOT_MARKERS

    def test_directory_constants(self):
        """Test directory path constants are defined."""
        assert path_constants.AGENTIC_CORE_DIR == "agentic_core"
        assert path_constants.ARTIFACTS_DIR == "artifacts"
        assert path_constants.ADG_ARTIFACTS_DIR == "artifacts/adg"
        assert path_constants.TOOLS_DIR == "tools"
        assert path_constants.TESTS_DIR == "tests"

    def test_get_validated_project_root(self):
        """Test project root detection."""
        # This test should work in the actual repo
        root = path_constants.get_validated_project_root()
        assert isinstance(root, Path)
        assert root.exists()

    def test_get_validated_project_root_caching(self):
        """Test project root detection is cached."""
        root1 = path_constants.get_validated_project_root()
        root2 = path_constants.get_validated_project_root()
        assert root1 == root2

    def test_get_apps_directories(self):
        """Test dynamic apps directory discovery."""
        apps_dirs = path_constants.get_apps_directories()
        assert isinstance(apps_dirs, list)
        assert all(isinstance(d, str) for d in apps_dirs)
        assert all(d.startswith("apps_") for d in apps_dirs)

    def test_get_apps_directories_caching(self):
        """Test apps directories discovery is cached."""
        apps1 = path_constants.get_apps_directories()
        apps2 = path_constants.get_apps_directories()
        assert apps1 == apps2

    def test_get_all_apps_paths(self):
        """Test getting absolute paths for all apps directories."""
        apps_paths = path_constants.get_all_apps_paths()
        assert isinstance(apps_paths, list)
        assert all(isinstance(p, Path) for p in apps_paths)
        assert all(p.exists() for p in apps_paths)

    def test_layer_roots(self):
        """Test LAYER_ROOTS constant."""
        assert "L0_routing" in path_constants.LAYER_ROOTS
        assert "L1_cognition" in path_constants.LAYER_ROOTS
        assert "L2_execution" in path_constants.LAYER_ROOTS
        assert "L3_orchestration" in path_constants.LAYER_ROOTS
        assert "L4_state" in path_constants.LAYER_ROOTS
        assert "L5_safety" in path_constants.LAYER_ROOTS
        assert "L6_observability" in path_constants.LAYER_ROOTS

    def test_root_whitelist(self):
        """Test ROOT_WHITELIST includes expected directories."""
        assert "agentic_core" in path_constants.ROOT_WHITELIST
        assert "tests" in path_constants.ROOT_WHITELIST
        assert "tools" in path_constants.ROOT_WHITELIST

    def test_flat_directories(self):
        """Test FLAT_DIRECTORIES constant."""
        assert "config" in path_constants.FLAT_DIRECTORIES
        assert "cache" in path_constants.FLAT_DIRECTORIES
        assert "interfaces" in path_constants.FLAT_DIRECTORIES

    def test_validate_path_within_project(self):
        """Test path validation within project root."""
        root = path_constants.get_validated_project_root()
        
        # Valid path
        valid_path = root / "agentic_core"
        assert path_constants.validate_path_within_project(valid_path, root) is True
        
        # Invalid path (outside root)
        invalid_path = Path("/tmp/some/path")
        assert path_constants.validate_path_within_project(invalid_path, root) is False

    def test_safe_path_join(self):
        """Test safe path joining with validation."""
        root = path_constants.get_validated_project_root()
        
        # Valid join
        result = path_constants.safe_path_join(root, "agentic_core", "L0_routing")
        assert isinstance(result, Path)
        assert result.is_absolute()

    def test_safe_path_join_invalid(self):
        """Test safe path join raises on invalid path."""
        root = path_constants.get_validated_project_root()
        
        # This should raise ValueError if the result is outside root
        with pytest.raises(ValueError, match="SAFETY VIOLATION"):
            # Try to escape the root using parent directory
            path_constants.safe_path_join(root, "..", "etc")

    def test_validate_flat_directory(self):
        """Test flat directory validation."""
        # Valid flat structure
        valid_path = ("config", "file.py")
        assert path_constants.validate_flat_directory(valid_path) is None
        
        # Invalid nested structure
        invalid_path = ("config", "subdir", "file.py")
        result = path_constants.validate_flat_directory(invalid_path)
        assert result is not None
        assert result["domain"] == "config"
        assert result["illegal_child"] == "subdir"

    def test_validate_flat_directory_pycache_allowed(self):
        """Test __pycache__ is allowed in flat directories."""
        # __pycache__ should not trigger violation
        pycache_path = ("config", "__pycache__", "file.pyc")
        result = path_constants.validate_flat_directory(pycache_path)
        assert result is None

    def test_forbidden_folder_pattern(self):
        """Test forbidden folder pattern regex."""
        import re
        
        pattern = path_constants.FORBIDDEN_FOLDER_PATTERN
        assert pattern.match("1_something")
        assert pattern.match("99_folder")
        assert not pattern.match("valid_folder")
        assert not pattern.match("folder_1")

    def test_forbidden_root_folders(self):
        """Test forbidden root folders constant."""
        assert "legacy_code" in path_constants.FORBIDDEN_ROOT_FOLDERS
        assert "legacy_engines" in path_constants.FORBIDDEN_ROOT_FOLDERS
        assert "old_core" in path_constants.FORBIDDEN_ROOT_FOLDERS

    def test_depth_rules(self):
        """Test DEPTH_RULES constant."""
        assert "agentic_core" in path_constants.DEPTH_RULES
        assert "tests" in path_constants.DEPTH_RULES
        assert path_constants.DEPTH_RULES["agentic_core"] == 3
        assert path_constants.DEPTH_RULES["tests"] == 2

    def test_allowed_duplicate_filenames(self):
        """Test ALLOWED_DUPLICATE_FILENAMES constant."""
        assert "__init__.py" in path_constants.ALLOWED_DUPLICATE_FILENAMES
        assert "config.py" in path_constants.ALLOWED_DUPLICATE_FILENAMES
        assert "utils.py" in path_constants.ALLOWED_DUPLICATE_FILENAMES

    def test_global_excluded_dirs(self):
        """Test GLOBAL_EXCLUDED_DIRS constant."""
        assert ".git" in path_constants.GLOBAL_EXCLUDED_DIRS
        assert "__pycache__" in path_constants.GLOBAL_EXCLUDED_DIRS
        assert "node_modules" in path_constants.GLOBAL_EXCLUDED_DIRS

    def test_public_api_exports(self):
        """Test that public API constants are exported."""
        assert hasattr(path_constants, "get_validated_project_root")
        assert hasattr(path_constants, "get_apps_directories")
        assert hasattr(path_constants, "get_all_apps_paths")
        assert hasattr(path_constants, "validate_path_within_project")
        assert hasattr(path_constants, "safe_path_join")
        assert hasattr(path_constants, "validate_flat_directory")
