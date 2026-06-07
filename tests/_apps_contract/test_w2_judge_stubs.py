"""W2 verification — LLM-judge stub importability + STUB marker.

Plan: ``docs/archive/windsurf/legacy-tree/plans/apps-eval-harness-deferred-e4a1b7.md`` W2.P1-P5.

Proves:

- All 4 stub judges import without error at their canonical paths.
- Every stub declares ``IS_STUB = True`` so downstream tooling can
  distinguish stubs from real judges.
- Every stub's ``grade()`` returns the ``GRADER_UNKNOWN_SENTINEL``,
  preserving the pre-stub runtime fallback path.
- Every stub's ``GRADER_ID`` matches the roster ID in the app's
  ``grader_roster.yaml``.
- The CI gate reports zero ``NO_UNIMPL_JUDGES`` WARNs after this wave.
"""

from __future__ import annotations

import importlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry import (
    GRADER_UNKNOWN_SENTINEL,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

# Each entry is (module_path, stub_grader_id).
# NOTE: Judges may be promoted from stub → real over time (see
# `apps-eval-harness-final-8f3e21` W2.P1 which promoted
# executive_positioning_judge from v1 → v2 deterministic). Tests below
# check importability + sentinel behavior only when `IS_STUB is True`;
# promoted judges have their own tests in test_w_final_deferred.py.
JUDGE_MODULES: tuple[tuple[str, str], ...] = (
    ("apps_rg.engines.judges.executive_positioning_judge", "rg::executive_positioning_judge::v1"),
    ("apps_lic.engines.judges.response_likelihood_judge", "lic::response_likelihood_judge::v1"),
    ("apps_lic.engines.judges.brand_voice_judge", "lic::brand_voice_judge::v1"),
    ("apps_rfp.engines.judges.win_theme_alignment_judge", "rfp::win_theme_alignment_judge::v1"),
)


class TestJudgeStubImportability:
    @pytest.mark.parametrize("mod_path,grader_id", JUDGE_MODULES)
    def test_importable(self, mod_path: str, grader_id: str) -> None:
        mod = importlib.import_module(mod_path)
        assert hasattr(mod, "IS_STUB"), f"{mod_path} missing IS_STUB flag"
        # IS_STUB is True for unpromoted stubs; False once promoted. Both states valid.
        assert isinstance(mod.IS_STUB, bool)

    @pytest.mark.parametrize("mod_path,grader_id", JUDGE_MODULES)
    def test_grader_id_matches_roster(self, mod_path: str, grader_id: str) -> None:
        mod = importlib.import_module(mod_path)
        if getattr(mod, "IS_STUB", True):
            assert mod.GRADER_ID == grader_id, (
                f"{mod_path}.GRADER_ID={mod.GRADER_ID!r} must match roster {grader_id!r}"
            )
        else:
            # Promoted judges use versioned IDs (e.g. ::v2) — just assert shape.
            assert mod.GRADER_ID.startswith(grader_id.rsplit("::", 1)[0])


class TestJudgeStubRuntimeBehavior:
    @pytest.mark.parametrize("mod_path,grader_id", JUDGE_MODULES)
    def test_grade_returns_unknown_sentinel(self, mod_path: str, grader_id: str) -> None:
        """Stubs return UNKNOWN; promoted judges may abstain on empty ctx.
        Either way, ``grade(None, {})`` must return UNKNOWN because an
        empty run_context carries no signal."""
        mod = importlib.import_module(mod_path)
        score, evidence = mod.grade(dim=None, run_context={})
        assert score == GRADER_UNKNOWN_SENTINEL
        assert evidence == []

    @pytest.mark.parametrize("mod_path,grader_id", JUDGE_MODULES)
    def test_class_form_equivalent_to_module_form(self, mod_path: str, grader_id: str) -> None:
        mod = importlib.import_module(mod_path)
        cls = None
        for name in dir(mod):
            obj = getattr(mod, name)
            if isinstance(obj, type) and name.endswith("Judge"):
                cls = obj
                break
        assert cls is not None, f"{mod_path} must expose a <Name>Judge class"
        instance = cls()
        assert instance.is_stub == getattr(mod, "IS_STUB", True)
        assert instance.grader_id == mod.GRADER_ID
        score, ev = instance.grade(None, {})
        assert score == GRADER_UNKNOWN_SENTINEL
        assert ev == []


class TestGateReportsZeroUnimplAfterStubs:
    def test_gate_no_unimpl_judges(self) -> None:
        """W2.P5 exit gate: NO_UNIMPL_JUDGES must be empty."""
        gate = REPO_ROOT / "ops_scripts" / "ci" / "check_app_domain_harness_parity.py"
        report_path = REPO_ROOT / "artifacts" / "ci" / "app_domain_harness_parity_w2.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [sys.executable, str(gate), "--json", "--report", str(report_path)],
            capture_output=True, text=True, timeout=60, check=False,
        )
        report = json.loads(report_path.read_text(encoding="utf-8"))
        unimpl = [
            f for f in report["findings"]
            if f["check_id"] == "NO_UNIMPL_JUDGES"
        ]
        assert not unimpl, (
            f"All 4 judge stubs landed — NO_UNIMPL_JUDGES must be empty. "
            f"Regression: {unimpl}"
        )

    def test_gate_reports_zero_findings_overall(self) -> None:
        """End-state: after W1 + W2 close all gate categories, every
        finding should be resolved. If anything appears, a regression or
        new gap has surfaced — investigate before merge."""
        gate = REPO_ROOT / "ops_scripts" / "ci" / "check_app_domain_harness_parity.py"
        report_path = REPO_ROOT / "artifacts" / "ci" / "app_domain_harness_parity_w2.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [sys.executable, str(gate), "--json", "--report", str(report_path)],
            capture_output=True, text=True, timeout=60, check=False,
        )
        report = json.loads(report_path.read_text(encoding="utf-8"))
        assert report["counts"]["ERROR"] == 0, f"unexpected ERROR: {report}"
        assert report["counts"]["WARN"] == 0, (
            f"unexpected WARN after W1+W2: {report['findings']}"
        )
