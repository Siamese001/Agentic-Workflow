"""
Scan the 10 ENFORCED_TERRITORIES for hardcoded string literals that should
use SSOT-defined path constants from structure_blueprint_config.py.

Outputs findings to artifacts/adg/hardcoded_ssot_violations.json
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# guardian: allow-global-mutation
sys.path.insert(0, str(ROOT))
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    ENFORCED_TERRITORIES,
    SOVEREIGN_EXCLUDED_FOLDERS,
)

SSOT_PATH_CONSTANTS: dict[str, str] = {'ARCHIVES_DIR': 'archives', 'AGENTIC_CORE_DIR': 'agentic_core', 'APPS_RG_DIR': 'apps_rg', 'APPS_LIC_DIR': 'apps_lic', 'APPS_SHARED_DIR': 'apps_shared', 'OPS_SCRIPTS_DIR': 'ops_scripts', 'TESTS_DIR': 'tests', 'L0_MAINTENANCE_DIR': 'agentic_core/L0_routing', 'L1_COGNITION_DIR': 'agentic_core/L1_cognition', 'L2_EXECUTION_DIR': 'agentic_core/L2_execution', 'L3_ORCHESTRATION_DIR': 'agentic_core/L3_orchestration', 'L4_STATE_DIR': 'agentic_core/L4_state', 'L5_SAFETY_DIR': 'agentic_core/L5_safety', 'L6_OBSERVABILITY_DIR': 'agentic_core/L6_observability', 'DOCS_REPORTS_PLANS': 'docs/reports/plans', 'REPORTS_DIR': 'reports', 'TOOLS_DIR': 'tools', 'SYSTEM_LEARNING_DIR': 'system_learning', 'DASHBOARD_DIR': 'agentic_core/L6_observability/dashboards', 'TESTS_UNIT_DIR': 'tests/unit', 'TESTS_INTEGRATION_DIR': 'tests/integration', 'TESTS_E2E_DIR': 'tests/e2e'}
SORTED_LITERALS = sorted(SSOT_PATH_CONSTANTS.items(), key=lambda x: -len(x[1]))

def _is_import_line(line: str) -> bool:
    s = line.strip()
    return s.startswith('import ') or s.startswith('from ')

def _is_comment(line: str) -> bool:
    return line.strip().startswith('#')

def scan() -> dict:
    violations: dict[str, list] = {}
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
                try:
                    text = fpath.read_text(encoding='utf-8', errors='replace')
                except (OSError, UnicodeDecodeError):    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling
                    continue
                lines = text.splitlines()
                for const_name, literal in SORTED_LITERALS:
                    if const_name in text:
                        continue
                    # guardian: allow-path-string
                    pat = re.compile('(?<![a-zA-Z0-9_/\\\\])[\'"]' + re.escape(literal) + '(?:[/\'"\\\\]|$)')
                    for lineno, line in enumerate(lines, 1):
                        if _is_comment(line) or _is_import_line(line):
                            continue
                        if pat.search(line):
                            if rel not in violations:
                                violations[rel] = []
                            violations[rel].append({'line': lineno, 'const': const_name, 'literal': literal, 'text': line.strip()[:120]})
                            break
    return violations

def main() -> None:
    print('[SCAN] Scanning 10 ENFORCED_TERRITORIES for hardcoded SSOT path literals...')
    violations = scan()
    out_dir = ROOT / 'artifacts' / 'adg'
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / 'hardcoded_ssot_violations.json'
    out_path.write_text(json.dumps(violations, indent=2), encoding='utf-8')
    total_files = len(violations)
    total_hits = sum(len(v) for v in violations.values())
    print(f'[SCAN] Done. {total_files} files with violations, {total_hits} total hits.')
    print(f'[SCAN] Output: {out_path}')
    print()
    for fpath in sorted(violations):
        print(f'  {fpath}')
        for h in violations[fpath]:
            print(f'''    L{h['line']:4d}  [{h['const']}]  "{h['literal']}"  ->  {h['text']}''')
if __name__ == '__main__':
    main()
