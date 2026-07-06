"""apps-test-model: APP CONTRACT.

R1B derived index entries are bound to refresh receipts and commit receipts.
"""

from __future__ import annotations

import json
from pathlib import Path

from apps_rg.cache.r1b_derived_index import (
    derived_index_root,
    list_derived_index_record_ids,
    load_derived_index_entry,
)
from apps_rg.cache.r1b_uwg_promotion import (
    AppsRgR1BUwgGateway,
    build_r1b_promotion_candidate,
    promote_and_project_r1b_cache,
)
from apps_rg.cache.r1b_whole_run_preflight import execute_whole_run_r1b_preflight
from tests.unit.apps_rg.r1b_fixture_builders import (
    build_admissible_intent_record,
    build_admissible_output_chunks,
    build_post_exit_eligibility,
    r1b_match_request,
    write_post_exit_artifacts,
)


def _project(tmp_path: Path) -> Path:
    record = build_admissible_intent_record(record_id="hir_refresh_receipt")
    chunks = build_admissible_output_chunks(record.record_id)
    run_dir = tmp_path / "run"
    write_post_exit_artifacts(run_dir, record)
    candidate = build_r1b_promotion_candidate(
        record=record,
        chunks=chunks,
        post_exit_eligibility=build_post_exit_eligibility(record, chunks),
        run_dir=run_dir,
    )
    outcome = promote_and_project_r1b_cache(
        candidate=candidate,
        projection_root=tmp_path,
        gateway=AppsRgR1BUwgGateway(),
    )
    assert outcome.status == "ADMITTED"
    return tmp_path


def test_derived_index_entry_points_to_refresh_and_commit_receipts(tmp_path: Path) -> None:
    root = _project(tmp_path)
    record_ids = list_derived_index_record_ids(root)
    assert record_ids
    entry = load_derived_index_entry(root, record_ids[0]) or {}
    manifest = json.loads((derived_index_root(root) / "manifest.json").read_text(encoding="utf-8"))
    refresh_ref = entry["source_refresh_receipt_ref"]
    refresh = json.loads((root / refresh_ref).read_text(encoding="utf-8"))

    assert entry["source_commit_receipt_ref"] in manifest["source_commit_receipt_refs"]
    assert refresh_ref in manifest["source_refresh_receipt_refs"]
    assert refresh["source_commit_receipt_ref"] == entry["source_commit_receipt_ref"]
    assert manifest["read_surface_role"] == "projection_not_truth"


def test_missing_refresh_receipt_causes_lookup_miss(tmp_path: Path) -> None:
    root = _project(tmp_path)
    entry = load_derived_index_entry(root, list_derived_index_record_ids(root)[0]) or {}
    (root / entry["source_refresh_receipt_ref"]).unlink()

    result = execute_whole_run_r1b_preflight(
        raw_request=r1b_match_request(),
        runs_dir=root,
        similarity_threshold=0.5,
        prompt_profile_hash="prompt_profile_w7_v1",
        gate_profile_hash="gate_profile_w7_v1",
    )

    assert result.r1b_hit is False
    assert result.generation_required is True
    assert "read_surface_refresh_receipt_missing" in result.compatibility_report[0]["reason_codes"]
