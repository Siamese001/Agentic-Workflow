"""apps-test-model: APP CONTRACT.

Strict L6 observability closure tests.
"""

from __future__ import annotations

import json
from pathlib import Path

from apps_rg.runtime.spine.l6_shadow_eval_runner import (
    _emit_l6_observability_closure_receipt,
)


def _paths(root: Path) -> tuple[dict[str, Path], dict[str, Path], Path]:
    trace = {
        "trace_reconciliation": root / "trace_reconciliation.json",
        "l6_trace_observability_summary": root / "l6_trace_observability_summary.json",
    }
    micro = {
        "l6_microstep_observations": root / "l6_microstep_observations.jsonl",
        "l6_apps_eval_grain_parity": root / "l6_apps_eval_grain_parity.json",
    }
    package_path = root / "l6_v40_shadow_eval_package.json"
    for path in (*trace.values(), *micro.values(), package_path):
        path.write_text("{}", encoding="utf-8")
    (root / "runtime_exhaust_bundle.json").write_text("{}", encoding="utf-8")
    (root / "exit_disposition_receipt.json").write_text("{}", encoding="utf-8")
    return trace, micro, package_path


def test_l6_advisory_only_evidence_is_a_hard_failure(tmp_path: Path) -> None:
    trace, micro, package_path = _paths(tmp_path)

    path = _emit_l6_observability_closure_receipt(
        artifact_dir=tmp_path,
        repo_root=tmp_path,
        package_path=package_path,
        package={
            "section_id": "headline",
            "runtime_exhaust_bundle_id": "reb-1",
            "valid_v40_shadow_exhaust": True,
            "readiness_decision": "READY_FOR_6B",
            "g28_audit_completeness": {"status": "PASS"},
            "g29_learning_firewall": {"status": "PASS"},
            "grain_parity_status": "WARN",
            "apps_eval_rows_bound": False,
            "evidence_class": "CONTRACT_ONLY_ADVISORY",
            "current_run_mutation_assertion": False,
            "current_run_x3_mutation_assertion": False,
            "direct_l4_write_assertion": False,
            "durable_write_assertion": False,
            "future_run_only_assertion": True,
        },
        trace_reconciliation_paths=trace,
        microstep_paths=micro,
    )
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["closure_status"] == "FAIL"
    assert "grain_parity_pass" in payload["failed_checks"]
    assert "apps_eval_rows_bound" in payload["failed_checks"]
    assert "apps_eval_bound_evidence" in payload["failed_checks"]


def test_l6_apps_eval_bound_evidence_closes_strictly(tmp_path: Path) -> None:
    trace, micro, package_path = _paths(tmp_path)

    path = _emit_l6_observability_closure_receipt(
        artifact_dir=tmp_path,
        repo_root=tmp_path,
        package_path=package_path,
        package={
            "section_id": "headline",
            "runtime_exhaust_bundle_id": "reb-1",
            "valid_v40_shadow_exhaust": True,
            "readiness_decision": "READY_FOR_6B",
            "g28_audit_completeness": {"status": "PASS"},
            "g29_learning_firewall": {"status": "PASS"},
            "grain_parity_status": "PASS",
            "apps_eval_rows_bound": True,
            "evidence_class": "APPS_EVAL_BOUND_PROOF",
            "current_run_mutation_assertion": False,
            "current_run_x3_mutation_assertion": False,
            "direct_l4_write_assertion": False,
            "durable_write_assertion": False,
            "future_run_only_assertion": True,
        },
        trace_reconciliation_paths=trace,
        microstep_paths=micro,
    )
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["closure_status"] == "PASS"
    assert payload["failed_checks"] == []
