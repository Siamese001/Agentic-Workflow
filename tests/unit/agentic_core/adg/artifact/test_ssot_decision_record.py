"""Unit tests for SSOTDecisionRecord (cross-bucket reconciliation).

Coverage:

* Closed enum: ``Outcome`` has exactly 8 values; severity map is total.
* Reconciler: every cell of the 3-axis (FOUND × ALLOWED × USED) matrix
  resolves to the spec-defined outcome.
* Determinism: ``manifest_hash`` is order-independent and reproducible;
  ``replay_key`` is reproducible; ``hmac_sig`` is deterministic for a
  fixed secret.
* Construction: ``SSOTDecisionRecord.build()`` populates all derived
  fields; optional fields default to None.
* Persistence: ``to_db_row()`` round-trips through the SQLite schema.
"""

from __future__ import annotations

import hashlib
import sqlite3
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agentic_core.adg.artifact.ssot_decision_record import (  # noqa: E402
    ALL_OUTCOMES,
    OUTCOME_SEVERITY,
    SQL_CREATE_SSOT_DECISION_RECORDS,
    SQL_INSERT_SSOT_DECISION_RECORD,
    Outcome,
    SSOTDecisionRecord,
    compute_hmac_sig,
    compute_manifest_hash,
    compute_replay_key,
    reconcile_from_refs,
    reconcile_outcome,
)


# ---------------------------------------------------------------------------
# Closed-enum invariants
# ---------------------------------------------------------------------------


class TestOutcomeEnum:
    def test_has_exactly_eight_outcomes(self) -> None:
        assert len(ALL_OUTCOMES) == 8

    def test_outcomes_match_spec(self) -> None:
        assert ALL_OUTCOMES == frozenset(
            {
                "VALID_USE",
                "ALLOWED_NOT_USED",
                "POLICY_BYPASS",
                "BLOCKED_UNUSED",
                "HIDDEN_PATH",
                "REGISTRY_DRIFT",
                "SEVERE_BYPASS",
                "CLEAN_ABSENCE",
            }
        )

    def test_severity_map_covers_every_outcome(self) -> None:
        assert set(OUTCOME_SEVERITY.keys()) == ALL_OUTCOMES

    def test_severity_levels_match_spec(self) -> None:
        assert OUTCOME_SEVERITY["POLICY_BYPASS"] == "INCIDENT"
        assert OUTCOME_SEVERITY["SEVERE_BYPASS"] == "CRITICAL"
        assert OUTCOME_SEVERITY["HIDDEN_PATH"] == "INTEGRITY"
        assert OUTCOME_SEVERITY["VALID_USE"] == "gold"

    def test_outcome_serializes_as_string(self) -> None:
        # Outcome inherits from str so it serializes cleanly.
        assert Outcome.VALID_USE == "VALID_USE"
        assert Outcome.SEVERE_BYPASS == "SEVERE_BYPASS"


# ---------------------------------------------------------------------------
# 8-cell decision matrix — exhaustive test of the reconciler
# ---------------------------------------------------------------------------


class TestDecisionMatrix:
    """Exhaustive test of the 3-axis (FOUND × ALLOWED × USED) matrix.

    Eight rows; each row is one cell of the matrix; the test name encodes
    the axis values and the expected outcome.
    """

    def test_found_allowed_used_yields_valid_use(self) -> None:
        # Gold path — proof of compliant use.
        assert reconcile_outcome(found=True, allowed=True, used=True) == Outcome.VALID_USE

    def test_found_allowed_not_used_yields_allowed_not_used(self) -> None:
        # Capability declared and present, no runtime evidence.
        assert reconcile_outcome(found=True, allowed=True, used=False) == Outcome.ALLOWED_NOT_USED

    def test_found_blocked_used_yields_policy_bypass(self) -> None:
        # INCIDENT — policy says no, code uses it anyway.
        assert reconcile_outcome(found=True, allowed=False, used=True) == Outcome.POLICY_BYPASS

    def test_found_blocked_not_used_yields_blocked_unused(self) -> None:
        assert reconcile_outcome(found=True, allowed=False, used=False) == Outcome.BLOCKED_UNUSED

    def test_not_found_allowed_used_yields_hidden_path(self) -> None:
        # INTEGRITY — runtime executed something the static graph does
        # not see. Stale ADG snapshot or instrumentation error.
        assert reconcile_outcome(found=False, allowed=True, used=True) == Outcome.HIDDEN_PATH

    def test_not_found_allowed_not_used_yields_registry_drift(self) -> None:
        # Hygiene — registry declares it, code does not exist, no runtime.
        assert reconcile_outcome(found=False, allowed=True, used=False) == Outcome.REGISTRY_DRIFT

    def test_not_found_blocked_used_yields_severe_bypass(self) -> None:
        # CRITICAL — runtime saw something not declared and not allowed.
        assert reconcile_outcome(found=False, allowed=False, used=True) == Outcome.SEVERE_BYPASS

    def test_not_found_blocked_not_used_yields_clean_absence(self) -> None:
        assert reconcile_outcome(found=False, allowed=False, used=False) == Outcome.CLEAN_ABSENCE


class TestReconcilerFromRefs:
    """Test ``reconcile_from_refs()`` derives axes correctly from ref lists."""

    def test_empty_static_yields_not_found(self) -> None:
        out = reconcile_from_refs(static_refs=[], runtime_refs=["r1"], registry_refs=["g1"])
        # NOT_FOUND + ALLOWED + USED → HIDDEN_PATH
        assert out == Outcome.HIDDEN_PATH

    def test_nonempty_static_yields_found(self) -> None:
        out = reconcile_from_refs(static_refs=["s1"], runtime_refs=["r1"], registry_refs=["g1"])
        # FOUND + ALLOWED + USED → VALID_USE
        assert out == Outcome.VALID_USE

    def test_empty_registry_yields_blocked(self) -> None:
        out = reconcile_from_refs(static_refs=["s1"], runtime_refs=["r1"], registry_refs=[])
        # FOUND + BLOCKED + USED → POLICY_BYPASS
        assert out == Outcome.POLICY_BYPASS

    def test_registry_present_but_non_authoritative_yields_blocked(self) -> None:
        # Stale registry counts as BLOCKED.
        out = reconcile_from_refs(
            static_refs=["s1"],
            runtime_refs=["r1"],
            registry_refs=["g1"],
            registry_authoritative=False,
        )
        assert out == Outcome.POLICY_BYPASS

    def test_runtime_present_but_non_authoritative_yields_not_used(self) -> None:
        # Missing-trace runtime counts as NOT_USED.
        out = reconcile_from_refs(
            static_refs=["s1"],
            runtime_refs=["r1"],
            registry_refs=["g1"],
            runtime_authoritative=False,
        )
        # FOUND + ALLOWED + NOT_USED → ALLOWED_NOT_USED
        assert out == Outcome.ALLOWED_NOT_USED

    def test_all_empty_yields_clean_absence(self) -> None:
        out = reconcile_from_refs(static_refs=[], runtime_refs=[], registry_refs=[])
        assert out == Outcome.CLEAN_ABSENCE

    def test_only_runtime_yields_severe_bypass(self) -> None:
        out = reconcile_from_refs(static_refs=[], runtime_refs=["r1"], registry_refs=[])
        # NOT_FOUND + BLOCKED + USED → SEVERE_BYPASS
        assert out == Outcome.SEVERE_BYPASS

    def test_only_registry_yields_registry_drift(self) -> None:
        out = reconcile_from_refs(static_refs=[], runtime_refs=[], registry_refs=["g1"])
        # NOT_FOUND + ALLOWED + NOT_USED → REGISTRY_DRIFT
        assert out == Outcome.REGISTRY_DRIFT


# ---------------------------------------------------------------------------
# Determinism helpers
# ---------------------------------------------------------------------------


class TestManifestHash:
    """The manifest_hash MUST be deterministic and order-independent."""

    BASE = {
        "static_refs": ["s2", "s1"],
        "runtime_refs": ["r1", "r2"],
        "registry_refs": ["g1"],
        "policy_hash": "policy-1",
        "blueprint_hash": "blueprint-1",
        "registry_digest_set": ["digest-A", "digest-B"],
    }

    def test_manifest_hash_is_64_hex_chars(self) -> None:
        h = compute_manifest_hash(**self.BASE)
        assert len(h) == 64
        int(h, 16)  # raises if not hex

    def test_manifest_hash_is_order_independent(self) -> None:
        h1 = compute_manifest_hash(**self.BASE)
        h2 = compute_manifest_hash(
            static_refs=["s1", "s2"],
            runtime_refs=["r2", "r1"],
            registry_refs=["g1"],
            policy_hash="policy-1",
            blueprint_hash="blueprint-1",
            registry_digest_set=["digest-B", "digest-A"],
        )
        assert h1 == h2, "manifest_hash MUST be order-independent"

    def test_manifest_hash_changes_with_policy(self) -> None:
        h1 = compute_manifest_hash(**self.BASE)
        h2 = compute_manifest_hash(**{**self.BASE, "policy_hash": "policy-2"})
        assert h1 != h2

    def test_manifest_hash_changes_with_static_refs(self) -> None:
        h1 = compute_manifest_hash(**self.BASE)
        h2 = compute_manifest_hash(**{**self.BASE, "static_refs": ["s99"]})
        assert h1 != h2


class TestReplayKey:
    """The replay_key MUST be deterministic for fixed inputs."""

    def test_replay_key_is_64_hex_chars(self) -> None:
        k = compute_replay_key(
            request_id="req-1",
            run_id="run-1",
            route_contract_id="route-1",
            policy_hash="policy-1",
        )
        assert len(k) == 64
        int(k, 16)

    def test_replay_key_is_reproducible(self) -> None:
        kwargs = dict(
            request_id="req-1",
            run_id="run-1",
            route_contract_id="route-1",
            policy_hash="policy-1",
        )
        assert compute_replay_key(**kwargs) == compute_replay_key(**kwargs)

    def test_replay_key_changes_with_run_id(self) -> None:
        k1 = compute_replay_key(
            request_id="req-1",
            run_id="run-1",
            route_contract_id="route-1",
            policy_hash="policy-1",
        )
        k2 = compute_replay_key(
            request_id="req-1",
            run_id="run-2",
            route_contract_id="route-1",
            policy_hash="policy-1",
        )
        assert k1 != k2


class TestHmacSig:
    """HMAC signature MUST be deterministic and depend on secret + manifest."""

    def test_hmac_sig_is_64_hex_chars(self) -> None:
        sig = compute_hmac_sig(manifest_hash="abc123", secret="test-secret")
        assert len(sig) == 64
        int(sig, 16)

    def test_hmac_sig_is_deterministic_for_same_secret(self) -> None:
        s1 = compute_hmac_sig(manifest_hash="abc123", secret="secret-1")
        s2 = compute_hmac_sig(manifest_hash="abc123", secret="secret-1")
        assert s1 == s2

    def test_hmac_sig_changes_with_secret(self) -> None:
        s1 = compute_hmac_sig(manifest_hash="abc123", secret="secret-1")
        s2 = compute_hmac_sig(manifest_hash="abc123", secret="secret-2")
        assert s1 != s2

    def test_hmac_sig_changes_with_manifest(self) -> None:
        s1 = compute_hmac_sig(manifest_hash="hash-1", secret="secret-1")
        s2 = compute_hmac_sig(manifest_hash="hash-2", secret="secret-1")
        assert s1 != s2

    def test_hmac_sig_uses_env_var_when_no_secret_given(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ADG_SSOT_HMAC_KEY", "from-env")
        s_env = compute_hmac_sig(manifest_hash="abc123")
        s_explicit = compute_hmac_sig(manifest_hash="abc123", secret="from-env")
        assert s_env == s_explicit


# ---------------------------------------------------------------------------
# SSOTDecisionRecord.build()
# ---------------------------------------------------------------------------


class TestRecordBuild:
    BASE_KW = dict(
        request_id="req-001",
        run_id="run-001",
        trace_id="trace-001",
        route_contract_id="route-001",
        policy_hash="policy-hash-1",
        blueprint_hash="blueprint-hash-1",
        registry_digest_set=["digest-1", "digest-2"],
    )

    def test_build_with_all_required_fields(self) -> None:
        rec = SSOTDecisionRecord.build(
            **self.BASE_KW,
            static_refs=["s1"],
            runtime_refs=["r1"],
            registry_refs=["g1"],
        )
        assert rec.request_id == "req-001"
        assert rec.outcome == "VALID_USE"
        assert len(rec.manifest_hash) == 64
        assert len(rec.replay_key) == 64
        assert len(rec.hmac_sig) == 64

    def test_build_optional_fields_default_to_none(self) -> None:
        rec = SSOTDecisionRecord.build(
            **self.BASE_KW,
            static_refs=["s1"],
            runtime_refs=["r1"],
            registry_refs=["g1"],
        )
        assert rec.evidence_contract_ref is None
        assert rec.prompt_artifact_ref is None
        assert rec.sealed_l2_artifact_ref is None
        assert rec.exit_review_packet_ref is None
        assert rec.x3_disposition is None
        assert rec.uwg_commit_receipt_ref is None

    def test_build_populates_optional_fields_when_supplied(self) -> None:
        rec = SSOTDecisionRecord.build(
            **self.BASE_KW,
            static_refs=["s1"],
            runtime_refs=["r1"],
            registry_refs=["g1"],
            evidence_contract_ref="evidence-001",
            prompt_artifact_ref="prompt-001",
            sealed_l2_artifact_ref="L2-sealed-001",
            exit_review_packet_ref="exit-review-001",
            x3_disposition="approved",
            uwg_commit_receipt_ref="uwg-receipt-001",
        )
        assert rec.evidence_contract_ref == "evidence-001"
        assert rec.uwg_commit_receipt_ref == "uwg-receipt-001"

    def test_build_outcome_matches_reconciler(self) -> None:
        # Empty static + nonempty runtime + empty registry → SEVERE_BYPASS.
        rec = SSOTDecisionRecord.build(
            **self.BASE_KW,
            static_refs=[],
            runtime_refs=["r1"],
            registry_refs=[],
        )
        assert rec.outcome == "SEVERE_BYPASS"

    def test_build_record_is_frozen(self) -> None:
        rec = SSOTDecisionRecord.build(
            **self.BASE_KW,
            static_refs=["s1"],
            runtime_refs=["r1"],
            registry_refs=["g1"],
        )
        # frozen=True dataclass — assignment to any field must raise.
        try:
            rec.request_id = "new-id"  # type: ignore[misc]
        except (AttributeError, Exception):
            return
        raise AssertionError("frozen=True should prevent mutation")

    def test_build_replay_key_stable_for_same_inputs(self) -> None:
        rec1 = SSOTDecisionRecord.build(
            **self.BASE_KW,
            static_refs=["s1"],
            runtime_refs=["r1"],
            registry_refs=["g1"],
        )
        rec2 = SSOTDecisionRecord.build(
            **self.BASE_KW,
            static_refs=["s1"],
            runtime_refs=["r1"],
            registry_refs=["g1"],
        )
        # Same identifiers → same replay_key.
        assert rec1.replay_key == rec2.replay_key
        # Same constituent evidence → same manifest_hash → same hmac_sig
        # (assuming same env-derived secret).
        assert rec1.manifest_hash == rec2.manifest_hash


# ---------------------------------------------------------------------------
# Persistence — round-trip through the SQLite schema
# ---------------------------------------------------------------------------


class TestPersistence:
    BASE_KW = dict(
        request_id="req-001",
        run_id="run-001",
        trace_id="trace-001",
        route_contract_id="route-001",
        policy_hash="policy-hash-1",
        blueprint_hash="blueprint-hash-1",
        registry_digest_set=["digest-1"],
    )

    @staticmethod
    def _build_db() -> sqlite3.Connection:
        con = sqlite3.connect(":memory:")
        con.executescript(SQL_CREATE_SSOT_DECISION_RECORDS)
        return con

    def test_schema_creates_without_error(self) -> None:
        con = self._build_db()
        # Inspect schema.
        cols = [r[1] for r in con.execute("PRAGMA table_info(ssot_decision_records)").fetchall()]
        # All required + optional columns must exist.
        for required in [
            "request_id",
            "run_id",
            "trace_id",
            "route_contract_id",
            "policy_hash",
            "blueprint_hash",
            "registry_digest_set",
            "static_refs",
            "runtime_refs",
            "registry_refs",
            "replay_key",
            "manifest_hash",
            "hmac_sig",
            "outcome",
        ]:
            assert required in cols, f"required column {required} missing"
        for optional in [
            "evidence_contract_ref",
            "prompt_artifact_ref",
            "sealed_l2_artifact_ref",
            "exit_review_packet_ref",
            "x3_disposition",
            "uwg_commit_receipt_ref",
        ]:
            assert optional in cols, f"optional column {optional} missing"

    def test_indexes_exist(self) -> None:
        con = self._build_db()
        idx = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='index'").fetchall()]
        for required in [
            "idx_ssot_run",
            "idx_ssot_trace",
            "idx_ssot_request",
            "idx_ssot_outcome",
            "idx_ssot_replay_key",
            "idx_ssot_manifest",
        ]:
            assert required in idx, f"index {required} missing"

    def test_insert_round_trip(self) -> None:
        con = self._build_db()
        rec = SSOTDecisionRecord.build(
            **self.BASE_KW,
            static_refs=["s1", "s2"],
            runtime_refs=["r1"],
            registry_refs=["g1"],
            x3_disposition="approved",
        )
        con.execute(SQL_INSERT_SSOT_DECISION_RECORD, rec.to_db_row())
        con.commit()
        row = con.execute(
            "SELECT request_id, run_id, outcome, replay_key, manifest_hash, hmac_sig, x3_disposition "
            "FROM ssot_decision_records WHERE request_id=?",
            ("req-001",),
        ).fetchone()
        assert row is not None
        rid, run, outcome, replay, manifest, sig, x3 = row
        assert rid == "req-001"
        assert run == "run-001"
        assert outcome == "VALID_USE"
        assert replay == rec.replay_key
        assert manifest == rec.manifest_hash
        assert sig == rec.hmac_sig
        assert x3 == "approved"

    def test_outcome_index_query_works(self) -> None:
        con = self._build_db()
        # Insert one record per outcome.
        outcomes = [
            ([], [], []),  # CLEAN_ABSENCE
            (["s"], ["r"], ["g"]),  # VALID_USE
            ([], ["r"], []),  # SEVERE_BYPASS
        ]
        for i, (s, r, g) in enumerate(outcomes):
            rec = SSOTDecisionRecord.build(
                **{**self.BASE_KW, "request_id": f"req-{i}"},
                static_refs=s,
                runtime_refs=r,
                registry_refs=g,
            )
            con.execute(SQL_INSERT_SSOT_DECISION_RECORD, rec.to_db_row())
        con.commit()
        bypass_count = con.execute(
            "SELECT COUNT(*) FROM ssot_decision_records WHERE outcome='SEVERE_BYPASS'"
        ).fetchone()[0]
        assert bypass_count == 1


# ---------------------------------------------------------------------------
# Tamper detection — manifest_hash mismatches surface
# ---------------------------------------------------------------------------


class TestTamperDetection:
    """If anyone tampers with the constituent evidence, recomputing
    manifest_hash MUST produce a different value."""

    BASE_KW = dict(
        request_id="req-001",
        run_id="run-001",
        trace_id="trace-001",
        route_contract_id="route-001",
        policy_hash="policy-hash-1",
        blueprint_hash="blueprint-hash-1",
        registry_digest_set=["digest-1"],
    )

    def test_tampering_with_static_refs_changes_manifest_hash(self) -> None:
        rec = SSOTDecisionRecord.build(
            **self.BASE_KW,
            static_refs=["s1"],
            runtime_refs=["r1"],
            registry_refs=["g1"],
        )
        # Recompute as if static_refs had been tampered with post-record.
        tampered_hash = compute_manifest_hash(
            static_refs=["s1", "evil-s2"],
            runtime_refs=["r1"],
            registry_refs=["g1"],
            policy_hash=rec.policy_hash,
            blueprint_hash=rec.blueprint_hash,
            registry_digest_set=rec.registry_digest_set,
        )
        assert rec.manifest_hash != tampered_hash

    def test_hmac_sig_verifies_manifest_hash(self) -> None:
        rec = SSOTDecisionRecord.build(
            **self.BASE_KW,
            static_refs=["s1"],
            runtime_refs=["r1"],
            registry_refs=["g1"],
        )
        # Re-compute hmac_sig from the recorded manifest_hash with the
        # same dev secret. They must match (verifying the record was
        # not partially tampered).
        recomputed = compute_hmac_sig(manifest_hash=rec.manifest_hash)
        assert rec.hmac_sig == recomputed
