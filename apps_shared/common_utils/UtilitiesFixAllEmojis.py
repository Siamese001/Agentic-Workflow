from __future__ import annotations
"""
Fix all Unicode emojis in Python files to ASCII equivalents.
Prevents Windows encoding issues.
"""
from pathlib import Path
from typing import Any

from agentic_core.L5_safety.validators.structure_blueprint import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)
from agentic_core.utils.sovereign_index import SovereignIndex
from agentic_core.utils.file_utils import safe_read_file, safe_write_file
emoji_map: Any = {'✅': '[OK]', '⚠️': '[!]', '🔧': '[+]', '🔄': '[~]', '🆕': '[NEW]', '♻️': '[REUSE]', '🚨': '[ALERT]', '🚫': '[X]', '❌': '[X]', '🧹': '[CLEAN]', '🏛️': '[ARCH]', '💾': '[SAVE]', '🔍': '[SCAN]', '📊': '[STATS]', '📂': '[DIR]', '📋': '[PLAN]', '🚀': '[START]', '🌱': '[GIT]', '🧬': '[CYCLE]'}

def fix_emojis_in_file(file_path: str) -> bool:
    """Replace all emojis in a file with ASCII equivalents."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content: Any = f.read()
        original_content: Any = content
        for emoji, replacement in EMOJI_MAP.items():
            content: Any = content.replace(emoji, replacement)
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'✓ Fixed: {file_path}')
            return True
        return False
    except Exception as e:
        print(f'✗ Error fixing {file_path}: {e}')
        return False

def main() -> Any:
    """Find and fix all Python files with emojis."""
    root: Any = Path('c:/Git/Agentic-Workflow')
    targets: Any = [root / AGENTIC_CORE_DIR, root / APPS_SHARED_DIR]
    fixed_count: Any = 0
    for target_dir in targets:
        if not target_dir.exists():
            continue
        # Phase 6.9 Sub-50: Use ssot_discovery instead of rglob
    from agentic_core.utils.ssot_discovery import get_python_files
    for py_file in get_python_files(target_dir):
            if fix_emojis_in_file(str(py_file)):
                fixed_count += 1
    print(f'\n[*] Fixed {fixed_count} files')
if __name__ == '__main__':
    main()
