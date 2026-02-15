#!/usr/bin/env python3
"""
Test: No Credentials in Repository

Guardian Enforcement Test for Credential Scanner

Ensures deterministic credential scanner executes and finds zero violations.
"""

import json
import subprocess
import sys
from pathlib import Path


def test_credential_guard_execution():
    """Test that credential guard executes and produces report."""
    root_path = Path(__file__).parent.parent.parent
    credential_guard_path = root_path / "tools" / "security" / "credential_guard.py"
    report_path = root_path / "artifacts" / "security" / "credential_scan_report.json"

    # Execute credential guard
    print("Executing credential guard...")
    result = subprocess.run(
        [sys.executable, str(credential_guard_path)], capture_output=True, text=True, cwd=str(root_path)
    )

    # Print execution output
    print("STDOUT:")
    print(result.stdout)
    if result.stderr:
        print("STDERR:")
        print(result.stderr)

    # Assert execution succeeded
    assert result.returncode == 0, f"Credential guard failed with exit code {result.returncode}"

    # Assert report was created
    assert report_path.exists(), f"Credential scan report not found at {report_path}"

    # Load and validate report
    with open(report_path) as f:
        report = json.load(f)

    # Assert report structure
    assert "files_scanned" in report, "Report missing 'files_scanned' field"
    assert "violations" in report, "Report missing 'violations' field"
    assert isinstance(report["files_scanned"], int), "files_scanned must be integer"
    assert isinstance(report["violations"], list), "violations must be list"

    # Assert zero violations
    assert len(report["violations"]) == 0, f"Credential violations detected. See {report_path}"

    # Assert files were actually scanned
    assert report["files_scanned"] > 0, "No files were scanned"

    print("✓ Credential guard executed successfully")
    print(f"✓ Report generated: {report_path}")
    print(f"✓ Files scanned: {report['files_scanned']}")
    print(f"✓ Violations: {len(report['violations'])}")


def test_no_files_modified():
    """Test that credential guard does not modify any files except the report."""
    root_path = Path(__file__).parent.parent.parent

    # Get git status before
    result = subprocess.run(
        ["git", "status", "--porcelain"], capture_output=True, text=True, cwd=str(root_path)
    )

    # Should be clean or only have report file changes
    all_changes = [line for line in result.stdout.split("\n") if line.strip()]
    modified_files = [
        line
        for line in all_changes
        if not line.startswith("??") and "credential_scan_report.json" not in line
    ]

    assert len(modified_files) == 0, f"Files were modified by credential guard: {modified_files}"

    print("✓ No files modified by credential guard (report file excluded)")


if __name__ == "__main__":
    print("Running credential guard enforcement test...")

    try:
        test_credential_guard_execution()
        test_no_files_modified()
        print("\n✓ All credential guard tests passed")
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)
