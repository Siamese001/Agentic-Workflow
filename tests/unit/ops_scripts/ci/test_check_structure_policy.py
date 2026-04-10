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

    def test_load_policy_raises_on_missing_file(self, tmp_path: Path) -> None:
        bad_path = tmp_path / "nonexistent.yaml"
        with pytest.raises(FileNotFoundError):
            _load_policy(policy_path=bad_path)

    def test_load_policy_custom_path(self, tmp_path: Path) -> None:
        custom = tmp_path / "custom.yaml"
        custom.write_text(
            "root_directories:\n  - foo\nlayer_roots: []\n",
            encoding="utf-8",
        )
        policy = _load_policy(policy_path=custom)
        assert policy["root_directories"] == ["foo"]
        assert policy["layer_roots"] == []


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
        import ops_scripts.ci.check_structure_policy as mod

        orig = mod._ROOT
        mod._ROOT = tmp_path
        try:
            violations = _check_forbidden_root_dirs(policy)
            assert any("FORBIDDEN" in v for v in violations)
        finally:
            mod._ROOT = orig

    def test_unknown_dir_detected(self, tmp_path: Path) -> None:
        (tmp_path / "rogue_dir").mkdir()
        policy = {
            "root_directories": ["allowed"],
            "excluded_directories": [],
            "forbidden_root_directories": [],
        }
        import ops_scripts.ci.check_structure_policy as mod

        orig = mod._ROOT
        mod._ROOT = tmp_path
        try:
            violations = _check_root_dirs(policy)
            assert len(violations) == 1
            assert "UNKNOWN root dir: rogue_dir/" in violations[0]
        finally:
            mod._ROOT = orig

    def test_apps_prefix_auto_allowed(self, tmp_path: Path) -> None:
        (tmp_path / "apps_new").mkdir()
        policy = {
            "root_directories": [],
            "excluded_directories": [],
            "forbidden_root_directories": [],
        }
        import ops_scripts.ci.check_structure_policy as mod

        orig = mod._ROOT
        mod._ROOT = tmp_path
        try:
            violations = _check_root_dirs(policy)
            assert violations == [], f"apps_ prefix should be auto-allowed: {violations}"
        finally:
            mod._ROOT = orig


class TestRootFileCheck:
    """Test root file validation."""

    def test_no_violations_on_current_repo(self) -> None:
        policy = _load_policy()
        violations = _check_root_files(policy)
        assert violations == [], f"Unexpected violations: {violations}"

    def test_disallowed_file_detected(self, tmp_path: Path) -> None:
        (tmp_path / "bad.exe").write_text("x", encoding="utf-8")
        policy = {"root_file_patterns": ["*.py", "*.md"]}
        import ops_scripts.ci.check_structure_policy as mod

        orig = mod._ROOT
        mod._ROOT = tmp_path
        try:
            violations = _check_root_files(policy)
            assert len(violations) == 1
            assert "DISALLOWED root file: bad.exe" in violations[0]
        finally:
            mod._ROOT = orig

    def test_dotfile_allowed(self, tmp_path: Path) -> None:
        (tmp_path / ".gitignore").write_text("x", encoding="utf-8")
        policy = {"root_file_patterns": [".*"]}
        import ops_scripts.ci.check_structure_policy as mod

        orig = mod._ROOT
        mod._ROOT = tmp_path
        try:
            violations = _check_root_files(policy)
            assert violations == []
        finally:
            mod._ROOT = orig


class TestFlatDirCheck:
    """Test flat directory validation."""

    def test_flat_violation_detected(self, tmp_path: Path) -> None:
        flat = tmp_path / "src" / "mixins"
        flat.mkdir(parents=True)
        (flat / "illegal_subdir").mkdir()
        policy = {
            "flat_directories": ["mixins"],
            "excluded_directories": ["__pycache__"],
        }
        import ops_scripts.ci.check_structure_policy as mod

        orig = mod._ROOT
        mod._ROOT = tmp_path
        try:
            violations = _check_flat_dirs(policy)
            assert len(violations) == 1
            assert "FLAT violation" in violations[0]
            assert "mixins" in violations[0]
        finally:
            mod._ROOT = orig

    def test_excluded_subdir_not_flagged(self, tmp_path: Path) -> None:
        flat = tmp_path / "src" / "mixins"
        flat.mkdir(parents=True)
        (flat / "__pycache__").mkdir()
        policy = {
            "flat_directories": ["mixins"],
            "excluded_directories": ["__pycache__"],
        }
        import ops_scripts.ci.check_structure_policy as mod

        orig = mod._ROOT
        mod._ROOT = tmp_path
        try:
            violations = _check_flat_dirs(policy)
            assert violations == [], f"Excluded subdir should not be flagged: {violations}"
        finally:
            mod._ROOT = orig


class TestLayerStructure:
    """Test layer structure validation."""

    def test_all_layers_present(self) -> None:
        policy = _load_policy()
        violations = _check_layer_structure(policy)
        assert violations == [], f"Missing layers: {violations}"

    def test_missing_layer_detected(self, tmp_path: Path) -> None:
        core = tmp_path / "agentic_core"
        core.mkdir()
        (core / "L0_routing").mkdir()
        # L1_cognition intentionally missing
        policy = {"layer_roots": ["L0_routing", "L1_cognition"]}
        import ops_scripts.ci.check_structure_policy as mod

        orig = mod._ROOT
        mod._ROOT = tmp_path
        try:
            violations = _check_layer_structure(policy)
            assert len(violations) == 1
            assert "MISSING layer root: agentic_core/L1_cognition/" in violations[0]
        finally:
            mod._ROOT = orig

    def test_no_agentic_core_dir(self, tmp_path: Path) -> None:
        policy = {"layer_roots": ["L0_routing"]}
        import ops_scripts.ci.check_structure_policy as mod

        orig = mod._ROOT
        mod._ROOT = tmp_path
        try:
            violations = _check_layer_structure(policy)
            assert violations == ["agentic_core/ directory not found"]
        finally:
            mod._ROOT = orig


class TestMainGate:
    """Test the main entry point."""

    def test_main_returns_zero_on_current_repo(self) -> None:
        result = main(verbose=False)
        assert result == 0, "Structure policy gate should pass on current repo"

    def test_main_returns_one_on_violations(self, tmp_path: Path) -> None:
        # Create a repo with a forbidden dir
        (tmp_path / "legacy_code").mkdir()
        (tmp_path / "agentic_core" / "L0_routing").mkdir(parents=True)
        policy_file = tmp_path / "policy.yaml"
        policy_file.write_text(
            "root_directories: []\n"
            "root_file_patterns: []\n"
            "flat_directories: []\n"
            "layer_roots: []\n"
            "excluded_directories: []\n"
            "forbidden_root_directories:\n  - legacy_code\n",
            encoding="utf-8",
        )
        import ops_scripts.ci.check_structure_policy as mod

        orig_root = mod._ROOT
        mod._ROOT = tmp_path
        try:
            # Patch _load_policy to use our custom file
            orig_load = mod._load_policy
            mod._load_policy = lambda: orig_load(policy_path=policy_file)
            result = main(verbose=False)
            assert result == 1, "Should return 1 when forbidden dir exists"
        finally:
            mod._ROOT = orig_root
            mod._load_policy = orig_load
