"""ADG-driven tests for L2_execution/types/token_enforcement_types.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.types.token_enforcement_types import TokenEnforcementOutcome


class TestTokenEnforcementOutcome:
    def test_is_enum(self):
        import enum
        assert issubclass(TokenEnforcementOutcome, enum.Enum)

    def test_pass_value(self):
        assert TokenEnforcementOutcome.PASS.value == "pass"

    def test_fail_pre_call_value(self):
        assert TokenEnforcementOutcome.FAIL_PRE_CALL.value == "fail_pre_call"

    def test_fail_post_call_value(self):
        assert TokenEnforcementOutcome.FAIL_POST_CALL.value == "fail_post_call"

    def test_has_three_members(self):
        assert len(list(TokenEnforcementOutcome)) == 3
