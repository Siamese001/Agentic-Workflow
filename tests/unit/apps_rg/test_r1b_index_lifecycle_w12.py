"""W12 — R1B durable write-to-read lifecycle proof."""

from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.cache.r1b_derived_index import derived_index_available
from apps_rg.cache.r1b_index_lifecycle import prove_r1b_index_lifecycle
from apps_rg.cache.r1b_uwg_promotion import AppsRgR1BUwgGateway
from apps_rg.cache.r1b_store import R1BSemanticCacheStore
from apps_rg.cache.r1b_uwg_promotion import build_r1b_promotion_candidate, promote_and_project_r1b_cache
from apps_rg.cache.r1b_whole_run_preflight import execute_whole_run_r1b_preflight
from tests.unit.apps_rg.r1b_fixture_builders import (
    build_admissible_intent_record,
    build_admissible_output_chunks,
    build_post_exit_eligibility,
    r1b_match_request,
    write_post_exit_artifacts,
)


def _promote_admissible(tmp_path: Path) -> Path:
    """Promote current W7-compatible section chunks so reuse compatibility passes."""
    record = build_admissible_intent_record(record_id="hir_w12_admissible_001")
    chunks = build_admissible_output_chunks(record.record_id)
    run_dir = tmp_path / "run"
    write_post_exit_artifacts(run_dir, record)
    cand = build_r1b_promotion_candidate(
        record=record,
        chunks=chunks,
        post_exit_eligibility=build_post_exit_eligibility(record, chunks),
        run_dir=run_dir,
    )
    store = R1BSemanticCacheStore(tmp_path / "proj")
    outcome = promote_and_project_r1b_cache(
        candidate=cand,
        projection_root=store.root,
        gateway=AppsRgR1BUwgGateway(),
    )
    assert outcome.status == "ADMITTED"
    return store.root


def _match_request() -> dict:
    return r1b_match_request()


def test_lifecycle_accepted_hit_requires_exit_review(tmp_path: Path) -> None:
    root = _promote_admissible(tmp_path)
    lifecycle = prove_r1b_index_lifecycle(
        projection_root=root,
        match_request=_match_request(),
        miss_request={"target_company": "X", "target_role": "Y"},
        reject_request=_match_request(),
        prompt_profile_hash="prompt_profile_w7_v1",
        gate_profile_hash="gate_profile_w7_v1",
    )
    assert lifecycle.accepted_hit is True
    assert derived_index_available(root)
    pf = execute_whole_run_r1b_preflight(
        raw_request=_match_request(),
        runs_dir=str(root),
        similarity_threshold=0.5,
        prompt_profile_hash="prompt_profile_w7_v1",
        gate_profile_hash="gate_profile_w7_v1",
    )
    assert pf.r1b_hit is True
    assert pf.terminal_packet is not None
    assert pf.terminal_packet.get("exit_review_required") is True
    assert pf.terminal_packet.get("exit_bypassed") is False


def test_lifecycle_miss_fallthrough(tmp_path: Path) -> None:
    root = _promote_admissible(tmp_path)
    lifecycle = prove_r1b_index_lifecycle(
        projection_root=root,
        match_request=_match_request(),
        miss_request={"target_company": "Unrelated", "target_role": "Role", "resume_hash": "z"},
        reject_request=_match_request(),
        prompt_profile_hash="prompt_profile_w7_v1",
        gate_profile_hash="gate_profile_w7_v1",
    )
    assert lifecycle.miss_fallthrough is True


def test_lifecycle_rejected_profile_mismatch(tmp_path: Path) -> None:
    root = _promote_admissible(tmp_path)
    lifecycle = prove_r1b_index_lifecycle(
        projection_root=root,
        match_request=_match_request(),
        miss_request={"target_company": "Unrelated", "target_role": "Role"},
        reject_request=_match_request(),
        prompt_profile_hash="wrong",
        gate_profile_hash="wrong",
    )
    assert lifecycle.rejected_candidate is True
