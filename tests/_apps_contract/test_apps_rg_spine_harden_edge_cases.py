"""Edge-case hardening — spine span coverage, L2 handoff, FEC preconditions, kill switches."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import pytest

from agentic_core.runtime.contracts.final_evidence_contract import (
    FinalEvidenceContract,
    SUPPORT_STATUS_PASS,
    SUPPORT_STATUS_WEAK,
)
from apps_rg.runtime.bindings.c0_binding import C0_GRAPH_LANE_NA_REF
from apps_rg.runtime.section_one_spine_no_two_path import inspect_no_two_path_lane
from apps_rg.runtime.spine.c0_fec_compose import (
    FEC_BRIDGE_MODE_SECTION,
    SectionFecBridgePreconditionError,
    assert_section_pa_fec_preconditions,
)
from apps_rg.runtime.spine.c0_graph_lane_receipt import (
    C0_GRAPH_LANE_RECEIPT_ARTIFACT,
    build_c0_graph_lane_receipt_from_bridge,
)
from apps_rg.runtime.spine.front_contracts import (
    activate_fixture_dev_bypass,
    build_section_front_spine_from_args,
    deactivate_fixture_dev_bypass,
    emit_section_front_spine_receipts,
)
from apps_rg.runtime.spine.governed_l6_shadow_compose import (
    governed_l6_shadow_enabled,
)
from apps_rg.runtime.spine.l2_handoff_receipt import build_section_l2_handoff_receipt
from apps_rg.runtime.spine.l6_eval_before_learn_receipt import build_l6_eval_before_learn_receipt
from apps_rg.runtime.spine.section_c0_retrieve import (
    STOP_AS_EVIDENCE_GAP,
    StopAsEvidenceGapError,
    assert_no_stop_as_evidence_gap,
    write_spine_c0_retrieve_receipt,
)
from apps_rg.runtime.spine.spine_span_emit import (
    REQUIRED_PRODUCT_SPINE_LAYERS,
    SPINE_SPAN_COVERAGE_RECEIPT,
    SPINE_SPAN_RECEIPT,
    emit_spine_span_coverage_receipt,
    emit_spine_span_event,
    read_spine_span_layer_keys,
    spine_span_emit_enabled,
    validate_spine_span_coverage,
)

REPO = Path(__file__).resolve().parents[2]


def _args() -> SimpleNamespace:
    return SimpleNamespace(
        target_company="Acme Corp",
        target_title="VP Engineering",
        target_role="VP Engineering",
        jd_text="Lead platform engineering.",
        briefing="Edge case harness.",
        base_resume_ref="",
    )


def test_validate_spine_span_coverage_reports_missing_layers() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        ad = Path(tmp)
        emit_spine_span_event(ad, layer_key="PA", binding_seam="test")
        report = validate_spine_span_coverage(ad, product_visible=True)
        assert report["complete"] is False
        assert "U0" in report["missing_layers"]
        assert set(REQUIRED_PRODUCT_SPINE_LAYERS) - set(report["observed_layers"]) == set(
            report["missing_layers"]
        )


def test_coverage_receipt_written_when_emit_enabled() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        ad = Path(tmp)
        for layer in REQUIRED_PRODUCT_SPINE_LAYERS:
            emit_spine_span_event(ad, layer_key=layer, binding_seam="test")
        path = emit_spine_span_coverage_receipt(ad, product_visible=True)
        assert path is not None
        assert (ad / SPINE_SPAN_COVERAGE_RECEIPT).is_file()
        doc = json.loads((ad / SPINE_SPAN_COVERAGE_RECEIPT).read_text(encoding="utf-8"))
        assert doc["complete"] is True


def test_span_emit_kill_switch_skips_receipt_and_coverage_complete() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        ad = Path(tmp)
        old = os.environ.get("APPS_RG_SPINE_SPAN_EMIT")
        os.environ["APPS_RG_SPINE_SPAN_EMIT"] = "0"
        try:
            assert spine_span_emit_enabled() is False
            assert emit_spine_span_event(ad, layer_key="U0", binding_seam="test") is None
            report = validate_spine_span_coverage(ad, product_visible=True)
            assert report["skipped"] is True
            assert report["complete"] is True
        finally:
            if old is None:
                os.environ.pop("APPS_RG_SPINE_SPAN_EMIT", None)
            else:
                os.environ["APPS_RG_SPINE_SPAN_EMIT"] = old


def test_l2_handoff_fails_without_pa_hmac() -> None:
    receipt = build_section_l2_handoff_receipt(
        {"product_visible": True, "compiled_prompt_artifact_summary": {}},
        section_id="headline",
    )
    assert receipt["handoff_status"] == "FAIL"
    assert receipt["validation"]["valid"] is False


def test_product_visible_pa_rejects_raw_proof_pool_direct(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("APPS_RG_TEST_HARNESS", raising=False)
    monkeypatch.setenv("APPS_RG_SECTION_FEC_BRIDGE_KILL_SWITCH", "1")
    monkeypatch.setattr(
        "apps_rg.runtime.spine.c0_fec_compose.fixture_dev_bypass_active",
        lambda: False,
    )
    monkeypatch.setattr(
        "apps_rg.runtime.c0.product_runtime_guards.product_fec_bridge_mandatory",
        lambda: True,
    )
    with pytest.raises(SectionFecBridgePreconditionError, match="raw_proof_pool_direct_to_pa"):
        assert_section_pa_fec_preconditions(
            {
                "product_visible": True,
                "section_fec_bridge": {
                    "fec_bridge_mode": "section_fec_bridge",
                    "route_contract_ref": "route_contract.json",
                },
                "raw_proof_pool_direct_to_pa": True,
            }
        )


def test_front_spine_emit_writes_u0_l1_l0_span_layers() -> None:
    activate_fixture_dev_bypass()
    try:
        with tempfile.TemporaryDirectory() as tmp:
            ad = Path(tmp)
            front = build_section_front_spine_from_args(
                section_id="headline",
                args=_args(),
                repo_root=REPO,
            )
            emit_section_front_spine_receipts(ad, front)
            layers = set(read_spine_span_layer_keys(ad))
            assert {"U0", "L1", "L0"}.issubset(layers)
            assert (ad / SPINE_SPAN_RECEIPT).is_file()
    finally:
        deactivate_fixture_dev_bypass()


def test_no_two_path_detects_raw_proof_pool_flag_in_compiled_artifact(tmp_path: Path) -> None:
    (tmp_path / "compiled_prompt_artifact.json").write_text(
        json.dumps({"raw_proof_pool_direct_to_pa": True}) + "\n",
        encoding="utf-8",
    )
    (tmp_path / "exit_disposition_receipt.json").write_text("{}\n", encoding="utf-8")
    ntp = inspect_no_two_path_lane(tmp_path)
    assert ntp["checks"]["raw_proof_pool_direct_to_pa"] is True
    assert ntp["no_two_path_preconditions_pass"] is False


def test_no_two_path_requires_exit_disposition_authority(tmp_path: Path) -> None:
    (tmp_path / "compiled_prompt_artifact.json").write_text(
        json.dumps({"raw_proof_pool_direct_to_pa": False}) + "\n",
        encoding="utf-8",
    )
    ntp = inspect_no_two_path_lane(tmp_path)
    assert ntp["checks"]["exit_refs_sealed_l2"] is False
    assert ntp["checks"]["exhaust_refs_exit_disposition"] is False
    assert ntp["no_two_path_preconditions_pass"] is False


# --- Span emit edge cases ---


def test_emit_spine_span_event_none_artifact_dir_returns_none() -> None:
    assert emit_spine_span_event(None, layer_key="U0", binding_seam="test") is None


def test_emit_spine_span_non_product_visible_skipped_without_force(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("APPS_RG_SPINE_SPAN_EMIT", raising=False)
    with tempfile.TemporaryDirectory() as tmp:
        ad = Path(tmp)
        assert emit_spine_span_event(ad, layer_key="U0", binding_seam="test", product_visible=False) is None
        assert not (ad / SPINE_SPAN_RECEIPT).exists()


def test_emit_spine_span_force_on_with_env_even_non_product(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APPS_RG_SPINE_SPAN_EMIT", "1")
    with tempfile.TemporaryDirectory() as tmp:
        ad = Path(tmp)
        path = emit_spine_span_event(ad, layer_key="U0", binding_seam="test", product_visible=False)
        assert path is not None


def test_span_jsonl_appends_duplicate_layer_keys() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        ad = Path(tmp)
        emit_spine_span_event(ad, layer_key="PA", binding_seam="a")
        emit_spine_span_event(ad, layer_key="PA", binding_seam="b")
        keys = read_spine_span_layer_keys(ad)
        assert keys.count("PA") == 2


def test_validate_spine_span_coverage_custom_required_subset() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        ad = Path(tmp)
        emit_spine_span_event(ad, layer_key="PA", binding_seam="test")
        report = validate_spine_span_coverage(ad, required_layers=("PA",), product_visible=True)
        assert report["complete"] is True
        assert report["missing_layers"] == []


def test_otel_dual_write_failure_classification(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_SPINE_OTEL_SDK", "1")
    monkeypatch.setenv("APPS_RG_SPINE_SPAN_EMIT", "1")
    with tempfile.TemporaryDirectory() as tmp:
        ad = Path(tmp)
        with mock.patch(
            "apps_rg.runtime.spine.spine_span_emit._try_otel_span",
            return_value=False,
        ):
            emit_spine_span_event(ad, layer_key="L2", binding_seam="test")
        line = json.loads((ad / SPINE_SPAN_RECEIPT).read_text(encoding="utf-8").strip())
        assert line["otel_dual_write_attempted"] is True
        assert line["otel_dual_write_ok"] is False
        assert line["proof_classification"] == "receipt_fallback_otel_unavailable"


# --- FEC / PA precondition edge cases ---


def _product_fec_mandatory(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("APPS_RG_TEST_HARNESS", raising=False)
    monkeypatch.setenv("APPS_RG_SECTION_FEC_BRIDGE_KILL_SWITCH", "1")
    monkeypatch.setattr(
        "apps_rg.runtime.spine.c0_fec_compose.fixture_dev_bypass_active",
        lambda: False,
    )
    monkeypatch.setattr(
        "apps_rg.runtime.c0.product_runtime_guards.product_fec_bridge_mandatory",
        lambda: True,
    )


def test_product_visible_pa_requires_fec_bridge(monkeypatch: pytest.MonkeyPatch) -> None:
    _product_fec_mandatory(monkeypatch)
    with pytest.raises(SectionFecBridgePreconditionError, match="section_fec_bridge"):
        assert_section_pa_fec_preconditions({"product_visible": True})


def test_product_visible_pa_rejects_unsupported_fec_bridge_mode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _product_fec_mandatory(monkeypatch)
    with pytest.raises(SectionFecBridgePreconditionError, match="unsupported fec_bridge_mode"):
        assert_section_pa_fec_preconditions(
            {
                "product_visible": True,
                "section_fec_bridge": {
                    "fec_bridge_mode": "legacy_bypass_mode",
                    "route_contract_ref": "route_contract.json",
                },
            }
        )


def test_product_visible_pa_requires_route_contract_ref(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _product_fec_mandatory(monkeypatch)
    with pytest.raises(SectionFecBridgePreconditionError, match="route_contract_ref"):
        assert_section_pa_fec_preconditions(
            {
                "product_visible": True,
                "section_fec_bridge": {"fec_bridge_mode": FEC_BRIDGE_MODE_SECTION},
            }
        )


def test_fixture_dev_bypass_skips_fec_preconditions(monkeypatch: pytest.MonkeyPatch) -> None:
    _product_fec_mandatory(monkeypatch)
    monkeypatch.setattr(
        "apps_rg.runtime.spine.c0_fec_compose.fixture_dev_bypass_active",
        lambda: True,
    )
    assert_section_pa_fec_preconditions(
        {"product_visible": True, "raw_proof_pool_direct_to_pa": True}
    )


# --- L2 handoff edge cases ---


def test_l2_handoff_passes_via_governed_pa_receipt_hmac() -> None:
    receipt = build_section_l2_handoff_receipt(
        {
            "product_visible": True,
            "governed_pa_receipt": {
                "core_assemble_prompt_invoked": True,
                "pa_hmac": "b" * 64,
            },
            "trace_root": "trace-1",
        },
        section_id="headline",
    )
    assert receipt["handoff_status"] == "PASS"


def test_l2_handoff_fails_grounding_without_trace_root() -> None:
    receipt = build_section_l2_handoff_receipt(
        {
            "product_visible": True,
            "compiled_prompt_artifact_summary": {"signature": "c" * 64},
            "grounding_required": True,
        },
        section_id="headline",
    )
    assert receipt["handoff_status"] == "FAIL"


# --- C0 evidence gap + graph lane edge cases ---


def _minimal_fec(**overrides: object) -> FinalEvidenceContract:
    base = dict(
        request_id="req-edge",
        run_id="run-edge",
        app_id="apps_rg",
        trace_id="trace-edge",
        l5_certification_ref="test:valid",
        support_status=SUPPORT_STATUS_PASS,
        support_target_met=True,
        final_evidence_digest="d" * 64,
        evidence_items=(),
    )
    base.update(overrides)
    return FinalEvidenceContract(**base)


def test_stop_as_evidence_gap_on_weak_fec_when_grounded() -> None:
    fec = _minimal_fec(support_status=SUPPORT_STATUS_WEAK, support_target_met=False)
    with pytest.raises(StopAsEvidenceGapError, match=STOP_AS_EVIDENCE_GAP) as exc:
        assert_no_stop_as_evidence_gap(grounding_required=True, fec=fec, section_id="headline")
    assert exc.value.support_status == SUPPORT_STATUS_WEAK


def test_stop_as_evidence_gap_skipped_when_grounding_not_required() -> None:
    fec = _minimal_fec(support_status=SUPPORT_STATUS_WEAK, support_target_met=False)
    assert_no_stop_as_evidence_gap(grounding_required=False, fec=fec)


def test_graph_lane_receipt_from_bridge_skills_bound_still_not_c0_3() -> None:
    skills_ref = "ref:graph:skills:v1"
    bridge = {
        "section_id": "headline",
        "graph_lane_na_ref": skills_ref,
        "graph_expansion_refs": [skills_ref],
        "proof_pool_metadata": {
            "c03_graphrag_bound": {
                "support_status": "SUPPORTED",
                "graph_lineage_refs": [skills_ref],
            },
        },
    }
    receipt = build_c0_graph_lane_receipt_from_bridge(bridge)
    assert receipt["skills_graph_bound"] is True
    assert receipt["canonical_c0_3_graph_rag_claimed"] is False
    assert receipt["graph_lane_deferred"] is False
    assert skills_ref in receipt["graph_expansion_refs"]


def test_write_spine_c0_retrieve_receipt_also_emits_graph_lane_receipt() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        ad = Path(tmp)
        spine_receipt = {
            "section_id": "headline",
            "graph_lane_na_ref": C0_GRAPH_LANE_NA_REF,
            "graph_expansion_refs": [C0_GRAPH_LANE_NA_REF],
            "graph_lane_deferred": True,
        }
        write_spine_c0_retrieve_receipt(ad, spine_receipt)
        assert (ad / "section_spine_c0_retrieve_receipt.json").is_file()
        assert (ad / C0_GRAPH_LANE_RECEIPT_ARTIFACT).is_file()
        graph_doc = json.loads((ad / C0_GRAPH_LANE_RECEIPT_ARTIFACT).read_text(encoding="utf-8"))
        assert graph_doc["graph_lane_deferred"] is True


# --- No-two-path partial chain edge cases ---


def test_no_two_path_fails_without_front_spine_contracts(tmp_path: Path) -> None:
    ntp = inspect_no_two_path_lane(tmp_path)
    assert ntp["checks"]["proof_pool_after_front_spine"] is False
    assert ntp["no_two_path_preconditions_pass"] is False


def test_no_two_path_partial_front_spine_without_fec(tmp_path: Path) -> None:
    for name in ("validated_request.json", "l1_plan_contract.json", "route_contract.json"):
        (tmp_path / name).write_text("{}\n", encoding="utf-8")
    ntp = inspect_no_two_path_lane(tmp_path)
    assert ntp["checks"]["proof_pool_after_front_spine"] is False


# --- L6 / governed shadow edge cases ---


def test_governed_l6_shadow_skip_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_GOVERNED_L6_SHADOW_SKIP", "1")
    assert governed_l6_shadow_enabled() is False


def test_l6_eval_receipt_defaults_block_promotion() -> None:
    receipt = build_l6_eval_before_learn_receipt(section_id="headline", run_id="r1")
    assert receipt["promotion_allowed"] is False
    assert receipt["eval_before_learn_satisfied"] is False
    assert receipt["gauntlet_satisfied"] is False


# --- Live smoke harness guard ---


def test_live_smoke_blocked_when_test_harness_set() -> None:
    live_smoke = REPO / "ops_scripts" / "apps_rg" / "live_section_spine_smoke_all_lanes.py"
    with tempfile.TemporaryDirectory() as chroma_tmp:
        env = dict(os.environ)
        env["CHROMA_PERSIST_DIR"] = chroma_tmp
        env["APPS_RG_TEST_HARNESS"] = "1"
        env.pop("APPS_RG_LIVE_SMOKE_DRY_RUN", None)
        completed = subprocess.run(
            [sys.executable, str(live_smoke)],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
            env=env,
        )
    assert completed.returncode == 2
    doc = json.loads(completed.stdout)
    assert doc["status"] == "BLOCKED"
    assert "APPS_RG_TEST_HARNESS" in doc["reason"]
