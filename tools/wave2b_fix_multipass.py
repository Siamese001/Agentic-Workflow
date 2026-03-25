#!/usr/bin/env python3
"""
Wave 2b multi-pass: Fix ALL broken try/except blocks in source modules.

Iterates until compile() succeeds or max passes reached.
Handles the pattern where guardian comment is between try body and except.
"""

import sys
from pathlib import Path


def fix_one_broken_except(lines: list[str]) -> tuple[list[str], bool]:
    """Find and fix ONE broken guardian/except pattern. Returns (new_lines, changed)."""
    result = []
    i = 0
    fixed = False

    while i < len(lines):
        line = lines[i]
        stripped = line.rstrip()

        # Pattern 1: guardian comment line followed by misindented except
        if not fixed and "guardian: allow-silent-swallow" in stripped:
            if i + 1 < len(lines):
                next_stripped = lines[i + 1].lstrip()
                if next_stripped.startswith("except"):
                    try_indent = _find_try_indent(result)
                    if try_indent is not None:
                        except_kw = next_stripped.rstrip()
                        fixed_line = " " * try_indent + except_kw + "  # guardian: allow-silent-swallow\n"
                        result.append(fixed_line)

                        # Fix handler body
                        i += 2
                        handler_indent = try_indent + 4
                        while i < len(lines):
                            h = lines[i]
                            hs = h.lstrip()
                            if not hs.strip():
                                result.append(h)
                                i += 1
                                continue
                            cur_indent = len(h) - len(h.lstrip())
                            if cur_indent > try_indent + 4 and not hs.startswith(
                                (
                                    "def ",
                                    "class ",
                                    "async def ",
                                    "@",
                                    "try:",
                                    "if ",
                                    "for ",
                                    "while ",
                                    "with ",
                                    "return ",
                                    "raise ",
                                    "yield ",
                                )
                            ):
                                result.append(" " * handler_indent + hs)
                                i += 1
                            elif cur_indent == 0 and not hs.startswith(("#", "def ", "class ", "@")):
                                # Module-level code that was de-indented — re-indent
                                result.append(" " * handler_indent + hs)
                                i += 1
                            else:
                                break
                        fixed = True
                        continue

        # Pattern 2: Bare "except" at wrong indent without guardian comment
        if not fixed and stripped.lstrip().startswith("except") and ":" in stripped:
            cur_indent = len(line) - len(line.lstrip())
            # Check if previous non-blank line's indent suggests this is misaligned
            try_indent = _find_try_indent(result)
            if try_indent is not None and cur_indent > try_indent + 4:
                # This except is over-indented
                except_kw = stripped.lstrip().rstrip()
                result.append(" " * try_indent + except_kw + "\n")
                i += 1
                fixed = True
                continue

        result.append(line)
        i += 1

    return result, fixed


def _find_try_indent(lines_so_far: list) -> int | None:
    """Scan backwards to find matching try: indent."""
    for j in range(len(lines_so_far) - 1, -1, -1):
        line = lines_so_far[j].rstrip()
        stripped = line.lstrip()
        if stripped.startswith("try:") and stripped == "try:":
            return len(line) - len(stripped)
        if stripped.startswith(("def ", "class ", "async def ")) and len(line) - len(stripped) == 0:
            return None
    return None


def fix_file(filepath: Path, max_passes: int = 20) -> tuple[bool, str]:
    """Multi-pass fix until compile() succeeds."""
    try:
        source = filepath.read_text("utf-8")
    except Exception as e:
        return False, f"read error: {e}"

    # Already valid?
    try:
        compile(source, str(filepath), "exec")
        return False, "already valid"
    except (SyntaxError, IndentationError):
        pass

    lines = source.splitlines(keepends=True)

    for pass_num in range(max_passes):
        lines, changed = fix_one_broken_except(lines)
        if not changed:
            break

        # Check if it compiles now
        candidate = "".join(lines)
        try:
            compile(candidate, str(filepath), "exec")
            filepath.write_text(candidate, encoding="utf-8")
            return True, f"fixed in {pass_num + 1} passes"
        except (SyntaxError, IndentationError):
            continue  # Keep fixing

    # Final attempt — write what we have and report
    candidate = "".join(lines)
    try:
        compile(candidate, str(filepath), "exec")
        filepath.write_text(candidate, encoding="utf-8")
        return True, f"fixed in {max_passes} passes"
    except (SyntaxError, IndentationError) as e:
        return False, f"still broken after {max_passes} passes: {e}"


def main():
    root = Path("agentic_core")
    broken_files = []

    for p in sorted(root.rglob("*.py")):
        try:
            source = p.read_text("utf-8")
            compile(source, str(p), "exec")
        except (SyntaxError, IndentationError):
            broken_files.append(p)

    print(f"Broken source files: {len(broken_files)}")

    fixed = 0
    still_broken = []

    for p in broken_files:
        changed, status = fix_file(p)
        if changed:
            fixed += 1
            print(f"  FIXED: {p} ({status})")
        else:
            still_broken.append((str(p).replace("\\", "/"), status))

    print(f"\nFixed: {fixed}")
    print(f"Still broken: {len(still_broken)}")

    if still_broken:
        print("\nStill broken (need manual fix):")
        for fp, status in still_broken:
            print(f"  {fp}: {status}")

    return fixed, still_broken


if __name__ == "__main__":
    fixed, still_broken = main()
    sys.exit(1 if still_broken and fixed == 0 else 0)
