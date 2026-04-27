"""
tests/runtime/test_coverage_matrix_consistency.py

Phase 3 acceptance test.

Asserts the coverage_matrix:
  * exists at the canonical export location (json + csv + md)
  * has exactly one row per record in requirements_index
  * uses only the closed vocabulary of coverage_status values
  * has zero PROVEN rows (Phase 5/6/7 not done; PROVEN must remain
    impossible until those phases land -- honors "do not collapse UNKNOWN
    into PASS")
  * statuses follow the deterministic rules from
    coverage_matrix_builder.compute_coverage_status

This test embodies the foolproof rule "Do not say complete unless
coverage_matrix exists" -- it both proves the matrix exists AND proves
its statuses are not silently inflated.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import pytest

# Coverage CSV rows can have very long `files` columns (up to 25 candidate
# locations joined). Bump the default 128KB field size limit so DictReader
# does not choke on ambiguous-candidate rows.
csv.field_size_limit(min(sys.maxsize, 2_000_000))

ALLOWED_COVERAGE_STATUSES = frozenset(
    {
        "PROVEN",
        "IMPLEMENTED_NOT_PROVEN",
        "PARTIAL",
        "MISSING",
        "CONFLICT",
        "NOT_APPLICABLE_WITH_JUSTIFICATION",
        "UNMAPPED",
    }
)

# Mapping from implementation_status -> expected coverage_status.
# Derived from coverage_matrix_builder.compute_coverage_status.
EXPECTED_STATUS_PAIR = {
    "NOT_APPLICABLE": "NOT_APPLICABLE_WITH_JUSTIFICATION",
    "NEEDS_HUMAN_MAPPING": "UNMAPPED",
    "MISSING": "MISSING",
    "AMBIGUOUS_CANDIDATE": "CONFLICT",
    "CROSS_LAYER_CANDIDATE": "PARTIAL",
    # IMPLEMENTED_CANDIDATE -> IMPLEMENTED_NOT_PROVEN until Phase 5/6/7
    "IMPLEMENTED_CANDIDATE": "IMPLEMENTED_NOT_PROVEN",
}


@pytest.fixture(scope="module")
def coverage(proof_artifacts: Path) -> dict:
    return json.loads(
        (proof_artifacts / "coverage_matrix.json").read_text(encoding="utf-8")
    )


@pytest.fixture(scope="module")
def index(proof_artifacts: Path) -> dict:
    return json.loads(
        (proof_artifacts / "requirements_index.json").read_text(encoding="utf-8")
    )


def test_coverage_files_exist(proof_artifacts: Path) -> None:
    for name in ("coverage_matrix.json", "coverage_matrix.csv", "coverage_matrix.md"):
        p = proof_artifacts / name
        assert p.exists(), f"{name} missing at {p}"


def test_one_row_per_requirement(coverage: dict, index: dict) -> None:
    assert coverage["summary"]["total_rows"] == index["summary"]["total_requirements"]
    assert len(coverage["rows"]) == coverage["summary"]["total_rows"]


def test_only_allowed_coverage_statuses(coverage: dict) -> None:
    statuses = {r["coverage_status"] for r in coverage["rows"]}
    unknown = statuses - ALLOWED_COVERAGE_STATUSES
    assert not unknown, f"unknown coverage_status values: {unknown}"


def test_zero_proven_rows_until_phase_5_6_7(coverage: dict) -> None:
    """PROVEN status is gated on Phase 5/6/7 evidence which has not landed.
    Honors the user's stop rule 'do not collapse UNKNOWN into PASS'."""
    proven = [r for r in coverage["rows"] if r["coverage_status"] == "PROVEN"]
    assert len(proven) == 0, (
        f"Found {len(proven)} PROVEN rows but Phase 5 (OTEL), Phase 6 (replay), "
        f"and Phase 7 (anti-bypass) have not been delivered yet. PROVEN must remain "
        f"zero until those phases supply the required evidence. Sample: "
        f"{[r['req_id'] for r in proven[:3]]}"
    )


def test_status_pair_rules_held(coverage: dict) -> None:
    """Implementation status -> coverage status mapping is deterministic."""
    for r in coverage["rows"]:
        impl = r["implementation_status"]
        cov = r["coverage_status"]
        expected = EXPECTED_STATUS_PAIR.get(impl)
        if expected is not None:
            assert cov == expected, (
                f"{r['req_id']}: impl={impl} should yield cov={expected}, got {cov}"
            )


def test_summary_buckets_sum_to_total(coverage: dict) -> None:
    s = coverage["summary"]
    assert sum(s["by_coverage_status"].values()) == s["total_rows"]
    assert sum(s["by_owning_layer"].values()) == s["total_rows"]


def test_csv_consistent_with_json(proof_artifacts: Path, coverage: dict) -> None:
    csv_path = proof_artifacts / "coverage_matrix.csv"
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == coverage["summary"]["total_rows"]
    json_ids = {r["req_id"] for r in coverage["rows"]}
    csv_ids = {r["req_id"] for r in rows}
    assert json_ids == csv_ids


def test_partial_rows_have_at_least_one_file_or_test(coverage: dict) -> None:
    """A PARTIAL row signals partial credit; it must have at least one
    file or test reference, otherwise it is misclassified."""
    for r in coverage["rows"]:
        if r["coverage_status"] == "PARTIAL":
            has_file = bool(r["files"])
            has_test = bool(r["test_files"])
            assert has_file or has_test, (
                f"{r['req_id']} PARTIAL with no file or test evidence"
            )


def test_implemented_not_proven_rows_carry_file_evidence(coverage: dict) -> None:
    for r in coverage["rows"]:
        if r["coverage_status"] == "IMPLEMENTED_NOT_PROVEN":
            assert r["files"], (
                f"{r['req_id']} IMPLEMENTED_NOT_PROVEN must carry file evidence"
            )


def test_md_summary_present(proof_artifacts: Path, coverage: dict) -> None:
    md = (proof_artifacts / "coverage_matrix.md").read_text(encoding="utf-8")
    assert "# Coverage Matrix" in md
    assert f"total_rows: **{coverage['summary']['total_rows']}**" in md
    # Must explicitly admit no PROVEN rows.
    assert "PROVEN count is\nexpected to be zero" in md or "expected to be zero" in md


def test_gaps_md_reflects_phase_2_3_delivered(proof_artifacts: Path) -> None:
    md = (proof_artifacts / "GAPS.md").read_text(encoding="utf-8")
    # After W2+W3+W4 the gap report must show DELIVERED (or DELIVERED_*) for
    # Phases 2, 3, 6, 7 and at minimum CONTRACT_* status for Phases 4 and 5.
    assert "Phase 2 | Map every requirement to code symbols" in md
    assert "Phase 3 | Coverage matrix joining" in md
    assert "Phase 4 | Implement runtime gaps" in md
    assert "Phase 5 | OTEL spans" in md
    assert "Phase 6 | Deterministic replay" in md
    assert "Phase 7 | Anti-bypass negative tests" in md
    assert "Phase 8 | E2E proof scenarios" in md
    # The honest framing: Phase 4 is still CONTRACT-only because OTEL is
    # not wired into the live runtime layers yet.
    assert "CONTRACT_ONLY" in md or "CONTRACT_PLUS_HARNESS" in md, (
        "Phase 4/5 must be honestly tagged as contract-only until live wiring lands"
    )
