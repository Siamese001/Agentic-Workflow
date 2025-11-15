# AUTO-GENERATED FLAT TEST FILE
# Sources:
#   - tests/architecture/test_architecture_compliance_v10_7.py
#   - tests/design/test_design_validation_dag_v10_7.py
#   - tests/architecture/test_core_module_exports.py
#   - tests/architecture/test_config_v10_7.py
# ------------------------------------------------------------------
# ----- BEGIN: tests/architecture/test_architecture_compliance_v10_7.py -----
import ast
import os
from pathlib import Path
import pytest


# ----------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
AGENTIC_ROOT = ROOT
STACKS_DIR = AGENTIC_ROOT / "agent_stacks_v10_8" / "components"
TOOLS_DIR = AGENTIC_ROOT / "tools_v10_7"


# ----------------------------------------------------------------------
# Helper: Parse Python module into AST
# ----------------------------------------------------------------------
def load_ast(path: Path) -> ast.Module:
    with path.open("r", encoding="utf-8") as f:
        return ast.parse(f.read())


# ----------------------------------------------------------------------
# 1. No global CONFIG imports anywhere in stacks or tools.
# ----------------------------------------------------------------------
@pytest.mark.architecture
@pytest.mark.parametrize("path", list(STACKS_DIR.rglob("*.py")) + list(TOOLS_DIR.rglob("*.py")))
def test_no_global_config_imports(path: Path):
    """
    v10.7 design forbids global config imports. All services must be DI-injected.
    """
    text = path.read_text()
    forbidden = [
        "from core import CONFIG",
        "import CONFIG",
        "from config import CONFIG",
        "from .config import CONFIG",
    ]

    for pattern in forbidden:
        assert pattern not in text, f"Forbidden global CONFIG import in {path}"


# ----------------------------------------------------------------------
# 2. No service locator patterns allowed.
# ----------------------------------------------------------------------
@pytest.mark.architecture
@pytest.mark.parametrize("path", list(AGENTIC_ROOT.rglob("*.py")))
def test_no_service_locator_patterns(path: Path):
    """
    Ensures no file uses Registry.get(), Container.resolve(), or other DI anti-patterns.
    """
    forbidden = [
        "Registry.get",
        "Container.resolve",
        "ServiceLocator",
        "dependency_registry",
    ]

    text = path.read_text()
    for f in forbidden:
        assert f not in text, f"Service locator anti-pattern detected in {path}: {f}"


# ----------------------------------------------------------------------
# 3. No stack may import another stack (strict layering).
# ----------------------------------------------------------------------
@pytest.mark.architecture
@pytest.mark.parametrize("path", list(STACKS_DIR.rglob("*.py")))
def test_no_cross_stack_imports(path: Path):
    """
    StrategyStack cannot import QAStack, DraftingStack cannot import RAGStack, etc.
    Prevents architecture collapse and circular dependencies.
    """
    text = path.read_text()

    # Extract stack directory names:
    stack_names = [p.name for p in STACKS_DIR.iterdir() if p.is_dir()]
    stack_names_lower = [name.lower() for name in stack_names]

    for other_stack in stack_names_lower:
        if other_stack in path.name.lower():
            continue  # Allow self-import inside a stack
        import_pattern = f"import {other_stack}"
        from_pattern = f"from {other_stack}"
        assert import_pattern not in text, f"Cross-stack import '{import_pattern}' found in {path}"
        assert from_pattern not in text, f"Cross-stack import '{from_pattern}' found in {path}"


# ----------------------------------------------------------------------
# 4. Agents must implement required interface structure: must have 'run'.
# ----------------------------------------------------------------------
def _get_classes_with_name(module_ast: ast.Module):
    for node in module_ast.body:
        if isinstance(node, ast.ClassDef):
            yield node


@pytest.mark.architecture
@pytest.mark.parametrize("pyfile", list(STACKS_DIR.rglob("*.py")))
def test_agents_have_run_method(pyfile: Path):
    """
    Ensures every agent class in stack directories has a 'run' method.
    This enforces the agent interface.

    Only classes ending in 'Agent' are checked.
    """
    tree = load_ast(pyfile)
    for cls in _get_classes_with_name(tree):
        if not cls.name.endswith("Agent"):
            continue

        has_run = any(
            isinstance(n, ast.FunctionDef) and n.name == "run"
            for n in cls.body
        )

        assert has_run, f"Agent '{cls.name}' must implement a run() method ({pyfile})"


# ----------------------------------------------------------------------
# 5. Stacks must not instantiate WorkflowContext internally.
# ----------------------------------------------------------------------
@pytest.mark.architecture
@pytest.mark.parametrize("path", list(STACKS_DIR.rglob("*.py")))
def test_no_context_instantiation(path: Path):
    """
    v10.7 design prohibits stacks from creating new WorkflowContext instances inside the agent.
    All context objects must be injected.

    Looks for 'WorkflowContext(' constructor usage.
    """
    text = path.read_text()
    assert "WorkflowContext(" not in text, (
        f"'WorkflowContext' must not be instantiated inside stack {path}. "
        f"Context is DI-provided."
    )


# ----------------------------------------------------------------------
# 6. No circular imports among stack modules.
# ----------------------------------------------------------------------
def _extract_imports(tree: ast.Module):
    imports = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.append(n.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return imports


@pytest.mark.architecture
def test_no_circular_imports():
    """
    Builds a simple dependency graph and ensures no A → B → A cycles.
    We only check stack files because other layers have external deps.
    """
    graph = {}
    files = list(STACKS_DIR.rglob("*.py"))

    # Build graph
    for f in files:
        tree = load_ast(f)
        imports = _extract_imports(tree)
        graph[f] = []
        for imp in imports:
            # Map import to a file if it lives under the stack components package
            for candidate in files:
                if candidate.stem == imp or candidate.stem == imp.split(".")[-1]:
                    graph[f].append(candidate)

    # Detect cycles (DFS)
    visited = set()
    stack = set()

    def dfs(node):
        if node in stack:
            raise AssertionError(f"Circular import detected at: {node}")
        if node in visited:
            return
        visited.add(node)
        stack.add(node)
        for nxt in graph[node]:
            dfs(nxt)
        stack.remove(node)

    for f in files:
        dfs(f)
# ----- END: tests/architecture/test_architecture_compliance_v10_7.py -----
# ----- BEGIN: tests/design/test_design_validation_dag_v10_7.py -----
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
# ----- END: tests/design/test_design_validation_dag_v10_7.py -----
# ----- BEGIN: tests/architecture/test_core_module_exports.py -----
from __future__ import annotations

from asyncio import TimeoutError as NativeTimeoutError

import core_v10_7


def _module_union() -> set[str]:
    """Return the union of all declared module exports plus AsyncTimeoutError."""

    modules = [
        core_v10_7.agents,
        core_v10_7.clients,
        core_v10_7.config,
        core_v10_7.constants,
        core_v10_7.context,
        core_v10_7.exceptions,
        core_v10_7.mcp,
        core_v10_7.models,
        core_v10_7.resilience,
        core_v10_7.services,
    ]
    exports = {symbol for module in modules for symbol in getattr(module, "__all__", [])}
    exports.add("AsyncTimeoutError")
    return exports


def test_public_api_contains_expected_symbols() -> None:
    expected = {"CacheManager", "WorkflowContext", "ConfigV10_7", "AsyncTimeoutError"}
    assert expected.issubset(set(core_v10_7.__all__))


def test_async_timeout_error_alias_matches_asyncio() -> None:
    assert core_v10_7.AsyncTimeoutError is NativeTimeoutError


def test_package_reexports_match_module_definitions() -> None:
    assert core_v10_7.CacheManager is core_v10_7.services.CacheManager
    assert core_v10_7.WorkflowContext is core_v10_7.context.WorkflowContext


def test_public_api_matches_union_of_submodules() -> None:
    assert set(core_v10_7.__all__) == _module_union()


def test_public_api_is_sorted() -> None:
    assert list(core_v10_7.__all__) == sorted(core_v10_7.__all__)
# ----- END: tests/architecture/test_core_module_exports.py -----
# ----- BEGIN: tests/architecture/test_config_v10_7.py -----
import pytest

from core_v10_7 import ConfigV10_7


def test_config_provides_nested_sections(config: ConfigV10_7) -> None:
    assert config.logging_config.log_level == "INFO"
    assert config.agent_stacks.enable_constitutional_review is True
    assert config.agent_stacks.conductor_max_steps == 10


def test_config_missing_section_raises_attribute_error(config: ConfigV10_7) -> None:
    with pytest.raises(AttributeError):
        _ = config.this_section_does_not_exist
# ----- END: tests/architecture/test_config_v10_7.py -----
