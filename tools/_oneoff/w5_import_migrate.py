"""W5.2 mechanical import migration: system_learning -> agentic_core.L6_system_learning."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKIP_PARTS = {
    ".git",
    "__pycache__",
    ".venv",
    "node_modules",
    ".pytest_cache",
    "artifacts",
    ".playwright-mcp",
}
SKIP_FRAGMENTS = (
    "/_archive/",
    "\\_archive\\",
    "pre-reqid-rewrite",
    ".bak",
    "w5_import_migrate.py",
)
# Root shim is rewritten explicitly in W5.1 — do not codemod it.
SKIP_EXACT = {
    REPO / "system_learning" / "__init__.py",
}

FROM_RE = re.compile(r"\bfrom\s+system_learning(\.[A-Za-z0-9_]+)*\s+import\b")
IMPORT_RE = re.compile(r"\bimport\s+system_learning(\.[A-Za-z0-9_]+)*\b")
IMPORT_AS_RE = re.compile(r"\bimport\s+system_learning(\.[A-Za-z0-9_]+)*\s+as\s+")


def should_skip(path: Path) -> bool:
    if path in SKIP_EXACT:
        return True
    s = path.as_posix()
    if any(p in path.parts for p in SKIP_PARTS):
        return True
    return any(f in s for f in SKIP_FRAGMENTS)


def migrate_text(text: str) -> tuple[str, int]:
    n = 0

    def sub_from(m: re.Match[str]) -> str:
        nonlocal n
        n += 1
        suffix = m.group(1) or ""
        return f"from agentic_core.L6_system_learning{suffix} import"

    def sub_import(m: re.Match[str]) -> str:
        nonlocal n
        n += 1
        suffix = m.group(1) or ""
        return f"import agentic_core.L6_system_learning{suffix}"

    text = FROM_RE.sub(sub_from, text)
    text = IMPORT_AS_RE.sub(
        lambda m: f"import agentic_core.L6_system_learning{(m.group(1) or '')} as ",
        text,
    )
    text = IMPORT_RE.sub(sub_import, text)
    # importlib string literals
    text2, c1 = re.subn(
        r'import_module\(\s*["\']system_learning',
        'import_module("agentic_core.L6_system_learning',
        text,
    )
    text3, c2 = re.subn(
        r'["\']system_learning\.([A-Za-z0-9_.]+)["\']',
        r'"agentic_core.L6_system_learning.\1"',
        text2,
    )
    n += c1 + c2
    return text3, n


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    total_files = 0
    total_repls = 0
    changed: list[str] = []
    for path in REPO.rglob("*.py"):
        if should_skip(path):
            continue
        try:
            original = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if "system_learning" not in original:
            continue
        updated, n = migrate_text(original)
        if n and updated != original:
            total_files += 1
            total_repls += n
            changed.append(path.relative_to(REPO).as_posix())
            if not args.dry_run:
                path.write_text(updated, encoding="utf-8")
    print(f"files_changed={total_files} replacements={total_repls} dry_run={args.dry_run}")
    for c in sorted(changed)[:30]:
        print(f"  {c}")
    if len(changed) > 30:
        print(f"  ... +{len(changed) - 30} more")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
