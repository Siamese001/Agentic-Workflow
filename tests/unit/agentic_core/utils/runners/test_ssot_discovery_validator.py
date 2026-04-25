"""Unit tests for agentic_core.utils.runners.ssot_discovery_validator.

Targets Wave-1 / Phase P3 of test-coverage-hotspots-8f2a1c plan.
Source module: 49 lines, fan_in=92 (L_SHARED, multiplier 1.50, impact 138.0).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.utils.runners.ssot_discovery_validator import (
    SSOTDiscoveryValidator,
    discover_ssot,
    get_python_files,
)


class TestSSOTDiscoveryValidatorRegister:
    """register_source() + get_source_path() contract."""

    def test_register_then_get_path_returns_registered_path(self) -> None:
        v = SSOTDiscoveryValidator()
        v.register_source("config", "/tmp/config.yaml", "abc123")
        assert v.get_source_path("config") == "/tmp/config.yaml"

    def test_get_source_path_unknown_returns_none(self) -> None:
        v = SSOTDiscoveryValidator()
        assert v.get_source_path("nope") is None

    def test_register_overwrites_existing(self) -> None:
        v = SSOTDiscoveryValidator()
        v.register_source("x", "/a", "h1")
        v.register_source("x", "/b", "h2")
        assert v.get_source_path("x") == "/b"
        assert v.validate_source("x", "h2") is True
        assert v.validate_source("x", "h1") is False

    def test_register_multiple_sources_independent(self) -> None:
        v = SSOTDiscoveryValidator()
        v.register_source("a", "/pa", "ha")
        v.register_source("b", "/pb", "hb")
        assert v.get_source_path("a") == "/pa"
        assert v.get_source_path("b") == "/pb"


class TestSSOTDiscoveryValidatorValidate:
    """validate_source() checksum semantics."""

    def test_validate_matching_checksum(self) -> None:
        v = SSOTDiscoveryValidator()
        v.register_source("doc", "/p", "sha-aaa")
        assert v.validate_source("doc", "sha-aaa") is True

    def test_validate_mismatched_checksum(self) -> None:
        v = SSOTDiscoveryValidator()
        v.register_source("doc", "/p", "sha-aaa")
        assert v.validate_source("doc", "sha-bbb") is False

    def test_validate_unknown_source_returns_false(self) -> None:
        v = SSOTDiscoveryValidator()
        assert v.validate_source("not-there", "any") is False

    def test_validate_empty_checksum_against_empty_registered(self) -> None:
        v = SSOTDiscoveryValidator()
        v.register_source("blank", "/p", "")
        assert v.validate_source("blank", "") is True


class TestDiscoverSSOTFunction:
    """Module-level discover_ssot() helper."""

    def test_discover_ssot_unregistered_returns_none(self) -> None:
        # discover_ssot constructs a fresh validator, so it's always empty
        assert discover_ssot("anything") is None

    def test_discover_ssot_empty_string_returns_none(self) -> None:
        assert discover_ssot("") is None


class TestGetPythonFiles:
    """get_python_files() filesystem walker."""

    def test_returns_empty_for_nonexistent_directory(self) -> None:
        result = get_python_files("/definitely/does/not/exist/xyzzy")
        assert result == []

    def test_finds_python_files_in_tmp_tree(self, tmp_path: Path) -> None:
        (tmp_path / "a.py").write_text("# a", encoding="utf-8")
        (tmp_path / "b.py").write_text("# b", encoding="utf-8")
        (tmp_path / "not_py.txt").write_text("x", encoding="utf-8")
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "c.py").write_text("# c", encoding="utf-8")
        result = get_python_files(tmp_path)
        assert len(result) == 3
        names = sorted(Path(p).name for p in result)
        assert names == ["a.py", "b.py", "c.py"]

    def test_custom_pattern_filters_by_glob(self, tmp_path: Path) -> None:
        (tmp_path / "include_me.txt").write_text("x", encoding="utf-8")
        (tmp_path / "skip_me.py").write_text("x", encoding="utf-8")
        result = get_python_files(tmp_path, pattern="*.txt")
        assert len(result) == 1
        assert Path(result[0]).name == "include_me.txt"

    def test_accepts_string_path_argument(self, tmp_path: Path) -> None:
        (tmp_path / "x.py").write_text("# x", encoding="utf-8")
        result = get_python_files(str(tmp_path))
        assert len(result) == 1

    def test_empty_directory_returns_empty_list(self, tmp_path: Path) -> None:
        result = get_python_files(tmp_path)
        assert result == []

    def test_skips_directories_only_returns_files(self, tmp_path: Path) -> None:
        nested = tmp_path / "dir.py"  # directory named like a .py file
        nested.mkdir()
        (nested / "real.py").write_text("# r", encoding="utf-8")
        result = get_python_files(tmp_path)
        # Should only include the file, not the directory named `dir.py`
        assert len(result) == 1
        assert Path(result[0]).name == "real.py"


class TestExports:
    """__all__ surface matches public API."""

    def test_all_exports_exist(self) -> None:
        import agentic_core.utils.runners.ssot_discovery_validator as mod

        for name in mod.__all__:
            assert hasattr(mod, name), f"__all__ lists {name!r} but module has no such attribute"

    def test_all_includes_expected_symbols(self) -> None:
        import agentic_core.utils.runners.ssot_discovery_validator as mod

        assert set(mod.__all__) == {
            "SSOTDiscoveryValidator",
            "discover_ssot",
            "get_python_files",
        }
