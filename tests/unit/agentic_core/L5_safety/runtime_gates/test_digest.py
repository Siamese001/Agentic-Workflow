"""Unit tests for agentic_core.L5_safety.runtime_gates.digest.

Wave 6.1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — P2 untested-module
coverage. Validates the pure deterministic sha256 digest helpers
``verdict_digest`` and ``mesh_digest``: determinism, ``sha256:`` prefix,
excluded-key invariance, key-order invariance, set/frozenset
order-independence, and mesh order-sensitivity. Pure surface only — no mocks.
"""
from __future__ import annotations

import pytest

from agentic_core.L5_safety.runtime_gates.digest import (
    mesh_digest,
    verdict_digest,
)


def _base_verdict() -> dict:
    return {
        "gate_id": "G1",
        "gate_family": "safety",
        "result": "PASS",
        "disposition": "ALLOW",
        "reason_codes": ["ok"],
        "score": 0.9,
        "threshold": 0.5,
    }


class TestVerdictDigest:
    def test_prefix(self) -> None:
        assert verdict_digest(_base_verdict()).startswith("sha256:")

    def test_hexdigest_length(self) -> None:
        digest = verdict_digest(_base_verdict())
        # "sha256:" (7) + 64 hex chars
        assert len(digest) == 71
        assert all(c in "0123456789abcdef" for c in digest[7:])

    def test_determinism(self) -> None:
        a = verdict_digest(_base_verdict())
        b = verdict_digest(_base_verdict())
        assert a == b

    def test_empty_dict_is_stable(self) -> None:
        assert verdict_digest({}) == verdict_digest({})
        assert verdict_digest({}).startswith("sha256:")

    @pytest.mark.parametrize(
        "excluded_key, value",
        (
            ("trace_id", "abc123"),
            ("created_at_run_offset", 42),
            ("span_id", "span-9"),
            ("deterministic_digest", "sha256:deadbeef"),
            ("not_in_allowlist", {"nested": True}),
        ),
    )
    def test_excluded_keys_do_not_change_digest(
        self, excluded_key: str, value: object
    ) -> None:
        base = _base_verdict()
        extended = {**base, excluded_key: value}
        assert verdict_digest(base) == verdict_digest(extended)

    def test_key_reorder_invariant(self) -> None:
        v1 = _base_verdict()
        v2 = dict(reversed(list(v1.items())))
        assert verdict_digest(v1) == verdict_digest(v2)

    def test_allowlisted_value_change_changes_digest(self) -> None:
        base = _base_verdict()
        mutated = {**base, "disposition": "BLOCK"}
        assert verdict_digest(base) != verdict_digest(mutated)

    def test_missing_allowlisted_key_treated_as_none(self) -> None:
        base = _base_verdict()
        explicit_none = {**base, "severity": None}
        # severity absent vs severity=None -> both canonicalize to None
        assert verdict_digest(base) == verdict_digest(explicit_none)

    def test_set_order_independence(self) -> None:
        a = {**_base_verdict(), "reason_codes": {"x", "y", "z"}}
        b = {**_base_verdict(), "reason_codes": {"z", "y", "x"}}
        assert verdict_digest(a) == verdict_digest(b)

    def test_frozenset_order_independence(self) -> None:
        a = {**_base_verdict(), "evidence_refs": frozenset({"r1", "r2"})}
        b = {**_base_verdict(), "evidence_refs": frozenset({"r2", "r1"})}
        assert verdict_digest(a) == verdict_digest(b)

    def test_nested_mapping_canonicalized(self) -> None:
        a = {**_base_verdict(), "remediation_hint": {"a": 1, "b": 2}}
        b = {**_base_verdict(), "remediation_hint": {"b": 2, "a": 1}}
        assert verdict_digest(a) == verdict_digest(b)

    def test_list_order_is_significant(self) -> None:
        a = {**_base_verdict(), "reason_codes": ["a", "b"]}
        b = {**_base_verdict(), "reason_codes": ["b", "a"]}
        assert verdict_digest(a) != verdict_digest(b)


class TestMeshDigest:
    def test_prefix(self) -> None:
        assert mesh_digest([_base_verdict()]).startswith("sha256:")

    def test_empty_iterable_is_stable(self) -> None:
        assert mesh_digest([]) == mesh_digest([])
        assert mesh_digest([]).startswith("sha256:")

    def test_determinism(self) -> None:
        verdicts = [_base_verdict(), {**_base_verdict(), "gate_id": "G2"}]
        assert mesh_digest(verdicts) == mesh_digest(list(verdicts))

    def test_order_sensitivity(self) -> None:
        v1 = _base_verdict()
        v2 = {**_base_verdict(), "gate_id": "G2"}
        assert mesh_digest([v1, v2]) != mesh_digest([v2, v1])

    def test_single_vs_empty_differ(self) -> None:
        assert mesh_digest([_base_verdict()]) != mesh_digest([])

    def test_accepts_generator(self) -> None:
        gen = (v for v in (_base_verdict(),))
        assert mesh_digest(gen).startswith("sha256:")
