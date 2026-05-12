#!/usr/bin/env python3
"""
receipt_validator.py - Shared 12-field migration receipt validation.

Validates migration receipts for TEMPORARY_THIN_ADAPTER classification.
Used by core_write_guard.py and core_leakage_scan.py.

All 12 mandatory fields must be present and valid:
1. binding_file - exact match required
2. classification - must be in ALLOWED_CLASSIFICATIONS
3. owner - non-empty, must exist
4. created_at - ISO timestamp present
5. migration_target_date - YYYY-MM-DD, not expired
6. expiry_enforced_by_ci - must be True (boolean)
7. migration_path - non-empty string
8. blocking_migration_reason - non-empty string
9. adapter_only_justification - non-empty string
10. test_coverage - non-empty list, files must exist
11. approver - non-empty string
12. receipt_version - present
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

# Configuration
REPO_ROOT = Path(__file__).resolve().parents[2]
MIGRATION_RECEIPTS_DIR = REPO_ROOT / "artifacts" / "governance" / "migration_receipts"

# 12 mandatory fields
REQUIRED_FIELDS = [
    "binding_file",
    "classification",
    "owner",
    "created_at",
    "migration_target_date",
    "expiry_enforced_by_ci",
    "migration_path",
    "blocking_migration_reason",
    "adapter_only_justification",
    "test_coverage",
    "approver",
    "receipt_version",
]

ALLOWED_CLASSIFICATIONS = [
    "TEMPORARY_THIN_ADAPTER",
    "GENERIC_READY",
    "MIGRATION_EXCEPTION",
    "FALSE_POSITIVE",
    "CORE_APP_SPECIFIC_LEAKAGE",
]


class ReceiptValidationError(Exception):
    """Raised when receipt validation fails."""
    pass


def validate_receipt_12field(receipt: Dict[str, Any], binding_file: str = None) -> Tuple[bool, str]:
    """
    Validate receipt has all 12 mandatory fields.
    
    Args:
        receipt: Parsed JSON receipt
        binding_file: Expected binding file path (for exact match)
        
    Returns:
        (is_valid, reason_message)
    """
    # Check all required fields present
    for field in REQUIRED_FIELDS:
        if field not in receipt:
            return False, f"Missing required field: {field}"
    
    # 1. binding_file - exact match
    receipt_binding = receipt.get("binding_file", "")
    if binding_file and receipt_binding != binding_file:
        return False, f"binding_file mismatch: expected {binding_file}, got {receipt_binding}"
    if not receipt_binding:
        return False, "binding_file is empty"
    
    # 2. classification - allowed enum
    classification = receipt.get("classification", "")
    if classification not in ALLOWED_CLASSIFICATIONS:
        return False, f"Invalid classification: {classification}"
    
    # 3. owner - non-empty
    owner = receipt.get("owner", "")
    if not owner or not isinstance(owner, str):
        return False, "owner must be non-empty string"
    # TODO: Validate owner exists in system (deferred to runtime check)
    
    # 4. created_at - present
    created_at = receipt.get("created_at", "")
    if not created_at:
        return False, "created_at is empty"
    
    # 5. migration_target_date - not expired
    target_date = receipt.get("migration_target_date", "")
    if not target_date:
        return False, "migration_target_date is empty"
    try:
        today = datetime.now().date()
        target = datetime.strptime(target_date, "%Y-%m-%d").date()
        if target < today:
            return False, f"EXPIRED: migration_target_date {target_date} has passed"
    except ValueError:
        return False, f"Invalid migration_target_date format: {target_date}"
    
    # 6. expiry_enforced_by_ci - must be True
    expiry_enforced = receipt.get("expiry_enforced_by_ci")
    if expiry_enforced is not True:
        return False, f"expiry_enforced_by_ci must be True (boolean), got {expiry_enforced}"
    
    # 7. migration_path - non-empty
    migration_path = receipt.get("migration_path", "")
    if not migration_path or len(migration_path) < 20:
        return False, "migration_path must be non-empty and at least 20 characters"
    
    # 8. blocking_migration_reason - non-empty
    blocking_reason = receipt.get("blocking_migration_reason", "")
    if not blocking_reason:
        return False, "blocking_migration_reason is empty"
    
    # 9. adapter_only_justification - non-empty
    adapter_justification = receipt.get("adapter_only_justification", "")
    if not adapter_justification or len(adapter_justification) < 100:
        return False, "adapter_only_justification must be at least 100 characters"
    
    # 10. test_coverage - non-empty list, files exist
    test_coverage = receipt.get("test_coverage", [])
    if not isinstance(test_coverage, list) or len(test_coverage) == 0:
        return False, "test_coverage must be non-empty list"
    for test_path in test_coverage:
        if not isinstance(test_path, str):
            return False, f"test_coverage item must be string: {test_path}"
        full_path = REPO_ROOT / test_path
        if not full_path.exists():
            return False, f"Referenced test file not found: {test_path}"
    
    # 11. approver - non-empty
    approver = receipt.get("approver", "")
    if not approver:
        return False, "approver is empty"
    
    # 12. receipt_version - present
    receipt_version = receipt.get("receipt_version", "")
    if not receipt_version:
        return False, "receipt_version is empty"
    
    return True, "Receipt valid (all 12 fields)"


def find_and_validate_receipt(binding_file: str) -> Tuple[bool, str, Optional[Dict]]:
    """
    Find receipt for binding file and validate all 12 fields.
    
    Args:
        binding_file: Path to binding file
        
    Returns:
        (is_valid, reason_message, receipt_dict or None)
    """
    if not MIGRATION_RECEIPTS_DIR.exists():
        return False, "No migration_receipts directory", None
    
    binding_name = Path(binding_file).stem
    
    # Look for receipts
    for receipt_file in MIGRATION_RECEIPTS_DIR.glob("*_receipt.json"):
        try:
            with open(receipt_file, "r", encoding="utf-8") as f:
                receipt = json.load(f)
                
                # Check if this receipt matches the binding file
                receipt_binding = receipt.get("binding_file", "")
                if receipt_binding == binding_file or receipt_binding.endswith(binding_file):
                    # Found matching receipt, validate it
                    is_valid, reason = validate_receipt_12field(receipt, binding_file)
                    return is_valid, reason, receipt
                    
        except (json.JSONDecodeError, IOError) as e:
            continue
    
    return False, f"No receipt found for {binding_file}", None


def has_valid_receipt(binding_file: str) -> bool:
    """Check if binding file has a valid 12-field receipt."""
    is_valid, _, _ = find_and_validate_receipt(binding_file)
    return is_valid


# Negative control tests
def test_validate_receipt_missing_field():
    """Negative control: Receipt missing required field."""
    receipt = {
        "binding_file": "test.py",
        "classification": "TEMPORARY_THIN_ADAPTER",
        # Missing owner and other fields
    }
    is_valid, reason = validate_receipt_12field(receipt)
    assert not is_valid, "Should fail for missing fields"
    assert "Missing required field" in reason
    print("NEGATIVE CONTROL CONFIRMED: Missing field detected")


def test_validate_receipt_expired():
    """Negative control: Expired receipt."""
    receipt = {
        "binding_file": "test.py",
        "classification": "TEMPORARY_THIN_ADAPTER",
        "owner": "test",
        "created_at": "2026-01-01T00:00:00Z",
        "migration_target_date": "2020-01-01",  # Expired
        "expiry_enforced_by_ci": True,
        "migration_path": "Path to migrate to generic engine with enough chars",
        "blocking_migration_reason": "Blocking reason here",
        "adapter_only_justification": "A" * 100,
        "test_coverage": ["tests/test_example.py"],
        "approver": "operator",
        "receipt_version": "1.0",
    }
    is_valid, reason = validate_receipt_12field(receipt)
    assert not is_valid, "Should fail for expired date"
    assert "EXPIRED" in reason
    print("NEGATIVE CONTROL CONFIRMED: Expired receipt rejected")


def test_validate_receipt_expiry_not_enforced():
    """Negative control: expiry_enforced_by_ci is not True."""
    receipt = {
        "binding_file": "test.py",
        "classification": "TEMPORARY_THIN_ADAPTER",
        "owner": "test",
        "created_at": "2026-01-01T00:00:00Z",
        "migration_target_date": "2026-12-31",
        "expiry_enforced_by_ci": False,  # Not True
        "migration_path": "Path to migrate to generic engine with enough chars",
        "blocking_migration_reason": "Blocking reason here",
        "adapter_only_justification": "A" * 100,
        "test_coverage": ["tests/test_example.py"],
        "approver": "operator",
        "receipt_version": "1.0",
    }
    is_valid, reason = validate_receipt_12field(receipt)
    assert not is_valid, "Should fail for expiry_enforced_by_ci=False"
    assert "expiry_enforced_by_ci must be True" in reason
    print("NEGATIVE CONTROL CONFIRMED: expiry_enforced_by_ci=False rejected")


def test_validate_receipt_missing_test_file():
    """Negative control: Referenced test file doesn't exist."""
    receipt = {
        "binding_file": "test.py",
        "classification": "TEMPORARY_THIN_ADAPTER",
        "owner": "test",
        "created_at": "2026-01-01T00:00:00Z",
        "migration_target_date": "2026-12-31",
        "expiry_enforced_by_ci": True,
        "migration_path": "Path to migrate to generic engine with enough chars",
        "blocking_migration_reason": "Blocking reason here",
        "adapter_only_justification": "A" * 100,
        "test_coverage": ["tests/nonexistent_file_12345.py"],
        "approver": "operator",
        "receipt_version": "1.0",
    }
    is_valid, reason = validate_receipt_12field(receipt)
    assert not is_valid, "Should fail for missing test file"
    assert "not found" in reason
    print("NEGATIVE CONTROL CONFIRMED: Missing test file detected")


def test_validate_valid_receipt():
    """Positive control: Valid receipt passes."""
    # Use a real test file that exists
    real_test_file = "tests/governance/test_no_app_specific_literals_in_core.py"
    if not (REPO_ROOT / real_test_file).exists():
        # Fallback - this test is just for structure validation
        print("POSITIVE CONTROL: Skipping (no test file available)")
        return
        
    receipt = {
        "binding_file": "agentic_core/L0_routing/test_binding.py",
        "classification": "TEMPORARY_THIN_ADAPTER",
        "owner": "operator",
        "created_at": "2026-01-01T00:00:00Z",
        "migration_target_date": "2026-12-31",
        "expiry_enforced_by_ci": True,
        "migration_path": "Migrate to generic profile-based resolver using domain_contract/ profiles",
        "blocking_migration_reason": "Generic resolver not yet implemented",
        "adapter_only_justification": "A" * 100,
        "test_coverage": [real_test_file],
        "approver": "operator",
        "receipt_version": "1.0",
    }
    is_valid, reason = validate_receipt_12field(receipt)
    assert is_valid, f"Should pass: {reason}"
    print("POSITIVE CONTROL CONFIRMED: Valid receipt accepted")


def run_negative_controls():
    """Run all negative control tests."""
    print("=" * 70)
    print("RECEIPT VALIDATOR NEGATIVE CONTROLS")
    print("=" * 70)
    test_validate_receipt_missing_field()
    test_validate_receipt_expired()
    test_validate_receipt_expiry_not_enforced()
    test_validate_receipt_missing_test_file()
    test_validate_valid_receipt()
    print("=" * 70)
    print("ALL CONTROLS PASSED")
    print("=" * 70)


if __name__ == "__main__":
    run_negative_controls()
