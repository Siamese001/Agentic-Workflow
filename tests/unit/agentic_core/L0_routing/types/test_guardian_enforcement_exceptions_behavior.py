"""Behavioral tests for ``agentic_core.L0_routing.types.guardian_enforcement_exceptions``.

Covers:
- Exception class hierarchy (V15EnforcementError is RuntimeError; SoftFail/HardFail are Exception).
- ``is_v15_enforced`` fail-closed default when env var unset.
- ``is_v15_enforced`` accepts documented truthy values (1, true, yes, on, log, soft).
- ``is_v15_enforced`` accepts documented falsy values (0, false, no, off).
- ``is_v15_enforced`` raises ValueError on unrecognized values (deterministic misconfig).
- Case-insensitive and whitespace-tolerant parsing.
- ``is_v15_hard_fail`` / ``is_v15_soft_fail`` orthogonal mode selection.
"""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.types.guardian_enforcement_exceptions import (
    V15EnforcementError,
    V15HardFailAbort,
    V15SoftFailAbort,
    is_v15_enforced,
    is_v15_hard_fail,
    is_v15_soft_fail,
)


class TestExceptionHierarchy:
    def test_enforcement_error_is_runtime_error(self) -> None:
        assert issubclass(V15EnforcementError, RuntimeError)

    def test_soft_fail_is_exception(self) -> None:
        assert issubclass(V15SoftFailAbort, Exception)
        assert not issubclass(V15SoftFailAbort, RuntimeError)

    def test_hard_fail_is_exception(self) -> None:
        assert issubclass(V15HardFailAbort, Exception)
        assert not issubclass(V15HardFailAbort, RuntimeError)

    def test_soft_and_hard_are_distinct(self) -> None:
        assert not issubclass(V15SoftFailAbort, V15HardFailAbort)
        assert not issubclass(V15HardFailAbort, V15SoftFailAbort)

    def test_raise_and_catch(self) -> None:
        with pytest.raises(V15EnforcementError):
            raise V15EnforcementError("violation")
        with pytest.raises(V15SoftFailAbort):
            raise V15SoftFailAbort("soft abort")
        with pytest.raises(V15HardFailAbort):
            raise V15HardFailAbort("hard abort")


class TestIsV15Enforced:
    def test_unset_defaults_to_enforced(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("V15_ENFORCEMENT", raising=False)
        assert is_v15_enforced() is True

    @pytest.mark.parametrize("value", ["0", "false", "no", "off", "False", "NO", "OFF"])
    def test_falsy_values_disable(self, monkeypatch: pytest.MonkeyPatch, value: str) -> None:
        monkeypatch.setenv("V15_ENFORCEMENT", value)
        assert is_v15_enforced() is False

    @pytest.mark.parametrize(
        "value",
        ["1", "true", "yes", "on", "log", "soft", "TRUE", "On", "Soft", "LOG"],
    )
    def test_truthy_values_enable(self, monkeypatch: pytest.MonkeyPatch, value: str) -> None:
        monkeypatch.setenv("V15_ENFORCEMENT", value)
        assert is_v15_enforced() is True

    def test_whitespace_tolerant(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("V15_ENFORCEMENT", "  true  ")
        assert is_v15_enforced() is True

    @pytest.mark.parametrize("value", ["maybe", "enabled", "disabled", "2", ""])
    def test_unrecognized_raises(self, monkeypatch: pytest.MonkeyPatch, value: str) -> None:
        monkeypatch.setenv("V15_ENFORCEMENT", value)
        with pytest.raises(ValueError, match="V15_ENFORCEMENT"):
            is_v15_enforced()


class TestIsV15HardFail:
    @pytest.mark.parametrize("value", ["1", "true", "yes", "TRUE", "Yes"])
    def test_hard_values(self, monkeypatch: pytest.MonkeyPatch, value: str) -> None:
        monkeypatch.setenv("V15_ENFORCEMENT", value)
        assert is_v15_hard_fail() is True

    @pytest.mark.parametrize("value", ["soft", "log", "on", "0", "false", ""])
    def test_non_hard_values(self, monkeypatch: pytest.MonkeyPatch, value: str) -> None:
        monkeypatch.setenv("V15_ENFORCEMENT", value)
        assert is_v15_hard_fail() is False

    def test_unset_not_hard(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("V15_ENFORCEMENT", raising=False)
        assert is_v15_hard_fail() is False


class TestIsV15SoftFail:
    def test_only_literal_soft(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("V15_ENFORCEMENT", "soft")
        assert is_v15_soft_fail() is True

    def test_case_insensitive_soft(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("V15_ENFORCEMENT", "SOFT")
        assert is_v15_soft_fail() is True

    @pytest.mark.parametrize("value", ["1", "true", "log", "on", "0", "false", ""])
    def test_non_soft_values(self, monkeypatch: pytest.MonkeyPatch, value: str) -> None:
        monkeypatch.setenv("V15_ENFORCEMENT", value)
        assert is_v15_soft_fail() is False

    def test_unset_not_soft(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("V15_ENFORCEMENT", raising=False)
        assert is_v15_soft_fail() is False


class TestModeOrthogonality:
    def test_hard_and_soft_mutually_exclusive(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """A single env value cannot be both hard-fail and soft-fail."""
        for value in ["1", "true", "yes", "soft", "log", "on", "0", "false", ""]:
            monkeypatch.setenv("V15_ENFORCEMENT", value)
            assert not (is_v15_hard_fail() and is_v15_soft_fail())
