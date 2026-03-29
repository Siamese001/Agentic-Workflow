import os
import ast

errors = []
for root, dirs, files in os.walk('tests/unit/agentic_core'):
    for f in files:
        if f.endswith('.py') and f.startswith('test_'):
            filepath = os.path.join(root, f)
            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    ast.parse(file.read())
            except SyntaxError as e:
                errors.append(f'{filepath}: {e}')
            except Exception as e:
                errors.append(f'{filepath}: {e}')

print(f'Syntax errors found: {len(errors)}')
for e in errors[:20]:
    print(e)
