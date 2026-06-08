"""Tests for path_constants.py module.

This module contains SSOT constants for structural paths and path validation
functions. Tests verify constant existence, types, and function behavior.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    SSOT_SCORE_THRESHOLD_DET,
    SSOT_SCORE_THRESHOLD_QWEN,
    consensus_majority_threshold,
    AGENTIC_CORE_LAYERS,
    APPS_PACKAGES,
    PROJECT_ROOT_MARKERS,
    get_validated_project_root,
    AGENTIC_CORE_DIR,
    INFRASTRUCTURE_DIR,
    APPS_EVAL_DIR,
    APPS_EXEC_DIR,
    APPS_LIC_DIR,
    APPS_RESEARCH_DIR,
    APPS_RFP_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    ARTIFACTS_DIR,
    ADG_ARTIFACTS_DIR,
    WINDSURF_ARTIFACTS_DIR,
    WINDSURF_PLANS_DIR,
    DOCS_DIR,
    DOCS_REPORTS_DIR,
    ADR_DIR,
    HEALING_BACKUPS_DIR,
    OPS_ARCHIVES_DIR,
    OPS_SCRIPTS_DIR,
    GOVERNANCE_SCRIPTS_DIR,
    SCRIPTS_DIR,
    SYSTEM_LEARNING_DIR,
    TESTS_DIR,
    WINDSURF_SCRIPTS_DIR,
    TESTS_UNIT_DIR,
    TOOLS_DIR,
    DASHBOARD_DIR,
    REPORTS_DIR,
    L0_MAINTENANCE_DIR,
    L0_ROUTING_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_apps_directories,
    get_all_apps_paths,
    LAYER_ROOTS,
    ROOT_WHITELIST,
    ROOT_PROTECTED_FILES,
    ROOT_ALLOWED_PATTERNS,
    SOVEREIGN_EXCLUDED_FOLDERS,
    VARIABLE_DEPTH_SUBFOLDERS,
    L4_APPROVED_FOLDERS,
    GLOBAL_EXCLUDED_DIRS,
    DISCOVERY_EXCLUDED_TERRITORIES,
    TOOLING_EXCLUDED_DIRS,
    DEPTH_RULES,
    PROJECT_ROOT_WHITELIST,
    CORE_SUBFOLDER_MAP,
    APPS_RG_SUBFOLDER_MAP,
    APPS_LIC_SUBFOLDER_MAP,
    APPS_SHARED_SUBFOLDER_MAP,
    APPS_EVAL_SUBFOLDER_MAP,
    APPS_EXEC_SUBFOLDER_MAP,
    APPS_RESEARCH_SUBFOLDER_MAP,
    APPS_RFP_SUBFOLDER_MAP,
    ALLOWED_DUPLICATE_FILENAMES,
    FLAT_DIRECTORIES,
    ALLOW_ROOT_PY_TERRITORIES,
    LAYER_PREFIX_EXEMPT_TERRITORIES,
    FORBIDDEN_FOLDER_PATTERN,
    FORBIDDEN_ROOT_FOLDERS,
    validate_path_within_project,
    safe_path_join,
    validate_flat_directory,
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    RUNTIME_STATE_JSON,
)


class TestHealingRoutingSsot:
    """Heal *float* cutoffs migrated out of ``path_constants`` — SSOT-backed."""

    def test_path_constants_does_not_expose_deprecated_float_aliases(self):
        import agentic_core.L0_routing.config.path_constants as pc

        assert not hasattr(pc, "HEALING_CONFIDENCE_X")
        assert not hasattr(pc, "HEALING_CONFIDENCE_Y")

    def test_heal_defaults_pair_ordering(self):
        from agentic_core.L2_execution.healers.routing_thresholds_ssot import (
            DEFAULT_HEAL_CONFIDENCE_HIGH,
            DEFAULT_HEAL_CONFIDENCE_MEDIUM,
        )

        assert DEFAULT_HEAL_CONFIDENCE_MEDIUM < DEFAULT_HEAL_CONFIDENCE_HIGH
    def test_ssot_score_threshold_det(self):
        """Test SSOT_SCORE_THRESHOLD_DET is an int."""
        assert isinstance(SSOT_SCORE_THRESHOLD_DET, int)
        assert SSOT_SCORE_THRESHOLD_DET >= 0

    def test_ssot_score_threshold_qwen(self):
        """Test SSOT_SCORE_THRESHOLD_QWEN is an int."""
        assert isinstance(SSOT_SCORE_THRESHOLD_QWEN, int)
        assert SSOT_SCORE_THRESHOLD_QWEN >= 0

    def test_ssot_thresholds_ordered(self):
        """Test SSOT thresholds are ordered correctly."""
        assert SSOT_SCORE_THRESHOLD_DET < SSOT_SCORE_THRESHOLD_QWEN


class TestConsensusMajorityThreshold:
    """Tests for consensus_majority_threshold function."""

    def test_consensus_majority_threshold_3(self):
        """Test threshold for 3 jurors (2/3)."""
        threshold = consensus_majority_threshold(3)
        assert threshold == 2 / 3

    def test_consensus_majority_threshold_4(self):
        """Test threshold for 4 jurors (3/4)."""
        threshold = consensus_majority_threshold(4)
        assert threshold == 3 / 4

    def test_consensus_majority_threshold_5(self):
        """Test threshold for 5 jurors (3/5)."""
        threshold = consensus_majority_threshold(5)
        assert threshold == 3 / 5

    def test_consensus_majority_threshold_7(self):
        """Test threshold for 7 jurors (4/7)."""
        threshold = consensus_majority_threshold(7)
        assert threshold == 4 / 7

    def test_consensus_majority_threshold_invalid(self):
        """Test that invalid juror count raises ValueError."""
        with pytest.raises(ValueError, match="must be >= 1"):
            consensus_majority_threshold(0)


class TestLayerAndPackageConstants:
    """Tests for layer and package constants."""

    def test_agentic_core_layers(self):
        """Test AGENTIC_CORE_LAYERS is a list of strings."""
        assert isinstance(AGENTIC_CORE_LAYERS, list)
        assert len(AGENTIC_CORE_LAYERS) > 0
        for layer in AGENTIC_CORE_LAYERS:
            assert isinstance(layer, str)

    def test_apps_packages(self):
        """Test APPS_PACKAGES is a list of strings."""
        assert isinstance(APPS_PACKAGES, list)
        assert len(APPS_PACKAGES) > 0
        for package in APPS_PACKAGES:
            assert isinstance(package, str)


class TestProjectRootDetection:
    """Tests for project root detection."""

    def test_project_root_markers(self):
        """Test PROJECT_ROOT_MARKERS is a tuple of strings."""
        assert isinstance(PROJECT_ROOT_MARKERS, tuple)
        assert len(PROJECT_ROOT_MARKERS) > 0
        for marker in PROJECT_ROOT_MARKERS:
            assert isinstance(marker, str)

    def test_get_validated_project_root(self):
        """Test get_validated_project_root returns a Path."""
        root = get_validated_project_root()
        assert isinstance(root, Path)


class TestDirectoryConstants:
    """Tests for directory constants."""

    def test_agentic_core_dir(self):
        """Test AGENTIC_CORE_DIR is a string."""
        assert isinstance(AGENTIC_CORE_DIR, str)

    def test_infrastructure_dir(self):
        """Test INFRASTRUCTURE_DIR is a string."""
        assert isinstance(INFRASTRUCTURE_DIR, str)

    def test_apps_directories(self):
        """Test apps_* directory constants are strings."""
        assert isinstance(APPS_EVAL_DIR, str)
        assert isinstance(APPS_EXEC_DIR, str)
        assert isinstance(APPS_LIC_DIR, str)
        assert isinstance(APPS_RESEARCH_DIR, str)
        assert isinstance(APPS_RFP_DIR, str)
        assert isinstance(APPS_RG_DIR, str)
        assert isinstance(APPS_SHARED_DIR, str)

    def test_artifact_directories(self):
        """Test artifact directory constants are strings."""
        assert isinstance(ARTIFACTS_DIR, str)
        assert isinstance(ADG_ARTIFACTS_DIR, str)
        assert isinstance(WINDSURF_ARTIFACTS_DIR, str)
        assert isinstance(WINDSURF_PLANS_DIR, str)

    def test_docs_directories(self):
        """Test documentation directory constants are strings."""
        assert isinstance(DOCS_DIR, str)
        assert isinstance(DOCS_REPORTS_DIR, str)
        assert isinstance(ADR_DIR, str)

    def test_ops_directories(self):
        """Test operations directory constants are strings."""
        assert isinstance(HEALING_BACKUPS_DIR, str)
        assert isinstance(OPS_ARCHIVES_DIR, str)
        assert isinstance(OPS_SCRIPTS_DIR, str)

    def test_other_directories(self):
        """Test other directory constants are strings."""
        assert isinstance(SCRIPTS_DIR, str)
        assert isinstance(SYSTEM_LEARNING_DIR, str)
        assert isinstance(TESTS_DIR, str)
        assert isinstance(GOVERNANCE_SCRIPTS_DIR, str)
        assert isinstance(WINDSURF_SCRIPTS_DIR, str)
        assert WINDSURF_SCRIPTS_DIR == GOVERNANCE_SCRIPTS_DIR
        assert isinstance(TESTS_UNIT_DIR, str)
        assert isinstance(TOOLS_DIR, str)
        assert isinstance(DASHBOARD_DIR, str)
        assert isinstance(REPORTS_DIR, str)

    def test_layer_directories(self):
        """Test layer-specific directory constants are strings."""
        assert isinstance(L0_MAINTENANCE_DIR, str)
        assert isinstance(L0_ROUTING_DIR, str)
        assert isinstance(L1_COGNITION_DIR, str)
        assert isinstance(L2_EXECUTION_DIR, str)
        assert isinstance(L3_ORCHESTRATION_DIR, str)
        assert isinstance(L4_STATE_DIR, str)
        assert isinstance(L5_SAFETY_DIR, str)
        assert isinstance(L6_OBSERVABILITY_DIR, str)


class TestDynamicDirectoryDiscovery:
    """Tests for dynamic directory discovery functions."""

    def test_get_apps_directories(self):
        """Test get_apps_directories returns a list of strings."""
        apps_dirs = get_apps_directories()
        assert isinstance(apps_dirs, list)
        for dir_name in apps_dirs:
            assert isinstance(dir_name, str)
            assert dir_name.startswith("apps_")

    def test_get_all_apps_paths(self):
        """Test get_all_apps_paths returns a list of Path objects."""
        apps_paths = get_all_apps_paths()
        assert isinstance(apps_paths, list)
        for path in apps_paths:
            assert isinstance(path, Path)


class TestLayerRoots:
    """Tests for LAYER_ROOTS constant."""

    def test_layer_roots(self):
        """Test LAYER_ROOTS is a frozenset of strings."""
        assert isinstance(LAYER_ROOTS, frozenset)
        assert len(LAYER_ROOTS) > 0
        for root in LAYER_ROOTS:
            assert isinstance(root, str)


class TestWhitelists:
    """Tests for whitelist constants."""

    def test_root_whitelist(self):
        """Test ROOT_WHITELIST is a frozenset of strings."""
        assert isinstance(ROOT_WHITELIST, frozenset)
        assert len(ROOT_WHITELIST) > 0
        for item in ROOT_WHITELIST:
            assert isinstance(item, str)

    def test_root_protected_files(self):
        """Test ROOT_PROTECTED_FILES is a frozenset of strings."""
        assert isinstance(ROOT_PROTECTED_FILES, frozenset)
        assert len(ROOT_PROTECTED_FILES) > 0
        for file_name in ROOT_PROTECTED_FILES:
            assert isinstance(file_name, str)

    def test_root_allowed_patterns(self):
        """Test ROOT_ALLOWED_PATTERNS is a tuple of strings."""
        assert isinstance(ROOT_ALLOWED_PATTERNS, tuple)
        assert len(ROOT_ALLOWED_PATTERNS) > 0
        for pattern in ROOT_ALLOWED_PATTERNS:
            assert isinstance(pattern, str)

    def test_sovereign_excluded_folders(self):
        """Test SOVEREIGN_EXCLUDED_FOLDERS is a frozenset of strings."""
        assert isinstance(SOVEREIGN_EXCLUDED_FOLDERS, frozenset)
        assert len(SOVEREIGN_EXCLUDED_FOLDERS) > 0
        for folder in SOVEREIGN_EXCLUDED_FOLDERS:
            assert isinstance(folder, str)


class TestSubfolderMaps:
    """Tests for subfolder map constants."""

    def test_core_subfolder_map(self):
        """Test CORE_SUBFOLDER_MAP is a mapping."""
        assert isinstance(CORE_SUBFOLDER_MAP, dict)
        for key, value in CORE_SUBFOLDER_MAP.items():
            assert isinstance(key, str)
            assert isinstance(value, list)

    def test_apps_subfolder_maps(self):
        """Test apps_* subfolder maps are mappings."""
        assert isinstance(APPS_RG_SUBFOLDER_MAP, dict)
        assert isinstance(APPS_LIC_SUBFOLDER_MAP, dict)
        assert isinstance(APPS_SHARED_SUBFOLDER_MAP, dict)
        assert isinstance(APPS_EVAL_SUBFOLDER_MAP, dict)
        assert isinstance(APPS_EXEC_SUBFOLDER_MAP, dict)
        assert isinstance(APPS_RESEARCH_SUBFOLDER_MAP, dict)
        assert isinstance(APPS_RFP_SUBFOLDER_MAP, dict)


class TestValidationConstants:
    """Tests for validation-related constants."""

    def test_allowed_duplicate_filenames(self):
        """Test ALLOWED_DUPLICATE_FILENAMES is a frozenset."""
        assert isinstance(ALLOWED_DUPLICATE_FILENAMES, frozenset)
        assert len(ALLOWED_DUPLICATE_FILENAMES) > 0
        for filename in ALLOWED_DUPLICATE_FILENAMES:
            assert isinstance(filename, str)

    def test_flat_directories(self):
        """Test FLAT_DIRECTORIES is a frozenset."""
        assert isinstance(FLAT_DIRECTORIES, frozenset)
        assert len(FLAT_DIRECTORIES) > 0
        for directory in FLAT_DIRECTORIES:
            assert isinstance(directory, str)

    def test_allow_root_py_territories(self):
        """Test ALLOW_ROOT_PY_TERRITORIES is a frozenset."""
        assert isinstance(ALLOW_ROOT_PY_TERRITORIES, frozenset)

    def test_layer_prefix_exempt_territories(self):
        """Test LAYER_PREFIX_EXEMPT_TERRITORIES is a frozenset."""
        assert isinstance(LAYER_PREFIX_EXEMPT_TERRITORIES, frozenset)

    def test_forbidden_folder_pattern(self):
        """Test FORBIDDEN_FOLDER_PATTERN is a compiled regex."""
        assert hasattr(FORBIDDEN_FOLDER_PATTERN, "match")

    def test_forbidden_root_folders(self):
        """Test FORBIDDEN_ROOT_FOLDERS is a frozenset."""
        assert isinstance(FORBIDDEN_ROOT_FOLDERS, frozenset)
        assert len(FORBIDDEN_ROOT_FOLDERS) > 0
        for folder in FORBIDDEN_ROOT_FOLDERS:
            assert isinstance(folder, str)


class TestPathValidationFunctions:
    """Tests for path validation functions."""

    def test_validate_path_within_project_valid(self):
        """Test validate_path_within_project with valid path."""
        root = get_validated_project_root()
        test_path = root / "agentic_core"
        assert validate_path_within_project(test_path, root) is True

    def test_validate_path_within_project_invalid(self):
        """Test validate_path_within_project with invalid path."""
        root = get_validated_project_root()
        test_path = Path("/nonexistent/path")
        assert validate_path_within_project(test_path, root) is False

    def test_safe_path_join_valid(self):
        """Test safe_path_join with valid path."""
        root = get_validated_project_root()
        result = safe_path_join(root, "agentic_core", "L0_routing")
        assert isinstance(result, Path)

    def test_safe_path_join_invalid(self):
        """Test safe_path_join with invalid path raises ValueError."""
        root = get_validated_project_root()
        with pytest.raises(ValueError, match="SAFETY VIOLATION"):
            safe_path_join(root, "..", "outside_project")

    def test_validate_flat_directory_compliant(self):
        """Test validate_flat_directory with compliant path."""
        path_parts = ("agentic_core", "config", "file.py")
        result = validate_flat_directory(path_parts)
        assert result is None

    def test_validate_flat_directory_violation(self):
        """Test validate_flat_directory detects violations."""
        path_parts = ("agentic_core", "cache", "subdir", "file.py")
        result = validate_flat_directory(path_parts)
        assert result is not None
        assert "domain" in result
        assert "illegal_child" in result

    def test_validate_flat_directory_pycache_exempt(self):
        """Test validate_flat_directory exempts __pycache__."""
        path_parts = ("agentic_core", "cache", "__pycache__", "file.pyc")
        result = validate_flat_directory(path_parts)
        assert result is None


class TestFileConstants:
    """Tests for file name constants."""

    def test_agent_discovery_json(self):
        """Test AGENT_DISCOVERY_JSON is a string."""
        assert isinstance(AGENT_DISCOVERY_JSON, str)

    def test_agent_discovery_manifest_json(self):
        """Test AGENT_DISCOVERY_MANIFEST_JSON is a string."""
        assert isinstance(AGENT_DISCOVERY_MANIFEST_JSON, str)

    def test_runtime_state_json(self):
        """Test RUNTIME_STATE_JSON is a string."""
        assert isinstance(RUNTIME_STATE_JSON, str)


class TestOtherConstants:
    """Tests for other important constants."""

    def test_variable_depth_subfolders(self):
        """Test VARIABLE_DEPTH_SUBFOLDERS is a frozenset."""
        assert isinstance(VARIABLE_DEPTH_SUBFOLDERS, frozenset)
        assert len(VARIABLE_DEPTH_SUBFOLDERS) > 0

    def test_l4_approved_folders(self):
        """Test L4_APPROVED_FOLDERS is a frozenset."""
        assert isinstance(L4_APPROVED_FOLDERS, frozenset)
        assert len(L4_APPROVED_FOLDERS) > 0

    def test_global_excluded_dirs(self):
        """Test GLOBAL_EXCLUDED_DIRS is a frozenset."""
        assert isinstance(GLOBAL_EXCLUDED_DIRS, frozenset)
        assert len(GLOBAL_EXCLUDED_DIRS) > 0

    def test_discovery_excluded_territories(self):
        """Test DISCOVERY_EXCLUDED_TERRITORIES is a frozenset."""
        assert isinstance(DISCOVERY_EXCLUDED_TERRITORIES, frozenset)

    def test_tooling_excluded_dirs(self):
        """Test TOOLING_EXCLUDED_DIRS is a frozenset."""
        assert isinstance(TOOLING_EXCLUDED_DIRS, frozenset)

    def test_depth_rules(self):
        """Test DEPTH_RULES is a mapping."""
        assert isinstance(DEPTH_RULES, dict)
        assert len(DEPTH_RULES) > 0
        for key, value in DEPTH_RULES.items():
            assert isinstance(key, str)
            assert isinstance(value, int)

    def test_project_root_whitelist(self):
        """Test PROJECT_ROOT_WHITELIST is a frozenset."""
        assert isinstance(PROJECT_ROOT_WHITELIST, frozenset)
        assert len(PROJECT_ROOT_WHITELIST) > 0
