#!/usr/bin/env python3
"""
L0 Maintenance: Sovereign State Reset
Purges volatile state that causes MemoryError and ensures clean SSL fixes.
"""
import os
import shutil
from pathlib import Path


def purge_volatile_state():
    # 1. TARGET DIRECTORIES (The Memory Eaters)
    TARGETS = [
        "**/__pycache__",
        "**/.pytest_cache", 
        ".git/lfs/cache",
        "archives/legacy_code/.cache"
    ]
    
    print("[*] SOVEREIGN STATE RESET INITIATED")
    
    # Find project root by looking for .env file
    root = Path.cwd()
    for parent in Path.cwd().parents:
        if (parent / ".env").exists():
            root = parent
            break
    
    print(f"   [ROOT] Project root: {root}")
    
    purged_count = 0
    for pattern in TARGETS:
        for path in root.glob(pattern):
            try:
                if path.is_dir():
                    shutil.rmtree(path)
                    print(f"   [PURGED] Folder: {path.relative_to(root)}")
                    purged_count += 1
                else:
                    path.unlink()
                    print(f"   [PURGED] File: {path.relative_to(root)}")
                    purged_count += 1
            except Exception as e:
                print(f"   [!] Skipping {path}: {e}")

    # 2. REDIS STATE FLUSH (Ensures L2 Fallback logic resets)
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.flushdb()
        print("   [OK] Redis State Flushed")
    except Exception as e:
        print(f"   [!] Redis not reachable for flush: {e}")

    # 3. PYTHON BYTECODE CLEANUP
    try:
        import glob
        pyc_files = list(root.rglob("*.pyc")) + list(root.rglob("*.pyo"))
        for pyc_file in pyc_files:
            try:
                pyc_file.unlink()
                purged_count += 1
            except:
                pass
        if pyc_files:
            print(f"   [OK] Purged {len(pyc_files)} bytecode files")
    except:
        pass

    print(f"   [COMPLETE] Sovereign state reset: {purged_count} items purged")

if __name__ == "__main__":
    purge_volatile_state()
