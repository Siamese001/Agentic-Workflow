"""W7 — apps_rg R1B ROLE_TARGET_RUN semantic cache persistence contract."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = REPO_ROOT / "artifacts" / "apps_rg" / "r1b_semantic_cache" / "w7_fixtures"
CACHE_PROFILE = REPO_ROOT / "apps_rg" / "config" / "domain_contract" / "cache_profiles.yaml"


def test_cache_profile_distinguishes_r1b_from_c0() -> None:
    data = yaml.safe_load(CACHE_PROFILE.read_text(encoding="utf-8"))
    preflight = data.get("section_cache_preflight") or {}
    assert preflight.get("c0_collection_excluded") == "fact_vectors"
    assert preflight.get("distinguish_semantic_cache_from_c0_fact_vectors") is True


def test_w7_fixtures_present() -> None:
    assert (FIXTURES / "historical_intent_record_admissible.json").is_file()
    assert (FIXTURES / "historical_output_chunks_admissible.json").is_file()
    assert (FIXTURES / "historical_intent_record_rejected_offline_stub.json").is_file()
    assert (FIXTURES / "historical_intent_record_rejected_not_proof_eligible.json").is_file()
    assert (FIXTURES / "compatibility_report_w7.json").is_file()


def test_admissible_fixture_cache_admissible() -> None:
    rec = json.loads((FIXTURES / "historical_intent_record_admissible.json").read_text(encoding="utf-8"))
    assert rec.get("cache_grain") == "ROLE_TARGET_RUN"
    assert rec.get("cache_admissible") is True
    assert rec.get("proof_eligible") is True


def test_rejected_fixtures_not_admissible() -> None:
    for name in ("rejected_offline_stub", "rejected_not_proof_eligible"):
        rec = json.loads((FIXTURES / f"historical_intent_record_{name}.json").read_text(encoding="utf-8"))
        assert rec.get("cache_admissible") is False


def test_output_chunks_parent_linked(tmp_path: Path) -> None:
    import json

    from apps_rg.cache.r1b_adapter import AppsRgR1BCacheAdapter
    from apps_rg.cache.r1b_constants import (
        CHUNK_TYPE_EXEC_SUMMARY,
        CHUNK_TYPE_FINAL_RESUME,
        CHUNK_TYPE_SECTION_PROOF,
    )

    artifact_dir = tmp_path / "exit"
    artifact_dir.mkdir()
    (artifact_dir / "x3_disposition.json").write_text(
        json.dumps(
            {
                "x3_code": "X3_ALLOW",
                "proof_eligible": True,
                "runtime_generation_status": "REAL_LLM",
            }
        ),
        encoding="utf-8",
    )
    (artifact_dir / "run_manifest.json").write_text("{}", encoding="utf-8")

    adapter = AppsRgR1BCacheAdapter(runs_dir=str(tmp_path))
    raw = {
        "target_company": "FixtureCo",
        "target_role": "Engineer",
        "generation_mode": "strategic_tailor",
        "resume_hash": "r1",
        "jd_hash": "j1",
        "brief_hash": "b1",
    }

    rid = adapter.store_intent_and_output(
        intent=raw,
        chunks=[
            {"chunk_type": CHUNK_TYPE_FINAL_RESUME, "chunk_text": "{}"},
            {
                "chunk_type": CHUNK_TYPE_EXEC_SUMMARY,
                "section_id": "executive_summary",
                "chunk_text": "x",
                "x2_status": "PASS",
            },
            {"chunk_type": CHUNK_TYPE_SECTION_PROOF, "section_id": "executive_summary", "chunk_text": "{}"},
        ],
        run_context={
            "record_id": "hir_contract",
            "post_exit_ingestion": True,
            "artifact_dir": str(artifact_dir),
            "x3_disposition": "X3_ALLOW",
            "proof_eligible": True,
            "runtime_generation_status": "REAL_LLM",
            "prompt_profile_hash": "p",
            "gate_profile_hash": "g",
        },
    )
    assert rid == "hir_contract"
    chunk_files = list((tmp_path / "chunks" / "hir_contract").glob("*.json"))
    assert len(chunk_files) >= 3
    for cf in chunk_files:
        ch = json.loads(cf.read_text(encoding="utf-8"))
        assert ch["parent_intent_record_id"] == "hir_contract"
        assert ch["independent_cache_identity"] is False
