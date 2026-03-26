#!/usr/bin/env python3
"""Fix template test files with undefined function_name variables."""

import pathlib
import re
import sys

def fix_function_name_errors(file_path: pathlib.Path) -> bool:
    """Fix undefined function_name errors in template files."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern to find undefined function_name references
        original = content
        
        # Replace f"{function_name} should return a result" with generic messages
        content = re.sub(
            r'f"\{function_name\} should return a result"',
            '"function should return a result"',
            content
        )
        
        # Replace other function_name references
        content = re.sub(
            r'f"\{function_name\}([^"]*)"',
            r'"function\1"',
            content
        )
        
        # Replace undefined constants like AGENTIC_CORE_DIR, L0_ROUTING_DIR, etc.
        content = re.sub(
            r'AGENTIC_CORE_DIR',
            '"/path/to/agentic_core"',
            content
        )
        
        content = re.sub(
            r'L0_ROUTING_DIR',
            '"/path/to/L0_routing"',
            content
        )
        
        content = re.sub(
            r'L1_COGNITION_DIR',
            '"/path/to/L1_cognition"',
            content
        )
        
        # Write back if changed
        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
        
    except Exception as e:
        print(f"Error fixing {file_path}: {e}", file=sys.stderr)
        return False

def main():
    """Fix all template error files."""
    # List of files with function_name errors from pytest output
    error_files = [
        "tests/unit/agentic_core/L0_routing/engines/test___init___adg.py",
        "tests/unit/agentic_core/L0_routing/meta_control/test___init___adg.py",
        "tests/unit/agentic_core/L0_routing/reasoning/test___init___adg.py",
        "tests/unit/agentic_core/L0_routing/scripts/test___init___adg.py",
        "tests/unit/agentic_core/L0_routing/scripts/test_coverage_adg.py",
        "tests/unit/agentic_core/L0_routing/scripts/test_drift_adg.py",
        "tests/unit/agentic_core/L0_routing/seams/test_safety_kernel_seam.py",
        "tests/unit/agentic_core/L0_routing/seams/test_vigilance_seam_adg.py",
        "tests/unit/agentic_core/L0_routing/types/test___init___adg.py",
        "tests/unit/agentic_core/L0_routing/types/test_boundary_types_adg.py",
        "tests/unit/agentic_core/L0_routing/types/test_crypto_trust_types.py",
        "tests/unit/agentic_core/L0_routing/types/test_determinism_types.py",
        "tests/unit/agentic_core/L0_routing/types/test_governance_types.py",
        "tests/unit/agentic_core/L0_routing/types/test_routing_artifact_types.py",
        "tests/unit/agentic_core/L0_routing/utils/test___init___adg.py",
        "tests/unit/agentic_core/L2_execution/types/test_token_enforcement_types_adg.py",
        "tests/unit/test_brand_compliance_agent.py",
        "tests/unit/test_campaign_planner_agent.py",
        "tests/unit/test_content_quality_agent.py",
        "tests/unit/test_fact_check_agent.py",
        "tests/unit/test_gap_closure_architect_agent.py",
        "tests/unit/test_proactive_agent.py",
        "tests/unit/test_rg_reflection_agent.py",
        "tests/unit/test_rg_resume_orchestrator.py",
        "tests/unit/test_rg_strategic_planner_agent.py",
        "tests/unit/test_rg_template_optimizer_agent.py",
        "tests/unit/test_section_balance_agent.py",
    ]
    
    fixed_count = 0
    for file_path in error_files:
        path = pathlib.Path(file_path)
        if path.exists():
            if fix_function_name_errors(path):
                print(f"Fixed: {file_path}")
                fixed_count += 1
        else:
            print(f"Not found: {file_path}")
    
    print(f"\nFixed {fixed_count} files")

if __name__ == "__main__":
    main()
