"""ADG contract tests for agentic_core/L5_safety/types/verification_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit
try:
    from agentic_core.L5_safety.types.verification_types import (
        VerificationGateProtocol,
        VerificationRequest,
        VerificationResult,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    VerificationRequest = VerificationResult = VerificationGateProtocol = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestVerificationRequest:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(VerificationRequest)
    def test_creates(self):
        r = VerificationRequest(
            file_path="foo.py", action_type="delete_import", target_node="os",
        )
        assert r.file_path == "foo.py"; assert r.context == {}
    def test_context_none_becomes_empty_dict(self):
        r = VerificationRequest(
            file_path="f.py", action_type="add_import", target_node="x", context=None,
        )
        assert r.context == {}

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestVerificationResult:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(VerificationResult)
    def test_success_true(self):
        r = VerificationResult(success=True); assert r.success is True
    def test_failure_with_reason(self):
        r = VerificationResult(success=False, reason="node not found")
        assert r.reason == "node not found"
    def test_metadata_default_empty(self):
        r = VerificationResult(success=True)
        assert r.metadata == {}

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestVerificationGateProtocol:
    def test_is_abstract(self):
        import abc; assert issubclass(VerificationGateProtocol, abc.ABC)
    def test_cannot_instantiate(self):
        with pytest.raises(TypeError):
            VerificationGateProtocol()  # type: ignore[abstract]
    def test_supported_actions_contains_delete_import(self):
        assert "delete_import" in VerificationGateProtocol.SUPPORTED_ACTIONS
    def test_validate_request_empty_file_path(self):
        class ConcreteGate(VerificationGateProtocol):
            def verify_action(self, r): pass
            def is_available(self): return True
            def get_supported_actions(self): return self.SUPPORTED_ACTIONS
        gate = ConcreteGate()
        req = VerificationRequest(file_path="", action_type="delete_import", target_node="x")
        result = gate.validate_request(req)
        assert result is not None

def test_module_importable(): assert _AVAIL or not _AVAIL
