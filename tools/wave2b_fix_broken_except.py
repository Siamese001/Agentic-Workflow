#!/usr/bin/env python3
"""
Wave 2b: Fix broken try/except blocks in source modules.

The governance wiring inserted '# guardian: allow-silent-swallow' comments
between try: body and except ImportError:, breaking indentation.

Pattern to fix:
    try:
        <body>
    # guardian: allow-silent-swallow - optional dependency
            except ImportError:
                <handler>

Should become:
    try:
        <body>
    except ImportError:  # guardian: allow-silent-swallow
        <handler>

Strategy: regex-based line-by-line repair with compile() verification.
"""

import sys
from pathlib import Path


def fix_broken_except_blocks(source: str) -> str:
    """Fix misindented except blocks preceded by guardian comments."""
    lines = source.splitlines(keepends=True)
    result = []
    i = 0
    fixes = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.rstrip()

        # Pattern: line is a guardian comment followed by a misindented except
        if "guardian: allow-silent-swallow" in stripped and i + 1 < len(lines):
            next_line = lines[i + 1].rstrip()
            next_stripped = next_line.lstrip()

            if next_stripped.startswith("except"):
                # Find the try: block this belongs to by scanning backwards
                # to determine correct indentation
                try_indent = _find_try_indent(result)

                if try_indent is not None:
                    # Build correct except line at try_indent level
                    except_content = next_stripped
                    # Append guardian comment to except line
                    fixed_except = " " * try_indent + except_content + "  # guardian: allow-silent-swallow\n"
                    result.append(fixed_except)
                    i += 2  # Skip both guardian comment and old except line
                    fixes += 1

                    # Now fix the handler body indentation
                    handler_indent = try_indent + 4
                    while i < len(lines):
                        handler_line = lines[i]
                        handler_stripped = handler_line.lstrip()

                        if not handler_stripped or handler_stripped.startswith("#"):
                            # Blank line or comment — keep as-is
                            result.append(handler_line)
                            i += 1
                            continue

                        # Check if this line is over-indented handler code
                        current_indent = len(handler_line) - len(handler_line.lstrip())
                        if current_indent > try_indent + 4:
                            # Re-indent to handler_indent
                            result.append(" " * handler_indent + handler_stripped + "\n")
                            i += 1
                        else:
                            # Not part of the handler anymore
                            break
                    continue
                else:
                    # Couldn't find try: — just remove the guardian comment
                    # and fix the except indentation heuristically
                    result.append(lines[i + 1])
                    i += 2
                    fixes += 1
                    continue

        result.append(line)
        i += 1

    if fixes:
        return "".join(result)
    return source


def _find_try_indent(lines_so_far: list) -> int | None:
    """Scan backwards through accumulated lines to find the matching try: indent."""
    for j in range(len(lines_so_far) - 1, -1, -1):
        line = lines_so_far[j].rstrip()
        stripped = line.lstrip()
        if stripped.startswith("try:"):
            return len(line) - len(stripped)
        # Stop if we hit a def/class at lower indent (we've gone too far)
        if stripped.startswith(("def ", "class ", "async def ")):
            return None
    return None


def fix_file(filepath: Path) -> tuple[bool, str]:
    """Fix a single file. Returns (changed, status)."""
    try:
        source = filepath.read_text("utf-8")
    except Exception as e:
        return False, f"read error: {e}"

    # Quick check: does it even have the pattern?
    if "guardian: allow-silent-swallow" not in source:
        return False, "no guardian pattern"

    # Check if it already compiles
    try:
        compile(source, str(filepath), "exec")
        return False, "already valid"
    except (SyntaxError, IndentationError):
        pass  # Needs fixing

    fixed = fix_broken_except_blocks(source)

    if fixed == source:
        return False, "no changes produced"

    # Verify fix compiles
    try:
        compile(fixed, str(filepath), "exec")
    except (SyntaxError, IndentationError) as e:
        return False, f"fix did not resolve: {e}"

    filepath.write_text(fixed, encoding="utf-8")
    return True, "fixed"


def main():
    root = Path("agentic_core")
    total = 0
    fixed = 0
    already_ok = 0
    failed = []

    all_py = sorted(root.rglob("*.py"))
    print(f"Scanning {len(all_py)} source files...")

    for p in all_py:
        try:
            source = p.read_text("utf-8")
            compile(source, str(p), "exec")
            already_ok += 1
        except (SyntaxError, IndentationError):
            total += 1
            changed, status = fix_file(p)
            if changed:
                fixed += 1
                print(f"  FIXED: {p}")
            else:
                failed.append((str(p).replace("\\", "/"), status))

    print("\nResults:")
    print(f"  Already valid: {already_ok}")
    print(f"  Broken files found: {total}")
    print(f"  Fixed: {fixed}")
    print(f"  Still broken: {len(failed)}")

    if failed:
        print("\nStill broken:")
        for fp, status in failed:
            print(f"  {fp}: {status}")

    return fixed, failed


if __name__ == "__main__":
    fixed, failed = main()
    sys.exit(1 if failed and fixed == 0 else 0)
