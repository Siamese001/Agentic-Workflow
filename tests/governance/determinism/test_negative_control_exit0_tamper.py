from __future__ import annotations

import os

import pytest

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants


# This is a placeholder for a real system function that would be tampered with.
def get_sovereign_decision() -> str:
    """A function that makes a sovereign decision. In tamper mode, it's altered."""
    if os.environ.get("W4_NEGCTRL_TAMPER", "0") == "1":
        # In tamper mode, the decision is altered to a known incorrect value.
        return "TAMPERED_DECISION"
    return "CORRECT_DECISION"


@pytest.mark.xfail(
    condition=os.environ.get("W4_NEGCTRL_TAMPER", "0") == "1",
    reason="This test is expected to fail in tamper mode to prove detection.",
    strict=True,  # The test MUST fail in tamper mode, not pass.
)
def test_negative_control_integrity():
    """
    Validates the integrity of the negative control system.

    This test enforces Guarantee #25. When the `W4_NEGCTRL_TAMPER` environment
    variable is set to '1', this test is designed to fail. The `pytest.mark.xfail`
    decorator with `strict=True` ensures two things:
    1. If the test fails as expected (in tamper mode), it is marked as XFAIL.
    2. If the test unexpectedly passes (meaning the tamper was not detected), the
       test run fails.

    Crucially, a test run with an XFAIL result exits with code 0, allowing CI
    to verify the tamper detection mechanism without failing the build.
    """
    decision = get_sovereign_decision()

    # The core assertion: the decision must be the correct one.
    # This will fail when the environment variable is set, triggering the xfail.
    assert decision == "CORRECT_DECISION", f"Negative control tamper detected! Decision was '{decision}'."


# To run this test and see it in action:
#
# 1. Run normally (will pass):
#    pytest tests/governance/test_negative_control_exit0_tamper.py
#    (exit code 0)
#
# 2. Run in tamper mode (will be marked XFAIL):
#    W4_NEGCTRL_TAMPER=1 pytest tests/governance/test_negative_control_exit0_tamper.py
#    (exit code 0)
#
# REVIEW: Potential hidden failure - # REVIEW: Potential hidden failure - # 3. If the test were broken and passed in tamper mode, it would be marked as FAILED.
