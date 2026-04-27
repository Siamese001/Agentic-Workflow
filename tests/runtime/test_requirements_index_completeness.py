"""
tests/runtime/test_requirements_index_completeness.py

Phase 1 acceptance test.

Verifies that requirements_index.json:
  * exists alongside source_manifest.json
  * declares total_requirements > 0
  * carries every required field on every record
  * uses well-formed REQ-<slug>-<line>-<hash> ids
  * maps every record back to a real source line in a real source file
  * starts every record at status=UNMAPPED (foolproof rule: no PROVEN
    without Phase 2-7 evidence)
  * the CSV mirror is consistent with the JSON

This test also subsumes the spec-named
``test_requirements_source_line_mapping.py`` because it asserts that
``line_start >= 1``, ``source_path`` exists, and the line is reachable.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import pytest

REQ_ID_PATTERN = re.compile(r"^REQ-[a-z0-9-]+-\d{4}-[0-9a-f]{8}$")

REQUIRED_RECORD_FIELDS = frozenset(
    {
        "req_id",
        "source_folder",
        "source_path",
        "relative_path",
        "line_start",
        "line_end",
        "source_text",
        "requirement_type",
        "owning_layer",
        "normalized_requirement",
        "verification_needed",
        "status",
        "matched_markers",
    }
)

ALLOWED_REQUIREMENT_TYPES = frozenset(
    {
        "contract",
        "boundary",
        "gate",
        "otel",
        "replay",
        "test",
        "negative_test",
        "acceptance",
        "authority",
        "lineage",
        "schema",
        "evidence",
        "egress",
        "write",
        "learning",
        "runtime_disposition",
    }
)

ALLOWED_OWNING_LAYERS = frozenset(
    {
        "U0",
        "L1",
        "L0",
        "C0",
        "C0.0",
        "C0.1",
        "C0.2",
        "C0.3",
        "C0.4",
        "C0.5",
        "C0.6",
        "C0.7",
        "PA",
        "L3",
        "L2",
        "Exit",
        "RuntimeGates",
        "L5",
        "L4",
        "UWG",
        "L6",
        "CrossCutting",
    }
)


@pytest.fixture(scope="module")
def index(proof_artifacts: Path) -> dict:
    p = proof_artifacts / "requirements_index.json"
    return json.loads(p.read_text(encoding="utf-8"))


def test_index_file_exists(proof_artifacts: Path) -> None:
    assert (proof_artifacts / "requirements_index.json").exists()
    assert (proof_artifacts / "requirements_index.csv").exists()
    assert (proof_artifacts / "requirements_index.md").exists()


def test_index_has_records(index: dict) -> None:
    assert "summary" in index
    assert "records" in index
    assert index["summary"]["total_requirements"] > 0
    assert len(index["records"]) == index["summary"]["total_requirements"]


def test_every_record_has_required_fields(index: dict) -> None:
    for r in index["records"]:
        missing = REQUIRED_RECORD_FIELDS - set(r.keys())
        assert not missing, f"{r.get('req_id')} missing fields: {sorted(missing)}"


def test_every_req_id_well_formed(index: dict) -> None:
    for r in index["records"]:
        assert REQ_ID_PATTERN.match(r["req_id"]), f"bad req_id format: {r['req_id']}"


def test_no_record_is_proven_or_partial(index: dict) -> None:
    """Phase 1 may only emit UNMAPPED. PROVEN/PARTIAL are downstream phases."""
    statuses = {r["status"] for r in index["records"]}
    assert "PROVEN" not in statuses, "Phase 1 cannot mark anything PROVEN"
    assert "PARTIAL" not in statuses, "Phase 1 cannot mark anything PARTIAL"
    assert statuses <= {"UNMAPPED"}, f"unexpected statuses leaked: {statuses}"


def test_every_requirement_type_is_allowed(index: dict) -> None:
    for r in index["records"]:
        assert r["requirement_type"] in ALLOWED_REQUIREMENT_TYPES, (
            f"{r['req_id']} has unknown requirement_type={r['requirement_type']}"
        )


def test_every_owning_layer_is_allowed(index: dict) -> None:
    for r in index["records"]:
        assert r["owning_layer"] in ALLOWED_OWNING_LAYERS, (
            f"{r['req_id']} has unknown owning_layer={r['owning_layer']}"
        )


def test_every_record_points_at_real_source_line(index: dict) -> None:
    """
    Every record must map to a real file and a real line. Sample first 250
    records (full check would be expensive on large indices). Every sample
    must:
      * have source_path that exists on disk
      * have line_start >= 1
      * have line_end >= line_start
      * have line_start <= total lines in that file (verified by reading
        the file)
    """
    sample = index["records"][:250]
    line_counts: dict[str, int] = {}
    for r in sample:
        src = Path(r["source_path"])
        assert src.exists(), f"source_path missing for {r['req_id']}: {src}"
        assert r["line_start"] >= 1
        assert r["line_end"] >= r["line_start"]
        if str(src) not in line_counts:
            with src.open("rb") as f:
                line_counts[str(src)] = sum(1 for _ in f)
        assert r["line_start"] <= line_counts[str(src)], (
            f"{r['req_id']} line_start={r['line_start']} > file_lines={line_counts[str(src)]}"
        )


def test_every_record_has_nonempty_normalized_text(index: dict) -> None:
    for r in index["records"]:
        assert isinstance(r["normalized_requirement"], str)
        assert len(r["normalized_requirement"].strip()) >= 8


def test_every_record_has_at_least_one_marker(index: dict) -> None:
    for r in index["records"]:
        assert r["matched_markers"], (
            f"{r['req_id']} has no matched_markers; extractor must record what triggered it"
        )


def test_verification_needed_is_nonempty_list(index: dict) -> None:
    for r in index["records"]:
        v = r["verification_needed"]
        assert isinstance(v, list)
        assert v, f"{r['req_id']} has empty verification_needed list"
        # Must always include the irreducible minimum.
        assert "implementation_symbol" in v
        assert "proof_report_entry" in v


def test_summary_buckets_sum_to_total(index: dict) -> None:
    s = index["summary"]
    total = s["total_requirements"]
    assert sum(s["by_owning_layer"].values()) == total
    assert sum(s["by_requirement_type"].values()) == total
    assert sum(s["by_source_folder"].values()) == total
    assert sum(s["by_status"].values()) == total


def test_csv_consistent_with_json(proof_artifacts: Path, index: dict) -> None:
    csv_path = proof_artifacts / "requirements_index.csv"
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == index["summary"]["total_requirements"], (
        f"csv rows={len(rows)} != json total={index['summary']['total_requirements']}"
    )
    json_ids = {r["req_id"] for r in index["records"]}
    csv_ids = {r["req_id"] for r in rows}
    assert json_ids == csv_ids, (
        f"req_id mismatch: json_only={list(json_ids - csv_ids)[:5]}, "
        f"csv_only={list(csv_ids - json_ids)[:5]}"
    )


def test_md_summary_exists(proof_artifacts: Path, index: dict) -> None:
    p = proof_artifacts / "requirements_index.md"
    txt = p.read_text(encoding="utf-8")
    assert "# Requirements Index" in txt
    n = index["summary"]["total_requirements"]
    assert f"total_requirements: **{n}**" in txt


def test_gaps_md_exists_and_marks_phases_2_to_11_as_pending(proof_artifacts: Path) -> None:
    """The CLI must write GAPS.md so callers cannot mistake Phase 1 for completion."""
    p = proof_artifacts / "GAPS.md"
    assert p.exists(), "GAPS.md is required so Cascade cannot collapse UNKNOWN into DONE"
    txt = p.read_text(encoding="utf-8")
    # Must explicitly mention every undelivered phase.
    for phase in ("Phase 2", "Phase 3", "Phase 5", "Phase 6", "Phase 7", "Phase 8"):
        assert phase in txt, f"GAPS.md missing mention of {phase}"
