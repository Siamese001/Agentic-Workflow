"""
Phase 4 — Wave 2 Tests: Versioned pattern compatibility enforcement.
"""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
)
from agentic_core.L2_execution.types.ml_pattern_record_types import (
    MLPatternRecord,
    PatternCompatibilityError,
    enforce_pattern_compatibility,
)
from agentic_core.L4_state.config.versioned_configs import (
    get_active_configs,
)

pytestmark = pytest.mark.unit_min_deps


def _active_hashes() -> tuple[str, str]:
    """Return (policy_hash, model_hash) from the L4 SSOT."""
    cfg = get_active_configs()
    return cfg.policy.config_hash, cfg.model.config_hash


def _record(
    domain_id: str = AGENTIC_CORE_DIR,
    policy_hash: str | None = None,
    model_hash: str | None = None,
    pattern_id: str = "p-001",
    payload: dict | None = None,
) -> MLPatternRecord:
    ph, mh = _active_hashes()
    return MLPatternRecord.build(
        domain_id=domain_id,
        policy_hash=policy_hash if policy_hash is not None else ph,
        model_hash=model_hash if model_hash is not None else mh,
        pattern_id=pattern_id,
        payload=payload or {"strategy": "fix_import"},
    )


class TestMLPatternRecord:
    def test_build_produces_valid_record(self):
        rec = _record()
        assert rec.schema_version == 1
        assert rec.domain_id == AGENTIC_CORE_DIR
        assert len(rec.domain_hash) == 64
        assert len(rec.policy_hash) == 64
        assert len(rec.model_hash) == 64
        assert len(rec.record_hash) == 64

    def test_domain_hash_is_deterministic(self):
        h1 = MLPatternRecord.compute_domain_hash(AGENTIC_CORE_DIR)
        h2 = MLPatternRecord.compute_domain_hash(AGENTIC_CORE_DIR)
        assert h1 == h2

    def test_different_domains_produce_different_hashes(self):
        h1 = MLPatternRecord.compute_domain_hash(AGENTIC_CORE_DIR)
        h2 = MLPatternRecord.compute_domain_hash(APPS_RG_DIR)
        assert h1 != h2

    def test_record_hash_stable(self):
        rec1 = _record(pattern_id="p-stable")
        rec2 = _record(pattern_id="p-stable")
        assert rec1.record_hash == rec2.record_hash

    def test_record_hash_changes_with_payload(self):
        rec1 = _record(payload={"strategy": "A"})
        rec2 = _record(payload={"strategy": "B"})
        assert rec1.record_hash != rec2.record_hash

    def test_canonical_bytes_excludes_record_hash(self):
        rec = _record()
        assert rec.record_hash.encode() not in rec.canonical_bytes()
        assert b"record_hash" not in rec.canonical_bytes()

    def test_rejects_empty_domain_id(self):
        ph, mh = _active_hashes()
        with pytest.raises(ValueError, match="domain_id"):
            MLPatternRecord(
                schema_version=1,
                domain_id="",
                domain_hash="a" * 64,
                policy_hash=ph,
                model_hash=mh,
                pattern_id="p",
                payload={},
                record_hash="b" * 64,
            )

    def test_rejects_bad_schema_version(self):
        ph, mh = _active_hashes()
        with pytest.raises(ValueError, match="schema_version"):
            MLPatternRecord(
                schema_version=0,
                domain_id=AGENTIC_CORE_DIR,
                domain_hash="a" * 64,
                policy_hash=ph,
                model_hash=mh,
                pattern_id="p",
                payload={},
                record_hash="b" * 64,
            )


class TestPatternCompatibilityEnforcement:
    def test_compatible_pattern_passes(self):
        rec = _record(domain_id=AGENTIC_CORE_DIR)
        ph, mh = _active_hashes()
        enforce_pattern_compatibility(rec, AGENTIC_CORE_DIR, ph, mh)

    def test_pattern_retrieval_filters_by_domain_hash(self):
        """
        Pattern stored for domain 'apps_rg' must be rejected when
        queried from domain 'agentic_core'.
        """
        ph, mh = _active_hashes()
        rec = _record(domain_id=APPS_RG_DIR)
        with pytest.raises(PatternCompatibilityError) as exc_info:
            enforce_pattern_compatibility(rec, AGENTIC_CORE_DIR, ph, mh)
        assert exc_info.value.violation_code == PatternCompatibilityError.DOMAIN_MISMATCH
        assert "DOMAIN_HASH_MISMATCH" in str(exc_info.value)

    def test_pattern_retrieval_rejects_policy_hash_mismatch(self):
        """
        Pattern with stale policy_hash must be rejected deterministically.
        """
        _, mh = _active_hashes()
        stale_policy_hash = "a" * 64
        rec = _record(policy_hash=stale_policy_hash)
        active_ph, _ = _active_hashes()
        with pytest.raises(PatternCompatibilityError) as exc_info:
            enforce_pattern_compatibility(rec, AGENTIC_CORE_DIR, active_ph, mh)
        assert exc_info.value.violation_code == PatternCompatibilityError.POLICY_MISMATCH
        assert "POLICY_HASH_MISMATCH" in str(exc_info.value)

    def test_pattern_retrieval_rejects_model_hash_mismatch(self):
        """
        Pattern with stale model_hash must be rejected deterministically.
        """
        ph, _ = _active_hashes()
        stale_model_hash = "b" * 64
        rec = _record(model_hash=stale_model_hash)
        _, active_mh = _active_hashes()
        with pytest.raises(PatternCompatibilityError) as exc_info:
            enforce_pattern_compatibility(rec, AGENTIC_CORE_DIR, ph, active_mh)
        assert exc_info.value.violation_code == PatternCompatibilityError.MODEL_MISMATCH
        assert "MODEL_HASH_MISMATCH" in str(exc_info.value)

    def test_domain_mismatch_takes_priority_over_policy(self):
        """Domain check runs first; wrong domain raises DOMAIN_HASH_MISMATCH."""
        stale_ph = "c" * 64
        _, mh = _active_hashes()
        rec = _record(domain_id=APPS_LIC_DIR, policy_hash=stale_ph)
        active_ph, _ = _active_hashes()
        with pytest.raises(PatternCompatibilityError) as exc_info:
            enforce_pattern_compatibility(rec, AGENTIC_CORE_DIR, active_ph, mh)
        assert exc_info.value.violation_code == PatternCompatibilityError.DOMAIN_MISMATCH

    def test_apps_rg_domain_compatible_with_apps_rg_query(self):
        ph, mh = _active_hashes()
        rec = _record(domain_id=APPS_RG_DIR)
        enforce_pattern_compatibility(rec, APPS_RG_DIR, ph, mh)

    def test_violation_code_constants(self):
        assert PatternCompatibilityError.DOMAIN_MISMATCH == "DOMAIN_HASH_MISMATCH"
        assert PatternCompatibilityError.POLICY_MISMATCH == "POLICY_HASH_MISMATCH"
        assert PatternCompatibilityError.MODEL_MISMATCH == "MODEL_HASH_MISMATCH"

    def test_policy_hash_from_active_config_matches(self):
        """Active PolicyConfig hash must match what's stored in a fresh record."""
        ph, mh = _active_hashes()
        rec = _record()
        assert rec.policy_hash == ph

    def test_model_hash_from_active_config_matches(self):
        """Active ModelConfig hash must match what's stored in a fresh record."""
        ph, mh = _active_hashes()
        rec = _record()
        assert rec.model_hash == mh
