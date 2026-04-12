"""Functional tests for agentic_core/L0_routing/types/guardian_contract_types.py.

These tests verify the actual behavior of V15 exception classes and functions.
"""

from __future__ import annotations

import os

import pytest

# Check if guardian_contract_types is available
try:
    from agentic_core.L0_routing.types.guardian_contract_types import (
        V15EnforcementError,
        V15HardFailAbort,
        V15SoftFailAbort,
        is_v15_enforced,
        is_v15_hard_fail,
        is_v15_soft_fail,
    )

    V15_AVAILABLE = True
except ImportError:
    V15_AVAILABLE = False


pytestmark = pytest.mark.unit


@pytest.mark.skipif(not V15_AVAILABLE, reason="V15 exception classes not available")
class TestV15Exceptions:
    """Test V15 exception classes and functions."""

    def test_V15EnforcementError_is_runtime_error(self):
        """V15EnforcementError should be a RuntimeError subclass."""
        assert issubclass(V15EnforcementError, RuntimeError)

    def test_V15EnforcementError_can_be_raised(self):
        """V15EnforcementError can be raised and caught."""
        with pytest.raises(V15EnforcementError):
            raise V15EnforcementError("test error")

    def test_V15SoftFailAbort_is_exception(self):
        """V15SoftFailAbort should be an Exception subclass."""
        assert issubclass(V15SoftFailAbort, Exception)

    def test_V15SoftFailAbort_can_be_raised(self):
        """V15SoftFailAbort can be raised and caught."""
        with pytest.raises(V15SoftFailAbort):
            raise V15SoftFailAbort("test abort")

    def test_V15HardFailAbort_is_exception(self):
        """V15HardFailAbort should be an Exception subclass."""
        assert issubclass(V15HardFailAbort, Exception)

    def test_V15HardFailAbort_can_be_raised(self):
        """V15HardFailAbort can be raised and caught."""
        with pytest.raises(V15HardFailAbort):
            raise V15HardFailAbort("test abort")

    def test_is_v15_enforced_default(self):
        """is_v15_enforced should return True by default (no env var)."""
        old_val = os.environ.pop("V15_ENFORCEMENT", None)
        try:
            assert is_v15_enforced() is True
        finally:
            if old_val is not None:
                os.environ["V15_ENFORCEMENT"] = old_val

    def test_is_v15_enforced_disabled(self):
        """is_v15_enforced should return False when explicitly disabled."""
        old_val = os.environ.pop("V15_ENFORCEMENT", None)
        try:
            os.environ["V15_ENFORCEMENT"] = "0"
            assert is_v15_enforced() is False
        finally:
            if old_val is not None:
                os.environ["V15_ENFORCEMENT"] = old_val
            else:
                os.environ.pop("V15_ENFORCEMENT", None)

    def test_is_v15_hard_fail_true(self):
        """is_v15_hard_fail should return True for hard fail values."""
        old_val = os.environ.pop("V15_ENFORCEMENT", None)
        try:
            os.environ["V15_ENFORCEMENT"] = "1"
            assert is_v15_hard_fail() is True
        finally:
            if old_val is not None:
                os.environ["V15_ENFORCEMENT"] = old_val
            else:
                os.environ.pop("V15_ENFORCEMENT", None)

    def test_is_v15_soft_fail_true(self):
        """is_v15_soft_fail should return True only for 'soft' mode."""
        old_val = os.environ.pop("V15_ENFORCEMENT", None)
        try:
            os.environ["V15_ENFORCEMENT"] = "soft"
            assert is_v15_soft_fail() is True
        finally:
            if old_val is not None:
                os.environ["V15_ENFORCEMENT"] = old_val
            else:
                os.environ.pop("V15_ENFORCEMENT", None)
