"""Plan or apply safe legacy-agent inheritance updates for certification."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

CLASS_PATTERN = re.compile(
    r"class\s+(?P<name>\w+(?:Agent|Specialist|Architect))\s*\((?P<bases>[^)]*)\):",
    re.MULTILINE,
)
DEFAULT_BASE_IMPORT = "from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent\n"


def _find_project_root() -> Path:
    current = Path(__file__).resolve().parent
    for candidate in (current, *current.parents):
        if (candidate / "l0_scripts").exists() and (candidate / "L0_routing_scripts").exists():
            return candidate
    return Path(__file__).resolve().parents[1]


def _iter_candidate_files(project_root: Path, domains: list[str]):
    if domains:
        for domain in domains:
            root = (project_root / domain).resolve()
            if root.exists():
                yield from root.rglob("*.py")
        return
    for path in project_root.rglob("*.py"):
        if "__pycache__" not in path.parts and "tests" not in path.parts:
            yield path


def _rewrite_content(content: str, base_import: str) -> tuple[str, bool]:
    changed = False

    def replace(match: re.Match[str]) -> str:
        nonlocal changed
        bases = match.group("bases")
        if "SovereignBaseAgent" in bases or "MCPHardenedMixin" not in bases:
            return match.group(0)
        changed = True
        return f"class {match.group('name')}(SovereignBaseAgent):"

    new_content = CLASS_PATTERN.sub(replace, content)
    if changed and "SovereignBaseAgent" not in new_content:
        lines = new_content.splitlines(keepends=True)
        insert_at = 0
        if lines and lines[0].startswith("#!"):
            insert_at = 1
        if lines and "SovereignBaseAgent" not in "".join(lines[: insert_at + 1]):
            lines.insert(insert_at, base_import)
            new_content = "".join(lines)
    return new_content, changed


def fix_agent_file(file_path: Path, *, apply: bool, base_import: str) -> bool:
    try:
        content = file_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"[certification-fix] unable to read {file_path}: {exc}", file=sys.stderr)
        return False

    new_content, changed = _rewrite_content(content, base_import)
    if not changed:
        return False

    print(f"{'Applying' if apply else 'Would apply'}: {file_path}")
    if apply:
        try:
            file_path.write_text(new_content, encoding="utf-8")
        except OSError as exc:
            print(f"[certification-fix] unable to write {file_path}: {exc}", file=sys.stderr)
            return False
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Plan or apply SovereignBaseAgent inheritance fixes")
    parser.add_argument("--apply", action="store_true", help="Write changes to disk")
    parser.add_argument(
        "--domain", action="append", default=[], help="Relative directory to scan; repeatable"
    )
    parser.add_argument(
        "--base-import", default=DEFAULT_BASE_IMPORT.strip(), help="Import line to insert when needed"
    )
    args = parser.parse_args(argv)

    project_root = _find_project_root()
    fixed_count = 0
    scanned = 0
    for file_path in _iter_candidate_files(project_root, args.domain):
        scanned += 1
        if fix_agent_file(file_path, apply=args.apply, base_import=args.base_import + "\n"):
            fixed_count += 1

    print(f"Scanned {scanned} files")
    print(f"{'Fixed' if args.apply else 'Planned'} {fixed_count} legacy agents")
    return 0


if __name__ == "__main__":
    sys.exit(main())
