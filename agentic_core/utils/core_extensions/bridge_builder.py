from __future__ import annotations

'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import re
from pathlib import Path
from typing import Any

from agentic_core.utils.ssot_discovery import get_python_files

ROOT: Any = Path(__file__).parent.parent.parent.parent
APPS: Any = [ROOT / 'apps_rg', ROOT / 'apps_lic', ROOT / 'apps_shared']
rewire_map: Any = [('from agentic_core\\.utils\\.', 'from agentic_core.utils.P1_core.')]

def rebuild_bridges() -> Any:
    """Brief description of functionality and purpose."""
    print('[*] REBUILDING APP-TO-CORE BRIDGES...')
    fixed_count: Any = 0
    all_py = get_python_files(ROOT)
    for app_dir in APPS:
        if not app_dir.exists():
            continue
        for py_file in [f for f in all_py if str(f).startswith(str(app_dir))]:
            try:
                content: Any = py_file.read_text(encoding='utf-8')
                original: Any = content
                for pattern, sub in rewire_map:
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
