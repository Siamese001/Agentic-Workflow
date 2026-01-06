import ast
from pathlib import Path

target_prefixes = ["agentic_core", "apps_rg", "apps_lic", "apps_shared"]
errors = []

for py_file in Path('.').rglob("*.py"):
    rel_path = py_file.relative_to('.')
    if not any(rel_path.parts[0].startswith(prefix) for prefix in target_prefixes):
        continue
    
    try:
        ast.parse(py_file.read_text(encoding="utf-8"))
    except SyntaxError as e:
        errors.append({
            'file': str(py_file),
            'line': e.lineno,
            'msg': e.msg
        })
    except Exception:
        pass

print(f"Found {len(errors)} files with AST parse errors:\n")
for err in sorted(errors, key=lambda x: x['file']):
    print(f"{err['file']}:{err['line']} - {err['msg']}")
