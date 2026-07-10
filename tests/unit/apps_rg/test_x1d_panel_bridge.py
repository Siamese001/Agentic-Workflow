"""W2: apps_rg grade-only path delegates to core JudgePanelRunner."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.judges.executive_summary_judge_packet import (
    judge_packet_hash,
    render_judge_prompt_from_packet,
)
from apps_rg.runtime.judges.executive_summary_x1d import run_llm_judges
from apps_rg.runtime.judges.x1d_panel_bridge import (
    build_core_contract_from_packet,
    emit_judge_attempt_ledger,
)
from apps_rg.runtime.judges.x1d_panel_harness import (
    JudgeAttemptReceipt,
    PanelRunResult,
)
from apps_rg.runtime.sections.executive_summary_x1d_judge_contract import (
    build_brown_brown_six_sentence_packet,
)


def test_build_core_contract_matches_packet_hash() -> None:
    packet = build_brown_brown_six_sentence_packet()
    prompt = render_judge_prompt_from_packet(packet)
    expected = judge_packet_hash(packet)
    contract = build_core_contract_from_packet(packet, prompt, canonical_hash=expected)
    assert contract.contract_hash() == expected


def test_run_llm_judges_grade_only_dispatches_to_panel_bridge(monkeypatch: pytest.MonkeyPatch) -> None:
    called: list[dict] = []

    def _fake_grade_only(**kwargs):
        called.append(kwargs)
        return []

    monkeypatch.setattr(
        "apps_rg.runtime.judges.x1d_panel_bridge.run_grade_only_judges_via_core_panel",
        _fake_grade_only,
    )

    packet = build_brown_brown_six_sentence_packet()
    run_llm_judges(
        resume_display_text=packet["candidate_output"]["resume_display_text"],
        claim_ledger=packet["candidate_output"]["claim_ledger"],
        judge_keys=["gemini_pro"],
        judge_packet=packet,
    )
    assert len(called) == 1
    assert called[0]["judge_packet"] is packet


def test_emit_judge_attempt_ledger_preserves_every_retry(tmp_path: Path) -> None:
    result = PanelRunResult(
        contract_hash="contract-1",
        outcomes=(),
        transport_violations=(),
        attempts=(
            JudgeAttemptReceipt(
                provider_key="anthropic_claude",
                contract_hash="contract-1",
                attempt=1,
                max_attempts=2,
                status="RETRYABLE_FAILURE",
                error="parse error",
            ),
            JudgeAttemptReceipt(
                provider_key="anthropic_claude",
                contract_hash="contract-1",
                attempt=2,
                max_attempts=2,
                status="PASS",
                receipt_attempt=2,
            ),
        ),
    )

    path = emit_judge_attempt_ledger(
        artifact_base=tmp_path,
        section_id="executive_summary",
        panel_result=result,
    )
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["schema_version"] == "apps_rg.judge_attempt_ledger.v1"
    assert payload["attempt_count"] == 2
    assert payload["retry_count"] == 1
    assert payload["attempts"][0]["error"] == "parse error"
    assert payload["attempts"][1]["attempt"] == 2
