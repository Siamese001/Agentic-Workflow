"""Wave 4.2 — apps_rg untested-hotspot coverage.

Covers ``apps_rg/runtime/aggregation/_digest_utils.py``: deterministic
canonical-JSON / sha256 / claim-normalization / tokenization helpers shared
by the aggregation modules.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from apps_rg.runtime.aggregation._digest_utils import (
    canonical_json_sorted,
    normalize_claim_text,
    rel_posix,
    sha256_file,
    sha256_file_bytes,
    sha256_utf8,
    tokenize,
)


class TestCanonicalJsonSorted:
    def test_keys_sorted_and_compact(self) -> None:
        out = canonical_json_sorted({"b": 1, "a": 2})
        assert out == '{"a":2,"b":1}'

    def test_deterministic_across_input_order(self) -> None:
        assert canonical_json_sorted({"x": 1, "y": 2}) == canonical_json_sorted({"y": 2, "x": 1})

    def test_non_ascii_preserved(self) -> None:
        assert "é" in canonical_json_sorted({"k": "café"})


class TestSha256:
    def test_sha256_utf8_matches_hashlib(self) -> None:
        assert sha256_utf8("hello") == hashlib.sha256(b"hello").hexdigest()

    def test_sha256_utf8_length(self) -> None:
        assert len(sha256_utf8("anything")) == 64

    def test_sha256_file_uses_text(self, tmp_path: Path) -> None:
        p = tmp_path / "f.txt"
        p.write_text("contents", encoding="utf-8")
        assert sha256_file(p) == sha256_utf8("contents")

    def test_sha256_file_bytes_uses_raw_bytes(self, tmp_path: Path) -> None:
        p = tmp_path / "f.bin"
        data = b"\x00\x01\x02raw"
        p.write_bytes(data)
        assert sha256_file_bytes(p) == hashlib.sha256(data).hexdigest()


class TestNormalizeClaimText:
    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("  Hello   World  ", "hello world"),
            ("MixedCase", "mixedcase"),
            ("a\t\nb", "a b"),
            ("", ""),
        ],
    )
    def test_normalization(self, raw: str, expected: str) -> None:
        assert normalize_claim_text(raw) == expected

    def test_none_safe(self) -> None:
        assert normalize_claim_text(None) == ""  # type: ignore[arg-type]


class TestTokenize:
    def test_drops_single_char_tokens(self) -> None:
        # "a" is length-1 and dropped; "10" and "led" survive.
        assert tokenize("a led 10 teams") == ["led", "10", "teams"]

    def test_keeps_percent_and_dollar(self) -> None:
        assert tokenize("grew 30% to $5m") == ["grew", "30%", "to", "$5m"]

    def test_empty_string(self) -> None:
        assert tokenize("") == []

    def test_lowercased(self) -> None:
        assert tokenize("Led TEAMS") == ["led", "teams"]


class TestRelPosix:
    def test_relative_path(self, tmp_path: Path) -> None:
        sub = tmp_path / "a" / "b.txt"
        assert rel_posix(tmp_path, sub) == "a/b.txt"

    def test_non_relative_falls_back_to_resolved(self, tmp_path: Path) -> None:
        other = tmp_path.parent / "elsewhere.txt"
        out = rel_posix(tmp_path / "repo", other)
        assert out.endswith("elsewhere.txt")
        assert "/" in out
