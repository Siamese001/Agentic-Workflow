"""Tests for the runtime trace contract CI gate.

Covers W1.3 of plan ``assurance-p1-gates-ab4758``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from ops_scripts.ci.check_runtime_trace_contract import (  # noqa: E402
    main,
    run_proof_for_contract,
)


class _FakeProc:
    """Minimal stand-in for subprocess.CompletedProcess."""

    def __init__(self, returncode: int, stdout: str, stderr: str = "") -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class TestRunProofForContract:
    def test_ok_result_parsed(self) -> None:
        payload = {
            "ok": True,
            "contract_id": "canary.lic.v1",
            "violations": [],
            "error": None,
        }
        with patch(
            "ops_scripts.ci.check_runtime_trace_contract.subprocess.run",
            return_value=_FakeProc(0, json.dumps(payload)),
        ):
            r = run_proof_for_contract("canary.lic.v1")
        assert r["ok"] is True
        assert r["exit_code"] == 0
        assert r["violations"] == []

    def test_violations_parsed(self) -> None:
        payload = {
            "ok": False,
            "contract_id": "canary.lic.v1",
            "violations": [
                {"kind": "missing_span", "detail": "x", "span_name": "foo"}
            ],
            "error": None,
        }
        with patch(
            "ops_scripts.ci.check_runtime_trace_contract.subprocess.run",
            return_value=_FakeProc(1, json.dumps(payload)),
        ):
            r = run_proof_for_contract("canary.lic.v1")
        assert r["ok"] is False
        assert r["exit_code"] == 1
        assert len(r["violations"]) == 1

    def test_timeout_returns_124(self) -> None:
        import subprocess as _sub

        with patch(
            "ops_scripts.ci.check_runtime_trace_contract.subprocess.run",
            side_effect=_sub.TimeoutExpired(cmd=["x"], timeout=5),
        ):
            r = run_proof_for_contract("canary.lic.v1", timeout=5)
        assert r["ok"] is False
        assert r["exit_code"] == 124
        assert "timeout" in (r["error"] or "")

    def test_invalid_json_yields_error(self) -> None:
        with patch(
            "ops_scripts.ci.check_runtime_trace_contract.subprocess.run",
            return_value=_FakeProc(0, "not-json-at-all"),
        ):
            r = run_proof_for_contract("canary.lic.v1")
        assert r["ok"] is False
        assert r["error"] is not None
        assert "proof_output_not_json" in r["error"]

    def test_empty_stdout_yields_error(self) -> None:
        with patch(
            "ops_scripts.ci.check_runtime_trace_contract.subprocess.run",
            return_value=_FakeProc(2, "", "boom"),
        ):
            r = run_proof_for_contract("canary.lic.v1")
        assert r["ok"] is False
        assert "empty_proof_output" in (r["error"] or "")


class TestMain:
    def test_main_passes_for_real_canary(
        self, capsys: pytest.CaptureFixture
    ) -> None:
        rc = main(["--contract", "canary.lic.v1"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "PASS" in out

    def test_main_returns_two_on_missing_contract(
        self, capsys: pytest.CaptureFixture
    ) -> None:
        rc = main(["--contract", "nope.does.not.exist.v1"])
        assert rc == 2  # contract_load_failed -> infra error
        out = capsys.readouterr().out
        assert "INFRA-ERROR" in out or "FAIL" in out

    def test_main_json_emits_results_array(
        self, capsys: pytest.CaptureFixture
    ) -> None:
        rc = main(["--contract", "canary.lic.v1", "--json"])
        assert rc == 0
        parsed = json.loads(capsys.readouterr().out)
        assert "results" in parsed
        assert parsed["results"][0]["contract_id"] == "canary.lic.v1"
