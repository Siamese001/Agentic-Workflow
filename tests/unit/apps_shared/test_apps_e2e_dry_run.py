"""Tests for apps_shared._apps_e2e_dry_run short-circuit helper.

Closes the 7/7 default-emit objective from the apps_e2e auditability
harness plan. Each app's __main__.main() calls maybe_short_circuit as its
first statement; when --apps-e2e-dry-run is in sys.argv the helper must
print a marker and exit 0 BEFORE any heavy work (_adg_bootstrap or
run_main delegation).
"""
from __future__ import annotations

import json
import sys

import pytest

from apps_shared import _apps_e2e_dry_run as mod


class TestMaybeShortCircuit:
    def test_no_op_when_flag_absent(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(sys, "argv", ["python", "-m", "apps_test"])
        # must not raise, must not exit
        mod.maybe_short_circuit("apps_test")

    def test_exits_zero_when_flag_present(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.setattr(sys, "argv", ["python", "-m", "apps_test", mod.DRY_RUN_FLAG])
        with pytest.raises(SystemExit) as exc_info:
            mod.maybe_short_circuit("apps_test")
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert mod.DRY_RUN_MARKER_PREFIX in captured.out

    def test_marker_payload_is_valid_json_with_app_name(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.setattr(sys, "argv", [mod.DRY_RUN_FLAG])
        with pytest.raises(SystemExit):
            mod.maybe_short_circuit("apps_lic")
        line = capsys.readouterr().out.strip()
        assert line.startswith(mod.DRY_RUN_MARKER_PREFIX)
        payload = json.loads(line[len(mod.DRY_RUN_MARKER_PREFIX) :])
        assert payload["app_name"] == "apps_lic"
        assert payload["apps_e2e_dry_run_marker"] is True
        assert payload["status"] == "dry_run_short_circuit"
        assert payload["flag"] == mod.DRY_RUN_FLAG

    def test_flag_constant_is_namespaced(self) -> None:
        # Must NOT collide with bare --dry-run (apps_qna has its own --dry-run).
        assert mod.DRY_RUN_FLAG == "--apps-e2e-dry-run"
        assert mod.DRY_RUN_FLAG != "--dry-run"

    def test_exports(self) -> None:
        for name in ("DRY_RUN_FLAG", "DRY_RUN_MARKER_PREFIX", "maybe_short_circuit"):
            assert name in mod.__all__
