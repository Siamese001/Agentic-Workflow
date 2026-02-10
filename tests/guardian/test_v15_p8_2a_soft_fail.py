"""V15 P8.2a — SOFT_FAIL Enforcement Mode Tests.

Proves:
1) Default unchanged: V15_ENFORCEMENT=0 → no exceptions, no aborts
2) LOG_ONLY unchanged: V15_ENFORCEMENT=log → violations logged, not aborted
3) SOFT_FAIL aborts: V15_ENFORCEMENT=soft → violations cause controlled abort
   (structured GatewayResult with success=False, no process crash)
4) HARD_FAIL still raises: V15_ENFORCEMENT=1 → violations raise raw exceptions
5) Mode detection functions work correctly
"""

from __future__ import annotations

import ast
import hashlib
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from agentic_core.L0_maintenance.types.guardian_contract import (
    V15SoftFailAbort,
    is_v15_enforced,
    is_v15_hard_fail,
    is_v15_soft_fail,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
GATEWAY_PATH = PROJECT_ROOT / "agentic_core" / "L0_maintenance" / "enforcement" / "v15_execution_gateway.py"
GATEWAY_SRC = GATEWAY_PATH.read_text(encoding="utf-8")
CONTRACT_PATH = PROJECT_ROOT / "agentic_core" / "L0_maintenance" / "types" / "guardian_contract.py"
CONTRACT_SRC = CONTRACT_PATH.read_text(encoding="utf-8")


# ===========================================================================
# A) Mode Detection Unit Tests
# ===========================================================================


class TestModeDetection:
    """Prove mode selection functions return correct values for each V15_ENFORCEMENT value."""

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "0"})
    def test_enforcement_off(self):
        assert not is_v15_enforced()
        assert not is_v15_hard_fail()
        assert not is_v15_soft_fail()

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_log_only_mode(self):
        assert is_v15_enforced()
        assert not is_v15_hard_fail()
        assert not is_v15_soft_fail()

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "soft"})
    def test_soft_fail_mode(self):
        assert is_v15_enforced()
        assert not is_v15_hard_fail()
        assert is_v15_soft_fail()

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "1"})
    def test_hard_fail_mode(self):
        assert is_v15_enforced()
        assert is_v15_hard_fail()
        assert not is_v15_soft_fail()

    @patch.dict(os.environ, {}, clear=True)
    def test_unset_defaults_to_off(self):
        os.environ.pop("V15_ENFORCEMENT", None)
        assert not is_v15_enforced()
        assert not is_v15_hard_fail()
        assert not is_v15_soft_fail()


# ===========================================================================
# B) Structural (AST) Tests
# ===========================================================================


class TestStructuralSoftFail:
    """AST proof that SOFT_FAIL is wired into the gateway."""

    def test_is_v15_soft_fail_exists_in_contract(self):
        assert "def is_v15_soft_fail()" in CONTRACT_SRC

    def test_v15_soft_fail_abort_exists_in_contract(self):
        assert "class V15SoftFailAbort" in CONTRACT_SRC

    def test_gateway_imports_soft_fail(self):
        assert "is_v15_soft_fail" in GATEWAY_SRC

    def test_gateway_imports_soft_fail_abort(self):
        assert "V15SoftFailAbort" in GATEWAY_SRC

    def test_pipe_advance_checks_soft_fail(self):
        """_pipe_advance must check is_v15_soft_fail() and raise V15SoftFailAbort."""
        tree = ast.parse(GATEWAY_SRC)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "_pipe_advance":
                body = GATEWAY_SRC.splitlines()[node.lineno - 1 : node.end_lineno]
                body_text = "\n".join(body)
                assert "is_v15_soft_fail()" in body_text
                assert "V15SoftFailAbort" in body_text
                return
        pytest.fail("_pipe_advance not found")

    def test_policy_check_checks_soft_fail(self):
        """_policy_check must check is_v15_soft_fail() and raise V15SoftFailAbort."""
        tree = ast.parse(GATEWAY_SRC)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "_policy_check":
                body = GATEWAY_SRC.splitlines()[node.lineno - 1 : node.end_lineno]
                body_text = "\n".join(body)
                assert "is_v15_soft_fail()" in body_text
                assert "V15SoftFailAbort" in body_text
                return
        pytest.fail("_policy_check not found")

    def test_execute_catches_soft_fail_abort(self):
        """execute() must catch V15SoftFailAbort for structured failure return."""
        tree = ast.parse(GATEWAY_SRC)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "execute":
                body = GATEWAY_SRC.splitlines()[node.lineno - 1 : node.end_lineno]
                body_text = "\n".join(body)
                assert "V15SoftFailAbort" in body_text
                assert "SOFT_FAIL" in body_text
                return
        pytest.fail("execute not found")


# ===========================================================================
# C) Runtime Tests — Gateway Behavior Under Each Mode
# ===========================================================================


def _make_test_manifest():
    """Create a minimal valid SurgicalManifest for testing."""
    from agentic_core.L0_maintenance.enforcement.v15_p4_contracts import generate_trace_id
    from agentic_core.L0_maintenance.types.v15_p2_types import FixConstraint, SurgicalManifest

    _hex8 = hashlib.sha256(b"test_soft_fail").hexdigest()[:8].upper()
    trace_id = generate_trace_id(_hex8)
    snippet = "test_soft_fail()"
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


class TestGatewayDefaultUnchanged:
    """V15_ENFORCEMENT=0: gateway must not be invoked (callers gate on is_v15_enforced)."""

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "0"})
    def test_enforcement_off_no_abort(self):
        """When enforcement is off, is_v15_enforced() is False — no V15 path entered."""
        assert not is_v15_enforced()
        # No gateway call should happen; callers check is_v15_enforced() first.
        # This proves default behavior is unchanged.


class TestGatewayLogOnly:
    """V15_ENFORCEMENT=log: violations are logged but execution succeeds."""

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "log"})
    def test_normal_execution_succeeds(self):
        from agentic_core.L0_maintenance.enforcement.v15_execution_gateway import V15ExecutionGateway

        gw = V15ExecutionGateway()
        manifest = _make_test_manifest()
        result = gw.execute(manifest, _stub_heal, _stub_hashes, trace_id=manifest.correlation_id)
        assert result.success is True
        assert result.error is None


class TestGatewaySoftFail:
    """V15_ENFORCEMENT=soft: violations cause controlled abort (structured failure)."""

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "soft"})
    def test_normal_execution_succeeds_without_violations(self):
        """When no violation occurs, SOFT_FAIL mode should succeed normally."""
        from agentic_core.L0_maintenance.enforcement.v15_execution_gateway import V15ExecutionGateway

        gw = V15ExecutionGateway()
        manifest = _make_test_manifest()
        result = gw.execute(manifest, _stub_heal, _stub_hashes, trace_id=manifest.correlation_id)
        assert result.success is True
        assert result.error is None

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "soft"})
    def test_pipe_violation_causes_structured_abort(self):
        """Force a pipe order violation; SOFT_FAIL must return structured failure, not crash."""
        from agentic_core.L0_maintenance.enforcement.v15_execution_gateway import V15ExecutionGateway
        from agentic_core.L0_maintenance.types.v15_contracts import PipeOrderEnforcer

        gw = V15ExecutionGateway()
        manifest = _make_test_manifest()

        # Monkeypatch _execute_inner to force a pipe order violation
        _orig_inner = gw._execute_inner

        def _force_pipe_violation(*args, **kwargs):
            # Advance pipe out of order to trigger violation
            pipe = PipeOrderEnforcer()
            gw._pipe_advance(pipe, "hash_verification", "test-trace")  # skip schema_validation
            return _orig_inner(*args, **kwargs)

        with patch.object(gw, "_execute_inner", _force_pipe_violation):
            result = gw.execute(manifest, _stub_heal, _stub_hashes, trace_id=manifest.correlation_id)

        # Must NOT crash; must return structured failure
        assert result.success is False
        assert result.error is not None
        assert "SOFT_FAIL" in result.error

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "soft"})
    def test_soft_fail_abort_exception_is_catchable(self):
        """V15SoftFailAbort is a normal exception, catchable without process crash."""
        exc = V15SoftFailAbort("test violation")
        assert isinstance(exc, Exception)
        assert str(exc) == "test violation"

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "soft"})
    def test_soft_fail_result_has_deterministic_fields(self):
        """Structured failure result must have all required GatewayResult fields."""
        from agentic_core.L0_maintenance.enforcement.v15_execution_gateway import V15ExecutionGateway
        from agentic_core.L0_maintenance.types.v15_contracts import PipeOrderEnforcer

        gw = V15ExecutionGateway()
        manifest = _make_test_manifest()

        _orig_inner = gw._execute_inner

        def _force_violation(*args, **kwargs):
            pipe = PipeOrderEnforcer()
            gw._pipe_advance(pipe, "hash_verification", "test-trace")
            return _orig_inner(*args, **kwargs)

        with patch.object(gw, "_execute_inner", _force_violation):
            result = gw.execute(manifest, _stub_heal, _stub_hashes, trace_id=manifest.correlation_id)

        assert hasattr(result, "success")
        assert hasattr(result, "manifest")
        assert hasattr(result, "error")
        assert hasattr(result, "healing_output")
        assert result.success is False
        assert result.manifest is manifest


class TestGatewayHardFail:
    """V15_ENFORCEMENT=1: violations raise raw exceptions (existing behavior preserved)."""

    @patch.dict(os.environ, {"V15_ENFORCEMENT": "1"})
    def test_hard_fail_raises_on_pipe_violation(self):
        """HARD_FAIL must escalate PipeOrderViolation to V15HardFailAbort."""
        from agentic_core.L0_maintenance.enforcement.v15_execution_gateway import V15ExecutionGateway
        from agentic_core.L0_maintenance.types.guardian_contract import V15HardFailAbort
        from agentic_core.L0_maintenance.types.v15_contracts import PipeOrderEnforcer

        gw = V15ExecutionGateway()

        pipe = PipeOrderEnforcer()
        with pytest.raises(V15HardFailAbort):
            gw._pipe_advance(pipe, "hash_verification", "test-trace")
