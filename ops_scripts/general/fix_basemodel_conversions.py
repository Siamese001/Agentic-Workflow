"""
Convert selected Pydantic BaseModel classes to a dataclass-oriented pattern.
"""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

BASEMODEL_FILES = [
    "knowledge_graph_agent.py",
    "onboarding_planner_agent.py",
    "stack_modernization_agent.py",
]


def _resolve_repo_root(explicit_root: str | None = None) -> Path:
    if explicit_root:
        return Path(explicit_root).expanduser().resolve()
    env_root = os.getenv("AGENTIC_WORKFLOW_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    for candidate in Path(__file__).resolve().parents:
        if (candidate / ".git").exists():
            return candidate
    return Path.cwd().resolve()


def _atomic_write(path: Path, content: str) -> None:
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(content, encoding="utf-8")
    tmp_path.replace(path)


def convert_basemodel_to_dataclass(file_path: Path, execute: bool = False) -> bool:
    """Convert Pydantic BaseModel classes to dataclasses."""
    content = file_path.read_text(encoding="utf-8", errors="replace")
    if "BaseModel" not in content:
        return False

    original_content = content
    if "from dataclasses import dataclass, field" not in content:
        lines = content.split("\n")
        insert_idx = 0
        for index, line in enumerate(lines):
            if line.startswith("from __future__"):
                insert_idx = index + 1
                break
            if line.startswith("import ") or line.startswith("from "):
                insert_idx = index
                break
        lines.insert(insert_idx, "from __future__ import annotations")
        lines.insert(insert_idx + 1, "from dataclasses import dataclass, field")
        lines.insert(insert_idx + 2, "from typing import Any")
        content = "\n".join(lines)

    content = re.sub(r"class (\w+)\(BaseModel\):", r"@dataclass\nclass \1:", content)
    content = re.sub(r"Field\(", "field(", content)
    content = re.sub(r"= Field\(default_factory=", "= field(default_factory=", content)
    content = re.sub(
        r"\s*@validator\([^)]+\)\s*\n\s*def [^:]+:[^}]+",
        "",
        content,
        flags=re.MULTILINE,
    )
    content = re.sub(
        r"field\(([^,]+), ge=([^,]+), le=([^,]+)",
        'field(\1, metadata={"ge": \2, "le": \3}',
        content,
    )

    if content == original_content:
        return False

    if execute:
        _atomic_write(file_path, content)
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Convert selected BaseModel classes to a dataclass-oriented pattern.",
    )
    parser.add_argument("--repo-root", help="Override automatic repository root detection.")
    parser.add_argument("--execute", action="store_true", help="Actually write changes. Default is dry-run.")
    args = parser.parse_args(argv)

    repo_root = _resolve_repo_root(args.repo_root)
    engines_dir = repo_root / "apps_lic" / "engines"

    print("🔄 Converting BaseModel to Sovereign Dataclasses")
    print("=" * 60)
    if not args.execute:
        print("[DRY RUN] No files will be modified.\n")

    fixed_count = 0
    for filename in BASEMODEL_FILES:
        file_path = engines_dir / filename
        if not file_path.exists():
            print(f"  ❌ {filename} not found")
            continue
        if convert_basemodel_to_dataclass(file_path, execute=args.execute):
            print(f"  {'✅' if args.execute else '○'} {filename}")
            fixed_count += 1
        else:
            print(f"  ⚠️  {filename} - no changes needed")

    print("\n" + "=" * 60)
    print(f"{'Converted' if args.execute else 'Would convert'} {fixed_count} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
