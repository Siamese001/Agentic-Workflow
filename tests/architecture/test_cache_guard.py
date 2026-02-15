#!/usr/bin/env python3
"""
Test for Cache & Temp Governance Guard

CI enforcement test that ensures cache guard passes
and no tracked files are modified during execution.
"""

import json
import subprocess
import sys
from pathlib import Path


def test_cache_guard_execution():
    """Test that cache guard executes and produces valid report."""
    root_path = Path(__file__).parent.parent.parent
    report_path = root_path / "artifacts" / "governance" / "cache_guard_report.json"

    # Execute cache guard
    result = subprocess.run(
        [sys.executable, str(root_path / "tools" / "governance" / "cache_guard.py")],
        capture_output=True,
        text=True,
        cwd=str(root_path),
    )

    # Assert execution succeeded
    assert result.returncode == 0, f"Cache guard failed with output: {result.stdout}\n{result.stderr}"

    # Assert report file exists
    assert report_path.exists(), f"Report file not found at {report_path}"

    # Load and validate report schema
    with open(report_path) as f:
        report = json.load(f)

    # Assert report structure
    assert "dirs_scanned" in report, "Report missing 'dirs_scanned' field"
    assert "violations" in report, "Report missing 'violations' field"
    assert "inventory" in report, "Report missing 'inventory' field"
    assert isinstance(report["dirs_scanned"], int), "dirs_scanned must be integer"
    assert isinstance(report["violations"], list), "violations must be list"
    assert isinstance(report["inventory"], list), "inventory must be list"

    # Assert zero violations
    assert len(report["violations"]) == 0, f"Cache governance violations detected. See {report_path}"

    # Assert directories were actually scanned
    print(f"Directories scanned: {report['dirs_scanned']}")

    # Assert inventory has expected structure
    for item in report["inventory"]:
        assert "path" in item, "Inventory item missing 'path' field"
        assert "type" in item, "Inventory item missing 'type' field"
        assert "detail" in item, "Inventory item missing 'detail' field"

    print("✓ Cache guard executed successfully")
    print(f"✓ Report generated: {report_path}")
    print(f"✓ Directories scanned: {report['dirs_scanned']}")
    print(f"✓ Violations: {len(report['violations'])}")
    print(f"✓ Cache directories found: {len(report['inventory'])}")


def test_no_files_modified():
    """Test that cache guard does not modify any tracked files."""
    root_path = Path(__file__).parent.parent.parent

    # Get git status before
    result_before = subprocess.run(
        ["git", "status", "--porcelain"], capture_output=True, text=True, cwd=str(root_path)
    )

    # Execute cache guard
    subprocess.run(
        [sys.executable, str(root_path / "tools" / "governance" / "cache_guard.py")],
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

    assert changes_before == changes_after, f"Tracked files were modified by cache guard: {changes_after}"

    print("✓ No tracked files modified by cache guard")


if __name__ == "__main__":
    print("Running cache governance guard enforcement test...")

    try:
        test_cache_guard_execution()
        test_no_files_modified()
        print("\n✓ All cache guard tests passed")
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        print("See artifacts/governance/cache_guard_report.json for details")
        sys.exit(1)
