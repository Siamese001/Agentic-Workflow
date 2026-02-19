#!/usr/bin/env python3
"""
Guardian Quarantine Contract Enforcement
artifact_class: QUARANTINE_CONTRACT
"""

import pathlib
from datetime import date, datetime

import pytest
import yaml


def test_quarantine_contract():
    """Test that quarantine policy is enforced."""
    quarantine_file = pathlib.Path("tests/_contracts/guardian_quarantine.yaml")

    if not quarantine_file.exists():
        pytest.fail("guardian_quarantine.yaml does not exist")

    with open(quarantine_file) as f:
        quarantine_data = yaml.safe_load(f)

    # Check structure
    assert "quarantined_tests" in quarantine_data
    assert "total_quarantined" in quarantine_data
    assert "created_date" in quarantine_data
    assert "policy" in quarantine_data

    quarantined_tests = quarantine_data["quarantined_tests"]

    # Check count matches actual entries
    assert quarantine_data["total_quarantined"] == len(quarantined_tests)

    # Check maximum limit
    assert len(quarantined_tests) <= 64, f"Too many quarantined tests: {len(quarantined_tests)} > 64"

    # Check each entry has required fields
    required_fields = ["path", "error_type", "reason", "owner", "expiry"]
    for entry in quarantined_tests:
        for field in required_fields:
            assert field in entry, f"Missing field '{field}' in entry: {entry}"

        # Check path format
        assert entry["path"].startswith("tests/"), f"Invalid path format: {entry['path']}"
        assert entry["path"].endswith(".py"), f"Path must be a Python file: {entry['path']}"

        # Check expiry dates
        expiry = entry["expiry"]
        if isinstance(expiry, str):
            expiry_date = datetime.strptime(expiry, "%Y-%m-%d").date()
        elif isinstance(expiry, datetime):
            expiry_date = expiry.date()
        elif isinstance(expiry, date):  # datetime.date
            expiry_date = expiry
        else:
            pytest.fail(f"Invalid expiry type for {entry['path']}: {type(expiry)}")

        if datetime.now().date() > expiry_date:
            pytest.fail(f"Quarantine entry for {entry['path']} expired on {expiry}")

        # Check owner is not empty
        assert entry["owner"].strip(), f"Empty owner in entry: {entry}"

    # Check paths are unique
    paths = [entry["path"] for entry in quarantined_tests]
    assert len(paths) == len(set(paths)), f"Duplicate paths in quarantine: {paths}"

    # Check no directories or globs - only explicit files
    for entry in quarantined_tests:
        path = entry["path"]
        assert path.endswith(".py"), f"Quarantine must be file-scoped: {path}"
        assert "*" not in path, f"Wildcard not allowed: {path}"
        assert "?" not in path, f"Wildcard not allowed: {path}"
        assert not path.endswith("/"), f"Directory quarantine not allowed: {path}"


def test_quarantine_files_exist():
    """Test that quarantined files actually exist."""
    quarantine_file = pathlib.Path("tests/_contracts/guardian_quarantine.yaml")

    with open(quarantine_file) as f:
        quarantine_data = yaml.safe_load(f)

    missing_files = []
    for entry in quarantine_data.get("quarantined_tests", []):
        path = entry["path"]
        # Check if file exists in canonical location
        if not pathlib.Path(path).exists():
            missing_files.append(path)

    if missing_files:
        pytest.fail(f"Quarantined files not found: {missing_files[:10]}")


if __name__ == "__main__":
    test_quarantine_contract()
    test_quarantine_files_exist()
    print("✅ Guardian quarantine contract satisfied!")
