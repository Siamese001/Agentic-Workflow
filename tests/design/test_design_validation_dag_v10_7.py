import pytest
from pathlib import Path
import ast

# ---------------------------------------------------------------------
# Locate the core workflow builder
# ---------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_BUILDER = ROOT / "agentic_workflow" / "workflow_v10_7" / "builder.py"


# ---------------------------------------------------------------------
# Expected DAG specification (10.7 design doc)
# ---------------------------------------------------------------------
EXPECTED_NODES = [
    "SafetyGuardStack",
    "StrategyStack",
    "RAGStack",
    "BulletStack",
    "DraftingStack",
    "QAStack",
    "HILInteractionStack",
]

EXPECTED_EDGES = [
    ("SafetyGuardStack", "StrategyStack"),
    ("StrategyStack", "RAGStack"),
    ("RAGStack", "BulletStack"),
    ("BulletStack", "DraftingStack"),
    ("DraftingStack", "QAStack"),
    ("QAStack", "HILInteractionStack"),
]

EXPECTED_ORDER = [
    "SafetyGuardStack",
    "StrategyStack",
    "RAGStack",
    "BulletStack",
    "DraftingStack",
    "QAStack",
    "HILInteractionStack",
]


# ---------------------------------------------------------------------
# Helper: parse AST of builder
# ---------------------------------------------------------------------
def load_ast(path: Path):
    assert path.exists(), f"Cannot find workflow builder at {path}"
    with path.open("r", encoding="utf-8") as f:
        return ast.parse(f.read())


# ---------------------------------------------------------------------
# Extract node registration + edges from builder.py
# ---------------------------------------------------------------------
def extract_graph_info(tree: ast.Module):
    nodes = []
    edges = []

    for node in ast.walk(tree):
        # add_node("Name")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr == "add_node":
                if node.args and isinstance(node.args[0], ast.Constant):
                    nodes.append(node.args[0].value)

        # add_edge("A","B")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr == "add_edge":
                if (
                    len(node.args) >= 2
                    and isinstance(node.args[0], ast.Constant)
                    and isinstance(node.args[1], ast.Constant)
                ):
                    edges.append((node.args[0].value, node.args[1].value))

    return nodes, edges


# ---------------------------------------------------------------------
# TEST 1 — Required nodes exist
# ---------------------------------------------------------------------
@pytest.mark.design
def test_all_required_nodes_exist():
    tree = load_ast(WORKFLOW_BUILDER)
    nodes, _ = extract_graph_info(tree)

    for required in EXPECTED_NODES:
        assert required in nodes, (
            f"Missing required DAG node '{required}'. "
            f"This violates v10.7 design specification."
        )


# ---------------------------------------------------------------------
# TEST 2 — No undocumented nodes exist
# ---------------------------------------------------------------------
@pytest.mark.design
def test_no_undocumented_nodes():
    tree = load_ast(WORKFLOW_BUILDER)
    nodes, _ = extract_graph_info(tree)

    extra = [n for n in nodes if n not in EXPECTED_NODES]
    assert not extra, (
        f"Undocumented DAG nodes detected: {extra}. "
        f"All nodes must appear in the v10.7 spec."
    )


# ---------------------------------------------------------------------
# TEST 3 — Required edges exist
# ---------------------------------------------------------------------
@pytest.mark.design
def test_required_edges_exist():
    tree = load_ast(WORKFLOW_BUILDER)
    _, edges = extract_graph_info(tree)

    for edge in EXPECTED_EDGES:
        assert edge in edges, (
            f"Missing required DAG edge {edge}. "
            f"Pipeline must follow v10.7 order."
        )


# ---------------------------------------------------------------------
# TEST 4 — No forbidden edges exist
# ---------------------------------------------------------------------
@pytest.mark.design
def test_no_forbidden_edges():
    tree = load_ast(WORKFLOW_BUILDER)
    _, edges = extract_graph_info(tree)

    expected_set = set(EXPECTED_EDGES)
    extra = [e for e in edges if e not in expected_set]

    assert not extra, (
        f"Forbidden DAG edges detected: {extra}. "
        f"No additional edges allowed in v10.7."
    )


# ---------------------------------------------------------------------
# TEST 5 — Execution order is correct (topological validation)
# ---------------------------------------------------------------------
@pytest.mark.design
def test_execution_order_matches_design():
    tree = load_ast(WORKFLOW_BUILDER)
    nodes, _ = extract_graph_info(tree)

    # Ensure expected sequence is a subsequence of actual nodes
    actual_positions = {n: i for i, n in enumerate(nodes)}

    for earlier, later in zip(EXPECTED_ORDER, EXPECTED_ORDER[1:]):
        assert actual_positions[earlier] < actual_positions[later], (
            f"Execution order incorrect: '{earlier}' must come before '{later}'."
        )


# ---------------------------------------------------------------------
# TEST 6 — Entry point MUST be SafetyGuardStack
# ---------------------------------------------------------------------
@pytest.mark.design
def test_entry_point_is_safetyguard():
    tree = load_ast(WORKFLOW_BUILDER)

    entry_points = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr == "set_entry_point":
                if node.args and isinstance(node.args[0], ast.Constant):
                    entry_points.append(node.args[0].value)

    assert entry_points, "No entry point defined in builder.py"
    assert entry_points[0] == "SafetyGuardStack", (
        "Entry point must ALWAYS be SafetyGuardStack in v10.7"
    )
