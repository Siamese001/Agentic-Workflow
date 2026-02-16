#!/usr/bin/env python3
"""
Artifacts Governance Guard

Deterministic read-only scanner for artifacts/ directory governance.
Enforces retention rules, sensitive content detection, and inventory tracking.
"""

import json
import re
from pathlib import Path
from typing import Any


def is_forbidden_artifact_name(file_path: Path) -> bool:
    """Check if file has a forbidden artifact name."""
    forbidden_patterns = [".secrets.baseline", "forensic_discovery_output.json"]
    return any(pattern in str(file_path) for pattern in forbidden_patterns)


def scan_sensitive_content(file_path: Path) -> list[str]:
    """Scan file for sensitive content patterns."""
    sensitive_patterns = [
        r"(?i)api[_-]?key\s*[:=]",
        r"(?i)secret\s*[:=]",
        r"sk-[A-Za-z0-9]{20,}",
        r"xox[baprs]-[A-Za-z0-9-]{10,}",
    ]

    violations = []

    try:
        # Skip binary files and files > 2MB
        if file_path.stat().st_size > 2 * 1024 * 1024:
            return violations

        with open(file_path, encoding="utf-8", errors="ignore") as f:
            content = f.read()

        for pattern in sensitive_patterns:
            if re.search(pattern, content):
                violations.append(f"Sensitive pattern detected: {pattern}")

    except (UnicodeDecodeError, PermissionError, OSError):
        # Skip files that can't be read as text
        pass

    return violations


def scan_artifacts_directory(artifacts_path: Path) -> dict[str, Any]:
    """Scan artifacts directory for governance violations."""
    violations = []
    inventory = []
    files_scanned = 0

    # Use deterministic ordering
    all_files = sorted(artifacts_path.rglob("*"))

    for file_path in all_files:
        # Skip directories
        if file_path.is_dir():
            continue

        files_scanned += 1

        # Get relative path from artifacts/
        relative_path = file_path.relative_to(artifacts_path)
        file_size = file_path.stat().st_size
        file_ext = file_path.suffix.lower()

        # Check 1: Forbidden artifact names
        if is_forbidden_artifact_name(relative_path):
            violations.append(
                {
                    "file": str(relative_path),
                    "type": "forbidden_artifact_name",
                    "detail": f"Forbidden artifact name: {relative_path}",
                }
            )

        # Check 2: Sensitive content
        sensitive_violations = scan_sensitive_content(file_path)
        for violation in sensitive_violations:
            violations.append({"file": str(relative_path), "type": "sensitive_content", "detail": violation})

        # Build inventory entry
        inventory_item = {"file": str(relative_path), "bytes": file_size, "ext": file_ext}

        # Add oversize detail for files > 5MB (informational only)
        if file_size > 5 * 1024 * 1024:
            inventory_item["detail"] = "oversize"

        inventory.append(inventory_item)

    return {"files_scanned": files_scanned, "violations": violations, "inventory": inventory}


def main():
    """Main scanner execution."""
    # Get repository root and artifacts path
    root_path = Path(__file__).parent.parent.parent
    artifacts_path = root_path / "artifacts"

    if not artifacts_path.exists():
        print(f"Error: artifacts directory not found at {artifacts_path}")
        return 1

    print(f"Scanning artifacts directory: {artifacts_path}")

    # Scan for violations
    result = scan_artifacts_directory(artifacts_path)

    # Ensure output directory exists
    output_dir = root_path / "artifacts" / "governance"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write report
    report_path = output_dir / "artifacts_guard_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, sort_keys=True)

    print(f"Scan complete. Report written to: {report_path}")
    print(f"Files scanned: {result['files_scanned']}")
    print(f"Violations found: {len(result['violations'])}")

    # Print inventory summary
    oversize_count = sum(1 for item in result["inventory"] if item.get("detail") == "oversize")
    if oversize_count > 0:
        print(f"Oversize files (>5MB): {oversize_count}")

    if result["violations"]:
        print("ARTIFACTS GOVERNANCE VIOLATIONS DETECTED:")
        for violation in result["violations"]:
            print(f"  {violation['file']}: {violation['type']} - {violation['detail']}")
        return 1
    else:
        print("No artifacts governance violations found.")
        return 0


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
