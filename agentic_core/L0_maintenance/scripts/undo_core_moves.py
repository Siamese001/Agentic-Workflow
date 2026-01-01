"""
Undo all the incorrect core/ subdirectory moves
"""
import shutil
from pathlib import Path
from typing import Any

def undo_core_moves() -> Any:
    """Move all files back from */core/ to parent directories"""
    root: Any = Path('.')
    directories: Any = ['agentic_core', 'apps_lic', 'apps_rg', 'apps_shared', 'config', 'observability', 'schemas', 'scripts', 'tools', 'validator', 'prompt_governance']
    moved_count: Any = 0
    for dir_name in directories:
        core_path: Any = root / dir_name / 'core'
        if not core_path.exists():
            continue
        for py_file in core_path.glob('*.py'):
            if py_file.name == '__init__.py':
                continue
            target: Any = core_path.parent / py_file.name
            if target.exists():
                print(f'Skipping {py_file} (target exists)')
                continue
            print(f'Moving {py_file} -> {dir_name}/{py_file.name}')
            shutil.move(str(py_file), str(target))
            moved_count += 1
        try:
            core_path.rmdir()
            print(f'Removed {dir_name}/core/')
        except:
            pass
    print(f'\nTotal files moved back: {moved_count}')
if __name__ == '__main__':
    undo_core_moves()
