from pathlib import Path

from agentic_core.L2_execution.utils import write_gateway as _wg

REPO_ROOT = Path(__file__).resolve().parents[3]

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_signs_execution_trace,
)

"\nAST REDUNDANCY ANALYZER - Sovereign Structural Deduplication\nDecember 30, 2025\n\nPerforms comprehensive AST-based fingerprinting to detect:\n1. Exact structural duplicates (identical normalized AST)\n2. Near-duplicates (>90% structural similarity)\n"
import ast
import hashlib
import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
)
from tqdm import tqdm


@dataclass
class AgentInfo:
    """Information about a discovered agent class."""

    name: str
    file_path: str
    layer: str
    line_number: int
    method_count: int
    fingerprint: str = ""
    normalized_ast: str = ""
    method_names: list[str] = field(default_factory=list)


class ASTNormalizer(ast.NodeTransformer):
    """
    Enhanced AST Normalizer for structural fingerprinting.

    Performs:
    - Method alphabetical sorting
    - Parameter/local variable canonicalization (param1, var1)
    - Docstring stripping
    - Long constant replacement
    - Import removal
    - Decorator normalization
    """

    def __init__(self):
        self.param_counter = 0
        self.var_counter = 0
        self.var_map: dict[str, str] = {}

    def reset(self):
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "ASTNormalizer.reset")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ASTNormalizer.reset".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        self.param_counter = 0
        self.var_counter = 0
        self.var_map = {}

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        """Normalize class: sort methods, strip docstrings."""
        new_body = []
        for item in node.body:
            if isinstance(item, ast.Expr) and isinstance(item.value, ast.Constant):
                if isinstance(item.value.value, str):
                    continue
            new_body.append(item)
        methods = [n for n in new_body if isinstance(n, ast.FunctionDef | ast.AsyncFunctionDef)]
        non_methods = [n for n in new_body if not isinstance(n, ast.FunctionDef | ast.AsyncFunctionDef)]
        methods.sort(key=lambda m: m.name)
        node.body = non_methods + methods
        node.decorator_list = []
        node.name = "NormalizedAgent"
        return self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """Normalize function: canonicalize params, strip docstrings."""
        self.reset()
        new_args = []
        for i, arg in enumerate(node.args.args):
            if arg.arg == "self":
                new_args.append(arg)
            else:
                canonical_name = f"param{i}"
                self.var_map[arg.arg] = canonical_name
                new_arg = ast.arg(arg=canonical_name, annotation=None)
                new_args.append(new_arg)
        node.args.args = new_args
        node.args.defaults = []
        node.args.kw_defaults = []
        node.args.kwonlyargs = []
        new_body = []
        for item in node.body:
            if isinstance(item, ast.Expr) and isinstance(item.value, ast.Constant):
                if isinstance(item.value.value, str):
                    continue
            new_body.append(item)
        node.body = new_body if new_body else [ast.Pass()]
        node.decorator_list = []
        node.returns = None
        return self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AsyncFunctionDef:
        """Same normalization for async functions."""
        self.reset()
        new_args = []
        for i, arg in enumerate(node.args.args):
            if arg.arg == "self":
                new_args.append(arg)
            else:
                canonical_name = f"param{i}"
                self.var_map[arg.arg] = canonical_name
                new_arg = ast.arg(arg=canonical_name, annotation=None)
                new_args.append(new_arg)
        node.args.args = new_args
        node.args.defaults = []
        node.args.kw_defaults = []
        node.args.kwonlyargs = []
        new_body = []
        for item in node.body:
            if isinstance(item, ast.Expr) and isinstance(item.value, ast.Constant):
                if isinstance(item.value.value, str):
                    continue
            new_body.append(item)
        node.body = new_body if new_body else [ast.Pass()]
        node.decorator_list = []
        node.returns = None
        return self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> ast.Name:
        """Canonicalize variable names."""
        if node.id in self.var_map:
            node.id = self.var_map[node.id]
        return node

    def visit_Constant(self, node: ast.Constant) -> ast.Constant:
        """Replace long constants."""
        if isinstance(node.value, str) and len(node.value) > 50:
            node.value = "LONG_STRING"
        elif isinstance(node.value, int | float) and abs(node.value) > 1000000:
            node.value = 999999
        return node

    def visit_Import(self, node: ast.Import) -> ast.Import | None:
        """Remove imports."""
        return None

    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.ImportFrom | None:
        """Remove imports."""
        return None


def extract_layer(file_path: str) -> str:
    """Extract layer designation from file path."""
    path_lower = file_path.lower()
    if "/l0_" in path_lower or "\\l0_" in path_lower:
        return "L0"
    elif "/l1_" in path_lower or "\\l1_" in path_lower:
        return "L1"
    elif "/l2_" in path_lower or "\\l2_" in path_lower:
        return "L2"
    elif "/l3_" in path_lower or "\\l3_" in path_lower:
        return "L3"
    elif "/l4_" in path_lower or "\\l4_" in path_lower:
        return "L4"
    elif "/l5_" in path_lower or "\\l5_" in path_lower:
        return "L5"
    elif "/observability/" in path_lower or "\\observability\\" in path_lower:
        return "OBS"
    elif "/utils/" in path_lower or "\\utils\\" in path_lower:
        return "UTIL"
    return "UNKNOWN"


def find_agent_classes(base_path: str) -> list[AgentInfo]:
    """Find all PascalCase *Agent classes in the codebase."""
    agents = []
    base = Path(base_path)
    agent_pattern = re.compile("^class\\s+([A-Z][a-zA-Z0-9]*Agent)\\s*[\\(:]", re.MULTILINE)
    not_agent_pattern = re.compile("#\\s*NOT_AN_AGENT")
    search_paths = [base]
    apps_rg = base.parent / APPS_RG_DIR
    apps_lic = base.parent / APPS_LIC_DIR
    apps_shared = base.parent / APPS_SHARED_DIR
    if apps_rg.exists():
        search_paths.append(apps_rg)
    if apps_lic.exists():
        search_paths.append(apps_lic)
    if apps_shared.exists():
        search_paths.append(apps_shared)
    for search_base in tqdm(search_paths, desc="Processing", unit="item"):
        from agentic_core.utils.runners.ssot_discovery_validator import get_python_files

        for py_file in tqdm(get_python_files(search_base), desc="Processing", unit="item"):
            if ".venv" in str(py_file):
                continue
            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                if not_agent_pattern.search(content):
                    continue
                matches = agent_pattern.finditer(content)
                for match in tqdm(matches, desc="Processing", unit="item"):
                    class_name = match.group(1)
                    line_number = content[: match.start()].count("\n") + 1
                    try:
                        tree = ast.parse(content)
                        method_count = 0
                        method_names = []
                        for node in ast.walk(tree):
                            if isinstance(node, ast.ClassDef) and node.name == class_name:
                                for item in node.body:
                                    if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                                        method_count += 1
                                        method_names.append(item.name)
                        agents.append(
                            AgentInfo(  # review: Syntax errors should be caught at parser level, not runtime
                                name=class_name,
                                file_path=str(py_file),
                                layer=extract_layer(str(py_file)),
                                line_number=line_number,
                                method_count=method_count,
                                method_names=method_names,
                            ),
                        )
                    except SyntaxError:  # review: Syntax errors should be caught at parser level, not runtime
                        agents.append(
                            AgentInfo(
                                name=class_name,
                                file_path=str(py_file),
                                layer=extract_layer(str(py_file)),
                                line_number=line_number,
                                method_count=0,
                                method_names=[],
                            ),
                        )
            except (RuntimeError, OSError) as e:  # guardian: allow-silent-swallow
                print(f"Error reading {py_file}: {e}")
    return agents


def generate_fingerprint(file_path: str, class_name: str) -> tuple[str, str]:
    """Generate SHA256 fingerprint for a class using normalized AST."""
    try:
        content = Path(file_path).read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(content)
        target_class = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                target_class = node
                break
        if not target_class:
            return ("NO_CLASS_FOUND", "")
        module = ast.Module(body=[target_class], type_ignores=[])
        normalizer = ASTNormalizer()
        normalized = normalizer.visit(
            module
        )  # review: Syntax errors should be caught at parser level, not runtime
        ast.fix_missing_locations(normalized)
        try:
            normalized_code = ast.unparse(normalized)
        except (ValueError, TypeError, RuntimeError) as e:
            raise
        fingerprint = hashlib.sha256(normalized_code.encode()).hexdigest()[:16]
        return (fingerprint, normalized_code)
    except SyntaxError as e:  # review: Syntax errors should be caught at parser level, not runtime
        return ("SYNTAX_ERROR", str(e))
    except (RuntimeError, OSError) as e:  # guardian: allow-silent-swallow
        return ("ERROR", str(e))


def calculate_similarity(code1: str, code2: str) -> float:
    """Calculate structural similarity between two normalized ASTs."""
    if not code1 or not code2:
        return 0.0
    tokens1 = set(code1.split())
    tokens2 = set(code2.split())
    if not tokens1 or not tokens2:
        return 0.0
    intersection = tokens1 & tokens2
    union = tokens1 | tokens2
    return len(intersection) / len(union) if union else 0.0


def analyze_redundancy(base_path: str) -> dict:
    """Main analysis function."""
    print("=" * 80)
    print("AST REDUNDANCY ANALYZER - SOVEREIGN STRUCTURAL DEDUPLICATION")
    print("December 30, 2025")
    print("=" * 80)
    print()
    print("PHASE 1: Discovering Agent Classes...")
    agents = find_agent_classes(base_path)
    print(f"  Found {len(agents)} PascalCase Agent classes")
    print()
    print("PHASE 2: Generating AST Fingerprints...")
    for agent in tqdm(agents, desc="Processing", unit="item"):
        fingerprint, normalized = generate_fingerprint(agent.file_path, agent.name)
        agent.fingerprint = fingerprint
        agent.normalized_ast = normalized
    print(f"  Generated fingerprints for {len(agents)} agents")
    print()
    print("PHASE 3: Detecting Exact Duplicates...")
    fingerprint_groups: dict[str, list[AgentInfo]] = defaultdict(list)
    for agent in agents:
        if not agent.fingerprint.startswith("ERROR") and (not agent.fingerprint.startswith("SYNTAX")):
            fingerprint_groups[agent.fingerprint].append(agent)
    exact_duplicates = {k: v for k, v in fingerprint_groups.items() if len(v) > 1}
    print(f"  Found {len(exact_duplicates)} groups of exact duplicates")
    print()
    print("PHASE 4: Analyzing Near-Duplicates (>90% similarity)...")
    near_duplicates = []
    agents_with_ast = [a for a in agents if a.normalized_ast and (not a.fingerprint.startswith("ERROR"))]
    for i, agent1 in enumerate(agents_with_ast):
        for agent2 in agents_with_ast[i + 1 :]:
            if agent1.fingerprint != agent2.fingerprint:
                similarity = calculate_similarity(agent1.normalized_ast, agent2.normalized_ast)
                if similarity >= 0.9:
                    near_duplicates.append((agent1, agent2, similarity))
    print(f"  Found {len(near_duplicates)} near-duplicate pairs")
    print()
    return {
        "total_agents": len(agents),
        "agents": agents,
        "exact_duplicates": exact_duplicates,
        "near_duplicates": near_duplicates,
    }


def print_report(results: dict):
    """Print formatted report."""
    print("=" * 80)
    print("COMPREHENSIVE AST REDUNDANCY REPORT")
    print("=" * 80)
    print()
    print("┌" + "─" * 78 + "┐")
    print("│ {:^76} │".format("AGENT FINGERPRINT REGISTRY"))
    print("├" + "─" * 40 + "┬" + "─" * 6 + "┬" + "─" * 8 + "┬" + "─" * 20 + "┤")
    print("│ {:^38} │ {:^4} │ {:^6} │ {:^18} │".format("Agent Name", "Layer", "Methods", "Fingerprint"))
    print("├" + "─" * 40 + "┼" + "─" * 6 + "┼" + "─" * 8 + "┼" + "─" * 20 + "┤")
    for agent in sorted(results["agents"], key=lambda a: (a.layer, a.name)):
        fp_display = agent.fingerprint[:16] if len(agent.fingerprint) >= 16 else agent.fingerprint
        print(f"│ {agent.name[:38]:38} │ {agent.layer:^4} │ {agent.method_count:^6} │ {fp_display:18} │")
    print("└" + "─" * 40 + "┴" + "─" * 6 + "┴" + "─" * 8 + "┴" + "─" * 20 + "┘")
    print()
    print("=" * 80)
    print("EXACT STRUCTURAL DUPLICATES")
    print("=" * 80)
    if results["exact_duplicates"]:
        for fingerprint, agents in tqdm(results["exact_duplicates"].items(), desc="Processing", unit="item"):
            print(f"\n[DUPLICATE GROUP] Fingerprint: {fingerprint}")
            print("-" * 60)
            for agent in agents:
                rel_path = agent.file_path.replace(str(REPO_ROOT) + "/", "")
                print(f"  - {agent.name}")
                print(f"    File: {rel_path}")
                print(f"    Layer: {agent.layer}, Methods: {agent.method_count}")
            l5_agents = [a for a in agents if a.layer == "L5"]
            if l5_agents:
                keep = l5_agents[0]
            else:
                keep = sorted(agents, key=lambda a: a.layer)[0]
            delete = [a for a in agents if a != keep]
            print("\n  RECOMMENDATION:")
            print(f"    KEEP:   {keep.name} ({keep.layer})")
            for d in delete:
                print(f"    DELETE: {d.name} ({d.layer})")
    else:
        print("\n[OK] No exact structural duplicates found!")
    print()
    print("=" * 80)
    print("NEAR-DUPLICATE PAIRS (>90% Structural Similarity)")
    print("=" * 80)
    if results["near_duplicates"]:
        for agent1, agent2, similarity in sorted(results["near_duplicates"], key=lambda x: -x[2]):
            print(f"\n[NEAR-DUP] Similarity: {similarity:.1%}")
            print(f"  1. {agent1.name} ({agent1.layer})")
            print(f"  2. {agent2.name} ({agent2.layer})")
            print("  → Consider merging or refactoring")
    else:
        print("\n[OK] No near-duplicates found!")
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total Agent Classes:     {results['total_agents']}")
    print(f"Exact Duplicate Groups:  {len(results['exact_duplicates'])}")
    print(f"Near-Duplicate Pairs:    {len(results['near_duplicates'])}")
    if not results["exact_duplicates"] and (not results["near_duplicates"]):
        print()
        print("=" * 80)
        print("AST REDUNDANCY ANALYSIS COMPLETE")
        print("STRUCTURAL DUPLICATES: NONE FOUND")
        print("CODEBASE ETERNALLY PURE AND MAXIMALLY SOVEREIGN")
        print("=" * 80)


if __name__ == "__main__":
    base_path = str(REPO_ROOT / "agentic_core")
    results = analyze_redundancy(base_path)
    print_report(results)
    report_path = REPO_ROOT / "ast_redundancy_report.json"
    json_data = {
        "total_agents": results["total_agents"],
        "agents": [
            {
                "name": a.name,
                "file_path": a.file_path,
                "layer": a.layer,
                "method_count": a.method_count,
                "fingerprint": a.fingerprint,
                "methods": a.method_names,
            }
            for a in results["agents"]
        ],
        "exact_duplicates": {
            k: [{"name": a.name, "file": a.file_path, "layer": a.layer} for a in v]
            for k, v in results["exact_duplicates"].items()
        },
        "near_duplicates": [
            {"agent1": a1.name, "agent2": a2.name, "similarity": s}
            for a1, a2, s in results["near_duplicates"]
        ],
    }
    _wg.write_text(report_path, json.dumps(json_data, indent=2))
    print(f"\nJSON report saved to: {report_path}")
