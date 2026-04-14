"""Generate smoke-test stubs for all discovered agent classes lacking tests."""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

LAYER_PRIORITY = ["L5", "L4", "L3", "L2", "L1", "L0", "Base", "L6", "Apps", "Utils", "Other"]
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


def _infer_layer(path: Path) -> str:
    text = str(path).replace("\\", "/")
    if "/L0_routing_scripts/" in text or "/l0_scripts/" in text or "/L0_routing/" in text:
        return "L0"
    if "/L1_" in text:
        return "L1"
    if "/L2_" in text:
        return "L2"
    if "/L3_" in text:
        return "L3"
    if "/L4_" in text:
        return "L4"
    if "/L5_" in text:
        return "L5"
    return "Other"


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
                    {
                        "class_name": node.name,
                        "path": str(path.relative_to(project_root)).replace("\\", "/"),
                        "layer": _infer_layer(path),
                    }
                )
    return agents


def _test_path(project_root: Path, agent: dict) -> Path:
    return project_root / "tests" / agent["layer"].lower() / f"test_{agent['class_name']}.py"


def _module_template(agent: dict) -> str:
    return f'''"""Auto-generated smoke tests for {agent["class_name"]}."""

from __future__ import annotations

from pathlib import Path


def test_source_file_exists():
    source_path = Path(__file__).resolve().parents[2] / "{agent["path"]}"
    assert source_path.exists()
'''


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate smoke tests for all discovered agents")
    parser.add_argument("--apply", action="store_true", help="Write generated tests to disk")
    args = parser.parse_args(argv)

    project_root = _find_project_root()
    agents = sorted(
        _discover_agents(project_root),
        key=lambda item: (
            LAYER_PRIORITY.index(item["layer"]) if item["layer"] in LAYER_PRIORITY else len(LAYER_PRIORITY),
            item["class_name"],
        ),
    )
    planned = []
    for agent in agents:
        test_file = _test_path(project_root, agent)
        if not test_file.exists():
            planned.append((agent, test_file))

    print("=" * 80)
    print("GENERATE ALL AGENT TESTS")
    print("=" * 80)
    print(f"Discovered agents: {len(agents)}")
    print(f"Missing tests: {len(planned)}")

    for agent, test_file in planned:
        print(
            f"  {'✅ generating' if args.apply else '📝 would generate'} {test_file.relative_to(project_root)}"
        )
        if args.apply:
            test_file.parent.mkdir(parents=True, exist_ok=True)
            test_file.write_text(_module_template(agent), encoding="utf-8")

    return 0


if __name__ == "__main__":
    sys.exit(main())
