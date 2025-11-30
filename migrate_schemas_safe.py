import os
import shutil
import json
from datetime import datetime

ROOT = r"C:\Users\amita\Documents\Work\AI Job Search\AI\ML\DL\GenAI\LLM 101\LLM Pipelines\Resume Gen\Git\Agentic_Workflow-10_11\schemas"
BACKUP_ROOT = r"C:\Users\amita\Documents\Work\AI Job Search\AI\ML\DL\GenAI\LLM 101\LLM Pipelines\Resume Gen\Git\Agentic_Workflow-10_11\schemas_backup"

# ---------------------------------------------------------------------
# 1. Define the NEW schema folder layout
# ---------------------------------------------------------------------
NEW_LAYOUT = {
    "core": [],
    "planning": [],
    "execution": [],
    "orchestration": [],
    "memory_state": [],
    "safety": [],
    "model_routing": [],
    "prompt_governance": [],
    "observability": [],
    "data_assets": [],
    "engines/resume_engine": [],
    "engines/outreach_engine": [],
    "tests": [],
}

# ---------------------------------------------------------------------
# 2. Create backup before migration
# ---------------------------------------------------------------------
def create_backup():
    """Create a complete backup of the schemas directory"""
    if os.path.exists(BACKUP_ROOT):
        shutil.rmtree(BACKUP_ROOT)
    
    print(f"Creating backup at: {BACKUP_ROOT}")
    shutil.copytree(ROOT, BACKUP_ROOT)
    print("✅ Backup created successfully")

# ---------------------------------------------------------------------
# 3. Ensure new folders exist
# ---------------------------------------------------------------------
def ensure_folders():
    print("Creating new folder structure...")
    for folder in NEW_LAYOUT.keys():
        target = os.path.join(ROOT, folder)
        os.makedirs(target, exist_ok=True)
        print(f"  Created: {folder}")

# ---------------------------------------------------------------------
# 4. Mapping of old → new folder locations
# ---------------------------------------------------------------------
MOVE_MAP = {
    # shared
    "shared": "core",
    # planning
    "l1_planning": "planning",
    "L1": "planning",
    # execution
    "l2_execution": "execution",
    "L2": "execution",
    # orchestration
    "l3_orchestration": "orchestration",
    "L3": "orchestration",
    # memory
    "l4_memory": "memory_state",
    "L4": "memory_state",
    "L4_memory_state": "memory_state",
    # safety
    "l5_safety": "safety",
    "L5": "safety",
    # top-level python files
    "agent.py": "core",
    "base.py": "core",
    "plan.py": "planning",
    # other containers
    "agents": "core",
    "memory": "memory_state",
    "plans": "planning",
    "tools": "execution",
}

# ---------------------------------------------------------------------
# 5. Collect all moves first (safer approach)
# ---------------------------------------------------------------------
def collect_moves():
    """Collect all file moves to execute later"""
    moves = []
    
    # Walk the directory tree to find all files
    for root, dirs, files in os.walk(ROOT):
        # Skip new folders and backup folder
        if (any(root.endswith(nf) for nf in NEW_LAYOUT.keys()) or 
            "backup" in root.lower() or 
            root == BACKUP_ROOT):
            continue

        # Process files in current directory
        for file in files:
            src = os.path.join(root, file)
            parent = os.path.basename(root)

            # Skip the migration script itself
            if file.endswith('_migrate_schemas_safe.py') or file.endswith('_migrate_schemas.py'):
                continue

            # Determine destination folder
            if file in MOVE_MAP:
                new_folder = MOVE_MAP[file]
            elif parent in MOVE_MAP:
                new_folder = MOVE_MAP[parent]
            else:
                # Skip files not in mapping but log them
                print(f"SKIP: {src} (not in move map)")
                continue

            dst_folder = os.path.join(ROOT, new_folder)
            dst = os.path.join(dst_folder, file)
            moves.append((src, dst, new_folder))
    
    return moves

# ---------------------------------------------------------------------
# 6. Execute all collected moves
# ---------------------------------------------------------------------
def execute_moves(moves):
    """Execute all file moves"""
    print(f"\nExecuting {len(moves)} file moves...")
    
    for src, dst, new_folder in moves:
        try:
            # Ensure destination folder exists
            dst_folder = os.path.dirname(dst)
            os.makedirs(dst_folder, exist_ok=True)
            
            # Skip if source doesn't exist (might have been moved already)
            if not os.path.exists(src):
                print(f"SKIP MISSING: {src}")
                continue
                
            # Skip if destination already exists
            if os.path.exists(dst):
                print(f"SKIP EXISTS: {dst}")
                continue
            
            print(f"MOVE: {src} → {dst}")
            shutil.move(src, dst)
            
        except Exception as e:
            print(f"ERROR moving {src}: {e}")

# ---------------------------------------------------------------------
# 7. Delete empty legacy folders
# ---------------------------------------------------------------------
def delete_empty():
    print("\nCleaning up empty folders...")
    
    # Get all directories to check (excluding new layout folders)
    all_dirs = []
    for root, dirs, files in os.walk(ROOT):
        if (any(root.endswith(nf) for nf in NEW_LAYOUT.keys()) or 
            "backup" in root.lower()):
            continue
        all_dirs.append(root)
    
    # Process in reverse order (leaf nodes first)
    for root in sorted(all_dirs, reverse=True):
        if root == ROOT:
            continue
            
        try:
            if not os.listdir(root):  # Directory is empty
                print(f"DELETE EMPTY: {root}")
                os.rmdir(root)
        except Exception as e:
            print(f"ERROR deleting {root}: {e}")

# ---------------------------------------------------------------------
# 8. Generate migration report
# ---------------------------------------------------------------------
def generate_report(moves):
    """Generate a report of what was migrated"""
    report = {
        "migration_timestamp": datetime.now().isoformat(),
        "total_files_moved": len(moves),
        "moves": [
            {
                "source": src,
                "destination": dst,
                "new_folder": new_folder
            }
            for src, dst, new_folder in moves
        ]
    }
    
    report_file = os.path.join(ROOT, "migration_report.json")
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📊 Migration report saved to: {report_file}")
    return report

# ---------------------------------------------------------------------
# 9. Verify migration
# ---------------------------------------------------------------------
def verify_migration():
    """Verify that the migration completed successfully"""
    print("\n🔍 Verifying migration...")
    
    # Check new folders exist and have content
    for folder in NEW_LAYOUT.keys():
        folder_path = os.path.join(ROOT, folder)
        if os.path.exists(folder_path):
            files = []
            for root, dirs, filenames in os.walk(folder_path):
                files.extend(filenames)
            print(f"  ✅ {folder}: {len(files)} files")
        else:
            print(f"  ❌ {folder}: Missing")
    
    print("\n✅ Migration verification complete")

# ---------------------------------------------------------------------
# 10. Run all migration steps
# ---------------------------------------------------------------------
if __name__ == "__main__":
    print("🚀 Starting safe schema migration...")
    
    try:
        # Step 1: Create backup
        create_backup()
        
        # Step 2: Create new folder structure
        ensure_folders()
        
        # Step 3: Collect all moves
        moves = collect_moves()
        print(f"\n📋 Collected {len(moves)} files to move")
        
        # Step 4: Execute moves
        execute_moves(moves)
        
        # Step 5: Clean up empty folders
        delete_empty()
        
        # Step 6: Generate report
        report = generate_report(moves)
        
        # Step 7: Verify migration
        verify_migration()
        
        print("\n🎉 SCHEMA MIGRATION COMPLETE")
        print(f"📁 Backup available at: {BACKUP_ROOT}")
        print(f"📊 Migration report: {len(moves)} files moved")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("🔄 Backup is available at:", BACKUP_ROOT)
        raise
