"""
Syntax Medic - Runtime/Shared Directory Audit
Scans for syntax errors before validation sweep
"""
import ast
import os
from pathlib import Path

def audit_runtime_syntax():
    target_dir = Path("agentic_core/runtime/shared")
    print(f"[*] Auditing {target_dir} for syntax errors...")
    
    valid_count = 0
    error_count = 0
    
    for py_file in sorted(target_dir.glob("*.py")):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                ast.parse(f.read())
            print(f"  [✓] {py_file.name}: Valid")
            valid_count += 1
        except SyntaxError as e:
            print(f"  [X] {py_file.name}: Syntax Error at line {e.lineno}")
            print(f"      -> {e.msg}")
            error_count += 1
        except Exception as e:
            print(f"  [!] {py_file.name}: Unexpected error: {e}")
            error_count += 1
    
    print(f"\n[SUMMARY] Valid: {valid_count} | Errors: {error_count}")
    return error_count == 0

if __name__ == "__main__":
    success = audit_runtime_syntax()
    exit(0 if success else 1)
