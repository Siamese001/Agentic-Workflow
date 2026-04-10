"""Tests for the YAML-only structure policy CI gate."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_ROOT))

from ops_scripts.ci.check_structure_policy import (
    _check_flat_dirs,
    _check_forbidden_root_dirs,
    _check_layer_structure,
    _check_root_dirs,
    _check_root_files,
    _load_policy,
    main,
)


class TestLoadPolicy:
    """Test policy YAML loading."""

    def test_load_policy_returns_dict(self) -> None:
        policy = _load_policy()
        assert isinstance(policy, dict)

    def test_policy_has_required_keys(self) -> None:
        policy = _load_policy()
        required = {
            "root_directories",
            "root_file_patterns",
            "layer_roots",
            "lcd_subfolders",
            "flat_directories",
            "excluded_directories",
            "forbidden_root_directories",
        }
        assert required.issubset(policy.keys())


class TestRootDirCheck:
    """Test root directory validation."""

    def test_no_violations_on_current_repo(self) -> None:
        policy = _load_policy()
        violations = _check_root_dirs(policy)
        assert violations == [], f"Unexpected violations: {violations}"

    def test_forbidden_dir_detected(self, tmp_path: Path) -> None:
        (tmp_path / "legacy_code").mkdir()
        policy = {
            "root_directories": [],
            "excluded_directories": [],
            "forbidden_root_directories": ["legacy_code"],
        }
        # Monkey-patch _ROOT for this test
        import ops_scripts.ci.check_structure_policy as mod

        orig = mod._ROOT
        mod._ROOT = tmp_path
        try:
            violations = _check_forbidden_root_dirs(policy)
            assert any("FORBIDDEN" in v for v in violations)
        finally:
            mod._ROOT = orig


class TestLayerStructure:
    """Test layer structure validation."""

    def test_all_layers_present(self) -> None:
        policy = _load_policy()
        violations = _check_layer_structure(policy)
        assert violations == [], f"Missing layers: {violations}"


class TestMainGate:
    """Test the main entry point."""

    def test_main_returns_zero_on_current_repo(self) -> None:
        result = main(verbose=False)
        assert result == 0, "Structure policy gate should pass on current repo"
