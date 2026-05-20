"""W6A — semantic cache shadow Chroma write quarantine in section evidence package."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.semantic_cache_persistence_quarantine import (
    CHROMA_CLASS_NON_DURABLE,
    CULPRIT_CALL_CHAIN,
    NO_DIRECT_CHROMA_ASSERTION_ARTIFACT,
    PROMOTE_TO_LONG_TERM_CALLERS,
    assess_uwg_durable_write_chain,
    build_semantic_cache_persistence_slots,
    classify_shadow_chroma_write_path,
    finalize_semantic_cache_quarantine,
)
from apps_rg.runtime.section_evidence_package import (
    EVIDENCE_PACKAGE_INDEX_ARTIFACT,
    finalize_section_evidence_package,
)
from apps_rg.runtime.section_l7_binding_manifest import build_section_l7_binding_manifest


def test_shadow_chroma_classified_non_durable_without_uwg_chain(tmp_path: Path) -> None:
    uwg = assess_uwg_durable_write_chain(
        repo_root=tmp_path,
        artifact_dir=tmp_path / "run",
        integrated_dir=None,
    )
    assert uwg["durable_proof_chain_complete"] is False
    assert classify_shadow_chroma_write_path(uwg_assessment=uwg) == CHROMA_CLASS_NON_DURABLE


def test_culprit_path_includes_execution_orchestrator() -> None:
    chain = " ".join(CULPRIT_CALL_CHAIN)
    assert "execution_orchestrator" in chain
    assert "gptcache_client" in chain
    callers = {c["caller"] for c in PROMOTE_TO_LONG_TERM_CALLERS}
    assert "agentic_core/L0_routing/reasoning/execution_orchestrator.py" in callers


def test_semantic_cache_slots_all_explicit(tmp_path: Path) -> None:
    ad = tmp_path / "run"
    ad.mkdir()
    bundle = finalize_semantic_cache_quarantine(
        repo_root=tmp_path,
        artifact_dir=ad,
        section_id="executive_summary",
        run_id="w6a_slots",
        integrated_dir=None,
    )
    slots = bundle["semantic_cache_persistence_slots"]["slots"]
    assert "commit_request" in slots
    assert "read_surface_refresh_receipt" in slots
    assert "no_direct_chroma_write_bypass_assertion" in slots
    assert slots["commit_request"]["status"] == "MISSING"
    assert slots["request_intent_embedding_ref"]["status"] == "MISSING"
    assert "mapping" in slots["request_intent_embedding_ref"]["notes"].lower()
    assert slots["cache_embedding_ref"]["status"] == "MISSING"
    assert bundle["semantic_cache_persistence_slots"]["vector_persistence_claimed"] is False
    assert bundle["semantic_cache_persistence_slots"]["chroma_persistence_claimed"] is False


def test_index_refresh_not_canonical_read_surface_without_bridge(tmp_path: Path) -> None:
    ad = tmp_path / "run"
    ad.mkdir()
    derived = tmp_path / "artifacts/apps_rg/r1b_semantic_cache/derived_index"
    derived.mkdir(parents=True)
    (derived / "manifest.json").write_text("{}\n", encoding="utf-8")
    slots_doc = build_semantic_cache_persistence_slots(
        repo_root=tmp_path,
        artifact_dir=ad,
        integrated_dir=None,
        uwg_assessment=assess_uwg_durable_write_chain(
            repo_root=tmp_path, artifact_dir=ad, integrated_dir=None
        ),
        assertion_path="artifacts/run/no_direct_chroma_write_bypass_assertion.json",
    )
    refresh = slots_doc["slots"]["read_surface_refresh_receipt"]
    assert refresh["status"] == "DRIFT"
    assert "IndexRefreshReceipt" in refresh["notes"] or refresh.get("artifact_name") == "IndexRefreshReceipt"


def test_finalize_emits_no_direct_chroma_assertion_and_package_slots(tmp_path: Path) -> None:
    ad = tmp_path / "run"
    ad.mkdir()
    (ad / "x3_disposition.json").write_text(
        json.dumps({"x3_code": "X3_BLOCK", "proof_eligible": False}),
        encoding="utf-8",
    )
    (ad / "run_manifest.json").write_text(
        json.dumps({"run_id": "w6a", "section_id": "executive_summary"}),
        encoding="utf-8",
    )
    (ad / "RUN_BUNDLE_INDEX.json").write_text(
        json.dumps({"schema_version": "1", "run_id": "w6a", "entries": []}),
        encoding="utf-8",
    )
    binding = build_section_l7_binding_manifest(
        repo_root=tmp_path,
        artifact_dir=ad,
        section_id="executive_summary",
        run_id="w6a",
    )
    finalize_section_evidence_package(
        repo_root=tmp_path,
        artifact_dir=ad,
        section_id="executive_summary",
        run_id="w6a",
        binding_manifest=binding,
    )
    assert (ad / NO_DIRECT_CHROMA_ASSERTION_ARTIFACT).is_file()
    pkg = json.loads((ad / EVIDENCE_PACKAGE_INDEX_ARTIFACT).read_text(encoding="utf-8"))
    assert pkg["chroma_semantic_cache_classification"] == CHROMA_CLASS_NON_DURABLE
    assert pkg["semantic_cache_persistence_status"] in ("NOT_PROVEN", "NOT_APPLICABLE")
    assert pkg["commit_request_status"] == "NOT_EMITTED"
    assert pkg["durable_semantic_cache_proof_present"] is False
    assert "semantic_cache_persistence_slots" in pkg
    assert pkg["semantic_cache_persistence_slots"]["commit_request"]["status"] == "MISSING"
    assertion = json.loads((ad / NO_DIRECT_CHROMA_ASSERTION_ARTIFACT).read_text(encoding="utf-8"))
    assert assertion["durable_persistence_claim_allowed"] is False
    assert assertion["chroma_semantic_cache_classification"] == CHROMA_CLASS_NON_DURABLE


def test_uwg_chain_partial_does_not_prove_chroma_durable(tmp_path: Path) -> None:
    ad = tmp_path / "run"
    ad.mkdir()
    (ad / "commit_request.json").write_text(
        json.dumps(
            {
                "payload": {
                    "affected_state_surfaces": ["memory"],
                    "expected_read_surface_refreshes": ["memory_projection"],
                }
            }
        ),
        encoding="utf-8",
    )
    uwg = assess_uwg_durable_write_chain(
        repo_root=tmp_path, artifact_dir=ad, integrated_dir=None
    )
    assert uwg["uwg_path_present"] is True
    assert uwg["durable_proof_chain_complete"] is False
    slots = build_semantic_cache_persistence_slots(
        repo_root=tmp_path,
        artifact_dir=ad,
        integrated_dir=None,
        uwg_assessment=uwg,
        assertion_path=None,
    )
    assert slots["semantic_cache_persistence_status"] in ("NOT_PROVEN", "PARTIAL_UWG_ARTIFACTS_ONLY")
    assert slots["slots"]["chroma_collection_index_ref"]["status"] == "MISSING"
