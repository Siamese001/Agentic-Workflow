"""
One-shot repair script: fix bad SSOT import injections that were placed inside
try blocks or other indented contexts by _fix_hardcoded_dirs_v2.py.

The pattern to fix is:
    try:
        <something>
    from agentic_core.L5_safety.config.structure_blueprint.ssot import (
        DISCOVERY_EXCLUDED_TERRITORIES,
        GLOBAL_EXCLUDED_DIRS,
        SOVEREIGN_EXCLUDED_FOLDERS,
    )
    except ...:

Which should become:
    from agentic_core.L5_safety.config.structure_blueprint.ssot import (
        DISCOVERY_EXCLUDED_TERRITORIES,
        GLOBAL_EXCLUDED_DIRS,
        SOVEREIGN_EXCLUDED_FOLDERS,
    )
    try:
        <something>
    except ...:

Also fixes "unexpected indent" cases where the import was injected after an
indented block without proper dedent.
"""

from __future__ import annotations

import ast
import pathlib
import re
import sys

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

ROOT = pathlib.Path(__file__).resolve().parents[2]

SSOT_IMPORT_BLOCK = """\
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
from agentic_core.L0_routing.config.path_constants import ARCHIVES_DIR
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)"""

SSOT_IMPORT_LINES = SSOT_IMPORT_BLOCK.splitlines()

SKIP_DIRS: frozenset[str] = frozenset(
    {
        ".venv",
        "venv",
        "__pycache__",
        ARCHIVES_DIR,
        "node_modules",
        ".healing_backups",
        ".sovereign_healing_backup",
    }
)


def has_syntax_error(src: str) -> bool:
    try:
        ast.parse(src)
        return False
    except SyntaxError:
        return True


def already_has_ssot_import(lines: list[str]) -> bool:
    for i, line in enumerate(lines):
        if "from agentic_core.L5_safety.config.structure_blueprint.ssot import" in line:
            # Check it's at module level (no leading whitespace)
            if not line[0].isspace():
                return True
    return False


def find_ssot_injection_indices(lines: list[str]) -> list[int]:
    """Return the start line indices of injected SSOT import blocks."""
    result = []
    for i, line in enumerate(lines):
        if "from agentic_core.L5_safety.config.structure_blueprint.ssot import" in line:
            result.append(i)
    return result


def remove_lines(lines: list[str], start: int, count: int) -> list[str]:
    return lines[:start] + lines[start + count :]


def insert_at(lines: list[str], idx: int, new_lines: list[str]) -> list[str]:
    return lines[:idx] + new_lines + [""] + lines[idx:]


def find_module_level_insert_point(lines: list[str]) -> int:
    """Find the best module-level position to insert an import block.

    Strategy: insert after the last top-level import statement found before
    any non-import module-level code, or after the module docstring.
    """
    in_docstring = False
    docstring_done = False
    last_import_line = -1
    first_code_line = -1

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Skip blank lines and comments
        if not stripped or stripped.startswith("#"):
            i += 1
            continue

        # Track docstring
        if not docstring_done:
            if stripped.startswith('"""') or stripped.startswith("'''"):
                quote = stripped[:3]
                if stripped.count(quote) >= 2:
                    # Single-line docstring
                    docstring_done = True
                    i += 1
                    continue
                else:
                    # Multi-line docstring
                    i += 1
                    while i < len(lines):
                        if quote in lines[i]:
                            i += 1
                            break
                        i += 1
                    docstring_done = True
                    continue
            else:
                docstring_done = True

        # Track imports
        if stripped.startswith("import ") or stripped.startswith("from "):
            last_import_line = i
            i += 1
            # Handle multi-line imports
            while i < len(lines) and lines[i - 1].rstrip().endswith("\\"):
                i += 1
            # Handle parenthesized imports
            if "(" in line and ")" not in line:
                while i < len(lines):
                    if ")" in lines[i]:
                        last_import_line = i
                        i += 1
                        break
                    i += 1
        else:
            if first_code_line == -1:
                first_code_line = i
            i += 1

    if last_import_line >= 0:
        return last_import_line + 1
    if first_code_line >= 0:
        return first_code_line
    return 0


def fix_file(path: pathlib.Path, dry_run: bool = False) -> bool:
    src = path.read_text(encoding="utf-8", errors="replace")
    if not has_syntax_error(src):
        return False

    lines = src.splitlines()

    # Find all injected SSOT import block start indices
    injection_indices = find_ssot_injection_indices(lines)
    if not injection_indices:
        return False

    # For each injection, check if it's at module level (no leading whitespace)
    bad_injections = [i for i in injection_indices if lines[i][0].isspace()]
    # Also catch non-indented but inside try (preceded by try: ... no except yet)
    for i in injection_indices:
        if not lines[i][0].isspace() and i not in bad_injections:
            # Check if lines before it are part of a try block without except
            # by looking for a bare 'from' after a try: line
            # Heuristic: if the line before (non-blank) ends with ':' and is 'try:'
            j = i - 1
            while j >= 0 and not lines[j].strip():
                j -= 1
            if j >= 0:
                prev = lines[j].strip()
                if prev and prev != ")" and not prev.startswith("from ") and not prev.startswith("import "):
                    # Check if any enclosing try block is unclosed
                    context = "\n".join(lines[:i])
                    try_count = len(re.findall(r"^\s*try\s*:", context, re.MULTILINE))
                    except_count = len(re.findall(r"^\s*except\b", context, re.MULTILINE))
                    if try_count > except_count:
                        bad_injections.append(i)

    if not bad_injections:
        return False

    # Process in reverse order to preserve indices
    new_lines = lines[:]
    ssot_block_size = 5  # from ... import (\n    D,\n    G,\n    S,\n)

    for injection_idx in sorted(set(bad_injections), reverse=True):
        # Remove the 5-line SSOT import block
        block_end = injection_idx
        # Find actual end of the block (closing paren)
        j = injection_idx
        while j < len(new_lines) and ")" not in new_lines[j]:
            j += 1
        block_end = j + 1  # inclusive end

        new_lines = new_lines[:injection_idx] + new_lines[block_end:]

    # Now insert at the proper module-level location (after removing bad injections)
    # Only add if not already present at module level
    if not already_has_ssot_import(new_lines):
        insert_point = find_module_level_insert_point(new_lines)
        import_lines = SSOT_IMPORT_LINES + [""]
        new_lines = new_lines[:insert_point] + import_lines + new_lines[insert_point:]

    new_src = "\n".join(new_lines)
    if not new_src.endswith("\n"):
        new_src += "\n"

    if has_syntax_error(new_src):
        print(f"  [SKIP] Could not fix syntax error in {path.relative_to(ROOT)}")
        return False

    if dry_run:
        print(f"  [DRY-RUN] Would fix {path.relative_to(ROOT)}")
        return True

    path.write_text(new_src, encoding="utf-8")
    print(f"  [FIXED] {path.relative_to(ROOT)}")
    return True


def main(dry_run: bool = False) -> int:
    fixed = 0
    errors = 0

    for p in sorted(ROOT.rglob("*.py")):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        try:
            result = fix_file(p, dry_run=dry_run)
            if result:
                fixed += 1
        except Exception as e:
            print(f"  [ERROR] {p.relative_to(ROOT)}: {e}")
            errors += 1

    print(f"\nDone. Fixed={fixed}, Errors={errors}, dry_run={dry_run}")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    sys.exit(main(dry_run=dry_run))
