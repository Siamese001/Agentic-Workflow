"""ADR-079: three-bucket stages are opt-in on the ADG hot path."""

from __future__ import annotations

import pytest

from tools.generate.integration import optional_three_bucket as mod


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
