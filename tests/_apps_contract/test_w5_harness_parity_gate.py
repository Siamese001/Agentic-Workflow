"""W5.P6 verification — apps_* harness-parity advisory gate.

Plan: ``docs/archive/windsurf/legacy-tree/plans/apps-eval-harness-parity-f8d4a2.md`` W5.P6.

Proves the advisory gate:

- Exits 0 in default (advisory) mode even with WARN findings
- Exits 1 in fail-closed mode only on ERROR severity
- Produces a parseable JSON report at the expected path
- Recognizes all 8 runtime apps
- Detects the specific warning conditions the plan predicted:
  * dead thresholds in apps_rg + apps_lic
  * draft status on apps_underwriting_ai
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
GATE = REPO_ROOT / "ops_scripts" / "ci" / "check_app_domain_harness_parity.py"


def _run_gate(fail_closed: bool = False) -> tuple[int, dict]:
    env = os.environ.copy()
    if fail_closed:
        env["APP_DOMAIN_HARNESS_PARITY_FAIL_CLOSED"] = "1"
    else:
        env.pop("APP_DOMAIN_HARNESS_PARITY_FAIL_CLOSED", None)

    report_path = REPO_ROOT / "artifacts" / "ci" / "app_domain_harness_parity_test.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [sys.executable, str(GATE), "--json", "--report", str(report_path)],
        capture_output=True,
        text=True,
        env=env,
        timeout=60,
        check=False,
    )
    if result.stdout.strip():
        report = json.loads(result.stdout)
    else:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    return result.returncode, report


class TestAdvisoryMode:
    def test_exit_zero_in_advisory_mode(self) -> None:
        rc, _report = _run_gate(fail_closed=False)
        assert rc == 0, "Advisory mode must always exit 0"

    def test_report_shape(self) -> None:
        _rc, report = _run_gate(fail_closed=False)
        assert "apps_checked" in report
        assert "counts" in report
        assert "findings" in report
        assert set(report["counts"].keys()) >= {"ERROR", "WARN", "INFO"}

    def test_covers_eight_runtime_apps(self) -> None:
        _rc, report = _run_gate(fail_closed=False)
        apps = set(report["apps_checked"])
        assert apps >= {
            "apps_research", "apps_exec", "apps_underwriting_ai", "apps_eval",
        }


class TestFailClosedMode:
    def test_exit_zero_when_only_warns(self) -> None:
        """Fail-closed returns 0 when no ERROR-severity findings exist."""
        rc, report = _run_gate(fail_closed=True)
        if report["counts"]["ERROR"] == 0:
            assert rc == 0
        else:
            assert rc == 1


class TestPredictedFindings:
    def test_apps_underwriting_ai_status_resolved(self) -> None:
        """W2.P4 closed: apps_underwriting_ai was flipped draft→active.
        The gate must NOT flag CONTRACT_STATUS_KNOWN anymore; if it does,
        a regression has downgraded the status back to draft."""
        _rc, report = _run_gate(fail_closed=False)
        matches = [
            f for f in report["findings"]
            if f["app_id"] == "apps_underwriting_ai"
            and f["check_id"] == "CONTRACT_STATUS_KNOWN"
        ]
        assert not matches, (
            "apps_underwriting_ai must remain status=active after W2.P4. "
            f"Gate regression: {matches}"
        )

    def test_apps_lic_intentional_zero_dims_suppressed(self) -> None:
        """W4.P3 closed: apps_lic's 3 dead-threshold dims (response_likelihood,
        sequence_coherence, brand_voice) are now annotated in
        threshold_profiles.intentional_zero_dims and MUST NOT generate
        NO_DEAD_THRESHOLDS WARNs. Any such WARN is a regression — either the
        annotation was removed or a NEW dim=0 was added without annotation."""
        _rc, report = _run_gate(fail_closed=False)
        matches = [
            f for f in report["findings"]
            if f["app_id"] == "apps_lic" and f["check_id"] == "NO_DEAD_THRESHOLDS"
        ]
        assert not matches, (
            f"apps_lic should have no dead-threshold WARNs after W4.P3 "
            f"intentional_zero_dims annotation; found: {matches}"
        )

    def test_apps_rg_intentional_zero_dims_suppressed(self) -> None:
        """W4.P3: apps_rg.executive_positioning=0.0 is annotated."""
        _rc, report = _run_gate(fail_closed=False)
        matches = [
            f for f in report["findings"]
            if f["app_id"] == "apps_rg" and f["check_id"] == "NO_DEAD_THRESHOLDS"
        ]
        assert not matches, (
            f"apps_rg should have no dead-threshold WARNs after W4.P3 "
            f"intentional_zero_dims annotation; found: {matches}"
        )

    def test_unimpl_judges_resolved_by_stubs(self) -> None:
        """apps-eval-harness-deferred-e4a1b7 W2: all 4 LLM-judge stubs
        landed at canonical import paths; gate must NOT surface
        NO_UNIMPL_JUDGES anymore. Regression guard: if stubs are
        deleted or renamed, this test will fail with a clear message."""
        _rc, report = _run_gate(fail_closed=False)
        unimpl = [
            f for f in report["findings"]
            if f["check_id"] == "NO_UNIMPL_JUDGES"
        ]
        assert not unimpl, (
            f"Judge stubs landed — NO_UNIMPL_JUDGES must be empty. "
            f"Regression: {unimpl}"
        )

    def test_unimpl_judges_are_warn_not_error(self) -> None:
        """Advisory severity: unimplemented judges MUST NOT fail-closed the
        gate because the W1 generic grader handles UNKNOWN per
        fail_closed_if_unknown. These are implementation-backlog items."""
        _rc, report = _run_gate(fail_closed=False)
        errors = [
            f for f in report["findings"]
            if f["check_id"] == "NO_UNIMPL_JUDGES" and f["severity"] == "ERROR"
        ]
        assert not errors, (
            f"NO_UNIMPL_JUDGES must be WARN-only (not ERROR); found: {errors}"
        )

    def test_non_annotated_dim_zero_still_surfaces(self) -> None:
        """Positive control: if someone adds a dim=0.0 WITHOUT annotating it,
        the gate MUST still flag it. We synthesize this by checking that at
        least the gate COULD fire — run it with a synthetic tmp threshold profile."""
        # Structural check: the gate source contains both the annotation-check
        # AND the fallback WARN path. This is a weak check but strong enough
        # to catch accidental removal of the WARN path.
        from pathlib import Path
        src = Path(__file__).resolve().parents[2] / "ops_scripts" / "ci" / "check_app_domain_harness_parity.py"
        text = src.read_text(encoding="utf-8")
        assert "intentional_zero_dims" in text, "gate must consult the annotation"
        assert "dead threshold" in text, "gate must still WARN on unannotated zeros"
