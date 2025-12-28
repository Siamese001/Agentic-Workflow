#!/usr/bin/env python3
"""
Sovereign Prune Empties - Final Stage of Hierarchy Healing
Purges empty legacy folders and stale __init__.py files after bulk move.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

# === CONFIGURATION ===
TARGET_ROOT = "agentic_core"
# The 'Scar Tissue' list
LEGACY_FOLDERS = [
    "P1_core", "P2_tools", "P3_engines", "P4_agents", "P5_healing", "P1_domain", 
    "P1_interfaces", "P2_domain", "P3_aggregation", "P5_meta", "boundaries", 
    "discovery", "identity", "inference", "planning", "planning_logic", "mcp", 
    "sandbox", "tools", "event_bus", "framework", "handoff_logic", "health", 
    "P5_workflow", "protocol", "security", "training", "automation", "migrations", 
    "cache", "checkpoints", "filesystem", "memory", "persistence_layer", 
    "S1_store", "semantic", "session_manager", "vector", "P1_red_team", 
    "P4_security", "audit_logs", "gravity", "policy", "validators"
]

def main():
    project_root = Path(__file__).resolve().parent.parent
    target_dir = project_root / TARGET_ROOT
    audit_log = project_root / "mission_audit.csv"
    
    print(f"--- SOVEREIGN PRUNE START: {TARGET_ROOT} ---")
    
    pruned_count = 0
    for layer in target_dir.iterdir():
        if not layer.is_dir() or not layer.name.startswith('L'):
            continue
            
        for legacy in LEGACY_FOLDERS:
            legacy_path = layer / legacy
            if legacy_path.exists():
                # Check if it only contains __init__.py or is truly empty
                files = [f for f in legacy_path.rglob('*') if f.is_file()]
                # If there's only an __init__.py left, it's a stale duplicate from our conflicts
                if len(files) <= 1:
                    if not files or files[0].name == "__init__.py":
                        try:
                            # Log it first
                            timestamp = datetime.now().isoformat()
                            with open(audit_log, "a") as f:
                                f.write(f"{timestamp},{legacy},PURGE,{legacy_path.relative_to(project_root)},None,Legacy Pruning\n")
                            
                            shutil.rmtree(legacy_path)
                            print(f"   [PURGE] Removed legacy folder: {legacy_path.relative_to(project_root)}")
                            pruned_count += 1
                        except Exception as e:
                            print(f"   [!] Error pruning {legacy}: {e}")

    print(f"\n[OK] Pruning complete. {pruned_count} legacy folders removed.")
    print("Run your validator now. Sovereignty awaits.")

if __name__ == "__main__":
    main()
