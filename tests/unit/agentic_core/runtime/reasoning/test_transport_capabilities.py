"""Wave 6.1 P2 hotspot tests — agentic_core.runtime.reasoning.transport_capabilities.

Covers the frozen+slots TransportCapabilities dataclass and its
``from_provider`` static factory across every branch: provider exposing
``reasoning_transport_kw_forwarded`` returning a frozenset / set / list /
tuple / None / missing / non-callable. No live providers — a tiny local stub
exposes the attribute under test.
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.runtime.reasoning.transport_capabilities import TransportCapabilities


class _Provider:
    """Local stub exposing reasoning_transport_kw_forwarded as a callable."""

    def __init__(self, value):
        self._value = value

    def reasoning_transport_kw_forwarded(self):
        return self._value


class _ProviderNonCallableAttr:
    """Stub where the attribute exists but is not callable."""

    reasoning_transport_kw_forwarded = frozenset({"temperature"})


class _ProviderNoAttr:
    """Stub with no transport-capability attribute at all."""


class TestConstructionAndDefaults:
    def test_construct_with_frozenset(self) -> None:
        cap = TransportCapabilities(frozenset({"temperature", "top_p"}))
        assert cap.forwarded_kw_names == frozenset({"temperature", "top_p"})

    def test_is_frozen(self) -> None:
        cap = TransportCapabilities(frozenset({"a"}))
        with pytest.raises(dataclasses.FrozenInstanceError):
            cap.forwarded_kw_names = frozenset({"b"})  # type: ignore[misc]

    def test_has_slots(self) -> None:
        cap = TransportCapabilities(frozenset())
        assert not hasattr(cap, "__dict__")

    def test_equality_by_value(self) -> None:
        a = TransportCapabilities(frozenset({"x"}))
        b = TransportCapabilities(frozenset({"x"}))
        assert a == b


class TestFromProvider:
    def test_frozenset_passed_through_identically(self) -> None:
        fs = frozenset({"temperature", "max_tokens"})
        cap = TransportCapabilities.from_provider(_Provider(fs))
        assert cap.forwarded_kw_names == fs
        assert isinstance(cap.forwarded_kw_names, frozenset)

    @pytest.mark.parametrize(
        "value",
        [
            {"temperature", "top_p"},
            ["temperature", "top_p"],
            ("temperature", "top_p"),
        ],
    )
    def test_set_list_tuple_coerced_to_frozenset(self, value) -> None:
        cap = TransportCapabilities.from_provider(_Provider(value))
        assert cap.forwarded_kw_names == frozenset({"temperature", "top_p"})
        assert isinstance(cap.forwarded_kw_names, frozenset)

    def test_list_elements_stringified(self) -> None:
        cap = TransportCapabilities.from_provider(_Provider([1, 2, 3]))
        assert cap.forwarded_kw_names == frozenset({"1", "2", "3"})

    def test_none_returns_empty(self) -> None:
        cap = TransportCapabilities.from_provider(_Provider(None))
        assert cap.forwarded_kw_names == frozenset()

    def test_missing_attribute_returns_empty(self) -> None:
        cap = TransportCapabilities.from_provider(_ProviderNoAttr())
        assert cap.forwarded_kw_names == frozenset()

    def test_non_callable_attribute_returns_empty(self) -> None:
        cap = TransportCapabilities.from_provider(_ProviderNonCallableAttr())
        assert cap.forwarded_kw_names == frozenset()

    def test_unexpected_type_returns_empty(self) -> None:
        # A getter returning e.g. an int is not frozenset/set/list/tuple → empty.
        cap = TransportCapabilities.from_provider(_Provider(42))
        assert cap.forwarded_kw_names == frozenset()

    def test_empty_collection_returns_empty(self) -> None:
        cap = TransportCapabilities.from_provider(_Provider([]))
        assert cap.forwarded_kw_names == frozenset()
