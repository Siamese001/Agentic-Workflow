"""AST-based skip site auditor across all test files."""
import ast
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)

root = Path('c:/Git/Agentic-Workflow/tests')
out = []
for path in sorted(root.rglob('test_*.py')):
    try:
        src = path.read_text(encoding='utf-8', errors='replace')
        tree = ast.parse(src)
    # guardian: allow-silent-swallow - acceptable exception handling
    except SyntaxError:
        continue
    rel = str(path.relative_to(root))
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr == 'importorskip':
            args = [ast.unparse(a) for a in node.args]
            out.append(f'importorskip|{rel}|{node.lineno}|{args}')
        elif isinstance(func, ast.Attribute) and func.attr == 'skip' and isinstance(func.value, ast.Name) and (func.value.id == 'pytest'):
            rawargs = [ast.unparse(a) for a in node.args]
            reason = rawargs[0].strip('"\'') if rawargs else ''
            out.append(f'pytest.skip|{rel}|{node.lineno}|{reason[:140]}')
Path('c:/Git/Agentic-Workflow/skip_audit.txt').write_text('\n'.join(out), encoding='utf-8')
print(f'TOTAL SKIP SITES: {len(out)}')
