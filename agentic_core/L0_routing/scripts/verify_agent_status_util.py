"""
Verify Agent Status - AST Analysis for Suspect Files

This script audits files suspected of being misclassified as Sovereign Agents.
For each file, it determines:
1. Inheritance: Does it inherit from SovereignBaseAgent or a Layer Base?
2. Methods: Does it implement heal_repository?
3. Nomenclature: Does the class name end in 'Agent'?

Usage: python scripts/verify_agent_status_util.py
"""

import ast
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Suspect files to audit
SUSPECT_FILES = [
    "agentic_core/L0_routing/scripts/full_agent_discovery.py",
    "agentic_core/L0_routing/scripts/auto_remediate_signatures.py",
    "agentic_core/L2_execution/pinecone_mcp_client.py",
    "agentic_core/L2_execution/caching_redis_mcp_client.py",
    "agentic_core/L5_safety/ArchivalGatekeeper.py",
    "agentic_core/L5_safety/validators/context.py",
    "agentic_core/L5_safety/validators/constants.py",
    "agentic_core/L6_observability/reasoning_utils.py",
    "agentic_core/utils/core_extensions/infrastructure_mixin.py",
    "agentic_core/utils/core_extensions/healer_mixin.py",
]

# Known Sovereign base classes
SOVEREIGN_BASES = {
    "SovereignBaseAgent",
    "L0MaintenanceBaseAgent",
    "L1CognitionBase",
    "L2ExecutionBase",
    "L3OrchestrationBase",
    "L4StateBase",
    "L5SafetyBase",
    "L6ObservabilityBase",
}

# Layer bases (broader set)
LAYER_BASES = SOVEREIGN_BASES | {
    "HealerMixin",
    "MCPHardenedMixin",
    "CanonBaseAgent",
    "CognitionCanonBaseAgent",
    "ExecutionCanonBaseAgent",
}


def extract_bases(class_node: ast.ClassDef) -> set[str]:
    """Extract base class names from class definition."""
    bases = set()
    for base in class_node.bases:
        if isinstance(base, ast.Name):
            bases.add(base.id)
        elif isinstance(base, ast.Attribute):
            bases.add(base.attr)
        elif isinstance(base, ast.Subscript):
            if isinstance(base.value, ast.Name):
                bases.add(base.value.id)
    return bases


def has_method(class_node: ast.ClassDef, method_name: str) -> bool:
    """Check if class has a specific method."""
    for item in class_node.body:
        if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
            if item.name == method_name:
                return True
    return False


def analyze_file(file_path: Path) -> dict[str, Any]:
    """Analyze a Python file for agent characteristics."""
    result = {
        "file": str(file_path.relative_to(PROJECT_ROOT)),
        "exists": file_path.exists(),
        "is_script": False,
        "classes": [],
        "verdict": "UNKNOWN",
        "reason": "",
    }

    if not file_path.exists():
        result["verdict"] = "NOT_FOUND"
        result["reason"] = "File does not exist"
        return result

    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except SyntaxError as e:
        result["verdict"] = "PARSE_ERROR"
        result["reason"] = f"Syntax error: {e}"
        return result

    # Find all class definitions
    classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

    if not classes:
        result["is_script"] = True
        result["verdict"] = "NOT_AGENT"
        result["reason"] = "Script file - no class definitions"
        return result

    for cls in classes:
        bases = extract_bases(cls)
        class_info = {
            "name": cls.name,
            "ends_with_agent": cls.name.endswith("Agent"),
            "bases": list(bases),
            "inherits_sovereign": bool(bases & SOVEREIGN_BASES),
            "inherits_layer_base": bool(bases & LAYER_BASES),
            "has_heal_repository": has_method(cls, "heal_repository"),
            "is_mixin": "Mixin" in cls.name,
            "is_dataclass": any(
                (isinstance(d, ast.Name) and d.id == "dataclass")
                or (isinstance(d, ast.Call) and isinstance(d.func, ast.Name) and d.func.id == "dataclass")
                for d in cls.decorator_list
            ),
        }

        # Determine if this class is a sovereign agent
        is_sovereign = (
            class_info["ends_with_agent"]
            and (class_info["inherits_sovereign"] or class_info["inherits_layer_base"])
            and not class_info["is_mixin"]
        )
        class_info["is_sovereign_agent"] = is_sovereign

        result["classes"].append(class_info)

    # Determine overall verdict
    sovereign_classes = [c for c in result["classes"] if c["is_sovereign_agent"]]
    mixin_classes = [c for c in result["classes"] if c["is_mixin"]]

    if sovereign_classes:
        result["verdict"] = "SOVEREIGN_AGENT"
        result["reason"] = f"Contains sovereign agent class(es): {[c['name'] for c in sovereign_classes]}"
    elif mixin_classes:
        result["verdict"] = "MIXIN"
        result["reason"] = f"Contains mixin class(es): {[c['name'] for c in mixin_classes]}"
    elif any(c["ends_with_agent"] for c in result["classes"]):
        # Has Agent suffix but doesn't inherit from sovereign bases
        agent_classes = [c for c in result["classes"] if c["ends_with_agent"]]
        result["verdict"] = "PSEUDO_AGENT"
        result["reason"] = (
            f"Has Agent suffix but no sovereign inheritance: {[c['name'] for c in agent_classes]}"
        )
    else:
        result["verdict"] = "NOT_AGENT"
        non_agent_classes = [c["name"] for c in result["classes"]]
        result["reason"] = f"Infrastructure/utility classes: {non_agent_classes}"

    return result


def print_report(results: list[dict]) -> None:
    """Print formatted verification report."""
    print("=" * 100)
    print("AGENT STATUS VERIFICATION REPORT")
    print("=" * 100)
    print()

    # Summary counts
    verdicts = {}
    for r in results:
        v = r["verdict"]
        verdicts[v] = verdicts.get(v, 0) + 1

    print("SUMMARY:")
    for verdict, count in sorted(verdicts.items()):
        print(f"  {verdict}: {count}")
    print()

    # Detailed results
    print("-" * 100)
    print("DETAILED ANALYSIS:")
    print("-" * 100)

    for r in results:
        print()
        print(f"FILE: {r['file']}")
        print(f"  Verdict: {r['verdict']}")
        print(f"  Reason: {r['reason']}")

        if r["classes"]:
            print(f"  Classes found: {len(r['classes'])}")
            for cls in r["classes"]:
                print(f"    - {cls['name']}:")
                print(f"        Ends with 'Agent': {cls['ends_with_agent']}")
                print(f"        Inherits Sovereign Base: {cls['inherits_sovereign']}")
                print(f"        Inherits Layer Base: {cls['inherits_layer_base']}")
                print(f"        Has heal_repository(): {cls['has_heal_repository']}")
                print(f"        Is Mixin: {cls['is_mixin']}")
                print(f"        Bases: {cls['bases']}")
                print(f"        => IS SOVEREIGN AGENT: {cls['is_sovereign_agent']}")

    print()
    print("=" * 100)
    print("EXCLUSION RECOMMENDATIONS:")
    print("=" * 100)

    to_exclude = [r for r in results if r["verdict"] in ("NOT_AGENT", "MIXIN", "PSEUDO_AGENT")]
    if to_exclude:
        print("\nThe following files should be EXCLUDED from agent discovery:")
        for r in to_exclude:
            print(f"  - {r['file']}")
            print(f"    Reason: {r['reason']}")
    else:
        print("\nNo files recommended for exclusion.")

    print()


def main():
    print("Scanning suspect files for agent characteristics...")
    print()

    results = []
    for rel_path in SUSPECT_FILES:
        file_path = PROJECT_ROOT / rel_path
        result = analyze_file(file_path)
        results.append(result)

    print_report(results)

    # Return exit code based on findings
    non_agents = [r for r in results if r["verdict"] in ("NOT_AGENT", "MIXIN", "PSEUDO_AGENT")]
    print(f"\nTotal suspects analyzed: {len(results)}")
    print(f"Confirmed non-agents: {len(non_agents)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
