"""Analyze the top five complex agents using a direct AST-based complexity breakdown."""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

DEFAULT_MANIFEST = "agent_discovery_full.json"


def _find_project_root() -> Path:
    current = Path(__file__).resolve().parent
    for candidate in (current, *current.parents):
        if (candidate / DEFAULT_MANIFEST).exists():
            return candidate
        if (candidate / "l0_scripts").exists() and (candidate / "L0_routing_scripts").exists():
            return candidate
    return Path(__file__).resolve().parents[1]


def calculate_method_cc(node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    cc = 1
    for child in ast.walk(node):
        if isinstance(
            child, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.ExceptHandler, ast.IfExp, ast.Match)
        ):
            cc += 1
        elif isinstance(child, ast.BoolOp):
            cc += max(0, len(child.values) - 1)
        elif isinstance(child, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
            cc += 1
    return cc


def analyze_method_complexity(file_path: Path) -> list[tuple[str, int]]:
    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(file_path))
    except (OSError, SyntaxError) as exc:
        print(f"[complexity] unable to analyze {file_path}: {exc}", file=sys.stderr)
        return []

    method_complexities: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    method_complexities.append((f"{node.name}.{item.name}", calculate_method_cc(item)))
    return sorted(method_complexities, key=lambda item: item[1], reverse=True)


def _load_agents(project_root: Path, manifest_name: str) -> list[dict]:
    manifest_path = project_root / manifest_name
    with manifest_path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError(f"Expected a list of agents in {manifest_path}")
    return data


def _resolve_relative_path(agent: dict) -> str:
    for key in ("file_path", "path"):
        value = agent.get(key)
        if value:
            return str(value)
    return ""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Report method-level complexity for the top N agents")
    parser.add_argument("--limit", type=int, default=5, help="Number of top agents to inspect")
    parser.add_argument(
        "--manifest", default=DEFAULT_MANIFEST, help="Manifest filename relative to the project root"
    )
    args = parser.parse_args(argv)

    try:
        project_root = _find_project_root()
        agents = _load_agents(project_root, args.manifest)
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"[complexity] {exc}", file=sys.stderr)
        return 1

    agents_sorted = sorted(
        agents, key=lambda item: int(item.get("cyclomatic_complexity", 0) or 0), reverse=True
    )
    print("=" * 80)
    print(f"TOP {args.limit} AGENTS BY COMPLEXITY - METHOD BREAKDOWN")
    print("=" * 80)
    for index, agent in enumerate(agents_sorted[: max(args.limit, 0)], start=1):
        name = agent.get("class_name", "Unknown")
        cc = int(agent.get("cyclomatic_complexity", 0) or 0)
        rel_path = _resolve_relative_path(agent)
        print(f"\n{index}. {name} (Total CC={cc})")
        print(f"   File: {rel_path or '<missing>'}")
        if not rel_path:
            continue
        file_path = project_root / rel_path
        if not file_path.exists():
            print(f"   [!] File not found: {file_path}")
            continue
        method_ccs = analyze_method_complexity(file_path)
        if not method_ccs:
            print("   [!] No class methods found or file could not be analyzed")
            continue
        print("\n   Top 10 most complex methods:")
        for method_name, method_cc in method_ccs[:10]:
            print(f"      {method_name}: CC={method_cc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
