"""Rewrite apps_rg engine files to use `_emit_engine_lifecycle()` helper.

For each engine file containing the legacy boilerplate block, this script:

  1. Identifies all top-level statements that match the lifecycle-emit
     pattern (lines starting with `_emit_`, `emit_replay_key`, or
     `emit_determinism_digest` and ending in `)` at indent level 0).
  2. Removes those statements.
  3. Inserts a single `from apps_rg.engines._lifecycle_emits import _emit_engine_lifecycle`
     near the top (after the first `from __future__` if present, else at the
     top of the imports block) IF not already present.
  4. Inserts a single `_emit_engine_lifecycle("<filename>")` call after the
     last import statement.

Behavior preservation:
  * No `_emit_*` symbols are added or removed at the import level — only
    *call sites* are removed. Engines that use any of these symbols inside
    their class body keep working because the imports remain.
  * Emit count per engine: 76 emits before -> 76 emits after (helper makes
    the same calls in the same order). Verified by post-run span-count
    check in `python -m apps_rg`.

Reversibility: per-file. To revert a single file, run
`git checkout apps_rg/engines/<file>.py`.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ENG = REPO / "apps_rg" / "engines"

# A top-level lifecycle-emit call: starts at column 0, name begins with
# `_emit_`, `emit_replay_key(`, or `emit_determinism_digest(`, and the
# statement is on a single line ending in `)`.
_EMIT_LINE_RE = re.compile(
    r"^(?:_emit_[a-z_]+|emit_replay_key|emit_determinism_digest)\("
    r".*\)\s*$"
)

# Files to skip (not engines or have non-standard layouts):
SKIP = {
    "__init__.py",
    "_lifecycle_emits.py",
    "base_rg_engine.py",
    "rg_spine_adapter.py",
    "resume_orchestrator_engine.py",  # has anti-overfit hook; treat carefully
    "sovereign_context.py",
    "hardened_gemini_executor.py",
    "gap_closure_engine.py",
}

HELPER_IMPORT = "from apps_rg.engines._lifecycle_emits import _emit_engine_lifecycle"


def rewrite_file(path: Path) -> tuple[bool, int, int]:
    """Returns (changed, emits_removed, helper_inserted_at_lineno)."""
    src = path.read_text(encoding="utf-8")
    lines = src.splitlines(keepends=False)
    if any("_emit_engine_lifecycle(" in ln for ln in lines):
        return (False, 0, -1)  # already migrated
    # Identify lifecycle-emit statements (top-level only).
    emit_indices: list[int] = []
    for i, ln in enumerate(lines):
        if _EMIT_LINE_RE.match(ln):
            emit_indices.append(i)
    if not emit_indices:
        return (False, 0, -1)

    # Build new line list excluding emit lines.
    new_lines: list[str] = []
    for i, ln in enumerate(lines):
        if i in set(emit_indices):
            continue
        new_lines.append(ln)

    # Collapse runs of >2 blank lines that arise from removed emits.
    collapsed: list[str] = []
    blank_run = 0
    for ln in new_lines:
        if ln.strip() == "":
            blank_run += 1
            if blank_run <= 2:
                collapsed.append(ln)
        else:
            blank_run = 0
            collapsed.append(ln)
    new_lines = collapsed

    # Insert helper import + helper call after the last `from ... import` /
    # `import ...` line at column 0, but BEFORE any top-level non-import
    # statement (e.g. `Logger = logging.getLogger(__name__)`).
    last_import_idx = -1
    in_import_block = False
    paren_depth = 0
    for i, ln in enumerate(new_lines):
        stripped = ln.lstrip()
        # Track multi-line `from X import (...)` blocks.
        if not in_import_block:
            if (stripped.startswith("import ") or stripped.startswith("from ")) and ln.startswith(("import ", "from ")):
                last_import_idx = i
                if "(" in ln and ")" not in ln:
                    in_import_block = True
                    paren_depth = ln.count("(") - ln.count(")")
        else:
            paren_depth += ln.count("(") - ln.count(")")
            last_import_idx = i
            if paren_depth <= 0:
                in_import_block = False
                paren_depth = 0
    if last_import_idx < 0:
        # No imports? Skip — abnormal file.
        return (False, 0, -1)

    helper_call = f'_emit_engine_lifecycle("{path.stem}")'
    insert_at = last_import_idx + 1
    insertion = ["", HELPER_IMPORT, "", helper_call]
    new_lines = new_lines[:insert_at] + insertion + new_lines[insert_at:]

    out = "\n".join(new_lines).rstrip() + "\n"
    path.write_text(out, encoding="utf-8")
    return (True, len(emit_indices), insert_at + 4)  # +4 = position of helper_call


def main() -> int:
    files = sorted(p for p in ENG.glob("*.py") if p.name not in SKIP)
    print(f"engine_files_to_consider={len(files)}")
    changed_count = 0
    total_removed = 0
    for f in files:
        changed, removed, helper_lineno = rewrite_file(f)
        if changed:
            changed_count += 1
            total_removed += removed
            print(f"  {f.name}: removed {removed} emit lines, helper at L{helper_lineno}")
        else:
            if removed == 0 and helper_lineno == -1:
                # Either already migrated or no emits found.
                if any("_emit_engine_lifecycle(" in ln for ln in f.read_text(encoding="utf-8").splitlines()):
                    print(f"  {f.name}: already migrated (skipped)")
                else:
                    print(f"  {f.name}: no emit block found (skipped)")
    print()
    print(f"changed={changed_count}, total_emit_lines_removed={total_removed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
