from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from apps_rg.runtime.sections import role_episode_lane
from apps_rg.runtime.validators.bullet_line_discipline_x2 import check_bullet_single_thought


def _bullet_l2(section_id: str, text: str) -> dict[str, Any]:
    source_id = f"fact_{section_id}"
    prefix = "bul_insurtech" if section_id.startswith("insurtech") else "bul_ey"
    bullets = [
        {
            "bullet_id": f"{prefix}_{idx:03d}",
            "bullet_text": text if idx == 1 else f"Delivered governed platform outcome for lane {idx}.",
            "source_fact_ids": [source_id],
        }
        for idx in range(1, 4)
    ]
    return {
        "section_id": section_id,
        "bullets": bullets,
        "claim_ledger": [
            {"claim_text": b["bullet_text"], "source_fact_ids": b["source_fact_ids"]}
            for b in bullets
        ],
    }


def _narrative_l2(section_id: str, text: str) -> dict[str, Any]:
    source_id = f"fact_{section_id}"
    return {
        "section_id": section_id,
        "narrative_sentence": text,
        "claim_ledger": [{"claim_text": text, "source_fact_ids": [source_id]}],
    }


def _gate_by_id(gates: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(g["gate_id"]): g for g in gates}


@pytest.mark.parametrize(
    "text",
    [
        "Delivered 99.99% uptime across U.S. regulated platforms.",
        "Scaled e.g. policy-governed delivery across Acme Inc. platforms.",
    ],
)
def test_shared_bullet_single_thought_accepts_decimals_and_abbreviations(text: str) -> None:
    ok, count, reason = check_bullet_single_thought(text)
    assert ok is True
    assert count == 1
    assert reason is None


def test_shared_bullet_single_thought_rejects_two_sentences() -> None:
    ok, count, reason = check_bullet_single_thought("Delivered platform controls. Expanded adoption.")
    assert ok is False
    assert count == 2
    assert reason


@pytest.mark.parametrize(
    ("section_id", "runner"),
    [
        ("insurtech_bullets", role_episode_lane.run_insurtech_bullets_x2_gates),
        ("ey_bullets", role_episode_lane.run_ey_bullets_x2_gates),
    ],
)
def test_role_episode_bullet_single_thought_accepts_decimal_metrics(
    section_id: str,
    runner,
) -> None:
    gates = runner(
        l2=_bullet_l2(section_id, "Delivered 99.99% uptime across U.S. regulated platforms."),
        allowed=[f"fact_{section_id}"],
        runtime_generation_status="REAL_LLM",
    )

    assert _gate_by_id(gates)[f"x2_{section_id}_bullet_single_thought"]["pass"] is True


@pytest.mark.parametrize(
    ("section_id", "runner"),
    [
        ("insurtech_narrative", role_episode_lane.run_insurtech_narrative_x2_gates),
        ("ey_narrative", role_episode_lane.run_ey_narrative_x2_gates),
    ],
)
def test_role_episode_narrative_exactly_one_sentence_accepts_decimal_metrics(
    section_id: str,
    runner,
) -> None:
    text = "Delivered 99.99% uptime across U.S. regulated platforms."
    gates = runner(
        l2=_narrative_l2(section_id, text),
        allowed=[f"fact_{section_id}"],
        runtime_generation_status="REAL_LLM",
    )

    gate = _gate_by_id(gates)[f"x2_{section_id}_exactly_one_sentence"]
    assert gate["pass"] is True
    assert gate["observed_value"]["sentence_count"] == 1


def test_role_episode_narrative_exactly_one_sentence_rejects_two_sentences() -> None:
    section_id = "ey_narrative"
    gates = role_episode_lane.run_ey_narrative_x2_gates(
        l2=_narrative_l2(section_id, "Delivered platform controls. Expanded adoption."),
        allowed=[f"fact_{section_id}"],
        runtime_generation_status="REAL_LLM",
    )

    gate = _gate_by_id(gates)[f"x2_{section_id}_exactly_one_sentence"]
    assert gate["pass"] is False
    assert gate["observed_value"]["sentence_count"] == 2


def test_scoped_runtime_sentence_gates_do_not_use_raw_period_counts() -> None:
    scoped_files = [
        Path(role_episode_lane.__file__),
        Path("apps_rg/runtime/validators/unify_narrative_x2.py"),
        Path("apps_rg/runtime/validators/ibm_narrative_x2.py"),
        Path("apps_rg/runtime/validators/narrative_mechanical_x2.py"),
    ]
    offenders: list[str] = []
    for path in scoped_files:
        text = path.read_text(encoding="utf-8")
        if 'count(".") + ' in text or "count('.') + " in text:
            offenders.append(path.as_posix())

    assert offenders == []
