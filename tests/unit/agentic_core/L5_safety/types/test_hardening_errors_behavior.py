"""Behavioral tests for agentic_core.L5_safety.types.hardening_errors.

Pure exception-marker module (9 RuntimeError subclasses gating Master
Hardening Consolidation Addendum violations). Tests verify:
  - Each class is a distinct type and a RuntimeError subclass (so callers
    catching `RuntimeError` still catch them — failure-contract stability)
  - Raising / catching / message propagation works
  - `__all__` exports every exception class

L5 is a ×2.0 criticality layer. Module ranked in top-10 by fan-in (7) in the
Stage 1 risk-weighted gap report.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def he():
    return pytest.importorskip("agentic_core.L5_safety.types.hardening_errors")


ERROR_CLASS_NAMES = [
    "ExecutionTraceIntegrityError",
    "MutationReplayIntegrityViolation",
    "LedgerIntegrityViolation",
    "MutationCommitFailure",
    "C0AuthorityLeakError",
    "C0MutationViolation",
    "RuntimePolicyMutationViolation",
    "HumanPatchValidationError",
    "HumanPatchL5ClearanceError",
]


# --------------------------------------------------------------------------- #
# Public surface                                                              #
# --------------------------------------------------------------------------- #


class TestPublicSurface:
    @pytest.mark.parametrize("name", ERROR_CLASS_NAMES)
    def test_all_exports_present(self, he, name):
        assert name in he.__all__, f"{name} missing from __all__"

    def test_all_has_no_extra_entries(self, he):
        assert set(he.__all__) == set(ERROR_CLASS_NAMES)

    @pytest.mark.parametrize("name", ERROR_CLASS_NAMES)
    def test_class_is_importable_by_name(self, he, name):
        cls = getattr(he, name, None)
        assert isinstance(cls, type), f"{name} is not a class"


# --------------------------------------------------------------------------- #
# Inheritance contract                                                        #
# --------------------------------------------------------------------------- #


class TestInheritanceContract:
    @pytest.mark.parametrize("name", ERROR_CLASS_NAMES)
    def test_is_runtime_error_subclass(self, he, name):
        cls = getattr(he, name)
        assert issubclass(cls, RuntimeError), (
            f"{name} must inherit RuntimeError so legacy `except RuntimeError` handlers still catch it"
        )

    @pytest.mark.parametrize("name", ERROR_CLASS_NAMES)
    def test_is_exception_subclass(self, he, name):
        cls = getattr(he, name)
        assert issubclass(cls, Exception)

    def test_distinct_classes(self, he):
        classes = [getattr(he, n) for n in ERROR_CLASS_NAMES]
        assert len(set(classes)) == len(classes), "each hardening error must be a distinct type"


# --------------------------------------------------------------------------- #
# Raise / catch behavior                                                      #
# --------------------------------------------------------------------------- #


class TestRaiseAndCatch:
    @pytest.mark.parametrize("name", ERROR_CLASS_NAMES)
    def test_can_raise_with_message(self, he, name):
        cls = getattr(he, name)
        with pytest.raises(cls) as exc_info:
            raise cls("addendum-violation-detail")
        assert str(exc_info.value) == "addendum-violation-detail"

    @pytest.mark.parametrize("name", ERROR_CLASS_NAMES)
    def test_can_raise_without_message(self, he, name):
        cls = getattr(he, name)
        with pytest.raises(cls):
            raise cls()

    @pytest.mark.parametrize("name", ERROR_CLASS_NAMES)
    def test_caught_by_runtime_error(self, he, name):
        cls = getattr(he, name)
        with pytest.raises(RuntimeError):
            raise cls("x")

    @pytest.mark.parametrize("name", ERROR_CLASS_NAMES)
    def test_caught_by_exception(self, he, name):
        cls = getattr(he, name)
        with pytest.raises(Exception):  # noqa: PT011 - intentionally broad
            raise cls("x")

    def test_cross_class_does_not_catch(self, he):
        """A MutationCommitFailure must not be caught as a LedgerIntegrityViolation."""
        with pytest.raises(he.MutationCommitFailure):
            try:
                raise he.MutationCommitFailure("commit failed")
            except he.LedgerIntegrityViolation:
                pytest.fail("wrong handler caught MutationCommitFailure")

    def test_chained_exception_preserves_cause(self, he):
        original = ValueError("original")
        try:
            try:
                raise original
            except ValueError as exc:
                raise he.MutationReplayIntegrityViolation("replay mismatch") from exc
        except he.MutationReplayIntegrityViolation as caught:
            assert caught.__cause__ is original
            assert str(caught) == "replay mismatch"


# --------------------------------------------------------------------------- #
# Docstrings present (documentation-as-contract)                              #
# --------------------------------------------------------------------------- #


class TestDocumentedContract:
    @pytest.mark.parametrize("name", ERROR_CLASS_NAMES)
    def test_has_docstring_referencing_addendum(self, he, name):
        cls = getattr(he, name)
        assert cls.__doc__ is not None, f"{name} has no docstring"
        # Each error documents its addendum section (loose check).
        assert "Addendum" in cls.__doc__, (
            f"{name} docstring should reference the Addendum section it enforces"
        )
