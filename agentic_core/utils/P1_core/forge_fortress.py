import os
import shutil
import logging
from pathlib import Path

# --- CONFIGURATION ---
ROOT = Path("C:/Git/Agentic-Workflow")
CORE = ROOT / "agentic_core"

# Set up logging for the audit trail
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# 1. CORE DOMAIN (Depth 4: agentic_core/Layer/Stage)
CORE_MAP = {
    "L0_maintenance": ["P1_core", "scripts", "migrations", "automation"],
    "L1_cognition": ["P1_core", "P1_interfaces", "P1_domain", "planning"],
    "L2_execution": ["P1_core", "P2_tools", "P3_engines", "P4_agents", "sandbox"],
    "L3_orchestration": ["P1_core", "health", "security", "training", "S3_vitality"],
    "L4_state": ["P1_core", "S1_store"],
    "L5_safety": ["P1_core", "P1_red_team", "P4_security"],
    "config": ["P1_core", "environments", "secrets"],
    "observability": ["P1_core", "logging", "telemetry", "monitoring"],
    "prompt_governance": ["P1_core", "P2_prompts", "P3_versioning"],
    "schemas": ["P1_core", "P2_validation", "P3_types"],
    "utils": ["P1_core", "P2_helpers", "P3_validators"],
    "runtime": ["P1_core", "S2_execution", "void_compliance"],
    "knowledge": ["P1_core", "P1_retrieve", "P3_engines"],
    "memory": ["P1_core"]
}

# 2. EXTERNAL TERRITORIES (Depth 3: Root/Folder/Stage)
EXTERNAL_MAP = {
    "apps_rg": ["engines", "templates", "P1_core"],
    "apps_lic": ["engines", "templates", "P1_core"],
    "apps_shared": ["models", "utils", "P1_core"],
    "tests": ["unit", "integration", "e2e", "performance", "fixtures", "security"],
    "data": ["raw", "processed", "vectordb"],
    "archives": ["logs", "backups", "refactors"]
}

# 3. MIGRATION LOGIC (Mapping loose root folders to Core homes)
ANNEXATION_PLAN = {
    "config": CORE / "config/P1_core",
    "observability": CORE / "observability/P1_core",
    "prompt_governance": CORE / "prompt_governance/P1_core",
    "schemas": CORE / "schemas/P1_core",
    "scripts": CORE / "L0_maintenance/scripts",
    "prompt_templates": CORE / "prompt_governance/P2_prompts"
}

def forge_fortress():
    logging.info("FORTRESS FORGE: Initializing System Reconstruction...")

    # --- PHASE 1: CORE RECONSTRUCTION ---
    for layer, stages in CORE_MAP.items():
        layer_path = CORE / layer
        layer_path.mkdir(parents=True, exist_ok=True)
        (layer_path / "__init__.py").touch()
        
        for stage in stages:
            stage_path = layer_path / stage
            stage_path.mkdir(parents=True, exist_ok=True)
            (stage_path / "__init__.py").touch()
            logging.debug(f"Stage Verified: {layer}/{stage}")

    # --- PHASE 2: EXTERNAL TERRITORY ALIGNMENT ---
    for folder, stages in EXTERNAL_MAP.items():
        folder_path = ROOT / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        
        for stage in stages:
            stage_path = folder_path / stage
            stage_path.mkdir(parents=True, exist_ok=True)
            # Data and Archives don't need Python package markers
            if folder not in ["data", "archives"]:
                (stage_path / "__init__.py").touch()

    # --- PHASE 3: SURGICAL ANNEXATION ---
    for old_name, destination in ANNEXATION_PLAN.items():
        old_path = ROOT / old_name
        if old_path.exists() and old_path.is_dir():
            logging.info(f"Annexing {old_name} territory into Sovereign Core...")
            
            for item in old_path.iterdir():
                # Skip already organized internal stages to prevent recursion
                if item.name in CORE_MAP.keys() or item.name == "__init__.py":
                    continue
                
                target = destination / item.name
                try:
                    if not target.exists():
                        shutil.move(str(item), str(target))
                        logging.info(f"  [MOVED] {item.name}")
                    else:
                        logging.warning(f"  [COLLISION] {item.name} exists in target. Manual merge required.")
                except Exception as e:
                    logging.error(f"  [FAILED] Move {item.name}: {e}")
            
            # Remove empty shell if safe
            if not any(old_path.iterdir()):
                try:
                    old_path.rmdir()
                except: pass

    logging.info("--- FORGE COMPLETE: Sovereign Architecture In Place ---")

if __name__ == "__main__":
    forge_fortress()
