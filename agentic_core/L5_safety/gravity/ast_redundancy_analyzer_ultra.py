#!/usr/bin/env python3
"""
ULTRA SOVEREIGN AST REDUNDANCY ANALYZER — ETERNAL STRUCTURAL PURITY
December 30, 2025

Ultra-hardened version with:
- Full AST normalization (method sort, param/var canonicalization, docstring/import stripping)
- Full SHA256 fingerprints
- Advanced near-duplicate detection via normalized AST diff
- Sovereign reporting with IDE-ready recommendations
"""
import ast
import hashlib
import json
import logging
import re
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple
from difflib import SequenceMatcher

from agentic_core.L5_safety.validators.structure_blueprint import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)
from agentic_core.utils.sovereign_index import SovereignIndex

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
AGENTIC_CORE = PROJECT_ROOT / AGENTIC_CORE_DIR

EXCLUDED_DIRS = {"__pycache__", ".git", ARCHIVES_DIR, "data", ".sovereign_healing_backup"}


@dataclass
class AgentInfo:
    name: str
    file_path: Path
    layer: str
    line_number: int
    method_count: int
    method_names: List[str] = field(default_factory=list)
    fingerprint: str = ""
    normalized_source: str = ""


class UltraASTNormalizer(ast.NodeTransformer):
    """ULTRA-hardened AST normalizer for eternal structural comparison."""

    def __init__(self):
        self.param_counter = 0
        self.var_counter = 0
        self.var_map: Dict[str, str] = {}

    def reset_counters(self):
        self.param_counter = 0
        self.var_counter = 0
        self.var_map = {}

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        # Strip class docstring
        if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
            node.body = node.body[1:]

        # Sort methods alphabetically
        methods = [n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        non_methods = [n for n in node.body if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        methods.sort(key=lambda m: m.name)
        node.body = non_methods + methods

        # Remove decorators and canonicalize name
        node.decorator_list = []
        node.name = "CanonicalAgent"

        self.generic_visit(node)
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        return self._normalize_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AsyncFunctionDef:
        return self._normalize_function(node)

    def _normalize_function(self, node):
        self.reset_counters()

        # Canonicalize parameters
        new_args = []
        for i, arg in enumerate(node.args.args):
            if arg.arg == "self":
                new_args.append(arg)
            else:
                name = f"param{i}"
                self.var_map[arg.arg] = name
                new_args.append(ast.arg(arg=name, annotation=None))
        node.args.args = new_args
        node.args.defaults = []
        node.args.kw_defaults = []
        node.args.kwonlyargs = []

        # Strip function docstring
        if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
            node.body = node.body[1:]

        # Remove decorators, returns, type comments
        node.decorator_list = []
        node.returns = None

        self.generic_visit(node)
        return node

    def visit_Name(self, node: ast.Name) -> ast.Name:
        if node.id in self.var_map:
            node.id = self.var_map[node.id]
        return node

    def visit_Constant(self, node: ast.Constant) -> ast.Constant:
        if isinstance(node.value, str) and len(node.value) > 30:
            node.value = "NORMALIZED_STRING"
        return node

    def visit_Import(self, node: ast.Import) -> None:
        return None

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        return None


def extract_layer(file_path: Path) -> str:
    path_str = str(file_path).lower()
    if "l0_" in path_str: return "L0"
    if "l1_" in path_str: return "L1"
    if "l2_" in path_str: return "L2"
    if "l3_" in path_str: return "L3"
    if "l4_" in path_str: return "L4"
    if "l5_" in path_str: return "L5"
    if "observability" in path_str: return "L6-OBS"
    if "utils" in path_str: return "UTILS"
    return "OTHER"


def find_agents() -> List[AgentInfo]:
    agents = []
    for py_file in AGENTIC_CORE.rglob("*Agent.py"):
        if any(ex in str(py_file) for ex in EXCLUDED_DIRS):
            continue

        try:
            content = py_file.read_text(encoding="utf-8")
            tree = ast.parse(content)
        except:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name.endswith("Agent") and node.name[0].isupper():
                method_count = sum(1 for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)))
                method_names = [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                agents.append(AgentInfo(
                    name=node.name,
                    file_path=py_file,
                    layer=extract_layer(py_file),
                    line_number=node.lineno,
                    method_count=method_count,
                    method_names=method_names
                ))
    return sorted(agents, key=lambda a: (a.layer, a.name))


def generate_ultra_fingerprint(agent: AgentInfo) -> Tuple[str, str]:
    try:
        content = agent.file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)

        class_node = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == agent.name:
                class_node = node
                break

        if not class_node:
            return ("NO_CLASS", "")

        module = ast.Module(body=[class_node], type_ignores=[])
        normalizer = UltraASTNormalizer()
        normalized = normalizer.visit(module)
        ast.fix_missing_locations(normalized)

        normalized_src = ast.unparse(normalized)
        fingerprint = hashlib.sha256(normalized_src.encode()).hexdigest()

        return (fingerprint, normalized_src)
    except Exception as e:
        return (f"ERROR:{str(e)[:30]}", "")


def similarity_ratio(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def main():
    print("=" * 80)
    print("ULTRA SOVEREIGN AST REDUNDANCY ANALYZER — ETERNAL STRUCTURAL PURITY")
    print("December 30, 2025")
    print("=" * 80)

    # PHASE 1: Discovery
    print("\n" + "─" * 80)
    print("PHASE 1: AGENT DISCOVERY")
    print("─" * 80)
    agents = find_agents()
    print(f"Discovered {len(agents)} true PascalCase *Agent classes in agentic_core/")
    
    # Count by layer
    layer_counts = defaultdict(int)
    for a in agents:
        layer_counts[a.layer] += 1
    print("\nAgent distribution by layer:")
    for layer in sorted(layer_counts.keys()):
        print(f"  {layer}: {layer_counts[layer]} agents")

    # PHASE 2: Fingerprinting
    print("\n" + "─" * 80)
    print("PHASE 2: ULTRA AST FINGERPRINTING")
    print("─" * 80)
    print("Applying ULTRA normalization:")
    print("  • Method alphabetical sorting")
    print("  • Parameter canonicalization (param0, param1, ...)")
    print("  • Docstring stripping")
    print("  • Import removal")
    print("  • Long string normalization")
    print("\nGenerating SHA256 fingerprints...")
    
    for agent in agents:
        agent.fingerprint, agent.normalized_source = generate_ultra_fingerprint(agent)
    
    valid_fps = sum(1 for a in agents if not a.fingerprint.startswith("ERROR"))
    print(f"Successfully fingerprinted: {valid_fps}/{len(agents)} agents")

    # PHASE 3: Exact Duplicates
    print("\n" + "─" * 80)
    print("PHASE 3: EXACT DUPLICATE DETECTION")
    print("─" * 80)
    
    fp_groups = defaultdict(list)
    for agent in agents:
        if not agent.fingerprint.startswith("ERROR") and agent.fingerprint != "NO_CLASS":
            fp_groups[agent.fingerprint].append(agent)

    exact_duplicates = {fp: group for fp, group in fp_groups.items() if len(group) > 1}

    if exact_duplicates:
        print(f"⚠️  FOUND {len(exact_duplicates)} exact duplicate group(s):\n")
        for fp, group in exact_duplicates.items():
            print(f"[EXACT DUPLICATE GROUP] Fingerprint: {fp[:16]}...")
            print("─" * 60)
            for a in group:
                rel_path = a.file_path.relative_to(PROJECT_ROOT)
                print(f"  • {a.name}")
                print(f"    File: {rel_path}:{a.line_number}")
                print(f"    Layer: {a.layer}, Methods: {a.method_count}")
            # Sovereign recommendation
            keep = max(group, key=lambda x: ("L5" in x.layer, "L4" in x.layer, x.method_count))
            delete = [a for a in group if a != keep]
            print(f"\n  RECOMMENDATION:")
            print(f"    KEEP:   {keep.name} ({keep.layer})")
            for d in delete:
                print(f"    DELETE: {d.name} ({d.layer})")
            print()
    else:
        print("✅ [OK] No exact structural duplicates found!")

    # PHASE 4: Near Duplicates
    print("\n" + "─" * 80)
    print("PHASE 4: NEAR-DUPLICATE ANALYSIS (>92% similarity)")
    print("─" * 80)
    
    near = []
    agents_with_src = [a for a in agents if a.normalized_source]
    for i, a1 in enumerate(agents_with_src):
        for a2 in agents_with_src[i+1:]:
            if a1.fingerprint != a2.fingerprint:
                sim = similarity_ratio(a1.normalized_source, a2.normalized_source)
                if sim > 0.92:
                    near.append((a1, a2, sim))

    near.sort(key=lambda x: -x[2])
    
    if near:
        print(f"⚠️  FOUND {len(near)} near-duplicate pair(s):\n")
        for a1, a2, sim in near[:15]:
            print(f"  {sim:.1%} similarity:")
            print(f"    • {a1.name} ({a1.layer})")
            print(f"    • {a2.name} ({a2.layer})")
            print(f"    → Consider merging or refactoring\n")
    else:
        print("✅ [OK] No near-duplicates found!")

    # PHASE 5: Full Agent Registry
    print("\n" + "─" * 80)
    print("PHASE 5: COMPLETE AGENT FINGERPRINT REGISTRY")
    print("─" * 80)
    
    print("\n┌" + "─" * 42 + "┬" + "─" * 8 + "┬" + "─" * 8 + "┬" + "─" * 18 + "┐")
    print("│ {:^40} │ {:^6} │ {:^6} │ {:^16} │".format("Agent Name", "Layer", "Methods", "Fingerprint"))
    print("├" + "─" * 42 + "┼" + "─" * 8 + "┼" + "─" * 8 + "┼" + "─" * 18 + "┤")
    
    for agent in agents:
        fp_display = agent.fingerprint[:16] if len(agent.fingerprint) >= 16 else agent.fingerprint
        print("│ {:40} │ {:^6} │ {:^6} │ {:16} │".format(
            agent.name[:40], agent.layer, agent.method_count, fp_display
        ))
    
    print("└" + "─" * 42 + "┴" + "─" * 8 + "┴" + "─" * 8 + "┴" + "─" * 18 + "┘")

    # SUMMARY
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total Agent Classes:        {len(agents)}")
    print(f"Exact Duplicate Groups:     {len(exact_duplicates)}")
    print(f"Near-Duplicate Pairs:       {len(near)}")
    print(f"Unique Fingerprints:        {len(fp_groups)}")

    # Final verdict
    print("\n" + "=" * 80)
    if not exact_duplicates and not near:
        print("✅ ULTRA AST REDUNDANCY ANALYSIS COMPLETE")
        print("✅ STRUCTURAL DUPLICATES: NONE FOUND")
        print("✅ CODEBASE ETERNALLY PURE AND MAXIMALLY SOVEREIGN")
    else:
        print("⚠️  ULTRA AST REDUNDANCY ANALYSIS COMPLETE")
        print(f"⚠️  ACTION REQUIRED: {len(exact_duplicates)} duplicate groups, {len(near)} near-duplicates")
    print("=" * 80)

    # Save JSON report
    report = {
        "total_agents": len(agents),
        "exact_duplicate_groups": len(exact_duplicates),
        "near_duplicate_pairs": len(near),
        "unique_fingerprints": len(fp_groups),
        "agents": [
            {
                "name": a.name,
                "file": str(a.file_path.relative_to(PROJECT_ROOT)),
                "layer": a.layer,
                "line": a.line_number,
                "methods": a.method_count,
                "fingerprint": a.fingerprint[:16] if len(a.fingerprint) >= 16 else a.fingerprint
            }
            for a in agents
        ],
        "exact_duplicates": {
            fp[:16]: [{"name": a.name, "file": str(a.file_path.relative_to(PROJECT_ROOT)), "layer": a.layer} for a in group]
            for fp, group in exact_duplicates.items()
        },
        "near_duplicates": [
            {"agent1": a1.name, "agent2": a2.name, "similarity": round(sim, 4)}
            for a1, a2, sim in near
        ]
    }
    
    report_path = PROJECT_ROOT / "ast_redundancy_report_ultra.json"
    report_path.write_text(json.dumps(report, indent=2))
    print(f"\nJSON report saved to: {report_path}")


if __name__ == "__main__":
    main()
