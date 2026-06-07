"""The eval suite must be all-green and the safety invariants must hold."""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from src.runtime.eval_suite import EVAL_CASES, run_eval  # noqa: E402


def test_all_eval_cases_pass():
    report = run_eval()
    failures = [r.case.case_id for r in report["results"] if not r.passed]
    assert failures == [], f"eval failures: {failures}"
    assert report["passed"] == report["total"] == len(EVAL_CASES)


def test_injection_always_caught_by_gate():
    report = run_eval()
    # The load-bearing guarantee: every injection is stopped by the gate.
    assert report["injection_cases"] >= 2
    assert report["injection_gate_caught"] == report["injection_cases"]


def test_only_authorized_paths_write():
    report = run_eval()
    # Exactly the clean-auto and complaint-approved cases produce a durable write.
    writers = {r.case.case_id for r in report["results"] if r.wrote}
    assert writers == {"clean_auto", "complaint_approved"}
    assert report["durable_writes"] == 2


def test_no_injection_case_ever_writes():
    report = run_eval()
    for r in report["results"]:
        if r.case.category == "injection":
            assert r.wrote is False
            assert r.final_exit != "X3C_COMMIT_REQUEST_TO_UWG"
