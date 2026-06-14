"""Wave 4.2 — apps_rg untested-hotspot coverage.

Covers ``apps_rg/types/AllProvidersDownError.py``: the provider-exhaustion
exception plus the lightweight ``HardenedRouter`` circuit-reset façade.
"""
from __future__ import annotations

import pytest

from apps_rg.types.AllProvidersDownError import (
    AllProvidersDownError,
    HardenedRouter,
    __all__ as module_all,
)


class TestAllProvidersDownError:
    def test_is_exception_subclass(self) -> None:
        assert issubclass(AllProvidersDownError, Exception)

    def test_default_message(self) -> None:
        err = AllProvidersDownError()
        assert str(err) == "all providers exhausted"

    def test_custom_message(self) -> None:
        err = AllProvidersDownError("lane X rejected")
        assert str(err) == "lane X rejected"

    def test_accepts_arbitrary_kwargs(self) -> None:
        # Extra kwargs are swallowed (historical router-contract compat).
        err = AllProvidersDownError("boom", provider="claude", attempts=3)
        assert str(err) == "boom"

    def test_raisable_and_catchable(self) -> None:
        with pytest.raises(AllProvidersDownError):
            raise AllProvidersDownError()


class TestHardenedRouter:
    def test_reset_all_circuit_breakers_returns_none(self) -> None:
        assert HardenedRouter().reset_all_circuit_breakers() is None

    def test_get_provider_health_empty_dict(self) -> None:
        health = HardenedRouter().get_provider_health()
        assert health == {}
        assert isinstance(health, dict)

    def test_distinct_instances(self) -> None:
        assert HardenedRouter() is not HardenedRouter()


def test_module_exports() -> None:
    assert set(module_all) == {"AllProvidersDownError", "HardenedRouter"}
