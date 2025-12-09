#!/usr/bin/env python3
"""
Maps import paths to maintain clean resume generation architecture.

Ensures code organization supports efficient resume generation
and easier maintenance for future enhancements.
"""

# Import mapping for canonical structure enforcement
IMPORT_MAPPINGS = {
    # Infrastructure merge
    "infrastructure": "infra",
    
    # Agents decomposition
    "agents.planning": "l1",
    "agents.execution": "l2", 
    "agents.meta": "meta",
    
    # Layer migrations
    "state": "l4",
    "safety": "l5",
    
    # Utility migrations
    "cli": "tools",
    "prompts": "l1",
    "profiles": "config",
    "retrieval": "retrievers",
}

# Specific file mappings for conflicts resolved
FILE_MAPPINGS = {
    # agents/planning -> l1 (agents versions were larger/more complete)
    "agents.planning.qa_planning": "l1.qa_planning",
    "agents.planning.safety_planning": "l1.safety_planning", 
    "agents.planning.strategy_planning": "l1.strategy_planning",
    "agents.planning.kg_rag_fusion_planning": "l1.kg_rag_fusion_planning",
    "agents.planning.kg_retrieval_planning": "l1.kg_retrieval_planning",
    "agents.planning.rag_planning": "l1.rag_planning",
    "agents.planning.v6_prompt_adapter": "l1.v6_prompt_adapter",
    "agents.planning.vector_search_planning": "l1.vector_search_planning",
    "agents.planning.workflow_planning": "l1.workflow_planning",
    
    # agents/execution -> l2
    "agents.execution.execution": "l2.execution",
    "agents.execution.agents": "l2.agents",
    
    # state -> l4
    "state.entity_resolution": "l4.entity_resolution",
    "state.hybrid_search": "l4.hybrid_search", 
    "state.journal": "l4.journal",
    "state.manager": "l4.manager",
    "state.pinecone_adapter": "l4.pinecone_adapter",
    "state.state_validation": "l4.state_validation",
    "state.temporal_kg": "l4.temporal_kg",
    "state.temporal_schemas": "l4.temporal_schemas",
    "state.triplet_store": "l4.triplet_store",
    "state.types": "l4.types",
    
    # safety -> l5
    "safety.injection_detection": "l5.injection_detection",
    "safety.policy": "l5.policy",
    "safety.types": "l5.types",
    
    # cli -> tools
    "cli.main_v10_10": "tools.main_v10_10",
    "cli.run_batch_v10_10": "tools.run_batch_v10_10",
    
    # infrastructure -> infra (preserve substructure)
    "infrastructure.context_engine": "infra.context_engine",
    "infrastructure.control_plane": "infra.control_plane",
    "infrastructure.dag": "infra.dag",
    "infrastructure.dag_engine": "infra.dag_engine",
    "infrastructure.model_routing": "infra.model_routing",
    "infrastructure.reasoning": "infra.reasoning",
    "infrastructure.sandbox": "infra.sandbox",
    "infrastructure.storage": "infra.storage",
    "infrastructure.di_container": "infra.di_container",
}

def apply_import_mappings():
    """
    Applies import mappings to maintain clean code architecture.

    Ensures resume generation system remains properly structured
    for improved maintainability and easier enhancements.
    """
    import os
    import re
    
    updated_files = []
    
    # Walk through all Python files
    for root, dirs, files in os.walk('.'):
        # Skip __pycache__ and other cache directories
        if '__pycache__' in root or '.git' in root:
            continue
            
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    original_content = content
                    
                    # Apply module-level mappings
                    for old_module, new_module in IMPORT_MAPPINGS.items():
                        # Pattern: from old_module import
                        pattern = rf'from {old_module}\.'
                        content = re.sub(pattern, f'from {new_module}.', content)
                        
                        # Pattern: import old_module
                        pattern = rf'import {old_module}\.'
                        content = re.sub(pattern, f'import {new_module}.', content)
                    
                    # Apply specific file mappings
                    for old_import, new_import in FILE_MAPPINGS.items():
                        # Pattern: from old_import import
                        pattern = rf'from {old_import} '
                        content = re.sub(pattern, f'from {new_import} ', content)
                        
                        # Pattern: from old_import import
                        pattern = rf'from {old_import}$'
                        content = re.sub(pattern, f'from {new_import}', content, flags=re.MULTILINE)
                    
                    # Write back if changed
                    if content != original_content:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(content)
                        updated_files.append(filepath)
                        print(f"Updated imports in: {filepath}")
                        
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")
    
    print(f"\nTotal files updated: {len(updated_files)}")
    return updated_files

if __name__ == "__main__":
    print("Applying canonical structure import mappings...")
    updated_files = apply_import_mappings()
    print("Import mapping complete!")
