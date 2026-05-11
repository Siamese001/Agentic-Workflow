#!/usr/bin/env python3
"""
boundary_receipt_validator.py - Validate governance receipts against schema.

Validates boundary, migration, and customization receipts for required fields.

Exit codes:
  0 - All receipts valid
  1 - Warnings (minor issues)
  2 - Errors (missing required fields)
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Set, Optional, Any

# Configuration
REPO_ROOT = Path("C:\\Git\\Agentic-Workflow-FRESH")
GOVERNANCE_DIR = REPO_ROOT / "artifacts" / "governance"
RECEIPT_DIRS = {
    "boundary": GOVERNANCE_DIR / "boundary_receipts",
    "migration": GOVERNANCE_DIR / "migration_receipts",
    "customization": GOVERNANCE_DIR / "customization_receipts",
    "verification": GOVERNANCE_DIR / "verification_receipts",
}

# Required fields by receipt type
RECEIPT_SCHEMAS = {
    "boundary": {
        "required": [
            "receipt_version",
            "audit_id",
            "timestamp",
            "changed_files",
            "classifications",
            "outcome",
        ],
        "recommended": [
            "forbidden_literals_found",
            "receipts_verified",
            "action_required",
            "next_steps",
        ]
    },
    "migration": {
        "required": [
            "receipt_version",
            "binding_file",
            "classification",
            "migration_target",
            "target_location",
        ],
        "recommended": [
            "app_profile_refs",
            "expected_completion",
            "acceptance_criteria",
        ]
    },
    "customization": {
        "required": [
            "receipt_version",
            "app_name",
            "customization_type",
            "files_created",
            "package_digest",
        ],
        "recommended": [
            "files_modified",
            "tests_added",
            "boundary_audit",
            "known_gaps",
        ]
    },
    "verification": {
        "required": [
            "receipt_version",
            "verification_passed",
            "refs_status",
            "digest_valid",
        ],
        "recommended": [
            "schema_valid",
            "field_map_valid",
            "errors",
        ]
    }
}

# Classification categories that require remediation
DRIFTED_CLASSIFICATIONS = [
    "CORE_APP_SPECIFIC_LEAKAGE",
    "MIGRATION_REQUIRED",
]


def find_all_receipts() -> List[Path]:
    """Find all receipt files in governance directories."""
    receipts = []
    
    for receipt_type, receipt_dir in RECEIPT_DIRS.items():
        if receipt_dir.exists():
            for receipt_file in receipt_dir.glob("*.json"):
                receipts.append(receipt_file)
    
    # Also check root governance dir
    if GOVERNANCE_DIR.exists():
        for receipt_file in GOVERNANCE_DIR.glob("*_receipt.json"):
            receipts.append(receipt_file)
    
    return sorted(receipts)


def determine_receipt_type(receipt: Dict, filepath: Path) -> str:
    """Determine receipt type from content or path."""
    # Check explicit type field
    if "receipt_type" in receipt:
        return receipt["receipt_type"]
    
    # Infer from content
    if "audit_id" in receipt and "classifications" in receipt:
        return "boundary"
    if "binding_file" in receipt and "migration_target" in receipt:
        return "migration"
    if "app_name" in receipt and "customization_type" in receipt:
        return "customization"
    if "verification_passed" in receipt and "refs_status" in receipt:
        return "verification"
    
    # Infer from path
    path_str = str(filepath)
    if "boundary" in path_str:
        return "boundary"
    if "migration" in path_str:
        return "migration"
    if "customization" in path_str:
        return "customization"
    if "verification" in path_str:
        return "verification"
    
    return "unknown"


def validate_receipt(receipt: Dict, receipt_type: str, filepath: Path) -> Dict:
    """Validate a single receipt against its schema."""
    errors = []
    warnings = []
    
    schema = RECEIPT_SCHEMAS.get(receipt_type, {"required": [], "recommended": []})
    
    # Check required fields
    for field in schema.get("required", []):
        if field not in receipt:
            errors.append(f"Missing required field: {field}")
    
    # Check recommended fields
    for field in schema.get("recommended", []):
        if field not in receipt:
            warnings.append(f"Missing recommended field: {field}")
    
    # Type-specific validations
    if receipt_type == "boundary":
        # Check classifications exist
        classifications = receipt.get("classifications", {})
        if not classifications:
            errors.append("classifications is empty")
        
        # Check outcome is valid
        outcome = receipt.get("outcome", "")
        valid_outcomes = ["ALLOW", "ALLOW_WITH_GENERIC_REFACTOR", "BLOCK_MOVE_TO_APPS_CONFIG", "BLOCK_ROLLBACK_REQUIRED"]
        if outcome and outcome not in valid_outcomes:
            warnings.append(f"Unexpected outcome value: {outcome}")
        
        # Check for drifted classifications with remediation
        if isinstance(classifications, dict):
            for file_path, classification in classifications.items():
                if classification in DRIFTED_CLASSIFICATIONS:
                    # Should have remediation
                    if "remediation" not in receipt and "next_steps" not in receipt:
                        warnings.append(f"Drifted classification {classification} for {file_path} lacks remediation")
    
    elif receipt_type == "migration":
        # Check classification is valid
        classification = receipt.get("classification", "")
        valid_classifications = ["TEMPORARY_THIN_ADAPTER", "CORE_APP_SPECIFIC_LEAKAGE", "GENERIC_READY", "MIGRATION_REQUIRED"]
        if classification and classification not in valid_classifications:
            warnings.append(f"Unexpected classification: {classification}")
        
        # Check expected_completion is a valid date string
        completion = receipt.get("expected_completion", "")
        if completion and not re.match(r"\d{4}(-Q[1-4]|\-\d{2})?", completion):
            warnings.append(f"Unexpected completion format: {completion}")
    
    elif receipt_type == "customization":
        # Check app_name is valid
        app_name = receipt.get("app_name", "")
        if app_name and not re.match(r"^apps_\w+$", app_name):
            warnings.append(f"Unexpected app_name format: {app_name}")
        
        # Check package_digest format
        digest = receipt.get("package_digest", "")
        if digest and not digest.startswith("sha256:"):
            warnings.append(f"Digest should start with sha256: prefix")
    
    # Check timestamp format
    timestamp = receipt.get("timestamp", "")
    if timestamp:
        if not re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", timestamp):
            warnings.append(f"Timestamp not in ISO8601 format: {timestamp}")
    
    # Determine status
    if errors:
        status = "INVALID"
        severity = "ERROR"
    elif warnings:
        status = "VALID_WITH_WARNINGS"
        severity = "WARNING"
    else:
        status = "VALID"
        severity = "OK"
    
    return {
        "file": str(filepath),
        "receipt_type": receipt_type,
        "status": status,
        "severity": severity,
        "errors": errors,
        "warnings": warnings,
    }


def main():
    """Main entry point."""
    print("BOUNDARY_RECEIPT_VALIDATOR: Validating governance receipts...")
    
    # Find all receipts
    receipts = find_all_receipts()
    
    if not receipts:
        print("\nNo receipts found to validate.")
        print(f"Receipt directories: {list(RECEIPT_DIRS.values())}")
        sys.exit(0)
    
    print(f"\nFound {len(receipts)} receipt(s) to validate.")
    
    # Validate each receipt
    results = []
    errors = 0
    warnings = 0
    
    for receipt_path in receipts:
        try:
            with open(receipt_path, 'r', encoding='utf-8') as f:
                receipt = json.load(f)
        except json.JSONDecodeError as e:
            results.append({
                "file": str(receipt_path),
                "receipt_type": "unknown",
                "status": "PARSE_ERROR",
                "severity": "ERROR",
                "errors": [f"JSON parse error: {e}"],
                "warnings": [],
            })
            errors += 1
            continue
        except IOError as e:
            results.append({
                "file": str(receipt_path),
                "receipt_type": "unknown",
                "status": "READ_ERROR",
                "severity": "ERROR",
                "errors": [f"Cannot read file: {e}"],
                "warnings": [],
            })
            errors += 1
            continue
        
        receipt_type = determine_receipt_type(receipt, receipt_path)
        result = validate_receipt(receipt, receipt_type, receipt_path)
        results.append(result)
        
        if result["severity"] == "ERROR":
            errors += 1
        elif result["severity"] == "WARNING":
            warnings += 1
    
    # Generate output
    output = {
        "validator": "boundary_receipt_validator",
        "timestamp": str(Path(__file__).stat().st_mtime),
        "receipts_checked": len(receipts),
        "valid": len([r for r in results if r["status"] == "VALID"]),
        "valid_with_warnings": len([r for r in results if r["status"] == "VALID_WITH_WARNINGS"]),
        "invalid": len([r for r in results if r["status"] == "INVALID"]),
        "parse_errors": len([r for r in results if "PARSE" in r["status"] or "READ" in r["status"]]),
        "results": results,
    }
    
    # Print JSON output
    print(json.dumps(output, indent=2))
    
    # Print summary
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    print(f"Receipts checked: {output['receipts_checked']}")
    print(f"  Valid: {output['valid']}")
    print(f"  Valid with warnings: {output['valid_with_warnings']}")
    print(f"  Invalid: {output['invalid']}")
    print(f"  Parse/Read errors: {output['parse_errors']}")
    
    # Print issues
    if errors > 0 or warnings > 0:
        print("\n" + "="*60)
        print("ISSUES")
        print("="*60)
        
        for result in results:
            if result["severity"] in ["ERROR", "WARNING"]:
                print(f"\n[{result['severity']}] {result['file']}")
                print(f"  Type: {result['receipt_type']}, Status: {result['status']}")
                
                for error in result["errors"]:
                    print(f"  ERROR: {error}")
                
                for warning in result["warnings"]:
                    print(f"  WARNING: {warning}")
    
    # Determine exit code
    if errors > 0:
        print("\n" + "="*60)
        print("BOUNDARY_RECEIPT_VALIDATOR: Errors found.")
        print("Please fix receipt issues before proceeding.")
        print("="*60)
        sys.exit(2)
    elif warnings > 0:
        print("\n" + "="*60)
        print("BOUNDARY_RECEIPT_VALIDATOR: Warnings found.")
        print("Receipts are valid but have minor issues.")
        print("="*60)
        sys.exit(1)
    else:
        print("\n" + "="*60)
        print("BOUNDARY_RECEIPT_VALIDATOR: All receipts valid.")
        print("="*60)
        sys.exit(0)


if __name__ == "__main__":
    main()
