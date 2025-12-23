import os
import re

# --- CONFIGURATION ---
PROJECT_ROOT = "C:/Git/Agentic-Workflow"

# The "Refactor Map" based on your audit
# Key: The old import string | Value: The new import string
IMPORT_REPLACEMENTS = {
    # Core Migrations
    r'from agentic_core.semantic_memory': 'from agentic_core.semantic_memory',
    r'import agentic_core.semantic_memory as semantic_memory': 'import agentic_core.semantic_memory as semantic_memory',
    r'from agentic_core.L1_cognition.thought_engine': 'from agentic_core.L1_cognition.thought_engine',
    r'from agentic_core\.L2_thought_nodes': 'from agentic_core.L1_cognition.thought_engine',
    
    # App Staging Migrations (The 50+ files)
    r'from apps_shared.P1_core import': 'from apps_shared.P1_core import',
    r'import apps_shared\.': 'import apps_shared.P1_core.P1_core.',
    r'from apps_lic.P1_core import': 'from apps_lic.P1_core import',
    r'from apps_rg.P1_core import': 'from apps_rg.P1_core import',
    
    # Common Typo fix in imports
    r'L0_maintenance': 'L0_maintenance'
}

def repair_imports(root_path):
    print(f"--- STARTING IMPORT REPAIR ---")
    
    for root, dirs, files in os.walk(root_path):
        # Skip junk
        if any(junk in root for junk in [".git", "__pycache__", "venv"]):
            continue
            
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                new_content = content
                changes_made = False
                
                for old_pattern, new_pattern in IMPORT_REPLACEMENTS.items():
                    if re.search(old_pattern, new_content):
                        new_content = re.sub(old_pattern, new_pattern, new_content)
                        changes_made = True
                
                if changes_made:
                    print(f"[REPAIRED]: {file_path}")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)

if __name__ == "__main__":
    # RUN THIS AFTER THE FOLDER REFACTOR IS DONE
    repair_imports(PROJECT_ROOT)
    print("--- IMPORT REPAIR COMPLETE ---")
