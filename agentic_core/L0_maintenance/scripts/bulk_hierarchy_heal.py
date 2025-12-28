#!/usr/bin/env python3
"""
One-Off Bulk Hierarchy Healer - Eternal Depth 4 Alignment
"""

import shutil
import os
import sys
from pathlib import Path
from datetime import datetime

# === CONFIGURATION ===
DRY_RUN = False                 # Set False to execute real moves
TARGET_ROOT = "agentic_core"     # Only heal inside agentic_core
PRIMARY_PARTITION_ONLY = True    # Move everything to the first (usually P1_core)

# === GRAVITY ANCHOR ===
current_file = Path(__file__).resolve()
project_root = next((p for p in current_file.parents if (p / ".env").exists()), None)

if not project_root:
    print("[!] Project root not found (.env missing).")
    sys.exit(1)

# === IMPORT SSOT ===
sys.path.insert(0, str(project_root))
try:
    from agentic_core.config.blueprint_sovereign.structure_blueprint import CORE_SUBFOLDER_MAP
except ImportError:
    print("[!] Critical Failure: Cannot find CORE_SUBFOLDER_MAP in structure_blueprint.py")
    sys.exit(1)

def log_move(file_name, src, dst):
    audit_log = project_root / "mission_audit.csv"
    timestamp = datetime.now().isoformat()
    log_entry = f"{timestamp},{file_name},HIERARCHY_HEAL,{src},{dst},Bulk Alignment\n"
    
    with open(audit_log, "a") as f:
        f.write(log_entry)
    print(f"   [LOG] {file_name} moved to {dst}")

def main():
    target_dir = project_root / TARGET_ROOT
    python_files = list(target_dir.rglob("*.py"))
    
    print(f"--- SOVEREIGN HEALING START: {TARGET_ROOT} ---")
    print(f"Mode: {'DRY RUN' if DRY_RUN else 'EXECUTION'}")
    
    # Create output file for dry run
    output_file = project_root / "hierarchy_heal_dry_run.txt"
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"=== BULK HIERARCHY HEAL ===\n")
        f.write(f"Target: {TARGET_ROOT}\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        f.write(f"Configuration: DRY_RUN = {DRY_RUN}\n\n")
        
        for file_path in python_files:
            rel = file_path.relative_to(project_root)
            parts = rel.parts # e.g. ('agentic_core', 'L3_orchestration', 'file.py')
            
            # We only care about files under agentic_core/L#/
            if len(parts) < 3 or not parts[1].startswith('L'):
                continue
                
            layer = parts[1]
            allowed_partitions = CORE_SUBFOLDER_MAP.get(layer, [])
            if not allowed_partitions: continue
            
            primary = allowed_partitions[0] # Default to the P1_core partition
            
            # Check for Depth 2 Violation (file directly in L-folder)
            is_depth_2 = (len(parts) == 3)
            # Check for Depth 3 Partition Violation (file in wrong subfolder)
            is_wrong_partition = (len(parts) == 4 and parts[2] not in allowed_partitions)
            
            if is_depth_2 or is_wrong_partition:
                dest_dir = project_root / TARGET_ROOT / layer / primary
                dest_path = dest_dir / file_path.name
                
                if dest_path.exists():
                    log_entry = f"[CONFLICT] {rel} >> {dest_path.relative_to(project_root)} (already exists)\n"
                    print(f"   [!] CONFLICT: {file_path.name} already exists in {primary}. Skipping.")
                    f.write(log_entry)
                    continue

                log_entry = f"[MOVE] {rel} >> {dest_path.relative_to(project_root)}\n"
                print(f"   [MOVE] {rel} >> {dest_path.relative_to(project_root)}")
                f.write(log_entry)
                
                # Execute the move if not in dry run mode
                if not DRY_RUN:
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(file_path), str(dest_path))
                    log_move(file_path.name, "/".join(parts[:-1]), f"{layer}/{primary}")
        
        f.write(f"\n=== SUMMARY ===\n")
        f.write(f"Total Python files scanned: {len(python_files)}\n")
        f.write(f"Output file: {output_file}\n")
        f.write(f"DRY_RUN = {DRY_RUN}\n")
    
    if DRY_RUN:
        print(f"\n[DRY RUN COMPLETE] Output saved to: {output_file}")
        print(f"Set DRY_RUN = False in the script to execute moves")
    else:
        print(f"\n[EXECUTION COMPLETE] All moves executed. Output saved to: {output_file}")
    
    # === AUTO-CLEANUP: Remove empty legacy partitions ===
    if not DRY_RUN:
        print("\n--- INITIATING AUTO-CLEANUP ---")
        legacy_partitions = [
            "P1_core", "P1_domain", "P1_interfaces", "P2_domain", "P3_aggregation",
            "P5_meta", "boundaries", "discovery", "identity", "inference",
            "planning", "planning_logic", "mcp", "sandbox", "tools",
            "P2_tools", "P3_engines", "P4_agents", "P5_healing",
            "event_bus", "framework", "handoff_logic", "health", "P5_workflow",
            "protocol", "security", "training", "automation", "migrations",
            "cache", "checkpoints", "filesystem", "memory", "persistence_layer",
            "S1_store", "semantic", "session_manager", "vector",
            "P1_red_team", "P4_security", "audit_logs", "gravity", "policy", "validators"
        ]

        for layer_folder in target_dir.iterdir():
            if not layer_folder.is_dir() or not layer_folder.name.startswith("L"):
                continue
            
            for legacy in legacy_partitions:
                legacy_path = layer_folder / legacy
                if legacy_path.exists():
                    # Check if empty or only contains __init__.py/pycache
                    remaining = [f for f in legacy_path.iterdir() if f.name != "__pycache__" and f.name != "__init__.py"]
                    if not remaining:
                        try:
                            shutil.rmtree(legacy_path)
                            print(f"   [CLEAN] Purged legacy folder: {legacy_path.relative_to(project_root)}")
                        except Exception as e:
                            print(f"   [!] Could not purge {legacy}: {e}")

    # === SUMMARY ===
    print("\n" + "="*70)
    print(f"[COMPLETE] Bulk hierarchy healing for {TARGET_ROOT}")
    if DRY_RUN:
        print("Status: PREVIEW MODE - No files were moved")
    else:
        print("Status: EXECUTED - Files moved and legacy folders cleaned")
    print("="*70)

if __name__ == "__main__":
    main()
