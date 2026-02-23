#!/usr/bin/env python3
"""
Consistency check script for architectural hardening specifications.

Verifies:
1. Required SCOPE headers exist in each spec
2. L6 spec contains no "abort/escalate/block" verbs
3. trace_id format string is identical across L0 and UWG specs

Exit code: 0 on success, 1 on violations
"""

import re
import sys
from pathlib import Path


def check_scope_headers(spec_dir: Path) -> list[str]:
    """Verify all specs have SCOPE section."""
    violations = []

    spec_files = [
        "AUTHORITY_HIERARCHY_INVARIANTS.md",
        "DEGRADATION_MATRIX.md",
        "L0_DECOMPOSITION_SPEC.md",
        "REPLAY_DETERMINISM_RULES.md",
        "HEALER_RETRY_HARDENING_SPEC.md",
        "L6_DRIFT_SAFEGUARDS_SPEC.md",
        "UWG_ISOLATION_SPEC.md",
        "PTC_SCOPE_LOCK_SPEC.md",
        "POLICY_EPOCH_SPEC.md",
        "LATENCY_BUDGET_SLA_SPEC.md",
    ]

    for spec_file in spec_files:
        spec_path = spec_dir / spec_file

        if not spec_path.exists():
            violations.append(f"MISSING FILE: {spec_file}")
            continue

        content = spec_path.read_text(encoding="utf-8")

        # Check for SCOPE section (must appear near top, within first 500 chars)
        if "## SCOPE" not in content[:500]:
            violations.append(f"MISSING SCOPE HEADER: {spec_file}")

        # Verify SCOPE section has "Governs:" line
        scope_match = re.search(r"## SCOPE\s+Governs:\s*\*\*(.+?)\*\*", content, re.DOTALL)
        if not scope_match:
            violations.append(f"MALFORMED SCOPE SECTION: {spec_file} (missing 'Governs:' line)")

    return violations


def check_l6_non_blocking(spec_dir: Path) -> list[str]:
    """Verify L6 spec contains no abort/escalate/block verbs."""
    violations = []

    l6_files = [
        "L6_DRIFT_SAFEGUARDS_SPEC.md",
        "DEGRADATION_MATRIX.md",  # Check L6 section only
    ]

    forbidden_verbs = [
        r"\babort\b",
        r"\bescalate\b",
        r"\bblock\b",
        r"\breject\b",
        r"\bkill\b",
        r"\bhard reject\b",
    ]

    for spec_file in l6_files:
        spec_path = spec_dir / spec_file

        if not spec_path.exists():
            continue

        content = spec_path.read_text(encoding="utf-8")

        # For DEGRADATION_MATRIX.md, only check L6 section
        if spec_file == "DEGRADATION_MATRIX.md":
            l6_match = re.search(
                r"## L6 Observability Degradation(.+?)(?=##|\Z)", content, re.DOTALL | re.IGNORECASE
            )
            if l6_match:
                content = l6_match.group(1)
            else:
                violations.append(f"L6 SECTION NOT FOUND: {spec_file}")
                continue

        # Check for forbidden verbs (case-insensitive)
        for verb_pattern in forbidden_verbs:
            matches = re.findall(verb_pattern, content, re.IGNORECASE)
            if matches:
                violations.append(
                    f"L6 NON-BLOCKING VIOLATION: {spec_file} contains forbidden verb '{matches[0]}'"
                )

    return violations


def check_trace_id_format_consistency(spec_dir: Path) -> list[str]:
    """Verify trace_id format is identical across L0 and UWG specs."""
    violations = []

    l0_spec = spec_dir / "L0_DECOMPOSITION_SPEC.md"
    uwg_spec = spec_dir / "UWG_ISOLATION_SPEC.md"

    if not l0_spec.exists():
        violations.append("MISSING FILE: L0_DECOMPOSITION_SPEC.md")
        return violations

    if not uwg_spec.exists():
        violations.append("MISSING FILE: UWG_ISOLATION_SPEC.md")
        return violations

    l0_content = l0_spec.read_text(encoding="utf-8")
    uwg_content = uwg_spec.read_text(encoding="utf-8")

    # Extract UUIDv7 format definitions
    l0_format = extract_trace_id_format(l0_content)
    uwg_format = extract_trace_id_format(uwg_content)

    if not l0_format:
        violations.append("L0 TRACE_ID FORMAT NOT FOUND: L0_DECOMPOSITION_SPEC.md")

    if not uwg_format:
        violations.append("UWG TRACE_ID FORMAT NOT FOUND: UWG_ISOLATION_SPEC.md")

    if l0_format and uwg_format and l0_format != uwg_format:
        violations.append(f"TRACE_ID FORMAT MISMATCH:\n  L0:  {l0_format}\n  UWG: {uwg_format}")

    # Verify both mention UUIDv7
    if "UUIDv7" not in l0_content:
        violations.append("L0 SPEC MISSING UUIDv7 REFERENCE")

    if "UUIDv7" not in uwg_content:
        violations.append("UWG SPEC MISSING UUIDv7 REFERENCE")

    return violations


def extract_trace_id_format(content: str) -> str:
    """Extract trace_id format definition from spec content."""
    # Look for "Format: UUIDv7" pattern
    format_match = re.search(r"\*\*Format:\*\*\s+(.+?)(?:\n|$)", content, re.IGNORECASE)

    if format_match:
        return format_match.group(1).strip()

    return ""


def main() -> int:
    """Run all consistency checks."""
    spec_dir = Path(__file__).parent.parent / "specs" / "hardening"

    if not spec_dir.exists():
        print(f"ERROR: Spec directory not found: {spec_dir}")
        return 1

    print("Running spec consistency checks...")
    print(f"Spec directory: {spec_dir}")
    print()

    all_violations = []

    # Check 1: SCOPE headers
    print("[1/3] Checking SCOPE headers...")
    scope_violations = check_scope_headers(spec_dir)
    all_violations.extend(scope_violations)

    if scope_violations:
        for violation in scope_violations:
            print(f"  ❌ {violation}")
    else:
        print("  ✓ All specs have valid SCOPE headers")
    print()

    # Check 2: L6 non-blocking
    print("[2/3] Checking L6 non-blocking invariant...")
    l6_violations = check_l6_non_blocking(spec_dir)
    all_violations.extend(l6_violations)

    if l6_violations:
        for violation in l6_violations:
            print(f"  ❌ {violation}")
    else:
        print("  ✓ L6 specs comply with non-blocking invariant")
    print()

    # Check 3: trace_id format consistency
    print("[3/3] Checking trace_id format consistency...")
    trace_violations = check_trace_id_format_consistency(spec_dir)
    all_violations.extend(trace_violations)

    if trace_violations:
        for violation in trace_violations:
            print(f"  ❌ {violation}")
    else:
        print("  ✓ trace_id format is consistent across L0 and UWG specs")
    print()

    # Summary
    print("=" * 60)
    if all_violations:
        print(f"FAILED: {len(all_violations)} violation(s) detected")
        return 1
    else:
        print("SUCCESS: All consistency checks passed")
        return 0


if __name__ == "__main__":
    sys.exit(main())
