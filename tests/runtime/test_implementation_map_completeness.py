"""
tests/runtime/test_implementation_map_completeness.py

Phase 2 acceptance test.

Asserts the implementation_map artifact:
  * exists at the canonical export location (json + csv + missing md)
  * has exactly one mapping per record in requirements_index
  * uses only the closed vocabulary of implementation_status values
  * carries a non-empty file evidence list whenever the status is one of
    IMPLEMENTED_CANDIDATE | CROSS_LAYER_CANDIDATE | AMBIGUOUS_CANDIDATE
  * surfaces every MISSING record in missing_requirements.md (capped to
    500 rows in the summary; the full set lives in implementation_map.csv)

This honors the foolproof rule: a record cannot be claimed to map to a
code symbol unless that symbol exists in the catalog and a file path is
recorded.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import pytest

# Implementation map rows can have very long `files` columns (up to 25
# candidate locations joined). Bump the default 128KB field size limit so
# DictReader does not choke on ambiguous-candidate rows.
csv.field_size_limit(min(sys.maxsize, 2_000_000))

ALLOWED_IMPL_STATUSES = frozenset(
    {
        "IMPLEMENTED_CANDIDATE",
        "CROSS_LAYER_CANDIDATE",
        "AMBIGUOUS_CANDIDATE",
        "MISSING",
        "NEEDS_HUMAN_MAPPING",
        "NOT_APPLICABLE",
    }
)

STATUSES_REQUIRING_FILES = frozenset(
    {"IMPLEMENTED_CANDIDATE", "CROSS_LAYER_CANDIDATE", "AMBIGUOUS_CANDIDATE"}
)


@pytest.fixture(scope="module")
def impl_map(proof_artifacts: Path) -> dict:
    return json.loads(
        (proof_artifacts / "implementation_map.json").read_text(encoding="utf-8")
    )


@pytest.fixture(scope="module")
def index(proof_artifacts: Path) -> dict:
    return json.loads(
        (proof_artifacts / "requirements_index.json").read_text(encoding="utf-8")
    )


def test_implementation_map_files_exist(proof_artifacts: Path) -> None:
    for name in ("implementation_map.json", "implementation_map.csv", "missing_requirements.md"):
        p = proof_artifacts / name
        assert p.exists(), f"{name} missing at {p}"


def test_one_mapping_per_record(impl_map: dict, index: dict) -> None:
    n_records = index["summary"]["total_requirements"]
    n_mappings = impl_map["summary"]["total_mappings"]
    assert n_records == n_mappings, (
        f"requirements={n_records} but mappings={n_mappings}"
    )


def test_every_req_id_in_index_has_mapping(impl_map: dict, index: dict) -> None:
    index_ids = {r["req_id"] for r in index["records"]}
    map_ids = {m["req_id"] for m in impl_map["mappings"]}
    missing = index_ids - map_ids
    extra = map_ids - index_ids
    assert not missing, f"requirements with no mapping: {list(missing)[:5]}"
    assert not extra, f"mappings with no requirement: {list(extra)[:5]}"


def test_only_allowed_implementation_statuses(impl_map: dict) -> None:
    statuses = {m["implementation_status"] for m in impl_map["mappings"]}
    unknown = statuses - ALLOWED_IMPL_STATUSES
    assert not unknown, f"unknown implementation_status values: {unknown}"


def test_status_summary_buckets_sum_to_total(impl_map: dict) -> None:
    s = impl_map["summary"]
    assert sum(s["by_implementation_status"].values()) == s["total_mappings"]


def test_candidate_statuses_carry_file_evidence(impl_map: dict) -> None:
    """A candidate status without file evidence is a contract violation."""
    for m in impl_map["mappings"]:
        if m["implementation_status"] in STATUSES_REQUIRING_FILES:
            assert m["files"], (
                f"{m['req_id']} has status {m['implementation_status']} but no files"
            )
            for f in m["files"]:
                assert "path" in f and f["path"]
                assert "symbol" in f and f["symbol"]
                assert "line" in f and isinstance(f["line"], int)
                assert f["line"] >= 1


def test_missing_status_has_no_files(impl_map: dict) -> None:
    for m in impl_map["mappings"]:
        if m["implementation_status"] == "MISSING":
            assert not m["files"], (
                f"{m['req_id']} status=MISSING must not carry file evidence"
            )


def test_needs_human_mapping_status_has_no_anchors(impl_map: dict) -> None:
    for m in impl_map["mappings"]:
        if m["implementation_status"] == "NEEDS_HUMAN_MAPPING":
            assert not m["anchors_extracted"], (
                f"{m['req_id']} NEEDS_HUMAN_MAPPING but anchors were extracted"
            )


def test_csv_consistent_with_json(proof_artifacts: Path, impl_map: dict) -> None:
    csv_path = proof_artifacts / "implementation_map.csv"
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == impl_map["summary"]["total_mappings"]
    json_ids = {m["req_id"] for m in impl_map["mappings"]}
    csv_ids = {r["req_id"] for r in rows}
    assert json_ids == csv_ids


def test_missing_requirements_md_present(proof_artifacts: Path, impl_map: dict) -> None:
    md = (proof_artifacts / "missing_requirements.md").read_text(encoding="utf-8")
    assert "# Missing Requirements" in md
    n_missing = sum(
        1
        for m in impl_map["mappings"]
        if m["implementation_status"] == "MISSING"
    )
    n_human = sum(
        1
        for m in impl_map["mappings"]
        if m["implementation_status"] == "NEEDS_HUMAN_MAPPING"
    )
    assert f"total_missing: **{n_missing}**" in md
    assert f"total_needs_human_mapping: **{n_human}**" in md


def test_file_evidence_paths_resolve_on_disk(impl_map: dict, repo_root: Path) -> None:
    """Sample 50 candidate mappings; their file paths must exist."""
    candidates = [
        m for m in impl_map["mappings"]
        if m["implementation_status"] in STATUSES_REQUIRING_FILES
    ][:50]
    for m in candidates:
        for f in m["files"]:
            p = repo_root / f["path"]
            assert p.exists(), f"file path in {m['req_id']} not on disk: {p}"
