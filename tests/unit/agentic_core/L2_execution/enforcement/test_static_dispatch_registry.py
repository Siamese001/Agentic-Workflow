"""Tests for StaticDispatchRegistry — replaces __import__/importlib dynamic dispatch."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.enforcement.static_dispatch_registry import (
    StaticDispatchRegistry,
    UnregisteredDispatchError,
    get_guardian_registry,
)


class TestStaticDispatchRegistryRegistration:
    def test_register_and_is_registered(self):
        reg = StaticDispatchRegistry()
        reg.register("mykey", "json")
        assert reg.is_registered("mykey")

    def test_unregistered_key_not_present(self):
        reg = StaticDispatchRegistry()
        assert not reg.is_registered("absent")

    def test_register_many(self):
        reg = StaticDispatchRegistry()
        reg.register_many({"a": "json", "b": "os"})
        assert reg.is_registered("a")
        assert reg.is_registered("b")

    def test_len(self):
        reg = StaticDispatchRegistry()
        reg.register("x", "json")
        reg.register("y", "os")
        assert len(reg) == 2

    def test_contains_operator(self):
        reg = StaticDispatchRegistry()
        reg.register("z", "json")
        assert "z" in reg
        assert "missing" not in reg

    def test_registered_keys_sorted(self):
        reg = StaticDispatchRegistry()
        reg.register_many({"b": "os", "a": "json", "c": "sys"})
        assert reg.registered_keys() == ["a", "b", "c"]

    def test_overwrite_clears_resolved_cache(self):
        reg = StaticDispatchRegistry()
        reg.register("k", "json")
        _ = reg.dispatch("k")
        reg.register("k", "os")
        mod = reg.dispatch("k")
        assert mod.__name__ == "os"


class TestStaticDispatchRegistryDispatch:
    def test_dispatch_returns_module(self):
        reg = StaticDispatchRegistry()
        reg.register("json_mod", "json")
        mod = reg.dispatch("json_mod")
        import json

        assert mod is json

    def test_dispatch_unregistered_raises(self):
        reg = StaticDispatchRegistry()
        with pytest.raises(UnregisteredDispatchError, match="No module registered"):
            reg.dispatch("not_there")

    def test_dispatch_caches_module(self):
        reg = StaticDispatchRegistry()
        reg.register("json_mod", "json")
        mod1 = reg.dispatch("json_mod")
        mod2 = reg.dispatch("json_mod")
        assert mod1 is mod2

    def test_dispatch_invalid_module_raises_import_error(self):
        reg = StaticDispatchRegistry()
        reg.register("bad", "totally_nonexistent_module_xyz_abc")
        with pytest.raises(ImportError):
            reg.dispatch("bad")


class TestStaticDispatchRegistryDispatchAttr:
    def test_dispatch_attr_returns_attribute(self):
        reg = StaticDispatchRegistry()
        reg.register("json_mod", "json")
        dumps = reg.dispatch_attr("json_mod", "dumps")
        import json

        assert dumps is json.dumps

    def test_dispatch_attr_missing_raises_attribute_error(self):
        reg = StaticDispatchRegistry()
        reg.register("json_mod", "json")
        with pytest.raises(AttributeError, match="has no attribute"):
            reg.dispatch_attr("json_mod", "nonexistent_attr_xyz")

    def test_dispatch_callable_returns_callable(self):
        reg = StaticDispatchRegistry()
        reg.register("json_mod", "json")
        fn = reg.dispatch_callable("json_mod", "dumps")
        assert callable(fn)
        assert fn({"k": 1}) == '{"k": 1}'

    def test_dispatch_callable_non_callable_raises_type_error(self):
        reg = StaticDispatchRegistry()
        reg.register("json_mod", "json")
        with pytest.raises(TypeError, match="not callable"):
            reg.dispatch_callable("json_mod", "__version__")

    def test_dispatch_attr_unregistered_raises(self):
        reg = StaticDispatchRegistry()
        with pytest.raises(UnregisteredDispatchError):
            reg.dispatch_attr("not_there", "fn")


class TestGuardianRegistry:
    def test_get_guardian_registry_returns_instance(self):
        reg = get_guardian_registry()
        assert isinstance(reg, StaticDispatchRegistry)

    def test_guardian_registry_singleton(self):
        r1 = get_guardian_registry()
        r2 = get_guardian_registry()
        assert r1 is r2

    def test_guardian_registry_has_hygiene_key(self):
        reg = get_guardian_registry()
        assert reg.is_registered("guardian.hygiene")

    def test_guardian_registry_has_c0_sovereignty_key(self):
        reg = get_guardian_registry()
        assert reg.is_registered("guardian.c0_sovereignty")

    def test_guardian_registry_has_all_key(self):
        reg = get_guardian_registry()
        assert reg.is_registered("guardian.all")

    def test_guardian_registry_dispatch_unregistered_fails_closed(self):
        reg = get_guardian_registry()
        with pytest.raises(UnregisteredDispatchError):
            reg.dispatch("nonexistent.guardian")
