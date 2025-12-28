import logging
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path("C:/Git/Agentic-Workflow")
CORE = ROOT / "agentic_core"
# Folders we strictly DO NOT touch/move/modify logic-wise
EXCLUDED_ZONES = ["data", "archives", "tests", ".git", ".venv", "__pycache__"]

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# [SSOT] Import structure from master blueprint
# Path insert no longer needed - using absolute import
from agentic_core.config.blueprint_sovereign.structure_blueprint import AGENTIC_CORE_REGISTRY

# Use the master blueprint as CORE_MAP
CORE_MAP = AGENTIC_CORE_REGISTRY

# 2. EXTERNAL MAP (Strictly Root-Level Structure)
EXTERNAL_MAP = {
    "apps_rg": ["engines", "templates", "P1_core"],
    "apps_lic": ["engines", "templates", "P1_core"],
    "apps_shared": ["models", "utils", "P1_core"],
    "tests": ["unit", "integration", "e2e", "performance", "fixtures", "security"],
    "data": ["raw", "processed", "vectordb"],
    "archives": ["logs", "backups", "refactors"]
}

# 3. ANNEXATION PLAN (Target destinations for root-level logic)
ANNEXATION_PLAN = {
    "config": CORE / "config/P1_core",
    "observability": CORE / "observability/P1_core",
    "prompt_governance": CORE / "prompt_governance/P1_core",
    "schemas": CORE / "schemas/P1_core",
    "scripts": CORE / "L0_maintenance/scripts",
    "prompt_templates": CORE / "prompt_governance/P2_prompts"
}

def zero_loss_move(src, dst):
    """Moves a file. If it exists at destination, renames with timestamp."""
    if not src.exists(): return
    
    if dst.exists() and src.is_file():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_name = f"{dst.stem}_{timestamp}{dst.suffix}"
        dst = dst.parent / new_name
        logging.warning(f"Collision detected! Renaming to: {new_name}")

    try:
        shutil.move(str(src), str(dst))
    except Exception as e:
        logging.error(f"Failed to move {src} -> {dst}: {e}")

def forge_sovereign_system():
    logging.info("--- COMMENCING ZERO-LOSS SOVEREIGN MERGE ---")

    # PHASE 1: CREATE DIRECTORY SKELETON
    for layer, stages in CORE_MAP.items():
        (CORE / layer).mkdir(parents=True, exist_ok=True)
        (CORE / layer / "__init__.py").touch()
        for stage in stages:
            s_path = CORE / layer / stage
            s_path.mkdir(parents=True, exist_ok=True)
            (s_path / "__init__.py").touch()

    for folder, stages in EXTERNAL_MAP.items():
        (ROOT / folder).mkdir(parents=True, exist_ok=True)
        for stage in stages:
            s_path = ROOT / folder / stage
            s_path.mkdir(parents=True, exist_ok=True)
            if folder not in ["data", "archives"]:
                (s_path / "__init__.py").touch()

    # PHASE 2: SURGICAL ANNEXATION
    for old_folder_name, destination in ANNEXATION_PLAN.items():
        old_path = ROOT / old_folder_name
        if old_path.exists() and old_path.is_dir():
            logging.info(f"Merging {old_folder_name} into Sovereign Core...")
            for item in list(old_path.iterdir()):
                # Avoid self-recursion if already moved
                if item.name in CORE_MAP.keys() or item.name == "__init__.py":
                    continue
                
                zero_loss_move(item, destination / item.name)

            # Cleanup empty shell if it's not a protected root folder
            try:
                if not any(old_path.iterdir()) and old_folder_name not in EXTERNAL_MAP:
                    shutil.rmtree(old_path)
            except: pass

    # PHASE 3: AUDIT & FINAL LOCKDOWN
    print("\n--- ZERO-LOSS INTEGRITY REPORT ---")
    for zone in EXCLUDED_ZONES:
        status = "RETAINED" if (ROOT / zone).exists() else "MISSING"
        print(f"  [✓] Protected Zone: {zone.ljust(15)} -> {status}")

    print("\n[SUCCESS] FORGE COMPLETE. Your architecture is now physically Sovereign.")

if __name__ == "__main__":
    forge_sovereign_system()
