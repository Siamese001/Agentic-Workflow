"""Build comprehensive agent inventory with AST-based metrics.

Produces artifacts/consolidation/agent_inventory.json
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]  # c:\Git\Agentic-Workflow
DISCOVERY_PATH = PROJECT_ROOT / "artifacts" / "consolidation" / "discovery_snapshot_before.json"
OUTPUT_PATH = PROJECT_ROOT / "artifacts" / "consolidation" / "agent_inventory.json"

# Boilerplate method names that don't count as domain logic
BOILERPLATE_METHODS = frozenset(
    {
        "__init__",
        "__post_init__",
        "__repr__",
        "__str__",
        "__eq__",
        "__hash__",
        "heal_repository",
        "heal",
        "can_run",
        "get_config",
        "get_name",
        "get_description",
        "to_dict",
        "from_dict",
        "validate",
    },
)

CAPABILITY_SUFFIXES = ("Capability", "Mixin", "Protocol")


def _resolve_agent_path(file_str: str) -> Path | None:
    normalized = file_str.replace("\\", "/")
    candidate = PROJECT_ROOT / normalized
    if candidate.exists():
        return candidate
    p = Path(file_str)
    if p.is_absolute() and p.exists():
        return p
    return None


def _get_layer(file_path: Path) -> str:
    rel = file_path.relative_to(PROJECT_ROOT).as_posix()
    for layer in [
        "L0_maintenance",
        "L1_cognition",
        "L2_execution",
        "L3_orchestration",
        "L4_knowledge",
        "L5_safety",
        "L6_observability",
    ]:
        if layer in rel:
            return layer.split("_")[0]
    if "apps_lic" in rel:
        return "apps_lic"
    if "apps_rg" in rel:
        return "apps_rg"
    if "apps_shared" in rel:
        return "apps_shared"
    return "unknown"


def _analyze_agent(file_path: Path) -> dict:
    source = file_path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return {"error": f"SyntaxError: {e.lineno}:{e.msg}"}

    total_loc = len([l for l in source.splitlines() if l.strip() and not l.strip().startswith("#")])

    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)

    internal_imports = [i for i in imports if i.startswith(("agentic_core", "apps_"))]

    agent_class = None
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef) and node.name.endswith("Agent"):
            agent_class = node
            break
    if not agent_class:
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                agent_class = node
                break

    if not agent_class:
        return {"total_loc": total_loc, "error": "no_class_found"}

    base_names: list[str] = []
    capability_mixins: list[str] = []
    base_classes: list[str] = []
    for base in agent_class.bases:
        name = ""
        if isinstance(base, ast.Name):
            name = base.id
        elif isinstance(base, ast.Attribute):
            name = base.attr
        if name:
            base_names.append(name)
            if any(name.endswith(s) for s in CAPABILITY_SUFFIXES):
                capability_mixins.append(name)
            else:
                base_classes.append(name)

    methods: list[str] = []
    domain_methods: list[str] = []
    boilerplate_loc = 0
    domain_loc = 0
    entrypoints: list[str] = []
    has_state = False

    for item in agent_class.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            methods.append(item.name)
            method_loc = (item.end_lineno or item.lineno) - item.lineno + 1

            if item.name in (
                "execute",
                "run",
                "process",
                "_process",
                "_validate",
                "collect_issues",
                "perform_checks",
                "run_inspection",
            ):
                entrypoints.append(item.name)

            # Check for super()-only methods (boilerplate wrappers)
            is_super_only = False
            for stmt in item.body:
                if isinstance(stmt, ast.Return) and isinstance(stmt.value, ast.Call):
                    func = stmt.value.func
                    if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Call):
                        if isinstance(func.value.func, ast.Name) and func.value.func.id == "super":
                            is_super_only = True

            if item.name in BOILERPLATE_METHODS or is_super_only:
                boilerplate_loc += method_loc
            else:
                domain_methods.append(item.name)
                domain_loc += method_loc

        elif isinstance(item, (ast.Assign, ast.AnnAssign)):
            has_state = True

    boilerplate_ratio = round(boilerplate_loc / max(total_loc, 1), 3)

    return {
        "class_name": agent_class.name,
        "layer": _get_layer(file_path),
        "file_path": file_path.relative_to(PROJECT_ROOT).as_posix(),
        "total_loc": total_loc,
        "domain_logic_loc": max(domain_loc, 0),
        "boilerplate_loc": boilerplate_loc,
        "boilerplate_ratio": boilerplate_ratio,
        "base_classes": base_classes,
        "capability_mixins": capability_mixins,
        "all_bases": base_names,
        "methods": methods,
        "domain_methods": domain_methods,
        "entrypoints": entrypoints,
        "stateful": has_state,
        "blast_radius": len(internal_imports),
        "internal_imports": internal_imports,
        "import_count": len(imports),
    }


def main() -> None:
    discovery = json.loads(DISCOVERY_PATH.read_text(encoding="utf-8-sig"))
    assert len(discovery) == 190, f"Expected 190 agents, got {len(discovery)}"

    inventory: list[dict] = []
    errors: list[str] = []

    for agent in discovery:
        file_str = agent.get("file", "")
        class_name = agent.get("class_name", "")
        file_path = _resolve_agent_path(file_str)

        if not file_path:
            errors.append(f"Cannot resolve: {file_str} ({class_name})")
            continue

        info = _analyze_agent(file_path)
        info["agent_id"] = agent.get("agent_id", class_name)
        info["discovery_class_name"] = class_name
        if "class_name" not in info:
            info["class_name"] = class_name
        if "file_path" not in info:
            info["file_path"] = file_str
        if "layer" not in info:
            info["layer"] = _get_layer(file_path)

        inventory.append(info)

    inventory.sort(key=lambda x: (x.get("layer", ""), x.get("class_name", "")))

    result = {
        "total_agents": len(inventory),
        "errors": errors,
        "error_count": len(errors),
        "summary": {
            "by_layer": {},
            "high_boilerplate": [],
            "low_domain_loc": [],
            "high_blast_radius": [],
        },
        "agents": inventory,
    }

    layer_counts: dict[str, int] = {}
    for a in inventory:
        layer = a.get("layer", "unknown")
        layer_counts[layer] = layer_counts.get(layer, 0) + 1
        if a.get("boilerplate_ratio", 0) > 0.7:
            result["summary"]["high_boilerplate"].append(a.get("class_name", ""))
        if a.get("domain_logic_loc", 999) < 5:
            result["summary"]["low_domain_loc"].append(a.get("class_name", ""))
        if a.get("blast_radius", 0) >= 20:
            result["summary"]["high_blast_radius"].append(a.get("class_name", ""))

    result["summary"]["by_layer"] = dict(sorted(layer_counts.items()))

    OUTPUT_PATH.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Inventory: {len(inventory)} agents")
    print(f"Errors: {len(errors)}")
    print(f"High boilerplate (>70%): {len(result['summary']['high_boilerplate'])}")
    print(f"Low domain LOC (<5): {len(result['summary']['low_domain_loc'])}")
    print(f"High blast radius (>=20): {len(result['summary']['high_blast_radius'])}")
    print(f"By layer: {result['summary']['by_layer']}")


if __name__ == "__main__":
    main()
