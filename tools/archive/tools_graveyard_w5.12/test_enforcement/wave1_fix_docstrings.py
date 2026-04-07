"""Fix unterminated docstrings in Wave 1 fixed files.

The broken template fixer extracted the first line starting with triple-quotes
but the original docstring was multi-line, leaving it unterminated.
Pattern: line 1 is '\"\"\"Some text.' without closing '\"\"\"'
Fix: close the docstring on the same line.
"""
from __future__ import annotations

import ast
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent


def fix_file(filepath: pathlib.Path) -> dict:
    """Fix unterminated docstrings and other syntax issues."""
    source = filepath.read_text(encoding="utf-8", errors="replace")

    # First check if it even has a syntax error
    try:
        ast.parse(source)
        return {"file": str(filepath), "status": "ok"}
    except SyntaxError:
        pass

    lines = source.splitlines()
    changed = False

    # Pattern 1: First line is unterminated triple-quoted string
    # e.g., '"""ADG importability contract for foo/bar.py.'
    # Fix: append '"""' to close it
    if lines and lines[0].startswith('"""') and not lines[0].endswith('"""'):
        # Count triple quotes on line 1
        count = lines[0].count('"""')
        if count == 1:  # Only opening, no closing
            lines[0] = lines[0] + '"""'
            changed = True

    # Pattern 2: Module-level docstring spans to line 2+ but line 2 starts code
    # Check if first line is a docstring that's now closed
    if changed:
        new_source = "\n".join(lines)
        try:
            ast.parse(new_source)
            filepath.write_text(new_source, encoding="utf-8")
            return {"file": str(filepath), "status": "fixed", "fix": "closed_docstring"}
        except SyntaxError:
            pass

    # Pattern 3: More complex — try to find and close any unterminated triple-quotes
    # Reset and try a different approach
    lines = source.splitlines()
    in_triple = False
    for i, line in enumerate(lines):
        tq_count = line.count('"""')
        if tq_count % 2 == 1:  # Odd number of triple quotes = toggles state
            in_triple = not in_triple
            if in_triple and i < len(lines) - 1:
                # Check if next line is clearly not part of the docstring
                next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""
                if next_line.startswith("from ") or next_line.startswith("import ") or next_line == "":
                    lines[i] = line + '"""'
                    in_triple = False
                    changed = True

    if changed:
        new_source = "\n".join(lines)
        try:
            ast.parse(new_source)
            filepath.write_text(new_source, encoding="utf-8")
            return {"file": str(filepath), "status": "fixed", "fix": "closed_triple_quote"}
        except SyntaxError as e:
            return {"file": str(filepath), "status": "still_broken", "error": str(e)[:100]}

    return {"file": str(filepath), "status": "still_broken", "error": "could not auto-fix"}


def main():
    test_dir = ROOT / "tests"
    all_files = sorted(test_dir.rglob("test_*.py"))
    # Also root test files
    all_files.extend(sorted(ROOT.glob("test_*.py")))

    print(f"Scanning {len(all_files)} files for syntax errors...", file=sys.stderr)

    syntax_errors_before = 0
    fixed = 0
    still_broken = 0
    broken_files = []

    for i, fp in enumerate(all_files):
        if i % 500 == 0 and i > 0:
            print(f"  ...{i}/{len(all_files)}", file=sys.stderr)

        try:
            source = fp.read_text(encoding="utf-8", errors="replace")
            ast.parse(source)
            continue  # No syntax error
        except SyntaxError:
            syntax_errors_before += 1

        result = fix_file(fp)
        if result["status"] == "fixed":
            fixed += 1
        elif result["status"] == "still_broken":
            still_broken += 1
            broken_files.append(result)

    print(f"\n{'='*60}")
    print("DOCSTRING FIX RESULTS")
    print(f"{'='*60}")
    print(f"Files with syntax errors: {syntax_errors_before}")
    print(f"Fixed: {fixed}")
    print(f"Still broken: {still_broken}")

    if broken_files:
        print("\nStill broken files (top 30):")
        for r in broken_files[:30]:
            rel = str(pathlib.Path(r["file"]).relative_to(ROOT)).replace("\\", "/")
            print(f"  {rel}: {r.get('error', '?')}")


if __name__ == "__main__":
    main()
