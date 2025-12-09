"""Add docstrings to functions/classes missing them."""
import ast
import os
from pathlib import Path

sovereign_dirs = [
    'agentic_core', 'apps_lic', 'apps_rg', 'apps_shared',
    'schemas', 'prompt_governance', 'observability', 'config'
]
fixed_count = 0


def get_body_start_line(node: ast.AST) -> int:
    """Get the line number where the function/class body starts."""
    if hasattr(node, 'body') and node.body:
        return node.body[0].lineno
    return node.lineno + 1


for sdir in sovereign_dirs:
    if not os.path.exists(sdir):
        continue
    for pyfile in Path(sdir).rglob('*.py'):
        try:
            content = pyfile.read_text(encoding='utf-8')
            tree = ast.parse(content)

            # Find functions/classes without docstrings
            needs_fix = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    if node.name.startswith('_'):
                        continue
                    if ast.get_docstring(node) is None:
                        body_line = get_body_start_line(node)
                        needs_fix.append((body_line, node.name, type(node).__name__, node.col_offset))

            if not needs_fix:
                continue

            # Sort by line number descending to avoid offset issues
            needs_fix.sort(key=lambda x: x[0], reverse=True)

            lines = content.split('\n')
            for body_line, name, node_type, col_offset in needs_fix:
                idx = body_line - 1
                if idx >= len(lines) or idx < 0:
                    continue

                body_indent = ' ' * (col_offset + 4)

                if node_type == 'ClassDef':
                    docstring = f'{body_indent}"""{name} implementation."""'
                else:
                    docstring = f'{body_indent}"""Execute {name} operation."""'

                # Insert docstring before the first body statement
                lines.insert(idx, docstring)

            pyfile.write_text('\n'.join(lines), encoding='utf-8')
            fixed_count += 1
            print(f'Fixed: {pyfile}')
        except SyntaxError:
            print(f'Syntax error in: {pyfile}')
        except (ValueError, TypeError, RuntimeError, OSError) as e:
            print(f'Error in {pyfile}: {e}')

print(f'Total files fixed: {fixed_count}')
