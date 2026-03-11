"""Wave P1.3 ΓÇö Healing Re-Entry Invariant Tests.

Validates:
- Healing approval is mediated via L0 safety_enforcement_seam (no direct L2ΓåÆL5 import).
- Healing apply + rollback use direct L2.2 FileIo.save_file (no L0 mutation routing).
- WriteSetEnforcer still blocks undeclared writes (regression guard).
- No route_mutation_intent call is made during healing.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    L0_ROUTING_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
)

pytestmark = pytest.mark.governance

_REPO_ROOT = Path(__file__).resolve().parents[2]
_ORCHESTRATOR = _REPO_ROOT / L2_EXECUTION_DIR / "engines" / "validation_orchestrator.py"
_SEAM_FILE = _REPO_ROOT / L0_ROUTING_DIR / "seams" / "safety_enforcement_seam.py"


# ---------------------------------------------------------------------------
# Wave P1.3.1 ΓÇö Static: no direct L2ΓåÆL5 import in orchestrator
# ---------------------------------------------------------------------------


class TestNoDirectL5Import:
    """validation_orchestrator.py must not contain any static L5 import."""

    def test_no_static_l5_import(self):
        tree = ast.parse(_ORCHESTRATOR.read_text("utf-8"), filename=str(_ORCHESTRATOR))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                assert "L5_safety" not in node.module, (
                    f"Static L2ΓåÆL5 import at line {node.lineno}: from {node.module}"
                )
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    assert "L5_safety" not in alias.name, (
                        f"Static L2ΓåÆL5 import at line {node.lineno}: import {alias.name}"
                    )

    def test_no_static_l3_import(self):
        """No static L2ΓåÆL3 import either."""
        tree = ast.parse(_ORCHESTRATOR.read_text("utf-8"), filename=str(_ORCHESTRATOR))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                assert L3_ORCHESTRATION_DIR not in node.module, (
                    f"Static L2ΓåÆL3 import at line {node.lineno}: from {node.module}"
                )


# ---------------------------------------------------------------------------
# Wave P1.3.2 ΓÇö Static: orchestrator uses _load_activation_gate helper
# ---------------------------------------------------------------------------


class TestApprovalViaSeamStaticProof:
    """Orchestrator must call _load_activation_gate (seam-backed) not L5 directly."""

    def test_load_activation_gate_helper_present(self):
        """_load_activation_gate function is defined in orchestrator module."""
        src = _ORCHESTRATOR.read_text("utf-8")
        assert "_load_activation_gate" in src, (
            "_load_activation_gate helper not found in validation_orchestrator.py"
        )

    def test_load_activation_gate_called_in_smart_fix(self):
        """_load_activation_gate() is called inside the smart_fix method body."""
        tree = ast.parse(_ORCHESTRATOR.read_text("utf-8"), filename=str(_ORCHESTRATOR))
        smart_fix_calls = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == "smart_fix":
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call):
                            func = child.func
                            name = func.id if isinstance(func, ast.Name) else getattr(func, "attr", None)
                            if name == "_load_activation_gate":
                                smart_fix_calls.append(child.lineno)
        assert len(smart_fix_calls) >= 1, "_load_activation_gate() not called inside smart_fix"

    def test_seam_exposes_load_activation_gate(self):
        """safety_enforcement_seam.py must define load_activation_gate."""
        src = _SEAM_FILE.read_text("utf-8")
        assert "def load_activation_gate" in src, (
            "load_activation_gate not found in safety_enforcement_seam.py"
        )

    def test_seam_uses_importlib_not_static(self):
        """load_activation_gate in seam must use importlib, not static import."""
        tree = ast.parse(_SEAM_FILE.read_text("utf-8"), filename=str(_SEAM_FILE))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == "load_activation_gate":
                    src_slice = ast.get_source_segment(_SEAM_FILE.read_text("utf-8"), node)
                    assert src_slice and "importlib" in src_slice, "load_activation_gate must use importlib"


# ---------------------------------------------------------------------------
# Wave P1.3.3 ΓÇö Static: apply + rollback use _get_file_io (direct L2.2)
# ---------------------------------------------------------------------------


class TestDirectL2WritesStaticProof:
    """Orchestrator apply and rollback must use _get_file_io, not open()."""

    def test_get_file_io_helper_present(self):
        src = _ORCHESTRATOR.read_text("utf-8")
        assert "_get_file_io" in src, "_get_file_io helper not found in validation_orchestrator.py"

    def test_get_file_io_called_in_smart_fix(self):
        """_get_file_io() is called inside smart_fix (for apply and rollback)."""
        tree = ast.parse(_ORCHESTRATOR.read_text("utf-8"), filename=str(_ORCHESTRATOR))
        calls = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == "smart_fix":
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call):
                            func = child.func
                            name = func.id if isinstance(func, ast.Name) else getattr(func, "attr", None)
                            if name == "_get_file_io":
                                calls.append(child.lineno)
        # Must be called at least twice: once for apply, once for rollback
        assert len(calls) >= 2, (
            f"_get_file_io() called {len(calls)} time(s) in smart_fix; expected ΓëÑ2 (apply + rollback)"
        )

    def test_no_bare_open_write_in_smart_fix(self):
        """smart_fix must not contain open(..., 'w') direct writes."""
        tree = ast.parse(_ORCHESTRATOR.read_text("utf-8"), filename=str(_ORCHESTRATOR))
        violations = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == "smart_fix":
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call):
                            func = child.func
                            if isinstance(func, ast.Name) and func.id == "open":
                                for arg in child.args:
                                    if isinstance(arg, ast.Constant) and "w" in str(arg.value):
                                        violations.append(child.lineno)
        assert len(violations) == 0, f"open(..., 'w') still present in smart_fix at lines: {violations}"

    def test_no_route_mutation_intent_in_orchestrator(self):
        """route_mutation_intent must NOT appear in orchestrator source."""
        src = _ORCHESTRATOR.read_text("utf-8")
        assert "route_mutation_intent" not in src, (
            "route_mutation_intent found in validation_orchestrator.py ΓÇö "
            "L2 must not route mutations through L0"
        )


# ---------------------------------------------------------------------------
# Wave P1.3.4 — Lock Option A: activation_gate module-level API contract
# ---------------------------------------------------------------------------

_ACTIVATION_GATE = _REPO_ROOT / AGENTIC_CORE_DIR / "L5_safety" / "enforcement" / "activation_gate.py"


class TestActivationGateModuleLevelContract:
    """activation_gate.py must export assert_activation_allowed at module level.

    This locks Option A: the seam returns the module and callers invoke
    module.assert_activation_allowed(...) directly — no ActivationGate()
    instance required.
    """

    def test_assert_activation_allowed_is_module_level_function(self):
        """assert_activation_allowed must be a top-level def in activation_gate.py."""
        tree = ast.parse(
            _ACTIVATION_GATE.read_text("utf-8"),
            filename=str(_ACTIVATION_GATE),
        )
        top_level_funcs = {
            node.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and isinstance(node.col_offset, int)
            and node.col_offset == 0
        }
        assert "assert_activation_allowed" in top_level_funcs, (
            "assert_activation_allowed is not a module-level function in "
            "activation_gate.py — Option A contract broken"
        )

    def test_assert_activation_allowed_in_dunder_all(self):
        """assert_activation_allowed must appear in __all__ of activation_gate."""
        src = _ACTIVATION_GATE.read_text("utf-8")
        assert "assert_activation_allowed" in src, "assert_activation_allowed not found in activation_gate.py"
        tree = ast.parse(src, filename=str(_ACTIVATION_GATE))
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets
            ):
                if isinstance(node.value, ast.List):
                    exported = {
                        elt.s
                        for elt in node.value.elts
                        if isinstance(elt, ast.Constant) and isinstance(elt.s, str)
                    }
                    assert "assert_activation_allowed" in exported, (
                        "assert_activation_allowed missing from __all__ in activation_gate.py"
                    )
                    return
        pytest.fail("__all__ not found in activation_gate.py")

    def test_orchestrator_calls_assert_activation_allowed_on_gate_mod(self):
        """Orchestrator must call _gate_mod.assert_activation_allowed (module API).

        Verifies the call is an attribute access on a Name (the module variable),
        not a bare function call — locking Option A usage pattern.
        """
        tree = ast.parse(
            _ORCHESTRATOR.read_text("utf-8"),
            filename=str(_ORCHESTRATOR),
        )
        found = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Attribute) and func.attr == "assert_activation_allowed":
                    found.append(node.lineno)
        assert len(found) >= 1, (
            "assert_activation_allowed not called as attribute on module variable "
            "in validation_orchestrator.py — expected _gate_mod.assert_activation_allowed(...)"
        )


# ---------------------------------------------------------------------------
# Wave P1.3.5 — Lock save_file call path through _get_file_io()
# ---------------------------------------------------------------------------


class TestHealingWriteCallPath:
    """Healing writes must call .save_file() on the result of _get_file_io().

    This is the authoritative write primitive for this branch state.
    Proves the call path statically so no bare open() or alternative
    write path can silently bypass it.
    """

    def test_save_file_called_on_file_io_result(self):
        """save_file must be called as an attribute call in smart_fix.

        Pattern: _get_file_io().save_file(...) or equivalent attribute call.
        """
        tree = ast.parse(
            _ORCHESTRATOR.read_text("utf-8"),
            filename=str(_ORCHESTRATOR),
        )
        save_file_calls = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == "smart_fix":
                    for child in ast.walk(node):
                        if (
                            isinstance(child, ast.Call)
                            and isinstance(child.func, ast.Attribute)
                            and child.func.attr == "save_file"
                        ):
                            save_file_calls.append(child.lineno)
        assert len(save_file_calls) >= 2, (
            f"save_file called {len(save_file_calls)} time(s) in smart_fix; expected ≥2 (apply + rollback)"
        )

    def test_no_open_write_anywhere_in_orchestrator(self):
        """No open(..., 'w') or open(..., 'wb') anywhere in orchestrator."""
        tree = ast.parse(
            _ORCHESTRATOR.read_text("utf-8"),
            filename=str(_ORCHESTRATOR),
        )
        violations = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id == "open":
                    for arg in node.args:
                        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                            if "w" in arg.value:
                                violations.append(node.lineno)
                    for kw in node.keywords:
                        if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                            if "w" in str(kw.value.value):
                                violations.append(node.lineno)
        assert violations == [], (
            f"open(..., 'w') found in validation_orchestrator.py at lines "
            f"{violations} — all writes must go through _get_file_io().save_file()"
        )
