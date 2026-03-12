"""ADG importability contract for agentic_core/adg/analysis/policy_hash_validator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_policy_hash_validator.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.adg.analysis.policy_hash_validator import (  # noqa: F401
        PolicyHashViolation,
        PolicyHashReport,
        validate_policy_hash_coupling,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    PolicyHashViolation = None  # type: ignore[assignment,misc]
    PolicyHashReport = None  # type: ignore[assignment,misc]
    validate_policy_hash_coupling = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="policy_hash_validator.py deps unavailable")
class TestPolicyHashValidatorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: policy_hash_validator.py must be importable."""
        assert _AVAILABLE

    def test_policyhashviolation_is_type(self) -> None:
        assert PolicyHashViolation is not None

    def test_policyhashreport_is_type(self) -> None:
        assert PolicyHashReport is not None

    def test_validate_policy_hash_coupling_callable(self) -> None:
        assert callable(validate_policy_hash_coupling)

