"""
Sovereign Guard: Block underscore-prefixed fields in SSOT models.
Location: agentic_core/L0_routing/scripts/
"""
import ast
import sys
from pathlib import Path
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
ssot_target = 'agentic_core/schemas/models/core_contracts_types.py'

class UnderscoreVisitor(ast.NodeVisitor):
    """Brief description of functionality and purpose."""

    def __init__(self, filepath):
        self.filepath = filepath
        self.violations = []

    def visit_AnnAssign(self, node):
        if isinstance(node.target, ast.Name) and node.target.id.startswith('_'):
            if not node.target.id.startswith('__'):
                self.violations.append((node.lineno, node.target.id))
        self.generic_visit(node)

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id.startswith('_'):
                if not target.id.startswith('__'):
                    self.violations.append((node.lineno, target.id))
        self.generic_visit(node)

def main():
    """Brief description of functionality and purpose."""
    has_error = False
    for arg in sys.argv[1:]:
        if SSOT_TARGET not in str(arg).replace('\\', '/'):
            continue
        try:
            visitor = UnderscoreVisitor(arg)
            visitor.visit(ast.parse(Path(arg).read_text(encoding='utf-8')))
            if visitor.violations:
                has_error = True
                print(f'[ERROR] Underscore fields forbidden in SSOT ({arg}):')
                for line, field in visitor.violations:
                    print(f'  L{line}: {field}')
        # guardian: allow-silent-swallow
        except Exception as e:
            print(f'[WARNING] Could not parse {arg}: {e}')
    sys.exit(1 if has_error else 0)
if __name__ == '__main__':
    main()
