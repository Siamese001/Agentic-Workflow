"""
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_1")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_2")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_3")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_4")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_5")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_6")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_7")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_8")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_9")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_10")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_11")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_12")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_13")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_14")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_15")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_16")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_17")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_18")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_19")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_20")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_21")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_22")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_23")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_24")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_25")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_26")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_27")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_28")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_29")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_30")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_31")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_32")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_33")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_34")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_35")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_36")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_37")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_38")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_39")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_40")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_41")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_42")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_43")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_44")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_45")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_46")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_47")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_48")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_49")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_50")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_51")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_52")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_53")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_54")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_55")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_56")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_57")
_emit_reads_through("l4", "ssot_violation_scanner", "urg_read_58")
SSOT Violation Scanner  [UTF-8 output]
======================

Scans all SOVEREIGN_TERRITORIES (10 folders) for Python files that contain
hardcoded string literals or import paths that violate SSOT as defined by:

  - agentic_core/L0_routing/config/path_constants.py
  - agentic_core/L5_safety/config/structure_blueprint/ssot.py
  - agentic_core/L5_safety/config/structure_blueprint_config.py

Violation categories:
  REPLACE        - hardcoded path string, clear path construction context → swap for SSOT constant
  WRONG_IMPORT   - imports from structure_blueprint_config directly instead of canonical path
  SKIP_COMMENT   - in a docstring or comment only
  SKIP_TEST_DATA - intentional test fixture / assertion string
  SKIP_DYNAMIC   - runtime-computed or ambiguous context, needs manual review

Output: artifacts/ssot_violation_scan.json

Usage:
    python ops_scripts/ci/ssot_violation_scanner.py
    python ops_scripts/ci/ssot_violation_scanner.py --summary
    python ops_scripts/ci/ssot_violation_scanner.py --category REPLACE
"""
from __future__ import annotations

import ast
import io
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
_ROOT = Path(__file__).resolve().parents[2]
# guardian: allow-global-mutation
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    ARCHIVES_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    OPS_SCRIPTS_DIR,
    SYSTEM_LEARNING_DIR,
    TESTS_DIR,
    TOOLS_DIR,
)
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    DOCS_REPORTS_PLANS,
    GLOBAL_EXCLUDED_DIRS,
    REPORTS_DIR,
    SOVEREIGN_EXCLUDED_FOLDERS,
    TESTS_UNIT_DIR,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import _emit_reads_through

SSOT_TARGETS: list[tuple[str, str, str, str]] = [(ARCHIVES_DIR, 'ARCHIVES_DIR', 'agentic_core.L0_routing.config.path_constants', 'root_dir'), (AGENTIC_CORE_DIR, 'AGENTIC_CORE_DIR', 'agentic_core.L0_routing.config.path_constants', 'root_dir'), (APPS_LIC_DIR, 'APPS_LIC_DIR', 'agentic_core.L0_routing.config.path_constants', 'root_dir'), (APPS_RG_DIR, 'APPS_RG_DIR', 'agentic_core.L0_routing.config.path_constants', 'root_dir'), (APPS_SHARED_DIR, 'APPS_SHARED_DIR', 'agentic_core.L0_routing.config.path_constants', 'root_dir'), (OPS_SCRIPTS_DIR, 'OPS_SCRIPTS_DIR', 'agentic_core.L0_routing.config.path_constants', 'root_dir'), (TESTS_DIR, 'TESTS_DIR', 'agentic_core.L0_routing.config.path_constants', 'root_dir'), (SYSTEM_LEARNING_DIR, 'SYSTEM_LEARNING_DIR', 'agentic_core.L0_routing.config.path_constants', 'root_dir'), (TOOLS_DIR, 'TOOLS_DIR', 'agentic_core.L0_routing.config.path_constants', 'root_dir'), (REPORTS_DIR, 'REPORTS_DIR', 'agentic_core.L5_safety.config.structure_blueprint.ssot', 'root_dir'), ('data', 'DATA_DIR', 'agentic_core.L5_safety.config.structure_blueprint.ssot', 'root_dir'), ('docs', 'DOCS_DIR', 'agentic_core.L5_safety.config.structure_blueprint.ssot', 'root_dir'), ('L0_routing', 'LAYER_ROOTS', 'agentic_core.L5_safety.config.structure_blueprint.ssot', 'layer_root'), ('L1_cognition', 'LAYER_ROOTS', 'agentic_core.L5_safety.config.structure_blueprint.ssot', 'layer_root'), ('L2_execution', 'LAYER_ROOTS', 'agentic_core.L5_safety.config.structure_blueprint.ssot', 'layer_root'), ('L3_orchestration', 'LAYER_ROOTS', 'agentic_core.L5_safety.config.structure_blueprint.ssot', 'layer_root'), ('L4_state', 'LAYER_ROOTS', 'agentic_core.L5_safety.config.structure_blueprint.ssot', 'layer_root'), ('L5_safety', 'LAYER_ROOTS', 'agentic_core.L5_safety.config.structure_blueprint.ssot', 'layer_root'), ('L6_observability', 'LAYER_ROOTS', 'agentic_core.L5_safety.config.structure_blueprint.ssot', 'layer_root'), (L0_MAINTENANCE_DIR, 'L0_ROUTING_DIR', 'agentic_core.L0_routing.config.path_constants', 'layer_path'), (L1_COGNITION_DIR, 'L1_COGNITION_DIR', 'agentic_core.L0_routing.config.path_constants', 'layer_path'), (L2_EXECUTION_DIR, 'L2_EXECUTION_DIR', 'agentic_core.L0_routing.config.path_constants', 'layer_path'), (L3_ORCHESTRATION_DIR, 'L3_ORCHESTRATION_DIR', 'agentic_core.L0_routing.config.path_constants', 'layer_path'), (L4_STATE_DIR, 'L4_STATE_DIR', 'agentic_core.L0_routing.config.path_constants', 'layer_path'), (L5_SAFETY_DIR, 'L5_SAFETY_DIR', 'agentic_core.L0_routing.config.path_constants', 'layer_path'), (L6_OBSERVABILITY_DIR, 'L6_OBSERVABILITY_DIR', 'agentic_core.L0_routing.config.path_constants', 'layer_path'), ('agentic_core/L6_observability/dashboards', 'DASHBOARD_DIR', 'agentic_core.L5_safety.config.structure_blueprint.ssot', 'compound_path'), ('agentic_core/config/core', 'BLUEPRINT_SOVEREIGN_DIR', 'agentic_core.L5_safety.config.structure_blueprint.ssot', 'compound_path'), ('agentic_core/runtime/types', 'SCHEMAS_DIR', 'agentic_core.L5_safety.config.structure_blueprint.ssot', 'compound_path'), ('agentic_core/prompt_governance', 'PROMPT_GOVERNANCE_DIR', 'agentic_core.L5_safety.config.structure_blueprint.ssot', 'compound_path'), ('agentic_core/utils', 'UTILS_DIR', 'agentic_core.L5_safety.config.structure_blueprint.ssot', 'compound_path'), ('agentic_core/runtime', 'RUNTIME_DIR', 'agentic_core.L5_safety.config.structure_blueprint.ssot', 'compound_path'), (DOCS_REPORTS_PLANS, 'DOCS_REPORTS_PLANS', 'agentic_core.L5_safety.config.structure_blueprint.ssot', 'compound_path'), ('reports/coverage_html', 'COVERAGE_HTML_DIR', 'agentic_core.L5_safety.config.structure_blueprint.ssot', 'compound_path'), (TESTS_UNIT_DIR, 'TESTS_UNIT_DIR', 'agentic_core.L5_safety.config.structure_blueprint.ssot', 'test_path'), ('tests/integration', 'TESTS_INTEGRATION_DIR', 'agentic_core.L5_safety.config.structure_blueprint.ssot', 'test_path'), ('tests/e2e', 'TESTS_E2E_DIR', 'agentic_core.L5_safety.config.structure_blueprint.ssot', 'test_path'), ('tests/unit_min_deps', 'TESTS_AUTOGEN_DIR', 'agentic_core.L5_safety.config.structure_blueprint.ssot', 'test_path'), ('tests/unit/agentic_core', 'TEST_CANONICAL_LOCATION_MAP', 'agentic_core.L5_safety.config.structure_blueprint.ssot', 'test_path'), ('tests/unit/apps_lic', 'TEST_CANONICAL_LOCATION_MAP', 'agentic_core.L5_safety.config.structure_blueprint.ssot', 'test_path'), ('tests/unit/apps_rg', 'TEST_CANONICAL_LOCATION_MAP', 'agentic_core.L5_safety.config.structure_blueprint.ssot', 'test_path'), ('tests/unit/apps_shared', 'TEST_CANONICAL_LOCATION_MAP', 'agentic_core.L5_safety.config.structure_blueprint.ssot', 'test_path'), ('tests/unit/system_learning', 'TEST_CANONICAL_LOCATION_MAP', 'agentic_core.L5_safety.config.structure_blueprint.ssot', 'test_path'), ('runtime_state.json', 'RUNTIME_STATE_JSON', 'agentic_core.L0_routing.config.path_constants', 'filename'), ('agent_discovery_full.json', 'AGENT_DISCOVERY_JSON', 'agentic_core.L5_safety.config.structure_blueprint.ssot', 'filename'), ('agent_discovery_full.manifest.json', 'AGENT_DISCOVERY_MANIFEST_JSON', 'agentic_core.L5_safety.config.structure_blueprint.ssot', 'filename')]
_TARGET_MAP: dict[str, tuple[str, str, str]] = {v: (c, m, t) for v, c, m, t in SSOT_TARGETS}
WRONG_IMPORT_PATTERNS: list[tuple[str, str]] = [('structure_blueprint_config', 'agentic_core.L5_safety.config.structure_blueprint'), ('agentic_core.L5_safety.config.structure_blueprint_config', 'agentic_core.L5_safety.config.structure_blueprint')]
SCAN_ROOTS: list[str] = [AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR, OPS_SCRIPTS_DIR, TESTS_DIR, TOOLS_DIR, SYSTEM_LEARNING_DIR, 'data', 'docs']
SSot_DEFINITION_FILES: frozenset[str] = frozenset({'agentic_core/L0_routing/config/path_constants.py', 'agentic_core/L5_safety/config/structure_blueprint/ssot.py', 'agentic_core/L5_safety/config/structure_blueprint/_constants.py', 'agentic_core/L5_safety/config/structure_blueprint/_verify.py'})
EXCLUDE_DIRS: frozenset[str] = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES
PATH_PARENT_TYPES: frozenset[str] = frozenset({'BinOp', 'Call', 'Attribute', 'Assign', 'AugAssign', 'AnnAssign', 'Return', 'keyword', 'JoinedStr', 'List', 'Tuple'})

def _get_project_root() -> Path:
    current = Path(__file__).resolve()
    for parent in [current, *current.parents]:
        if (parent / 'pyproject.toml').exists() or (parent / '.git').exists():
            return parent
    return Path.cwd()

def _is_already_using_constant(line_text: str) -> bool:
    """Return True if the line already references an SSOT constant."""
    ssot_suffixes = ('_DIR', '_ROOT', '_ROOTS', '_MAP', '_JSON', '_PLANS', '_BASE')
    return any(s in line_text for s in ssot_suffixes)

def _is_dict_key_or_comparison(value: str, line_text: str) -> bool:
    """Return True for dict-key lookups, startswith/endswith — not path constructions."""
    checks = (f'.get("{value}"', f".get('{value}'", f'["{value}"]', f"['{value}']", f'.startswith("{value}"', f".startswith('{value}'", f'.endswith("{value}"', f".endswith('{value}'", f'.index("{value}"', f".index('{value}'", f'.split("{value}"', f".split('{value}'", f'== "{value}"', f"== '{value}'", f'!= "{value}"', f"!= '{value}'", f'in "{value}"', f"in '{value}'")
    return any(p in line_text for p in checks)

def _classify_string_hit(node: ast.Constant, tree: ast.Module, source_lines: list[str], file_path: Path) -> str:
    value: str = node.value
    line_idx = node.lineno - 1
    line_text = source_lines[line_idx] if line_idx < len(source_lines) else ''
    if line_text.lstrip().startswith('#'):
        return 'SKIP_COMMENT'
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            if child is node:
                if isinstance(parent, ast.Expr) and isinstance(parent.value, ast.Constant):
                    return 'SKIP_COMMENT'
    if _is_already_using_constant(line_text):
        return 'SKIP_COMMENT'
    if _is_dict_key_or_comparison(value, line_text):
        return 'SKIP_DYNAMIC'
    test_data_signals = ('test_', '_test', 'assert', 'expected', 'fixture', 'parametrize', 'EXPECTED', 'pytest.param')
    is_test_file = any(s in str(file_path) for s in ('test_', '_test', 'tests/', 'tests\\'))
    if is_test_file:
        if any(sig in line_text for sig in test_data_signals):
            return 'SKIP_TEST_DATA'
        if 'assert' in line_text or 'expected' in line_text.lower():
            return 'SKIP_TEST_DATA'
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            if child is node:
                ptype = type(parent).__name__
                if ptype in PATH_PARENT_TYPES:
                    return 'REPLACE'
                if ptype in ('Compare', 'If', 'Assert'):
                    return 'SKIP_DYNAMIC'
    return 'SKIP_DYNAMIC'

def _scan_imports(tree: ast.Module, file_path: Path, project_root: Path) -> list[dict]:
    """Detect WRONG_IMPORT violations in import statements."""
    hits = []
    rel = str(file_path.relative_to(project_root))
    for node in ast.walk(tree):
        if isinstance(node, (ast.ImportFrom, ast.Import)):
            if isinstance(node, ast.ImportFrom):
                module = node.module or ''
            else:
                for alias in node.names:
                    module = alias.name
                    for bad, good in WRONG_IMPORT_PATTERNS:
                        if bad in module:
                            hits.append({'file': rel, 'line': node.lineno, 'col': 0, 'value': module, 'ssot_constant': good, 'classification': 'WRONG_IMPORT', 'category': 'wrong_import', 'context': f'import {module}', 'canonical_module': good})
                continue
            for bad, good in WRONG_IMPORT_PATTERNS:
                if bad in module:
                    if 'structure_blueprint_config' in rel:
                        continue
                    hits.append({'file': rel, 'line': node.lineno, 'col': 0, 'value': module, 'ssot_constant': good, 'classification': 'WRONG_IMPORT', 'category': 'wrong_import', 'context': f'from {module} import ...', 'canonical_module': good})
    return hits

def scan_file(file_path: Path, project_root: Path) -> list[dict]:
    hits = []
    try:
        source = file_path.read_text(encoding='utf-8', errors='replace')
        tree = ast.parse(source, filename=str(file_path))
    except (SyntaxError, OSError, UnicodeDecodeError):    # guardian: Parsing and encoding errors need separate handling strategies
        return []
    source_lines = source.splitlines()
    rel = str(file_path.relative_to(project_root)).replace('\\', '/')
    is_definition_site = rel in SSot_DEFINITION_FILES
    for node in ast.walk(tree):
        if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
            continue
        value = node.value
        entry = _TARGET_MAP.get(value)
        if entry is None:
            continue
        constant, canonical_module, category = entry
        if is_definition_site:
            classification = 'SKIP_DYNAMIC'
        else:
            classification = _classify_string_hit(node, tree, source_lines, file_path)
        line_idx = node.lineno - 1
        context = source_lines[line_idx].strip() if line_idx < len(source_lines) else ''
        hits.append({'file': rel, 'line': node.lineno, 'col': node.col_offset, 'value': value, 'ssot_constant': constant, 'classification': classification, 'category': category, 'context': context, 'canonical_module': canonical_module})
    hits.extend(_scan_imports(tree, file_path, project_root))
    return hits

def scan_all(project_root: Path) -> list[dict]:
    all_hits: list[dict] = []
    files_scanned = 0
    files_skipped = 0
    for root_name in SCAN_ROOTS:
        root_path = project_root / root_name
        if not root_path.exists():
            continue
        for py_file in root_path.rglob('*.py'):
            if any(part in EXCLUDE_DIRS for part in py_file.parts):
                files_skipped += 1
                continue
            files_scanned += 1
            all_hits.extend(scan_file(py_file, project_root))
    print(f'[scanner] Scanned {files_scanned} files, skipped {files_skipped}')
    return all_hits

def build_report(hits: list[dict]) -> dict:
    classifications = ['REPLACE', 'WRONG_IMPORT', 'SKIP_COMMENT', 'SKIP_TEST_DATA', 'SKIP_DYNAMIC']
    by_cls: dict[str, list[dict]] = {c: [] for c in classifications}
    by_constant: dict[str, list[dict]] = {}
    by_category: dict[str, list[dict]] = {}
    by_file: dict[str, list[dict]] = {}
    for h in hits:
        cls = h['classification']
        by_cls.setdefault(cls, []).append(h)
        by_constant.setdefault(h['ssot_constant'], []).append(h)
        by_category.setdefault(h['category'], []).append(h)
        by_file.setdefault(h['file'], []).append(h)
    actionable = by_cls['REPLACE'] + by_cls['WRONG_IMPORT']
    file_counts: dict[str, int] = {}
    for h in actionable:
        file_counts[h['file']] = file_counts.get(h['file'], 0) + 1
    top_files = sorted(file_counts.items(), key=lambda x: -x[1])[:30]
    summary = {'total_hits': len(hits), 'replace_count': len(by_cls['REPLACE']), 'wrong_import_count': len(by_cls.get('WRONG_IMPORT', [])), 'skip_comment_count': len(by_cls['SKIP_COMMENT']), 'skip_test_data_count': len(by_cls['SKIP_TEST_DATA']), 'skip_dynamic_count': len(by_cls['SKIP_DYNAMIC']), 'actionable_total': len(actionable), 'by_constant': {k: len(v) for k, v in sorted(by_constant.items(), key=lambda x: -len(x[1]))}, 'by_category': {k: len(v) for k, v in sorted(by_category.items(), key=lambda x: -len(x[1]))}, 'top_offending_files': [{'file': f, 'count': c} for f, c in top_files]}
    return {'summary': summary, 'hits_by_classification': by_cls, 'hits_by_constant': dict(by_constant.items()), 'hits_by_category': by_category, 'all_hits': hits}

def main() -> int:
    summary_only = '--summary' in sys.argv
    filter_cat = None
    if '--category' in sys.argv:
        idx = sys.argv.index('--category')
        if idx + 1 < len(sys.argv):
            filter_cat = sys.argv[idx + 1].upper()
    project_root = _get_project_root()
    print(f'[scanner] Project root: {project_root}')
    print(f'[scanner] Targets: {len(SSOT_TARGETS)} string constants + {len(WRONG_IMPORT_PATTERNS)} import patterns')
    print(f'[scanner] Scanning {len(SCAN_ROOTS)} SOVEREIGN_TERRITORIES...')
    hits = scan_all(project_root)
    report = build_report(hits)
    output_path = project_root / 'artifacts' / 'ssot_violation_scan.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(f'\n[scanner] Report written to: {output_path.relative_to(project_root)}')
    s = report['summary']
    w = 62
    print(f"\n{'=' * w}")
    print('SSOT VIOLATION SCAN — SUMMARY')
    print(f"{'=' * w}")
    print(f"  Total hits          : {s['total_hits']}")
    print(f"  REPLACE             : {s['replace_count']}  ← path construction, swap to constant")
    print(f"  WRONG_IMPORT        : {s['wrong_import_count']}  ← bad import path, use canonical")
    print(f"  SKIP_DYNAMIC        : {s['skip_dynamic_count']}  ← manual review")
    print(f"  SKIP_COMMENT        : {s['skip_comment_count']}")
    print(f"  SKIP_TEST_DATA      : {s['skip_test_data_count']}")
    print(f"  ── Actionable total : {s['actionable_total']}")
    print('\n  By category:')
    for cat, cnt in sorted(s['by_category'].items(), key=lambda x: -x[1]):
        print(f'    {cat:<25} {cnt}')
    print('\n  By constant (top 20):')
    for const, cnt in list(s['by_constant'].items())[:20]:
        print(f'    {const:<35} {cnt}')
    print('\n  Top offending files:')
    for entry in s['top_offending_files'][:20]:
        print(f"    [{entry['count']:>3}]  {entry['file']}")
    if summary_only:
        return 0
    show_cats = [filter_cat] if filter_cat else ['REPLACE', 'WRONG_IMPORT']
    for cat in show_cats:
        cat_hits = report['hits_by_classification'].get(cat, [])
        if not cat_hits:
            continue
        print(f"\n{'=' * w}")
        print(f'{cat} HITS ({len(cat_hits)} total)')
        print(f"{'=' * w}")
        for h in cat_hits:
            print(f"  {h['file']}:{h['line']}  [{h['ssot_constant']}]  <{h['category']}>")
            print(f"    {h['context']}")
    return 0
if __name__ == '__main__':
    sys.exit(main())
