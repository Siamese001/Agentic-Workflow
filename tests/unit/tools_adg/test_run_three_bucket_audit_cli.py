"""CLI guards for optional three-bucket audit refresh (off hot path)."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from unittest import mock

import pytest

_audit_cli = importlib.import_module("tools.adg.run_three_bucket_audit")


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


def test_main_exits_when_no_stage_enabled(capsys: pytest.CaptureFixture[str]) -> None:
    with mock.patch.object(sys, "argv", ["run_three_bucket_audit.py"]):
        code = _audit_cli.main()
    assert code == 2
    assert "no three-bucket stage enabled" in capsys.readouterr().err


def test_main_exits_when_snapshot_missing(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setenv("ADG_THREE_BUCKET", "1")
    missing = Path("/nonexistent/adg.sqlite")
    with mock.patch.object(sys, "argv", ["run_three_bucket_audit.py", "--snapshot", str(missing)]):
        code = _audit_cli.main()
    assert code == 2
    assert "snapshot not found" in capsys.readouterr().err
