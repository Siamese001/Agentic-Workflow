"""W8.1 — same-run c02_chroma_write must not satisfy product PASS without pre-run index receipt."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.c02_chroma_lifecycle import (
    C02_CHROMA_WRITE_ATTEMPTED,
    C02_CHROMA_WRITE_SKIPPED,
    build_c02_chroma_write_receipt,
    same_run_write_blocks_product_pass,
)
from apps_rg.runtime.product_output_policy import (
    lane_run_dir_meets_product_bar,
    product_fail_closed_runtime,
    product_pass_allows_c02_write,
)


def test_product_fail_closed_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("APPS_RG_TEST_HARNESS", raising=False)
    monkeypatch.delenv("APPS_RG_ALLOW_PRODUCT_SHORTCUTS", raising=False)
    monkeypatch.delenv("APPS_RG_WHOLE_RUN_ENVELOPE", raising=False)
    assert product_fail_closed_runtime() is True


def test_shortcuts_opt_out(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("APPS_RG_TEST_HARNESS", raising=False)
    monkeypatch.setenv("APPS_RG_ALLOW_PRODUCT_SHORTCUTS", "1")
    assert product_fail_closed_runtime() is False


def test_same_run_write_blocks_product_pass_without_index_receipt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("APPS_RG_TEST_HARNESS", raising=False)
    monkeypatch.delenv("APPS_RG_ALLOW_PRODUCT_SHORTCUTS", raising=False)
    write = {
        "status": C02_CHROMA_WRITE_ATTEMPTED,
        "attempted": True,
        "upserted_count": 3,
    }
    assert same_run_write_blocks_product_pass(write) is True
    ok, reason = product_pass_allows_c02_write(write, index_maintenance_bound=False)
    assert ok is False
    assert "same_run" in reason


def test_same_run_write_allowed_with_index_build_receipt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("APPS_RG_TEST_HARNESS", raising=False)
    monkeypatch.delenv("APPS_RG_ALLOW_PRODUCT_SHORTCUTS", raising=False)
    write = {"status": C02_CHROMA_WRITE_ATTEMPTED, "attempted": True}
    ok, _ = product_pass_allows_c02_write(write, index_maintenance_bound=True)
    assert ok is True


def test_product_skip_write_receipt_shape(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("APPS_RG_TEST_HARNESS", raising=False)
    monkeypatch.delenv("APPS_RG_ALLOW_PRODUCT_SHORTCUTS", raising=False)
    wr = build_c02_chroma_write_receipt(None)
    assert wr["status"] == C02_CHROMA_WRITE_SKIPPED
    assert wr["bge_embed_for_write"] is False


def test_lane_bar_rejects_same_run_ingest_pass_without_index_receipt(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.delenv("APPS_RG_TEST_HARNESS", raising=False)
    monkeypatch.delenv("APPS_RG_ALLOW_PRODUCT_SHORTCUTS", raising=False)
    run_dir = tmp_path / "lane"
    run_dir.mkdir()
    room = {
        "bridge_doc": {
            "c0_evidence_room": {
                "c02": {
                    "c02_chroma_write": {
                        "status": C02_CHROMA_WRITE_ATTEMPTED,
                        "attempted": True,
                    },
                    "fact_vectors_ingest": {"status": "PASS", "upserted_count": 2},
                }
            }
        }
    }
    (run_dir / "c0_evidence_room_receipt.json").write_text(
        json.dumps(room), encoding="utf-8"
    )
    (run_dir / "l2_output.json").write_text(
        json.dumps(
            {
                "runtime_generation_status": "REAL_LLM",
                "product_quality_status": "PASS",
                "provider_requested": "retired_provider_profile",
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "provider_request.json").write_text(
        json.dumps({"provider": "retired_provider_profile"}), encoding="utf-8"
    )
    (run_dir / "x3_disposition.json").write_text(
        json.dumps({"x3_code": "X3_ALLOW"}), encoding="utf-8"
    )
    ok, reason = lane_run_dir_meets_product_bar(run_dir)
    assert ok is False
    assert "same_run" in reason
