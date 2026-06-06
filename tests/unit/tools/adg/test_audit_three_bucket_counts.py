"""Unit tests for tools/adg/audit_three_bucket_counts.run_authority_audit.

Projects legacy edge authority histograms into three-bucket proof/risk/inventory
counts consumed by ADG three-bucket reports and gap remediation gates.
"""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.adg.audit_three_bucket_counts import run_authority_audit  # noqa: E402


def _build_authority_snapshot(path: Path) -> None:
    """Synthetic ADG snapshot with one row per legacy authority label."""
    con = sqlite3.connect(path)
    con.execute(
        "CREATE TABLE edges (id INTEGER PRIMARY KEY, authority TEXT)"
    )
    rows = [
        ("verified", 10),
        ("unresolved", 4),
        ("dynamic", 3),
        ("external", 2),
        ("test_only", 5),
        ("runtime_observed", 6),
        ("<NULL>", 2),
        ("unknown_legacy_label", 1),
    ]
    for authority, count in rows:
        for _ in range(count):
            con.execute("INSERT INTO edges (authority) VALUES (?)", (authority,))
    con.commit()
    con.close()


@pytest.fixture
def authority_snapshot(tmp_path: Path) -> Path:
    snap = tmp_path / "adg_indexed_test.sqlite"
    _build_authority_snapshot(snap)
    return snap


def test_run_authority_audit_projects_legacy_histogram(authority_snapshot: Path) -> None:
    result = run_authority_audit(authority_snapshot)

    assert result["snapshot"] == authority_snapshot.name
    assert result["total_edges"] == 33
    assert result["before_legacy_authority_histogram"]["verified"] == 10
    assert result["after_projected_bucket_counts"] == {
        "static": 24,  # verified + unresolved + dynamic + external + test_only
        "runtime": 6,
        "registry": 0,
    }
    assert result["after_projected_authority_status_counts"]["AUTHORITATIVE"] == 10
    assert result["after_projected_authority_status_counts"]["AUTHORITATIVE_RUNTIME"] == 6
    assert result["after_projected_authority_status_counts"]["RISK_SIGNAL_ONLY"] == 4
    assert result["after_projected_authority_status_counts"]["UNKNOWN_NOT_PROOF"] == 3
    assert result["after_projected_authority_status_counts"]["EXTERNAL_ONLY"] == 2
    assert result["after_projected_authority_status_counts"]["EXCLUDED_TEST_ONLY"] == 5
    assert result["proof_count"] == 16
    assert result["risk_count"] == 7
    assert result["inventory_only_count"] == 7


def test_run_authority_audit_skips_null_and_unknown_legacy_labels(
    authority_snapshot: Path,
) -> None:
    result = run_authority_audit(authority_snapshot)

    # NULL + unknown labels are present in the histogram but excluded from projection.
    assert result["before_legacy_authority_histogram"]["<NULL>"] == 2
    assert result["before_legacy_authority_histogram"]["unknown_legacy_label"] == 1
    projected_total = sum(result["after_projected_bucket_counts"].values())
    assert projected_total == 30


def test_run_authority_audit_writes_json_when_out_path_set(
    authority_snapshot: Path, tmp_path: Path
) -> None:
    out_path = tmp_path / "authority_counts.json"
    result = run_authority_audit(authority_snapshot, out_path=out_path)

    assert out_path.is_file()
    loaded = json.loads(out_path.read_text(encoding="utf-8"))
    assert loaded["proof_count"] == result["proof_count"]
    assert loaded["snapshot"] == authority_snapshot.name


def test_run_authority_audit_empty_snapshot(tmp_path: Path) -> None:
    snap = tmp_path / "empty.sqlite"
    con = sqlite3.connect(snap)
    con.execute("CREATE TABLE edges (id INTEGER PRIMARY KEY, authority TEXT)")
    con.commit()
    con.close()

    result = run_authority_audit(snap)
    assert result["total_edges"] == 0
    assert result["proof_count"] == 0
    assert result["risk_count"] == 0
    assert result["inventory_only_count"] == 0
