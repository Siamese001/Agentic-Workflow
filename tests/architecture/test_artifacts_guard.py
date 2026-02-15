#!/usr/bin/env python3
"""
Test for Artifacts Governance Guard

CI enforcement test that ensures artifacts guard passes
and no tracked files are modified during execution.
"""

import json
import subprocess
import sys
from pathlib import Path


def test_artifacts_guard_execution():
    """Test that artifacts guard executes and produces valid report."""
    root_path = Path(__file__).parent.parent.parent
    report_path = root_path / "artifacts" / "governance" / "artifacts_guard_report.json"

    # Execute artifacts guard
    result = subprocess.run(
        [sys.executable, str(root_path / "tools" / "governance" / "artifacts_guard.py")],
        capture_output=True,
        text=True,
        cwd=str(root_path),
    )

    # Assert execution succeeded
    assert result.returncode == 0, f"Artifacts guard failed with output: {result.stdout}\n{result.stderr}"

    # Assert report file exists
    assert report_path.exists(), f"Report file not found at {report_path}"

    # Load and validate report schema
    with open(report_path) as f:
        report = json.load(f)

    # Assert report structure
    assert "files_scanned" in report, "Report missing 'files_scanned' field"
    assert "violations" in report, "Report missing 'violations' field"
    assert "inventory" in report, "Report missing 'inventory' field"
    assert isinstance(report["files_scanned"], int), "files_scanned must be integer"
    assert isinstance(report["violations"], list), "violations must be list"
    assert isinstance(report["inventory"], list), "inventory must be list"

    # Assert zero violations
    assert len(report["violations"]) == 0, f"Artifacts governance violations detected. See {report_path}"

    # Assert files were actually scanned
    assert report["files_scanned"] > 0, "No files were scanned"

    # Assert inventory has expected structure
    for item in report["inventory"]:
        assert "file" in item, "Inventory item missing 'file' field"
        assert "bytes" in item, "Inventory item missing 'bytes' field"
        assert "ext" in item, "Inventory item missing 'ext' field"

    print("✓ Artifacts guard executed successfully")
    print(f"✓ Report generated: {report_path}")
    print(f"✓ Files scanned: {report['files_scanned']}")
    print(f"✓ Violations: {len(report['violations'])}")
    print(f"✓ Inventory items: {len(report['inventory'])}")


def test_no_files_modified():
    """Test that artifacts guard does not modify any tracked files."""
    root_path = Path(__file__).parent.parent.parent

    # Get git status before
    result_before = subprocess.run(
        ["git", "status", "--porcelain"], capture_output=True, text=True, cwd=str(root_path)
    )

    # Execute artifacts guard
    subprocess.run(
        [sys.executable, str(root_path / "tools" / "governance" / "artifacts_guard.py")],
        capture_output=True,
        text=True,
        cwd=str(root_path),
    )

    # Get git status after
    result_after = subprocess.run(
        ["git", "status", "--porcelain"], capture_output=True, text=True, cwd=str(root_path)
    )

    # Assert no changes in tracked files
    changes_before = [line for line in result_before.stdout.split("\n") if line.strip()]
    changes_after = [line for line in result_after.stdout.split("\n") if line.strip()]

    assert changes_before == changes_after, f"Tracked files were modified by artifacts guard: {changes_after}"

    print("✓ No tracked files modified by artifacts guard")


if __name__ == "__main__":
    print("Running artifacts governance guard enforcement test...")

    try:
        test_artifacts_guard_execution()
        test_no_files_modified()
        print("\n✓ All artifacts guard tests passed")
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        print("See artifacts/governance/artifacts_guard_report.json for details")
        sys.exit(1)
