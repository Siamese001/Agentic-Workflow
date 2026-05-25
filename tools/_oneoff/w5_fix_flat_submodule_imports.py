"""Map flat agentic_core.L6_system_learning.<name> imports to canonical submodule paths."""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PKG = REPO / "agentic_core" / "L6_system_learning"
PREFIX = "agentic_core.L6_system_learning"
TOP_LEVEL = {p.name for p in PKG.iterdir() if p.is_dir() and not p.name.startswith("_")}

FROM_RE = re.compile(
    rf"from\s+{re.escape(PREFIX)}\.([a-zA-Z0-9_]+)\s+import"
)
IMPORT_RE = re.compile(
    rf"import\s+{re.escape(PREFIX)}\.([a-zA-Z0-9_]+)(?:\s+as\s+(\w+))?"
)


def _mod_dotted(target: Path) -> str:
    rel = target.with_suffix("").relative_to(PKG)
    parts = list(rel.parts)
    if target.name == "__init__.py":
        parts = parts[:-1]
    return f"{PREFIX}.{'.'.join(parts)}"


def resolve_module(mod: str) -> str | None:
    if (PKG / f"{mod}.py").is_file() or (PKG / mod / "__init__.py").is_dir():
        return None  # already valid top-level
    matches = sorted(PKG.rglob(f"{mod}.py"))
    if len(matches) != 1:
        return None
    dotted = _mod_dotted(matches[0])
    if dotted == f"{PREFIX}.{mod}":
        return None
    return dotted


def fix_file(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    n = 0

    def from_repl(m: re.Match[str]) -> str:
        nonlocal n
        mod = m.group(1)
        dotted = resolve_module(mod)
        if not dotted:
            return m.group(0)
        n += 1
        return f"from {dotted} import"

    def import_repl(m: re.Match[str]) -> str:
        nonlocal n
        mod = m.group(1)
        alias = m.group(2)
        dotted = resolve_module(mod)
        if not dotted:
            return m.group(0)
        n += 1
        tail = f" as {alias}" if alias else ""
        return f"import {dotted}{tail}"

    new = FROM_RE.sub(from_repl, text)
    new = IMPORT_RE.sub(import_repl, new)
    if n:
        path.write_text(new, encoding="utf-8")
    return n


def main() -> None:
    total = 0
    for py in sorted(PKG.rglob("*.py")):
        c = fix_file(py)
        if c:
            print(f"{py.relative_to(REPO).as_posix()}: {c}")
            total += c
    print(f"total {total}")


if __name__ == "__main__":
    main()
