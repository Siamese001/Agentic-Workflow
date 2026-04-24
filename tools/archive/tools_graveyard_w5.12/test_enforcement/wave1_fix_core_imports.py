"""Wave 1: Fix first-party import skip violations in core tests.

Handles three violation patterns:
1. broken_template_missing_except — Generated ADG stubs with syntax errors
2. first_party_stub_on_importerror — try/except ImportError → stubs to None
3. first_party_pass_on_importerror — try/except ImportError → pass
4. first_party_flag_on_importerror — try/except ImportError → HAS_X = False

Strategy:
- Remove try/except ImportError wrappers around first-party imports
- Convert to direct imports (failures surface as test errors)
- Remove skipif(not _AVAILABLE) decorators
- Remove _AVAILABLE flag and stub assignments
- Keep actual test logic intact
"""

from __future__ import annotations

import ast
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent

FIRST_PARTY_TOPS = frozenset(
    {
        "agentic_core",
        "apps_lic",
        "apps_rg",
        "apps_shared",
        "apps_exec",
        "apps_rfp",
        "apps_research",
        "apps_eval",
        "system_learning",
        "infrastructure",
        "tools",
        "ops_scripts",
        "data",
    }
)


def _is_first_party(module_name: str) -> bool:
    if not module_name:
        return False
    return module_name.split(".")[0] in FIRST_PARTY_TOPS


def fix_broken_template(filepath: pathlib.Path) -> dict:
    """Fix broken generated ADG test stubs (missing except clause)."""
    source = filepath.read_text(encoding="utf-8", errors="replace")
    lines = source.splitlines()

    # Detect the broken pattern:
    # try:
    #     import xxx as _mod  # noqa: F401
    #     _AVAILABLE = True
    # pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    #     _mod = None
    #     _AVAILABLE = False

    # Extract the import target
    import_match = None
    for line in lines:
        m = re.match(r"\s+import\s+([\w.]+)\s+as\s+_mod", line)
        if m:
            import_match = m.group(1)
            break
        m = re.match(r"\s+from\s+([\w.]+)\s+import", line)
        if m:
            import_match = m.group(1)
            break

    if not import_match:
        return {"file": str(filepath), "status": "skip", "reason": "could not find import target"}

    # Extract module name for docstring
    module_name = import_match.split(".")[-1]
    if module_name == "__init__":
        module_name = import_match.split(".")[-2] if len(import_match.split(".")) > 1 else import_match

    # Extract docstring if present
    docstring = ""
    for line in lines:
        if line.startswith('"""'):
            docstring = line
            break

    if not docstring:
        docstring = f'"""Import contract test for {import_match}."""'

    # Detect pytestmark
    has_pytestmark = any("pytestmark" in line for line in lines)
    pytestmark_line = ""
    if has_pytestmark:
        for line in lines:
            if "pytestmark" in line:
                pytestmark_line = line.strip()
                break

    # Build clean replacement
    new_lines = [
        docstring,
        "from __future__ import annotations",
        "",
        "import pytest",
        "",
    ]
    if pytestmark_line:
        new_lines.append(pytestmark_line)
        new_lines.append("")

    # Use the right import form
    if "as _mod" in source:
        new_lines.append(f"import {import_match} as _mod  # noqa: F401")
    else:
        new_lines.append(f"import {import_match}  # noqa: F401")

    new_lines.extend(
        [
            "",
            "",
            "def test_module_importable():",
            f'    """Module {module_name} must be importable."""',
            "    assert _mod is not None"
            if "as _mod" in source
            else f"    assert {import_match} is not None",
            "",
        ]
    )

    new_source = "\n".join(new_lines)
    filepath.write_text(new_source, encoding="utf-8")
    return {"file": str(filepath), "status": "fixed", "pattern": "broken_template"}


def fix_stub_pattern(filepath: pathlib.Path) -> dict:
    """Fix try/except ImportError → stub pattern.

    Converts:
        try:
            from module import A, B, C
            _AVAILABLE = True
        except ImportError:
            _AVAILABLE = False
            A = None
            B = None

        @pytest.mark.skipif(not _AVAILABLE, ...)
        class TestX:
            ...

    To:
        from module import A, B, C

        class TestX:
            ...
    """
    source = filepath.read_text(encoding="utf-8", errors="replace")

    try:
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError:
        return {"file": str(filepath), "status": "skip", "reason": "syntax error"}

    lines = source.splitlines()
    # Track regions to remove/replace
    edits = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Try):
            continue

        # Check if any handler catches ImportError
        import_error_handler = None
        for handler in node.handlers:
            if handler.type is None:
                continue
            if isinstance(handler.type, ast.Name) and handler.type.id in (
                "ImportError",
                "ModuleNotFoundError",
            ):
                import_error_handler = handler
                break
            if isinstance(handler.type, ast.Tuple):
                if any(
                    isinstance(e, ast.Name) and e.id in ("ImportError", "ModuleNotFoundError")
                    for e in handler.type.elts
                ):
                    import_error_handler = handler
                    break

        if not import_error_handler:
            continue

        # Check if the try block contains first-party imports
        has_first_party = False
        import_lines = []
        for stmt in node.body:
            if isinstance(stmt, ast.Import):
                for alias in stmt.names:
                    if _is_first_party(alias.name):
                        has_first_party = True
                import_lines.append(stmt)
            elif isinstance(stmt, ast.ImportFrom):
                if stmt.module and _is_first_party(stmt.module):
                    has_first_party = True
                import_lines.append(stmt)

        if not has_first_party:
            continue

        # Get the import source lines (just the import statements, preserving original text)
        import_source_lines = []
        for imp_node in import_lines:
            start = imp_node.lineno - 1
            end = imp_node.end_lineno or imp_node.lineno
            for ln in range(start, end):
                if ln < len(lines):
                    # Remove indentation from try block (typically 4 spaces)
                    text = lines[ln]
                    # Strip one level of indentation (the try: block indent)
                    if text.startswith("        "):
                        text = text[4:]  # Remove one indent level
                    elif text.startswith("    "):
                        text = text[4:]
                    import_source_lines.append(text)

        # Calculate the full try/except block range
        try_start = node.lineno  # 1-indexed
        try_end = node.end_lineno or node.lineno

        # Also find and remove _AVAILABLE assignment in try body
        # (keep only import lines)
        replacement = "\n".join(import_source_lines)

        edits.append(
            {
                "start": try_start,
                "end": try_end,
                "replacement": replacement,
            }
        )

    if not edits:
        return {"file": str(filepath), "status": "skip", "reason": "no first-party try/except found"}

    # Apply edits in reverse order to preserve line numbers
    edits.sort(key=lambda e: e["start"], reverse=True)
    for edit in edits:
        start_idx = edit["start"] - 1
        end_idx = edit["end"]
        lines[start_idx:end_idx] = edit["replacement"].splitlines()

    new_source = "\n".join(lines)

    # Remove skipif(not _AVAILABLE, ...) decorators
    new_source = re.sub(
        r'@pytest\.mark\.skipif\(not _AVAILABLE,\s*reason="[^"]*"\)\n',
        "",
        new_source,
    )
    # Also handle single-quoted reason
    new_source = re.sub(
        r"@pytest\.mark\.skipif\(not _AVAILABLE,\s*reason='[^']*'\)\n",
        "",
        new_source,
    )

    # Remove _AVAILABLE references in simple assertions
    new_source = re.sub(
        r"\n\s*assert _AVAILABLE or not _AVAILABLE\n",
        "\n",
        new_source,
    )

    # Remove standalone _AVAILABLE = True lines that may remain
    new_source = re.sub(r"\n\s*_AVAILABLE = True\n", "\n", new_source)

    # Remove test_module_importable that just checks _AVAILABLE
    new_source = re.sub(
        r'\ndef test_module_importable\(\):\n\s*"""[^"]*"""\n\s*assert _AVAILABLE or not _AVAILABLE\n',
        '\ndef test_module_importable():\n    """Module must be importable."""\n    pass  # Import verified at module level\n',
        new_source,
    )

    # Clean up multiple blank lines
    while "\n\n\n\n" in new_source:
        new_source = new_source.replace("\n\n\n\n", "\n\n\n")

    filepath.write_text(new_source, encoding="utf-8")
    return {"file": str(filepath), "status": "fixed", "pattern": "stub_pattern"}


def fix_pass_or_flag_pattern(filepath: pathlib.Path) -> dict:
    """Fix try/except ImportError → pass or flag pattern."""
    source = filepath.read_text(encoding="utf-8", errors="replace")

    try:
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError:
        return {"file": str(filepath), "status": "skip", "reason": "syntax error"}

    lines = source.splitlines()
    edits = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Try):
            continue

        has_import_error = False
        for handler in node.handlers:
            if handler.type is None:
                continue
            if isinstance(handler.type, ast.Name) and handler.type.id in (
                "ImportError",
                "ModuleNotFoundError",
            ):
                has_import_error = True
            if isinstance(handler.type, ast.Tuple):
                if any(
                    isinstance(e, ast.Name) and e.id in ("ImportError", "ModuleNotFoundError")
                    for e in handler.type.elts
                ):
                    has_import_error = True

        if not has_import_error:
            continue

        has_first_party = False
        import_lines = []
        for stmt in node.body:
            if isinstance(stmt, ast.Import):
                for alias in stmt.names:
                    if _is_first_party(alias.name):
                        has_first_party = True
                import_lines.append(stmt)
            elif isinstance(stmt, ast.ImportFrom):
                if stmt.module and _is_first_party(stmt.module):
                    has_first_party = True
                import_lines.append(stmt)

        if not has_first_party:
            continue

        # Get import source lines with dedented text
        import_source = []
        for imp_node in import_lines:
            start = imp_node.lineno - 1
            end = imp_node.end_lineno or imp_node.lineno
            for ln in range(start, end):
                if ln < len(lines):
                    text = lines[ln]
                    if text.startswith("        "):
                        text = text[4:]
                    elif text.startswith("    "):
                        text = text[4:]
                    import_source.append(text)

        edits.append(
            {
                "start": node.lineno,
                "end": node.end_lineno or node.lineno,
                "replacement": "\n".join(import_source),
            }
        )

    if not edits:
        return {"file": str(filepath), "status": "skip", "reason": "no first-party try/except found"}

    edits.sort(key=lambda e: e["start"], reverse=True)
    for edit in edits:
        start_idx = edit["start"] - 1
        end_idx = edit["end"]
        lines[start_idx:end_idx] = edit["replacement"].splitlines()

    new_source = "\n".join(lines)

    # Clean up _AVAILABLE-related patterns
    new_source = re.sub(
        r'@pytest\.mark\.skipif\(not _AVAILABLE,\s*reason="[^"]*"\)\n',
        "",
        new_source,
    )
    new_source = re.sub(
        r"@pytest\.mark\.skipif\(not _AVAILABLE,\s*reason='[^']*'\)\n",
        "",
        new_source,
    )
    new_source = re.sub(r"\n\s*_AVAILABLE = True\n", "\n", new_source)
    new_source = re.sub(
        r"\n\s*assert _AVAILABLE or not _AVAILABLE\n",
        "\n",
        new_source,
    )

    while "\n\n\n\n" in new_source:
        new_source = new_source.replace("\n\n\n\n", "\n\n\n")

    filepath.write_text(new_source, encoding="utf-8")
    return {"file": str(filepath), "status": "fixed", "pattern": "pass_or_flag"}


def main():
    vio_path = ROOT / "artifacts" / "test_enforcement" / "test_violations.json"
    with open(vio_path) as f:
        violations = json.load(f)

    # Group violations by file and type
    broken_templates = set()
    stub_files = set()
    pass_flag_files = set()

    for v in violations:
        vtype = v["violation_type"]
        fp = v["file_path"]
        if vtype == "broken_template_missing_except":
            broken_templates.add(fp)
        elif vtype == "first_party_stub_on_importerror":
            stub_files.add(fp)
        elif vtype in ("first_party_pass_on_importerror", "first_party_flag_on_importerror"):
            pass_flag_files.add(fp)

    # Don't double-process files that are in multiple categories
    stub_files -= broken_templates
    pass_flag_files -= broken_templates
    pass_flag_files -= stub_files

    print("Wave 1 targets:")
    print(f"  Broken templates: {len(broken_templates)}")
    print(f"  Stub patterns: {len(stub_files)}")
    print(f"  Pass/flag patterns: {len(pass_flag_files)}")
    print(f"  Total: {len(broken_templates) + len(stub_files) + len(pass_flag_files)}")
    print()

    results = {"fixed": 0, "skipped": 0, "errors": []}

    # Fix broken templates
    print("Fixing broken templates...")
    for i, fp in enumerate(sorted(broken_templates)):
        if i % 200 == 0 and i > 0:
            print(f"  ...{i}/{len(broken_templates)}")
        abs_path = ROOT / fp
        if not abs_path.exists():
            results["errors"].append({"file": fp, "error": "file not found"})
            continue
        try:
            result = fix_broken_template(abs_path)
            if result["status"] == "fixed":
                results["fixed"] += 1
            else:
                results["skipped"] += 1
        except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
            results["errors"].append({"file": fp, "error": str(e)})

    # Fix stub patterns
    print("Fixing stub patterns...")
    for fp in sorted(stub_files):
        abs_path = ROOT / fp
        if not abs_path.exists():
            results["errors"].append({"file": fp, "error": "file not found"})
            continue
        try:
            result = fix_stub_pattern(abs_path)
            if result["status"] == "fixed":
                results["fixed"] += 1
            else:
                results["skipped"] += 1
        except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
            results["errors"].append({"file": fp, "error": str(e)})

    # Fix pass/flag patterns
    print("Fixing pass/flag patterns...")
    for fp in sorted(pass_flag_files):
        abs_path = ROOT / fp
        if not abs_path.exists():
            results["errors"].append({"file": fp, "error": "file not found"})
            continue
        try:
            result = fix_pass_or_flag_pattern(abs_path)
            if result["status"] == "fixed":
                results["fixed"] += 1
            else:
                results["skipped"] += 1
        except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
            results["errors"].append({"file": fp, "error": str(e)})

    print(f"\n{'=' * 60}")
    print("WAVE 1 RESULTS")
    print(f"{'=' * 60}")
    print(f"Fixed: {results['fixed']}")
    print(f"Skipped: {results['skipped']}")
    print(f"Errors: {len(results['errors'])}")

    if results["errors"]:
        print("\nErrors:")
        for e in results["errors"][:20]:
            print(f"  {e['file']}: {e['error']}")

    # Write results
    out_path = ROOT / "artifacts" / "test_enforcement" / "wave1_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults: {out_path}")


if __name__ == "__main__":
    main()
