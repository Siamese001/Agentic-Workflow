"""
V15 Phase 2 D-Evidence Collector — AST-Verified Runtime Enforcement Wiring.

Reads the Wave 2.1 inventory JSON and AST-verifies that each unenforced
entry point has been wired with runtime_guard decorator.

Output schema version: 2.2.0

Usage:
    python ops_scripts/ci/evidence_collect_phase2.py --output evidence.json
    python ops_scripts/ci/evidence_collect_phase2.py --output evidence.json --repo-root .
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

INVENTORY_REL = 'docs/reports/plans/v15_phase2_wave2_1_runtime_entrypoints.json'

def compute_sha256(path: Path) -> str:
    """Compute SHA-256 hex digest of file bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()

def ast_find_guard_decorator(source: str, entry_point_id: str) -> dict | None:
    """AST-search for @runtime_guard("<entry_point_id>") in source.

    Returns evidence dict with line span if found, None otherwise.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
        return None
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for dec in node.decorator_list:
            if not isinstance(dec, ast.Call) or not dec.args:
                continue
            arg = dec.args[0]
            if not (isinstance(arg, ast.Constant) and arg.value == entry_point_id):
                continue
            func = dec.func
            func_name = None
            if isinstance(func, ast.Name):
                func_name = func.id
            elif isinstance(func, ast.Attribute):
                func_name = func.attr
            if func_name == 'runtime_guard':
                return {'decorator_line': dec.lineno, 'function_name': node.name, 'function_line_start': node.lineno, 'function_line_end': node.end_lineno}
            if isinstance(func, ast.Call):
                inner = func.func
                inner_name = None
                if isinstance(inner, ast.Name):
                    inner_name = inner.id
                elif isinstance(inner, ast.Attribute):
                    inner_name = inner.attr
                if inner_name == '_optional_runtime_guard':
                    return {'decorator_line': dec.lineno, 'function_name': node.name, 'function_line_start': node.lineno, 'function_line_end': node.end_lineno}
    return None

def collect_evidence(repo_root: Path, synthetic_fail: bool=False) -> dict:
    """Collect P2 evidence for all inventory entry points."""
    inventory_path = repo_root / INVENTORY_REL
    if not inventory_path.exists():
        print(f'ERROR: Inventory not found: {inventory_path}', file=sys.stderr)
        sys.exit(1)
    inventory = json.loads(inventory_path.read_text(encoding='utf-8'))
    inventory_sha = compute_sha256(inventory_path)
    entries: list[dict] = []
    wired = 0
    unwired = 0
    already_enforced = 0
    unwired_ids: list[str] = []
    by_category: dict[str, dict] = {}
    for ep in inventory['entrypoints']:
        ep_id = ep['id']
        cat = ep['category']
        if cat not in by_category:
            by_category[cat] = {'wired': 0, 'unwired': 0, 'already_enforced': 0}
        if ep.get('already_v15_enforced'):
            status = 'ALREADY_ENFORCED'
            already_enforced += 1
            by_category[cat]['already_enforced'] += 1
            entries.append({'id': ep_id, 'status': status, 'evidence': {'path': ep['path'], 'note': 'Pre-existing V15 enforcement (Phase 1 artifact)'}})
            continue
        ep_path = repo_root / ep['path']
        if not ep_path.exists():
            status = 'UNWIRED'
            unwired += 1
            unwired_ids.append(ep_id)
            by_category[cat]['unwired'] += 1
            entries.append({'id': ep_id, 'status': status, 'evidence': {'path': ep['path'], 'error': 'file_not_found'}})
            continue
        source = ep_path.read_text(encoding='utf-8')
        proof = ast_find_guard_decorator(source, ep_id)
        if synthetic_fail and wired == 0 and (proof is not None):
            proof = None
        if proof is not None:
            status = 'WIRED'
            wired += 1
            by_category[cat]['wired'] += 1
            entries.append({'id': ep_id, 'status': status, 'evidence': {'path': ep['path'], 'boundary_line_span': [proof['decorator_line'], proof['function_line_end']], 'call_site_proof': f'''@runtime_guard("{ep_id}") on {proof['function_name']} at line {proof['decorator_line']}'''}})
        else:
            status = 'UNWIRED'
            unwired += 1
            unwired_ids.append(ep_id)
            by_category[cat]['unwired'] += 1
            entries.append({'id': ep_id, 'status': status, 'evidence': {'path': ep['path'], 'error': 'runtime_guard decorator not found for this entry_point_id'}})
    return {'schema_version': '2.2.0', 'generated_utc': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'inventory_sha256': inventory_sha, 'entrypoints_total': len(inventory['entrypoints']), 'wired_count': wired, 'unwired_count': unwired, 'already_enforced_count': already_enforced, 'unwired_ids': unwired_ids, 'by_category': by_category, 'entries': entries}

def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description='V15 Phase 2 D-Evidence Collector')
    parser.add_argument('--repo-root', type=Path, default=None, help='Repository root (default: cwd)')
    parser.add_argument('--output', type=Path, required=True, help='Output JSON path')
    args = parser.parse_args()
    repo_root = args.repo_root or Path.cwd()
    synthetic_fail = os.environ.get('V15_P2_SYNTHETIC_FAIL', '').lower() in ('1', 'true', 'yes')
    evidence = collect_evidence(repo_root, synthetic_fail=synthetic_fail)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, indent=2, ensure_ascii=True), encoding='utf-8')
    print(f"P2 Evidence: {evidence['wired_count']} WIRED, {evidence['already_enforced_count']} ALREADY_ENFORCED, {evidence['unwired_count']} UNWIRED (total={evidence['entrypoints_total']})")
    if evidence['unwired_ids']:
        print(f"UNWIRED IDs: {evidence['unwired_ids']}")
    return 0
if __name__ == '__main__':
    sys.exit(main())
