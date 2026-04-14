"""Generate smoke-test stubs for a prioritized subset of discovered agent classes."""

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
    rel_source_path = agent["path"]
    class_name = agent["class_name"]
    return f'''"""Auto-generated smoke tests for {class_name}."""

from __future__ import annotations

import importlib.util
from pathlib import Path

SOURCE_PATH = Path(__file__).resolve().parents[2] / "{rel_source_path}"
CLASS_NAME = "{class_name}"


def _load_class():
    spec = importlib.util.spec_from_file_location(SOURCE_PATH.stem, SOURCE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {{SOURCE_PATH}}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, CLASS_NAME)


def test_source_file_exists():
    assert SOURCE_PATH.exists()


def test_class_is_defined():
    cls = _load_class()
    assert cls.__name__ == CLASS_NAME
'''


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate smoke tests for a prioritized subset of discovered agents"
    )
    parser.add_argument("--apply", action="store_true", help="Write generated tests to disk")
    parser.add_argument("--max-per-layer", type=int, default=10, help="Maximum tests to generate per layer")
    args = parser.parse_args(argv)

    project_root = _find_project_root()
    agents = _discover_agents(project_root)
    total_generated = 0

    print("=" * 70)
    print("AGENT TEST GENERATION")
    print("=" * 70)
    print(f"Total discovered agents: {len(agents)}")

    for layer in LAYER_PRIORITY:
        layer_agents = [agent for agent in agents if agent["layer"] == layer]
        if not layer_agents:
            continue
        generated_here = 0
        print(f"\nGenerating tests for {layer} layer ({len(layer_agents)} agents)")
        for agent in layer_agents:
            if generated_here >= max(args.max_per_layer, 0):
                break
            test_file = _test_path(project_root, agent)
            if test_file.exists():
                print(f"  ⏭️  {agent['class_name']}: test already exists")
                continue
            generated_here += 1
            total_generated += 1
            print(
                f"  {'✅ generating' if args.apply else '📝 would generate'} {test_file.relative_to(project_root)}"
            )
            if args.apply:
                test_file.parent.mkdir(parents=True, exist_ok=True)
                test_file.write_text(_module_template(agent), encoding="utf-8")
        if len(layer_agents) > args.max_per_layer:
            print(f"  ... {len(layer_agents) - args.max_per_layer} more agents in {layer}")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total tests {'generated' if args.apply else 'planned'}: {total_generated}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
