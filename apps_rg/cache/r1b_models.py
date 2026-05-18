"""R1B ROLE_TARGET_RUN grain — HistoricalIntentRecord + HistoricalOutputChunk."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from apps_rg.cache.r1b_constants import (
    APP_ID_APPS_RG,
    CACHE_GRAIN_ROLE_TARGET_RUN,
    CACHE_SCHEMA_VERSION,
)


@dataclass
class HistoricalIntentRecord:
    record_id: str
    app_id: str
    cache_grain: str
    request_intent_text: str
    normalized_intent_digest: str
    request_intent_vector_ref: str
    source_run_id: str
    target_company: str
    target_role: str
    job_family: str
    jd_digest: str
    briefing_digest: str
    srfs_digest: str
    proof_pool_digest: str
    skills_ledger_digest: str
    base_resume_digest: str
    final_resume_digest: str
    prompt_profile_hash: str
    model_profile_hash: str
    gate_profile_hash: str
    x3_disposition: str
    proof_eligible: bool
    cache_admissible: bool
    generated_at_utc: str
    non_admissible_reason: str = ""
    schema_version: str = CACHE_SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HistoricalIntentRecord:
        known = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        kwargs = {k: v for k, v in data.items() if k in known}
        kwargs.setdefault("app_id", APP_ID_APPS_RG)
        kwargs.setdefault("cache_grain", CACHE_GRAIN_ROLE_TARGET_RUN)
        kwargs.setdefault("schema_version", CACHE_SCHEMA_VERSION)
        return cls(**kwargs)


@dataclass
class HistoricalOutputChunk:
    chunk_id: str
    parent_intent_record_id: str
    chunk_type: str
    section_id: str
    chunk_text: str
    chunk_digest: str
    chunk_vector_ref: str
    artifact_ref: str
    artifact_digest: str
    source_fact_ids: list[str]
    proof_pool_refs: list[str]
    support_status: str
    x2_status: str
    x1d_status: str
    section_prompt_hash: str
    section_model_profile_hash: str
    generated_at_utc: str
    schema_version: str = CACHE_SCHEMA_VERSION
    # Child chunks only — never indexed as independent R1B lookup keys.
    independent_cache_identity: bool = field(default=False, init=False)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d.pop("independent_cache_identity", None)
        d["independent_cache_identity"] = False
        d["parent_required_for_reuse"] = True
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HistoricalOutputChunk:
        known = {
            f.name
            for f in cls.__dataclass_fields__.values()  # type: ignore[attr-defined]
            if f.name != "independent_cache_identity"
        }
        extra_keys = ("independent_cache_identity", "parent_required_for_reuse")
        kwargs = {k: v for k, v in data.items() if k in known and k not in extra_keys}
        kwargs.setdefault("section_id", "")
        kwargs.setdefault("chunk_text", "")
        kwargs.setdefault("chunk_vector_ref", "")
        kwargs.setdefault("source_fact_ids", [])
        kwargs.setdefault("proof_pool_refs", [])
        kwargs.setdefault("schema_version", CACHE_SCHEMA_VERSION)
        return cls(**kwargs)


__all__ = ["HistoricalIntentRecord", "HistoricalOutputChunk"]
