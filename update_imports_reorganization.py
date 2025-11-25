#!/usr/bin/env python3
"""
Update all imports after reorganization to OpenAI agentic architecture.
This script updates import statements to reflect the new capability-based folder structure.
"""

import os
from pathlib import Path

# Define the root directory
ROOT = Path(__file__).parent

# Define import mappings (old -> new) for the reorganized structure
IMPORT_MAPPINGS = {
    # L1 -> agents/planning
    "from l1.": "from agents.planning.",
    "import l1.": "import agents.planning.",
    "from workflow_planning import": "from agents.planning.workflow_planning import",
    "import workflow_planning": "import agents.planning.workflow_planning",
    "from strategy_planning import": "from agents.planning.strategy_planning import",
    "import strategy_planning": "import agents.planning.strategy_planning",
    "from safety_planning import": "from agents.planning.safety_planning import",
    "import safety_planning": "import agents.planning.safety_planning",
    "from rag_planning import": "from agents.planning.rag_planning import",
    "import rag_planning": "import agents.planning.rag_planning",
    "from qa_planning import": "from agents.planning.qa_planning import",
    "import qa_planning": "import agents.planning.qa_planning",
    "from kg_rag_fusion_planning import": "from agents.planning.kg_rag_fusion_planning import",
    "import kg_rag_fusion_planning": "import agents.planning.kg_rag_fusion_planning",
    "from kg_retrieval_planning import": "from agents.planning.kg_retrieval_planning import",
    "import kg_retrieval_planning": "import agents.planning.kg_retrieval_planning",
    "from vector_search_planning import": "from agents.planning.vector_search_planning import",
    "import vector_search_planning": "import agents.planning.vector_search_planning",
    
    # L2 -> agents/execution
    "from l2.": "from agents.execution.",
    "import l2.": "import agents.execution.",
    "from agents import": "from agents.execution.agents import",
    "import agents": "import agents.execution.agents",
    "from execution import": "from agents.execution.execution import",
    "import execution": "import agents.execution.execution",
    "from fusion_executor import": "from agents.execution.fusion_executor import",
    "import fusion_executor": "import agents.execution.fusion_executor",
    "from invalidation_executor import": "from agents.execution.invalidation_executor import",
    "import invalidation_executor": "import agents.execution.invalidation_executor",
    "from kg_retrieval_executor import": "from agents.execution.kg_retrieval_executor import",
    "import kg_retrieval_executor": "import agents.execution.kg_retrieval_executor",
    "from triplet_extraction_executor import": "from agents.execution.triplet_extraction_executor import",
    "import triplet_extraction_executor": "import agents.execution.triplet_extraction_executor",
    "from vector_search_executor import": "from agents.execution.vector_search_executor import",
    "import vector_search_executor": "import agents.execution.vector_search_executor",
    
    # L3 -> orchestration
    "from l3.": "from orchestration.",
    "import l3.": "import orchestration.",
    "from workflow_graph import": "from orchestration.workflow_graph import",
    "import workflow_graph": "import orchestration.workflow_graph",
    "from routing import": "from orchestration.routing import",
    "import routing": "import orchestration.routing",
    
    # Core orchestration -> orchestration
    "from core.agent_bus import": "from orchestration.agent_bus import",
    "import agent_bus": "import orchestration.agent_bus",
    "from core.agent_registry import": "from orchestration.agent_registry import",
    "import agent_registry": "import orchestration.agent_registry",
    "from core.orchestrator import": "from orchestration.orchestrator import",
    "import orchestrator": "import orchestration.orchestrator",
    "from core.workflow_context import": "from orchestration.workflow_context import",
    "import workflow_context": "import orchestration.workflow_context",
    "from core.workflow_engine import": "from orchestration.workflow_engine import",
    "import workflow_engine": "import orchestration.workflow_engine",
    
    # Infra -> infrastructure
    "from infra.": "from infrastructure.",
    "import infra.": "import infrastructure.",
    
    # L4 -> state
    "from l4.": "from state.",
    "import l4.": "import state.",
    
    # L5 -> safety
    "from l5.": "from safety.",
    "import l5.": "import safety.",
    
    # Meta -> agents/meta or prompts/builders
    "from meta.multi_agent import": "from agents.meta.multi_agent import",
    "import multi_agent": "import agents.meta.multi_agent",
    "from core.cognitive_agents import": "from agents.meta.cognitive_agents import",
    "import cognitive_agents": "import agents.meta.cognitive_agents",
    "from meta.prompt_builder import": "from prompts.builders.prompt_builder import",
    "import prompt_builder": "import prompts.builders.prompt_builder",
    
    # Storage files -> infrastructure/storage
    "from vector_store_chroma import": "from infrastructure.storage.vector_store_chroma import",
    "import vector_store_chroma": "import infrastructure.storage.vector_store_chroma",
    "from cache_redis import": "from infrastructure.storage.cache_redis import",
    "import cache_redis": "import infrastructure.storage.cache_redis",
    "from retrieval import": "from infrastructure.storage.retrieval import",
    "import retrieval": "import infrastructure.storage.retrieval",
    
    # Tools -> tools/
    "from runtime_utils import": "from tools.runtime_utils import",
    "import runtime_utils": "import tools.runtime_utils",
    "from golden_eval import": "from tools.golden_eval import",
    "import golden_eval": "import tools.golden_eval",
    "from simulation import": "from tools.simulation import",
    "import simulation": "import tools.simulation",
    "from registry import": "from tools.registry import",
    "import registry": "import tools.registry",
    
    # Core models (keep in core for now)
    "from core.models.": "from core.models.",
    "import core.models.": "import core.models.",
    
    # Core integration -> infrastructure
    "from core.integration import": "from infrastructure.integration import",
    "import integration": "import infrastructure.integration",
    "from core.di_container import": "from infrastructure.di_container import",
    "import di_container": "import infrastructure.di_container",
}

def fix_file(filepath: Path) -> bool:
    """Fix imports in a single file. Returns True if changes were made."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply all mappings
        for old_import, new_import in IMPORT_MAPPINGS.items():
            content = content.replace(old_import, new_import)
        
        # Write back if changed
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    """Fix all Python files in the repository."""
    changed_files = []
    
    # Walk through all Python files
    for filepath in ROOT.rglob("*.py"):
        # Skip this script itself and other scripts
        if filepath.name in ["update_imports_reorganization.py", "dependency_analyzer.py", "fix_imports.py"]:
            continue
        
        # Skip cache and generated directories
        if any(skip in str(filepath) for skip in ["__pycache__", ".pytest_cache", ".venv", ".git"]):
            continue
        
        if fix_file(filepath):
            changed_files.append(filepath.relative_to(ROOT))
    
    # Print summary
    if changed_files:
        print(f"Updated imports in {len(changed_files)} files:")
        for f in sorted(changed_files):
            print(f"  - {f}")
    else:
        print("No files needed import updates.")

if __name__ == "__main__":
    main()
