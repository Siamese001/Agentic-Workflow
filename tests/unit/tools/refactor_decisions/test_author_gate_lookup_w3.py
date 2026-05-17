"""Unit tests for W3 lookup reason taxonomy (tools/refactor_decisions/author_gate_lookup_w3.py)."""

import pytest

from tools.refactor_decisions.author_gate_lookup_w3 import (
    LOOKUP_W3_POLICY_VERSION,
    sort_reason_codes,
    validate_reason_codes,
)


def test_sort_reason_codes_deterministic_and_dedupes():
    a = sort_reason_codes(["MATCHED_WEAK_BIND", "COLD_CORPUS", "MATCHED_WEAK_BIND", "BELOW_THRESHOLD"])
    b = sort_reason_codes(["BELOW_THRESHOLD", "COLD_CORPUS", "MATCHED_WEAK_BIND"])
    assert a == b
    assert a == ["COLD_CORPUS", "BELOW_THRESHOLD", "MATCHED_WEAK_BIND"]


def test_validate_reason_codes_rejects_unknown():
    with pytest.raises(ValueError, match="Unknown lookup reason code"):
        validate_reason_codes(["MATCHED_STRONG_BIND", "NOT_A_REAL_CODE"])


def test_policy_version_is_non_empty():
    assert LOOKUP_W3_POLICY_VERSION
    assert "lookup" in LOOKUP_W3_POLICY_VERSION.lower()
