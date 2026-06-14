"""Unit tests for agentic_core.L5_safety.exceptions.

Wave 6.1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — P2 untested-module
coverage. Validates the L5 certification exception hierarchy: subclass
relationships, raise/catch via base, __all__ membership, and message-carrying
instantiation. Pure surface only — no live deps, no mocks.
"""
from __future__ import annotations

import pytest

from agentic_core.L5_safety import exceptions as exc_mod
from agentic_core.L5_safety.exceptions import (
    L5AuthorityWideningError,
    L5CertificationError,
    L5DigestMismatchError,
    L5MalformedReceiptError,
)

_SUBCLASSES = (
    L5AuthorityWideningError,
    L5DigestMismatchError,
    L5MalformedReceiptError,
)


class TestHierarchy:
    def test_base_is_exception_subclass(self) -> None:
        assert issubclass(L5CertificationError, Exception)

    @pytest.mark.parametrize("cls", _SUBCLASSES)
    def test_subclasses_inherit_base(self, cls: type) -> None:
        assert issubclass(cls, L5CertificationError)

    @pytest.mark.parametrize("cls", _SUBCLASSES)
    def test_subclasses_are_exceptions(self, cls: type) -> None:
        assert issubclass(cls, Exception)

    def test_subclasses_are_distinct(self) -> None:
        assert not issubclass(L5DigestMismatchError, L5AuthorityWideningError)
        assert not issubclass(L5AuthorityWideningError, L5MalformedReceiptError)


class TestRaiseCatch:
    @pytest.mark.parametrize("cls", _SUBCLASSES)
    def test_caught_via_base(self, cls: type) -> None:
        with pytest.raises(L5CertificationError):
            raise cls("boom")

    @pytest.mark.parametrize("cls", _SUBCLASSES)
    def test_caught_via_own_type(self, cls: type) -> None:
        with pytest.raises(cls):
            raise cls("boom")

    def test_base_not_caught_as_subclass(self) -> None:
        with pytest.raises(L5CertificationError):
            try:
                raise L5CertificationError("base")
            except L5AuthorityWideningError:  # pragma: no cover - must not match
                pytest.fail("base should not match subclass handler")


class TestInstantiation:
    @pytest.mark.parametrize(
        "cls",
        (L5CertificationError, *_SUBCLASSES),
    )
    def test_message_roundtrips(self, cls: type) -> None:
        err = cls("specific reason")
        assert str(err) == "specific reason"
        assert err.args == ("specific reason",)

    def test_no_arg_instantiation(self) -> None:
        err = L5CertificationError()
        assert str(err) == ""


class TestAll:
    def test_all_membership(self) -> None:
        assert set(exc_mod.__all__) == {
            "L5CertificationError",
            "L5AuthorityWideningError",
            "L5DigestMismatchError",
            "L5MalformedReceiptError",
        }

    @pytest.mark.parametrize(
        "name",
        (
            "L5CertificationError",
            "L5AuthorityWideningError",
            "L5DigestMismatchError",
            "L5MalformedReceiptError",
        ),
    )
    def test_all_names_exported(self, name: str) -> None:
        assert name in exc_mod.__all__
        assert hasattr(exc_mod, name)
