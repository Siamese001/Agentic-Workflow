"""Tests for the LICCoreContext dependency management helpers."""
import importlib

import pytest

from src.lic_agentic.core.dependency_injection import (
    DependencyAlreadyRegisteredError,
    DependencyNotRegisteredError,
    LICCoreContext,
)


def test_register_factory_and_instance_enforce_uniqueness():
    ctx = LICCoreContext()
    ctx.register_factory("value", lambda _ctx: object())
    with pytest.raises(DependencyAlreadyRegisteredError):
        ctx.register_factory("value", lambda _ctx: object())
    ctx.register_instance("static", object())
    with pytest.raises(DependencyAlreadyRegisteredError):
        ctx.register_instance("static", object())


def test_resolve_supports_singleton_and_transient():
    ctx = LICCoreContext()
    ctx.register_factory("singleton", lambda _ctx: object())
    ctx.register_factory("transient", lambda _ctx: object(), singleton=False)
    assert ctx.resolve("singleton") is ctx.resolve("singleton")
    assert ctx.resolve("transient") is not ctx.resolve("transient")


def test_resolve_raises_for_unknown_dependency():
    ctx = LICCoreContext()
    with pytest.raises(DependencyNotRegisteredError):
        ctx.resolve("missing")


def test_bootstrap_wires_selector_with_shared_dependencies():
    ctx = LICCoreContext.bootstrap()
    selector = ctx.resolve("mcp_selector")
    assert selector.client is ctx.resolve("mcp_client")
    assert selector.policy is ctx.resolve("policy_controller")
    assert selector is ctx.resolve("mcp_selector")


def test_dependency_exceptions_module_is_importable():
    module = importlib.import_module("src.lic_agentic.core.exceptions")
    assert hasattr(module, "__all__")
