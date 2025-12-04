#!/usr/bin/env python3
"""
Updates import paths after reorganization for clean architecture.

Ensures resume generation system maintains proper structure
 for improved code organization and easier maintenance.
"""

from pathlib import Path

# Define the root directory
ROOT = Path(__file__).parent

# Define import mappings (old -> new) for the reorganized structure
IMPORT_MAPPINGS = {
    # L1 -> agents/planning
    "from l1.": "from l1.",
    "import l1.": "import l1.",
    "from workflow_planning import": "from l1.workflow_planning import",
    "import workflow_planning": "import l1.workflow_planning",
    "from strategy_planning import": "from l1.strategy_planning import",
    "import strategy_planning": "import l1.strategy_planning",
    "from safety_planning import": "from l1.safety_planning import",
    "import safety_planning": "import l1.safety_planning",
    "from rag_planning import": "from l1.rag_planning import",
    "import rag_planning": "import l1.rag_planning",
    "from qa_planning import": "from l1.qa_planning import",
    "import qa_planning": "import l1.qa_planning",
    "from kg_rag_fusion_planning import": "from l1.kg_rag_fusion_planning import",
    "import kg_rag_fusion_planning": "import l1.kg_rag_fusion_planning",
    "from kg_retrieval_planning import": "from l1.kg_retrieval_planning import",
    "import kg_retrieval_planning": "import l1.kg_retrieval_planning",
    "from vector_search_planning import": "from l1.vector_search_planning import",
    "import vector_search_planning": "import l1.vector_search_planning",
    
    # L2 -> agents/execution
    "from l2.": "from l2.",
    "import l2.": "import l2.",
    "from agents import": "from l2.agents import",
    "import agents": "import l2.agents",
    "from execution import": "from l2.execution import",
    "import execution": "import l2.execution",
    "from fusion_executor import": "from l2.fusion_executor import",
    "import fusion_executor": "import l2.fusion_executor",
    "from invalidation_executor import": "from l2.invalidation_executor import",
    "import invalidation_executor": "import l2.invalidation_executor",
    "from kg_retrieval_executor import": "from l2.kg_retrieval_executor import",
    "import kg_retrieval_executor": "import l2.kg_retrieval_executor",
    "from triplet_extraction_executor import": "from l2.triplet_extraction_executor import",
    "import triplet_extraction_executor": "import l2.triplet_extraction_executor",
    "from vector_search_executor import": "from l2.vector_search_executor import",
    "import vector_search_executor": "import l2.vector_search_executor",
    
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
    "from infra.": "from infra.",
    "import infra.": "import infra.",
    
    # L4 -> state
    "from l4.": "from l4.",
    "import l4.": "import l4.",
    
    # L5 -> safety
    "from l5.": "from l5.",
    "import l5.": "import l5.",
    
    # Meta -> agents/meta or prompts/builders
    "from meta.multi_agent import": "from meta.multi_agent import",
    "import multi_agent": "import meta.multi_agent",
    "from core.cognitive_agents import": "from meta.cognitive_agents import",
    "import cognitive_agents": "import meta.cognitive_agents",
    "from meta.prompt_builder import": "from l1.builders.prompt_builder import",
    "import prompt_builder": "import l1.builders.prompt_builder",
    
    # Storage files -> infrastructure/storage
    "from vector_store_chroma import": "from infra.storage.vector_store_chroma import",
    "import vector_store_chroma": "import infra.storage.vector_store_chroma",
    "from cache_redis import": "from infra.storage.cache_redis import",
    "import cache_redis": "import infra.storage.cache_redis",
    "from retrieval import": "from infra.storage.retrieval import",
    "import retrieval": "import infra.storage.retrieval",
    
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
    "from core.integration import": "from infra.integration import",
    "import integration": "import infra.integration",
    "from core.di_container import": "from infra.di_container import",
    "import di_container": "import infra.di_container",
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
