"""Tests for L0 composition_root evidence resolver wiring.

Covers:
* Default fail-closed behavior when no app resolver registered
* register_evidence_source delegation
* SEMANTIC_CACHE_FAIL_OPEN_RESOLVER rollback flag
* Resolver-raised exceptions are swallowed and treated as unresolved
* Idempotent install (second install_default_resolvers is a no-op)
"""

from __future__ import annotations

import importlib

import pytest


@pytest.fixture
def composition_root_module(monkeypatch):
    """Reload composition_root with a clean state for each test."""
    monkeypatch.delenv("SEMANTIC_CACHE_FAIL_OPEN_RESOLVER", raising=False)
    from agentic_core.L0_routing import composition_root  # noqa: PLC0415

    importlib.reload(composition_root)
    yield composition_root
    composition_root.clear_evidence_source()


def test_default_resolver_is_fail_closed(composition_root_module):
    """No registered source ⇒ every id treated as unresolved."""
    assert composition_root_module._composed_resolver("any-id") is False


def test_register_source_delegates(composition_root_module):
    """Registered resolver controls the answer."""
    composition_root_module.register_evidence_source(lambda eid: eid == "good")
    assert composition_root_module._composed_resolver("good") is True
    assert composition_root_module._composed_resolver("bad") is False


def test_clear_source_reverts_to_default(composition_root_module):
    composition_root_module.register_evidence_source(lambda _: True)
    assert composition_root_module._composed_resolver("x") is True
    composition_root_module.clear_evidence_source()
    assert composition_root_module._composed_resolver("x") is False


def test_resolver_raise_is_swallowed_as_unresolved(composition_root_module):
    def boom(_eid: str) -> bool:
        raise RuntimeError("downstream evidence store unreachable")

    composition_root_module.register_evidence_source(boom)
    assert composition_root_module._composed_resolver("x") is False


def test_fail_open_rollback_flag(monkeypatch, composition_root_module):
    monkeypatch.setenv("SEMANTIC_CACHE_FAIL_OPEN_RESOLVER", "1")
    # No app resolver registered → falls through to fail-open under the flag.
    assert composition_root_module._composed_resolver("any") is True


def test_install_default_resolvers_is_idempotent(composition_root_module):
    composition_root_module.install_default_resolvers()
    composition_root_module.install_default_resolvers()
    assert composition_root_module._INSTALLED is True


def test_wired_into_l4_cache_manager(composition_root_module):
    """The L4 set_evidence_resolver pointer should be the composed resolver."""
    from agentic_core.L4_state.utils.memory import semantic_cache_manager  # noqa: PLC0415

    composition_root_module.register_evidence_source(lambda eid: eid == "ok")
    # The L4 module-level resolver is what the cache hot path calls.
    assert semantic_cache_manager._EVIDENCE_RESOLVER("ok") is True
    assert semantic_cache_manager._EVIDENCE_RESOLVER("nope") is False
