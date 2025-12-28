#!/usr/bin/env python3
"""
Fix final remaining violations
"""
import sys
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from agentic_core.runtime.shared_runtime.import_healer import ImportHealer

project_root = Path(__file__).parent
agentic_core = project_root / "agentic_core"

print("="*70)
print("FIXING FINAL VIOLATIONS")
print("="*70)

healer = ImportHealer(project_root)
moved_count = 0

# 1. Move remaining schema files to models/
schema_files = ["simulation.py", "tone.py", "tool_args.py"]
schemas_dir = agentic_core / "schemas"
models_dir = schemas_dir / "models"

# 2. Move observability/meta and observability/logs to metrics/
obs_meta = agentic_core / "observability" / "meta"
obs_logs = agentic_core / "observability" / "logs"
metrics_dir = agentic_core / "observability" / "metrics"

# 3. Fix pinecone_store.py depth (depth 5 → depth 4)
pinecone_old = agentic_core / "semantic_memory" / "vector_stores" / "pinecone" / "pinecone_store.py"
pinecone_new = agentic_core / "semantic_memory" / "vector_stores" / "pinecone_store.py"

print(f"\nFound {len(schema_files)} schema files to move")
print(f"Found observability/meta folder: {obs_meta.exists()}")
print(f"Found observability/logs folder: {obs_logs.exists()}")
print(f"Found pinecone_store.py at depth 5: {pinecone_old.exists()}")

response = input("\nProceed with fixes? (yes/no): ")
if response.lower() != 'yes':
    print("Aborted")
    sys.exit(0)

# Move schema files
print("\n" + "="*70)
print("MOVING SCHEMA FILES")
print("="*70)

for filename in schema_files:
    old_path = schemas_dir / filename
    new_path = models_dir / filename
    
    if not old_path.exists():
        print(f"[!] Not found: {filename}")
        continue
    
    try:
        old_path_str = str(old_path.relative_to(project_root)).replace('\\', '/')
        new_path_str = str(new_path.relative_to(project_root)).replace('\\', '/')
        healer.register_relocation(old_path_str, new_path_str)
        
        shutil.move(str(old_path), str(new_path))
        moved_count += 1
        print(f"[✓] Moved: {filename}")
    except Exception as e:
        print(f"[!] Failed: {e}")

# Move observability folders
print("\n" + "="*70)
print("MOVING OBSERVABILITY SUBFOLDERS")
print("="*70)

metrics_dir.mkdir(parents=True, exist_ok=True)

# Move meta folder contents
if obs_meta.exists():
    for item in obs_meta.rglob("*"):
        if item.is_file() and not item.name.startswith('.'):
            rel_path = item.relative_to(obs_meta)
            target = metrics_dir / "meta" / rel_path
            
            try:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(item), str(target))
                print(f"[✓] Moved meta/{item.name}")
                moved_count += 1
            except Exception as e:
                print(f"[!] Failed: {e}")
    
    try:
        shutil.rmtree(obs_meta)
        print(f"[✓] Removed: observability/meta/")
    except Exception as e:
        print(f"[!] Failed to remove meta: {e}")

# Move logs folder contents
if obs_logs.exists():
    for item in obs_logs.rglob("*"):
        if item.is_file() and not item.name.startswith('.'):
            rel_path = item.relative_to(obs_logs)
            target = metrics_dir / "logs" / rel_path
            
            try:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(item), str(target))
                print(f"[✓] Moved logs/{item.name}")
                moved_count += 1
            except Exception as e:
                print(f"[!] Failed: {e}")
    
    try:
        shutil.rmtree(obs_logs)
        print(f"[✓] Removed: observability/logs/")
    except Exception as e:
        print(f"[!] Failed to remove logs: {e}")

# Fix pinecone_store.py depth
print("\n" + "="*70)
print("FIXING PINECONE DEPTH")
print("="*70)

if pinecone_old.exists():
    try:
        old_path_str = str(pinecone_old.relative_to(project_root)).replace('\\', '/')
        new_path_str = str(pinecone_new.relative_to(project_root)).replace('\\', '/')
        healer.register_relocation(old_path_str, new_path_str)
        
        shutil.move(str(pinecone_old), str(pinecone_new))
        moved_count += 1
        print(f"[✓] Moved: pinecone_store.py (depth 5 → 4)")
        
        # Remove empty pinecone folder
        pinecone_dir = pinecone_old.parent
        if pinecone_dir.exists() and not any(pinecone_dir.iterdir()):
            shutil.rmtree(pinecone_dir)
            print(f"[✓] Removed empty: pinecone/")
    except Exception as e:
        print(f"[!] Failed: {e}")

# Fix imports
if moved_count > 0:
    print(f"\n{'='*70}")
    print("FIXING IMPORTS")
    print(f"{'='*70}")
    
    results = healer.heal_all_imports_in_directory(agentic_core)
    if results:
        print(f"[✓] Fixed imports in {len(results)} files")
    else:
        print("[!] No imports needed fixing")

print(f"\n{'='*70}")
print("SUMMARY")
print(f"{'='*70}")
print(f"Files moved: {moved_count}")
print("\nRe-run validation:")
print("  python run_agentic_core_validation.py")
