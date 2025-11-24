"""Fix all imports after reorganization to OpenAI agentic architecture."""

import os
import re
from pathlib import Path

# Define the root directory
ROOT = Path(__file__).parent

# Define import mappings (old -> new)
IMPORT_MAPPINGS = {
    "from workflow_graph import": "from l3.workflow_graph import",
    "import workflow_graph": "import l3.workflow_graph as workflow_graph",
    "from workflow_planning import": "from l1.workflow_planning import",
    "import workflow_planning": "import l1.workflow_planning as workflow_planning",
    "from routing import": "from meta.routing import",
    "import routing": "import meta.routing as routing",
    "from multi_agent import": "from meta.multi_agent import",
    "import multi_agent": "import meta.multi_agent as multi_agent",
    "from ranking import": "from meta.ranking import",
    "import ranking": "import meta.ranking as ranking",
    "from self_correction import": "from meta.self_correction import",
    "import self_correction": "import meta.self_correction as self_correction",
    "from prompt_builder import": "from meta.prompt_builder import",
    "import prompt_builder": "import meta.prompt_builder as prompt_builder",
    "from models import": "from core.models.models import",
    "import models": "import core.models.models as models",
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
        # Skip this script itself
        if filepath.name == "fix_imports.py":
            continue
        
        # Skip __pycache__ and other generated directories
        if "__pycache__" in str(filepath) or ".pytest_cache" in str(filepath):
            continue
        
        if fix_file(filepath):
            changed_files.append(filepath.relative_to(ROOT))
    
    # Print summary
    if changed_files:
        print(f"Fixed imports in {len(changed_files)} files:")
        for f in sorted(changed_files):
            print(f"  - {f}")
    else:
        print("No files needed import fixes.")

if __name__ == "__main__":
    main()
