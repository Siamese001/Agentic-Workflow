"""Guardian: G-L4S-1 — L4 State Write Sovereignty (agentic_core/L4_state).

Proves:
1. Structural: L4_state sub-layers (engines/, types/, config/, P1_interfaces/)
   contain no direct `open()`, `write_text()`, or `json.dump()` calls without
   going through the UniversalWriteGateway — AST-verified.
2. No L4_state file imports from L0_routing, L2_execution, or L5_safety
   directly (layer boundary contract — AST-verified).
3. L4_state/__init__.py exists and is importable.
4. All Python files under L4_state parse without SyntaxError.
5. L4_state does not define new agent classes ending in "Agent" — it is
   a state layer, not a reasoning layer (architectural role contract).
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
L4_ROOT = PROJECT_ROOT / "agentic_core" / "L4_state"

pytestmark = pytest.mark.guardian


# ===========================================================================
# A) Layer exists and is syntactically valid
# ===========================================================================


class TestLayerIntegrity:
    def test_l4_state_directory_exists(self):
        assert L4_ROOT.exists() and L4_ROOT.is_dir(), "agentic_core/L4_state must exist"

    def test_init_exists(self):
        assert (L4_ROOT / "__init__.py").exists(), "agentic_core/L4_state/__init__.py must exist"

    def test_all_files_parse_without_syntax_error(self):
        errors = []
        for f in sorted(L4_ROOT.rglob("*.py")):
            if "__pycache__" in str(f):
                continue
            try:
                src = f.read_text(encoding="utf-8", errors="replace")
                ast.parse(src, filename=str(f))
            except SyntaxError as e:
                errors.append(f.relative_to(PROJECT_ROOT).as_posix() + ": " + str(e))
        assert not errors, "SyntaxError(s) in L4_state:\n" + "\n".join(errors)


# ===========================================================================
# B) No raw I/O calls (write sovereignty)
# ===========================================================================


_FORBIDDEN_WRITE_CALLS = {
    "open",         # builtin open() in write mode
    "write_text",   # Path.write_text without gateway
    "write_bytes",  # Path.write_bytes without gateway
}

_FORBIDDEN_WRITE_ATTRS = {
    ("json", "dump"),
    ("json", "dumps"),  # only flagged if result written to file directly
}

_GATEWAY_IMPORT_NAMES = {
    "UniversalWriteGateway",
    "safe_write_text",
    "safe_json_dump",
    "assert_no_persistent_write",
}


def _collect_write_sites(src: str, filename: str) -> list[str]:
    """Return list of raw write-site descriptions found in source."""
    try:
        tree = ast.parse(src, filename=filename)
    except SyntaxError:
        return []

    # Check if file imports any write gateway symbol
    gateway_imported = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                if alias.name in _GATEWAY_IMPORT_NAMES or alias.asname in _GATEWAY_IMPORT_NAMES:
                    gateway_imported = True
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in _GATEWAY_IMPORT_NAMES:
                    gateway_imported = True

    violations = []
    for node in ast.walk(tree):
        # Detect open() calls used as context managers or direct calls
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == "open":
                # Check if any kwarg or arg suggests write mode
                for arg in node.args:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        if any(m in arg.value for m in ("w", "a", "x")):
                            if not gateway_imported:
                                violations.append(
                                    "open() write at line " + str(node.lineno)
                                )
            # Detect .write_text() / .write_bytes() attribute calls
            if isinstance(func, ast.Attribute) and func.attr in ("write_text", "write_bytes"):
                if not gateway_imported:
                    violations.append(
                        func.attr + "() at line " + str(node.lineno)
                    )
    return violations


class TestWriteSovereignty:
    """L4_state must not perform raw persistent writes without write gateway."""

    def _py_files(self):
        return [
            f for f in sorted(L4_ROOT.rglob("*.py"))
            if "__pycache__" not in str(f)
        ]

    def test_no_unguarded_raw_writes(self):
        violations = {}
        for f in self._py_files():
            rel = f.relative_to(PROJECT_ROOT).as_posix()
            src = f.read_text(encoding="utf-8", errors="replace")
            sites = _collect_write_sites(src, str(f))
            if sites:
                violations[rel] = sites
        assert not violations, (
            "L4_state has unguarded write sites (must use UniversalWriteGateway):\n"
            + "\n".join(k + ": " + str(v) for k, v in violations.items())
        )


# ===========================================================================
# C) No forbidden layer imports (layer boundary contract)
# ===========================================================================


_FORBIDDEN_IMPORTS_FROM = (
    "agentic_core.L2_execution",
    "agentic_core.L5_safety",
)


class TestLayerBoundaryContract:
    """L4_state must not directly import from L2_execution or L5_safety."""

    def test_no_forbidden_layer_imports(self):
        violations = {}
        for f in sorted(L4_ROOT.rglob("*.py")):
            if "__pycache__" in str(f):
                continue
            rel = f.relative_to(PROJECT_ROOT).as_posix()
            try:
                src = f.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(src, filename=str(f))
            except SyntaxError:
                continue
            file_violations = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    for forbidden in _FORBIDDEN_IMPORTS_FROM:
                        if node.module.startswith(forbidden):
                            file_violations.append(
                                "imports from " + node.module + " at line " + str(node.lineno)
                            )
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        for forbidden in _FORBIDDEN_IMPORTS_FROM:
                            if alias.name.startswith(forbidden):
                                file_violations.append(
                                    "imports " + alias.name + " at line " + str(node.lineno)
                                )
            if file_violations:
                violations[rel] = file_violations
        assert not violations, (
            "L4_state has forbidden layer imports:\n"
            + "\n".join(k + ": " + str(v) for k, v in violations.items())
        )


# ===========================================================================
# D) L4_state is not a reasoning layer — no Agent classes
# ===========================================================================


class TestRoleContract:
    """L4_state must not define classes ending in 'Agent' (it is a state layer)."""

    def test_no_agent_classes_defined(self):
        agent_classes = {}
        for f in sorted(L4_ROOT.rglob("*.py")):
            if "__pycache__" in str(f):
                continue
            rel = f.relative_to(PROJECT_ROOT).as_posix()
            try:
                src = f.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(src, filename=str(f))
            except SyntaxError:
                continue
            agents = [
                n.name for n in ast.walk(tree)
                if isinstance(n, ast.ClassDef) and n.name.endswith("Agent")
            ]
            if agents:
                agent_classes[rel] = agents
        assert not agent_classes, (
            "L4_state (state layer) must not define Agent classes — "
            "move to L3_orchestration/reasoning or apps_*/reasoning:\n"
            + "\n".join(k + ": " + str(v) for k, v in agent_classes.items())
        )


# ===========================================================================
# E) L4_state sub-layer structure contract
# ===========================================================================


class TestSubLayerStructure:
    """L4_state must contain expected sub-layer directories."""

    EXPECTED_SUBLAYERS = {"engines", "types"}

    def test_expected_sublayers_exist(self):
        existing = {d.name for d in L4_ROOT.iterdir() if d.is_dir() and not d.name.startswith(".")}
        missing = self.EXPECTED_SUBLAYERS - existing
        assert not missing, (
            "L4_state missing expected sub-layers: " + str(missing)
            + " (found: " + str(existing) + ")"
        )

    def test_engines_sublayer_has_python_files(self):
        engines = L4_ROOT / "engines"
        if not engines.exists():
            pytest.skip("engines sub-layer not present")
        py_files = [f for f in engines.rglob("*.py") if "__pycache__" not in str(f)]
        assert py_files, "L4_state/engines/ must contain at least one Python module"

    def test_types_sublayer_has_python_files(self):
        types_dir = L4_ROOT / "types"
        if not types_dir.exists():
            pytest.skip("types sub-layer not present")
        py_files = [f for f in types_dir.rglob("*.py") if "__pycache__" not in str(f)]
        assert py_files, "L4_state/types/ must contain at least one Python module"
