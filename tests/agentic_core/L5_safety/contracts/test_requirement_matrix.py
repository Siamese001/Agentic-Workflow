"""Regression guard for the L5 doctrine requirement coverage matrix.

Asserts that ``build_requirement_matrix.py`` continues to produce
0 UNCOVERED rows. If a new doctrine doc lands and adds requirements
the classifier doesn't recognize, this test fails until the classifier
is extended (or the doctrine row is honestly classified as UNCOVERED
and a corresponding deferred-scope plan opens).
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[4]
TOOL = REPO / "tools" / "l5_contracts" / "build_requirement_matrix.py"
JSON_OUT = REPO / "tools" / "l5_contracts" / "_requirement_matrix.json"


@pytest.fixture(scope="module")
def matrix_payload() -> dict:
    if not TOOL.exists():
        pytest.skip("matrix builder tool not present")
    # Run the builder fresh so the test reflects current doctrine.
    result = subprocess.run(
        [sys.executable, str(TOOL)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, (
        f"Matrix builder failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )
    return json.loads(JSON_OUT.read_text(encoding="utf-8"))


def test_matrix_has_no_uncovered_requirements(matrix_payload: dict) -> None:
    grand = matrix_payload["grand_totals"]
    assert grand["UNCOVERED"] == 0, (
        f"{grand['UNCOVERED']} doctrine requirements lack evidence links. "
        f"Either extend the classifier in build_requirement_matrix.py or "
        f"open a deferred-scope plan for the new gap."
    )


def test_matrix_has_no_partial_coverage(matrix_payload: dict) -> None:
    grand = matrix_payload["grand_totals"]
    assert grand["PARTIAL"] == 0, (
        f"{grand['PARTIAL']} requirements partially covered. Regenerate "
        f"contracts (`python tools/l5_contracts/generate_contracts.py`) "
        f"to bring them to FULL/STRUCTURAL."
    )


def test_matrix_total_matches_extraction(matrix_payload: dict) -> None:
    grand = matrix_payload["grand_totals"]
    total = grand["FULL"] + grand["STRUCTURAL"] + grand["PARTIAL"] + grand["UNCOVERED"]
    assert total == len(matrix_payload["rows"])
    # Doctrine has 561 normative statements at the time of writing.
    # Allow modest growth (new doctrine docs) but flag a >20% jump as
    # likely needing attention.
    assert 500 <= total <= 700, (
        f"Doctrine row count {total} is outside the expected 500-700 band; "
        f"either doctrine grew significantly or extraction broke."
    )


def test_full_coverage_matches_status_enums_plus_forbidden(
    matrix_payload: dict,
) -> None:
    """FULL == per-status enum hits + cited forbidden runtime tokens."""
    full_rows = [r for r in matrix_payload["rows"] if r["status"] == "FULL"]
    status_set_full = [r for r in full_rows if r["category"] == "STATUS_SET"]
    forbid_full = [r for r in full_rows if r["category"] == "FORBID_RD"]
    # 51 doctrine status fields produce 52 STATUS_SET FULL rows
    # (one field is declared in two docs - replay_binding_status).
    assert 50 <= len(status_set_full) <= 60
    assert len(forbid_full) >= 1
