"""
Repair script: remove misplaced SSOT import blocks (injected mid-code by v2 fixer)
and re-insert them at true module level.

Targets files that have a SyntaxError due to the SSOT block appearing at col-0
inside an indented context.
"""

from __future__ import annotations

import ast
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]

SSOT_IMPORT_LINES = [
    "from agentic_core.L5_safety.config.structure_blueprint.ssot import (",
    "    DISCOVERY_EXCLUDED_TERRITORIES,",
    "    GLOBAL_EXCLUDED_DIRS,",
    "    SOVEREIGN_EXCLUDED_FOLDERS,",
    ")",
]
# Some files only imported 2 of the 3
SSOT_IMPORT_PARTIAL_2 = [
    "from agentic_core.L5_safety.config.structure_blueprint.ssot import (",
    "    GLOBAL_EXCLUDED_DIRS,",
    "    SOVEREIGN_EXCLUDED_FOLDERS,",
    ")",
]

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


def _has_syntax_error(src: str) -> bool:
    try:
        ast.parse(src)
        return False
    except SyntaxError:
        return True


def _find_ssot_block(lines: list[str]) -> tuple[int, int] | None:
    """Return (start, end_inclusive) of the first SSOT import block, or None."""
    for i, line in enumerate(lines):
        if re.match(
            r"from agentic_core\.L5_safety\.config\.structure_blueprint\.ssot import",
            line.strip(),
        ):
            # Find closing paren
            j = i
            while j < len(lines):
                if lines[j].strip() == ")":
                    return (i, j)
                j += 1
            return (i, i)  # single-line form (unlikely but safe)
    return None


def _module_level_insert_point(lines: list[str]) -> int:
    """After last top-level import, before first non-import code."""
    last_import = -1
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue
        # Skip module docstring
        if i == 0 or (last_import == -1 and stripped.startswith(('"""', "'''"))):
            q = stripped[:3]
            if stripped.count(q) >= 2:
                i += 1
                continue
            i += 1
            while i < len(lines) and q not in lines[i]:
                i += 1
            i += 1
            continue
        if stripped.startswith("import ") or stripped.startswith("from "):
            last_import = i
            # advance past multi-line
            if "(" in stripped and ")" not in stripped:
                i += 1
                while i < len(lines):
                    if ")" in lines[i]:
                        last_import = i
                        i += 1
                        break
                    i += 1
            else:
                i += 1
        else:
            break
    return last_import + 1 if last_import >= 0 else 0


def fix_file(path: pathlib.Path) -> str | None:
    """Return 'fixed', 'skip', or 'error'."""
    src = path.read_text(encoding="utf-8", errors="replace")
    if not _has_syntax_error(src):
        return "skip"

    lines = src.splitlines()

    # Find the SSOT block
    block = _find_ssot_block(lines)
    if block is None:
        return "skip"  # syntax error unrelated to our injection

    start, end = block

    # Check if it's truly misplaced (not at col 0, or col 0 but inside indented context)
    # A misplaced block appears at col 0 but inside try/if/def/class indentation
    # We detect this by looking at context: if removing the block fixes the syntax error
    candidate = lines[:start] + lines[end + 1 :]
    # Skip blank line after the block if present
    if end + 1 < len(lines) and not lines[end + 1].strip():
        candidate = lines[:start] + lines[end + 2 :]

    test_src = "\n".join(candidate)

    # Remove block, see if rest parses (with or without the import)
    if _has_syntax_error(test_src):
        # Remaining code still has issues — don't touch
        return "skip"

    # Good: removing the misplaced block fixes the syntax.
    # Now re-insert at module level if not already present.
    has_ssot = any(
        "from agentic_core.L5_safety.config.structure_blueprint.ssot import" in l for l in candidate
    )
    if not has_ssot:
        insert_pt = _module_level_insert_point(candidate)
        candidate = candidate[:insert_pt] + SSOT_IMPORT_LINES + [""] + candidate[insert_pt:]

    new_src = "\n".join(candidate)
    if not new_src.endswith("\n"):
        new_src += "\n"

    if _has_syntax_error(new_src):
        return "error"

    path.write_text(new_src, encoding="utf-8")
    return "fixed"


def main() -> int:
    fixed = skipped = errors = 0
    for p in sorted(ROOT.rglob("*.py")):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        result = fix_file(p)
        if result == "fixed":
            print(f"FIXED  {p.relative_to(ROOT)}")
            fixed += 1
        elif result == "error":
            print(f"ERROR  {p.relative_to(ROOT)}")
            errors += 1

    print(f"\nfixed={fixed}, skipped={skipped}, errors={errors}")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
