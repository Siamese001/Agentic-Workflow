"""Identify missing agent tests and optionally generate minimal smoke-test stubs."""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

CLASS_SUFFIXES = ("Agent", "Specialist", "Architect", "Auditor", "Validator")


def _find_project_root() -> Path:
    current = Path(__file__).resolve().parent
    for candidate in (current, *current.parents):
        if (candidate / "l0_scripts").exists() and (candidate / "L0_routing_scripts").exists():
            return candidate
    return Path(__file__).resolve().parents[1]


def _iter_python_files(project_root: Path):
    for path in project_root.rglob("*.py"):
        if "__pycache__" not in path.parts and "tests" not in path.parts:
            yield path


def _discover_agents(project_root: Path) -> list[dict]:
    agents = []
    for path in _iter_python_files(project_root):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (OSError, SyntaxError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name.endswith(CLASS_SUFFIXES):
                agents.append(
                    {"class_name": node.name, "path": str(path.relative_to(project_root)).replace("\\", "/")}
                )
    return agents


def _test_path(project_root: Path, agent: dict) -> Path:
    return project_root / "tests" / "other" / f"test_{agent['class_name']}.py"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Identify missing tests for discovered agents")
    parser.add_argument("--apply", action="store_true", help="Write generated tests to disk")
    parser.add_argument(
        "--limit", type=int, default=0, help="Maximum missing tests to generate; 0 means no limit"
    )
    args = parser.parse_args(argv)

    project_root = _find_project_root()
    agents = _discover_agents(project_root)
    missing = []
    for agent in agents:
        test_file = _test_path(project_root, agent)
        if not test_file.exists():
            missing.append((agent, test_file))

    print(f"Missing tests: {len(missing)}")
    generated = 0
    for agent, test_file in missing:
        if args.limit and generated >= args.limit:
            break
        print(
            f"  {'✅ generating' if args.apply else '📝 would generate'} {test_file.relative_to(project_root)}"
        )
        if args.apply:
            test_file.parent.mkdir(parents=True, exist_ok=True)
            test_file.write_text(
                f'""Auto-generated smoke tests for {agent["class_name"]}."""\n\nfrom pathlib import Path\n\n\ndef test_source_file_exists():\n    assert (Path(__file__).resolve().parents[2] / "{agent["path"]}").exists()\n',
                encoding="utf-8",
            )
        generated += 1

    print(f"Total tests {'generated' if args.apply else 'planned'}: {generated}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
