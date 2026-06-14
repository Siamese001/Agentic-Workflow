"""Wave 4.2 — unit tests for apps_rg.cache.r1b_models.

Covers the R1B ROLE_TARGET_RUN grain records: HistoricalIntentRecord and
HistoricalOutputChunk to_dict/from_dict round trips, schema-version defaults,
and the child-chunk independent_cache_identity firewall invariant.
"""

from __future__ import annotations

from apps_rg.cache.r1b_constants import (
    APP_ID_APPS_RG,
    CACHE_GRAIN_ROLE_TARGET_RUN,
    CACHE_SCHEMA_VERSION,
)
from apps_rg.cache.r1b_models import HistoricalIntentRecord, HistoricalOutputChunk


def _intent(**overrides) -> HistoricalIntentRecord:
    base = dict(
        record_id="rec1",
        app_id=APP_ID_APPS_RG,
        cache_grain=CACHE_GRAIN_ROLE_TARGET_RUN,
        request_intent_text="text",
        normalized_intent_digest="d",
        request_intent_vector_ref="v",
        source_run_id="run1",
        target_company="Acme",
        target_role="SVP",
        job_family="eng",
        jd_digest="jd",
        briefing_digest="br",
        srfs_digest="srfs",
        proof_pool_digest="pp",
        skills_ledger_digest="sk",
        base_resume_digest="base",
        final_resume_digest="final",
        prompt_profile_hash="pph",
        model_profile_hash="mph",
        gate_profile_hash="gph",
        x3_disposition="X3_ALLOW",
        proof_eligible=True,
        cache_admissible=True,
        generated_at_utc="2026-01-01T00:00:00Z",
    )
    base.update(overrides)
    return HistoricalIntentRecord(**base)


class TestHistoricalIntentRecord:
    def test_schema_version_default(self) -> None:
        assert _intent().schema_version == CACHE_SCHEMA_VERSION

    def test_non_admissible_reason_default_empty(self) -> None:
        assert _intent().non_admissible_reason == ""

    def test_to_dict_round_trip(self) -> None:
        rec = _intent()
        restored = HistoricalIntentRecord.from_dict(rec.to_dict())
        assert restored == rec

    def test_from_dict_fills_app_and_grain_defaults(self) -> None:
        data = _intent().to_dict()
        del data["app_id"]
        del data["cache_grain"]
        del data["schema_version"]
        restored = HistoricalIntentRecord.from_dict(data)
        assert restored.app_id == APP_ID_APPS_RG
        assert restored.cache_grain == CACHE_GRAIN_ROLE_TARGET_RUN
        assert restored.schema_version == CACHE_SCHEMA_VERSION

    def test_from_dict_ignores_unknown_keys(self) -> None:
        data = _intent().to_dict()
        data["junk_field"] = "ignore-me"
        restored = HistoricalIntentRecord.from_dict(data)
        assert not hasattr(restored, "junk_field")


def _chunk(**overrides) -> HistoricalOutputChunk:
    base = dict(
        chunk_id="c1",
        parent_intent_record_id="rec1",
        chunk_type="section",
        section_id="headline",
        chunk_text="text",
        chunk_digest="cd",
        chunk_vector_ref="cv",
        artifact_ref="ar",
        artifact_digest="ad",
        source_fact_ids=["fact_001"],
        proof_pool_refs=["pp_001"],
        support_status="SUPPORTED",
        x2_status="PASS",
        x1d_status="PASS",
        section_prompt_hash="sph",
        section_model_profile_hash="smph",
        generated_at_utc="2026-01-01T00:00:00Z",
    )
    base.update(overrides)
    return HistoricalOutputChunk(**base)


class TestHistoricalOutputChunk:
    def test_independent_cache_identity_is_false_and_not_init(self) -> None:
        chunk = _chunk()
        assert chunk.independent_cache_identity is False

    def test_to_dict_firewall_flags(self) -> None:
        d = _chunk().to_dict()
        assert d["independent_cache_identity"] is False
        assert d["parent_required_for_reuse"] is True

    def test_from_dict_drops_firewall_keys(self) -> None:
        d = _chunk().to_dict()
        # to_dict injects parent_required_for_reuse; from_dict must not choke.
        restored = HistoricalOutputChunk.from_dict(d)
        assert restored.independent_cache_identity is False
        assert restored.chunk_id == "c1"
        assert restored.section_id == "headline"

    def test_from_dict_defaults_optional_collections(self) -> None:
        minimal = {
            "chunk_id": "c2",
            "parent_intent_record_id": "rec1",
            "chunk_type": "section",
            "chunk_digest": "cd",
            "artifact_ref": "ar",
            "artifact_digest": "ad",
            "support_status": "SUPPORTED",
            "x2_status": "PASS",
            "x1d_status": "PASS",
            "section_prompt_hash": "sph",
            "section_model_profile_hash": "smph",
            "generated_at_utc": "2026-01-01T00:00:00Z",
        }
        restored = HistoricalOutputChunk.from_dict(minimal)
        assert restored.section_id == ""
        assert restored.source_fact_ids == []
        assert restored.proof_pool_refs == []
        assert restored.schema_version == CACHE_SCHEMA_VERSION
