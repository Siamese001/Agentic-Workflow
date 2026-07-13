from __future__ import annotations

import hashlib
import json
from pathlib import Path

from apps_rg.runtime.spine.l6_shadow_eval_runner import (
    maybe_run_l6_v40_shadow_eval_for_section,
    run_l6_v40_shadow_eval_for_section,
)
from tests.l6_observability.test_runtime_exhaust_v40_adapter import _seed_artifacts


def _seed_l5_receipt(root: Path) -> None:
    payload = {
        "schema_version": "apps_rg.l5_certification_receipt.v1",
        "certification_status": "PASS",
        "scope": "apps_rg.l6_shadow_eval",
        "run_id": "run-v40",
        "tenant_id": "tenant-apps-rg",
        "expires_at_utc": "2099-01-01T00:00:00Z",
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload["receipt_digest"] = "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()
    (root / "l5_certification_receipt.json").write_text(
        json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8"
    )


def test_apps_rg_v40_runner_closes_observability_with_eval_binding_pending(
    tmp_path: Path,
) -> None:
    _seed_artifacts(tmp_path)
    _seed_l5_receipt(tmp_path)

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
    assert package["registry_digest"] == package["microstep_contract_digest"]
    assert package["registry_digest"].startswith("sha256:")
    assert package["runtime_exhaust_bundle_digest"].startswith("sha256:")

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
    assert closure["registry_digest"] == package["registry_digest"]


def test_trace_reconciliation_is_emitted_before_microstep_observation(
    tmp_path: Path,
) -> None:
    _seed_artifacts(tmp_path)
    _seed_l5_receipt(tmp_path)
    outputs = run_l6_v40_shadow_eval_for_section(
        tmp_path,
        section_id="summary",
        repo_root=tmp_path,
        tenant_id="tenant-apps-rg",
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
    _seed_l5_receipt(tmp_path)
    assert maybe_run_l6_v40_shadow_eval_for_section(
        tmp_path,
        section_id="summary",
        repo_root=tmp_path,
        env={
            "APPS_RG_L6_V40_SHADOW_EVAL_SKIP": "1",
            "APPS_RG_EXECUTION_PROFILE": "non_product",
        },
    ) == {}

    outputs = maybe_run_l6_v40_shadow_eval_for_section(
        tmp_path,
        section_id="summary",
        repo_root=tmp_path,
        tenant_id="tenant-apps-rg",
        l5_certification_ref="l5-cert-ref:apps-rg",
        env={"APPS_RG_L6_V40_SHADOW_EVAL": "1"},
    )
    assert outputs["l6_v40_shadow_eval_package"].is_file()


def test_product_profile_cannot_skip_l6(tmp_path: Path) -> None:
    _seed_artifacts(tmp_path)
    _seed_l5_receipt(tmp_path)
    outputs = maybe_run_l6_v40_shadow_eval_for_section(
        tmp_path,
        section_id="summary",
        repo_root=tmp_path,
        tenant_id="tenant-apps-rg",
        l5_certification_ref="l5-cert-ref:apps-rg",
        env={
            "APPS_RG_L6_V40_SHADOW_EVAL_SKIP": "1",
            "APPS_RG_EXECUTION_PROFILE": "product",
        },
    )
    assert outputs["l6_v40_shadow_eval_package"].is_file()


def test_invalid_l5_receipt_fails_observability_closure(tmp_path: Path) -> None:
    _seed_artifacts(tmp_path)
    _seed_l5_receipt(tmp_path)
    receipt_path = tmp_path / "l5_certification_receipt.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["receipt_digest"] = "sha256:" + "0" * 64
    receipt_path.write_text(json.dumps(receipt) + "\n", encoding="utf-8")

    outputs = run_l6_v40_shadow_eval_for_section(
        tmp_path,
        section_id="summary",
        repo_root=tmp_path,
        tenant_id="tenant-apps-rg",
        l5_certification_ref="l5-cert-ref:apps-rg",
    )
    package = json.loads(outputs["l6_v40_shadow_eval_package"].read_text(encoding="utf-8"))
    closure = json.loads(
        outputs["l6_observability_closure_receipt"].read_text(encoding="utf-8")
    )
    assert package["l5_certification_valid"] is False
    assert "L5_CERTIFICATION_DIGEST_INVALID" in package["v40_gap_codes"]
    assert closure["observability_closure_status"] == "FAIL"
