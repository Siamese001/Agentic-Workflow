import ast
import os
from pathlib import Path
import pytest


# ----------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
AGENTIC_ROOT = ROOT / "agentic_workflow"
STACKS_DIR = AGENTIC_ROOT / "stacks_v10_7"
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
            # Map import to a file if it lives under stacks_v10_7
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
