"""Unit tests for agentic_core.L4_state.contracts.digests.

Wave 3.2 (plan adg-testing-hotspots-wave-plan-a7f3c1) — Core P1 state-contract
surface. ``digests`` (fan_in=11, L4_STATE) provides the deterministic digest
helpers (canonical JSON + SHA-256) every doctrinal L4 record relies on.
Coverage of canonical-encoding rules, digest determinism, and key-order
invariance.
"""

from __future__ import annotations

import hashlib

import pytest

from agentic_core.L4_state.contracts.digests import (
    canonical_json_dumps,
    compute_deterministic_digest,
)


class TestCanonicalJsonDumps:
    def test_keys_sorted(self) -> None:
        assert canonical_json_dumps({"b": 1, "a": 2}) == '{"a":2,"b":1}'

    def test_no_whitespace_separators(self) -> None:
        out = canonical_json_dumps({"a": 1, "b": 2})
        assert " " not in out
        assert out == '{"a":1,"b":2}'

    def test_nested_keys_sorted(self) -> None:
        out = canonical_json_dumps({"outer": {"z": 1, "a": 2}})
        assert out == '{"outer":{"a":2,"z":1}}'

    def test_list_order_preserved(self) -> None:
        out = canonical_json_dumps({"items": [3, 1, 2]})
        assert out == '{"items":[3,1,2]}'

    def test_unicode_preserved_verbatim(self) -> None:
        out = canonical_json_dumps({"name": "café"})
        assert "café" in out

    def test_key_order_invariant(self) -> None:
        assert canonical_json_dumps({"a": 1, "b": 2}) == canonical_json_dumps({"b": 2, "a": 1})


class TestComputeDeterministicDigest:
    def test_returns_64_char_lowercase_hex(self) -> None:
        d = compute_deterministic_digest({"a": 1})
        assert len(d) == 64
        assert d == d.lower()
        assert all(c in "0123456789abcdef" for c in d)

    def test_same_input_same_digest(self) -> None:
        payload = {"x": 1, "y": [1, 2, 3]}
        assert compute_deterministic_digest(payload) == compute_deterministic_digest(payload)

    def test_key_order_does_not_change_digest(self) -> None:
        assert compute_deterministic_digest({"a": 1, "b": 2}) == compute_deterministic_digest(
            {"b": 2, "a": 1},
        )

    def test_different_input_different_digest(self) -> None:
        assert compute_deterministic_digest({"a": 1}) != compute_deterministic_digest({"a": 2})

    @pytest.mark.parametrize(
        "p1,p2",
        [
            ({"a": 1}, {"a": "1"}),  # int vs str
            ({"a": [1, 2]}, {"a": [2, 1]}),  # list order matters
            ({"a": 1}, {"a": 1, "b": 2}),  # extra key
        ],
    )
    def test_distinct_payloads_distinct_digests(self, p1: dict, p2: dict) -> None:
        assert compute_deterministic_digest(p1) != compute_deterministic_digest(p2)

    def test_matches_manual_sha256(self) -> None:
        payload = {"a": 1, "b": 2}
        expected = hashlib.sha256(
            canonical_json_dumps(payload).encode("utf-8"),
        ).hexdigest()
        assert compute_deterministic_digest(payload) == expected

    def test_empty_payload_is_stable(self) -> None:
        assert compute_deterministic_digest({}) == compute_deterministic_digest({})
