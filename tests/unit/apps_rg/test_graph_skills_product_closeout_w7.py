"""W7: graph-skills product proof closeout in package disposition."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.internal.resume_package_disposition import (
    evaluate_resume_package,
    summarize_graph_skills_product_closeout,
)
from tests._apps_contract.test_resume_package_x3 import _write_minimal_fixture_tree


def _graph_gate(verdict: str = "PASS", *, warnings: list[dict] | None = None) -> dict:
    status = "PASS" if verdict == "PASS" else "WARN"
    return {
        "gate_id": "x2_cross_section_graph_coherence",
        "verdict": verdict,
        "pass": verdict == "PASS",
        "observed": {
            "schema": "apps_rg.cross_section_graph_coherence_receipt.v1",
            "status": status,
            "active_section_count": 4,
            "native_c03_section_count": 2,
            "role_episode_section_count": 2,
            "unique_graph_skill_node_count": 6,
            "unique_source_fact_id_count": 8,
            "unique_role_episode_bundle_count": 3,
            "active_section_ids": [
                "executive_summary",
                "competencies",
                "unify_bullets",
                "ibm_bullets",
            ],
            "native_c03_section_ids": ["executive_summary", "competencies"],
            "role_episode_section_ids": ["unify_bullets", "ibm_bullets"],
            "warnings": warnings or [],
        },
    }


def _evaluate_with_cross_section(tmp_path: Path, cross_section_x2: dict) -> dict:
    paths = _write_minimal_fixture_tree(tmp_path)
    rollup = json.loads(paths.rollup_json.read_text(encoding="utf-8"))
    return evaluate_resume_package(
        paths=paths,
        rollup=rollup,
        locked_x2=json.loads(paths.locked_copy_x2_json.read_text(encoding="utf-8")),
        final_manifest=json.loads(paths.final_resume_manifest_json.read_text(encoding="utf-8")),
        final_x2=json.loads(paths.final_resume_x2_json.read_text(encoding="utf-8")),
        docx_manifest=json.loads(paths.docx_manifest_json.read_text(encoding="utf-8")),
        docx_manifest_x2=json.loads(paths.docx_manifest_x2_json.read_text(encoding="utf-8")),
        docx_render_manifest=json.loads(paths.docx_render_manifest_json.read_text(encoding="utf-8")),
        docx_render_x2=json.loads(paths.docx_render_x2_json.read_text(encoding="utf-8")),
        cross_section_x2=cross_section_x2,
    )


@pytest.fixture(autouse=True)
def _package_fixture_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_TEST_HARNESS", "1")
    monkeypatch.setenv("APPS_RG_SECTION_RUNTIME_EXHAUST_KILL_SWITCH", "0")
    monkeypatch.delenv("APPS_RG_WHOLE_RUN_ENVELOPE", raising=False)
    monkeypatch.delenv("APPS_RG_CORRELATED_CLI_RUN", raising=False)


def test_graph_skills_closeout_ready_from_cross_section_gate() -> None:
    summary = summarize_graph_skills_product_closeout(
        {"gates": [_graph_gate("PASS")], "all_pass": True}
    )

    assert summary["product_proof_closeout_status"] == "READY"
    assert summary["ready_for_product_proof_support"] is True
    assert summary["active_section_count"] == 4
    assert summary["does_not_upgrade_package_x3"] is True


def test_graph_skills_closeout_warn_does_not_claim_ready() -> None:
    summary = summarize_graph_skills_product_closeout(
        {
            "gates": [
                _graph_gate(
                    "WARN",
                    warnings=[{"reason_code": "graph_metadata_breadth_below_floor"}],
                )
            ]
        }
    )

    assert summary["product_proof_closeout_status"] == "ADVISORY_WARN"
    assert summary["ready_for_product_proof_support"] is False
    assert summary["warning_reason_codes"] == ["graph_metadata_breadth_below_floor"]


def test_evaluate_resume_package_embeds_graph_skills_closeout(tmp_path: Path) -> None:
    dsp = _evaluate_with_cross_section(
        tmp_path,
        {"gates": [_graph_gate("PASS")], "warn_policy": {"product_allow_blocked_by_cross_section": False}},
    )

    closeout = dsp["aggregation_product_proof"]["graph_skills_closeout"]
    assert closeout["product_proof_closeout_status"] == "READY"
    assert closeout["ready_for_product_proof_support"] is True
    assert dsp["graph_skills_product_proof_closeout"] == closeout
    assert dsp["proof_eligible"] is False


def test_evaluate_resume_package_missing_graph_gate_is_explicit(tmp_path: Path) -> None:
    dsp = _evaluate_with_cross_section(tmp_path, {"gates": []})

    closeout = dsp["aggregation_product_proof"]["graph_skills_closeout"]
    assert closeout["product_proof_closeout_status"] == "MISSING"
    assert closeout["cross_section_graph_gate_present"] is False
    assert closeout["ready_for_product_proof_support"] is False
