"""Wave 1 post-fix cleanup: Remove residual _AVAILABLE references and fix remaining issues.

Scans all Wave 1 fixed files for:
1. Residual _AVAILABLE references (assertions, assignments, skipif decorators)
2. Syntax errors introduced by the fix
3. Stale test_module_importable functions that still test _AVAILABLE
"""

from __future__ import annotations

import ast
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent


def cleanup_file(filepath: pathlib.Path) -> dict:
    """Clean up residual _AVAILABLE patterns in a fixed file."""
    source = filepath.read_text(encoding="utf-8", errors="replace")
    original = source
    changed = False

    # 1. Remove any remaining skipif(not _AVAILABLE, ...) decorators
    source = re.sub(
        r'@pytest\.mark\.skipif\(not _AVAILABLE,\s*reason=["\'][^"\']*["\']\)\n',
        "",
        source,
    )

    # 2. Remove _AVAILABLE = True/False assignments
    source = re.sub(r"^\s*_AVAILABLE\s*=\s*(True|False)\s*$", "", source, flags=re.MULTILINE)

    # 3. Fix test_module_importable that asserts _AVAILABLE
    source = re.sub(
        r'(def test_module_importable\(\):\n\s*"""[^"]*"""\n)\s*assert _AVAILABLE or not _AVAILABLE',
        r"\1    pass  # Import verified at module level",
        source,
    )
    source = re.sub(
        r'(def test_module_importable\(\):\n\s*"""[^"]*"""\n)\s*assert _AVAILABLE\b',
        r"\1    pass  # Import verified at module level",
        source,
    )

    # 4. Fix class-level assert _AVAILABLE
    source = re.sub(
        r'(\s+)(def test_module_importable\(self\)[^:]*:\n\s+"""[^"]*"""\n)\s+assert _AVAILABLE\b',
        r"\1\2\1    pass  # Import verified at module level",
        source,
    )

    # 5. Remove standalone assert _AVAILABLE lines (not inside a function)
    source = re.sub(
        r"^\s+assert _AVAILABLE\s*$",
        "        pass  # Import verified at module level",
        source,
        flags=re.MULTILINE,
    )

    # 6. Remove _IMPORT_OK = True/False
    source = re.sub(r"^\s*_IMPORT_OK\s*=\s*(True|False)\s*$", "", source, flags=re.MULTILINE)

    # 7. Remove _exc assignment leftovers (except ImportError as _exc:)
    # These should be gone but check
    source = re.sub(r"^\s*_exc\s*=\s*None\s*$", "", source, flags=re.MULTILINE)

    # 8. Clean up multiple blank lines
    while "\n\n\n\n" in source:
        source = source.replace("\n\n\n\n", "\n\n\n")

    # 9. Remove trailing whitespace on blank lines
    source = re.sub(r"^[ \t]+$", "", source, flags=re.MULTILINE)

    changed = source != original

    if changed:
        filepath.write_text(source, encoding="utf-8")

    # Verify syntax
    try:
        ast.parse(source, filename=str(filepath))
        syntax_ok = True
    except SyntaxError as e:
        syntax_ok = False

    return {
        "file": str(filepath.relative_to(ROOT)),
        "changed": changed,
        "syntax_ok": syntax_ok,
    }


def main():
    test_dir = ROOT / "tests"
    test_files = sorted(test_dir.rglob("test_*.py"))
    # Also check root level
    test_files.extend(sorted(ROOT.glob("test_*.py")))
    # Add conftest files
    test_files.extend(sorted(test_dir.rglob("conftest.py")))

    print(f"Post-fix cleanup scanning {len(test_files)} files...", file=sys.stderr)

    stats = {"cleaned": 0, "syntax_errors": 0, "unchanged": 0, "total": 0}
    syntax_error_files = []
    still_has_available = []

    for i, fp in enumerate(test_files):
        if i % 500 == 0 and i > 0:
            print(f"  ...{i}/{len(test_files)}", file=sys.stderr)
        stats["total"] += 1
        result = cleanup_file(fp)

        if result["changed"]:
            stats["cleaned"] += 1
        else:
            stats["unchanged"] += 1

        if not result["syntax_ok"]:
            stats["syntax_errors"] += 1
            syntax_error_files.append(result["file"])

        # Check for residual _AVAILABLE
        source = fp.read_text(encoding="utf-8", errors="replace")
        if "_AVAILABLE" in source and "def " in source:
            # Check it's actually used, not just in a comment
            for line in source.splitlines():
                stripped = line.strip()
                if (
                    "_AVAILABLE" in stripped
                    and not stripped.startswith("#")
                    and not stripped.startswith('"""')
                ):
                    still_has_available.append(result["file"])
                    break

    print(f"\n{'=' * 60}")
    print("POST-FIX CLEANUP RESULTS")
    print(f"{'=' * 60}")
    print(f"Total files scanned: {stats['total']}")
    print(f"Files cleaned: {stats['cleaned']}")
    print(f"Files unchanged: {stats['unchanged']}")
    print(f"Files with syntax errors: {stats['syntax_errors']}")
    print(f"Files still referencing _AVAILABLE: {len(still_has_available)}")

    if syntax_error_files:
        print("\nSyntax error files (top 20):")
        for f in syntax_error_files[:20]:
            print(f"  {f}")

    if still_has_available:
        print("\nFiles still referencing _AVAILABLE (top 20):")
        for f in still_has_available[:20]:
            print(f"  {f}")


if __name__ == "__main__":
    main()
