from __future__ import annotations
"""
Phase 1: Test Sovereignty Syntax Repair
Target: Bulk-repair indentation and markdown fences.
"""
import os
import pathlib
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
from archives.location_violations.sovereign_index import SovereignIndex

def repair_test_syntax(test_dir: Any=TESTS_DIR) -> Any:
    """Brief description of functionality and purpose."""
    files_fixed: Any = 0
    for path in pathlib.Path(test_dir).rglob('*.py'):
        try:
            lines: Any = path.read_text(encoding='utf-8').splitlines()
            new_lines: Any = []
            changed: Any = False
            if lines and lines[0].startswith('```'):
                lines: Any = [l for l in lines if not l.startswith('```')]
                changed: Any = True
            i: Any = 0
            while i < len(lines):
                line: Any = lines[i]
                new_lines.append(line)
                if line.strip().startswith('except ') and line.strip().endswith(':'):
                    if i + 1 < len(lines):
                        next_line: Any = lines[i + 1]
                        if next_line.strip() and (not next_line.startswith((' ', '\t'))):
                            indent: Any = len(line) - len(line.lstrip())
                            proper_indent: Any = ' ' * (indent + 4)
                            j: Any = i + 1
                            while j < len(lines):
                                following_line: Any = lines[j]
                                if following_line.strip() and (not following_line.startswith((' ', '\t'))):
                                    new_lines.append(proper_indent + following_line.lstrip())
                                    changed: Any = True
                                    j += 1
                                else:
                                    break
                            i: Any = j - 1
                i += 1
            if changed:
                path.write_text('\n'.join(new_lines), encoding='utf-8')
                files_fixed += 1
                print(f'[FIXED] Syntax repair in {path}')
        except Exception as e:
            print(f'[ERROR] Failed to process {path}: {e}')
    return files_fixed
if __name__ == '__main__':
    count: Any = repair_test_syntax()
    print(f'\nTotal files repaired: {count}')
