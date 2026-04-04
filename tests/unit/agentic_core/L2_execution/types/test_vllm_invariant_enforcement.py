"""

"""

import pytest


@pytest.fixture(autouse=True)
def reset_adapter_state():
    """Reset adapter singletons before each test."""


def test_adapter_local_success_with_zero_violations():
        """Test that valid local request produces zero violations."""


def test_adapter_with_fingerprint_produces_no_violations():
    """Test that providing fingerprint produces no violations.

    """


def test_adapter_result_has_invariant_violations_field():
    """Test that result always has invariant_violations field."""


def test_adapter_preserves_phase_1_4_behavior():
    """Test that Phase 5 preserves Phase 1-4 routing behavior when no violations."""


def test_adapter_fail_violation_triggers_gemini_with_violations_attached():
    """Test that FAIL violation triggers Gemini fallback with violations in telemetry.

    """
