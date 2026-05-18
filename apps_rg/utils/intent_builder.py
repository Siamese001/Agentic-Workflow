"""Build ROLE_TARGET_RUN cache intent payloads for apps_rg R1B warm-up."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class AppsRgCacheIntent:
    target_company: str
    target_role: str
    target_level: str
    policy_hash: str
    blueprint_hash: str
    tenant_id: str
    request_id: str
    source_resume_hash: str
    generation_mode: str
    jd_hash: str
    brief_hash: str

    def to_cache_key_dict(self) -> dict[str, Any]:
        return {
            "target_company": self.target_company,
            "target_role": self.target_role,
            "target_level": self.target_level,
            "generation_mode": self.generation_mode,
            "resume_hash": self.source_resume_hash,
            "jd_hash": self.jd_hash,
            "brief_hash": self.brief_hash,
            "tenant_id": self.tenant_id,
            "request_id": self.request_id,
        }


def build_intent_from_request(
    *,
    candidate_profile_path: str,
    target_company: str,
    target_role: str,
    target_level: str,
    policy_hash: str,
    blueprint_hash: str,
    tenant_id: str,
    request_id: str,
) -> AppsRgCacheIntent:
    del candidate_profile_path  # stub path for warm-up only
    return AppsRgCacheIntent(
        target_company=target_company,
        target_role=target_role,
        target_level=target_level,
        policy_hash=policy_hash,
        blueprint_hash=blueprint_hash,
        tenant_id=tenant_id,
        request_id=request_id,
        source_resume_hash="warm_stub_resume_hash",
        generation_mode="strategic_tailor",
        jd_hash="warm_stub_jd",
        brief_hash="warm_stub_brief",
    )


__all__ = ["AppsRgCacheIntent", "build_intent_from_request"]
