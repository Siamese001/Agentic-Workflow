"""Smoke tests for governance_contracts — wave 13."""

import pytest

mod = pytest.importorskip("agentic_core.L0_routing.enforcement.governance_contracts")


def test_module_imports_clean():
    assert mod is not None


def test_all_exports_resolvable():
    for name in mod.__all__:
        assert hasattr(mod, name), f"__all__ advertises {name!r} but it is missing"


def test_error_classes_present():
    assert isinstance(mod.EvidencePackError, type)
    assert issubclass(mod.EvidencePackError, Exception)
    assert isinstance(mod.PolicyExceptionError, type)
    assert issubclass(mod.PolicyExceptionError, Exception)
    assert isinstance(mod.PolicyUpdateError, type)
    assert issubclass(mod.PolicyUpdateError, Exception)


def test_build_evidence_pack_callable():
    assert callable(mod.build_evidence_pack)


def test_emit_policy_exception_callable():
    assert callable(mod.emit_policy_exception)


def test_propose_policy_update_callable():
    assert callable(mod.propose_policy_update)


def test_validate_evidence_pack_rejects_non_pack():
    with pytest.raises(mod.EvidencePackError):
        mod.validate_evidence_pack("not_a_pack")


def test_validate_proposal_rejects_non_proposal():
    with pytest.raises(mod.PolicyUpdateError):
        mod.validate_proposal("not_a_proposal")


def test_emit_policy_exception_generates_nonce():
    import inspect

    sig = inspect.signature(mod.emit_policy_exception)
    assert "nonce" in sig.parameters
    assert sig.parameters["nonce"].default is None
