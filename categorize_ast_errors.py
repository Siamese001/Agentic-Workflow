"""Categorize AST errors by severity and fixability."""
import ast
from pathlib import Path
from collections import defaultdict

target_prefixes = ["agentic_core", "apps_rg", "apps_lic", "apps_shared"]
error_map = defaultdict(list)

for py_file in Path('.').rglob("*.py"):
    rel_path = py_file.relative_to('.')
    if not any(rel_path.parts[0].startswith(prefix) for prefix in target_prefixes):
        continue
    
    try:
        content = py_file.read_text(encoding="utf-8")
        ast.parse(content)
    except SyntaxError as e:
        error_type = e.msg
        error_map[error_type].append((str(py_file), e.lineno))
    except Exception:
        pass

print("AST Error Categories:\n")
for error_type, files in sorted(error_map.items(), key=lambda x: len(x[1]), reverse=True):
    print(f"\n{error_type} ({len(files)} files):")
    for f, line in files[:3]:  # Show first 3
        print(f"  - {f}:{line}")
    if len(files) > 3:
        print(f"  ... and {len(files) - 3} more")

print(f"\n{'='*80}")
print(f"Total files with errors: {sum(len(v) for v in error_map.values())}")
print(f"Unique error types: {len(error_map)}")
