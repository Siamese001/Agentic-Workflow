"""Truncated exec-summary JSON salvage (finish_reason=length)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.sections.executive_summary_lane import (
    parse_model_json,
    salvage_truncated_executive_summary_json,
)

_REPO = Path(__file__).resolve().parents[3]
_W2_RESP = (
    _REPO
    / "artifacts/apps_rg/runtime_proofs/executive_summary/real"
    / "exec_summary_20260526_084014"
    / "provider_response_judge_regen_cycle00_attempt00_judge_regen-00-00-b282622c.json"
)


@pytest.mark.skipif(not _W2_RESP.is_file(), reason="W2 artifact not on disk")
def test_salvage_w2_truncated_judge_regen_response() -> None:
    payload = json.loads(_W2_RESP.read_text(encoding="utf-8"))
    raw = str(payload.get("raw_model_output") or "")
    salvaged, err = salvage_truncated_executive_summary_json(raw)
    assert salvaged is not None, err
    assert "federated architecture" in str(salvaged.get("resume_display_text") or "")


def test_parse_model_json_salvages_truncated_self_check() -> None:
    truncated = (
        '{"executive_strategy_thesis":"Thesis.",'
        '"resume_display_text":"Six sentence paragraph.",'
        '"claim_ledger":[{"claim_text":"c","source_fact_ids":["fact_exec_002"]}],'
        '"jd_alignment":{"targeting_only":true,"jd_used_as_proof":false},'
        '"gap_notes":[],"change_log":[],"self_check":{"composition_th'
    )
    parsed, err = parse_model_json(truncated)
    assert parsed is not None, err
    assert parsed.get("resume_display_text") == "Six sentence paragraph."
