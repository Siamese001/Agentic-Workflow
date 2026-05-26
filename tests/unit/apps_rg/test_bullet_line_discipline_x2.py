"""W2.1 — bullet line-discipline X2 (shared split_sentences)."""

from __future__ import annotations

from apps_rg.runtime.validators.bullet_line_discipline_x2 import (
    check_bullet_single_thought,
    check_ibm_narrative_slot_reservation,
)
from apps_rg.runtime.validators.executive_summary_sentence_utils import split_sentences
from apps_rg.runtime.validators.ibm_bullets_x2 import run_ibm_bullets_x2_gates
from apps_rg.runtime.validators.unify_bullets_x2 import UNIFY_BULLET_IDS, run_unify_bullets_x2_gates


def _fake_judges() -> list[dict]:
    return [{"evaluator_mode": "MOCK", "pass": True}]


def _unify_bullets_ok() -> list[dict]:
    bullets = [
        {"bullet_id": bid, "bullet_text": f"Delivered governed platform outcome for {bid}.", "source_fact_ids": [bid]}
        for bid in UNIFY_BULLET_IDS
    ]
    if bullets[5]["bullet_id"] == "bul_unify_006":
        bullets[5]["bullet_text"] = (
            "Generated $22M revenue with 20% margin while scaling team from 8 to 28 "
            "and compressing cycle from six months to three weeks."
        )
    ledger = [{"claim_text": b["bullet_text"], "source_fact_ids": b["source_fact_ids"]} for b in bullets]
    return bullets, ledger


def test_split_sentences_respects_abbreviations() -> None:
    text = "Led U.S. expansion for Dr. Smith at Acme Inc. e.g. regulated delivery."
    assert len(split_sentences(text)) == 1


def test_multi_sentence_bullet_fails_single_thought() -> None:
    text = "First sentence here. Second sentence here."
    ok, count, reason = check_bullet_single_thought(text)
    assert not ok
    assert count == 2
    assert reason


def test_unify_x2_multi_sentence_bullet_gate_fails() -> None:
    bullets, ledger = _unify_bullets_ok()
    bullets[0]["bullet_text"] = "First thought. Second thought."
    parsed = {"bullets": bullets, "claim_ledger": ledger}
    gates = run_unify_bullets_x2_gates(
        bullets=bullets,
        parsed_output=parsed,
        claim_ledger=ledger,
        allowed_fact_ids=set(UNIFY_BULLET_IDS),
        jd_text="",
        runtime_generation_status="MOCKED",
        x1d_judges=_fake_judges(),
    )
    by_id = {g.gate_id: g for g in gates}
    assert by_id["x2_unify_bullet_single_thought"].pass_ is False


def test_unify_x2_embedded_newline_gate_fails() -> None:
    bullets, ledger = _unify_bullets_ok()
    bullets[1]["bullet_text"] = "Line one\nLine two"
    parsed = {"bullets": bullets, "claim_ledger": ledger}
    gates = run_unify_bullets_x2_gates(
        bullets=bullets,
        parsed_output=parsed,
        claim_ledger=ledger,
        allowed_fact_ids=set(UNIFY_BULLET_IDS),
        jd_text="",
        runtime_generation_status="MOCKED",
        x1d_judges=_fake_judges(),
    )
    by_id = {g.gate_id: g for g in gates}
    assert by_id["x2_unify_bullet_no_embedded_newline"].pass_ is False


def test_ibm_narrative_slot_reservation_heuristic() -> None:
    ok, hits, _ = check_ibm_narrative_slot_reservation(
        "This role positioned the candidate as a capstone leader in summary."
    )
    assert not ok
    assert hits


def test_ibm_x2_narrative_slot_gate_registered() -> None:
    bullets = [
        {"bullet_id": f"bul_ibm_00{i}", "bullet_text": f"IBM outcome {i}.", "source_fact_ids": [f"bul_ibm_00{i}"]}
        for i in range(1, 6)
    ]
    bullets[0]["bullet_text"] = "This role positioned the leader as a capstone narrative."
    ledger = [{"claim_text": b["bullet_text"], "source_fact_ids": b["source_fact_ids"]} for b in bullets]
    parsed = {"bullets": bullets, "claim_ledger": ledger}
    gates = run_ibm_bullets_x2_gates(
        bullets=bullets,
        parsed_output=parsed,
        claim_ledger=ledger,
        allowed_fact_ids={b["bullet_id"] for b in bullets},
        jd_text="",
        runtime_generation_status="MOCKED",
        x1d_judges=_fake_judges(),
    )
    by_id = {g.gate_id: g for g in gates}
    assert "x2_ibm_narrative_slot_reservation" in by_id
    assert by_id["x2_ibm_narrative_slot_reservation"].pass_ is False
