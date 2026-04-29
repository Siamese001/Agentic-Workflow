"""Unit tests for agentic_core.adg.ci.gate_result."""

from __future__ import annotations

import json
import pytest

from agentic_core.adg.ci.gate_result import (
    GateResult,
    RollupResult,
    VALID_BUCKETS,
    VALID_STATUSES,
    VALID_EVIDENCE_MODES,
    VALID_ENFORCEMENT_MODES,
    gate_result_from_dict,
)


class TestGateResultConstruction:
    def test_minimal_construction(self):
        r = GateResult(
            gate_id="static.test",
            bucket="static",
            status="PASS",
        )
        assert r.gate_id == "static.test"
        assert r.bucket == "static"
        assert r.status == "PASS"
        assert r.evidence_mode == "inventory"
        assert r.enforcement_mode == "advisory"
        assert r.started_at  # auto-populated

    def test_invalid_status_raises(self):
        with pytest.raises(ValueError, match="status"):
            GateResult(gate_id="g", bucket="static", status="MAYBE")

    def test_invalid_bucket_raises(self):
        with pytest.raises(ValueError, match="bucket"):
            GateResult(gate_id="g", bucket="nonsense", status="PASS")

    def test_invalid_evidence_mode_raises(self):
        with pytest.raises(ValueError, match="evidence_mode"):
            GateResult(
                gate_id="g", bucket="static", status="PASS",
                evidence_mode="hopeful",
            )

    def test_invalid_enforcement_mode_raises(self):
        with pytest.raises(ValueError, match="enforcement_mode"):
            GateResult(
                gate_id="g", bucket="static", status="PASS",
                enforcement_mode="laissez_faire",
            )

    def test_pass_with_actual_fail_reason_raises(self):
        with pytest.raises(ValueError, match="actual_fail_reason"):
            GateResult(
                gate_id="g", bucket="static", status="PASS",
                actual_fail_reason="this should not be set",
            )

    def test_fail_without_actual_fail_reason_raises(self):
        with pytest.raises(ValueError, match="actual_fail_reason"):
            GateResult(gate_id="g", bucket="static", status="FAIL")

    def test_sample_failures_truncated_to_10(self):
        r = GateResult(
            gate_id="g",
            bucket="static",
            status="FAIL",
            actual_fail_reason="too_many",
            sample_failures=[{"i": i} for i in range(50)],
        )
        assert len(r.sample_failures) == 10

    def test_finalize_computes_artifact_hash(self):
        r = GateResult(gate_id="g", bucket="static", status="PASS").finalize()
        assert len(r.artifact_hash) == 16
        assert all(c in "0123456789abcdef" for c in r.artifact_hash)

    def test_finalize_is_deterministic(self):
        r1 = GateResult(
            gate_id="g", bucket="static", status="PASS",
            started_at="2026-04-29T00:00:00+00:00",
        ).finalize()
        r2 = GateResult(
            gate_id="g", bucket="static", status="PASS",
            started_at="2026-04-29T00:00:00+00:00",
        ).finalize()
        assert r1.artifact_hash == r2.artifact_hash

    def test_finalize_changes_with_payload(self):
        r1 = GateResult(
            gate_id="g", bucket="static", status="PASS",
            started_at="2026-04-29T00:00:00+00:00",
            counts={"a": 1},
        ).finalize()
        r2 = GateResult(
            gate_id="g", bucket="static", status="PASS",
            started_at="2026-04-29T00:00:00+00:00",
            counts={"a": 2},
        ).finalize()
        assert r1.artifact_hash != r2.artifact_hash


class TestGateResultRoundtrip:
    def test_to_json_then_from_dict(self):
        r = GateResult(
            gate_id="reg.x",
            bucket="registry",
            status="WARN",
            evidence_mode="proof",
            enforcement_mode="strict",
            counts={"n": 5},
            sample_failures=[{"why": "demo"}],
            bypass_env_detected=["FOO_BYPASS"],
        ).finalize()

        rebuilt = gate_result_from_dict(r.to_json())
        assert rebuilt.gate_id == r.gate_id
        assert rebuilt.bucket == r.bucket
        assert rebuilt.status == r.status
        assert rebuilt.counts == r.counts
        assert rebuilt.bypass_env_detected == r.bypass_env_detected
        assert rebuilt.artifact_hash == r.artifact_hash

    def test_from_dict_missing_required_raises(self):
        with pytest.raises(ValueError, match="missing required"):
            gate_result_from_dict({"gate_id": "g", "bucket": "static"})

    def test_from_dict_invalid_status_raises(self):
        with pytest.raises(ValueError, match="status"):
            gate_result_from_dict(
                {"gate_id": "g", "bucket": "static", "status": "BOGUS"}
            )

    def test_from_dict_tolerates_extra_keys(self):
        # Forward compatibility — runner should not break on unknown future keys.
        rebuilt = gate_result_from_dict({
            "gate_id": "g",
            "bucket": "static",
            "status": "PASS",
            "future_field_42": "ignore_me",
        })
        assert rebuilt.gate_id == "g"


class TestEnums:
    def test_buckets_complete(self):
        # Spec requires every bucket from the user request.
        for b in (
            "static", "registry", "runtime", "cross_bucket",
            "provenance", "schema", "preflight",
        ):
            assert b in VALID_BUCKETS

    def test_statuses_complete(self):
        for s in ("PASS", "FAIL", "WARN", "SKIP", "ERROR"):
            assert s in VALID_STATUSES

    def test_evidence_modes(self):
        assert VALID_EVIDENCE_MODES == frozenset({"proof", "risk", "inventory"})

    def test_enforcement_modes(self):
        assert VALID_ENFORCEMENT_MODES == frozenset(
            {"strict", "advisory", "ratchet", "audit"}
        )


class TestRollupResult:
    def test_to_json_serializable(self):
        rollup = RollupResult(
            suite="quick",
            snapshot_id="snap_1",
            started_at="2026-04-29T00:00:00+00:00",
            overall_status="PASS",
        )
        # Must round-trip through json.dumps.
        s = json.dumps(rollup.to_json())
        assert json.loads(s)["suite"] == "quick"
