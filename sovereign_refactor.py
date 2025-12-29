import os
import shutil
import sys
from pathlib import Path

# --- CONFIGURATION ---
DRY_RUN = False  # FLIP TO FALSE TO EXECUTE
PROJECT_ROOT = "C:/Git/Agentic-Workflow"

# [SSOT] Import structure from master blueprint
from agentic_core.config.blueprint_sovereign.structure_blueprint import CORE_SUBFOLDER_MAP

# Use the master blueprint as FULL_CORE_SCHEMA
FULL_CORE_SCHEMA = CORE_SUBFOLDER_MAP

# APP TERRITORIES
APP_SCHEMAS = {
    "apps_rg": ["engines", "templates", "P1_core"],
    "apps_lic": ["engines", "templates", "P1_core"],
    "apps_shared": ["models", "utils", "P1_core"]
}

# THE MIGRATION MAP (Legacy -> New Path)
MERGE_MAP = {
    "memory": "semantic_memory",
    "L0_maintenance": "L0_maintenance",
    "L2_thought_nodes": "L1_cognition/thought_engine",
    "core": "P1_core",
    "core_logic": "P1_core"
}

IGNORE_LIST = ["__pycache__", ".git", ".pytest_cache", "venv", ".vscode"]

def log(action, message):
    prefix = "[DRY RUN]" if DRY_RUN else "[EXECUTING]"
    print(f"{prefix} {action.ljust(12)}: {message}")

def build_and_migrate(root_path):
    # 1. ORCHESTRATE AGENTIC_CORE
    core_path = os.path.join(root_path, "agentic_core")
    
    # First, handle migrations inside core (Renames/Nesting)
    for legacy, target_sub in MERGE_MAP.items():
        legacy_path = os.path.join(core_path, legacy)
        if os.path.exists(legacy_path):
            target_path = os.path.join(core_path, target_sub)
            log("MIGRATE", f"agentic_core/{legacy} -> agentic_core/{target_sub}")
            if not DRY_RUN:
                os.makedirs(target_path, exist_ok=True)
                for item in os.listdir(legacy_path):
                    shutil.move(os.path.join(legacy_path, item), os.path.join(target_path, item))
                os.rmdir(legacy_path)

    # Now, enforce full Level 3 depth and .gitkeeps
    for l2, l3_list in FULL_CORE_SCHEMA.items():
        for l3 in l3_list:
            l3_path = os.path.join(core_path, l2, l3)
            if not os.path.exists(l3_path):
                log("CREATE", f"agentic_core/{l2}/{l3}")
                if not DRY_RUN: os.makedirs(l3_path, exist_ok=True)
            
            # Place .gitkeep to ensure empty folders are tracked
            gitkeep = os.path.join(l3_path, ".gitkeep")
            if not os.path.exists(gitkeep):
                log("GITKEEP", f"Creating .gitkeep in {l2}/{l3}")
                if not DRY_RUN:
                    with open(gitkeep, 'w') as f: f.write('')

    # 2. CLEANSE APP TERRITORIES
    for app, allowed in APP_SCHEMAS.items():
        app_path = os.path.join(root_path, app)
        if not os.path.exists(app_path): continue
        
        # Ensure L2 folders exist
        for l2 in allowed:
            os.makedirs(os.path.join(app_path, l2), exist_ok=True) if not DRY_RUN else None
            
        # Move orphaned files to P1_core
        for item in os.listdir(app_path):
            item_path = os.path.join(app_path, item)
            if os.path.isfile(item_path) and item != ".gitkeep":
                log("STAGING", f"{app}/{item} -> {app}/P1_core/")
                if not DRY_RUN:
                    shutil.move(item_path, os.path.join(app_path, "P1_core", item))
            elif os.path.isdir(item_path) and item not in allowed and item not in IGNORE_LIST:
                log("MERGE APP DIR", f"{app}/{item} -> {app}/P1_core/")
                if not DRY_RUN:
                    # Move dir contents to P1_core
                    for sub in os.listdir(item_path):
                        shutil.move(os.path.join(item_path, sub), os.path.join(app_path, "P1_core", sub))
                    os.rmdir(item_path)

if __name__ == "__main__":
    print(f"--- INITIALIZING SOVEREIGN REFACTOR ---")
    build_and_migrate(PROJECT_ROOT)
    if DRY_RUN: print("\n--- AUDIT COMPLETE. No changes made. Set DRY_RUN=False to apply. ---")
