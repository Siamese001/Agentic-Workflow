"""
Fix multiline for-loops that _fix_progress.py could not handle.

Pattern: the for-statement spans multiple lines because the iterable
is a list/tuple literal or a multi-arg call:

    for var in [          for var in (
        item1,                item1,
        item2,                item2,
    ]:                    ):

Strategy:
1. Locate the for-loop at the flagged line.
2. If the line ends with `in [` or `in (` (optionally with space/comment),
   insert `tqdm(` between `in ` and the opening bracket.
3. Walk forward to find the closing bracket+colon at indent level 0 relative
   to the for-loop. Insert `, desc="Processing", unit="item")` before `:`.
4. Ensure `from tqdm import tqdm` is present at top level.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


# ---------------------------------------------------------------------------
# Violation collection
# ---------------------------------------------------------------------------


def get_violations() -> dict[str, list[int]]:
    """Return {filepath: [lineno, ...]} for all remaining violations."""
    result = subprocess.run(
        [sys.executable, "ops_scripts/ci/check_query_progress_bar.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=180,
    )
    violations: dict[str, list[int]] = {}
    for raw in result.stdout.splitlines():
        raw = raw.strip().lstrip("- ").strip()
        m = re.match(r"^(.+?\.py):(\d+):", raw.replace("\\", "/"))
        if m:
            fp = m.group(1)
            ln = int(m.group(2))
            violations.setdefault(fp, []).append(ln)
    return violations


# ---------------------------------------------------------------------------
# Core fixer
# ---------------------------------------------------------------------------


def _find_closing_bracket(lines: list[str], start_idx: int, open_char: str) -> int:
    """
    Starting from start_idx, find the line index of the closing bracket
    that matches open_char (either '[' or '(').
    Returns the 0-indexed line number, or -1 if not found.
    """
    close_char = "]" if open_char == "[" else ")"
    depth = 0
    for i in range(start_idx, len(lines)):
        for ch in lines[i]:
            if ch == open_char:
                depth += 1
            elif ch == close_char:
                depth -= 1
                if depth == 0:
                    return i
    return -1


def fix_multiline_for(lines: list[str], lineno: int) -> bool:
    """
    Try to wrap the multiline for-loop at lineno (1-indexed) with tqdm.
    Returns True if the file was modified.
    """
    idx = lineno - 1  # 0-indexed
    if idx >= len(lines):
        return False

    line = lines[idx]

    # Already has tqdm — skip
    if "tqdm(" in line:
        return False

    # Match:  <indent>(async )? for <vars> in <open_bracket>
    m = re.match(
        r"^(\s*)(async\s+)?for\s+(.+?)\s+in\s+(\[|\()(.*)$",
        line.rstrip("\n"),
    )
    if not m:
        return False

    indent = m.group(1)
    async_ = m.group(2) or ""
    var = m.group(3)
    open_br = m.group(4)
    rest_of_line = m.group(5)  # anything after the opening bracket

    close_idx = _find_closing_bracket(lines, idx, open_br)
    if close_idx == -1:
        return False

    close_line = lines[close_idx].rstrip("\n")

    # The close line should end with ]: or ): (possibly with trailing comment/spaces)
    close_char = "]" if open_br == "[" else ")"
    cm = re.match(r"^(\s*\\" + re.escape(close_char) + r")(\s*:)(\s*(?:#.*)?)$", close_line)
    if not cm:
        # Try a more relaxed match: line contains the close char then a colon
        cm2 = re.search(re.escape(close_char) + r"\s*:", close_line)
        if not cm2:
            return False
        # Replace the first occurrence of close_char + ':' with close_char + ', ...)'
        new_close = close_line.replace(
            close_char + ":",
            f'{close_char}, desc="Processing", unit="item"):',
            1,
        )
        # Also need to add closing paren for the tqdm() call before ':'
        # Actually we're inserting `tqdm(` on the for line, and closing `)` on the close line
        # The close line was `]:`; now needs to be `], desc="...", unit="item"):`
        lines[close_idx] = new_close + "\n"
    else:
        prefix = cm.group(1)
        colon = cm.group(2)
        comment = cm.group(3)
        lines[close_idx] = f'{prefix}, desc="Processing", unit="item"){colon}{comment}\n'

    # Update the for line: insert `tqdm(` after `in `
    lines[idx] = (
        f"{indent}{async_}for {var} in tqdm({open_br}{rest_of_line}\n"
        if rest_of_line
        else f"{indent}{async_}for {var} in tqdm({open_br}\n"
    )

    return True


def ensure_tqdm_import(lines: list[str]) -> list[str]:
    """Add `from tqdm import tqdm` at top level if not already present."""
    if any(l.strip() == "from tqdm import tqdm" for l in lines):
        return lines

    # Find last top-level import line
    insert_after = 0
    for i, line in enumerate(lines):
        s = line.strip()
        if line[0:1] not in (" ", "\t") and s.startswith(("from __future__", "import ", "from ")):
            insert_after = i + 1

    new_lines = list(lines)
    new_lines.insert(insert_after, "from tqdm import tqdm\n")
    return new_lines


def fix_file(filepath: str, linenos: list[int]) -> int:
    full = ROOT / filepath
    if not full.exists():
        return 0

    lines = full.read_text(encoding="utf-8").splitlines(keepends=True)
    needs_import = not any(l.strip() == "from tqdm import tqdm" for l in lines)

    fixed = 0
    for ln in sorted(linenos, reverse=True):
        if fix_multiline_for(lines, ln):
            fixed += 1
        else:
            print(f"  SKIP line {ln}: pattern not recognized in {filepath}")

    if fixed == 0:
        return 0

    if needs_import:
        lines = ensure_tqdm_import(lines)

    full.write_text("".join(lines), encoding="utf-8")
    return fixed


def main() -> None:
    violations = get_violations()
    total = sum(len(v) for v in violations.values())
    print(f"Remaining violations: {total} across {len(violations)} files\n")

    total_fixed = 0
    for fp, lns in sorted(violations.items()):
        n = fix_file(fp, lns)
        if n:
            print(f"  Fixed {n}/{len(lns)} in {fp}")
            total_fixed += n

    print(f"\nTotal fixed: {total_fixed}")

    # Final check
    result = subprocess.run(
        [sys.executable, "ops_scripts/ci/check_query_progress_bar.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=180,
    )
    remaining = sum(1 for l in result.stdout.splitlines() if re.match(r"^\s*-\s+.+\.py:\d+:", l))
    if remaining == 0:
        print("[PASS] No remaining violations.")
    else:
        print(f"[WARN] {remaining} violations remain.")
        print(result.stdout[-2000:])


if __name__ == "__main__":
    main()
