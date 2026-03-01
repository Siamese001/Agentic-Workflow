"""Dry-run import scanner for apps_lic.

Walks every .py file under apps_lic/, attempts to import it as a module,
and captures all errors. Outputs a structured report to stdout.
"""

import ast
import importlib
import sys
import traceback
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
APPS_LIC_DIR = REPO_ROOT / "apps_lic"

# Ensure repo root is on sys.path
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

errors = []
warnings = []
ok_modules = []


def module_name_from_path(path: Path) -> str:
    rel = path.relative_to(REPO_ROOT)
    parts = list(rel.with_suffix("").parts)
    return ".".join(parts)


def ast_check(path: Path) -> list[str]:
    """Return list of syntax/AST-level issues."""
    issues = []
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        ast.parse(source, filename=str(path))
    except SyntaxError as e:
        issues.append(f"SyntaxError at line {e.lineno}: {e.msg}")
    return issues


def try_import(mod_name: str, path: Path) -> tuple[bool, str | None]:
    try:
        importlib.import_module(mod_name)
        return True, None
    except Exception:
        tb = traceback.format_exc()
        return False, tb


def scan():
    py_files = sorted(APPS_LIC_DIR.rglob("*.py"))
    print(f"SCAN: {len(py_files)} .py files found under apps_lic/\n")

    for py_file in py_files:
        # Skip __pycache__
        if "__pycache__" in py_file.parts:
            continue

        mod_name = module_name_from_path(py_file)
        rel_path = py_file.relative_to(REPO_ROOT)

        # Step 1: AST syntax check
        ast_issues = ast_check(py_file)
        if ast_issues:
            for issue in ast_issues:
                msg = f"[AST]  {rel_path}: {issue}"
                errors.append(msg)
                print(msg)
            continue  # Skip import attempt if syntax is broken

        # Step 2: Import attempt
        ok, tb = try_import(mod_name, py_file)
        if ok:
            ok_modules.append(mod_name)
            print(f"[OK]   {rel_path}")
        else:
            # Extract the last meaningful line from the traceback
            lines = [l for l in tb.strip().splitlines() if l.strip()]
            summary = lines[-1] if lines else "unknown error"
            errors.append(f"[ERR]  {rel_path}: {summary}")
            print(f"[ERR]  {rel_path}: {summary}")
            # Print full traceback indented
            for line in tb.strip().splitlines():
                print(f"       {line}")
            print()


def main():
    scan()
    print("\n" + "=" * 70)
    print(f"SUMMARY: {len(ok_modules)} OK  |  {len(errors)} ERRORS")
    print("=" * 70)
    if errors:
        print("\nERRORS:")
        for e in errors:
            print(f"  {e}")
    else:
        print("\nNo import errors detected.")


if __name__ == "__main__":
    main()
