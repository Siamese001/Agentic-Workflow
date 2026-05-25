"""P1 section repair ledger — counted regen and product pass blocking."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.section_repair_ledger import (
    KIND_DETERMINISTIC_REWRITE,
    KIND_MECHANICAL,
    KIND_REGEN_LLM,
    infer_product_quality_with_repair_ledger,
    init_ledger,
    ledger_blocks_product_pass,
    record_repair,
    record_x2_run,
    set_authoritative_attempt,
)
from apps_rg.runtime.section_repair_policy import (
    deterministic_rewrite_allowed,
    graph_only_reformat_allowed,
)


@pytest.fixture
def artifact_dir(tmp_path: Path) -> Path:
    d = tmp_path / "run"
    d.mkdir()
    return d


def _bootstrap_product_fail_closed(monkeypatch: pytest.MonkeyPatch, artifact_dir: Path) -> None:
    """Init ledger after env reflects product fail-closed (conftest sets TEST_HARNESS=1)."""
    monkeypatch.setenv("APPS_RG_WHOLE_RUN_ENVELOPE", "1")
    monkeypatch.delenv("APPS_RG_TEST_HARNESS", raising=False)
    init_ledger(artifact_dir, section_id="executive_summary", run_id="run-test")


def test_deterministic_rewrite_blocked_on_product_fail_closed(monkeypatch, artifact_dir: Path) -> None:
    _bootstrap_product_fail_closed(monkeypatch, artifact_dir)
    assert deterministic_rewrite_allowed() is False
    from apps_rg.runtime.sections.executive_summary_repair_policy import (
        RELEASE_GRAPH_ONLY_DETERMINISTIC_REFORMAT_ENABLED,
    )

    assert graph_only_reformat_allowed() is bool(RELEASE_GRAPH_ONLY_DETERMINISTIC_REFORMAT_ENABLED)


def test_ledger_blocks_pass_after_deterministic_rewrite_without_regen(
    monkeypatch, artifact_dir: Path
) -> None:
    _bootstrap_product_fail_closed(monkeypatch, artifact_dir)
    record_repair(
        artifact_dir,
        kind=KIND_DETERMINISTIC_REWRITE,
        operation="graph_only_display_authority_fallback",
        reason="shape_fail",
        replaced_l2=True,
    )
    record_x2_run(
        artifact_dir,
        run_number=1,
        after_l2_source="initial_llm",
        x2_gates=[{"gate_id": "g1", "pass": True}],
    )
    ledger = json.loads((artifact_dir / "section_repair_ledger.json").read_text(encoding="utf-8"))
    blocked, reason = ledger_blocks_product_pass(ledger)
    assert blocked is True
    assert "deterministic_rewrite" in reason
    status, pq_reason = infer_product_quality_with_repair_ledger(
        runtime_generation_status="REAL_LLM",
        x2_failed_gate_ids=[],
        pass_reason="ok",
        artifact_dir=artifact_dir,
    )
    assert status == "FAIL"
    assert "deterministic_rewrite" in pq_reason


def test_ledger_allows_graph_only_quality_repair_without_blocking_product_pass(
    monkeypatch, artifact_dir: Path
) -> None:
    _bootstrap_product_fail_closed(monkeypatch, artifact_dir)
    record_repair(
        artifact_dir,
        kind=KIND_DETERMINISTIC_REWRITE,
        operation="graph_only_generation_quality_repair",
        reason="synthesis_violations",
        replaced_l2=True,
    )
    ledger = json.loads((artifact_dir / "section_repair_ledger.json").read_text(encoding="utf-8"))
    blocked, reason = ledger_blocks_product_pass(ledger)
    assert blocked is False, reason


def test_ledger_allows_counted_regen_authoritative_attempt(
    monkeypatch, artifact_dir: Path
) -> None:
    _bootstrap_product_fail_closed(monkeypatch, artifact_dir)
    record_x2_run(
        artifact_dir,
        run_number=1,
        after_l2_source="initial_llm",
        x2_gates=[{"gate_id": "g1", "pass": False}],
    )
    record_repair(
        artifact_dir,
        kind=KIND_REGEN_LLM,
        operation="judge_remediation_regen",
        reason="judge_gap",
        replaced_l2=True,
    )
    set_authoritative_attempt(artifact_dir, 2, reason="regen_x2_pass")
    record_x2_run(
        artifact_dir,
        run_number=2,
        after_l2_source="regen_llm",
        x2_gates=[{"gate_id": "g1", "pass": True}],
    )
    ledger = json.loads((artifact_dir / "section_repair_ledger.json").read_text(encoding="utf-8"))
    blocked, _ = ledger_blocks_product_pass(ledger)
    assert blocked is False
    status, _ = infer_product_quality_with_repair_ledger(
        runtime_generation_status="REAL_LLM",
        x2_failed_gate_ids=[],
        pass_reason="ok",
        artifact_dir=artifact_dir,
    )
    assert status == "PASS"


def test_mechanical_only_after_attempt1_x2_fail_still_blocks_pass(
    monkeypatch, artifact_dir: Path
) -> None:
    _bootstrap_product_fail_closed(monkeypatch, artifact_dir)
    record_x2_run(
        artifact_dir,
        run_number=1,
        after_l2_source="initial_llm",
        x2_gates=[{"gate_id": "g1", "pass": False}],
    )
    record_repair(
        artifact_dir,
        kind=KIND_MECHANICAL,
        operation="strip_credential_dump_sentences",
        reason="removed_1",
        replaced_l2=False,
    )
    record_x2_run(
        artifact_dir,
        run_number=2,
        after_l2_source="initial_llm",
        x2_gates=[{"gate_id": "g1", "pass": True}],
    )
    ledger = json.loads((artifact_dir / "section_repair_ledger.json").read_text(encoding="utf-8"))
    blocked, reason = ledger_blocks_product_pass(ledger)
    assert blocked is True
    assert "attempt_1_x2_failed" in reason


def test_mechanical_finalize_coherence_does_not_block_product_pass(
    monkeypatch, artifact_dir: Path
) -> None:
    _bootstrap_product_fail_closed(monkeypatch, artifact_dir)
    record_repair(
        artifact_dir,
        kind=KIND_MECHANICAL,
        operation="executive_summary_finalize_coherence",
        reason="display_ledger_coherence",
        replaced_l2=False,
    )
    record_x2_run(
        artifact_dir,
        run_number=1,
        after_l2_source="initial_llm",
        x2_gates=[{"gate_id": "x2_claim_ledger_materialized_or_gap_excused", "pass": True}],
    )
    ledger = json.loads((artifact_dir / "section_repair_ledger.json").read_text(encoding="utf-8"))
    blocked, reason = ledger_blocks_product_pass(ledger)
    assert blocked is False
    assert reason == ""
    status, pq_reason = infer_product_quality_with_repair_ledger(
        runtime_generation_status="REAL_LLM",
        x2_failed_gate_ids=[],
        pass_reason="ok",
        artifact_dir=artifact_dir,
    )
    assert status == "PASS"
    assert pq_reason == "ok"


def test_regen_without_authoritative_bump_blocks_pass(monkeypatch, artifact_dir: Path) -> None:
    _bootstrap_product_fail_closed(monkeypatch, artifact_dir)
    record_repair(
        artifact_dir,
        kind=KIND_REGEN_LLM,
        operation="synthesis_regen",
        reason="shape",
        replaced_l2=True,
    )
    record_x2_run(
        artifact_dir,
        run_number=1,
        after_l2_source="initial_llm",
        x2_gates=[{"gate_id": "g1", "pass": True}],
    )
    ledger = json.loads((artifact_dir / "section_repair_ledger.json").read_text(encoding="utf-8"))
    blocked, reason = ledger_blocks_product_pass(ledger)
    assert blocked is True
    assert "authoritative_attempt_still_1" in reason


def test_regen_with_authoritative_bump_allows_product_pass(
    monkeypatch, artifact_dir: Path
) -> None:
    _bootstrap_product_fail_closed(monkeypatch, artifact_dir)
    record_repair(
        artifact_dir,
        kind=KIND_REGEN_LLM,
        operation="synthesis_regen",
        reason="shape",
        replaced_l2=True,
    )
    set_authoritative_attempt(artifact_dir, 2, reason="synthesis_regen_shape_pass")
    record_x2_run(
        artifact_dir,
        run_number=1,
        after_l2_source="regen_llm",
        x2_gates=[{"gate_id": "g1", "pass": True}],
    )
    ledger = json.loads((artifact_dir / "section_repair_ledger.json").read_text(encoding="utf-8"))
    blocked, reason = ledger_blocks_product_pass(ledger)
    assert blocked is False
    status, _ = infer_product_quality_with_repair_ledger(
        runtime_generation_status="REAL_LLM",
        x2_failed_gate_ids=[],
        pass_reason="ok",
        artifact_dir=artifact_dir,
    )
    assert status == "PASS"


def test_all_generated_lanes_have_repair_ledger_wiring() -> None:
    """Static guard: every generated lane must init section_repair_ledger."""
    repo = Path(__file__).resolve().parents[4]
    checks = {
        "headline": repo / "apps_rg/runtime/sections/headline_lane.py",
        "executive_summary": repo / "apps_rg/runtime/sections/executive_summary_lane.py",
        "competencies": repo / "apps_rg/runtime/sections/competencies_lane_execution.py",
        "unify_bullets": repo / "apps_rg/runtime/sections/unify_bullets_lane.py",
        "unify_narrative": repo / "apps_rg/runtime/sections/unify_narrative_lane.py",
        "ibm_bullets": repo / "apps_rg/runtime/sections/ibm_bullets_lane.py",
        "ibm_narrative": (
            repo / "apps_rg/runtime/sections/ibm_narrative_lane_execution.py",
            repo / "apps_rg/runtime/sections/ibm_narrative_lane_runtime.py",
        ),
    }
    for section_id, paths in checks.items():
        if isinstance(paths, Path):
            paths = (paths,)
        texts = [p.read_text(encoding="utf-8") for p in paths]
        combined = "\n".join(texts)
        assert "start_lane_repair_ledger" in combined or "init_ledger" in combined, section_id
        assert (
            "finalize_lane_product_quality" in combined
            or "infer_product_quality_with_repair_ledger" in combined
        ), section_id
