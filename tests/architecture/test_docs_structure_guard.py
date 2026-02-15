#!/usr/bin/env python3
"""
Test for Documentation Structure Guard

CI enforcement test that ensures docs structure guard passes
and no tracked files are modified during execution.
"""

import json
import subprocess
import sys
from pathlib import Path


def test_docs_structure_guard_execution():
    """Test that docs structure guard executes and produces valid report."""
    root_path = Path(__file__).parent.parent.parent
    report_path = root_path / "artifacts" / "governance" / "docs_structure_report.json"

    # Execute docs structure guard
    result = subprocess.run(
        [sys.executable, str(root_path / "tools" / "governance" / "docs_structure_guard.py")],
        capture_output=True,
        text=True,
        cwd=str(root_path),
    )

    # Assert execution succeeded
    assert result.returncode == 0, (
        f"Docs structure guard failed with output: {result.stdout}\n{result.stderr}"
    )

    # Assert report file exists
    assert report_path.exists(), f"Report file not found at {report_path}"

    # Load and validate report schema
    with open(report_path) as f:
        report = json.load(f)

    # Assert report structure
    assert "files_scanned" in report, "Report missing 'files_scanned' field"
    assert "violations" in report, "Report missing 'violations' field"
    assert isinstance(report["files_scanned"], int), "files_scanned must be integer"
    assert isinstance(report["violations"], list), "violations must be list"

    # Assert zero violations
    assert len(report["violations"]) == 0, f"Docs structure violations detected. See {report_path}"

    # Assert files were actually scanned
    assert report["files_scanned"] > 0, "No files were scanned"

    print("✓ Docs structure guard executed successfully")
    print(f"✓ Report generated: {report_path}")
    print(f"✓ Files scanned: {report['files_scanned']}")
    print(f"✓ Violations: {len(report['violations'])}")


def test_no_files_modified():
    """Test that docs structure guard does not modify any tracked files."""
    root_path = Path(__file__).parent.parent.parent

    # Get git status before
    result_before = subprocess.run(
        ["git", "status", "--porcelain"], capture_output=True, text=True, cwd=str(root_path)
    )

    # Execute docs structure guard
    subprocess.run(
        [sys.executable, str(root_path / "tools" / "governance" / "docs_structure_guard.py")],
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

    assert changes_before == changes_after, (
        f"Tracked files were modified by docs structure guard: {changes_after}"
    )

    print("✓ No tracked files modified by docs structure guard")


if __name__ == "__main__":
    print("Running docs structure guard enforcement test...")

    try:
        test_docs_structure_guard_execution()
        test_no_files_modified()
        print("\n✓ All docs structure guard tests passed")
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
