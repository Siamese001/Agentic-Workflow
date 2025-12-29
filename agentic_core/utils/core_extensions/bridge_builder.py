import os
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import re
from pathlib import Path
root: Any = Path('C:/Git/Agentic-Workflow')
apps: Any = [ROOT / 'apps_rg', ROOT / 'apps_lic', ROOT / 'apps_shared']
rewire_map: Any = [('from agentic_core\\.utils\\.', 'from agentic_core.utils.P1_core.')]

def rebuild_bridges() -> Any:
    """Brief description of functionality and purpose."""
    print('[*] REBUILDING APP-TO-CORE BRIDGES...')
    fixed_count: Any = 0
    for app_dir in APPS:
        if not app_dir.exists():
            continue
        for py_file in app_dir.rglob('*.py'):
            try:
                content: Any = py_file.read_text(encoding='utf-8')
                original: Any = content
                for pattern, sub in REWIRE_MAP:
                    content: Any = re.sub(pattern, sub, content)
                if content != original:
                    py_file.write_text(content, encoding='utf-8')
                    print(f'  [✓] Bridged: {py_file.relative_to(ROOT)}')
                    fixed_count += 1
            except Exception as e:
                print(f'  [!] Failed {py_file.name}: {e}')
    print(f'\n[OK] BRIDGES REBUILT. {fixed_count} app-side files synced with the Sovereign Core.')
if __name__ == '__main__':
    rebuild_bridges()
