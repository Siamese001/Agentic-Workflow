"""Wave 2: Fix remaining 64 violations in specific files.

Three patterns:
1. try/except ImportError with pytest.importorskip in except handler (2 files)
2. try/except (ImportError, ModuleNotFoundError) → pytest.skip inside test functions (30 violations in ~8 files)
3. pytest.skip("Cannot import fixer") in core tests (32 violations in 3 files)

Strategy:
- Pattern 1: Remove entire try/except, keep direct import
- Pattern 2: Remove try/except wrapper inside test functions, use direct import
- Pattern 3: Remove try/except + pytest.skip, use direct import at module level
"""
from __future__ import annotations

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent


def fix_try_except_importorskip_in_except(filepath: pathlib.Path) -> dict:
    """Fix pattern: try: from X import ... except ImportError: pytest.importorskip(...)"""
    source = filepath.read_text(encoding="utf-8", errors="replace")
    original = source

    # Remove the entire try/except block, keep only the import statements
    # Pattern: try:\n    from X import (\n...\n)\n\nexcept ImportError:\n    pytest.importorskip(...)\n\n    X = None\n...

    lines = source.splitlines()
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Detect start of try: block
        if stripped == "try:":
            # Collect the try block contents (imports)
            try_imports = []
            j = i + 1
            while j < len(lines):
                inner = lines[j]
                inner_stripped = inner.strip()
                if inner_stripped.startswith(("except ", "except(")):
                    break
                if inner_stripped and not inner_stripped.startswith("#"):
                    # Dedent by one level (4 spaces)
                    if inner.startswith("        "):
                        try_imports.append(inner[4:])
                    elif inner.startswith("    "):
                        try_imports.append(inner[4:])
                    else:
                        try_imports.append(inner)
                elif not inner_stripped:
                    try_imports.append("")
                j += 1

            # Check if except handler catches ImportError
            if j < len(lines) and ("ImportError" in lines[j] or "ModuleNotFoundError" in lines[j]):
                # Skip the except block entirely
                k = j + 1
                while k < len(lines):
                    exc_line = lines[k].strip()
                    # End of except block: next non-indented, non-empty line
                    if exc_line and not lines[k].startswith("    ") and not lines[k].startswith("\t"):
                        break
                    k += 1

                # Check if any of the imports are first-party
                has_first_party = any(
                    "agentic_core" in l or "apps_" in l or "system_learning" in l or
                    "infrastructure" in l or "tools" in l or "ops_scripts" in l
                    for l in try_imports
                )

                if has_first_party:
                    # Remove _AVAILABLE = True from imports
                    clean_imports = [l for l in try_imports if "_AVAILABLE" not in l and l.strip()]
                    new_lines.extend(clean_imports)
                    new_lines.append("")
                    i = k
                    continue

            # Not an ImportError handler, keep as-is
            new_lines.append(line)
            i += 1
            continue

        new_lines.append(line)
        i += 1

    new_source = "\n".join(new_lines)

    if new_source != original:
        filepath.write_text(new_source, encoding="utf-8")
        return {"status": "fixed", "pattern": "importorskip_in_except"}
    return {"status": "unchanged"}


def fix_inline_try_except_skip(filepath: pathlib.Path) -> dict:
    """Fix pattern: try: import X; ... except (ImportError, ModuleNotFoundError): pytest.skip(...)

    This pattern appears inside test functions. Convert to direct import.
    """
    source = filepath.read_text(encoding="utf-8", errors="replace")
    original = source

    # Replace inline try/except ImportError → pytest.skip patterns inside functions
    # Pattern:
    #     try:
    #         import X as mod
    #         assert mod is not None
    #     except (ImportError, ModuleNotFoundError) as e:
    #         pytest.skip(f"... {e}")

    # Use regex to match these blocks
    pattern = re.compile(
        r'(\s+)try:\n'
        r'\1    (import [^\n]+)\n'
        r'(?:\1    [^\n]*\n)*?'  # Optional additional lines in try
        r'\1except \(?(?:ImportError|ModuleNotFoundError)[^:]*:\n'
        r'(?:\1    [^\n]*\n)*',  # except body
        re.MULTILINE,
    )

    def replace_match(m):
        indent = m.group(1)
        import_line = m.group(2).strip()
        return f"{indent}{import_line}\n{indent}assert mod is not None\n"

    new_source = pattern.sub(replace_match, source)

    if new_source != original:
        filepath.write_text(new_source, encoding="utf-8")
        return {"status": "fixed", "pattern": "inline_try_except_skip"}
    return {"status": "unchanged"}


def fix_skip_cannot_import(filepath: pathlib.Path) -> dict:
    """Fix pattern: pytest.skip('Cannot import fixer') in core test functions.

    These are tests that try to import a fixer module and skip if it fails.
    Convert to direct import at top of test.
    """
    source = filepath.read_text(encoding="utf-8", errors="replace")
    original = source

    # Pattern inside test functions:
    #     try:
    #         from X import Y
    #     except ImportError:
    #         pytest.skip("Cannot import fixer")

    # Replace with direct import (remove try/except)
    pattern = re.compile(
        r'(\s+)try:\n'
        r'((?:\1    (?:from |import )[^\n]+\n)+)'  # import lines
        r'\1except (?:\(?(?:ImportError|ModuleNotFoundError)[^:]*\)?:\n)'
        r'\1    pytest\.skip\([^\)]+\)\n',
        re.MULTILINE,
    )

    def replace_match(m):
        indent = m.group(1)
        import_lines = m.group(2)
        # Dedent import lines by one level
        dedented = []
        for line in import_lines.splitlines():
            if line.startswith(indent + "    "):
                dedented.append(indent + line[len(indent) + 4:])
            else:
                dedented.append(line)
        return "\n".join(dedented) + "\n"

    new_source = pattern.sub(replace_match, source)

    if new_source != original:
        filepath.write_text(new_source, encoding="utf-8")
        return {"status": "fixed", "pattern": "skip_cannot_import"}
    return {"status": "unchanged"}


def main():
    vio_path = ROOT / "artifacts" / "test_enforcement" / "test_violations.json"
    with open(vio_path) as f:
        violations = json.load(f)

    # Collect unique files by violation type
    files_by_type = {}
    for v in violations:
        vtype = v["violation_type"]
        fp = v["file_path"]
        files_by_type.setdefault(vtype, set()).add(fp)

    print(f"Remaining violations: {len(violations)}")
    for vtype, files in sorted(files_by_type.items()):
        print(f"  {vtype}: {len(files)} files")

    fixed_count = 0

    # Fix importorskip_in_core + first_party_import_skip (module-level try/except)
    module_level_files = files_by_type.get("importorskip_in_core", set()) | \
                         files_by_type.get("first_party_import_skip", set())

    print(f"\nFixing {len(module_level_files)} files with module-level try/except...")
    for fp in sorted(module_level_files):
        abs_path = ROOT / fp
        if not abs_path.exists():
            print(f"  MISSING: {fp}")
            continue

        # Try module-level fix first
        r = fix_try_except_importorskip_in_except(abs_path)
        if r["status"] == "fixed":
            fixed_count += 1
            print(f"  FIXED (module-level): {fp}")
            continue

        # Try inline fix
        r = fix_inline_try_except_skip(abs_path)
        if r["status"] == "fixed":
            fixed_count += 1
            print(f"  FIXED (inline): {fp}")
            continue

        # Try skip-cannot-import fix
        r = fix_skip_cannot_import(abs_path)
        if r["status"] == "fixed":
            fixed_count += 1
            print(f"  FIXED (skip-import): {fp}")
            continue

        print(f"  UNCHANGED: {fp}")

    # Fix core_test_import_skip
    skip_files = files_by_type.get("core_test_import_skip", set())
    print(f"\nFixing {len(skip_files)} files with core_test_import_skip...")
    for fp in sorted(skip_files):
        abs_path = ROOT / fp
        if not abs_path.exists():
            print(f"  MISSING: {fp}")
            continue

        r = fix_skip_cannot_import(abs_path)
        if r["status"] == "fixed":
            fixed_count += 1
            print(f"  FIXED (skip-import): {fp}")
            continue

        # Try inline fix
        r = fix_inline_try_except_skip(abs_path)
        if r["status"] == "fixed":
            fixed_count += 1
            print(f"  FIXED (inline): {fp}")
            continue

        r = fix_try_except_importorskip_in_except(abs_path)
        if r["status"] == "fixed":
            fixed_count += 1
            print(f"  FIXED (module-level): {fp}")
            continue

        print(f"  UNCHANGED: {fp}")

    print(f"\nTotal fixed: {fixed_count}")

    # Verify no syntax errors introduced
    import ast
    syntax_errors = 0
    for fp_set in files_by_type.values():
        for fp in fp_set:
            abs_path = ROOT / fp
            if abs_path.exists():
                try:
                    ast.parse(abs_path.read_text(encoding="utf-8", errors="replace"))
                except SyntaxError:
                    syntax_errors += 1
                    print(f"  SYNTAX ERROR: {fp}")
    print(f"Syntax errors in modified files: {syntax_errors}")


if __name__ == "__main__":
    main()
