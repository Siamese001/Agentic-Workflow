from asyncio import TimeoutError as NativeTimeoutError

import core_v10_7


def test_public_api_contains_expected_symbols() -> None:
    expected = {"CacheManager", "WorkflowContext", "ConfigV10_7", "AsyncTimeoutError"}
    assert expected.issubset(set(core_v10_7.__all__))


def test_async_timeout_error_alias_matches_asyncio() -> None:
    assert core_v10_7.AsyncTimeoutError is NativeTimeoutError


def test_package_reexports_match_module_definitions() -> None:
    assert core_v10_7.CacheManager is core_v10_7.services.CacheManager
    assert core_v10_7.WorkflowContext is core_v10_7.context.WorkflowContext
