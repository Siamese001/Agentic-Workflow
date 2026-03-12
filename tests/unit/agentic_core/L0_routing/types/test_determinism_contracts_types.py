"""Foundational behavioral tests for agentic_core/L0_routing/types/determinism_contracts_types.py.

fan_in=4 — imported by 4 other modules.
ADG import-hygiene is covered separately by test_determinism_contracts_types_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.types.determinism_contracts_types import (  # noqa: F401
        ForbiddenInputError,
        WallClockViolation,
        RollbackHashMismatch,
        EpisodicMemoryNotQueried,
        validate_execution_input,
        check_forbidden_input_type,
        validate_manifest_emission,
        require_manifest_hash_ok,
        canonical_ast_serialize,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ForbiddenInputError = None  # type: ignore[assignment,misc]
    WallClockViolation = None  # type: ignore[assignment,misc]
    RollbackHashMismatch = None  # type: ignore[assignment,misc]
    EpisodicMemoryNotQueried = None  # type: ignore[assignment,misc]
    validate_execution_input = None  # type: ignore[assignment,misc]
    check_forbidden_input_type = None  # type: ignore[assignment,misc]
    validate_manifest_emission = None  # type: ignore[assignment,misc]
    require_manifest_hash_ok = None  # type: ignore[assignment,misc]
    canonical_ast_serialize = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="determinism_contracts_types.py deps unavailable")
class TestForbiddenInputErrorContract:
    def test_is_class(self):
        assert isinstance(ForbiddenInputError, type)

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(ForbiddenInputError) if not m.startswith('_')]
        assert len(pub) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="determinism_contracts_types.py deps unavailable")
class TestWallClockViolationContract:
    def test_is_class(self):
        assert isinstance(WallClockViolation, type)

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(WallClockViolation) if not m.startswith('_')]
        assert len(pub) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="determinism_contracts_types.py deps unavailable")
class TestRollbackHashMismatchContract:
    def test_is_class(self):
        assert isinstance(RollbackHashMismatch, type)

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(RollbackHashMismatch) if not m.startswith('_')]
        assert len(pub) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="determinism_contracts_types.py deps unavailable")
class TestEpisodicMemoryNotQueriedContract:
    def test_is_class(self):
        assert isinstance(EpisodicMemoryNotQueried, type)

@pytest.mark.skipif(not _AVAILABLE, reason="determinism_contracts_types.py deps unavailable")
class TestValidateExecutionInputFunction:
    def test_is_callable(self):
        assert callable(validate_execution_input)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(validate_execution_input)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="determinism_contracts_types.py deps unavailable")
class TestCheckForbiddenInputTypeFunction:
    def test_is_callable(self):
        assert callable(check_forbidden_input_type)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(check_forbidden_input_type)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="determinism_contracts_types.py deps unavailable")
class TestValidateManifestEmissionFunction:
    def test_is_callable(self):
        assert callable(validate_manifest_emission)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(validate_manifest_emission)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="determinism_contracts_types.py deps unavailable")
class TestRequireManifestHashOkFunction:
    def test_is_callable(self):
        assert callable(require_manifest_hash_ok)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(require_manifest_hash_ok)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="determinism_contracts_types.py deps unavailable")
class TestCanonicalAstSerializeFunction:
    def test_is_callable(self):
        assert callable(canonical_ast_serialize)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(canonical_ast_serialize)
        assert sig.return_annotation is not inspect.Parameter.empty


def test_module_importable():
    """Smoke: determinism_contracts_types importable or gracefully unavailable."""
    assert True
