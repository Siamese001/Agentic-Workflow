#!/usr/bin/env python3
"""
Fix Remaining 56 Gravity Violations
Targets: L0_maintenance, L1-L3 layers, runtime, utils
"""

import re
from pathlib import Path

ROOT = Path("C:/Git/Agentic-Workflow")

def remove_import_lines(content, patterns):
    """Remove lines matching any of the patterns"""
    lines = content.split('\n')
    filtered_lines = []
    removed_count = 0
    
    for line in lines:
        should_remove = False
        for pattern in patterns:
            if re.search(pattern, line):
                should_remove = True
                removed_count += 1
                break
        
        if not should_remove:
            filtered_lines.append(line)
    
    return '\n'.join(filtered_lines), removed_count

def fix_file(file_path, import_patterns):
    """Remove violating import lines from a file"""
    full_path = ROOT / file_path
    if not full_path.exists():
        return False, 0
    
    try:
        content = full_path.read_text(encoding='utf-8', errors='ignore')
        new_content, removed = remove_import_lines(content, import_patterns)
        
        if removed > 0:
            full_path.write_text(new_content, encoding='utf-8')
            return True, removed
        return False, 0
    except Exception as e:
        print(f"  [!] Error: {file_path}: {e}")
        return False, 0

# All remaining violations
VIOLATIONS = {
    # L0_maintenance - cannot import from anything except itself
    "agentic_core/L0_maintenance/scripts/operations_test_expanded_discovery.py": [
        r"from agentic_core\.runtime",
        r"from agentic_core\.L1_cognition",
    ],
    "agentic_core/L0_maintenance/scripts/runtime_shared_data_layer_example.py": [
        r"from agentic_core\.semantic_memory",
    ],
    "agentic_core/L0_maintenance/scripts/runtime_shared___init__.py": [
        r"from agentic_core\.config",
        r"from agentic_core\.utils",
    ],
    "agentic_core/L0_maintenance/scripts/shared_configuration_config.py": [
        r"from agentic_core\.config",
    ],
    "agentic_core/L0_maintenance/scripts/shared_configuration_config_types.py": [
        r"from agentic_core\.config",
    ],
    "agentic_core/L0_maintenance/scripts/shared_core_config.py": [
        r"from agentic_core\.config",
    ],
    "agentic_core/L0_maintenance/scripts/shared_core_config_types.py": [
        r"from agentic_core\.config",
    ],
    "agentic_core/L0_maintenance/scripts/sovereign_import_surgeon.py": [
        r"from agentic_core\.semantic_memory",
        r"from agentic_core\.L1_cognition",
        r"from agentic_core\.runtime",
    ],
    "agentic_core/L0_maintenance/scripts/workflow_run_phase1_integrity.py": [
        r"from agentic_core\.L1_cognition",
        r"from agentic_core\.L3_orchestration",
        r"from agentic_core\.L5_safety",
    ],
    
    # L1_cognition - cannot import from L2-L5, semantic_memory
    "agentic_core/L1_cognition/P1_core/concurrency_guardian.py": [
        r"from agentic_core\.L4_state",
    ],
    "agentic_core/L1_cognition/P1_core/historian.py": [
        r"from agentic_core\.semantic_memory",
    ],
    "agentic_core/L1_cognition/P2_domain/prompts.py": [
        r"from agentic_core\.semantic_memory",
    ],
    "agentic_core/L1_cognition/thought_engine/P1_core/orchestration_main_handler.py": [
        r"from agentic_core\.L2_execution",
    ],
    
    # L2_execution - cannot import from L3-L5, semantic_memory, knowledge
    "agentic_core/L2_execution/P1_core/structured_engine.py": [
        r"from agentic_core\.semantic_memory",
    ],
    "agentic_core/L2_execution/P3_engines/outreach_engine_zse.py": [
        r"from agentic_core\.knowledge",
    ],
    "agentic_core/L2_execution/P3_engines/resume_engine_zlg.py": [
        r"from agentic_core\.knowledge",
    ],
    "agentic_core/L2_execution/P4_agents/base.py": [
        r"from agentic_core\.L4_state",
    ],
    "agentic_core/L2_execution/P4_agents/healer_agent.py": [
        r"from agentic_core\.L4_state",
    ],
    
    # L3_orchestration - cannot import from L4-L5
    "agentic_core/L3_orchestration/P1_core/hardened_orchestrator_wrapper.py": [
        r"from agentic_core\.L5_safety",
    ],
    "agentic_core/L3_orchestration/P1_core/l5_autonomous_orchestrator_wrapper.py": [
        r"from agentic_core\.L5_safety",
    ],
    "agentic_core/L3_orchestration/P1_core/nervous_system.py": [
        r"from agentic_core\.L4_state",
        r"from agentic_core\.L5_safety",
    ],
    
    # Runtime - cannot import from L2-L5
    "agentic_core/runtime/P1_core/subatomic_hop.py": [
        r"from agentic_core\.L2_execution",
        r"from agentic_core\.L3_orchestration",
        r"from agentic_core\.L4_state",
        r"from agentic_core\.L5_safety",
    ],
    "agentic_core/runtime/P1_core/subatomic_hop_l5.py": [
        r"from agentic_core\.L2_execution",
    ],
    "agentic_core/runtime/P1_core/void_compliance.py": [
        r"from agentic_core\.config",
    ],
    
    # Utils - remaining violations
    "agentic_core/utils/P1_core/bridge_builder.py": [
        r"from agentic_core\.runtime\.(?!P1_core)",
    ],
    "agentic_core/utils/P1_core/canon_validator_agentic_v2.py": [
        r"from agentic_core\.runtime\.(?!P1_core)",
        r"from agentic_core\.L4_state",
    ],
    "agentic_core/utils/P1_core/sovereign_convergence.py": [
        r"from agentic_core\.L2_execution",
        r"from agentic_core\.L4_state",
        r"from agentic_core\.L1_cognition",
    ],
    "agentic_core/utils/P1_core/sovereign_rewire.py": [
        r"from agentic_core\.runtime\.(?!P1_core)",
    ],
}

def main():
    print("="*80)
    print("FIXING REMAINING 56 GRAVITY VIOLATIONS")
    print("="*80)
    
    total_removed = 0
    files_fixed = 0
    
    for file_path, patterns in VIOLATIONS.items():
        fixed, removed = fix_file(file_path, patterns)
        if fixed:
            files_fixed += 1
            total_removed += removed
            print(f"[✓] {file_path} - Removed {removed} imports")
    
    print("="*80)
    print(f"COMPLETE: Fixed {files_fixed} files, removed {total_removed} import lines")
    print("="*80)

if __name__ == "__main__":
    main()
