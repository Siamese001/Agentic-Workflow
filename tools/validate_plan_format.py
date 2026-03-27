#!/usr/bin/env python3
"""
Windsurf Plan Format Validator
Enforces plan structure compliance with Windsurf guidelines.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# Plan structure requirements
REQUIRED_SECTIONS = [
    "## Wave Structure",
    "## Rules",
    "## Success Criteria"
]

WAVE_TABLE_PATTERN = r"\| Waves \| Metric \| Scope \| Checkpoint \|(\s*\| Tokens \|)?"

def validate_plan_format(plan_path: str) -> Dict[str, Any]:
    """Validate plan follows Windsurf format requirements."""
    
    with open(plan_path, 'r') as f:
        content = f.read()
    
    issues = []
    warnings = []
    
    # Check for required sections
    for section in REQUIRED_SECTIONS:
        if section not in content:
            issues.append(f"Missing required section: {section}")
    
    # Check wave table at top (after title, before other sections)
    lines = content.split('\n')
    wave_table_found = False
    wave_table_line = None
    
    for i, line in enumerate(lines):
        if line.startswith("## Wave Structure"):
            # Look for table in next 10 lines
            for j in range(i+1, min(i+11, len(lines))):
                if re.match(WAVE_TABLE_PATTERN, lines[j]):
                    wave_table_found = True
                    wave_table_line = j+1
                    break
            break
    
    if not wave_table_found:
        issues.append("Wave table not found after '## Wave Structure' section")
        issues.append(f"Expected pattern: | Waves | Metric | Scope | Checkpoint | [Tokens |]")
    
    # Check for token estimates in wave table
    if wave_table_line:
        # Look for token values in table rows (skip header)
        token_found = False
        for j in range(wave_table_line + 2, min(wave_table_line+15, len(lines))):  # Skip header and separator
            if '|' in lines[j] and any(char.isdigit() for char in lines[j]):
                # Check if this looks like a data row with tokens
                row = lines[j]
                if 'Wave' in row or any(x in row.lower() for x in ['k', 'm', 'token']):
                    token_found = True
                    break
        
        if not token_found:
            warnings.append("No token estimates found in wave table")
    
    # Check for evidence/documentation
    if "### Evidence" not in content and "### Target" not in content:
        warnings.append("No evidence or target sections found")
    
    # Check for implementation details
    if "## Implementation Commands" not in content:
        warnings.append("No implementation commands section")
    
    # Check for rollback strategy
    if "## Rollback Strategy" not in content:
        warnings.append("No rollback strategy section")
    
    # Check for ADG impact (if relevant)
    if "dependency" in content.lower() and "## ADG Impact" not in content:
        warnings.append("Consider adding ADG Impact section for dependency changes")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "wave_table_found": wave_table_found,
        "wave_table_line": wave_table_line
    }

def test_plan_validator():
    """Test the plan validator against known good/bad examples."""
    
    print("=== Testing Plan Validator ===\n")
    
    # Test 1: Check existing plan format
    existing_plan = "docs/reports/plans/convergent_wave_plan_101_150.md"
    if os.path.exists(existing_plan):
        print(f"Testing existing plan: {existing_plan}")
        result = validate_plan_format(existing_plan)
        print(f"Valid: {result['valid']}")
        if result['issues']:
            print("Issues:")
            for issue in result['issues']:
                print(f"  - {issue}")
        if result['warnings']:
            print("Warnings:")
            for warning in result['warnings']:
                print(f"  - {warning}")
        print()
    
    # Test 2: Check the problematic plan I created
    problematic_plan = "C:/Users/amita/.windsurf/plans/dependency-reclassification-swe15-format-2b3c4d.md"
    if os.path.exists(problematic_plan):
        print(f"Testing problematic plan: {problematic_plan}")
        result = validate_plan_format(problematic_plan)
        print(f"Valid: {result['valid']}")
        if result['issues']:
            print("Issues:")
            for issue in result['issues']:
                print(f"  - {issue}")
        if result['warnings']:
            print("Warnings:")
            for warning in result['warnings']:
                print(f"  - {warning}")
        print()
    
    # Test 3: Create a minimal valid plan to test validator
    test_plan_content = """# Test Plan

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Test metric | Test scope | A | 10,000 |

## Rules
- Test rule 1
- Test rule 2

## Success Criteria
- [ ] Criteria 1
- [ ] Criteria 2
"""
    
    test_plan_path = "test_plan.md"
    with open(test_plan_path, 'w') as f:
        f.write(test_plan_content)
    
    print("Testing minimal valid plan")
    result = validate_plan_format(test_plan_path)
    print(f"Valid: {result['valid']}")
    if result['issues']:
        print("Issues:")
        for issue in result['issues']:
            print(f"  - {issue}")
    if result['warnings']:
        print("Warnings:")
        for warning in result['warnings']:
            print(f"  - {warning}")
    
    # Cleanup
    os.remove(test_plan_path)
    
    print("\n=== Plan Validator Test Complete ===")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Validate specific plan
        plan_path = sys.argv[1]
        result = validate_plan_format(plan_path)
        
        print(f"Plan: {plan_path}")
        print(f"Valid: {result['valid']}")
        
        if result['issues']:
            print("\n❌ Issues:")
            for issue in result['issues']:
                print(f"  - {issue}")
        
        if result['warnings']:
            print("\n⚠️  Warnings:")
            for warning in result['warnings']:
                print(f"  - {warning}")
        
        if result['valid']:
            print("\n✅ Plan format is valid!")
            sys.exit(0)
        else:
            print("\n❌ Plan format validation failed!")
            sys.exit(1)
    else:
        # Run tests
        test_plan_validator()
