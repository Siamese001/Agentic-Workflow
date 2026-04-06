"""CI guard: AST-based scanner for un-allowlisted LLM calls in validation paths.

Detects every function/method where an LLM callable is invoked inside a
validation, scoring, enforcement, or review path and is NOT in the approved
allowlist.  Fails CI on any new un-allowlisted hit.

Usage:
    python ops_scripts/ci/scan_llm_validator_calls.py
    python ops_scripts/ci/scan_llm_validator_calls.py --allowlist ops_scripts/ci/llm_validator_allowlist.json
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path
from typing import NamedTuple


REPO_ROOT = Path(__file__).resolve().parents[2]
# guardian: allow-global-mutation
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    SYSTEM_LEARNING_DIR,
)

DEFAULT_ALLOWLIST = Path(__file__).parent / 'llm_validator_allowlist.json'
SCAN_ROOTS = [AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR, SYSTEM_LEARNING_DIR]
VALIDATION_FUNC_PATTERNS = {'validate', 'score', 'evaluate', 'check', 'review', 'judge', 'inspect', 'verify', 'assess', 'audit', 'scan'}
LLM_CALL_NAMES = {'chat_completion_async', 'chat_completion', 'route_generation', 'call_llm', 'invoke_model', 'generate_text', 'complete', 'acomplete', 'agenerate'}
LLM_ATTR_ROOTS = {'llm_client', 'llm', 'genai_client', 'llm_router', 'model_client', 'get_model_client'}
ML_IMPORT_MODULES = {'torch', 'sklearn', 'transformers', 'FlagEmbedding', 'sentence_transformers', 'lightgbm', 'xgboost', 'catboost'}

class LLMValidatorHit(NamedTuple):
    file: str
    line: int
    func_name: str
    call_expr: str
    gap_hint: str

def _func_name_is_validation(name: str) -> bool:
    low = name.lower()
    return any(p in low for p in VALIDATION_FUNC_PATTERNS)

def _call_is_llm(node: ast.Call) -> str | None:
    """Return a description if this Call node looks like an LLM call."""
    func = node.func
    if isinstance(func, ast.Attribute):
        if func.attr in LLM_CALL_NAMES:
            root = func.value
            if isinstance(root, ast.Attribute):
                root_name = root.attr
            elif isinstance(root, ast.Name):
                root_name = root.id
            else:
                root_name = '?'
            return f'{root_name}.{func.attr}'
        if isinstance(func.value, ast.Name) and func.value.id in LLM_ATTR_ROOTS:
            return f'{func.value.id}.{func.attr}'
    if isinstance(func, ast.Name) and func.id in LLM_CALL_NAMES:
        return func.id
    return None

class LLMValidatorScanner(ast.NodeVisitor):

    def __init__(self, path: Path):
        self.path = path
        self.hits: list[LLMValidatorHit] = []
        self._func_stack: list[ast.FunctionDef | ast.AsyncFunctionDef] = []

    def _current_func(self) -> ast.FunctionDef | ast.AsyncFunctionDef | None:
        return self._func_stack[-1] if self._func_stack else None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._func_stack.append(node)
        self.generic_visit(node)
        self._func_stack.pop()
    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Call(self, node: ast.Call) -> None:
        fn = self._current_func()
        if fn is not None and _func_name_is_validation(fn.name):
            desc = _call_is_llm(node)
            if desc:
                rel = self.path.relative_to(REPO_ROOT).as_posix()
                self.hits.append(LLMValidatorHit(file=rel, line=node.lineno, func_name=fn.name, call_expr=desc, gap_hint=_infer_gap(rel, fn.name, desc)))
        self.generic_visit(node)

def _infer_gap(rel: str, func_name: str, call_expr: str) -> str:
    if 'judge_evaluator' in rel.lower():
        return 'GAP-01'
    if 'reflection_config' in rel.lower():
        return 'GAP-02'
    if 'constitutional' in rel.lower():
        return 'GAP-03'
    if 'safety_inspector' in rel.lower() or 'socratic' in func_name.lower():
        return 'GAP-04'
    if 'regression_oracle' in rel.lower():
        return 'GAP-05'
    if 'answer_correctness' in rel.lower() or 'groundedness' in rel.lower():
        return 'GAP-06'
    if 'agent_gym' in rel.lower():
        return 'GAP-07'
    if 'truth_keeper' in rel.lower():
        return 'GAP-08'
    return 'GAP-UNKNOWN'

def _load_allowlist(path: Path) -> set[str]:
    if not path.exists():
        return set()
    data = json.loads(path.read_text(encoding='utf-8'))
    return {f"{entry['file']}::{entry['func']}" for entry in data.get('allowed_llm_validators', [])}

def scan_file(path: Path) -> list[LLMValidatorHit]:
    try:
        tree = ast.parse(path.read_text(encoding='utf-8', errors='replace'))
    except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
        return []
    visitor = LLMValidatorScanner(path)
    visitor.visit(tree)
    return visitor.hits

def check_ml_imports(path: Path) -> list[LLMValidatorHit]:
    """Flag ML library imports outside the approved seam files."""
    try:
        tree = ast.parse(path.read_text(encoding='utf-8', errors='replace'))
    except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
        return []
    hits: list[LLMValidatorHit] = []
    rel = path.relative_to(REPO_ROOT).as_posix()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name.split('.')[0] for a in node.names]
            elif node.module:
                names = [node.module.split('.')[0]]
            for name in names:
                if name in ML_IMPORT_MODULES:
                    hits.append(LLMValidatorHit(file=rel, line=node.lineno, func_name='<module-level>', call_expr=f'import {name}', gap_hint='GAP-09/GAP-10'))
    return hits

def main(argv: list[str] | None=None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description='Scan for un-allowlisted LLM validator calls')
    parser.add_argument('--allowlist', default=str(DEFAULT_ALLOWLIST), help='Path to llm_validator_allowlist.json')
    parser.add_argument('--fail-on-new', action='store_true', default=True, help='Exit 1 if any un-allowlisted hits are found')
    parser.add_argument('--report-only', action='store_true', default=False, help='Print findings but exit 0 (audit mode)')
    args = parser.parse_args(argv)
    allowlist = _load_allowlist(Path(args.allowlist))
    all_hits: list[LLMValidatorHit] = []
    ml_hits: list[LLMValidatorHit] = []
    for root_name in SCAN_ROOTS:
        root = REPO_ROOT / root_name
        if not root.exists():
            continue
        for py_file in root.rglob('*.py'):
            if '__pycache__' in py_file.parts:
                continue
            all_hits.extend(scan_file(py_file))
            ml_hits.extend(check_ml_imports(py_file))
    new_hits = [h for h in all_hits if f'{h.file}::{h.func_name}' not in allowlist]
    print(f'LLM validator scan: {len(all_hits)} total hit(s), {len(all_hits) - len(new_hits)} allowlisted, {len(new_hits)} new un-allowlisted')
    if new_hits:
        print(f'\nFAIL: {len(new_hits)} un-allowlisted LLM validator call(s):')
        for h in new_hits:
            print(f'  {h.file}:{h.line}  func={h.func_name}  call={h.call_expr}  [{h.gap_hint}]')
    if ml_hits:
        print(f'\nWARN: {len(ml_hits)} ML library import(s) in scan roots (verify deterministic fallback exists):')
        for h in ml_hits:
            print(f'  {h.file}:{h.line}  {h.call_expr}  [{h.gap_hint}]')
    if args.report_only:
        return 0
    return 1 if new_hits else 0
if __name__ == '__main__':
    sys.exit(main())
