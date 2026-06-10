"""W3.0 — headline format repair: max one LLM regen replacing L2 before X2."""

from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.runtime.section_repair_ledger import KIND_REGEN_LLM, init_ledger, record_repair
from tests.unit.apps_rg.section_rigor.repair_authority import assert_single_repair_authority_path


def test_headline_single_format_regen_passes(tmp_path: Path) -> None:
    adir = tmp_path / "headline"
    adir.mkdir()
    init_ledger(adir, section_id="headline", run_id="fmt1")
    record_repair(
        adir,
        kind=KIND_REGEN_LLM,
        operation="headline_format_repair",
        reason="word_count=14 or pipe_format invalid",
        replaced_l2=True,
    )
    from apps_rg.runtime.section_repair_ledger import load_ledger, set_authoritative_attempt

    set_authoritative_attempt(adir, 2, reason="single_format_regen")
    ok, reason = assert_single_repair_authority_path(load_ledger(adir))
    assert ok, reason


def test_headline_double_format_regen_red_path(tmp_path: Path) -> None:
    adir = tmp_path / "headline2"
    adir.mkdir()
    init_ledger(adir, section_id="headline", run_id="fmt2")
    record_repair(adir, kind=KIND_REGEN_LLM, operation="headline_format_repair", replaced_l2=True)
    record_repair(adir, kind=KIND_REGEN_LLM, operation="headline_proof_shape_retry", replaced_l2=True)
    from apps_rg.runtime.section_repair_ledger import load_ledger

    ok, reason = assert_single_repair_authority_path(load_ledger(adir))
    assert not ok


def test_headline_single_content_signal_regen_passes(tmp_path: Path) -> None:
    adir = tmp_path / "headline_cs"
    adir.mkdir()
    init_ledger(adir, section_id="headline", run_id="cs1")
    record_repair(
        adir,
        kind=KIND_REGEN_LLM,
        operation="headline_content_signal_repair",
        reason="x2_headline_governance_or_regulated_ai_signal_required:none",
        replaced_l2=True,
    )
    from apps_rg.runtime.section_repair_ledger import load_ledger, set_authoritative_attempt

    set_authoritative_attempt(adir, 2, reason="headline_content_signal_repair_x2_pass")
    ok, reason = assert_single_repair_authority_path(load_ledger(adir))
    assert ok, reason


def test_headline_content_signal_regen_after_format_regen_red_path(tmp_path: Path) -> None:
    adir = tmp_path / "headline_cs2"
    adir.mkdir()
    init_ledger(adir, section_id="headline", run_id="cs2")
    record_repair(adir, kind=KIND_REGEN_LLM, operation="headline_format_repair", replaced_l2=True)
    record_repair(
        adir,
        kind=KIND_REGEN_LLM,
        operation="headline_content_signal_repair",
        replaced_l2=True,
    )
    from apps_rg.runtime.section_repair_ledger import load_ledger

    ok, reason = assert_single_repair_authority_path(load_ledger(adir))
    assert not ok
