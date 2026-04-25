"""Smoke tests for proof_of_ledger — wave 31."""

import pytest

mod = pytest.importorskip("agentic_core.L4_state.enforcement.proof_of_ledger")


def test_module_imports_clean():
    assert mod is not None


def test_ProofOfLedger_class_present():
    assert hasattr(mod, "ProofOfLedger")
    assert isinstance(mod.ProofOfLedger, type)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
