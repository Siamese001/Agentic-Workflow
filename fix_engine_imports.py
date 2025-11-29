#!/usr/bin/env python3
"""
Targeted import fix for engine restructuring.
Fixes imports that expect flat module paths but now have nested structure.
"""

import re
from pathlib import Path

# Mapping of expected flat imports to actual nested paths
IMPORT_MAPPING = {
    # L1 Planning imports - draft_planning modules
    'from agentic_core.l1_planning.draft_planning.lic_outreach_archetype_planning import': 
        'from agentic_core.l1_planning.draft_planning.lic_outreach_archetype_planning import',
    'from agentic_core.l1_planning.draft_planning.lic_outreach_dataclasses import': 
        'from agentic_core.l1_planning.draft_planning.lic_outreach_dataclasses import',
    'from agentic_core.l1_planning.draft_planning.lic_fusion_planner import': 
        'from agentic_core.l1_planning.draft_planning.lic_fusion_planner import',
    'from agentic_core.l1_planning.draft_planning.lic_grounding_planner import': 
        'from agentic_core.l1_planning.draft_planning.lic_grounding_planner import',
    'from agentic_core.l1_planning.draft_planning.lic_persona_planner import': 
        'from agentic_core.l1_planning.draft_planning.lic_persona_planner import',
    'from agentic_core.l1_planning.draft_planning.lic_profile_planner import': 
        'from agentic_core.l1_planning.draft_planning.lic_profile_planner import',
    'from agentic_core.l1_planning.draft_planning.lic_research_planner import': 
        'from agentic_core.l1_planning.draft_planning.lic_research_planner import',
    'from agentic_core.l1_planning.draft_planning.lic_message_planning import': 
        'from agentic_core.l1_planning.draft_planning.lic_message_planning import',
    'from agentic_core.l1_planning.draft_planning.lic_draft_planning import': 
        'from agentic_core.l1_planning.draft_planning.lic_draft_planning import',
    'from agentic_core.l1_planning.draft_planning.lic_plan_schema import': 
        'from agentic_core.l1_planning.draft_planning.lic_plan_schema import',
    'from agentic_core.l1_planning.draft_planning.lic_planner import': 
        'from agentic_core.l1_planning.draft_planning.lic_planner import',
    'from agentic_core.l1_planning.draft_planning.lic_prompt_builder import': 
        'from agentic_core.l1_planning.draft_planning.lic_prompt_builder import',
    'from agentic_core.l1_planning.draft_planning.lic_prompt_system_v10_10 import': 
        'from agentic_core.l1_planning.draft_planning.lic_prompt_system_v10_10 import',
    'from agentic_core.l1_planning.draft_planning.lic_instructional_injection_v6 import': 
        'from agentic_core.l1_planning.draft_planning.lic_instructional_injection_v6 import',
    'from agentic_core.l1_planning.draft_planning.lic_many_shot_examples import': 
        'from agentic_core.l1_planning.draft_planning.lic_many_shot_examples import',
    
    # L1 Planning imports - rag_planning modules
    'from agentic_core.l1_planning.rag_planning.lic_kg_rag_fusion_planning import': 
        'from agentic_core.l1_planning.rag_planning.lic_kg_rag_fusion_planning import',
    'from agentic_core.l1_planning.rag_planning.lic_kg_retrieval_planning import': 
        'from agentic_core.l1_planning.rag_planning.lic_kg_retrieval_planning import',
    
    # L1 Planning imports - strategy_planning modules
    'from agentic_core.l1_planning.strategy_planning.persona_planning.lic_persona_planner import': 
        'from agentic_core.l1_planning.strategy_planning.persona_planning.lic_persona_planner import',
    
    # L2 Execution imports (K nodes)
    'from agentic_core.l2_execution.engines.outreach.lic_k1_research import': 
        'from agentic_core.l2_execution.engines.outreach.lic_k1_research import',
    'from agentic_core.l2_execution.engines.outreach.lic_k2_insights import': 
        'from agentic_core.l2_execution.engines.outreach.lic_k2_insights import',
    'from agentic_core.l2_execution.engines.outreach.lic_k3_draft import': 
        'from agentic_core.l2_execution.engines.outreach.lic_k3_draft import',
    'from agentic_core.l2_execution.engines.outreach.lic_k4_regen import': 
        'from agentic_core.l2_execution.engines.outreach.lic_k4_regen import',
    'from agentic_core.l2_execution.engines.outreach.lic_k5_validation import': 
        'from agentic_core.l2_execution.engines.outreach.lic_k5_validation import',
    'from agentic_core.l2_execution.engines.outreach.lic_k6_cta import': 
        'from agentic_core.l2_execution.engines.outreach.lic_k6_cta import',
    'from agentic_core.l2_execution.engines.outreach.lic_k7_assembly import': 
        'from agentic_core.l2_execution.engines.outreach.lic_k7_assembly import',
    
    # L2 Execution imports - RG modules
    'from agentic_core.l2_execution.engines.resume.rg_k1_extract import': 
        'from agentic_core.l2_execution.engines.resume.rg_k1_extract import',
    'from agentic_core.l2_execution.engines.resume.rg_k2_clean import': 
        'from agentic_core.l2_execution.engines.resume.rg_k2_clean import',
    'from agentic_core.l2_execution.engines.resume.rg_k3_quantify import': 
        'from agentic_core.l2_execution.engines.resume.rg_k3_quantify import',
    'from agentic_core.l2_execution.engines.resume.rg_k4_rewrite import': 
        'from agentic_core.l2_execution.engines.resume.rg_k4_rewrite import',
    'from agentic_core.l2_execution.engines.resume.rg_k5_skillmap import': 
        'from agentic_core.l2_execution.engines.resume.rg_k5_skillmap import',
    'from agentic_core.l2_execution.engines.resume.rg_k6_assemble import': 
        'from agentic_core.l2_execution.engines.resume.rg_k6_assemble import',
    'from agentic_core.l2_execution.engines.resume.rg_k7_format import': 
        'from agentic_core.l2_execution.engines.resume.rg_k7_format import',
    'from agentic_core.l2_execution.engines.resume.rg_k8_validate import': 
        'from agentic_core.l2_execution.engines.resume.rg_k8_validate import',
    
    # L3 Orchestration imports
    'from agentic_core.l3_orchestration.draft_orchestration.lic_orchestrator import': 
        'from agentic_core.l3_orchestration.draft_orchestration.lic_orchestrator import',
    'from agentic_core.l3_orchestration.draft_orchestration.lic_enhanced_orchestrator import': 
        'from agentic_core.l3_orchestration.draft_orchestration.lic_enhanced_orchestrator import',
    'from agentic_core.l3_orchestration.agent_orchestration.lic_outreach_factory import': 
        'from agentic_core.l3_orchestration.agent_orchestration.lic_outreach_factory import',
    'from agentic_core.l3_orchestration.agent_orchestration.lic_outreach_orchestrator import': 
        'from agentic_core.l3_orchestration.agent_orchestration.lic_outreach_orchestrator import',
    
    # L4 State imports (memory -> state rename)
    'from agentic_core.l4_memory_state.': 'from agentic_core.l4_memory_state.',
    'import agentic_core.l4_memory_state.': 'import agentic_core.l4_memory_state.',
    
    # L5 Safety imports
    'from agentic_core.l5_safety.lic_': 'from agentic_core.l5_safety.safety_validator.safety_validator.lic_',
    'from agentic_core.l5_safety.safety_validator.safety_validator.safety_validator.safety_': 'from agentic_core.l5_safety.safety_validator.safety_validator.safety_validator.safety_',
}

def fix_imports_in_file(file_path):
    """Fix imports in a single file using both explicit mappings and regex patterns."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply all explicit import mappings first
        for old_import, new_import in IMPORT_MAPPING.items():
            content = content.replace(old_import, new_import)
        
        # Apply regex-based patterns for systematic fixes
        patterns = [
            # L1 Planning - missing modules
            (r'from engine\.l1_planning\.(\w+) import', r'from agentic_core.l1_planning.draft_planning.lic_\1 import'),
            (r'from engine\.l1_planning\.(\w+)_planning import', r'from agentic_core.l1_planning.draft_planning.lic_\1_planning import'),
            
            # L2 Execution - K nodes directly under l2_execution
            (r'from engine\.l2_execution\.lic_(k\d+_\w+) import', r'from agentic_core.l2_execution.engines.outreach.lic_\1 import'),
            (r'from engine\.l2_execution\.(\w+) import', r'from agentic_core.l2_execution.engines.outreach.lic_\1 import'),
            
            # L2 Execution - RG modules
            (r'from engine\.l2_execution\.rg_(k\d+_\w+) import', r'from agentic_core.l2_execution.engines.resume.rg_\1 import'),
            
            # L3 Orchestration
            (r'from engine\.l3_orchestration\.lic_(\w+) import', r'from agentic_core.l3_orchestration.draft_orchestration.lic_\1 import'),
            (r'from engine\.l3_orchestration\.(\w+)_orchestrator import', r'from agentic_core.l3_orchestration.agent_orchestration.lic_\1_orchestrator import'),
            
            # L4 State - temporal modules
            (r'from engine\.l4_state\.(\w+_\w+) import', r'from agentic_core.l4_memory_state.temporal.\1 import'),
            (r'from engine\.l4_state\.(\w+) import', r'from agentic_core.l4_memory_state.providers.\1 import'),
            
            # L5 Safety
            (r'from engine\.l5_safety\.lic_(\w+) import', r'from agentic_core.l5_safety.safety_validator.lic_\1 import'),
            (r'from engine\.l5_safety\.(\w+) import', r'from agentic_core.l5_safety.safety_policy.\1 import'),
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
        
        # Write back if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Process all Python files in the repository."""
    repo_root = Path('.')
    files_processed = 0
    files_updated = 0
    
    print("Starting targeted engine import fix...")
    
    # Process all Python files
    for py_file in repo_root.rglob('*.py'):
        # Skip .venv and __pycache__
        if '.venv' in str(py_file) or '__pycache__' in str(py_file):
            continue
            
        files_processed += 1
        if fix_imports_in_file(py_file):
            files_updated += 1
            print(f"Fixed: {py_file}")
    
    print(f"\nSummary:")
    print(f"Files processed: {files_processed}")
    print(f"Files updated: {files_updated}")

if __name__ == "__main__":
    main()
