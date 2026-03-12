"""ADG-driven tests for agentic_core/runtime/exceptions/healer_exceptions.py — fan_in=3.

Contract tests: HealerError hierarchy — all six exception classes.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.runtime.exceptions.healer_exceptions import (
    CircularDependencyError,
    ConfigurationError,
    HealerError,
    HealingBudgetExceededError,
    HealingTimeoutError,
    SovereignError,
    ValidationRegistryError,
)


class TestHealerError:
    def test_is_exception_subclass(self):
        assert issubclass(HealerError, Exception)

    def test_message_stored(self):
        err = HealerError("test message")
        assert err.message == "test message"

    def test_details_default_empty(self):
        err = HealerError("msg")
        assert err.details == {}

    def test_details_stored(self):
        err = HealerError("msg", {"key": "val"})
        assert err.details["key"] == "val"

    def test_str_without_details(self):
        err = HealerError("plain message")
        assert str(err) == "plain message"

    def test_str_with_details(self):
        err = HealerError("msg", {"k": "v"})
        assert "msg" in str(err)
        assert "k=v" in str(err)

    def test_can_be_raised(self):
        with pytest.raises(HealerError):
            raise HealerError("oops")


class TestCircularDependencyError:
    def test_is_healer_error(self):
        assert issubclass(CircularDependencyError, HealerError)

    def test_cycle_path_stored(self):
        err = CircularDependencyError(["A", "B", "C"])
        assert err.cycle_path == ["A", "B", "C"]

    def test_message_contains_cycle(self):
        err = CircularDependencyError(["A", "B"])
        assert "A" in str(err)
        assert "B" in str(err)

    def test_can_be_raised(self):
        with pytest.raises(CircularDependencyError):
            raise CircularDependencyError(["X", "Y"])


class TestHealingBudgetExceededError:
    def test_is_healer_error(self):
        assert issubclass(HealingBudgetExceededError, HealerError)

    def test_budget_attributes_stored(self):
        err = HealingBudgetExceededError(budget_used=15, budget_limit=10)
        assert err.budget_used == 15
        assert err.budget_limit == 10

    def test_message_contains_values(self):
        err = HealingBudgetExceededError(15, 10)
        assert "15" in str(err)
        assert "10" in str(err)

    def test_can_be_raised(self):
        with pytest.raises(HealingBudgetExceededError):
            raise HealingBudgetExceededError(5, 3)


class TestValidationRegistryError:
    def test_is_healer_error(self):
        assert issubclass(ValidationRegistryError, HealerError)

    def test_attributes_stored(self):
        err = ValidationRegistryError("my_key", "not found")
        assert err.registry_key == "my_key"
        assert err.reason == "not found"

    def test_message_contains_key_and_reason(self):
        err = ValidationRegistryError("k", "bad")
        assert "k" in str(err)
        assert "bad" in str(err)


class TestHealingTimeoutError:
    def test_is_healer_error(self):
        assert issubclass(HealingTimeoutError, HealerError)

    def test_attributes_stored(self):
        err = HealingTimeoutError(timeout_seconds=30, operation="heal_layer")
        assert err.timeout_seconds == 30
        assert err.operation == "heal_layer"

    def test_message_contains_operation(self):
        err = HealingTimeoutError(60, "scan")
        assert "scan" in str(err)
        assert "60" in str(err)


class TestSovereignError:
    def test_is_healer_error(self):
        assert issubclass(SovereignError, HealerError)

    def test_message_stored(self):
        err = SovereignError("violation")
        assert "violation" in str(err)

    def test_violation_type_stored(self):
        err = SovereignError("msg", violation_type="LAYER_BREACH")
        assert err.violation_type == "LAYER_BREACH"

    def test_violation_type_defaults_none(self):
        err = SovereignError("msg")
        assert err.violation_type is None


class TestConfigurationError:
    def test_is_healer_error(self):
        assert issubclass(ConfigurationError, HealerError)

    def test_message_stored(self):
        err = ConfigurationError("bad config")
        assert "bad config" in str(err)

    def test_config_key_stored(self):
        err = ConfigurationError("msg", config_key="MY_KEY")
        assert err.config_key == "MY_KEY"

    def test_config_key_defaults_none(self):
        err = ConfigurationError("msg")
        assert err.config_key is None
