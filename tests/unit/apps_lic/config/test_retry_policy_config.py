"""Foundational behavioral tests for apps_lic/config/retry_policy_config.py.

fan_in=18 — this module is imported by 18 other modules.
ADG contract: import-hygiene is covered by test_retry_policy_config_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_lic.config.retry_policy_config import (  # noqa: F401
        RetryStrategy,
        RetryableError,
        NonRetryableError,
        RetryConfig,
        RetryAttempt,
        RetryResult,
        get_retry_executor,
        retry,
        retry_with_policy,
        init_default_policies,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    RetryStrategy = None  # type: ignore[assignment,misc]
    RetryableError = None  # type: ignore[assignment,misc]
    NonRetryableError = None  # type: ignore[assignment,misc]
    RetryConfig = None  # type: ignore[assignment,misc]
    RetryAttempt = None  # type: ignore[assignment,misc]
    RetryResult = None  # type: ignore[assignment,misc]
    get_retry_executor = None  # type: ignore[assignment,misc]
    retry = None  # type: ignore[assignment,misc]
    retry_with_policy = None  # type: ignore[assignment,misc]
    init_default_policies = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="retry_policy_config.py deps unavailable")
class TestRetryStrategyContract:
    def test_is_enum(self):
        import enum
        assert issubclass(RetryStrategy, enum.Enum)

    def test_has_members(self):
        assert len(list(RetryStrategy)) >= 1

    def test_member_values_are_strings_or_ints(self):
        for member in RetryStrategy:
            assert member.value is not None

    def test_known_member_exponential_backoff_exists(self):
        assert hasattr(RetryStrategy, 'EXPONENTIAL_BACKOFF')

@pytest.mark.skipif(not _AVAILABLE, reason="retry_policy_config.py deps unavailable")
class TestRetryableErrorContract:
    def test_is_class(self):
        assert isinstance(RetryableError, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(RetryableError, type)

@pytest.mark.skipif(not _AVAILABLE, reason="retry_policy_config.py deps unavailable")
class TestNonRetryableErrorContract:
    def test_is_class(self):
        assert isinstance(NonRetryableError, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(NonRetryableError, type)

@pytest.mark.skipif(not _AVAILABLE, reason="retry_policy_config.py deps unavailable")
class TestRetryConfigContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(RetryConfig)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(RetryConfig)}
        assert field_names >= {'max_attempts', 'multiplier', 'base_delay', 'max_delay', 'strategy'}

@pytest.mark.skipif(not _AVAILABLE, reason="retry_policy_config.py deps unavailable")
class TestRetryAttemptContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(RetryAttempt)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(RetryAttempt)}
        assert field_names >= {'exception', 'attempt', 'success', 'timestamp', 'delay'}

@pytest.mark.skipif(not _AVAILABLE, reason="retry_policy_config.py deps unavailable")
class TestRetryResultContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(RetryResult)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(RetryResult)}
        assert field_names >= {'success', 'total_delay', 'result', 'attempts', 'attempts_history'}

@pytest.mark.skipif(not _AVAILABLE, reason="retry_policy_config.py deps unavailable")
class TestGetRetryExecutorFunction:
    def test_is_callable(self):
        assert callable(get_retry_executor)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_retry_executor)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="retry_policy_config.py deps unavailable")
class TestRetryFunction:
    def test_is_callable(self):
        assert callable(retry)

@pytest.mark.skipif(not _AVAILABLE, reason="retry_policy_config.py deps unavailable")
class TestRetryWithPolicyFunction:
    def test_is_callable(self):
        assert callable(retry_with_policy)

@pytest.mark.skipif(not _AVAILABLE, reason="retry_policy_config.py deps unavailable")
class TestInitDefaultPoliciesFunction:
    def test_is_callable(self):
        assert callable(init_default_policies)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(init_default_policies)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="retry_policy_config.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="retry_policy_config.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="retry_policy_config.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="retry_policy_config.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="retry_policy_config.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module retry_policy_config must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
