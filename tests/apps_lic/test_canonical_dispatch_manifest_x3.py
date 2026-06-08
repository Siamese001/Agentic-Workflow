"""Manifest X3 serialization for canonical apps_lic dispatch."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentic_core.runtime.contracts.x3_disposition import X3Disposition
from apps_lic.runtime.dispatch import stage_receipts as sr
from apps_lic.runtime.dispatch.canonical_dispatch import (
    build_cli_ingress_raw,
    run_canonical_apps_lic_spine,
)
from apps_lic.runtime.dispatch.spine_run_result import (
    SpineRunResult,
    x3_manifest_fields,
)

_R4_MANAGED_STAGE_FILES = (
    sr.FILENAME_INGRESS_RAW,
    sr.FILENAME_U0_RECEIPT,
    sr.FILENAME_L1_PLAN,
    sr.FILENAME_ROUTE_CONTRACT,
    sr.FILENAME_C0_FEC,
    sr.FILENAME_FEC_SUMMARY,
    sr.FILENAME_PA_RECEIPT,
    sr.FILENAME_L3_WORKFLOW,
    sr.FILENAME_L2_EXECUTION,
    sr.FILENAME_EXIT_DISPOSITION,
    sr.FILENAME_SPINE_MANIFEST,
)


def _assert_stage_receipt(data: dict, *, stage: str) -> None:
    assert data["schema_version"] == sr.STAGE_RECEIPT_SCHEMA_VERSION
    assert data["stage"] == stage
    assert data["request_id"]
    assert data["run_id"]
    assert data["digest"]
    assert data["artifact_ref"]
    assert isinstance(data["upstream_receipt_refs"], list)
    assert isinstance(data["downstream_receipt_refs"], list)

_EXIT_CERT_REF = "exit-apps-lic-outreach-message-ag8-w7-f3c2e1"


class TestX3ManifestFieldsHelper:
    def test_extracts_final_output_disposition_x3d(self) -> None:
        x3 = X3Disposition(
            request_id="req_1",
            run_id="run_1",
            app_id="apps_lic",
            trace_id="trace_1",
            exit_status="success",
            outcome_authorized=True,
            final_output={"disposition": "X3D", "reason_codes": []},
            l5_certification_ref=_EXIT_CERT_REF,
        )
        disp, exit_status, authorized = x3_manifest_fields(x3)
        assert disp == "X3D"
        assert exit_status == "success"
        assert authorized is True

    def test_falls_back_to_exit_status_when_disposition_missing(self) -> None:
        x3 = X3Disposition(
            request_id="req_2",
            run_id="run_2",
            app_id="apps_lic",
            trace_id="trace_2",
            exit_status="escalated",
            outcome_authorized=False,
            final_output={},
            l5_certification_ref=_EXIT_CERT_REF,
        )
        disp, exit_status, authorized = x3_manifest_fields(x3)
        assert disp == "escalated"
        assert exit_status == "escalated"
        assert authorized is False

    def test_unknown_only_when_both_missing(self) -> None:
        x3 = X3Disposition(
            request_id="req_3",
            run_id="run_3",
            app_id="apps_lic",
            trace_id="trace_3",
            exit_status="",
            outcome_authorized=False,
            final_output={},
            l5_certification_ref=_EXIT_CERT_REF,
        )
        disp, _, _ = x3_manifest_fields(x3)
        assert disp == "UNKNOWN"

    def test_spine_run_result_to_manifest_dict_includes_exit_fields(self) -> None:
        result = SpineRunResult(
            run_id="run_1",
            request_id="req_1",
            trace_id="trace_1",
            route_id="lic.outreach_message.r4_managed_draft",
            route_family="R4_MANAGED_DRAFT",
            execution_form="managed_workflow",
            x3_disposition="X3D",
            terminal_r5=False,
            terminal_r5_reason="",
            artifact_dir=Path("artifacts/apps_lic/spine_convergence/runs/run_1"),
            exit_status="success",
            outcome_authorized=True,
        )
        manifest = result.to_manifest_dict()
        assert manifest["x3_disposition"] == "X3D"
        assert manifest["exit_status"] == "success"
        assert manifest["outcome_authorized"] is True


class TestCanonicalSpineManifestX3Integration:
    def test_spine_manifest_matches_exit_not_unknown(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.setenv("APPS_LIC_TEST_PROVIDER_STUB", "1")
        raw = build_cli_ingress_raw(
            run_id="pytest_manifest_x3_01",
            request_id="req_pytest_manifest_x3_01",
            manual_brief="Enterprise renewal outreach for VP Technology at Acme Corp.",
        )
        result = run_canonical_apps_lic_spine(raw, artifact_root=tmp_path / "run")
        assert result.terminal_r5 is False
        assert result.x3_disposition != "UNKNOWN"
        assert result.exit_status == "success"
        assert result.outcome_authorized is True

        manifest_path = result.artifact_dir / "spine_run_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert manifest["x3_disposition"] == result.x3_disposition
        assert manifest["x3_disposition"] != "UNKNOWN"
        assert manifest["exit_status"] == "success"
        assert manifest["outcome_authorized"] is True
        assert manifest["x3_disposition"] == "X3D"

    def test_r4_managed_workflow_writes_per_stage_receipts(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.setenv("APPS_LIC_TEST_PROVIDER_STUB", "1")
        raw = build_cli_ingress_raw(
            run_id="pytest_stage_receipts_01",
            request_id="req_pytest_stage_receipts_01",
            manual_brief="Enterprise renewal outreach for VP Technology at Acme Corp.",
        )
        result = run_canonical_apps_lic_spine(raw, artifact_root=tmp_path / "run")
        assert result.route_family == "R4_MANAGED_DRAFT"
        assert result.terminal_r5 is False

        for filename in _R4_MANAGED_STAGE_FILES:
            assert (result.artifact_dir / filename).is_file(), f"missing {filename}"

        manifest = json.loads(
            (result.artifact_dir / sr.FILENAME_SPINE_MANIFEST).read_text(encoding="utf-8")
        )
        assert manifest["stage_receipt_refs"] == list(_R4_MANAGED_STAGE_FILES)

        u0 = json.loads((result.artifact_dir / sr.FILENAME_U0_RECEIPT).read_text(encoding="utf-8"))
        l1 = json.loads((result.artifact_dir / sr.FILENAME_L1_PLAN).read_text(encoding="utf-8"))
        route = json.loads((result.artifact_dir / sr.FILENAME_ROUTE_CONTRACT).read_text(encoding="utf-8"))
        c0 = json.loads((result.artifact_dir / sr.FILENAME_C0_FEC).read_text(encoding="utf-8"))
        pa = json.loads((result.artifact_dir / sr.FILENAME_PA_RECEIPT).read_text(encoding="utf-8"))
        l3 = json.loads((result.artifact_dir / sr.FILENAME_L3_WORKFLOW).read_text(encoding="utf-8"))
        l2 = json.loads((result.artifact_dir / sr.FILENAME_L2_EXECUTION).read_text(encoding="utf-8"))
        exit_rcpt = json.loads(
            (result.artifact_dir / sr.FILENAME_EXIT_DISPOSITION).read_text(encoding="utf-8")
        )

        _assert_stage_receipt(u0, stage="U0")
        _assert_stage_receipt(l1, stage="L1")
        _assert_stage_receipt(route, stage="L0")
        _assert_stage_receipt(c0, stage="C0")
        _assert_stage_receipt(pa, stage="PA")
        _assert_stage_receipt(l3, stage="L3")
        _assert_stage_receipt(l2, stage="L2")
        _assert_stage_receipt(exit_rcpt, stage="EXIT")

        assert sr.FILENAME_U0_RECEIPT in l1["upstream_receipt_refs"]
        assert sr.FILENAME_L1_PLAN in route["upstream_receipt_refs"]
        assert sr.FILENAME_ROUTE_CONTRACT in c0["upstream_receipt_refs"]
        assert sr.FILENAME_C0_FEC in pa["upstream_receipt_refs"]
        assert sr.FILENAME_PA_RECEIPT in l3["upstream_receipt_refs"]
        assert sr.FILENAME_L3_WORKFLOW in l2["upstream_receipt_refs"]
        assert sr.FILENAME_L2_EXECUTION in exit_rcpt["upstream_receipt_refs"]
        assert exit_rcpt["payload"]["x3_disposition"] == "X3D"
        assert exit_rcpt["payload"]["exit_status"] == "success"
        assert exit_rcpt["payload"]["outcome_authorized"] is True
