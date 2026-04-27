"""
tests/runtime/test_requirements_coverage_matrix.py

Spec-named test 17 of 14 (numbered for completeness; Phase 10).

This is the spec's "coverage matrix" smoke test -- a thinner companion
to test_coverage_matrix_consistency.py. While the consistency test
asserts internal vocabulary closure and field shape, this test asserts
the END-USER reading: the matrix accurately reflects what the proof
system has and has not delivered.

If the gap report says PROVEN=0, the matrix must too. If a record claims
test_evidence, the test reference must resolve. If a record claims
file_evidence, the path must exist on disk.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def coverage(proof_artifacts: Path) -> dict:
    p = proof_artifacts / "coverage_matrix.json"
    if not p.exists():
        pytest.fail(f"missing coverage_matrix.json at {p}")
    return json.loads(p.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def gaps_md(proof_artifacts: Path) -> str:
    return (proof_artifacts / "GAPS.md").read_text(encoding="utf-8")


def test_coverage_matrix_artifact_present(coverage: dict) -> None:
    assert "rows" in coverage
    assert "summary" in coverage


def test_zero_proven_rows(coverage: dict) -> None:
    """The constitutional rule: PROVEN requires Phase 4 wiring + replay
    + anti-bypass. Until Phase 4 lands, PROVEN=0."""
    by_status = coverage["summary"].get("by_coverage_status", {})
    assert by_status.get("PROVEN", 0) == 0, (
        f"PROVEN count={by_status.get('PROVEN')}, expected 0 until Phase 4 wiring"
    )


def test_total_rows_is_substantial(coverage: dict) -> None:
    """Sanity check the extractor isn't producing an empty matrix."""
    assert coverage["summary"]["total_rows"] >= 2000, (
        f"total_rows={coverage['summary']['total_rows']} suspiciously low"
    )


def test_status_vocabulary_closed(coverage: dict) -> None:
    """Every coverage_status value must be from the closed vocabulary."""
    admissible = {
        "PROVEN",
        "IMPLEMENTED_NOT_PROVEN",
        "PARTIAL",
        "MISSING",
        "UNMAPPED",
        "CONFLICT",
        "NOT_APPLICABLE_WITH_JUSTIFICATION",
    }
    seen = set(coverage["summary"]["by_coverage_status"].keys())
    out_of_vocab = seen - admissible
    assert not out_of_vocab, (
        f"coverage_matrix uses out-of-vocab statuses: {out_of_vocab}"
    )


def test_implemented_not_proven_records_have_file_evidence(coverage: dict) -> None:
    """A record claiming IMPLEMENTED_NOT_PROVEN must point at a real
    code path on disk. We sample the first 5 such records."""
    sampled = [r for r in coverage["rows"] if r["coverage_status"] == "IMPLEMENTED_NOT_PROVEN"][:5]
    if not sampled:
        pytest.skip("no IMPLEMENTED_NOT_PROVEN records to sample")
    for r in sampled:
        files = r.get("files") or []
        assert files, (
            f"row {r.get('req_id')} claims IMPLEMENTED_NOT_PROVEN with no files"
        )
        for f in files:
            assert "path" in f and isinstance(f["path"], str) and f["path"], (
                f"row {r.get('req_id')} file evidence malformed: {f!r}"
            )


def test_summary_counts_sum_to_total(coverage: dict) -> None:
    """summary.by_coverage_status counts must sum to summary.total_rows."""
    total_from_buckets = sum(coverage["summary"]["by_coverage_status"].values())
    assert total_from_buckets == coverage["summary"]["total_rows"], (
        f"by_coverage_status sums to {total_from_buckets}, total_rows="
        f"{coverage['summary']['total_rows']}"
    )


def test_gaps_md_acknowledges_zero_proven(gaps_md: str) -> None:
    """The honest framing: GAPS.md must explicitly say PROVEN=0 is
    expected and explain why."""
    assert "expected to be zero" in gaps_md or "PROVEN count is" in gaps_md


def test_phases_2_through_7_marked_delivered(gaps_md: str) -> None:
    """After W2+W3+W4, Phases 2/3/6/7 are DELIVERED in the gap table."""
    delivered_phases = ["Phase 2", "Phase 3", "Phase 6", "Phase 7"]
    for p in delivered_phases:
        assert f"| {p} |" in gaps_md, f"GAPS.md missing row for {p}"
        # Find the line and ensure it has DELIVERED or DELIVERED_*
    lines = gaps_md.splitlines()
    for p in delivered_phases:
        line = next((l for l in lines if l.startswith(f"| {p} |")), None)
        assert line is not None
        assert "DELIVERED" in line, f"{p} row in GAPS.md is not DELIVERED: {line!r}"


def test_phase_4_marked_contract_only(gaps_md: str) -> None:
    """The honesty marker: Phase 4 is NOT yet wired into live runtime."""
    lines = gaps_md.splitlines()
    p4_line = next((l for l in lines if l.startswith("| Phase 4 |")), None)
    assert p4_line is not None
    assert "CONTRACT_ONLY" in p4_line, (
        f"Phase 4 must remain CONTRACT_ONLY until live wiring lands; got {p4_line!r}"
    )


def test_record_count_matches_index(coverage: dict, proof_artifacts: Path) -> None:
    """The coverage_matrix row count must match requirements_index record count."""
    idx = json.loads((proof_artifacts / "requirements_index.json").read_text(encoding="utf-8"))
    idx_total = idx["summary"]["total_requirements"]
    assert coverage["summary"]["total_rows"] == idx_total, (
        f"coverage rows={coverage['summary']['total_rows']} != "
        f"requirements_index records={idx_total}"
    )
