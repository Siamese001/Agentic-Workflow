"""Runtime-hardened tests for ``guardian_contract_types``."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def guardian_symbols():
    module = pytest.importorskip("agentic_core.L0_routing.types.guardian_contract_types")
    return {
        "V15EnforcementError": module.V15EnforcementError,
        "V15HardFailAbort": module.V15HardFailAbort,
        "V15SoftFailAbort": module.V15SoftFailAbort,
        "is_v15_enforced": module.is_v15_enforced,
        "is_v15_hard_fail": module.is_v15_hard_fail,
        "is_v15_soft_fail": module.is_v15_soft_fail,
    }


class TestV15Exceptions:
    def test_exception_class_hierarchy(self, guardian_symbols):
        assert issubclass(guardian_symbols["V15EnforcementError"], RuntimeError)
        assert issubclass(guardian_symbols["V15SoftFailAbort"], Exception)
        assert issubclass(guardian_symbols["V15HardFailAbort"], Exception)

    @pytest.mark.parametrize(
        ("symbol_name", "message"),
        [
            ("V15EnforcementError", "test error"),
            ("V15SoftFailAbort", "test abort"),
            ("V15HardFailAbort", "test abort"),
        ],
    )
    def test_exception_types_can_be_raised(self, guardian_symbols, symbol_name, message):
        error_type = guardian_symbols[symbol_name]

        with pytest.raises(error_type):
            raise error_type(message)

    @pytest.mark.parametrize(
        ("env_value", "expected"),
        [
            (None, True),
            ("0", False),
            ("1", True),
            ("soft", True),
        ],
    )
    def test_is_v15_enforced(self, guardian_symbols, monkeypatch, env_value, expected):
        if env_value is None:
            monkeypatch.delenv("V15_ENFORCEMENT", raising=False)
        else:
            monkeypatch.setenv("V15_ENFORCEMENT", env_value)

        assert guardian_symbols["is_v15_enforced"]() is expected

    def test_is_v15_hard_fail_true(self, guardian_symbols, monkeypatch):
        monkeypatch.setenv("V15_ENFORCEMENT", "1")

        assert guardian_symbols["is_v15_hard_fail"]() is True

    def test_is_v15_soft_fail_true(self, guardian_symbols, monkeypatch):
        monkeypatch.setenv("V15_ENFORCEMENT", "soft")

        assert guardian_symbols["is_v15_soft_fail"]() is True
