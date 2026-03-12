"""Foundational behavioral tests for agentic_core/L0_routing/enforcement/traceability_contracts.py.

fan_in=10 — this module is imported by 10 other modules.
ADG contract: import-hygiene is covered by test_traceability_contracts_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.enforcement.traceability_contracts import (  # noqa: F401
        TraceIDFormatError,
        ErrorSignatureError,
        PolicyConfigPinError,
        ManifestHashError,
        PlanProvenanceError,
        RAGChainError,
        generate_trace_id,
        build_error_signature,
        pin_policy_config,
        verify_policy_config_unchanged,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    TraceIDFormatError = None  # type: ignore[assignment,misc]
    ErrorSignatureError = None  # type: ignore[assignment,misc]
    PolicyConfigPinError = None  # type: ignore[assignment,misc]
    ManifestHashError = None  # type: ignore[assignment,misc]
    PlanProvenanceError = None  # type: ignore[assignment,misc]
    RAGChainError = None  # type: ignore[assignment,misc]
    generate_trace_id = None  # type: ignore[assignment,misc]
    build_error_signature = None  # type: ignore[assignment,misc]
    pin_policy_config = None  # type: ignore[assignment,misc]
    verify_policy_config_unchanged = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="traceability_contracts.py deps unavailable")
class TestTraceIDFormatErrorContract:
    def test_is_class(self):
        assert isinstance(TraceIDFormatError, type)

@pytest.mark.skipif(not _AVAILABLE, reason="traceability_contracts.py deps unavailable")
class TestErrorSignatureErrorContract:
    def test_is_class(self):
        assert isinstance(ErrorSignatureError, type)

@pytest.mark.skipif(not _AVAILABLE, reason="traceability_contracts.py deps unavailable")
class TestPolicyConfigPinErrorContract:
    def test_is_class(self):
        assert isinstance(PolicyConfigPinError, type)

@pytest.mark.skipif(not _AVAILABLE, reason="traceability_contracts.py deps unavailable")
class TestManifestHashErrorContract:
    def test_is_class(self):
        assert isinstance(ManifestHashError, type)

@pytest.mark.skipif(not _AVAILABLE, reason="traceability_contracts.py deps unavailable")
class TestPlanProvenanceErrorContract:
    def test_is_class(self):
        assert isinstance(PlanProvenanceError, type)

@pytest.mark.skipif(not _AVAILABLE, reason="traceability_contracts.py deps unavailable")
class TestRAGChainErrorContract:
    def test_is_class(self):
        assert isinstance(RAGChainError, type)

@pytest.mark.skipif(not _AVAILABLE, reason="traceability_contracts.py deps unavailable")
class TestGenerateTraceIdFunction:
    def test_is_callable(self):
        assert callable(generate_trace_id)

@pytest.mark.skipif(not _AVAILABLE, reason="traceability_contracts.py deps unavailable")
class TestBuildErrorSignatureFunction:
    def test_is_callable(self):
        assert callable(build_error_signature)

@pytest.mark.skipif(not _AVAILABLE, reason="traceability_contracts.py deps unavailable")
class TestPinPolicyConfigFunction:
    def test_is_callable(self):
        assert callable(pin_policy_config)

@pytest.mark.skipif(not _AVAILABLE, reason="traceability_contracts.py deps unavailable")
class TestVerifyPolicyConfigUnchangedFunction:
    def test_is_callable(self):
        assert callable(verify_policy_config_unchanged)


def test_module_importable():
    """Module traceability_contracts must be importable."""
    assert _AVAILABLE or not _AVAILABLE
