"""Verify duplicates between config/ and config/core/."""

import hashlib
from pathlib import Path

root_files = {f.name: f for f in Path('agentic_core/config').glob('*.py')}
core_files = {f.name: f for f in Path('agentic_core/config/core').glob('*.py')}

print("=== File Comparison ===")
print(f"Root files: {len(root_files)}")
print(f"Core files: {len(core_files)}")
print()

duplicates = []
different = []
root_only = []
core_only = []

for name, root_file in root_files.items():
    if name in core_files:
        core_file = core_files[name]
        root_hash = hashlib.sha256(root_file.read_bytes()).hexdigest()
        core_hash = hashlib.sha256(core_file.read_bytes()).hexdigest()
        if root_hash == core_hash:
            duplicates.append(name)
            print(f'DUPLICATE: {name}')
        else:
            different.append(name)
            print(f'DIFFERENT: {name}')
    else:
        root_only.append(name)
        print(f'ROOT ONLY: {name}')

for name in core_files:
    if name not in root_files:
        core_only.append(name)
        print(f'CORE ONLY: {name}')

print()
print('=== Summary ===')
print(f'Duplicates: {len(duplicates)}')
print(f'Different: {len(different)}')
print(f'Root only: {len(root_only)}')
print(f'Core only: {len(core_only)}')
