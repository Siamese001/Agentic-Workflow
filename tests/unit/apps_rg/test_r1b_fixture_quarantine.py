"""apps-test-model: APP CONTRACT.

R1B fixture mirror writes are opt-in proof artifacts, not runtime truth.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.cache.r1b_store import (
    R1BSemanticCacheStore,
    assert_fixture_store_not_used_for_runtime_lookup,
)
from apps_rg.cache.r1b_uwg_promotion import (
    AppsRgR1BUwgGateway,
    build_r1b_promotion_candidate,
    promote_and_project_r1b_cache,
)
from tests.unit.apps_rg.r1b_fixture_builders import (
    build_admissible_intent_record,
    build_admissible_output_chunks,
    build_post_exit_eligibility,
    write_post_exit_artifacts,
)


def _candidate(tmp_path: Path):
    record = build_admissible_intent_record(record_id="hir_fixture_quarantine")
    chunks = build_admissible_output_chunks(record.record_id)
    run_dir = tmp_path / "run"
    write_post_exit_artifacts(run_dir, record)
    return build_r1b_promotion_candidate(
        record=record,
        chunks=chunks,
        post_exit_eligibility=build_post_exit_eligibility(record, chunks),
        run_dir=run_dir,
    )


def test_fixture_manifest_is_not_runtime_routing_truth(tmp_path: Path) -> None:
    manifest = R1BSemanticCacheStore(tmp_path).store_manifest()
    assert manifest["runtime_read_eligible"] is False
    assert manifest["routing_truth"] is False
    assert manifest["requires_explicit_test_flag"] is True


def test_fixture_runtime_lookup_guard_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("APPS_RG_R1B_ALLOW_FIXTURE_FALLBACK_FOR_TESTS", raising=False)
    with pytest.raises(RuntimeError, match="not runtime read truth"):
        assert_fixture_store_not_used_for_runtime_lookup(purpose="unit-test")


def test_blocked_promotion_does_not_write_fixture_mirror_by_default(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APPS_RG_R1B_SKIP_UWG", "1")
    candidate = _candidate(tmp_path)
    store = R1BSemanticCacheStore(tmp_path / "fixture")

    outcome = promote_and_project_r1b_cache(
        candidate=candidate,
        projection_root=store.root,
        fixture_store=store,
        gateway=AppsRgR1BUwgGateway(),
    )

    assert outcome.status == "BLOCKED"
    assert outcome.fixture_mirror_written is False
    assert store.list_intent_record_ids() == []


def test_blocked_promotion_fixture_mirror_requires_explicit_flag(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APPS_RG_R1B_SKIP_UWG", "1")
    candidate = _candidate(tmp_path)
    store = R1BSemanticCacheStore(tmp_path / "fixture")

    outcome = promote_and_project_r1b_cache(
        candidate=candidate,
        projection_root=store.root,
        fixture_store=store,
        gateway=AppsRgR1BUwgGateway(),
        mirror_fixture_on_blocked=True,
    )

    assert outcome.status == "BLOCKED"
    assert outcome.fixture_mirror_written is True
    assert outcome.fixture_mirror_written_reason == "blocked_projection_explicit_test_mirror"
    assert store.list_intent_record_ids() == [candidate.record.record_id]
