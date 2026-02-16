"""G-16-8: L7 meta-learning determinism enforcement tests.

Tests:
1) Forbidden call scan (static) — no uuid4/datetime.now/time.time/time.monotonic in L7.
2) Stable hash test (behavioral) — same input ⇒ same hash, same serialization bytes.
3) Order stability test — shuffled dict/list ⇒ identical deterministic_json output.
4) Structural — exactly one determinism module in L7.
"""

from __future__ import annotations

import ast
import pathlib
import re

import pytest

from system_learning.enforcement.determinism import (
    FORBIDDEN_PATTERNS,
    assert_no_nondeterminism,
    deterministic_json,
    stable_sha256_json,
)

L7_ROOT = pathlib.Path("system_learning")

# ============================================================================
# §1 — Forbidden Call Scan (static)
# ============================================================================


class TestForbiddenCallScan:
    """Assert zero occurrences of nondeterministic calls in L7 type/emission files."""

    @pytest.fixture(autouse=True)
    def _collect_sources(self) -> None:
        self.sources: list[tuple[pathlib.Path, str]] = []
        for p in L7_ROOT.rglob("*.py"):
            if "enforcement" in str(p):
                continue
            self.sources.append((p, p.read_text(encoding="utf-8", errors="ignore")))

    @pytest.mark.parametrize(
        "pattern",
        [r"uuid4\b", r"datetime\.now\b", r"time\.time\b", r"time\.monotonic\b"],
    )
    def test_no_forbidden_pattern(self, pattern: str) -> None:
        hits = []
        for path, src in self.sources:
            if re.search(pattern, src):
                hits.append(str(path))
        assert hits == [], f"Forbidden pattern {pattern!r} found in: {hits}"

    def test_no_hashlib_outside_enforcement(self) -> None:
        """hashlib must only appear in the enforcement module, not in type files."""
        hits = []
        for path, src in self.sources:
            if re.search(r"\bhashlib\b", src):
                hits.append(str(path))
        assert hits == [], f"hashlib found outside enforcement module: {hits}"

    def test_assert_no_nondeterminism_clean_passes(self) -> None:
        """Clean source text should not raise."""
        clean = "import json\ndef foo(): return json.dumps({}, sort_keys=True)"
        assert_no_nondeterminism(clean, filepath="<test>")

    @pytest.mark.parametrize(
        "bad_source",
        [
            "import uuid; x = uuid.uuid4()",
            "from datetime import datetime; t = datetime.now()",
            "import time; t = time.time()",
            "import time; t = time.monotonic()",
        ],
    )
    def test_assert_no_nondeterminism_rejects_forbidden(self, bad_source: str) -> None:
        with pytest.raises(PermissionError, match="L7_DETERMINISM_VIOLATION"):
            assert_no_nondeterminism(bad_source, filepath="<test>")


# ============================================================================
# §2 — Stable Hash Test (behavioral)
# ============================================================================


class TestStableHash:
    """Same input ⇒ same hash, same serialization bytes."""

    SAMPLE_OBJ = {
        "artifact_type": "META_LEARNING_PROPOSAL",
        "proposer": "test_agent",
        "target_component": "routing_thresholds",
        "semantic_clock": {"tick": 42, "vector_clock": {"a": 1, "b": 2}},
        "proposed_change": {
            "before": {"threshold": 0.5},
            "after": {"threshold": 0.7},
        },
        "metric_name": "response_quality",
        "evidence_hash": "abc123",
    }

    def test_hash_idempotent(self) -> None:
        h1 = stable_sha256_json(self.SAMPLE_OBJ)
        h2 = stable_sha256_json(self.SAMPLE_OBJ)
        assert h1 == h2, "Same input must produce identical hash"

    def test_serialization_idempotent(self) -> None:
        s1 = deterministic_json(self.SAMPLE_OBJ)
        s2 = deterministic_json(self.SAMPLE_OBJ)
        assert s1 == s2, "Same input must produce identical bytes"

    def test_hash_is_sha256_hex(self) -> None:
        h = stable_sha256_json(self.SAMPLE_OBJ)
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_hash_changes_on_different_input(self) -> None:
        modified = {**self.SAMPLE_OBJ, "proposer": "different_agent"}
        h1 = stable_sha256_json(self.SAMPLE_OBJ)
        h2 = stable_sha256_json(modified)
        assert h1 != h2, "Different input must produce different hash"


# ============================================================================
# §3 — Order Stability Test
# ============================================================================


class TestOrderStability:
    """Shuffled dict insertion order / list order ⇒ same deterministic output."""

    def test_dict_insertion_order_irrelevant(self) -> None:
        d1 = {"z": 1, "a": 2, "m": 3}
        d2 = {"a": 2, "m": 3, "z": 1}
        assert deterministic_json(d1) == deterministic_json(d2)

    def test_nested_dict_order_irrelevant(self) -> None:
        d1 = {"outer": {"z": 1, "a": 2}, "inner": {"c": 3, "b": 4}}
        d2 = {"inner": {"b": 4, "c": 3}, "outer": {"a": 2, "z": 1}}
        assert deterministic_json(d1) == deterministic_json(d2)

    def test_hash_invariant_to_insertion_order(self) -> None:
        d1 = {"z": 1, "a": 2, "m": 3}
        d2 = {"a": 2, "m": 3, "z": 1}
        assert stable_sha256_json(d1) == stable_sha256_json(d2)

    def test_list_order_preserved(self) -> None:
        """Lists are ordered — different order ⇒ different output (by design)."""
        d1 = {"items": [1, 2, 3]}
        d2 = {"items": [3, 2, 1]}
        assert deterministic_json(d1) != deterministic_json(d2)

    def test_compact_separators(self) -> None:
        """Output must use compact separators (no spaces)."""
        result = deterministic_json({"a": 1, "b": [2, 3]})
        assert " " not in result
        assert result == '{"a":1,"b":[2,3]}'


# ============================================================================
# §4 — Structural (single module, all hashing uses SSOT)
# ============================================================================


class TestStructural:
    """Exactly one determinism enforcement module in L7."""

    def test_single_determinism_module(self) -> None:
        modules = list(L7_ROOT.rglob("determinism.py"))
        assert len(modules) == 1, f"Expected exactly 1 determinism module, found {len(modules)}: {modules}"

    def test_all_type_files_import_determinism(self) -> None:
        """All L7 type files with hashing must import from enforcement.determinism."""
        type_files = list((L7_ROOT / "types").glob("*.py"))
        missing = []
        for p in type_files:
            if p.name == "__init__.py":
                continue
            src = p.read_text(encoding="utf-8", errors="ignore")
            if "stable_sha256_json" in src or "deterministic_json" in src:
                if "from system_learning.enforcement.determinism" not in src:
                    missing.append(str(p))
        assert missing == [], f"Type files using determinism helpers but not importing from SSOT: {missing}"

    def test_no_inline_hashlib_in_types(self) -> None:
        """No L7 type file should import hashlib directly."""
        type_files = list((L7_ROOT / "types").glob("*.py"))
        violators = []
        for p in type_files:
            src = p.read_text(encoding="utf-8", errors="ignore")
            try:
                tree = ast.parse(src, filename=str(p))
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name == "hashlib":
                            violators.append(str(p))
                elif isinstance(node, ast.ImportFrom):
                    if node.module and "hashlib" in node.module:
                        violators.append(str(p))
        assert violators == [], f"L7 type files still importing hashlib directly: {violators}"

    def test_forbidden_patterns_constant_matches_scan(self) -> None:
        """FORBIDDEN_PATTERNS must cover all 4 banned calls."""
        expected = {"uuid4", "datetime.now", "time.time", "time.monotonic"}
        covered = set()
        for pat in FORBIDDEN_PATTERNS:
            for exp in expected:
                if exp.replace(".", r"\.") in pat or exp in pat:
                    covered.add(exp)
        assert covered == expected, f"FORBIDDEN_PATTERNS missing coverage for: {expected - covered}"
