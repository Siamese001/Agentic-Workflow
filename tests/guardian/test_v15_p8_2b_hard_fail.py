"""V15 P8.2b — HARD_FAIL Deterministic Abort Surface Tests.

Proves with a single shared violation trigger (pipe order violation):
1) LOG_ONLY: violation does not raise, gateway returns normally
2) SOFT_FAIL: violation does not raise out of execute(); returns GatewayResult failure
3) HARD_FAIL: violation raises V15HardFailAbort (NOT V15SoftFailAbort, NOT raw exceptions)
4) V15HardFailAbort is a distinct type from V15SoftFailAbort
"""

from __future__ import annotations

import ast
import hashlib
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from agentic_core.L0_routing.types.guardian_contract_types import (
    V15HardFailAbort,
    V15SoftFailAbort,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
GATEWAY_PATH = PROJECT_ROOT / "agentic_core" / "L0_routing" / "enforcement" / "execution_gateway.py"
GATEWAY_SRC = GATEWAY_PATH.read_text(encoding="utf-8")
CONTRACT_PATH = PROJECT_ROOT / "agentic_core" / "L0_routing" / "types" / "guardian_contract.py"
CONTRACT_SRC = CONTRACT_PATH.read_text(encoding="utf-8")


# ===========================================================================
# A) Structural (AST) Tests
# ===========================================================================


class TestStructuralHardFail:
    """AST-level proof of deterministic HARD_FAIL abort surface."""

    def test_v15_hard_fail_abort_exists(self):
        assert "class V15HardFailAbort" in CONTRACT_SRC

    def test_v15_hard_fail_abort_is_exception(self):
        tree = ast.parse(CONTRACT_SRC)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "V15HardFailAbort":
                base_names = [b.id for b in node.bases if isinstance(b, ast.Name)]
                assert "Exception" in base_names
                return
        pytest.fail("V15HardFailAbort class not found")

    def test_gateway_imports_hard_fail_abort(self):
        assert "V15HardFailAbort" in GATEWAY_SRC

    def test_pipe_advance_raises_hard_fail_abort(self):
        """_pipe_advance must raise V15HardFailAbort, not bare 'raise'."""
        tree = ast.parse(GATEWAY_SRC)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "_pipe_advance":
                body = GATEWAY_SRC.splitlines()[node.lineno - 1 : node.end_lineno]
                body_text = "\n".join(body)
                assert "V15HardFailAbort" in body_text
                return
        pytest.fail("_pipe_advance not found")

    def test_policy_check_raises_hard_fail_abort(self):
        """_policy_check must raise V15HardFailAbort, not bare 'raise'."""
        tree = ast.parse(GATEWAY_SRC)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "_policy_check":
                body = GATEWAY_SRC.splitlines()[node.lineno - 1 : node.end_lineno]
                body_text = "\n".join(body)
                assert "V15HardFailAbort" in body_text
                return
        pytest.fail("_policy_check not found")

    def test_execute_does_not_catch_hard_fail_abort(self):
        """execute() must NOT catch V15HardFailAbort — only V15SoftFailAbort."""
        tree = ast.parse(GATEWAY_SRC)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "execute":
                body = GATEWAY_SRC.splitlines()[node.lineno - 1 : node.end_lineno]
                body_text = "\n".join(body)
                # Must catch SoftFailAbort
                assert "V15SoftFailAbort" in body_text
                # Must NOT catch HardFailAbort in execute (only in _execute_inner callers)
                # The except clause should reference SoftFailAbort, not HardFailAbort
                for child in ast.walk(node):
                    if isinstance(child, ast.ExceptHandler) and child.type is not None:
                        if isinstance(child.type, ast.Name):
                            assert child.type.id != "V15HardFailAbort", (
                                "execute() must not catch V15HardFailAbort"
                            )
                return
        pytest.fail("execute not found")


# ===========================================================================
# B) Type Distinction Tests
# ===========================================================================


class TestTypeSafety:
    """Prove HARD_FAIL and SOFT_FAIL abort types are distinct."""

    def test_hard_fail_abort_not_subclass_of_soft(self):
        assert not issubclass(V15HardFailAbort, V15SoftFailAbort)

    def test_soft_fail_abort_not_subclass_of_hard(self):
        assert not issubclass(V15SoftFailAbort, V15HardFailAbort)

    def test_hard_fail_abort_is_exception(self):
        assert issubclass(V15HardFailAbort, Exception)

    def test_soft_fail_abort_is_exception(self):
        assert issubclass(V15SoftFailAbort, Exception)

    def test_hard_fail_abort_carries_message(self):
        exc = V15HardFailAbort("test reason")
        assert "test reason" in str(exc)


# ===========================================================================
# C) Runtime Tests — Same Violation, Three Modes
# ===========================================================================


def _make_test_manifest():
    """Create a minimal valid SurgicalManifest."""
    from agentic_core.L0_routing.enforcement.traceability_contracts import generate_trace_id
    from agentic_core.L0_routing.types.determinism_types import FixConstraint, SurgicalManifest

    _hex8 = hashlib.sha256(b"test_hard_fail").hexdigest()[:8].upper()
    trace_id = generate_trace_id(_hex8)
    snippet = "test_hard_fail()"
    return SurgicalManifest(
        schema_version="1.0.0",
        correlation_id=trace_id,
        node_id="TestNode",
        target_layer="L0",
        ast_snippet=snippet,
        serialization_canon="test",
        fix_constraint=FixConstraint.RELAXED,
        manifest_hash=hashlib.sha256(snippet.encode()).hexdigest(),
        change_history=(),
        provenance_chain=(trace_id,),
    )


def _stub_heal(manifest):
    return {"status": "ok", "errors": 0}


def _stub_hashes():
    return (
        hashlib.sha256(b"fs").hexdigest(),
        hashlib.sha256(b"git").hexdigest(),
        hashlib.sha256(b"mem").hexdigest(),
    )


def _force_pipe_violation(gw):
    """Monkeypatch gateway to force a pipe order violation in _execute_inner."""
    from agentic_core.L0_routing.types.routing_contracts_types import PipeOrderEnforcer

    _orig_inner = gw._execute_inner

    def _patched(*args, **kwargs):
        pipe = PipeOrderEnforcer()
        gw._pipe_advance(pipe, "hash_verification", "test-trace")  # skip step 1
        return _orig_inner(*args, **kwargs)

    return _patched


class TestLogOnlyNoAbort:
    """V15_ENFORCEMENT=log: violation logged, no exception, normal return."""

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_pipe_violation_no_raise(self):
        from agentic_core.L0_routing.enforcement.execution_gateway import V15ExecutionGateway
        from agentic_core.L0_routing.types.routing_contracts_types import PipeOrderEnforcer

        gw = V15ExecutionGateway()
        pipe = PipeOrderEnforcer()
        # This should NOT raise — just log
        gw._pipe_advance(pipe, "hash_verification", "test-trace")
        # If we reach here, LOG_ONLY did not abort
        assert True

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_gateway_returns_normally(self):
        from agentic_core.L0_routing.enforcement.execution_gateway import V15ExecutionGateway

        gw = V15ExecutionGateway()
        manifest = _make_test_manifest()
        result = gw.execute(manifest, _stub_heal, _stub_hashes, trace_id=manifest.correlation_id)
        assert result.success is True


class TestSoftFailStructuredReturn:
    """V15_ENFORCEMENT=soft: violation returns GatewayResult failure, no raise out of execute()."""

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "soft"})
    def test_pipe_violation_returns_structured_failure(self):
        from agentic_core.L0_routing.enforcement.execution_gateway import V15ExecutionGateway

        gw = V15ExecutionGateway()
        manifest = _make_test_manifest()

        with patch.object(gw, "_execute_inner", _force_pipe_violation(gw)):
            result = gw.execute(manifest, _stub_heal, _stub_hashes, trace_id=manifest.correlation_id)

        assert result.success is False
        assert "SOFT_FAIL" in result.error
        # Must NOT be V15HardFailAbort
        assert "HARD_FAIL" not in result.error


class TestHardFailDeterministicAbort:
    """V15_ENFORCEMENT=1: violation raises V15HardFailAbort, not raw exceptions."""

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "1"})
    def test_pipe_violation_raises_hard_fail_abort(self):
        from agentic_core.L0_routing.enforcement.execution_gateway import V15ExecutionGateway
        from agentic_core.L0_routing.types.routing_contracts_types import PipeOrderEnforcer

        gw = V15ExecutionGateway()
        pipe = PipeOrderEnforcer()

        with pytest.raises(V15HardFailAbort) as exc_info:
            gw._pipe_advance(pipe, "hash_verification", "test-trace")

        assert "HARD_FAIL" in str(exc_info.value)
        assert "pipe_order_violation" in str(exc_info.value)

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "1"})
    def test_hard_fail_is_not_soft_fail(self):
        """Ensure HARD_FAIL raises V15HardFailAbort, NOT V15SoftFailAbort."""
        from agentic_core.L0_routing.enforcement.execution_gateway import V15ExecutionGateway
        from agentic_core.L0_routing.types.routing_contracts_types import PipeOrderEnforcer

        gw = V15ExecutionGateway()
        pipe = PipeOrderEnforcer()

        with pytest.raises(V15HardFailAbort):
            gw._pipe_advance(pipe, "hash_verification", "test-trace")

        # Confirm it's specifically NOT V15SoftFailAbort
        try:
            pipe2 = PipeOrderEnforcer()
            gw._pipe_advance(pipe2, "hash_verification", "test-trace")
            pytest.fail("Should have raised")
        except V15SoftFailAbort:
            pytest.fail("HARD_FAIL must not raise V15SoftFailAbort")
        except V15HardFailAbort:
            pass  # correct

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "1"})
    def test_hard_fail_not_raw_pipe_order_violation(self):
        """HARD_FAIL must raise V15HardFailAbort, NOT raw PipeOrderViolation."""
        from agentic_core.L0_routing.enforcement.execution_gateway import V15ExecutionGateway
        from agentic_core.L0_routing.types.routing_contracts_types import PipeOrderEnforcer, PipeOrderViolation

        gw = V15ExecutionGateway()
        pipe = PipeOrderEnforcer()

        try:
            gw._pipe_advance(pipe, "hash_verification", "test-trace")
            pytest.fail("Should have raised")
        except V15HardFailAbort:
            pass  # correct — deterministic type
        except PipeOrderViolation:
            pytest.fail("HARD_FAIL must raise V15HardFailAbort, not raw PipeOrderViolation")

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "1"})
    def test_hard_fail_propagates_through_execute(self):
        """V15HardFailAbort must propagate through execute() uncaught."""
        from agentic_core.L0_routing.enforcement.execution_gateway import V15ExecutionGateway

        gw = V15ExecutionGateway()
        manifest = _make_test_manifest()

        with patch.object(gw, "_execute_inner", _force_pipe_violation(gw)):
            with pytest.raises(V15HardFailAbort):
                gw.execute(manifest, _stub_heal, _stub_hashes, trace_id=manifest.correlation_id)

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "1"})
    def test_hard_fail_chains_original_cause(self):
        """V15HardFailAbort should chain the original violation as __cause__."""
        from agentic_core.L0_routing.enforcement.execution_gateway import V15ExecutionGateway
        from agentic_core.L0_routing.types.routing_contracts_types import PipeOrderEnforcer, PipeOrderViolation

        gw = V15ExecutionGateway()
        pipe = PipeOrderEnforcer()

        with pytest.raises(V15HardFailAbort) as exc_info:
            gw._pipe_advance(pipe, "hash_verification", "test-trace")

        assert exc_info.value.__cause__ is not None
        assert isinstance(exc_info.value.__cause__, PipeOrderViolation)
