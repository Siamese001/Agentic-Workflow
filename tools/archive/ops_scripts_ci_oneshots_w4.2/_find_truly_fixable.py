"""Search for truly fixable SSOT hardcoding cases."""
import ast
import os
import sys
from pathlib import Path

# guardian: allow-global-mutation
sys.path.insert(0, '.')
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    ENFORCED_TERRITORIES,
    SOVEREIGN_EXCLUDED_FOLDERS,
)
from ops_scripts.ci._fix_hardcoded_ssot_literals import CONST_DEFS

ROOT = Path('.')
truly_fixable = []
literal_to_const = {literal: (const, module) for const, literal, module in CONST_DEFS}
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
            try:
                content = fpath.read_text(encoding='utf-8', errors='replace')
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Constant) and isinstance(node.value, str):
                        if node.value in literal_to_const:
                            const, module = literal_to_const[node.value]
                            parent = None
                            for p in ast.walk(tree):
                                if hasattr(p, 'body') or hasattr(p, 'elts') or hasattr(p, 'args'):
                                    if isinstance(p, ast.List) and node in p.elts:
                                        parent_of_list = None
                                        for gp in ast.walk(tree):
                                            if hasattr(gp, 'value') and gp.value is p:
                                                parent_of_list = gp
                                                break
                                            elif hasattr(gp, 'elts') and p in gp.elts:
                                                parent_of_list = gp
                                                break
                                        if not isinstance(parent_of_list, ast.Dict):
                                            truly_fixable.append((str(fpath.relative_to(ROOT)), node.lineno, node.value, const))
                            if isinstance(p, ast.Call) and node in p.args:
                                if hasattr(p.func, 'attr') and p.func.attr in ('add', 'append'):
                                    truly_fixable.append((str(fpath.relative_to(ROOT)), node.lineno, node.value, const))
            except (OSError, UnicodeDecodeError, SyntaxError):    # guardian: Parsing and encoding errors need separate handling strategies
                pass
print('Truly fixable cases:')
for p, l, val, const in truly_fixable:
    print(f'  {p}:{l} "{val}" -> {const}')
