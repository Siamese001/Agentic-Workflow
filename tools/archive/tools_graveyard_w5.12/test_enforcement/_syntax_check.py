"""Quick syntax check across all test files."""

import ast
import pathlib

root = pathlib.Path(".")
errs = 0
ok = 0
err_files = []

for f in sorted(pathlib.Path("tests").rglob("test_*.py")):
    try:
        ast.parse(f.read_text(encoding="utf-8", errors="replace"))
        ok += 1
    except SyntaxError:
        errs += 1
        err_files.append(str(f).replace("\\", "/"))

# Also root test files
for f in sorted(root.glob("test_*.py")):
    try:
        ast.parse(f.read_text(encoding="utf-8", errors="replace"))
        ok += 1
    except SyntaxError:
        errs += 1
        err_files.append(str(f).replace("\\", "/"))

print(f"OK: {ok}, Syntax errors: {errs}")
if err_files:
    print("Error files:")
    for f in err_files:
        print(f"  {f}")
