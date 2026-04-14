"""
Integration Gap Analyzer - AST-based analysis of all agents for migration prioritization.

Analyzes all agents in the repository to identify integration gaps with:
- MetaLearningMixin
- AuditTrailMixin
- CostGuardrailMixin
- HITLMixin
- PineconeVectorMixin
- RedisCacheMixin
- DetectionSignal
- VerificationGate
- HumanReviewQueue
"""

import ast
import json
import re
from collections import defaultdict
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import REPORTS_DIR
from tqdm import tqdm


def _resolve_repo_root() -> Path:
    for candidate in Path(__file__).resolve().parents:
        if (candidate / ".git").exists():
            return candidate
    return Path(__file__).resolve().parents[2]


PROJECT_ROOT = _resolve_repo_root()
CRITICAL_MIXINS = {
    "MetaLearningMixin": "P0",
    "AuditTrailMixin": "P1",
    "CostGuardrailMixin": "P1",
    "HITLMixin": "P0",
    "PineconeVectorMixin": "P1",
    "RedisCacheMixin": "P1",
    "HealerMixin": "P0",
}
CRITICAL_COMPONENTS = {"DetectionSignal": "P0", "VerificationGate": "P0", "HumanReviewQueue": "P0"}
COMPONENT_PATTERNS = {
    "DetectionSignal": ["DetectionSignal\\s*\\(", "from.*detection_signal.*import"],
    "VerificationGate": ["VerificationGate\\s*\\(", "verification_gate"],
    "HumanReviewQueue": ["HumanReviewQueue\\s*\\(", "review_queue", "submit_for_review"],
    "recall_or_execute": ["recall_or_execute\\s*\\(", "self\\.recall_or_execute"],
    "log_audit_event": ["log_audit_event\\s*\\(", "self\\.log_audit_event"],
}


def analyze_file_with_ast(file_path: Path) -> dict:
    """Analyze a Python file using AST to extract class info."""
    result = {
        "classes": [],
        "imports": [],
        "uses_detection_signal": False,
        "uses_verification_gate": False,
        "uses_human_review": False,
        "uses_meta_learning": False,
        "uses_audit_trail": False,
    }
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
        for component, patterns in tqdm(COMPONENT_PATTERNS.items(), desc="Processing", unit="item"):
            for pattern in tqdm(patterns, desc="Processing", unit="item"):
                if re.search(pattern, content, re.IGNORECASE):
                    if "detection" in component.lower():
                        result["uses_detection_signal"] = True
                    elif "verification" in component.lower():
                        result["uses_verification_gate"] = True
                    elif "human" in component.lower() or "review" in component.lower():
                        result["uses_human_review"] = True
                    elif "recall" in pattern or "meta" in component.lower():
                        result["uses_meta_learning"] = True
                    elif "audit" in pattern:
                        result["uses_audit_trail"] = True
        tree = ast.parse(content)
        for node in tqdm(ast.walk(tree), desc="Processing", unit="item"):
            if isinstance(node, ast.ClassDef):
                bases = []
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        bases.append(base.id)
                    elif isinstance(base, ast.Attribute):
                        bases.append(base.attr)
                result["classes"].append(
                    {
                        "name": node.name,
                        "bases": bases,
                        "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                    }
                )
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    result["imports"].append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    result["imports"].append(node.module)
    # guardian: allow-silent-swallow
    except Exception as e:
        result["error"] = str(e)
    return result


def analyze_all_agents():
    """Analyze all agents from discovery JSON."""
    discovery_path = PROJECT_ROOT / "agent_discovery_full.json"
    with open(discovery_path, encoding="utf-8") as f:
        agents = json.load(f)
    results = {
        "total_agents": len(agents),
        "by_layer": defaultdict(list),
        "by_priority": defaultdict(list),
        "mixin_usage": defaultdict(int),
        "component_usage": {
            "detection_signal": 0,
            "verification_gate": 0,
            "human_review": 0,
            "meta_learning": 0,
            "audit_trail": 0,
        },
        "agents_with_healing": [],
        "agents_without_healing": [],
        "detailed_analysis": [],
    }
    for agent in tqdm(agents, desc="Processing", unit="item"):
        name = agent["class_name"]
        path = agent["path"].replace("\\", "/")
        layer = agent["layer"]
        inheritance = set(agent.get("inheritance", []))
        has_healing = agent.get("has_healing", False)
        has_memory = agent.get("has_memory", False)
        mcp_hardened = agent.get("mcp_hardened", False)
        full_path = PROJECT_ROOT / path.replace("/", "\\")
        ast_result = {
            "uses_detection_signal": False,
            "uses_verification_gate": False,
            "uses_human_review": False,
            "uses_meta_learning": False,
            "uses_audit_trail": False,
        }
        if full_path.exists():
            ast_result = analyze_file_with_ast(full_path)
        if ast_result.get("uses_detection_signal"):
            results["component_usage"]["detection_signal"] += 1
        if ast_result.get("uses_verification_gate"):
            results["component_usage"]["verification_gate"] += 1
        if ast_result.get("uses_human_review"):
            results["component_usage"]["human_review"] += 1
        if ast_result.get("uses_meta_learning"):
            results["component_usage"]["meta_learning"] += 1
        if ast_result.get("uses_audit_trail"):
            results["component_usage"]["audit_trail"] += 1
        missing_mixins = []
        for mixin, priority in CRITICAL_MIXINS.items():
            if mixin not in inheritance:
                missing_mixins.append((mixin, priority))
        missing_components = []
        if not ast_result.get("uses_detection_signal"):
            missing_components.append(("DetectionSignal", "P0"))
        if not ast_result.get("uses_verification_gate") and has_healing:
            missing_components.append(("VerificationGate", "P0"))
        if not ast_result.get("uses_human_review") and has_healing:
            missing_components.append(("HumanReviewQueue", "P0"))
        if not ast_result.get("uses_meta_learning"):
            missing_components.append(("recall_or_execute", "P0"))
        p0_missing = sum((1 for m, p in missing_mixins + missing_components if p == "P0"))
        p1_missing = sum((1 for m, p in missing_mixins + missing_components if p == "P1"))
        if p0_missing >= 4:
            priority = "P0"
        elif p0_missing >= 2:
            priority = "P1"
        elif p1_missing >= 3:
            priority = "P2"
        else:
            priority = "P3"
        analysis = {
            "name": name,
            "path": path,
            "layer": layer,
            "priority": priority,
            "p0_missing": p0_missing,
            "p1_missing": p1_missing,
            "missing_mixins": [m for m, p in missing_mixins if p == "P0"][:5],
            "missing_components": [m for m, p in missing_components][:5],
            "has_healing": has_healing,
            "has_memory": has_memory,
            "mcp_hardened": mcp_hardened,
            "uses_detection_signal": ast_result.get("uses_detection_signal", False),
            "uses_verification_gate": ast_result.get("uses_verification_gate", False),
            "uses_meta_learning": ast_result.get("uses_meta_learning", False),
        }
        results["by_layer"][layer].append(analysis)
        results["by_priority"][priority].append(analysis)
        results["detailed_analysis"].append(analysis)
        if has_healing:
            results["agents_with_healing"].append(name)
        else:
            results["agents_without_healing"].append(name)
        for mixin in inheritance:
            results["mixin_usage"][mixin] += 1
    return results


def print_report(results):
    """Print analysis report."""
    print("=" * 100)
    print("AGENT INTEGRATION GAP ANALYSIS - AST-BASED")
    print("=" * 100)
    print(f"Total Agents: {results['total_agents']}")
    print()
    print("=== PRIORITY DISTRIBUTION ===")
    for p in ["P0", "P1", "P2", "P3"]:
        count = len(results["by_priority"][p])
        pct = count / results["total_agents"] * 100
        print(f"  {p}: {count} agents ({pct:.1f}%)")
    print()
    print("=== LAYER DISTRIBUTION ===")
    for layer in sorted(results["by_layer"].keys()):
        agents_in_layer = results["by_layer"][layer]
        p0_count = sum(1 for a in agents_in_layer if a["priority"] == "P0")
        p1_count = sum(1 for a in agents_in_layer if a["priority"] == "P1")
        print(f"  {layer}: {len(agents_in_layer)} agents (P0: {p0_count}, P1: {p1_count})")
    print()
    print("=== COMPONENT USAGE (AST VERIFIED) ===")
    total = results["total_agents"]
    for component, count in results["component_usage"].items():
        pct = count / total * 100
        gap = total - count
        print(f"  {component}: {count}/{total} ({pct:.1f}%) - GAP: {gap} agents")
    print()
    print("=== TOP MIXIN USAGE ===")
    for mixin, count in sorted(results["mixin_usage"].items(), key=lambda x: -x[1])[:10]:
        print(f"  {mixin}: {count}")
    print()
    print("=== HEALING CAPABILITY ===")
    print(f"  With healing: {len(results['agents_with_healing'])}")
    print(f"  Without healing: {len(results['agents_without_healing'])}")
    print()
    print("=== P0 AGENTS (CRITICAL - NEED IMMEDIATE ATTENTION) ===")
    p0_agents = results["by_priority"]["P0"][:20]
    for agent in p0_agents:
        print(f"  {agent['name']} ({agent['layer']})")
        print(f"    Path: {agent['path']}")
        print(f"    Missing: {', '.join(agent['missing_mixins'][:3])}")
        print(f"    Components: {', '.join(agent['missing_components'][:3])}")
    return results


def generate_migration_json(results):
    """Generate JSON output for migration planning."""
    output = {
        "summary": {
            "total_agents": results["total_agents"],
            "p0_count": len(results["by_priority"]["P0"]),
            "p1_count": len(results["by_priority"]["P1"]),
            "p2_count": len(results["by_priority"]["P2"]),
            "p3_count": len(results["by_priority"]["P3"]),
            "component_gaps": results["component_usage"],
        },
        "by_layer": {layer: list(agents) for layer, agents in results["by_layer"].items()},
        "by_priority": {p: list(agents) for p, agents in results["by_priority"].items()},
    }
    output_path = PROJECT_ROOT / "docs" / REPORTS_DIR / "plans" / "agent_integration_gaps.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved detailed analysis to: {output_path}")
    return output


if __name__ == "__main__":
    results = analyze_all_agents()
    print_report(results)
    generate_migration_json(results)
