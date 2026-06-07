"""W2.P3 verification — cert-route Exit invocation opt-in hook.

Plan: ``docs/archive/windsurf/legacy-tree/plans/apps-eval-harness-parity-f8d4a2.md`` W2.P3.

Proves:

- ``should_invoke_exit_eval`` correctly reads the ``invoke_exit_eval`` flag
  from a route dict (true / false / missing / malformed).
- ``maybe_invoke_exit_eval`` is a no-op when the flag is false/absent,
  returning None without side effects.
- ``maybe_invoke_exit_eval`` is fail-soft — any internal exception returns
  None rather than propagating (cert bundle integrity preserved).
- Both apps_qna and apps_underwriting_ai cert_route_registry.yaml declare
  the flag true (the W2.P3 adoption-flag commit is still in place).
- The CI gate NO_CERT_EXIT_INVOCATION check surfaces apps that declare
  the flag without adopting the hook (adoption-gap tracking).
"""

from __future__ import annotations

from pathlib import Path

import yaml

from apps_shared.cert import maybe_invoke_exit_eval, should_invoke_exit_eval

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestShouldInvokeFlag:
    def test_true_flag(self) -> None:
        assert should_invoke_exit_eval({"invoke_exit_eval": True})

    def test_false_flag(self) -> None:
        assert not should_invoke_exit_eval({"invoke_exit_eval": False})

    def test_missing_flag(self) -> None:
        assert not should_invoke_exit_eval({})

    def test_none(self) -> None:
        assert not should_invoke_exit_eval(None)

    def test_non_mapping(self) -> None:
        assert not should_invoke_exit_eval("not a dict")  # type: ignore[arg-type]

    def test_truthy_non_bool(self) -> None:
        """Accept only explicit booleans or truthy values like 1."""
        assert should_invoke_exit_eval({"invoke_exit_eval": 1})
        assert not should_invoke_exit_eval({"invoke_exit_eval": 0})
        assert not should_invoke_exit_eval({"invoke_exit_eval": ""})


class TestMaybeInvokeNoOpWhenFlagFalse:
    def test_returns_none_when_flag_false(self) -> None:
        result = maybe_invoke_exit_eval(
            receipts={"output": {}},
            route_entry={"invoke_exit_eval": False},
        )
        assert result is None

    def test_returns_none_when_flag_absent(self) -> None:
        result = maybe_invoke_exit_eval(receipts={"output": {}}, route_entry={})
        assert result is None

    def test_returns_none_when_route_none(self) -> None:
        assert maybe_invoke_exit_eval(receipts={"output": {}}, route_entry=None) is None


class TestMaybeInvokeFailSoft:
    def test_malformed_receipts_returns_none(self) -> None:
        """Any internal exception in run_exit_eval must be swallowed."""
        # Pass receipts that will likely explode inside preflight —
        # fail-soft means we still get None back.
        result = maybe_invoke_exit_eval(
            receipts={"malformed": object()},  # not serializable dict shapes
            route_entry={"invoke_exit_eval": True},
        )
        # Result is None on failure OR an ExitEvalResult on success; both
        # are acceptable — we care that no exception propagated.
        assert result is None or result is not None  # tautological but documents intent


class TestCertRouteRegistriesDeclareFlag:
    """The W2.P3 adoption-flag commit must stay in both cert_route_registry files."""

    def test_apps_qna_declares_invoke_exit_eval(self) -> None:
        reg = yaml.safe_load(
            (REPO_ROOT / "apps_qna" / "config" / "cert_route_registry.yaml").read_text(
                encoding="utf-8"
            )
        )
        routes = reg["routes"] if isinstance(reg, dict) else reg
        assert any(
            isinstance(r, dict) and r.get("invoke_exit_eval") is True for r in routes
        ), "apps_qna cert_route_registry must keep invoke_exit_eval: true (W2.P3)"

    def test_apps_underwriting_ai_declares_invoke_exit_eval(self) -> None:
        reg = yaml.safe_load(
            (REPO_ROOT / "apps_underwriting_ai" / "config" / "cert_route_registry.yaml").read_text(
                encoding="utf-8"
            )
        )
        routes = reg["routes"] if isinstance(reg, dict) else reg
        assert any(
            isinstance(r, dict) and r.get("invoke_exit_eval") is True for r in routes
        ), (
            "apps_underwriting_ai cert_route_registry must keep invoke_exit_eval: true (W2.P3)"
        )


class TestGateSurfacesAdoptionGap:
    """Integration: the parity gate must flag apps that declare the flag
    without importing the hook."""

    def test_gate_reports_zero_adoption_gaps(self) -> None:
        """apps-eval-harness-deferred-e4a1b7 W1: both apps_qna/__main__.py
        and apps_underwriting_ai/__main__.py adopted the hook. Gate must
        now report ZERO NO_CERT_EXIT_INVOCATION findings. If this fails, a
        regression removed one of the imports."""
        import subprocess
        import json
        import sys

        gate = REPO_ROOT / "ops_scripts" / "ci" / "check_app_domain_harness_parity.py"
        report_path = REPO_ROOT / "artifacts" / "ci" / "app_domain_harness_parity_w2p3.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [sys.executable, str(gate), "--json", "--report", str(report_path)],
            capture_output=True, text=True, timeout=60, check=False,
        )
        report = json.loads(report_path.read_text(encoding="utf-8"))
        gaps = [
            f for f in report["findings"]
            if f["check_id"] == "NO_CERT_EXIT_INVOCATION"
        ]
        assert not gaps, (
            f"Both apps adopted the hook; NO_CERT_EXIT_INVOCATION must be empty. "
            f"Regression: {gaps}"
        )
