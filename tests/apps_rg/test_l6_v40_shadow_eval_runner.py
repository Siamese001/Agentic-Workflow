"""apps-test-model: APP CONTRACT."""

from __future__ import annotations

import json
from pathlib import Path

from apps_rg.runtime.spine.l6_shadow_eval_runner import (
    maybe_run_l6_v40_shadow_eval_for_section,
    run_l6_v40_shadow_eval_for_section,
)
from tests.l6_observability.test_runtime_exhaust_v40_adapter import _seed_artifacts


def test_apps_rg_v40_runner_writes_package_and_spans(tmp_path: Path) -> None:
    _seed_artifacts(tmp_path)

    outputs = run_l6_v40_shadow_eval_for_section(
        tmp_path,
        section_id="summary",
        repo_root=tmp_path,
        session_id="sess-apps-rg",
        tenant_id="tenant-apps-rg",
        l5_certification_ref="l5-cert-ref:apps-rg",
    )

    package = json.loads(outputs["l6_v40_shadow_eval_package"].read_text(encoding="utf-8"))
    assert package["valid_v40_shadow_exhaust"] is True
    assert package["g28_audit_completeness"]["verdict"] == "PASS"
    assert package["g29_learning_firewall"]["verdict"] == "PASS"
    assert package["current_run_x3_mutation_assertion"] is False
    assert outputs["l6_v40_shadow_eval_spans"].is_file()
    assert outputs["trace_reconciliation"].is_file()
    assert outputs["trace_reconciliation_rows"].is_file()
    assert outputs["l6_trace_observability_summary"].is_file()
    assert outputs["l6_observability_closure_receipt"].is_file()
    assert package["trace_reconciliation_ref"] == "trace_reconciliation.json"
    assert package["trace_reconciliation_rows_ref"] == "trace_reconciliation_rows.jsonl"
    assert package["l6_trace_observability_summary_ref"] == "l6_trace_observability_summary.json"
    assert package["l6_observability_closure_receipt_ref"] == "l6_observability_closure_receipt.json"
    assert outputs["l6_apps_eval_grain_parity"].is_file()
    assert package["l6_apps_eval_grain_parity_ref"] == "l6_apps_eval_grain_parity.json"
    assert package["alignment_source"] == "contract_only_pseudo_rows"
    assert package["evidence_class"] == "CONTRACT_ONLY_ADVISORY"
    assert package["apps_eval_rows_bound"] is False
    assert package["grain_parity_status"] == "WARN"
    closure = json.loads(outputs["l6_observability_closure_receipt"].read_text(encoding="utf-8"))
    assert closure["closure_status"] == "FAIL"
    assert closure["failed_checks"] == [
        "grain_parity_pass",
        "apps_eval_rows_bound",
        "apps_eval_bound_evidence",
    ]
    assert closure["checks"]["trace_reconciliation_exists"] is True
    observations = [
        json.loads(line)
        for line in outputs["l6_microstep_observations"].read_text(encoding="utf-8").splitlines()
    ]
    trace_rows = [
        row
        for row in observations
        if row["microstep_id"] == "L6.trace_reconciliation.present"
    ]
    assert trace_rows[0]["observed_status"] == "OBSERVED"


def test_section_l6_contract_only_grain_parity_warns(tmp_path: Path) -> None:
    _seed_artifacts(tmp_path)

    outputs = run_l6_v40_shadow_eval_for_section(
        tmp_path,
        section_id="summary",
        repo_root=tmp_path,
        session_id="sess-apps-rg",
        tenant_id="tenant-apps-rg",
        l5_certification_ref="l5-cert-ref:apps-rg",
    )

    parity = json.loads(outputs["l6_apps_eval_grain_parity"].read_text(encoding="utf-8"))
    assert parity["alignment_source"] == "contract_only_pseudo_rows"
    assert parity["apps_eval_rows_bound"] is False
    assert parity["grain_parity_status"] == "WARN"


def test_apps_rg_v40_runner_is_env_gated(tmp_path: Path) -> None:
    _seed_artifacts(tmp_path)

    default_outputs = maybe_run_l6_v40_shadow_eval_for_section(
        tmp_path,
        section_id="summary",
        repo_root=tmp_path,
        session_id="sess-apps-rg",
        tenant_id="tenant-apps-rg",
        l5_certification_ref="l5-cert-ref:apps-rg",
        env={},
    )
    assert default_outputs["l6_v40_shadow_eval_package"].is_file()

    assert maybe_run_l6_v40_shadow_eval_for_section(
        tmp_path,
        section_id="summary",
        repo_root=tmp_path,
        env={"APPS_RG_L6_V40_SHADOW_EVAL_SKIP": "1"},
    ) == {}

    outputs = maybe_run_l6_v40_shadow_eval_for_section(
        tmp_path,
        section_id="summary",
        repo_root=tmp_path,
        session_id="sess-apps-rg",
        tenant_id="tenant-apps-rg",
        l5_certification_ref="l5-cert-ref:apps-rg",
        env={"APPS_RG_L6_V40_SHADOW_EVAL": "1"},
    )
    assert outputs["l6_v40_shadow_eval_package"].is_file()
