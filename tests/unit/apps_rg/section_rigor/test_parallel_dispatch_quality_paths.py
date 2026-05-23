"""W1.1 — at most one LLM repair authority path before X2 (repair ledger)."""

from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.runtime.section_repair_ledger import (
    KIND_MECHANICAL,
    KIND_REGEN_LLM,
    init_ledger,
    record_repair,
    record_x2_run,
)
from tests.unit.apps_rg.section_rigor.repair_authority import (
    assert_single_repair_authority_path,
    count_regen_llm_replaced,
    mechanical_repairs_same_authority,
)

_LANES = ("headline", "executive_summary", "competencies")


@pytest.mark.parametrize("lane", _LANES)
def test_single_regen_llm_passes(lane: str, tmp_path: Path) -> None:
    adir = tmp_path / lane
    adir.mkdir()
    init_ledger(adir, section_id=lane, run_id=f"test_{lane}")
    record_repair(
        adir,
        kind=KIND_REGEN_LLM,
        operation="format_repair",
        reason="shape",
        replaced_l2=True,
        detail={"section_id": lane},
    )
    from apps_rg.runtime.section_repair_ledger import load_ledger, set_authoritative_attempt

    set_authoritative_attempt(adir, 2, reason="single_regen_test")
    record_x2_run(adir, run_number=1, after_l2_source=KIND_REGEN_LLM, x2_gates=[{"gate_id": "x2_json_parse_valid", "pass": True}])

    ledger = load_ledger(adir)
    ok, reason = assert_single_repair_authority_path(ledger)
    assert ok, reason
    assert count_regen_llm_replaced(list(ledger.get("repairs") or [])) == 1


def test_double_regen_llm_red_path(tmp_path: Path) -> None:
    adir = tmp_path / "double_regen"
    adir.mkdir()
    init_ledger(adir, section_id="headline", run_id="red_path")
    record_repair(adir, kind=KIND_REGEN_LLM, operation="repair_a", replaced_l2=True)
    record_repair(adir, kind=KIND_REGEN_LLM, operation="repair_b", replaced_l2=True)
    from apps_rg.runtime.section_repair_ledger import load_ledger

    ledger = load_ledger(adir)
    ok, reason = assert_single_repair_authority_path(ledger)
    assert not ok
    assert "multiple_regen" in reason


def test_mechanical_only_no_regen_passes(tmp_path: Path) -> None:
    adir = tmp_path / "mech"
    adir.mkdir()
    init_ledger(adir, section_id="competencies", run_id="mech_only")
    record_repair(adir, kind=KIND_MECHANICAL, operation="fact_id_typo_repair", replaced_l2=False)
    from apps_rg.runtime.section_repair_ledger import load_ledger

    ledger = load_ledger(adir)
    assert mechanical_repairs_same_authority(list(ledger.get("repairs") or []))
    ok, _ = assert_single_repair_authority_path(ledger)
    assert ok


def test_ordered_repair_ledger_records_authority_path(tmp_path: Path) -> None:
    adir = tmp_path / "ordered"
    adir.mkdir()
    init_ledger(adir, section_id="executive_summary", run_id="ordered")
    record_repair(adir, kind=KIND_MECHANICAL, operation="normalize_claim_ledger", replaced_l2=False)
    record_repair(adir, kind=KIND_REGEN_LLM, operation="synthesis_regen", replaced_l2=True)
    from apps_rg.runtime.section_repair_ledger import load_ledger

    ledger = load_ledger(adir)
    repairs = list(ledger.get("repairs") or [])
    assert [r.get("seq") for r in repairs] == [1, 2]
    assert repairs[-1].get("kind") == KIND_REGEN_LLM
