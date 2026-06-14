"""Unit tests for agentic_core.L6_observability.shadow_eval._digest.

Wave 6.1 (P2 untested-module coverage) — L6 shadow-eval digest SSOT.
``_digest`` owns the deterministic content-hash semantics every L6 receipt
pins to. Pure / deterministic: ``_canonicalize`` recursion, ``canonical_json``
stable encoding, ``compute_digest`` (derived-hash-field exclusion), and
``stamp_digest`` (mutable + frozen-dataclass paths).
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.L6_observability.shadow_eval._digest import (
    CONTENT_HASH_FIELD,
    DIGEST_FIELD,
    SEAL_HASH_FIELD,
    canonical_json,
    compute_digest,
    stamp_digest,
)


@dataclasses.dataclass
class _Mutable:
    a: int = 1
    b: str = "x"
    deterministic_digest: str = ""


@dataclasses.dataclass(frozen=True)
class _Frozen:
    a: int = 1
    deterministic_digest: str = ""


class TestFieldConstants:
    def test_field_names(self) -> None:
        assert DIGEST_FIELD == "deterministic_digest"
        assert SEAL_HASH_FIELD == "seal_hash"
        assert CONTENT_HASH_FIELD == "proposal_content_hash"


class TestCanonicalJson:
    def test_dict_key_order_irrelevant(self) -> None:
        assert canonical_json({"b": 1, "a": 2}) == canonical_json({"a": 2, "b": 1})

    def test_tuple_and_list_equivalent(self) -> None:
        assert canonical_json([1, 2, 3]) == canonical_json((1, 2, 3))

    def test_no_whitespace(self) -> None:
        out = canonical_json({"a": 1, "b": [1, 2]})
        assert " " not in out

    def test_set_is_sorted_by_repr(self) -> None:
        assert canonical_json({3, 1, 2}) == canonical_json({2, 1, 3})

    def test_dataclass_canonicalized(self) -> None:
        assert canonical_json(_Mutable(a=5, b="y")) == canonical_json(
            {"a": 5, "b": "y", "deterministic_digest": ""}
        )

    def test_non_serializable_falls_back_to_repr(self) -> None:
        obj = object()
        assert canonical_json(obj) == f'"{repr(obj)}"'


class TestComputeDigest:
    def test_is_sha256_hex(self) -> None:
        d = compute_digest({"a": 1})
        assert len(d) == 64
        assert all(c in "0123456789abcdef" for c in d)

    def test_deterministic(self) -> None:
        payload = {"x": [1, 2], "y": {"z": 3}}
        assert compute_digest(payload) == compute_digest(payload)

    def test_key_order_does_not_change_digest(self) -> None:
        assert compute_digest({"a": 1, "b": 2}) == compute_digest({"b": 2, "a": 1})

    def test_content_change_changes_digest(self) -> None:
        assert compute_digest({"a": 1}) != compute_digest({"a": 2})

    def test_derived_hash_fields_excluded_by_default(self) -> None:
        base = {"a": 1}
        with_hashes = {
            "a": 1,
            DIGEST_FIELD: "deadbeef",
            SEAL_HASH_FIELD: "cafe",
            CONTENT_HASH_FIELD: "f00d",
            "hmac_sig": "sig",
        }
        assert compute_digest(base) == compute_digest(with_hashes)

    def test_custom_exclude_drops_field(self) -> None:
        full = {"a": 1, "volatile": "now"}
        assert compute_digest(full, exclude=frozenset({"volatile"})) == compute_digest(
            {"a": 1}
        )

    def test_non_dict_payload_digested(self) -> None:
        # list payloads have no fields to exclude; still deterministic
        assert compute_digest([1, 2, 3]) == compute_digest([1, 2, 3])
        assert compute_digest([1, 2, 3]) != compute_digest([3, 2, 1])


class TestStampDigest:
    def test_mutable_record_stamped_in_place(self) -> None:
        rec = _Mutable()
        out = stamp_digest(rec)
        assert out is rec
        assert rec.deterministic_digest
        assert len(rec.deterministic_digest) == 64

    def test_frozen_record_stamped(self) -> None:
        rec = _Frozen()
        out = stamp_digest(rec)
        assert out is rec
        assert rec.deterministic_digest

    def test_stamp_excludes_its_own_digest_field(self) -> None:
        # Stamping twice must produce the same digest (digest field is excluded).
        rec = _Mutable()
        stamp_digest(rec)
        first = rec.deterministic_digest
        stamp_digest(rec)
        assert rec.deterministic_digest == first

    def test_immutable_target_swallowed(self) -> None:
        # An object that cannot accept setattr is returned unchanged (no raise).
        sentinel = (1, 2, 3)
        assert stamp_digest(sentinel) is sentinel
