"""disposition_authority labeling on lane X3 and section Exit receipts."""

from __future__ import annotations

import json
from pathlib import Path

from apps_rg.runtime.disposition_authority import (
    DISPOSITION_AUTHORITY_LANE,
    apply_lane_x3_authority_fields,
)
from apps_rg.runtime.exit.executive_summary_x3 import aggregate_x3
from apps_rg.runtime.section_exit_spine_receipt import (
    EXIT_DISPOSITION_RECEIPT_ARTIFACT,
    build_exit_disposition_receipt_for_section,
    build_exit_review_packet_for_section,
)


def test_lane_x3_to_dict_carries_disposition_authority_lane() -> None:
    x3 = aggregate_x3(
        resume_display_text="x" * 80,
        claim_ledger=[],
        x2_gates=[{"gate_id": "g1", "pass": True}],
        x1d_judges=[],
        runtime_generation_status="REAL_LLM",
        product_quality_status="PASS",
        judge_required_for_allow=False,
    )
    doc = x3.to_dict()
    assert doc["disposition_authority"] == DISPOSITION_AUTHORITY_LANE
    assert doc["section_x3_mirror_only"] is True
    assert doc["spine_x3_claimed"] is False


def test_exit_disposition_receipt_labels_lane_authority_not_spine(tmp_path: Path) -> None:
    art = tmp_path / "lane_run"
    art.mkdir()
    (art / "x3_disposition.json").write_text(
        json.dumps(
            apply_lane_x3_authority_fields(
                {"x3_code": "X3_ALLOW", "decisive_reason": "ok"}
            )
        ),
        encoding="utf-8",
    )
    (art / "sealed_l2_artifact.json").write_text("{}", encoding="utf-8")
    (art / "l2_execution_packet.json").write_text("{}", encoding="utf-8")
    receipt = build_exit_disposition_receipt_for_section(
        section_id="executive_summary",
        runtime_payload={"run_id": "r1", "sealed_l2_artifact_ref": "sealed_l2_artifact.json"},
        artifact_dir=art,
    )
    assert receipt["disposition_authority"] == DISPOSITION_AUTHORITY_LANE
    assert receipt["section_x3_mirror_only"] is True
    assert receipt["spine_x3_claimed"] is False
    assert receipt["canonical_exit_authority"] == "exit_disposition_receipt"


def test_exit_review_packet_marks_section_x3_non_authoritative(tmp_path: Path) -> None:
    art = tmp_path / "lane_run2"
    art.mkdir()
    (art / "x3_disposition.json").write_text('{"x3_code":"X3_REVIEW"}', encoding="utf-8")
    (art / "sealed_l2_artifact.json").write_text("{}", encoding="utf-8")
    pkt = build_exit_review_packet_for_section(
        section_id="headline",
        runtime_payload={"sealed_l2_artifact_ref": "sealed_l2_artifact.json"},
        artifact_dir=art,
    )
    assert pkt["section_x3_authoritative"] is False
    assert pkt["disposition_authority"] == DISPOSITION_AUTHORITY_LANE
    assert pkt["spine_x3_claimed"] is False


def test_apply_lane_x3_authority_fields_idempotent() -> None:
    base = {"x3_code": "X3_ALLOW"}
    once = apply_lane_x3_authority_fields(base)
    twice = apply_lane_x3_authority_fields(once)
    assert twice["disposition_authority"] == DISPOSITION_AUTHORITY_LANE
    assert base["x3_code"] == "X3_ALLOW"
