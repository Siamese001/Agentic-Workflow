"""Find and optionally fix agents missing super().heal_repository() using AST analysis."""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

AGENT_DISCOVERY_JSON = "agent_discovery_full.json"


def _find_project_root() -> Path:
    current = Path(__file__).resolve().parent
    for candidate in (current, *current.parents):
        if (candidate / AGENT_DISCOVERY_JSON).exists():
            return candidate
        if (candidate / "l0_scripts").exists() and (candidate / "L0_routing_scripts").exists():
            return candidate
    return Path(__file__).resolve().parents[1]


def has_super_heal_call(func_node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    for node in ast.walk(func_node):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Attribute) or node.func.attr != "heal_repository":
            continue
        value = node.func.value
        if isinstance(value, ast.Call) and isinstance(value.func, ast.Name) and value.func.id == "super":
            return True
    return False


def check_invocation_status_dashboard(
    source: str,
) -> tuple[str, ast.FunctionDef | ast.AsyncFunctionDef | None]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return "Inherited", None

    heal_methods = [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "heal_repository"
    ]
    if not heal_methods:
        return "Inherited", None

    first_method = heal_methods[0]
    if has_super_heal_call(first_method):
        return "Yes", first_method
    return "No (missing super)", first_method


def is_method_in_class(func_node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    return bool(func_node.args.args) and func_node.args.args[0].arg == "self"


def find_insertion_point(
    func_node: ast.FunctionDef | ast.AsyncFunctionDef, lines: list[str]
) -> tuple[int, str]:
    if not func_node.body:
        return -1, ""
    first_stmt = func_node.body[0]
    is_docstring = (
        isinstance(first_stmt, ast.Expr)
        and isinstance(first_stmt.value, ast.Constant)
        and isinstance(first_stmt.value.value, str)
    )
    if is_docstring and len(func_node.body) > 1:
        insert_line = func_node.body[1].lineno - 1
    else:
        insert_line = first_stmt.lineno - 1
    ref_line = lines[insert_line]
    indent_str = " " * (len(ref_line) - len(ref_line.lstrip()))
    return insert_line, indent_str


def add_super_call(source: str) -> str:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return source

    heal_methods = [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "heal_repository"
    ]
    if not heal_methods:
        return source

    func_node = heal_methods[0]
    if has_super_heal_call(func_node) or not is_method_in_class(func_node):
        return source

    lines = source.splitlines()
    insert_line, indent_str = find_insertion_point(func_node, lines)
    if insert_line < 0:
        return source

    args = [arg.arg for arg in func_node.args.args if arg.arg != "self"]
    super_call = f"{indent_str}super().heal_repository({', '.join(args)})"
    lines.insert(insert_line, super_call)
    return "\n".join(lines) + ("\n" if source.endswith("\n") else "")


def _load_agents(project_root: Path) -> list[dict]:
    manifest_path = project_root / AGENT_DISCOVERY_JSON
    with manifest_path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError(f"Expected a list of agents in {manifest_path}")
    return data


def _resolve_agent_path(project_root: Path, agent: dict) -> Path | None:
    for key in ("path", "file_path"):
        value = agent.get(key)
        if value:
            return project_root / str(value)
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Find and optionally fix missing super().heal_repository() invocations"
    )
    parser.add_argument(
        "--apply", action="store_true", help="Write fixes to disk instead of running in report mode"
    )
    args = parser.parse_args(argv)

    try:
        project_root = _find_project_root()
        agents = _load_agents(project_root)
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"[missing-invocation] {exc}", file=sys.stderr)
        return 1

    status_counts = {"Yes": 0, "No (missing super)": 0, "Inherited": 0}
    missing_invocation: list[dict[str, str]] = []

    for agent in agents:
        path = _resolve_agent_path(project_root, agent)
        if path is None or not path.exists():
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            status, _ = check_invocation_status_dashboard(content)
            status_counts[status] = status_counts.get(status, 0) + 1
            if status == "No (missing super)":
                missing_invocation.append(
                    {"path": str(path), "rel_path": str(path.relative_to(project_root))}
                )
        except OSError as exc:
            print(f"[missing-invocation] unable to read {path}: {exc}", file=sys.stderr)

    print(f"Loaded {sum(status_counts.values())} agents from registry")
    print("\nInvocation status counts:")
    for status, count in status_counts.items():
        print(f"  {status}: {count}")

    total = sum(status_counts.values())
    invocation_pct = ((status_counts["Yes"] + status_counts["Inherited"]) / total * 100) if total else 0.0
    print(f"\nCurrent Invocation %: {invocation_pct:.1f}%")
    print(f"\n=== Agents needing fix ({len(missing_invocation)}) ===")
    for agent in sorted(missing_invocation, key=lambda item: item["rel_path"]):
        print(f"  {agent['rel_path']}")

    if not args.apply or not missing_invocation:
        return 0

    print(f"\n=== APPLYING FIXES ({len(missing_invocation)} files) ===")
    fixed_count = 0
    skipped_count = 0
    for agent in missing_invocation:
        path = Path(agent["path"])
        try:
            content = path.read_text(encoding="utf-8")
            new_content = add_super_call(content)
            if new_content == content:
                print(f"  ⊘ Skipped: {agent['rel_path']}")
                skipped_count += 1
                continue
            ast.parse(new_content)
            verify_status, _ = check_invocation_status_dashboard(new_content)
            if verify_status != "Yes":
                print(f"  ✗ Verification failed: {agent['rel_path']} ({verify_status})")
                continue
            path.write_text(new_content, encoding="utf-8")
            print(f"  ✓ Fixed: {agent['rel_path']}")
            fixed_count += 1
        except (OSError, SyntaxError, ValueError) as exc:
            print(f"  ✗ Error fixing {agent['rel_path']}: {exc}")

    print(f"\nFixed {fixed_count}/{len(missing_invocation)} files (skipped {skipped_count})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
