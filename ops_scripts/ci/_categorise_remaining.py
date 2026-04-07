"""
Categorise the 214 remaining violations into:
  A) Mixed list — const already imported but siblings still raw strings (fixable)
  B) .startswith / .endswith tuple arg — borderline, manual fix
  C) Dict key/value — skip
  D) Test assertion string — skip
  E) String template / f-string content — skip
  F) Other safe (path chain, compare) — fixable
"""
from __future__ import annotations

import os
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# guardian: allow-global-mutation
sys.path.insert(0, str(ROOT))
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    ENFORCED_TERRITORIES,
    SOVEREIGN_EXCLUDED_FOLDERS,
)

CONSTS: list[tuple[str, str]] = sorted([('ARCHIVES_DIR', ARCHIVES_DIR), ('AGENTIC_CORE_DIR', AGENTIC_CORE_DIR), ('APPS_RG_DIR', APPS_RG_DIR), ('APPS_LIC_DIR', APPS_LIC_DIR), ('APPS_SHARED_DIR', APPS_SHARED_DIR), ('OPS_SCRIPTS_DIR', OPS_SCRIPTS_DIR), ('TESTS_DIR', TESTS_DIR), ('TOOLS_DIR', TOOLS_DIR), ('SYSTEM_LEARNING_DIR', SYSTEM_LEARNING_DIR), ('L0_MAINTENANCE_DIR', L0_MAINTENANCE_DIR), ('L1_COGNITION_DIR', L1_COGNITION_DIR), ('L2_EXECUTION_DIR', L2_EXECUTION_DIR), ('L3_ORCHESTRATION_DIR', L3_ORCHESTRATION_DIR), ('L4_STATE_DIR', L4_STATE_DIR), ('L5_SAFETY_DIR', L5_SAFETY_DIR), ('L6_OBSERVABILITY_DIR', L6_OBSERVABILITY_DIR), ('DOCS_REPORTS_PLANS', DOCS_REPORTS_PLANS), ('REPORTS_DIR', REPORTS_DIR), ('TESTS_UNIT_DIR', TESTS_UNIT_DIR)], key=lambda x: -len(x[1]))
SSOT_SKIP = ('agentic_core/L5_safety/config/structure_blueprint/', 'agentic_core/L0_routing/config/path_constants')
categories: dict[str, list[dict]] = defaultdict(list)
for territory in sorted(ENFORCED_TERRITORIES):
    scan_root = ROOT / territory
    if not scan_root.exists():
        continue
    for dirpath, dirs, files in os.walk(scan_root):
        dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
        for fname in files:
            if not fname.endswith('.py'):
                continue
            fpath = Path(dirpath) / fname
            rel = fpath.relative_to(ROOT).as_posix()
            if any(rel.startswith(p) for p in SSOT_SKIP):
                continue
            try:
                content = fpath.read_text(encoding='utf-8', errors='replace')
            except (OSError, UnicodeDecodeError):    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling
                continue
            lines = content.splitlines()
            for const, lit in CONSTS:
                if const in content:
                    continue
                pat = re.compile('(?P<q>[\'"])' + re.escape(lit) + '(?P=q)')
                for lineno, line in enumerate(lines, 1):
                    s = line.strip()
                    if s.startswith('#') or s.startswith('import ') or s.startswith('from '):
                        continue
                    m = pat.search(line)
                    if not m:
                        continue
                    after = line[m.end()] if m.end() < len(line) else ''
                    if after == '/':
                        continue
                    entry = {'rel': rel, 'line': lineno, 'const': const, 'lit': lit, 'text': s[:110]}
                    if re.search('\\.(startswith|endswith)\\s*\\(', line):
                        categories['B_startswith'].append(entry)
                    # guardian: allow-path-string
                    elif re.search('[\'"]' + re.escape(lit) + '[\'"]\\s*:', line):
                        categories['C_dict_key'].append(entry)
                    # guardian: allow-path-string
                    elif re.search(':\\s*[\'"]' + re.escape(lit) + '[\'"]', line):
                        categories['C_dict_value'].append(entry)
                    elif 'assert' in s:
                        categories['D_assert'].append(entry)
                    elif re.search('f[\'""]', line):
                        categories['E_fstring'].append(entry)
                    # guardian: allow-path-string
                    elif re.search('\\[.*[\'"]' + re.escape(lit) + '[\'"].*,', line):
                        categories['A_mixed_list'].append(entry)
                    # guardian: allow-path-string
                    elif re.search('\\(.*[\'"]' + re.escape(lit) + '[\'"].*,', line):
                        categories['A_mixed_tuple'].append(entry)
                    else:
                        categories['F_other'].append(entry)
                    break
for cat, items in sorted(categories.items()):
    print(f'\n=== {cat}: {len(items)} ===')
    for it in items[:15]:
        print(f"  [{it['const']}] {it['rel']}:{it['line']}")
        print(f"    {it['text']}")
