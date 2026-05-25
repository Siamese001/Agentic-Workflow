"""Fix over-broad W5 codemod: same-dir modules -> relative imports."""
from __future__ import annotations

import re
from pathlib import Path

PKG = Path("agentic_core/L6_system_learning")
PREFIX = "agentic_core.L6_system_learning"

FROM_ABS = re.compile(
    rf"^(\s*)from\s+{re.escape(PREFIX)}\.([a-zA-Z0-9_]+)\s+import\s+",
    re.M,
)
IMPORT_ABS = re.compile(
    rf"^(\s*)import\s+{re.escape(PREFIX)}\.([a-zA-Z0-9_]+)\s*(?:as\s+(\w+))?\s*$",
    re.M,
)


def fix_file(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    parent = path.parent
    n = 0

    def from_repl(m: re.Match[str]) -> str:
        nonlocal n
        mod = m.group(2)
        if (parent / f"{mod}.py").is_file() or (parent / mod / "__init__.py").is_file():
            n += 1
            return f"{m.group(1)}from .{mod} import "
        return m.group(0)

    def import_repl(m: re.Match[str]) -> str:
        nonlocal n
        mod = m.group(2)
        if (parent / f"{mod}.py").is_file():
            n += 1
            alias = m.group(3)
            if alias:
                return f"{m.group(1)}from . import {mod} as {alias}"
            return f"{m.group(1)}from . import {mod}"
        return m.group(0)

    new = FROM_ABS.sub(from_repl, text)
    new = IMPORT_ABS.sub(import_repl, new)
    if n:
        path.write_text(new, encoding="utf-8")
    return n


def main() -> None:
    total = 0
    files = 0
    for py in PKG.rglob("*.py"):
        c = fix_file(py)
        if c:
            files += 1
            total += c
            print(f"{py.as_posix()}: {c}")
    print(f"fixed {total} imports in {files} files")


if __name__ == "__main__":
    main()
