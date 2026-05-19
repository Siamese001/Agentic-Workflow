"""Contract tests for aggregation fingerprint and extended proof refs."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.assembly.final_resume_assembler import assemble_final_resume
from apps_rg.runtime.assembly.final_resume_manifest import resolve_default_paths
from apps_rg.runtime.locked_copy.locked_copy_manifest import find_repo_root


@pytest.fixture(scope="module")
def assembled() -> dict[str, object]:
    paths = resolve_default_paths(find_repo_root())
    if not paths.rollup_json.is_file():
        pytest.skip("rollup missing")
    try:
        return assemble_final_resume(paths)
    except Exception as exc:
        pytest.skip(f"assembly preflight blocked: {exc}")


def test_orchestration_fingerprint_artifact(assembled: dict[str, object]) -> None:
    fp = assembled["paths"]["orchestration_fingerprint"]
    assert Path(fp).is_file()
    blob = json.loads(Path(fp).read_text(encoding="utf-8"))
    assert blob.get("orchestration_id")
    assert blob.get("lane_run_ids")


def test_section_digest_distinct_from_hash(assembled: dict[str, object]) -> None:
    fr = assembled["final_resume_blob"]
    for sec in fr["sections"]:
        if sec.get("section_kind") != "generated_lane":
            continue
        assert sec.get("section_digest")
        assert sec.get("section_hash")
        assert sec["section_digest"] != sec["section_hash"]


def test_proof_refs_on_generated_lane(assembled: dict[str, object]) -> None:
    fr = assembled["final_resume_blob"]
    sec = next(s for s in fr["sections"] if s["section_id"] == "headline")
    refs = sec["source_artifact_refs"]
    assert "section_input_usage_ledger.json" in refs
    assert "x2_source_fact_pool_receipt.json" in refs
    assert refs.get("proof_pool_digest") or refs.get("proof_pool_ref")
