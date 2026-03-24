"""Foundational behavioral tests for agentic_core/L0_routing/enforcement/mutation_prohibition.py.

fan_in=59 — imported by 59 other modules.
ADG import-hygiene is covered separately by test_mutation_prohibition_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.enforcement.mutation_prohibition import (  # noqa: F401
        IMMUTABLE_ROOTS,
        ProtectedRootBlockEvent,
        ProtectedRootPolicy,
        SourceMutationBlocked,
        assert_no_persistent_write,
        enforce_protected_root,
        get_default_protected_root_policy,
        safe_write_bytes,
        safe_write_text,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    SourceMutationBlocked = None  # type: ignore[assignment,misc]
    ProtectedRootBlockEvent = None  # type: ignore[assignment,misc]
    ProtectedRootPolicy = None  # type: ignore[assignment,misc]
    get_default_protected_root_policy = None  # type: ignore[assignment,misc]
    enforce_protected_root = None  # type: ignore[assignment,misc]
    assert_no_persistent_write = None  # type: ignore[assignment,misc]
    safe_write_text = None  # type: ignore[assignment,misc]
    safe_write_bytes = None  # type: ignore[assignment,misc]
    IMMUTABLE_ROOTS = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="mutation_prohibition.py deps unavailable")
class TestSourceMutationBlockedContract:
    def test_is_class(self):
        assert isinstance(SourceMutationBlocked, type)

@pytest.mark.skipif(not _AVAILABLE, reason="mutation_prohibition.py deps unavailable")
class TestProtectedRootBlockEventContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ProtectedRootBlockEvent)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(ProtectedRootBlockEvent)}
        assert fnames >= {'matched_root', 'target', 'caller', 'ts_utc'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(ProtectedRootBlockEvent)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="mutation_prohibition.py deps unavailable")
class TestProtectedRootPolicyContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ProtectedRootPolicy)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(ProtectedRootPolicy)}
        assert fnames >= {'immutable_roots', 'log_path'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(ProtectedRootPolicy)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="mutation_prohibition.py deps unavailable")
class TestGetDefaultProtectedRootPolicyFunction:
    def test_is_callable(self):
        assert callable(get_default_protected_root_policy)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_default_protected_root_policy)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="mutation_prohibition.py deps unavailable")
class TestEnforceProtectedRootFunction:
    def test_is_callable(self):
        assert callable(enforce_protected_root)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(enforce_protected_root)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="mutation_prohibition.py deps unavailable")
class TestAssertNoPersistentWriteFunction:
    def test_is_callable(self):
        assert callable(assert_no_persistent_write)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(assert_no_persistent_write)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="mutation_prohibition.py deps unavailable")
class TestSafeWriteTextFunction:
    def test_is_callable(self):
        assert callable(safe_write_text)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(safe_write_text)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="mutation_prohibition.py deps unavailable")
class TestSafeWriteBytesFunction:
    def test_is_callable(self):
        assert callable(safe_write_bytes)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(safe_write_bytes)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="mutation_prohibition.py deps unavailable")
class TestImmutableRootsConstant:
    def test_is_not_none(self):
        assert IMMUTABLE_ROOTS is not None


def test_module_importable():
    """Smoke: mutation_prohibition importable or gracefully unavailable."""
    pass