"""Bulk-update L6 doc folder path after W2 rename (one-off)."""
from __future__ import annotations

from pathlib import Path

OLD = "06_L6_Observability_and_System_Learning"
NEW = "06_L6_Observability_and_System_Learning"
SKIP_PARTS = {
    ".git",
    "__pycache__",
    ".venv",
    "node_modules",
    ".pytest_cache",
    "artifacts",
}
SKIP_PATH_FRAGMENTS = (
    "/_archive/",
    "\\_archive\\",
    "pre-reqid-rewrite",
    ".bak",
)


def should_skip(path: Path) -> bool:
    if any(p in SKIP_PARTS for p in path.parts):
        return True
    s = path.as_posix()
    return any(f in s for f in SKIP_PATH_FRAGMENTS)


def walk_roots() -> list[Path]:
    return [
        Path("docs/reference"),
        Path("system_learning"),
        Path("agentic_core"),
        Path("tests"),
        Path("tools"),
        Path("ops_scripts"),
        Path(".claude/plans/l6-repo-reorganization-mental-model-c4e8f2.md"),
        Path("docs/reports/cursor"),
    ]


def main() -> None:
    changed: list[str] = []
    for root in walk_roots():
        if root.is_file():
            paths = [root]
        else:
            paths = [p for p in root.rglob("*") if p.is_file()]
        for path in paths:
            if should_skip(path):
                continue
            if path.suffix.lower() not in {
                ".md",
                ".json",
                ".py",
                ".yaml",
                ".yml",
                ".csv",
                ".txt",
            }:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if OLD not in text:
                continue
            path.write_text(text.replace(OLD, NEW), encoding="utf-8")
            changed.append(path.as_posix())
    print(f"updated {len(changed)} files")
    for c in sorted(changed)[:40]:
        print(" ", c)
    if len(changed) > 40:
        print(f"  ... and {len(changed) - 40} more")


if __name__ == "__main__":
    main()
