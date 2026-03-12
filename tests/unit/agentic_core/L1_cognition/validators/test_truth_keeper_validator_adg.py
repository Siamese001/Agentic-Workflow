"""ADG-driven tests for L1_cognition/validators/truth_keeper_validator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L1_cognition.validators.truth_keeper_validator import TruthKeeper


class TestTruthKeeper:
    def test_creates_with_defaults(self):
        tk = TruthKeeper()
        assert tk.llm_client is None
        assert tk.api_key is None

    def test_creates_with_llm_client(self):
        mock_client = object()
        tk = TruthKeeper(llm_client=mock_client)
        assert tk.llm_client is mock_client

    def test_has_check_file_consistency(self):
        assert hasattr(TruthKeeper, "check_file_consistency")
