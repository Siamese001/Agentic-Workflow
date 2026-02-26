"""Quick check of scanner violation counts for test code."""
import ast
import tempfile
from pathlib import Path
from agentic_core.L5_safety.static_checks.system_invariant_scanner import (
    SystemInvariantScanner,
    scan_repository_for_bypasses,
)

# Test 1: gateway bypass code
code = (
    "import os\n"
    "def f():\n"
    '    open("t.txt","w")\n'
    '    os.remove("x")\n'
    '    open("a.txt","w")  # guardian: allow-direct-write\n'
)
with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
    tmp.write(code)
    p = Path(tmp.name)

s = SystemInvariantScanner(p)
s.visit(ast.parse(code))
print(f"Gateway bypass violations: {len(s.violations)}")
for v in s.violations:
    print(f"  {v.rule_id}: {v.snippet}")
p.unlink()

# Test 2: scan L2_execution bucket
root = Path(__file__).resolve().parents[2]
bucket = root / "agentic_core" / "L2_execution"
print(f"\nL2_execution bucket exists: {bucket.exists()}")
py_files = [f for f in bucket.rglob("*.py") if "__pycache__" not in f.parts]
print(f"L2_execution .py files: {len(py_files)}")
violations = scan_repository_for_bypasses(bucket)
prefix = str(bucket)
filtered = [v for v in violations if str(Path(v.file_path).resolve()).startswith(prefix)]
print(f"L2_execution violations: {len(filtered)}")
if filtered:
    for v in filtered[:5]:
        print(f"  {v.file_path}:{v.line} [{v.rule_id}]")
