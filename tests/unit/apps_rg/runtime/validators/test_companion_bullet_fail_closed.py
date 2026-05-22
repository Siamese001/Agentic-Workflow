"""Fail-closed companion resolution — no stale global bullet fallback on product path."""

from __future__ import annotations

import json
import os

import pytest

from apps_rg.runtime.validators.companion_bullet_finalization import (
    ACCEPTED_FINALIZED_COMPANION_STATUS,
    build_companion_bullets_context,
    companion_blocks_narrative_llm,
)
from apps_rg.runtime.validators.unify_bullets_x2 import UNIFY_BULLET_IDS
from tests.unit.apps_rg.section_rigor.unify_ibm_lane_fixtures import REPO, unify_bullets_parsed_from_mock


def test_product_path_blocks_narrative_llm_without_finalized_companion(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("APPS_RG_TEST_HARNESS", raising=False)
    ctx = {"status": "NOT_FINALIZED", "reason": "product_quality_not_PASS:FAIL"}
    assert companion_blocks_narrative_llm(ctx) is True


def test_no_stale_global_fallback_when_modular_root_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("APPS_RG_TEST_HARNESS", raising=False)
    monkeypatch.delenv("APPS_RG_MODULAR_R4_SECTIONS_ROOT", raising=False)
    ctx = build_companion_bullets_context(
        REPO,
        upstream_section_id="unify_bullets",
        expected_bullet_ids=UNIFY_BULLET_IDS,
    )
    assert ctx["status"] == "MISSING"
    assert "no_modular_accepted_upstream" in str(ctx.get("reason") or "")


def test_modular_pointer_used_when_finalized(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("APPS_RG_TEST_HARNESS", raising=False)
    parsed, _ = unify_bullets_parsed_from_mock()
    sections_root = (
        REPO / "artifacts" / "apps_rg" / "runtime_proofs" / "contract_harness" / "_modular_companion_fail_closed"
    )
    sections_root.mkdir(parents=True, exist_ok=True)
    lane_base = sections_root / "unify_bullets"
    run_dir = lane_base / "real" / "unify_bullets_modular_test"
    run_dir.mkdir(parents=True, exist_ok=True)
    l2 = {
        "section_id": "unify_bullets",
        "product_quality_status": "PASS",
        "runtime_generation_status": "REAL_LLM",
        "bullets": parsed["bullets"],
    }
    (run_dir / "l2_output.json").write_text(json.dumps(l2), encoding="utf-8")
    (run_dir / "x3_disposition.json").write_text(
        json.dumps({"x3_code": "X3_ALLOW"}),
        encoding="utf-8",
    )
    rel = os.path.relpath(run_dir, REPO).replace("\\", "/")
    (lane_base / "latest_successful_real_run.json").write_text(
        json.dumps({"run_dir": rel}),
        encoding="utf-8",
    )
    monkeypatch.setenv("APPS_RG_MODULAR_R4_SECTIONS_ROOT", str(sections_root.resolve()))
    ctx = build_companion_bullets_context(
        REPO,
        upstream_section_id="unify_bullets",
        expected_bullet_ids=UNIFY_BULLET_IDS,
    )
    assert ctx["status"] == ACCEPTED_FINALIZED_COMPANION_STATUS
