from __future__ import annotations

import json
from pathlib import Path

from apps_rg.runtime.spine.l6_shadow_eval_runner import (
    maybe_run_l6_v40_shadow_eval_for_section,
    run_l6_v40_shadow_eval_for_section,
)
from tests.l6_observability.test_runtime_exhaust_v40_adapter import _seed_artifacts


def test_apps_rg_v40_runner_closes_observability_with_eval_binding_pending(
    tmp_path: Path,
) -> None:
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
    closure = json.loads(
        outputs["l6_observability_closure_receipt"].read_text(encoding="utf-8")
    )

    assert package["valid_v40_shadow_exhaust"] is True
    assert package["g28_audit_completeness"]["verdict"] == "PASS"
    assert package["g29_learning_firewall"]["verdict"] == "PASS"
    assert package["current_run_x3_mutation_assertion"] is False
    assert package["alignment_source"] == "contract_only_pseudo_rows"
    assert package["evidence_class"] == "CONTRACT_ONLY_ADVISORY"
    assert package["apps_eval_rows_bound"] is False
    assert package["grain_parity_status"] == "WARN"

    assert outputs["l6_v40_shadow_eval_spans"].is_file()
    assert outputs["trace_reconciliation"].is_file()
    assert outputs["trace_reconciliation_rows"].is_file()
    assert outputs["l6_trace_observability_summary"].is_file()
    assert outputs["l6_microstep_observations"].is_file()
    assert closure["observability_closure_status"] == "PASS"
    assert closure["closure_status"] == "PASS"
    assert closure["eval_binding_status"] == "PENDING"
    assert closure["failed_checks"] == []
    assert closure["artifact_digests"]
    assert closure["closure_digest"].startswith("sha256:")


def test_trace_reconciliation_is_emitted_before_microstep_observation(
    tmp_path: Path,
) -> None:
    _seed_artifacts(tmp_path)
    outputs = run_l6_v40_shadow_eval_for_section(
        tmp_path,
        section_id="summary",
        repo_root=tmp_path,
        l5_certification_ref="l5-cert-ref:apps-rg",
    )
    observations = [
        json.loads(line)
        for line in outputs["l6_microstep_observations"].read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    trace_rows = [
        row for row in observations if row["microstep_id"] == "L6.trace_reconciliation.present"
    ]
    assert trace_rows
    assert trace_rows[0]["observed_status"] == "OBSERVED"


def test_apps_rg_v40_runner_is_env_gated(tmp_path: Path) -> None:
    _seed_artifacts(tmp_path)
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
        l5_certification_ref="l5-cert-ref:apps-rg",
        env={"APPS_RG_L6_V40_SHADOW_EVAL": "1"},
    )
    assert outputs["l6_v40_shadow_eval_package"].is_file()
