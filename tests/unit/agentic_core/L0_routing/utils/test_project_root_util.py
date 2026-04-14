"""Runtime-hardened behavioral tests for project_root_util."""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def mod():
    return pytest.importorskip("agentic_core.utils.project_root_util")


def test_expected_helpers_exist(mod):
    for name in ["get_project_root", "get_project_root_safe", "_validated_root"]:
        value = getattr(mod, name, None)
        assert callable(value), f"{name} must be callable"


def test_validated_root_none_round_trip(mod):
    assert mod._validated_root(None) is None


def test_validated_root_handles_missing_path(mod, tmp_path):
    missing = tmp_path / "definitely_missing"
    assert not missing.exists()
    assert mod._validated_root(missing) is None


def test_validated_root_accepts_existing_path(mod, tmp_path):
    result = mod._validated_root(tmp_path)
    if result is not None:
        assert isinstance(result, Path)
        assert result.exists()
