"""Add docstrings to functions/classes missing them."""
import ast
import os
from pathlib import Path

sovereign_dirs = ['agentic_core', 'apps_lic', 'apps_rg', 'apps_shared', 'schemas', 'prompt_governance', 'observability', 'config']
fixed_count = 0

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
                        needs_fix.append((node.lineno, node.name, type(node).__name__))
            
            if not needs_fix:
                continue
                
            # Add docstrings by line
            lines = content.split('\n')
            offset = 0
            for lineno, name, node_type in sorted(needs_fix):
                idx = lineno - 1 + offset
                if idx >= len(lines):
                    continue
                line = lines[idx]
                indent = len(line) - len(line.lstrip())
                body_indent = ' ' * (indent + 4)
                
                if node_type == 'ClassDef':
                    docstring = f'{body_indent}"""{name} implementation."""'
                else:
                    docstring = f'{body_indent}"""Execute {name} operation."""'
                
                # Insert after the def/class line
                lines.insert(idx + 1, docstring)
                offset += 1
            
            pyfile.write_text('\n'.join(lines), encoding='utf-8')
            fixed_count += 1
            print(f'Fixed: {pyfile.name}')
        except (ValueError, TypeError, RuntimeError, OSError) as e:
            pass

print(f'Total files fixed: {fixed_count}')
