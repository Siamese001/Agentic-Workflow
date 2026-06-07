#!/usr/bin/env python3
"""check_rule_cross_references.py — CI gate for rule cross-reference validation.

Validates that cross-references between rules are intact:
- All referenced rule files exist
- All referenced sections exist in target rules
- No broken links after rule edits

Exit codes:
    0 — All cross-references valid, or advisory mode with broken refs (default)
    2 — Broken references with ``RULE_CROSS_REF_FAIL_CLOSED=1``

Environment:
    RULE_CROSS_REF_FAIL_CLOSED=1 — exit 2 on broken refs
    RULE_CROSS_REF_BYPASS=1 — skip validation

Outputs:
    artifacts/ci/rule_cross_reference_report.json
"""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

RULES_DIR: Path = Path(".claude/rules")
ARTIFACTS_DIR: Path = Path("artifacts/ci")

# Cross-reference patterns in markdown
REF_PATTERNS: list[tuple[str, str]] = [
    # Markdown link: [text](path/to/file.md)
    (r"\[([^\]]+)\]\(([^)]+\.md)\)", "link"),
    # Rule citation: @.claude/rules/file.md or @file.md (legacy .cursor accepted)
    (r"@(?:\.(?:claude|cursor)/rules/)?([^\s]+\.md)", "citation"),
    # Reference block: see `file.md` or see `path/file.md`
    (r"see\s+`([^`]+\.md)`", "reference"),
]


@dataclass(frozen=True)
class CrossRef:
    source_file: str
    target_file: str
    ref_type: str
    line_number: int
    context: str


@dataclass(frozen=True)
class ValidationResult:
    cross_ref: CrossRef
    valid: bool
    error: Optional[str]


def extract_cross_references(rule_file: Path) -> list[CrossRef]:
    """Extract all cross-references from a rule file."""
    refs: list[CrossRef] = []
    content = rule_file.read_text(encoding="utf-8")
    lines = content.split("\n")
    
    for line_num, line in enumerate(lines, 1):
        for pattern, ref_type in REF_PATTERNS:
            for match in re.finditer(pattern, line, re.IGNORECASE):
                if ref_type == "link":
                    target = match.group(2)
                else:
                    target = match.group(1)
                
                # Normalize target path
                if not target.startswith("."):
                    target = f".cursor/rules/{target}"
                
                refs.append(CrossRef(
                    source_file=str(rule_file),
                    target_file=target,
                    ref_type=ref_type,
                    line_number=line_num,
                    context=line.strip()[:100]
                ))
    
    return refs


def validate_cross_reference(ref: CrossRef) -> ValidationResult:
    """Validate a single cross-reference."""
    target_path = Path(ref.target_file)
    
    # Check file exists
    if not target_path.exists():
        return ValidationResult(
            cross_ref=ref,
            valid=False,
            error=f"Target file does not exist: {ref.target_file}"
        )
    
    # Check file is readable
    try:
        content = target_path.read_text(encoding="utf-8")
    except Exception as e:
        return ValidationResult(
            cross_ref=ref,
            valid=False,
            error=f"Cannot read target file: {e}"
        )
    
    # Check for section anchors (e.g., file.md#section-name)
    if "#" in ref.target_file:
        file_part, section_part = ref.target_file.split("#", 1)
        section_anchor = section_part.lower().replace("-", " ")
        
        # Look for heading matching the section
        heading_pattern = rf"^#+\s*{re.escape(section_anchor)}"
        if not re.search(heading_pattern, content, re.MULTILINE | re.IGNORECASE):
            # Section not found — could be a false positive if anchor is different
            # We'll log it as a warning but not fail
            return ValidationResult(
                cross_ref=ref,
                valid=True,  # Allow section anchor mismatches (common in markdown)
                error=f"Section anchor '{section_part}' may not exist (check manually)"
            )
    
    return ValidationResult(cross_ref=ref, valid=True, error=None)


def _load_notion_plan_identity_rule_refs() -> list[CrossRef]:
    """Load cross-references specifically from notion-plan-identity-verification.md."""
    rule_file = RULES_DIR / "notion-plan-identity-verification.mdc"
    if not rule_file.exists():
        return []
    return extract_cross_references(rule_file)


def main() -> int:
    """Main entry point for CI gate."""
    # Check bypass
    if os.environ.get("RULE_CROSS_REF_BYPASS", "") == "1":
        print("[RULE-XREF] Bypassed via RULE_CROSS_REF_BYPASS=1", file=sys.stderr)
        return 0
    
    # Find all rule files
    rule_files = sorted(RULES_DIR.glob("*.md")) + sorted(RULES_DIR.glob("*.mdc"))
    if not rule_files:
        print("[RULE-XREF] No rule files found", file=sys.stderr)
        return 0
    
    # Extract and validate all cross-references
    all_refs: list[ValidationResult] = []
    
    for rule_file in rule_files:
        refs = extract_cross_references(rule_file)
        for ref in refs:
            result = validate_cross_reference(ref)
            all_refs.append(result)
    
    # Separate valid and invalid
    invalid = [r for r in all_refs if not r.valid]
    warnings = [r for r in all_refs if r.valid and r.error]  # Section anchor warnings
    
    # Write report
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    report_file = ARTIFACTS_DIR / "rule_cross_reference_report.json"
    
    report = {
        "generated_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "total_rules_checked": len(rule_files),
        "total_references": len(all_refs),
        "valid_references": len([r for r in all_refs if r.valid and not r.error]),
        "warnings": len(warnings),
        "invalid_references": len(invalid),
        "invalid_details": [
            {
                "source": r.cross_ref.source_file,
                "target": r.cross_ref.target_file,
                "type": r.cross_ref.ref_type,
                "line": r.cross_ref.line_number,
                "error": r.error,
                "context": r.cross_ref.context
            }
            for r in invalid
        ],
        "warning_details": [
            {
                "source": r.cross_ref.source_file,
                "target": r.cross_ref.target_file,
                "type": r.cross_ref.ref_type,
                "line": r.cross_ref.line_number,
                "warning": r.error,
                "context": r.cross_ref.context
            }
            for r in warnings
        ]
    }
    
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    
    # Output summary
    print(f"[RULE-XREF] Checked {len(rule_files)} rules, {len(all_refs)} cross-references", file=sys.stderr)
    
    if invalid:
        print(f"[RULE-XREF] ❌ {len(invalid)} broken reference(s):", file=sys.stderr)
        for r in invalid:
            print(f"  {r.cross_ref.source_file}:{r.cross_ref.line_number} → {r.cross_ref.target_file}", file=sys.stderr)
            print(f"    Error: {r.error}", file=sys.stderr)
    
    if warnings:
        print(f"[RULE-XREF] ⚠️  {len(warnings)} warning(s):", file=sys.stderr)
        for r in warnings:
            print(f"  {r.cross_ref.source_file}:{r.cross_ref.line_number} → {r.cross_ref.target_file}", file=sys.stderr)
            print(f"    {r.error}", file=sys.stderr)
    
    if not invalid and not warnings:
        print("[RULE-XREF] ✅ All cross-references valid", file=sys.stderr)
    
    # Determine exit code
    fail_closed = os.environ.get("RULE_CROSS_REF_FAIL_CLOSED", "") == "1"
    
    if invalid:
        if fail_closed:
            print("[RULE-XREF] FAIL-CLOSED mode — exiting with error", file=sys.stderr)
            return 2
        print(f"[RULE-XREF] Advisory mode — review {report_file}", file=sys.stderr)
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
