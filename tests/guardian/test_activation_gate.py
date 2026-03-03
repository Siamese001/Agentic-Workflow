"""Guardian tests for G-16-6 — Activation Gate enforcement.

Validates:
1. Happy path: all components present → no raise.
2. Missing component denial (3 tests): each missing component → PermissionError.
3. Structural wiring: orchestrate() calls assert_activation_allowed.
4. Fail-closed proof: version marker present, gate raises on any missing component.
"""

from __future__ import annotations

import ast
import sys
import types
from pathlib import Path

import pytest

from agentic_core.L5_safety.enforcement.activation_gate import (
    ACTIVATION_GATE_VERSION,
    assert_activation_allowed,
)

# =====================================================================
# 1. Happy path
# =====================================================================


class TestHappyPath:
    """All enforcement modules present → gate allows."""

    def test_all_components_present_no_raise(self):
        """With real modules present, assert_activation_allowed must not raise."""
        assert_activation_allowed()

    def test_all_components_present_with_trace_id(self):
        """With trace_id supplied, still passes when modules present."""
        assert_activation_allowed(trace_id="trace-happy-path")


# =====================================================================
# 2. Missing component denial
# =====================================================================


class TestMissingComponentDenial:
    """Each missing component must trigger PermissionError (FAIL-CLOSED)."""

    def test_missing_capability_chokepoint(self, monkeypatch):
        """Missing capability_chokepoint → PermissionError."""
        mod_key = "agentic_core.L2_execution.enforcement.capability_chokepoint"
        original = sys.modules.get(mod_key)
        monkeypatch.setitem(sys.modules, mod_key, None)
        try:
            with pytest.raises(PermissionError, match="capability_chokepoint"):
                assert_activation_allowed(trace_id="trace-missing-cc")
        finally:
            if original is not None:
                sys.modules[mod_key] = original
            else:
                sys.modules.pop(mod_key, None)

    def test_missing_mutation_prohibition(self, monkeypatch):
        """Missing mutation_prohibition → PermissionError."""
        mod_key = "agentic_core.L5_safety.enforcement.mutation_prohibition_enforcer"
        original = sys.modules.get(mod_key)
        monkeypatch.setitem(sys.modules, mod_key, None)
        try:
            with pytest.raises(PermissionError, match="mutation_prohibition"):
                assert_activation_allowed(trace_id="trace-missing-mp")
        finally:
            if original is not None:
                sys.modules[mod_key] = original
            else:
                sys.modules.pop(mod_key, None)

    def test_missing_healer_pipe_order(self, monkeypatch):
        """Missing healer_pipe_order → PermissionError."""
        mod_key = "agentic_core.L2_execution.enforcement.healer_pipe_order"
        original = sys.modules.get(mod_key)
        monkeypatch.setitem(sys.modules, mod_key, None)
        try:
            with pytest.raises(PermissionError, match="healer_pipe_order"):
                assert_activation_allowed(trace_id="trace-missing-hpo")
        finally:
            if original is not None:
                sys.modules[mod_key] = original
            else:
                sys.modules.pop(mod_key, None)

    def test_multiple_missing_lists_all(self, monkeypatch):
        """Multiple missing → PermissionError lists all missing keys."""
        keys = [
            "agentic_core.L2_execution.enforcement.capability_chokepoint",
            "agentic_core.L2_execution.enforcement.healer_pipe_order",
        ]
        originals = {k: sys.modules.get(k) for k in keys}
        for k in keys:
            monkeypatch.setitem(sys.modules, k, None)
        try:
            with pytest.raises(PermissionError) as exc_info:
                assert_activation_allowed()
            msg = str(exc_info.value)
            assert "capability_chokepoint" in msg
            assert "healer_pipe_order" in msg
        finally:
            for k in keys:
                if originals[k] is not None:
                    sys.modules[k] = originals[k]
                else:
                    sys.modules.pop(k, None)

    def test_missing_symbol_on_module(self, monkeypatch):
        """Module importable but symbol missing → PermissionError."""
        mod_key = "agentic_core.L2_execution.enforcement.capability_chokepoint"
        original = sys.modules.get(mod_key)
        # Create a stub module without authorize_and_execute
        stub = types.ModuleType(mod_key)
        monkeypatch.setitem(sys.modules, mod_key, stub)
        try:
            with pytest.raises(PermissionError, match="capability_chokepoint"):
                assert_activation_allowed()
        finally:
            if original is not None:
                sys.modules[mod_key] = original
            else:
                sys.modules.pop(mod_key, None)


# =====================================================================
# 3. Structural wiring
# =====================================================================


class TestStructuralWiring:
    """Verify that the canonical runtime entrypoint calls the activation gate."""

    def test_orchestrate_calls_activation_gate(self):
        """unified_workflow_config.py must contain assert_activation_allowed in orchestrate()."""
        config_path = Path("agentic_core/L2_execution/config/unified_workflow_config.py")
        assert config_path.exists(), f"Missing: {config_path}"

        source = config_path.read_text(encoding="utf-8")
        tree = ast.parse(source)

        found_in_orchestrate = False
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == "orchestrate":
                    # Walk the body of orchestrate for the call
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call):
                            func = child.func
                            if isinstance(func, ast.Name) and func.id == "assert_activation_allowed":
                                found_in_orchestrate = True
                            elif isinstance(func, ast.Attribute) and func.attr == "assert_activation_allowed":
                                found_in_orchestrate = True

        assert found_in_orchestrate, (
            "assert_activation_allowed() not found in orchestrate() body. "
            "G-16-6 activation gate is not wired."
        )

    def test_activation_gate_import_present(self):
        """unified_workflow_config.py must import assert_activation_allowed."""
        config_path = Path("agentic_core/L2_execution/config/unified_workflow_config.py")
        source = config_path.read_text(encoding="utf-8")
        tree = ast.parse(source)

        imported = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and "activation_gate" in node.module:
                    for alias in node.names:
                        if alias.name == "assert_activation_allowed":
                            imported = True

        assert imported, "assert_activation_allowed not imported in unified_workflow_config.py"

    def test_single_activation_gate_module(self):
        """Exactly one activation_gate.py must exist under agentic_core/."""
        matches = list(Path("agentic_core").rglob("activation_gate.py"))
        assert len(matches) == 1, f"Expected 1 activation_gate.py, found {len(matches)}: {matches}"

    def test_dashboard_e2e_pipeline_calls_activation_gate(self):
        """dashboard_e2e_pipeline.py must contain assert_activation_allowed in run()."""
        pipeline_path = Path("agentic_core/L2_execution/enforcement/dashboard_e2_e_pipeline.py")
        assert pipeline_path.exists(), f"Missing: {pipeline_path}"

        source = pipeline_path.read_text(encoding="utf-8")
        tree = ast.parse(source)

        found_in_run = False
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == "run":
                    # Walk the body of run for the call
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call):
                            func = child.func
                            if isinstance(func, ast.Name) and func.id == "assert_activation_allowed":
                                found_in_run = True
                            elif isinstance(func, ast.Attribute) and func.attr == "assert_activation_allowed":
                                found_in_run = True

        assert found_in_run, (
            "assert_activation_allowed() not found in run() body of dashboard_e2e_pipeline.py. "
            "G-16-6 activation gate is not wired."
        )


# =====================================================================
# 4. Fail-closed proof
# =====================================================================


class TestFailClosedProof:
    """Prove the gate is fail-closed by design."""

    def test_version_marker_present(self):
        """ACTIVATION_GATE_VERSION must be a non-empty string."""
        assert isinstance(ACTIVATION_GATE_VERSION, str)
        assert len(ACTIVATION_GATE_VERSION) > 0

    def test_version_marker_value(self):
        """Version marker must match expected value."""
        assert ACTIVATION_GATE_VERSION == "v5.4-P0"

    def test_denial_message_is_deterministic(self, monkeypatch):
        """PermissionError message must be deterministic and contain version."""
        mod_key = "agentic_core.L2_execution.enforcement.healer_pipe_order"
        original = sys.modules.get(mod_key)
        monkeypatch.setitem(sys.modules, mod_key, None)
        try:
            with pytest.raises(PermissionError) as exc_info:
                assert_activation_allowed(trace_id="det-trace")
            msg = str(exc_info.value)
            assert "ACTIVATION_DENIED" in msg
            assert "v5.4-P0" in msg
            assert "healer_pipe_order" in msg
            assert "trace_id=det-trace" in msg
        finally:
            if original is not None:
                sys.modules[mod_key] = original
            else:
                sys.modules.pop(mod_key, None)

    def test_denial_without_trace_id(self, monkeypatch):
        """Denial message must not contain trace_id when not supplied."""
        mod_key = "agentic_core.L2_execution.enforcement.healer_pipe_order"
        original = sys.modules.get(mod_key)
        monkeypatch.setitem(sys.modules, mod_key, None)
        try:
            with pytest.raises(PermissionError) as exc_info:
                assert_activation_allowed()
            msg = str(exc_info.value)
            assert "trace_id" not in msg
        finally:
            if original is not None:
                sys.modules[mod_key] = original
            else:
                sys.modules.pop(mod_key, None)
