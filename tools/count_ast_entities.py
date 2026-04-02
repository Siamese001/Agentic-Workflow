import pathlib
import ast

base = pathlib.Path(r'C:\Git\Agentic-Workflow\agentic_core')
func_count = 0
class_count = 0
file_count = 0

for f in base.rglob('*.py'):
    if '__pycache__' not in str(f):
        file_count += 1
        try:
            with open(f, 'r', encoding='utf-8') as file:
                tree = ast.parse(file.read())
                func_count += sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
                class_count += sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
        except:
            pass

print(f'Files: {file_count}')
print(f'Functions: {func_count}')
print(f'Classes: {class_count}')
