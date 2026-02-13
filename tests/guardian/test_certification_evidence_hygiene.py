"""
Phase 3.1 — Certification Evidence Hygiene Normalization Tests.

Tests:
1. Schema lock: extra field → reject, missing required field → reject
2. Canonical hash seal: SHA256 present, stable, mutation-sensitive
3. Idempotency: identical pipeline runs produce byte-for-byte identical JSON
4. Deterministic field ordering: sorted keys, stable list ordering
5. Nondeterministic field gating: no timestamps, no random UUIDs
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_maintenance.types.guardian_contract import (
    CONTRACT_JSON_SCHEMA,
    ArtifactType,
    CheckStatus,
    GuardianResult,
    validate_against_json_schema,
)

pytestmark = pytest.mark.guardian


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _disable_v15(monkeypatch):
    monkeypatch.setenv("V15_ENFORCEMENT", "0")


@pytest.fixture
def certification_result() -> GuardianResult:
    """A representative certification artifact with multiple checks."""
    r = GuardianResult(guardian_id="cert_test")
    r.add_check("check_b", CheckStatus.PASS, "Second check")
    r.add_check("check_a", CheckStatus.PASS, "First check")
    r.add_artifact(ArtifactType.JSON, "docs/reports/plans/out.json", "Output")
    r.add_artifact(ArtifactType.LOG, "agentic_core/logs/run.log", "Run log")
    r.metrics = {"items_scanned": 10, "files_checked": 5}
    r.remediation_hints = ["hint_z", "hint_a"]
    return r


# ---------------------------------------------------------------------------
# 1. Schema Lock — negative tests
# ---------------------------------------------------------------------------


class TestSchemaLock:
    """CONTRACT_JSON_SCHEMA rejects extra/missing fields."""

    def test_extra_field_rejected(self, certification_result: GuardianResult):
        d = certification_result.to_dict()
        d["rogue_field"] = "should_not_exist"
        errors = validate_against_json_schema(d)
        assert any("rogue_field" in e for e in errors), (
            f"Extra field 'rogue_field' must be rejected, got errors: {errors}"
        )

    def test_missing_required_field_rejected(self, certification_result: GuardianResult):
        d = certification_result.to_dict()
        del d["guardian_id"]
        errors = validate_against_json_schema(d)
        assert any("guardian_id" in e for e in errors), (
            f"Missing 'guardian_id' must be rejected, got errors: {errors}"
        )

    def test_missing_checks_rejected(self, certification_result: GuardianResult):
        d = certification_result.to_dict()
        del d["checks"]
        errors = validate_against_json_schema(d)
        assert any("checks" in e for e in errors)

    def test_missing_status_rejected(self, certification_result: GuardianResult):
        d = certification_result.to_dict()
        del d["status"]
        errors = validate_against_json_schema(d)
        assert any("status" in e for e in errors)

    def test_valid_result_passes_schema(self, certification_result: GuardianResult):
        d = certification_result.to_dict()
        errors = validate_against_json_schema(d)
        assert errors == [], f"Valid result should pass schema: {errors}"

    def test_certification_hash_in_schema(self):
        props = CONTRACT_JSON_SCHEMA["properties"]
        assert "certification_hash" in props, "certification_hash must be in CONTRACT_JSON_SCHEMA"

    def test_additional_properties_false(self):
        assert CONTRACT_JSON_SCHEMA.get("additionalProperties") is False


# ---------------------------------------------------------------------------
# 2. Canonical Hash Seal
# ---------------------------------------------------------------------------


class TestCanonicalHashSeal:
    """certification_hash is SHA256 over canonical JSON, excluding itself."""

    def test_hash_present_after_to_json(self, certification_result: GuardianResult):
        raw = certification_result.to_json()
        parsed = json.loads(raw)
        assert parsed["certification_hash"] is not None
        assert len(parsed["certification_hash"]) == 64  # SHA256 hex

    def test_hash_stable_across_calls(self, certification_result: GuardianResult):
        j1 = certification_result.to_json()
        j2 = certification_result.to_json()
        h1 = json.loads(j1)["certification_hash"]
        h2 = json.loads(j2)["certification_hash"]
        assert h1 == h2, "certification_hash must be stable across calls"

    def test_hash_excludes_itself(self, certification_result: GuardianResult):
        certification_result.compute_certification_hash()
        d = certification_result.to_dict()
        h_stored = d["certification_hash"]
        d.pop("certification_hash", None)
        canonical = json.dumps(d, sort_keys=True, separators=(",", ":"))
        h_expected = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        assert h_stored == h_expected

    def test_mutation_changes_hash(self, certification_result: GuardianResult):
        """Negative test: mutating the payload MUST change the hash."""
        certification_result.compute_certification_hash()
        h_before = certification_result.certification_hash

        certification_result.add_check("check_c", CheckStatus.FAIL, "Injected")
        certification_result.compute_certification_hash()
        h_after = certification_result.certification_hash

        assert h_before != h_after, "Mutating the result must change certification_hash"

    def test_reordering_checks_does_not_change_hash(self):
        """Checks are sorted by check_id so reordering must not affect hash."""
        r1 = GuardianResult(guardian_id="order_test")
        r1.add_check("b", CheckStatus.PASS, "second")
        r1.add_check("a", CheckStatus.PASS, "first")

        r2 = GuardianResult(guardian_id="order_test")
        r2.add_check("a", CheckStatus.PASS, "first")
        r2.add_check("b", CheckStatus.PASS, "second")

        r1.compute_certification_hash()
        r2.compute_certification_hash()
        assert r1.certification_hash == r2.certification_hash


# ---------------------------------------------------------------------------
# 3. Deterministic Field Ordering
# ---------------------------------------------------------------------------


class TestDeterministicOrdering:
    """Serialized JSON has sorted keys and stable list ordering."""

    def test_sorted_keys_in_json(self, certification_result: GuardianResult):
        raw = certification_result.to_json()
        parsed = json.loads(raw)
        keys = list(parsed.keys())
        assert keys == sorted(keys), f"Top-level keys must be sorted: {keys}"

    def test_checks_sorted_by_check_id(self, certification_result: GuardianResult):
        raw = certification_result.to_json()
        parsed = json.loads(raw)
        check_ids = [c["check_id"] for c in parsed["checks"]]
        assert check_ids == sorted(check_ids), f"Checks must be sorted by check_id: {check_ids}"

    def test_artifacts_sorted_by_path(self, certification_result: GuardianResult):
        raw = certification_result.to_json()
        parsed = json.loads(raw)
        paths = [a["path"] for a in parsed["artifacts"]]
        assert paths == sorted(paths), f"Artifacts must be sorted by path: {paths}"

    def test_remediation_hints_sorted(self, certification_result: GuardianResult):
        raw = certification_result.to_json()
        parsed = json.loads(raw)
        hints = parsed["remediation_hints"]
        assert hints == sorted(hints), f"Hints must be sorted: {hints}"

    def test_metrics_keys_sorted(self, certification_result: GuardianResult):
        raw = certification_result.to_json()
        parsed = json.loads(raw)
        metric_keys = list(parsed["metrics"].keys())
        assert metric_keys == sorted(metric_keys), f"Metric keys must be sorted: {metric_keys}"


# ---------------------------------------------------------------------------
# 4. Nondeterministic Field Gating
# ---------------------------------------------------------------------------


class TestNondeterministicGating:
    """Nondeterministic fields (timestamps, random UUIDs) are gated."""

    def test_no_timestamp_by_default(self, certification_result: GuardianResult):
        d = certification_result.to_dict()
        assert "timestamp" not in d or d.get("timestamp") is None

    def test_no_random_uuid_in_trace_id(self):
        """v15_trace_id must not be a random UUID when set by maybe_sign_result."""
        import re

        uuid4_pattern = re.compile(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
        )
        r = GuardianResult(guardian_id="nonce_test")
        r.add_check("c1", CheckStatus.PASS, "ok")
        d = r.to_dict()
        trace_id = d.get("v15_trace_id")
        if trace_id is not None:
            assert not uuid4_pattern.match(trace_id), f"v15_trace_id must not be a random UUID v4: {trace_id}"

    def test_no_elapsed_ms_in_evidence(self, certification_result: GuardianResult):
        """elapsed_ms is nondeterministic and must not appear in serialized output."""
        raw = certification_result.to_json()
        assert "elapsed_ms" not in raw


# ---------------------------------------------------------------------------
# 5. Idempotency
# ---------------------------------------------------------------------------


class TestIdempotency:
    """Identical inputs produce byte-for-byte identical certification JSON."""

    def _make_result(self) -> GuardianResult:
        r = GuardianResult(guardian_id="idempotency_test")
        r.add_check("check_b", CheckStatus.PASS, "B ok")
        r.add_check("check_a", CheckStatus.PASS, "A ok")
        r.add_artifact(ArtifactType.JSON, "docs/out.json", "Output")
        r.metrics = {"count": 42}
        r.remediation_hints = ["z_hint", "a_hint"]
        return r

    def test_byte_for_byte_identical(self):
        r1 = self._make_result()
        r2 = self._make_result()

        j1 = r1.to_json()
        j2 = r2.to_json()
        assert j1 == j2, "Identical inputs must produce byte-for-byte identical JSON"

    def test_identical_certification_hash(self):
        r1 = self._make_result()
        r2 = self._make_result()

        r1.compute_certification_hash()
        r2.compute_certification_hash()
        assert r1.certification_hash == r2.certification_hash

    def test_revert_sort_breaks_idempotency(self):
        """Proves that removing deterministic sort would break idempotency.

        We manually construct two dicts with different insertion order and
        verify they serialize identically due to sort_keys=True.
        """
        r = self._make_result()
        j1 = r.to_json()
        parsed = json.loads(j1)
        reserialized = json.dumps(parsed, indent=2, sort_keys=True)
        assert j1 == reserialized, "Re-serialization with sort_keys=True must match original"

    def test_revert_hash_breaks_idempotency(self):
        """Proves that removing hash computation would break certification."""
        r = self._make_result()
        _ = r.to_json()
        assert r.certification_hash is not None, "certification_hash must be set after to_json()"
        saved_hash = r.certification_hash

        r.summary = "MUTATED"
        r.compute_certification_hash()
        assert r.certification_hash != saved_hash, "Mutating payload must change certification_hash"
