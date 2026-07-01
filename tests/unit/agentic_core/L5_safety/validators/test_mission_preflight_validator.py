"""Smoke tests for mission_preflight_validator — wave 17."""

from pathlib import Path

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.validators.mission_preflight_validator")


def test_module_imports_clean():
    assert mod is not None


def test_MissionPreflight_class_present():
    assert hasattr(mod, "MissionPreflight")
    assert isinstance(mod.MissionPreflight, type)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)


def test_target_territory_returns_first_project_segment_or_none(tmp_path: Path) -> None:
    validator = mod.MissionPreflight.__new__(mod.MissionPreflight)
    validator.project_root = tmp_path.resolve()

    inside = tmp_path / "apps" / "nested" / "file.py"
    outside = Path(tmp_path.anchor) / "outside" / "file.py"

    assert validator._target_territory(inside) == "apps"
    assert validator._target_territory(outside) is None
