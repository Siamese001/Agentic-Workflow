"""Shared AST scanning infrastructure for Guardian sovereign agent contract tests.

All enforcement is AST-based. No runtime imports of production agents.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

# ── Project paths ──────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
AGENTIC_CORE = PROJECT_ROOT / "agentic_core"

# ── Constants ──────────────────────────────────────────────────────────────────
AGENT_FILENAME_RE = re.compile(r"^[A-Z][A-Za-z0-9]*Agent\.py$")

# Layer base classes that inherit (directly) from SovereignBaseAgent.
# AST-only: we track known names rather than resolving MRO at runtime.
KNOWN_SOVEREIGN_BASES = frozenset(
    {
        "SovereignBaseAgent",
        "L0RoutingBase",
        "L1CognitionBase",
        "L2ExecutionBase",
        "L3OrchestrationBase",
        "L4StateBase",
        "L5SafetyBase",
        "L6ObservabilityBase",
    },
)

APPROVED_GUARD_DECORATORS = frozenset(
    {
        "v15_runtime_guard",
        "_optional_v15_runtime_guard",
    },
)

ARTIFACT_CALL_NAMES = frozenset(
    {
        "emit_artifact",
        "publish",
        "emit_result",
        "produce_artifact",
    },
)

ARTIFACT_CLASS_NAMES = frozenset(
    {
        "Artifact",
    },
)

FORBIDDEN_TEST_MODULES = frozenset(
    {
        "pytest",
        "unittest",
        "hypothesis",
    },
)

FORBIDDEN_TEST_PREFIXES = ("tests.", "support.")


# ── File collection ────────────────────────────────────────────────────────────
def collect_reasoning_agent_files() -> list[Path]:
    """Collect all PascalCase *Agent.py under agentic_core/**/reasoning/."""
    results: list[Path] = []
    for reasoning_dir in sorted(AGENTIC_CORE.rglob("reasoning")):
        if not reasoning_dir.is_dir():
            continue
        for py_file in sorted(reasoning_dir.glob("*.py")):
            if AGENT_FILENAME_RE.match(py_file.name):
                results.append(py_file)
    return results


# ── AST helpers ────────────────────────────────────────────────────────────────
def parse_file_ast(filepath: Path) -> ast.Module | None:
    """Parse file to AST. Returns None on SyntaxError/UnicodeDecodeError."""
    try:
        source = filepath.read_text(encoding="utf-8")
        return ast.parse(source, filename=str(filepath))
    except (SyntaxError, UnicodeDecodeError):
        return None


def rel(filepath: Path) -> str:
    """Canonical relative path from project root (forward slashes)."""
    return str(filepath.relative_to(PROJECT_ROOT)).replace("\\", "/")


# ── Exemption check (Phase 8) ─────────────────────────────────────────────────
def check_exemption(tree: ast.Module) -> tuple[bool, str]:
    """Check for __agent_contract_exempt__ + __agent_contract_exempt_reason__.

    Returns (exempt: bool, reason: str).
    If exempt is True but reason is empty, the exemption is INVALID.
    """
    exempt_flag = False
    exempt_reason = ""
    for node in ast.iter_child_nodes(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if not isinstance(target, ast.Name):
                continue
            if target.id == "__agent_contract_exempt__":
                if isinstance(node.value, ast.Constant) and node.value.value is True:
                    exempt_flag = True
            elif target.id == "__agent_contract_exempt_reason__":
                if isinstance(node.value, ast.Constant) and isinstance(
                    node.value.value,
                    str,
                ):
                    exempt_reason = node.value.value.strip()
    if exempt_flag and not exempt_reason:
        # Invalid: exempt without reason
        return False, ""
    return exempt_flag, exempt_reason


def find_agent_class(tree: ast.Module, expected_name: str) -> ast.ClassDef | None:
    """Find top-level ClassDef matching expected_name."""
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef) and node.name == expected_name:
            return node
    return None


def get_top_level_classes(tree: ast.Module) -> list[ast.ClassDef]:
    """Return all top-level ClassDef nodes."""
    return [n for n in ast.iter_child_nodes(tree) if isinstance(n, ast.ClassDef)]


def get_class_base_names(cls: ast.ClassDef) -> list[str]:
    """Extract base class names from a ClassDef (surface-level names only)."""
    names: list[str] = []
    for base in cls.bases:
        if isinstance(base, ast.Name):
            names.append(base.id)
        elif isinstance(base, ast.Attribute):
            names.append(base.attr)
    return names


def get_decorator_names(node: ast.FunctionDef | ast.ClassDef) -> list[str]:
    """Extract decorator names (handles Name and Call wrappers)."""
    names: list[str] = []
    for dec in node.decorator_list:
        if isinstance(dec, ast.Name):
            names.append(dec.id)
        elif isinstance(dec, ast.Call):
            if isinstance(dec.func, ast.Name):
                names.append(dec.func.id)
            elif isinstance(dec.func, ast.Attribute):
                names.append(dec.func.attr)
        elif isinstance(dec, ast.Attribute):
            names.append(dec.attr)
    return names


def find_method(cls: ast.ClassDef, method_name: str) -> ast.FunctionDef | None:
    """Find a method by name in a ClassDef."""
    for node in ast.iter_child_nodes(cls):
        if isinstance(node, ast.FunctionDef) and node.name == method_name:
            return node
    return None


def is_stub_body(body: list[ast.stmt]) -> bool:
    """Check if a function body is a stub (pass, ..., raise NotImplementedError, docstring-only)."""
    real_stmts: list[ast.stmt] = []
    for stmt in body:
        # Skip docstrings
        if (
            isinstance(stmt, ast.Expr)
            and isinstance(stmt.value, ast.Constant)
            and isinstance(stmt.value.value, str)
        ):
            continue
        real_stmts.append(stmt)

    if not real_stmts:
        # docstring-only
        return True

    if len(real_stmts) == 1:
        s = real_stmts[0]
        # pass
        if isinstance(s, ast.Pass):
            return True
        # Ellipsis (...)
        if isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant) and s.value.value is ...:
            return True
        # raise NotImplementedError
        if isinstance(s, ast.Raise):
            exc = s.exc
            if isinstance(exc, ast.Call) and isinstance(exc.func, ast.Name):
                if exc.func.id == "NotImplementedError":
                    return True
            elif isinstance(exc, ast.Name) and exc.id == "NotImplementedError":
                return True

    return False


def is_super_only_delegation(body: list[ast.stmt]) -> bool:
    """Check if body is only ``return super().method(...)`` with no real logic.

    This catches the pattern where an agent defines execute() but merely
    delegates to the base class, adding zero domain logic.  Such a body
    passes ``is_stub_body`` (which looks for pass/…/raise/docstring-only)
    but is semantically equivalent to a stub because
    SovereignBaseAgent.execute raises NotImplementedError.
    """
    # Strip docstrings
    real_stmts: list[ast.stmt] = [
        s
        for s in body
        if not (
            isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant) and isinstance(s.value.value, str)
        )
    ]
    if len(real_stmts) != 1:
        return False
    stmt = real_stmts[0]
    # Must be a bare ``return <call>``
    if not isinstance(stmt, ast.Return) or stmt.value is None:
        return False
    call = stmt.value
    if not isinstance(call, ast.Call):
        return False
    func = call.func
    if not isinstance(func, ast.Attribute):
        return False
    # The value of the attribute must be ``super()``
    if not isinstance(func.value, ast.Call):
        return False
    super_call = func.value
    if isinstance(super_call.func, ast.Name) and super_call.func.id == "super":
        return True
    return False


# ── Artifact-specific dict-key sets ───────────────────────────────────────────
# Strict keys that unambiguously signal artifact production.
# "results" and "output" are intentionally excluded — they are generic
# return-dict keys that do NOT prove artifact emission.
ARTIFACT_DICT_KEYS_STRICT = frozenset({"artifacts", "artifact"})


def get_all_imports(tree: ast.Module) -> list[tuple[str, int]]:
    """Return (module_name, lineno) for all imports in the module."""
    results: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                results.append((alias.name, node.lineno))
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                results.append((node.module, node.lineno))
    return results


def ast_contains_call(node: ast.AST, func_names: frozenset[str]) -> bool:
    """Check if AST subtree contains any Call to a function in func_names.

    Handles:
      - bare calls: emit_artifact(...)
      - attribute calls: self.emit_artifact(...)
    """
    for child in ast.walk(node):
        if not isinstance(child, ast.Call):
            continue
        if isinstance(child.func, ast.Name) and child.func.id in func_names:
            return True
        if isinstance(child.func, ast.Attribute) and child.func.attr in func_names:
            return True
    return False


def ast_contains_name(node: ast.AST, names: frozenset[str]) -> bool:
    """Check if AST subtree contains any Name node with id in names."""
    for child in ast.walk(node):
        if isinstance(child, ast.Name) and child.id in names:
            return True
    return False


def ast_contains_string(node: ast.AST, substrings: frozenset[str]) -> bool:
    """Check if AST subtree contains any string constant containing a substring."""
    for child in ast.walk(node):
        if isinstance(child, ast.Constant) and isinstance(child.value, str):
            for sub in substrings:
                if sub in child.value:
                    return True
    return False
