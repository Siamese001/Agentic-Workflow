#!/usr/bin/env python3
"""
Fix test imports to use agentic_core paths after migration.

This script updates test imports from old L1-L5 paths to new agentic_core paths.
"""

import re
from pathlib import Path

def update_test_imports():
    """Update test imports in all Python files under tests/ directory."""
    
    # Import mappings for test files - longest match first
    import_mappings = {
        # L1 specific subdirectories
        r'from l1\.rag_planning\.': 'from agentic_core.l1_planning.rag_planning.',
        r'from l1\.strategy_planning\.': 'from agentic_core.l1_planning.strategy_planning.',
        r'from l1\.safety_planning\.': 'from agentic_core.l1_planning.safety_planning.',
        r'from l1\.draft_planning\.': 'from agentic_core.l1_planning.draft_planning.',
        r'from l1\.': 'from agentic_core.l1_planning.',
        
        # L2 specific subdirectories  
        r'from l2\.kg\.': 'from agentic_core.l2_execution.rag_execution.kg.',
        r'from l2\.vector\.': 'from agentic_core.l2_execution.rag_execution.vector.',
        r'from l2\.tool_clients\.': 'from agentic_core.l2_execution.tool_clients.',
        r'from l2\.rag_execution\.': 'from agentic_core.l2_execution.rag_execution.',
        r'from l2\.draft_execution\.': 'from agentic_core.l2_execution.draft_execution.',
        r'from l2\.bullet_execution\.': 'from agentic_core.l2_execution.bullet_execution.',
        r'from l2\.mcp\.': 'from agentic_core.l2_execution.mcp.',
        r'from l2\.': 'from agentic_core.l2_execution.',
        
        # L3 specific subdirectories
        r'from l3\.rag_orchestration\.': 'from agentic_core.l3_orchestration.rag_orchestration.',
        r'from l3\.draft_orchestration\.': 'from agentic_core.l3_orchestration.draft_orchestration.',
        r'from l3\.agent_orchestration\.': 'from agentic_core.l3_orchestration.agent_orchestration.',
        r'from l3\.': 'from agentic_core.l3_orchestration.',
        
        # L4 specific subdirectories
        r'from l4\.temporal_agents\.': 'from agentic_core.l4_memory.temporal_agents.',
        r'from l4\.db_interface\.': 'from agentic_core.l4_memory.db_interface.',
        r'from l4\.chunker\.': 'from agentic_core.l4_memory.chunker.',
        r'from l4\.knowledge_graph\.': 'from agentic_core.l4_memory.knowledge_graph.',
        r'from l4\.embeddings\.': 'from agentic_core.l4_memory.embeddings.',
        r'from l4\.': 'from agentic_core.l4_memory.',
        
        # L5 specific subdirectories
        r'from l5\.safety_policy\.': 'from agentic_core.l5_safety.safety_policy.',
        r'from l5\.constitutional_engine\.': 'from agentic_core.l5_safety.constitutional_engine.',
        r'from l5\.safety_validator\.': 'from agentic_core.l5_safety.safety_validator.',
        r'from l5\.': 'from agentic_core.l5_safety.',
        
        # Import statements
        r'import l1\.rag_planning\.': 'import agentic_core.l1_planning.rag_planning.',
        r'import l1\.strategy_planning\.': 'import agentic_core.l1_planning.strategy_planning.',
        r'import l1\.safety_planning\.': 'import agentic_core.l1_planning.safety_planning.',
        r'import l1\.draft_planning\.': 'import agentic_core.l1_planning.draft_planning.',
        r'import l1\.': 'import agentic_core.l1_planning.',
        
        r'import l2\.kg\.': 'import agentic_core.l2_execution.rag_execution.kg.',
        r'import l2\.vector\.': 'import agentic_core.l2_execution.rag_execution.vector.',
        r'import l2\.tool_clients\.': 'import agentic_core.l2_execution.tool_clients.',
        r'import l2\.rag_execution\.': 'import agentic_core.l2_execution.rag_execution.',
        r'import l2\.draft_execution\.': 'import agentic_core.l2_execution.draft_execution.',
        r'import l2\.bullet_execution\.': 'import agentic_core.l2_execution.bullet_execution.',
        r'import l2\.mcp\.': 'import agentic_core.l2_execution.mcp.',
        r'import l2\.': 'import agentic_core.l2_execution.',
        
        r'import l3\.rag_orchestration\.': 'import agentic_core.l3_orchestration.rag_orchestration.',
        r'import l3\.draft_orchestration\.': 'import agentic_core.l3_orchestration.draft_orchestration.',
        r'import l3\.agent_orchestration\.': 'import agentic_core.l3_orchestration.agent_orchestration.',
        r'import l3\.': 'import agentic_core.l3_orchestration.',
        
        r'import l4\.temporal_agents\.': 'import agentic_core.l4_memory.temporal_agents.',
        r'import l4\.db_interface\.': 'import agentic_core.l4_memory.db_interface.',
        r'import l4\.chunker\.': 'import agentic_core.l4_memory.chunker.',
        r'import l4\.knowledge_graph\.': 'import agentic_core.l4_memory.knowledge_graph.',
        r'import l4\.embeddings\.': 'import agentic_core.l4_memory.embeddings.',
        r'import l4\.': 'import agentic_core.l4_memory.',
        
        r'import l5\.safety_policy\.': 'import agentic_core.l5_safety.safety_policy.',
        r'import l5\.constitutional_engine\.': 'import agentic_core.l5_safety.constitutional_engine.',
        r'import l5\.safety_validator\.': 'import agentic_core.l5_safety.safety_validator.',
        r'import l5\.': 'import agentic_core.l5_safety.',
        
        # Engine-specific imports that should now use agentic_core
        r'from apps\.outreach_engine\.l[1-5]': 'from agentic_core',
        r'from apps\.resume_engine\.l[1-5]': 'from agentic_core',
    }
    
    tests_dir = Path("tests")
    if not tests_dir.exists():
        print("tests/ directory not found!")
        return
    
    files_updated = 0
    files_processed = 0
    
    # Process all Python files in tests/
    for py_file in tests_dir.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue
            
        files_processed += 1
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Apply import mappings
            for pattern, replacement in import_mappings.items():
                content = re.sub(pattern, replacement, content)
            
            # Write back if changed
            if content != original_content:
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                files_updated += 1
                print(f"Updated: {py_file}")
                
        except Exception as e:
            print(f"Error processing {py_file}: {e}")
    
    print(f"\nSummary:")
    print(f"Files processed: {files_processed}")
    print(f"Files updated: {files_updated}")

if __name__ == "__main__":
    update_test_imports()
