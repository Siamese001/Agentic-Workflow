"""Unit tests for section-lane C0 metrics emit, consume, and X2 gates."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentic_core.runtime.contracts.final_evidence_contract import SUPPORT_STATUS_PASS
from apps_rg.runtime.bindings.c0_metrics_writer import SCHEMA_VERSION
from apps_rg.runtime.bindings.section_lane_c0_metrics import (
    C0_METRICS_FILENAME,
    augment_section_x2_gates,
    build_section_c0_metrics_x2_gates,
    emit_section_lane_c0_metrics,
    fec_from_section_bridge,
    load_section_lane_c0_metrics,
    materialize_section_lane_c0_metrics,
    merge_c0_metrics_into_section_metric_receipt,
    resolve_section_lane_c0_metrics,
    validate_c0_metrics_document,
)
from apps_rg.runtime.sections.section_x2_gate_outputs import write_section_x2_gate_outputs
from apps_rg.runtime.section_fec_bridge import FEC_BRIDGE_MODE_SECTION


def _minimal_bridge_doc() -> dict:
    return {
        "fec_bridge_mode": FEC_BRIDGE_MODE_SECTION,
        "support_status": SUPPORT_STATUS_PASS,
        "proof_source": "proof_pool",
        "allowed_fact_ids": ["fact_a", "fact_b"],
        "evidence_items": [
            {
                "evidence_id": "evidence:section:fact_a",
                "source_fact_id": "fact_a",
                "source_class": "candidate_fact_ledger",
            },
        ],
        "final_evidence_contract_snapshot": {
            "support_status": SUPPORT_STATUS_PASS,
            "evidence_item_count": 1,
        },
    }


def test_fec_from_section_bridge_builds_items() -> None:
    fec = fec_from_section_bridge(_minimal_bridge_doc(), run_id="run_test")
    assert len(fec.evidence_items) >= 1
    assert fec.support_status == SUPPORT_STATUS_PASS


def test_fec_from_section_bridge_normalizes_supported_label() -> None:
    doc = _minimal_bridge_doc()
    doc["support_status"] = "SUPPORTED"
    fec = fec_from_section_bridge(doc, run_id="run_test")
    assert fec.support_status == SUPPORT_STATUS_PASS


def test_emit_and_load_c0_metrics_roundtrip(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "headline_run"
    artifact_dir.mkdir()
    runtime_payload: dict = {
        "run_id": "headline_test_001",
        "section_fec_bridge": _minimal_bridge_doc(),
    }

    class _Spine:
        validated_request = {"manual_brief": "brief text"}

    metrics = emit_section_lane_c0_metrics(
        artifact_dir,
        section_id="headline",
        runtime_payload=runtime_payload,
        front_spine=_Spine(),  # type: ignore[arg-type]
    )
    assert metrics is not None
    assert (artifact_dir / C0_METRICS_FILENAME).is_file()
    loaded = load_section_lane_c0_metrics(artifact_dir)
    assert loaded is not None
    assert loaded["schema_version"] == SCHEMA_VERSION
    assert runtime_payload["c0_metrics_ref"] == C0_METRICS_FILENAME
    assert "support_status" in runtime_payload


def test_merge_c0_metrics_into_section_metric_receipt() -> None:
    receipt: dict = {}
    payload = {
        "c0_metrics_ref": "c0_metrics.json",
        "support_status": "PASS",
        "support_target_met": True,
    }
    merge_c0_metrics_into_section_metric_receipt(receipt, payload)
    assert receipt["c0_metrics_ref"] == "c0_metrics.json"
    assert receipt["support_status"] == "PASS"
    assert receipt["support_target_met"] is True


def test_x2_gates_require_metrics_for_grounded_lane(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "lane"
    artifact_dir.mkdir()
    gates = augment_section_x2_gates([], artifact_dir, "headline")
    gate_ids = {g["gate_id"] for g in gates}
    assert "x2_c0_metrics_artifact_present" in gate_ids
    assert "x2_c0_support_status_gate" in gate_ids
    assert all(not g["pass"] for g in gates)

    (artifact_dir / C0_METRICS_FILENAME).write_text(
        json.dumps(
            {
                "schema_version": SCHEMA_VERSION,
                "run_id": "r1",
                "route_id": "R0",
                "retrieval_mode": "NONE",
                "briefing_source_type": "NONE",
                "company_brief_provenance": None,
                "source_class_coverage": {},
                "support_status": "PASS",
                "support_target_met": True,
                "evidence_counts": {"total": 1, "excluded": 0, "blocked": 0},
                "retrieval_sources": ["proof_pool"],
                "excluded_evidence_refs": [],
                "blocked_source_refs": [],
                "freshness_receipts": [],
                "citation_map": [],
                "support_score_profile": {},
                "final_evidence_digest": "abc123",
            }
        ),
        encoding="utf-8",
    )
    ok_gates = build_section_c0_metrics_x2_gates(
        load_section_lane_c0_metrics(artifact_dir),
        section_id="headline",
    )
    assert all(g["pass"] for g in ok_gates)


def test_validate_c0_metrics_document_rejects_missing_keys() -> None:
    ok, reason = validate_c0_metrics_document({"schema_version": SCHEMA_VERSION})
    assert not ok
    assert "missing keys" in reason


def test_resolve_metrics_materializes_from_runtime_payload(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "lane"
    artifact_dir.mkdir()
    metrics = {
        "schema_version": SCHEMA_VERSION,
        "run_id": "r1",
        "route_id": "R0",
        "retrieval_mode": "NONE",
        "briefing_source_type": "NONE",
        "company_brief_provenance": None,
        "source_class_coverage": {},
        "support_status": "PASS",
        "support_target_met": True,
        "evidence_counts": {"total": 1, "excluded": 0, "blocked": 0},
        "retrieval_sources": ["proof_pool"],
        "excluded_evidence_refs": [],
        "blocked_source_refs": [],
        "freshness_receipts": [],
        "citation_map": [],
        "support_score_profile": {},
        "final_evidence_digest": "abc",
    }
    payload = {"c0_metrics": metrics}
    resolved = resolve_section_lane_c0_metrics(artifact_dir, payload)
    assert resolved is not None
    assert (artifact_dir / C0_METRICS_FILENAME).is_file()


def test_write_section_x2_gate_outputs_appends_c0_gates(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "headline_run"
    artifact_dir.mkdir()
    metrics = {
        "schema_version": SCHEMA_VERSION,
        "run_id": "r1",
        "route_id": "R0",
        "retrieval_mode": "NONE",
        "briefing_source_type": "NONE",
        "company_brief_provenance": None,
        "source_class_coverage": {},
        "support_status": "PASS",
        "support_target_met": True,
        "evidence_counts": {"total": 2, "excluded": 0, "blocked": 0},
        "retrieval_sources": ["proof_pool"],
        "excluded_evidence_refs": [],
        "blocked_source_refs": [],
        "freshness_receipts": [],
        "citation_map": [],
        "support_score_profile": {},
        "final_evidence_digest": "deadbeef",
    }
    materialize_section_lane_c0_metrics(artifact_dir, metrics)
    write_section_x2_gate_outputs(
        artifact_dir,
        "headline",
        [{"gate_id": "x2_json_parse_valid", "pass": True}],
    )
    doc = json.loads((artifact_dir / "x2_gate_outputs.json").read_text(encoding="utf-8"))
    gate_ids = {g["gate_id"] for g in doc["gates"]}
    assert "x2_c0_metrics_artifact_present" in gate_ids
    assert "x2_c0_support_status_gate" in gate_ids


def test_support_status_gate_fails_on_empty_status(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "lane"
    artifact_dir.mkdir()
    (artifact_dir / C0_METRICS_FILENAME).write_text(
        json.dumps(
            {
                "schema_version": SCHEMA_VERSION,
                "run_id": "r",
                "route_id": "R0",
                "retrieval_mode": "NONE",
                "briefing_source_type": "NONE",
                "company_brief_provenance": None,
                "source_class_coverage": {},
                "support_status": "EMPTY",
                "support_target_met": False,
                "evidence_counts": {"total": 0, "excluded": 0, "blocked": 0},
                "retrieval_sources": [],
                "excluded_evidence_refs": [],
                "blocked_source_refs": [],
                "freshness_receipts": [],
                "citation_map": [],
                "support_score_profile": {},
                "final_evidence_digest": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            }
        ),
        encoding="utf-8",
    )
    gates = build_section_c0_metrics_x2_gates(
        load_section_lane_c0_metrics(artifact_dir),
        section_id="headline",
    )
    support_gate = next(g for g in gates if g["gate_id"] == "x2_c0_support_status_gate")
    assert support_gate["pass"] is False
