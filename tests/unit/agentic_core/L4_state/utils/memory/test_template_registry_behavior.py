"""Behavioral tests for ``agentic_core.L4_state.utils.memory.template_registry``.

Covers:
- TemplateEntry frozen dataclass construction.
- TemplateRegistry singleton semantics (__new__ caches class-level instance).
- get_s0 delegates to version_store.get_system_prompt.
- get_i0_mixin delegates to version_store.get_mixin.
- register_template hashes content, caches entry, and persists via store.
- list_available_mixins delegates to version_store.list_mixins.
- get_template_registry accessor returns module singleton.
"""

from __future__ import annotations

import hashlib
from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.L4_state.utils.memory import template_registry as mod
from agentic_core.L4_state.utils.memory.template_registry import (
    TemplateEntry,
    TemplateRegistry,
    get_template_registry,
)
from agentic_core.prompt_governance.contracts.template_manifest_types import (
    TemplateManifest,
)


def _manifest(template_id: str = "tpl-1") -> TemplateManifest:
    return TemplateManifest(
        template_id=template_id,
        version="1.0.0",
        git_commit_hash="abc123",
        required_variables=("foo", "bar"),
    )


@pytest.fixture(autouse=True)
def _reset_singletons() -> Generator[None, None, None]:
    """Clear singleton caches between tests."""
    TemplateRegistry._instance = None
    mod._registry_instance = None
    yield
    TemplateRegistry._instance = None
    mod._registry_instance = None


# ---- TemplateEntry -------------------------------------------------------


class TestTemplateEntry:
    def test_frozen(self) -> None:
        entry = TemplateEntry(manifest=_manifest(), content="hello")
        with pytest.raises(AttributeError):
            entry.content = "other"  # type: ignore[misc]

    def test_holds_manifest_and_content(self) -> None:
        m = _manifest()
        entry = TemplateEntry(manifest=m, content="body")
        assert entry.manifest is m
        assert entry.content == "body"


# ---- Singleton semantics ------------------------------------------------


class TestSingleton:
    def test_class_instance_cached(self) -> None:
        r1 = TemplateRegistry()
        r2 = TemplateRegistry()
        assert r1 is r2

    def test_module_accessor_returns_singleton(self) -> None:
        r1 = get_template_registry()
        r2 = get_template_registry()
        assert r1 is r2
        assert isinstance(r1, TemplateRegistry)

    def test_init_idempotent_does_not_reset_cache(self) -> None:
        r = TemplateRegistry()
        r._cache["marker"] = TemplateEntry(manifest=_manifest(), content="x")
        # Second call to __init__ (via second TemplateRegistry() call) must NOT
        # clear the cache — the singleton uses __initialized guard.
        TemplateRegistry()
        assert "marker" in r._cache


# ---- Delegation to version store ----------------------------------------


class TestGetS0:
    def test_delegates_to_store(self) -> None:
        registry = TemplateRegistry()
        store = MagicMock()
        store.get_system_prompt.return_value = "SYSTEM-PROMPT"
        with patch.object(registry, "_get_version_store", return_value=store):
            result = registry.get_s0("hash-abc")
        store.get_system_prompt.assert_called_once_with("hash-abc")
        assert result == "SYSTEM-PROMPT"

    def test_keyerror_propagates(self) -> None:
        registry = TemplateRegistry()
        store = MagicMock()
        store.get_system_prompt.side_effect = KeyError("missing")
        with patch.object(registry, "_get_version_store", return_value=store):
            with pytest.raises(KeyError):
                registry.get_s0("bad")


class TestGetI0Mixin:
    def test_delegates_to_store(self) -> None:
        registry = TemplateRegistry()
        store = MagicMock()
        store.get_mixin.return_value = "MIXIN-CONTENT"
        with patch.object(registry, "_get_version_store", return_value=store):
            result = registry.get_i0_mixin("mx-1")
        store.get_mixin.assert_called_once_with("mx-1")
        assert result == "MIXIN-CONTENT"

    def test_keyerror_propagates(self) -> None:
        registry = TemplateRegistry()
        store = MagicMock()
        store.get_mixin.side_effect = KeyError("missing")
        with patch.object(registry, "_get_version_store", return_value=store):
            with pytest.raises(KeyError):
                registry.get_i0_mixin("bad")


# ---- register_template --------------------------------------------------


class TestRegisterTemplate:
    def test_hashes_content_sha256(self) -> None:
        registry = TemplateRegistry()
        content = "template body"
        expected_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        store = MagicMock()
        with patch.object(registry, "_get_version_store", return_value=store):
            result = registry.register_template(_manifest(), content)
        assert result == expected_hash

    def test_caches_entry_under_hash(self) -> None:
        registry = TemplateRegistry()
        m = _manifest()
        content = "body"
        store = MagicMock()
        with patch.object(registry, "_get_version_store", return_value=store):
            h = registry.register_template(m, content)
        assert h in registry._cache
        assert registry._cache[h].manifest is m
        assert registry._cache[h].content == content

    def test_persists_via_store(self) -> None:
        registry = TemplateRegistry()
        m = _manifest(template_id="T1")
        store = MagicMock()
        with patch.object(registry, "_get_version_store", return_value=store):
            h = registry.register_template(m, "xyz")
        store.store_template.assert_called_once_with("T1", h, "xyz")

    def test_identical_content_identical_hash(self) -> None:
        registry = TemplateRegistry()
        store = MagicMock()
        with patch.object(registry, "_get_version_store", return_value=store):
            h1 = registry.register_template(_manifest("a"), "same")
            h2 = registry.register_template(_manifest("b"), "same")
        assert h1 == h2


# ---- list_available_mixins ----------------------------------------------


class TestListMixins:
    def test_delegates_to_store(self) -> None:
        registry = TemplateRegistry()
        store = MagicMock()
        store.list_mixins.return_value = ["mx-a", "mx-b"]
        with patch.object(registry, "_get_version_store", return_value=store):
            result = registry.list_available_mixins()
        store.list_mixins.assert_called_once_with()
        assert result == ["mx-a", "mx-b"]
