"""Tests for apps_shared service components."""

import json

import pytest

from apps_shared.services.config_loader_service import (
    ConfigLoaderService,
)
from apps_shared.services.environment_validator_service import (
    EnvironmentValidatorService,
)
from apps_shared.services.operational_scanner_service import OperationalScannerService


class TestConfigLoaderService:
    """Test ConfigLoaderService."""

    def test_service_import(self):
        """Test that ConfigLoaderService can be imported."""
        assert ConfigLoaderService is not None

    def test_service_class_exists(self):
        """Test that ConfigLoaderService class exists."""
        assert callable(ConfigLoaderService)


class TestEnvironmentValidatorService:
    """Test EnvironmentValidatorService."""

    def test_service_import(self):
        """Test that EnvironmentValidatorService can be imported."""
        assert EnvironmentValidatorService is not None

    def test_service_class_exists(self):
        """Test that EnvironmentValidatorService class exists."""
        assert callable(EnvironmentValidatorService)


class TestConfigLoaderServiceBehavior:
    """G1: Behavior coverage for phase-added ConfigLoaderService guardrails."""

    def test_load_json_config_happy_path(self, tmp_path):
        cfg = tmp_path / "config.json"
        cfg.write_text('{"key": "value"}', encoding="utf-8")
        svc = ConfigLoaderService()
        result = svc.load_json_config(str(cfg))
        assert result == {"key": "value"}

    def test_load_json_config_missing_file_raises(self, tmp_path):
        svc = ConfigLoaderService()
        with pytest.raises(FileNotFoundError):
            svc.load_json_config(str(tmp_path / "nonexistent.json"))

    def test_load_json_config_outside_allowed_roots_raises(self, tmp_path):
        allowed = tmp_path / "allowed"
        allowed.mkdir()
        other = tmp_path / "other"
        other.mkdir()
        cfg = other / "config.json"
        cfg.write_text('{"x": 1}', encoding="utf-8")
        svc = ConfigLoaderService(config={"allowed_config_roots": [str(allowed)]})
        with pytest.raises(PermissionError):
            svc.load_json_config(str(cfg))

    def test_load_json_config_exceeds_size_cap_raises(self, tmp_path):
        cfg = tmp_path / "config.json"
        cfg.write_text(json.dumps({"key": "x" * 100}), encoding="utf-8")
        svc = ConfigLoaderService(config={"max_config_bytes": 10})
        with pytest.raises(ValueError, match="exceeds max size"):
            svc.load_json_config(str(cfg))

    def test_load_json_config_non_dict_payload_raises(self, tmp_path):
        cfg = tmp_path / "config.json"
        cfg.write_text("[1, 2, 3]", encoding="utf-8")
        svc = ConfigLoaderService()
        with pytest.raises(ValueError, match="JSON object"):
            svc.load_json_config(str(cfg))

    def test_mtime_cache_returns_independent_copies(self, tmp_path):
        cfg = tmp_path / "config.json"
        cfg.write_text('{"val": 1}', encoding="utf-8")
        svc = ConfigLoaderService()
        r1 = svc.load_json_config(str(cfg))
        r2 = svc.load_json_config(str(cfg))
        assert r1 == r2
        assert r1 is not r2

    def test_get_cached_configs_lists_loaded_paths(self, tmp_path):
        cfg = tmp_path / "config.json"
        cfg.write_text('{"a": 1}', encoding="utf-8")
        svc = ConfigLoaderService()
        assert svc.get_cached_configs() == []
        svc.load_json_config(str(cfg))
        cached = svc.get_cached_configs()
        assert len(cached) == 1

    def test_clear_cache_empties_cache(self, tmp_path):
        cfg = tmp_path / "config.json"
        cfg.write_text('{"a": 1}', encoding="utf-8")
        svc = ConfigLoaderService()
        svc.load_json_config(str(cfg))
        assert svc.get_cached_configs()
        svc.clear_cache()
        assert svc.get_cached_configs() == []


class TestEnvironmentValidatorServiceBehavior:
    """G2: Behavior coverage for phase-added EnvironmentValidatorService guardrails."""

    def test_validate_environment_with_set_var(self, monkeypatch):
        monkeypatch.setenv("_TEST_APPS_SHARED_VAR", "secret")
        svc = EnvironmentValidatorService(config={"required_vars": ["_TEST_APPS_SHARED_VAR"]})
        result = svc.validate_environment()
        assert result["valid"] is True
        assert "_TEST_APPS_SHARED_VAR" in result["present"]
        assert result["missing"] == []

    def test_validate_environment_missing_var(self, monkeypatch):
        monkeypatch.delenv("_TEST_APPS_SHARED_MISSING", raising=False)
        svc = EnvironmentValidatorService(config={"required_vars": ["_TEST_APPS_SHARED_MISSING"]})
        result = svc.validate_environment()
        assert result["valid"] is False
        assert "_TEST_APPS_SHARED_MISSING" in result["missing"]
        assert result["total_required"] == 1

    def test_get_env_var_empty_string_treated_as_missing(self, monkeypatch):
        monkeypatch.setenv("_TEST_EMPTY_VAR", "   ")
        svc = EnvironmentValidatorService()
        assert svc.get_env_var("_TEST_EMPTY_VAR") is None
        assert svc.get_env_var("_TEST_EMPTY_VAR", "fallback") == "fallback"
        assert svc.is_var_set("_TEST_EMPTY_VAR") is False

    def test_build_required_vars_deduplicates_and_strips(self):
        svc = EnvironmentValidatorService(config={"required_vars": ["VAR_X", " VAR_X ", "VAR_Y", ""]})
        assert svc.required_vars == ("VAR_X", "VAR_Y")

    def test_redact_env_snapshot_masks_values(self, monkeypatch):
        monkeypatch.setenv("_TEST_KEY_SET", "real-secret")
        monkeypatch.delenv("_TEST_KEY_MISSING", raising=False)
        svc = EnvironmentValidatorService()
        snapshot = svc.redact_env_snapshot(["_TEST_KEY_SET", "_TEST_KEY_MISSING"])
        assert snapshot["_TEST_KEY_SET"] == "<set>"
        assert snapshot["_TEST_KEY_MISSING"] == "<missing>"


class TestOperationalScannerService:
    """G3: Behavior coverage for phase-added OperationalScannerService guardrails."""

    def test_scan_directory_happy_path(self, tmp_path):
        (tmp_path / "a.py").write_text("x = 1", encoding="utf-8")
        (tmp_path / "b.py").write_text("y = 2", encoding="utf-8")
        svc = OperationalScannerService()
        result = svc.scan_directory(str(tmp_path), file_extensions=["py"])
        names = [r["name"] for r in result]
        assert "a.py" in names
        assert "b.py" in names

    def test_scan_directory_missing_dir_raises(self, tmp_path):
        svc = OperationalScannerService()
        with pytest.raises(FileNotFoundError):
            svc.scan_directory(str(tmp_path / "nonexistent"))

    def test_scan_directory_max_files_cap(self, tmp_path):
        for i in range(5):
            (tmp_path / f"file{i}.txt").write_text("x", encoding="utf-8")
        svc = OperationalScannerService(config={"max_files": 3})
        result = svc.scan_directory(str(tmp_path))
        assert len(result) == 3

    def test_get_scan_summary_empty(self):
        svc = OperationalScannerService()
        summary = svc.get_scan_summary()
        assert summary == {"total_files": 0, "allowed_duplicates": 0, "unique_files": 0}

    def test_get_scan_summary_unique_files_arithmetic(self, tmp_path):
        (tmp_path / "a.py").write_text("x", encoding="utf-8")
        svc = OperationalScannerService()
        svc.scan_directory(str(tmp_path))
        summary = svc.get_scan_summary()
        assert summary["unique_files"] == summary["total_files"] - summary["allowed_duplicates"]

    def test_normalize_extensions_adds_dot_prefix(self):
        result = OperationalScannerService._normalize_extensions(["py", ".PY", "txt"])
        assert result == {".py", ".txt"}

    def test_normalize_extensions_none_returns_none(self):
        assert OperationalScannerService._normalize_extensions(None) is None
        assert OperationalScannerService._normalize_extensions([]) is None
