"""ADR-079: three-bucket stages are opt-in on the ADG hot path."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[5]
_OPT_PATH = _REPO_ROOT / "tools" / "generate" / "integration" / "optional_three_bucket.py"
_spec = importlib.util.spec_from_file_location(
    "tools.generate.integration.optional_three_bucket",
    _OPT_PATH,
)
assert _spec and _spec.loader
mod = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = mod
_spec.loader.exec_module(mod)


@pytest.fixture(autouse=True)
def _clear_three_bucket_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "ADG_THREE_BUCKET",
        "ADG_RUNTIME_VIEW",
        "ADG_REGISTRY_LIFT",
        "ADG_THREE_BUCKET_REPORTS",
        "ADG_THREE_BUCKET_SIGN",
    ):
        monkeypatch.delenv(name, raising=False)


def test_default_hot_path_skips_all_stages() -> None:
    assert mod.three_bucket_master_enabled() is False
    assert mod.any_three_bucket_stage_enabled() is False
    assert "OFF" in mod.format_mode_banner()


def test_master_flag_enables_audit_bundle(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ADG_THREE_BUCKET", "1")
    assert mod.runtime_view_enabled() is True
    assert mod.registry_lift_enabled() is True
    assert mod.three_bucket_reports_enabled() is True
    assert mod.any_three_bucket_stage_enabled() is True


def test_reports_only_flag_enables_reports_stage(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ADG_THREE_BUCKET_REPORTS", "1")
    assert mod.three_bucket_reports_enabled() is True
    assert mod.runtime_view_enabled() is False
    assert mod.any_three_bucket_stage_enabled() is True
