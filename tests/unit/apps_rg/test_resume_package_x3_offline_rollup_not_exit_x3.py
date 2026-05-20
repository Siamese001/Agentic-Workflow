"""SP-003: package rollup X3 is not Exit/spine/product X3."""
from __future__ import annotations

import json

import pytest

from apps_rg.runtime.non_product_proof_stamp import (
    PACKAGE_DISPOSITION_CLASSIFICATION,
    guard_reject_non_product_for_certification,
    package_rollup_non_product_stamp,
)
from apps_rg.runtime.internal.resume_package_disposition import X3_ALLOW_CODE, evaluate_resume_package
from tests._apps_contract.test_resume_package_x3 import (
    _mk_x2,
    _write_minimal_fixture_tree,
)


def test_package_stamp_when_allow() -> None:
    stamp = package_rollup_non_product_stamp(package_x3_allow=True)
    assert stamp["package_disposition_classification"] == PACKAGE_DISPOSITION_CLASSIFICATION
    assert stamp["package_x3_allow"] is True
    assert stamp["exit_x3_disposition"] == "NOT_CLAIMED"
    assert stamp["spine_x3_allow"] is False
    assert stamp["product_x3_allow"] is False
    assert stamp["eligible_for_l7_certification"] is False
    assert stamp["proof_eligible"] is False


def test_guard_rejects_package_disposition_for_l7_cert() -> None:
    payload = package_rollup_non_product_stamp(package_x3_allow=True)
    payload["disposition_family"] = "resume_package_x3"
    with pytest.raises(ValueError, match="non-product proof"):
        guard_reject_non_product_for_certification(payload, context="test_gate")


def test_evaluate_resume_package_includes_offline_classification(tmp_path) -> None:
    paths = _write_minimal_fixture_tree(tmp_path)
    rollup = json.loads(paths.rollup_json.read_text(encoding="utf-8"))
    dsp = evaluate_resume_package(
        paths=paths,
        rollup=rollup,
        locked_x2=json.loads(paths.locked_copy_x2_json.read_text(encoding="utf-8")),
        final_manifest=json.loads(paths.final_resume_manifest_json.read_text(encoding="utf-8")),
        final_x2=json.loads(paths.final_resume_x2_json.read_text(encoding="utf-8")),
        docx_manifest=json.loads(paths.docx_manifest_json.read_text(encoding="utf-8")),
        docx_manifest_x2=json.loads(paths.docx_manifest_x2_json.read_text(encoding="utf-8")),
        docx_render_manifest=json.loads(paths.docx_render_manifest_json.read_text(encoding="utf-8")),
        docx_render_x2=json.loads(paths.docx_render_x2_json.read_text(encoding="utf-8")),
    )
    assert dsp["package_disposition_classification"] == PACKAGE_DISPOSITION_CLASSIFICATION
    assert dsp.get("package_x3_allow") == (dsp["final_x3_code"] == X3_ALLOW_CODE)
    assert dsp["exit_x3_disposition"] == "NOT_CLAIMED"
    assert dsp["aggregation_product_proof"]["product_allow_claimed"] is False
