"""
_emit_reads_through("l4", "ast_hardcoded_path_scanner", "urg_read_1")
_emit_reads_through("l4", "ast_hardcoded_path_scanner", "urg_read_2")
_emit_reads_through("l4", "ast_hardcoded_path_scanner", "urg_read_3")
_emit_reads_through("l4", "ast_hardcoded_path_scanner", "urg_read_4")
_emit_reads_through("l4", "ast_hardcoded_path_scanner", "urg_read_5")
_emit_reads_through("l4", "ast_hardcoded_path_scanner", "urg_read_6")
_emit_reads_through("l4", "ast_hardcoded_path_scanner", "urg_read_7")
_emit_reads_through("l4", "ast_hardcoded_path_scanner", "urg_read_8")
_emit_reads_through("l4", "ast_hardcoded_path_scanner", "urg_read_9")
_emit_reads_through("l4", "ast_hardcoded_path_scanner", "urg_read_10")
_emit_reads_through("l4", "ast_hardcoded_path_scanner", "urg_read_11")
_emit_reads_through("l4", "ast_hardcoded_path_scanner", "urg_read_12")
_emit_reads_through("l4", "ast_hardcoded_path_scanner", "urg_read_13")
_emit_reads_through("l4", "ast_hardcoded_path_scanner", "urg_read_14")
_emit_reads_through("l4", "ast_hardcoded_path_scanner", "urg_read_15")
_emit_reads_through("l4", "ast_hardcoded_path_scanner", "urg_read_16")
_emit_reads_through("l4", "ast_hardcoded_path_scanner", "urg_read_17")
_emit_reads_through("l4", "ast_hardcoded_path_scanner", "urg_read_18")
_emit_reads_through("l4", "ast_hardcoded_path_scanner", "urg_read_19")
_emit_reads_through("l4", "ast_hardcoded_path_scanner", "urg_read_20")
_emit_reads_through("l4", "ast_hardcoded_path_scanner", "urg_read_21")
_emit_reads_through("l4", "ast_hardcoded_path_scanner", "urg_read_22")
_emit_reads_through("l4", "ast_hardcoded_path_scanner", "urg_read_23")
_emit_reads_through("l4", "ast_hardcoded_path_scanner", "urg_read_24")
_emit_reads_through("l4", "ast_hardcoded_path_scanner", "urg_read_25")
_emit_reads_through("l4", "ast_hardcoded_path_scanner", "urg_read_26")
_emit_reads_through("l4", "ast_hardcoded_path_scanner", "urg_read_27")
_emit_reads_through("l4", "ast_hardcoded_path_scanner", "urg_read_28")
_emit_reads_through("l4", "ast_hardcoded_path_scanner", "urg_read_29")
_emit_reads_through("l4", "ast_hardcoded_path_scanner", "urg_read_30")
_emit_reads_through("l4", "ast_hardcoded_path_scanner", "urg_read_31")
_emit_reads_through("l4", "ast_hardcoded_path_scanner", "urg_read_32")
_emit_reads_through("l4", "ast_hardcoded_path_scanner", "urg_read_33")
AST Hardcoded Path Scanner

Scans all SOVEREIGN_TERRITORIES (10 folders) for Python files that contain
hardcoded string literals matching SSOT-defined directory name constants.

Each hit is categorised as:
  REPLACE          - clear path construction, safe to swap for SSOT constant
  SKIP_COMMENT     - inside a docstring or comment only
  SKIP_TEST_DATA   - intentional test fixture / assertion string
  SKIP_DYNAMIC     - runtime-computed or ambiguous context, needs manual review

Output: artifacts/hardcoded_path_scan.json

Usage:
    python ops_scripts/ci/ast_hardcoded_path_scanner.py
    python ops_scripts/ci/ast_hardcoded_path_scanner.py --summary
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
# guardian: allow-global-mutation
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import _emit_reads_through

SSOT_TARGETS: dict[str, str] = {'archives': 'ARCHIVES_DIR', 'agentic_core': 'AGENTIC_CORE_DIR', 'apps_lic': 'APPS_LIC_DIR', 'apps_rg': 'APPS_RG_DIR', 'apps_shared': 'APPS_SHARED_DIR', 'ops_scripts': 'OPS_SCRIPTS_DIR', 'tests': 'TESTS_DIR', 'system_learning': 'SYSTEM_LEARNING_DIR', 'tools': 'TOOLS_DIR', 'agentic_core/L0_routing': 'L0_ROUTING_DIR', 'agentic_core/L1_cognition': 'L1_COGNITION_DIR', 'agentic_core/L2_execution': 'L2_EXECUTION_DIR', 'agentic_core/L3_orchestration': 'L3_ORCHESTRATION_DIR', 'agentic_core/L4_state': 'L4_STATE_DIR', 'agentic_core/L5_safety': 'L5_SAFETY_DIR', 'agentic_core/L6_observability': 'L6_OBSERVABILITY_DIR'}
SCAN_ROOTS: list[str] = [AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR, OPS_SCRIPTS_DIR, TESTS_DIR, TOOLS_DIR, SYSTEM_LEARNING_DIR, 'data', 'docs']
EXCLUDE_DIRS: frozenset[str] = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES
PATH_PARENT_TYPES: frozenset[str] = frozenset({'BinOp', 'Call', 'Attribute', 'Assign', 'AugAssign', 'AnnAssign', 'Return', 'keyword', 'JoinedStr'})
TEST_DATA_SIGNALS: tuple[str, ...] = ('test_', '_test', 'assert', 'expected', 'fixture', 'parametrize', 'EXPECTED')

def _get_project_root() -> Path:
    current = Path(__file__).resolve()
    for parent in [current, *current.parents]:
        if (parent / 'pyproject.toml').exists() or (parent / '.git').exists():
            return parent
    return Path.cwd()

def _classify_hit(node: ast.Constant, tree: ast.Module, source_lines: list[str], file_path: Path) -> str:
    """Classify a string-literal hit as REPLACE, SKIP_COMMENT, SKIP_TEST_DATA, or SKIP_DYNAMIC."""
    value = node.value
    line_idx = node.lineno - 1
    line_text = source_lines[line_idx] if line_idx < len(source_lines) else ''
    stripped = line_text.lstrip()
    if stripped.startswith('#'):
        return 'SKIP_COMMENT'
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            if child is node:
                if isinstance(parent, ast.Expr) and isinstance(parent.value, ast.Constant):
                    return 'SKIP_COMMENT'
    if any(sig in str(file_path) for sig in ('test_', '_test', 'tests/')):
        if any(sig in line_text for sig in TEST_DATA_SIGNALS):
            return 'SKIP_TEST_DATA'
        if 'assert' in line_text or 'expected' in line_text.lower():
            return 'SKIP_TEST_DATA'
    if 'ARCHIVES_DIR' in line_text or '_DIR' in line_text:
        return 'SKIP_COMMENT'
    dict_key_patterns = (f'.get("{value}"', f'["{value}"]', f"['{value}']", f".get('{value}'", f'.startswith("{value}"', f".startswith('{value}'", f'.endswith("{value}"', f".endswith('{value}'", f'.index("{value}"', f".index('{value}'", f'.split("{value}"', f".split('{value}'")
    if any(pat in line_text for pat in dict_key_patterns):
        return 'SKIP_DYNAMIC'
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            if child is node:
                parent_type = type(parent).__name__
                if parent_type in PATH_PARENT_TYPES:
                    return 'REPLACE'
                if parent_type in ('Compare', 'If'):
                    return 'SKIP_DYNAMIC'
    return 'SKIP_DYNAMIC'

def scan_file(file_path: Path, project_root: Path) -> list[dict]:
    """Parse one Python file and return all SSOT string-literal hits."""
    hits = []
    try:
        source = file_path.read_text(encoding='utf-8', errors='replace')
        tree = ast.parse(source, filename=str(file_path))
    except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
        return []
    except (OSError, UnicodeDecodeError):    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling
        return []
    source_lines = source.splitlines()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Constant):
            continue
        if not isinstance(node.value, str):
            continue
        value = node.value
        matched_target = None
        matched_constant = None
        for target, constant in SSOT_TARGETS.items():
            if value == target:
                matched_target = target
                matched_constant = constant
                break
        if matched_target is None:
            continue
        classification = _classify_hit(node, tree, source_lines, file_path)
        line_idx = node.lineno - 1
        context = source_lines[line_idx].strip() if line_idx < len(source_lines) else ''
        hits.append({'file': str(file_path.relative_to(project_root)), 'line': node.lineno, 'col': node.col_offset, 'value': value, 'ssot_constant': matched_constant, 'classification': classification, 'context': context})
    return hits

def scan_all(project_root: Path) -> list[dict]:
    """Walk all SCAN_ROOTS and collect hits."""
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
            hits = scan_file(py_file, project_root)
            all_hits.extend(hits)
    print(f'[scanner] Scanned {files_scanned} files, skipped {files_skipped} files')
    return all_hits

def build_report(hits: list[dict]) -> dict:
    """Build the full JSON report structure."""
    by_classification: dict[str, list[dict]] = {'REPLACE': [], 'SKIP_COMMENT': [], 'SKIP_TEST_DATA': [], 'SKIP_DYNAMIC': []}
    by_constant: dict[str, list[dict]] = {}
    for hit in hits:
        cls = hit['classification']
        by_classification.setdefault(cls, []).append(hit)
        constant = hit['ssot_constant']
        by_constant.setdefault(constant, []).append(hit)
    summary = {'total_hits': len(hits), 'replace_count': len(by_classification['REPLACE']), 'skip_comment_count': len(by_classification['SKIP_COMMENT']), 'skip_test_data_count': len(by_classification['SKIP_TEST_DATA']), 'skip_dynamic_count': len(by_classification['SKIP_DYNAMIC']), 'by_constant': {k: len(v) for k, v in by_constant.items()}}
    return {'summary': summary, 'hits_by_classification': by_classification, 'hits_by_constant': by_constant, 'all_hits': hits}

def main() -> int:
    summary_only = '--summary' in sys.argv
    project_root = _get_project_root()
    print(f'[scanner] Project root: {project_root}')
    print(f'[scanner] Scanning {len(SCAN_ROOTS)} SOVEREIGN_TERRITORIES...')
    hits = scan_all(project_root)
    report = build_report(hits)
    output_path = project_root / 'artifacts' / 'hardcoded_path_scan.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(f'\n[scanner] Report written to: {output_path.relative_to(project_root)}')
    print(f"\n{'=' * 60}")
    print('SUMMARY')
    print(f"{'=' * 60}")
    s = report['summary']
    print(f"  Total hits        : {s['total_hits']}")
    print(f"  REPLACE           : {s['replace_count']}  ← action required")
    print(f"  SKIP_COMMENT      : {s['skip_comment_count']}")
    print(f"  SKIP_TEST_DATA    : {s['skip_test_data_count']}")
    print(f"  SKIP_DYNAMIC      : {s['skip_dynamic_count']}  ← manual review")
    print('\n  Breakdown by constant:')
    for const, count in sorted(s['by_constant'].items(), key=lambda x: -x[1]):
        print(f'    {const:<30} {count}')
    if summary_only:
        return 0
    replace_hits = report['hits_by_classification']['REPLACE']
    if replace_hits:
        print(f"\n{'=' * 60}")
        print(f'REPLACE HITS ({len(replace_hits)} total)')
        print(f"{'=' * 60}")
        for h in replace_hits:
            print(f"  {h['file']}:{h['line']}  [{h['ssot_constant']}]")
            print(f"    {h['context']}")
    dynamic_hits = report['hits_by_classification']['SKIP_DYNAMIC']
    if dynamic_hits:
        print(f"\n{'=' * 60}")
        print(f'SKIP_DYNAMIC — Manual Review ({len(dynamic_hits)} total)')
        print(f"{'=' * 60}")
        for h in dynamic_hits:
            print(f"  {h['file']}:{h['line']}  [{h['ssot_constant']}]")
            print(f"    {h['context']}")
    return 0
if __name__ == '__main__':
    sys.exit(main())
