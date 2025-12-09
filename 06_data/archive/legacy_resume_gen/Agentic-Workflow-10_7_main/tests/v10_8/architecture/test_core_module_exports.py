from __future__ import annotations

from asyncio import TimeoutError as NativeTimeoutError

import core_v10_7


def _module_union() -> set[str]:
    """Return the union of all declared module exports plus AsyncTimeoutError."""

    modules = [
        core_v10_7.agents,
        core_v10_7.clients,
        core_v10_7.config,
        core_v10_7.constants,
        core_v10_7.context,
        core_v10_7.exceptions,
        core_v10_7.mcp,
        core_v10_7.models,
        core_v10_7.resilience,
        core_v10_7.services,
    ]
    exports = {symbol for module in modules for symbol in getattr(module, "__all__", [])}
    exports.add("AsyncTimeoutError")
    return exports


def test_public_api_contains_expected_symbols() -> None:
    expected = {"CacheManager", "WorkflowContext", "ConfigV10_7", "AsyncTimeoutError"}
    assert expected.issubset(set(core_v10_7.__all__))


def test_async_timeout_error_alias_matches_asyncio() -> None:
    assert core_v10_7.AsyncTimeoutError is NativeTimeoutError


def test_package_reexports_match_module_definitions() -> None:
    assert core_v10_7.CacheManager is core_v10_7.services.CacheManager
    assert core_v10_7.WorkflowContext is core_v10_7.context.WorkflowContext


def test_public_api_matches_union_of_submodules() -> None:
    assert set(core_v10_7.__all__) == _module_union()


def test_public_api_is_sorted() -> None:
    assert list(core_v10_7.__all__) == sorted(core_v10_7.__all__)
