#!/usr/bin/env python3
"""
GOV-4: Governance receipts valid (advisory)

Validates that all TEMPORARY_THIN_ADAPTER files in agentic_core have
proper migration receipts with all 12 required fields.

Exit codes:
  0 - PASS (all receipts valid or advisory mode with warnings)
  1 - WARN (advisory mode, receipt violations found)
  2 - FAIL (strict mode, receipt violations found or validation error)
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

# Configuration
ADVISORY_SUNSET = "2026-06-15"
BYPASS_VAR = "GOV_RECEIPTS_BYPASS"
RECEIPT_SCHEMA_VERSION = "1.0"

# 12 mandatory fields for TEMPORARY_THIN_ADAPTER receipts
REQUIRED_RECEIPT_FIELDS = [
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
]


def get_repo_root() -> Path:
    """Get repository root directory."""
    return Path(__file__).resolve().parents[2]


def get_enforcement_mode(cli_strict: bool) -> Tuple[bool, str]:
    """Returns (is_strict, reason_message)."""
    today = datetime.now().isoformat()[:10]

    # Check bypass env var first
    if os.environ.get(BYPASS_VAR):
        return False, f"BYPASS ACTIVE ({BYPASS_VAR}=1)"

    # After sunset, strict is default
    if today > ADVISORY_SUNSET:
        if cli_strict:
            return True, f"STRICT MODE (sunset {ADVISORY_SUNSET} passed, --strict flag)"
        return True, f"STRICT MODE (sunset {ADVISORY_SUNSET} enforced)"

    # Before sunset, advisory default unless --strict passed
    if cli_strict:
        return True, "Strict mode (CLI flag)"

    return False, f"Advisory mode (sunset {ADVISORY_SUNSET})"


def validate_receipt(receipt_path: Path) -> Tuple[bool, str]:
    """Validate a single receipt file."""
    try:
        with open(receipt_path, "r", encoding="utf-8") as f:
            receipt = json.load(f)
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"
    except Exception as e:
        return False, f"Read error: {e}"

    # Check all required fields present and non-empty
    for field in REQUIRED_RECEIPT_FIELDS:
        if field not in receipt:
            return False, f"Missing required field: {field}"
        if not receipt[field] and field != "expiry_enforced_by_ci":
            return False, f"Empty required field: {field}"

    # Validate classification
    if receipt["classification"] not in ALLOWED_CLASSIFICATIONS:
        return False, f"Invalid classification: {receipt['classification']}"

    # Validate expiry_enforced_by_ci is true (not just truthy)
    if receipt["expiry_enforced_by_ci"] is not True:
        return False, "expiry_enforced_by_ci must be true (boolean)"

    # Validate migration_target_date not expired
    target_date = receipt.get("migration_target_date")
    today = datetime.now().isoformat()[:10]
    if target_date and target_date < today:
        return False, f"EXPIRED: Migration target date {target_date} has passed"

    # Validate test_coverage is a non-empty list
    test_coverage = receipt.get("test_coverage", [])
    if not isinstance(test_coverage, list) or len(test_coverage) == 0:
        return False, "test_coverage must be a non-empty list"

    # Validate test files exist
    repo_root = get_repo_root()
    for test_path in test_coverage:
        full_path = repo_root / test_path
        if not full_path.exists():
            return False, f"Referenced test not found: {test_path}"

    # Validate migration_path has minimum length (20 chars)
    migration_path = receipt.get("migration_path", "")
    if len(migration_path) < 20:
        return False, "migration_path must be at least 20 characters"

    # Validate adapter_only_justification has minimum length (100 chars)
    justification = receipt.get("adapter_only_justification", "")
    if len(justification) < 100:
        return False, "adapter_only_justification must be at least 100 characters"

    return True, "Receipt valid"


def scan_receipts() -> Tuple[int, int, list]:
    """Scan all receipts and return (valid_count, invalid_count, errors)."""
    repo_root = get_repo_root()
    receipts_dir = repo_root / "artifacts" / "governance" / "migration_receipts"

    if not receipts_dir.exists():
        # No receipts yet - this is OK, will be created in W4
        return 0, 0, []

    valid_count = 0
    invalid_count = 0
    errors = []

    for receipt_file in receipts_dir.glob("*_receipt.json"):
        is_valid, message = validate_receipt(receipt_file)
        if is_valid:
            valid_count += 1
        else:
            invalid_count += 1
            errors.append(f"{receipt_file.name}: {message}")

    return valid_count, invalid_count, errors


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="GOV-4: Validate governance migration receipts"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail-closed mode (post-sunset, this is default)",
    )
    args = parser.parse_args()

    is_strict, mode_reason = get_enforcement_mode(args.strict)

    print(f"[GOV-4] Governance receipts valid")
    print(f"[GOV-4] Mode: {mode_reason}")

    # Scan receipts
    valid_count, invalid_count, errors = scan_receipts()

    total_count = valid_count + invalid_count

    if total_count == 0:
        # No receipts yet - this is expected in W1, will be addressed in W4
        print(f"[GOV-4] ⚠️  WARN: No migration receipts found (expected in W1, will be created in W4)")
        if is_strict:
            print(f"[GOV-4] ❌ FAIL: No receipts in strict mode")
            return 2
        return 0  # Advisory = non-blocking

    if invalid_count == 0:
        print(f"[GOV-4] ✅ PASS: All {valid_count} receipts valid")
        return 0

    # Invalid receipts found
    if is_strict:
        print(f"[GOV-4] ❌ FAIL: {invalid_count} of {total_count} receipts invalid in strict mode")
        for error in errors:
            print(f"[GOV-4]   - {error}")
        return 2
    else:
        print(f"[GOV-4] ⚠️  WARN: {invalid_count} of {total_count} receipts invalid ({mode_reason})")
        for error in errors:
            print(f"[GOV-4]   - {error}")
        return 0  # Advisory = non-blocking


if __name__ == "__main__":
    sys.exit(main())
