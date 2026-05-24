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


def test_reports_only_flag_does_not_enable_runtime_or_registry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ADG_THREE_BUCKET_REPORTS", "1")
    assert mod.runtime_view_enabled() is False
    assert mod.registry_lift_enabled() is False
    assert mod.three_bucket_reports_enabled() is True
    assert "reports" in mod.format_mode_banner()


def test_sign_flag_alone_enables_stage_without_master(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ADG_THREE_BUCKET_SIGN", "1")
    assert mod.three_bucket_sign_enabled() is True
    assert mod.three_bucket_master_enabled() is False
    assert mod.any_three_bucket_stage_enabled() is True
    assert mod.format_mode_banner() == "three_bucket=AUDIT[sign]"


def test_run_enrichment_skips_when_all_stages_disabled(tmp_path) -> None:
    snap = tmp_path / "unused.sqlite"
    snap.write_text("", encoding="utf-8")
    result = mod.run_optional_three_bucket_enrichment(snap)
    assert result.skipped_reason is not None
    assert result.runtime_rows_written == 0
    assert result.report_paths == {}
