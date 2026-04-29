"""End-to-end tests for the runtime trace proof runner.

Covers W1.2 of plan ``assurance-p1-gates-ab4758``.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Ensure repo root is importable when this test runs in any pytest config.
_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.proof.run_runtime_trace_proof import main, run_proof  # noqa: E402


class TestRunProofHappyPath:
    def test_canary_passes(self) -> None:
        result = run_proof(contract_id="canary.lic.v1")
        assert result["ok"] is True, f"expected pass; result={result!r}"
        assert result["error"] is None
        assert result["spans_emitted"] == 7
        assert result["spans_ingested"] == 7
        assert result["snapshot_id"] is not None
        assert result["violations"] == []

    def test_explicit_trace_id_carried_through(self) -> None:
        result = run_proof(contract_id="canary.lic.v1", trace_id="explicit-tid-1")
        assert result["trace_id"] == "explicit-tid-1"
        assert result["ok"] is True


class TestRunProofMissingContract:
    def test_unresolved_contract_yields_error(self) -> None:
        result = run_proof(contract_id="nonexistent.canary.v1")
        assert result["ok"] is False
        assert result["error"] is not None
        assert "contract_load_failed" in str(result["error"])
        assert result["violations"] == []


class TestRunProofNegativeControl:
    """Confirm the proof fails closed when a required span is missing.

    This is a critical assurance: an empty or truncated trace MUST be
    detected. We patch the canary builder to drop the final UWG span and
    confirm the proof returns ok=False with a missing_span violation.
    """

    def test_missing_uwg_span_fails(self) -> None:
        from agentic_core.L6_observability.runtime_trace import (
            build_canary_lic_spans,
        )

        def _truncated(**kwargs: object) -> list[dict]:
            spans = build_canary_lic_spans(**kwargs)  # type: ignore[arg-type]
            return [s for s in spans if s["name"] != "uwg.commit"]

        # Patch in BOTH the source module (canary_emitter) and the
        # re-export at the package surface — run_proof imports from the
        # latter, but unittest.mock can only resolve the actual lookup.
        with (
            patch(
                "agentic_core.L6_observability.runtime_trace.canary_emitter.build_canary_lic_spans",
                side_effect=_truncated,
            ),
            patch(
                "agentic_core.L6_observability.runtime_trace.build_canary_lic_spans",
                side_effect=_truncated,
            ),
        ):
            result = run_proof(contract_id="canary.lic.v1")

        assert result["ok"] is False, "truncated trace must fail proof"
        assert result["error"] is None  # Not infrastructure error - genuine violation.
        kinds = {v["kind"] for v in result["violations"]}
        assert "missing_span" in kinds


class TestMainCli:
    def test_main_returns_zero_on_pass(self, capsys: pytest.CaptureFixture) -> None:
        rc = main(["--contract", "canary.lic.v1"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "PASS" in out

    def test_main_returns_two_on_missing_contract(self, capsys: pytest.CaptureFixture) -> None:
        rc = main(["--contract", "nope.does.not.exist.v1"])
        assert rc == 2
        out = capsys.readouterr().out
        assert "FAIL" in out
        assert "contract_load_failed" in out

    def test_main_json_emits_valid_json(self, capsys: pytest.CaptureFixture) -> None:
        import json as _json

        rc = main(["--contract", "canary.lic.v1", "--json"])
        assert rc == 0
        out = capsys.readouterr().out
        parsed = _json.loads(out)
        assert parsed["ok"] is True
        assert parsed["contract_id"] == "canary.lic.v1"
        assert parsed["spans_emitted"] == 7
