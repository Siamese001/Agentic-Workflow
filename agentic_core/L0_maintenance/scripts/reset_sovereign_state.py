from __future__ import annotations
"""
L0 Maintenance: Sovereign State Reset
Purges volatile state that causes MemoryError and ensures clean SSL fixes.
"""
import os
import shutil
from pathlib import Path
from typing import Any

def purge_volatile_state() -> Any:
    """Brief description of functionality and purpose."""
    TARGETS: Any = ['**/__pycache__', '**/.pytest_cache', '.git/lfs/cache', 'archives/legacy_code/.cache']
    print('[*] SOVEREIGN STATE RESET INITIATED')
    root: Any = Path.cwd()
    for parent in Path.cwd().parents:
        if (parent / '.env').exists():
            root: Any = parent
            break
    print(f'   [ROOT] Project root: {root}')
    purged_count: Any = 0
    for pattern in TARGETS:
        for path in root.glob(pattern):
            try:
                if path.is_dir():
                    shutil.rmtree(path)
                    print(f'   [PURGED] Folder: {path.relative_to(root)}')
                    purged_count += 1
                else:
                    path.unlink()
                    print(f'   [PURGED] File: {path.relative_to(root)}')
                    purged_count += 1
            except Exception as e:
                print(f'   [!] Skipping {path}: {e}')
    try:
        import redis
        r: Any = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.flushdb()
        print('   [OK] Redis State Flushed')
    except Exception as e:
        print(f'   [!] Redis not reachable for flush: {e}')
    try:
        from agentic_core.utils.ssot_discovery import get_data_files
        pyc_files: Any = list(get_data_files(root, extensions=['.pyc'])) + list(get_data_files(root, extensions=['.pyo']))
        for pyc_file in pyc_files:
            try:
                pyc_file.unlink()
                purged_count += 1
            except Exception as e:
                print(f'   [!] Failed to remove {pyc_file}: {e}')
        if pyc_files:
            print(f'   [OK] Purged {len(pyc_files)} bytecode files')
    except:
        pass
    print(f'   [COMPLETE] Sovereign state reset: {purged_count} items purged')
if __name__ == '__main__':
    purge_volatile_state()
