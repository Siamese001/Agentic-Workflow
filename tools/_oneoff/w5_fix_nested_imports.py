"""Resolve flat agentic_core.L6_system_learning.<mod> imports to correct submodule paths."""
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


def module_path(mod: str) -> Path | None:
    for candidate in (PKG / f"{mod}.py", PKG / mod / "__init__.py"):
        if candidate.is_file():
            return candidate
    matches = sorted(PKG.rglob(f"{mod}.py"))
    if len(matches) == 1:
        return matches[0]
    return None


def relative_import(from_file: Path, target: Path) -> str:
    from_pkg = from_file.parent
    target_mod = target.with_suffix("")
    rel = target_mod.relative_to(PKG)
    parts = list(rel.parts)
    if target.name == "__init__.py":
        parts = parts[:-1]
    # build relative from from_pkg to target package
    from_parts = list(from_pkg.relative_to(PKG).parts)
    common = 0
    for a, b in zip(from_parts, parts, strict=False):
        if a != b:
            break
        common += 1
    ups = [".."] * (len(from_parts) - common)
    down = parts[common:]
    segs = ups + down
    if not segs:
        return "."
    return "." + ("." + ".".join(segs) if segs[0] == ".." else ".".join(segs))


def fix_file(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    n = 0

    def repl(m: re.Match[str]) -> str:
        nonlocal n
        mod = m.group(1)
        target = module_path(mod)
        if target is None:
            return m.group(0)
        # Keep canonical cross-subpackage absolute imports when module is a top-level subpackage.
        rel_parts = target.relative_to(PKG).parts
        if len(rel_parts) == 2 and rel_parts[0] in TOP_LEVEL and rel_parts[1] == f"{mod}.py":
            return m.group(0)
        if len(rel_parts) == 1 and rel_parts[0] == f"{mod}.py" and mod in TOP_LEVEL:
            return m.group(0)
        if target is None:
            return m.group(0)
        rel = relative_import(path, target)
        n += 1
        return f"from {rel} import"

    new = FROM_RE.sub(repl, text)
    if n:
        path.write_text(new, encoding="utf-8")
    return n


def main() -> None:
    total = 0
    for py in PKG.rglob("*.py"):
        c = fix_file(py)
        if c:
            print(f"{py.relative_to(REPO).as_posix()}: {c}")
            total += c
    print(f"total {total}")


if __name__ == "__main__":
    main()
