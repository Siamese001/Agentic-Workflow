"""C0 proof-authority profile for apps_rg generated sections.

The authority decision is separate from generated-lane membership. A section only
hard-requires C0 fact-vector hydration when it consumes ``fact_vectors`` directly
for proof/ranking. Narrative lanes inherit finalized bullet proof instead.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from apps_rg.runtime.section_execution_plan import (
    BULLET_LANES,
    NARRATIVE_UPSTREAM_BULLET_LANE,
)

AUTHORITY_DIRECT_VECTOR_PROOF: Final[str] = "direct_vector_proof"
AUTHORITY_INHERITED_BULLET_PROOF: Final[str] = "inherited_bullet_proof"
AUTHORITY_AGGREGATE_SECTION_PROOF: Final[str] = "aggregate_section_proof"
AUTHORITY_POSITIONING_ONLY: Final[str] = "positioning_only"


@dataclass(frozen=True)
class C0SectionAuthorityProfile:
    section_id: str
    authority_mode: str
    direct_vector_proof: bool
    inherited_bullet_proof: bool = False
    aggregate_section_proof: bool = False
    positioning_only: bool = False
    upstream_sections: tuple[str, ...] = ()
    product_hybrid_allowed: bool = False


_DIRECT_VECTOR_SECTIONS: Final[tuple[str, ...]] = ("competencies", *BULLET_LANES)

_SECTION_AUTHORITY: Final[dict[str, C0SectionAuthorityProfile]] = {
    section_id: C0SectionAuthorityProfile(
        section_id=section_id,
        authority_mode=AUTHORITY_DIRECT_VECTOR_PROOF,
        direct_vector_proof=True,
        product_hybrid_allowed=True,
    )
    for section_id in _DIRECT_VECTOR_SECTIONS
}

_SECTION_AUTHORITY.update(
    {
        section_id: C0SectionAuthorityProfile(
            section_id=section_id,
            authority_mode=AUTHORITY_INHERITED_BULLET_PROOF,
            direct_vector_proof=False,
            inherited_bullet_proof=True,
            upstream_sections=(upstream,),
            product_hybrid_allowed=False,
        )
        for section_id, upstream in NARRATIVE_UPSTREAM_BULLET_LANE.items()
    }
)

_SECTION_AUTHORITY.update(
    {
        "executive_summary": C0SectionAuthorityProfile(
            section_id="executive_summary",
            authority_mode=AUTHORITY_AGGREGATE_SECTION_PROOF,
            direct_vector_proof=True,
            aggregate_section_proof=True,
            upstream_sections=(
                "competencies",
                "unify_bullets",
                "ibm_bullets",
                "insurtech_bullets",
                "ey_bullets",
                "unify_narrative",
                "ibm_narrative",
                "insurtech_narrative",
                "ey_narrative",
            ),
            product_hybrid_allowed=True,
        ),
        "headline": C0SectionAuthorityProfile(
            section_id="headline",
            authority_mode=AUTHORITY_POSITIONING_ONLY,
            direct_vector_proof=True,
            aggregate_section_proof=True,
            positioning_only=True,
            upstream_sections=(
                "executive_summary",
                "competencies",
                "unify_bullets",
                "ibm_bullets",
                "insurtech_bullets",
                "ey_bullets",
            ),
            product_hybrid_allowed=True,
        ),
    }
)


def c0_section_authority_profile(section_id: str) -> C0SectionAuthorityProfile:
    sid = str(section_id or "").strip().lower().replace("-", "_")
    return _SECTION_AUTHORITY.get(
        sid,
        C0SectionAuthorityProfile(
            section_id=sid,
            authority_mode=AUTHORITY_DIRECT_VECTOR_PROOF,
            direct_vector_proof=True,
            product_hybrid_allowed=True,
        ),
    )


def direct_vector_section_ids() -> tuple[str, ...]:
    return tuple(
        section_id
        for section_id, profile in _SECTION_AUTHORITY.items()
        if profile.direct_vector_proof
    )


def c0_authority_manifest() -> dict[str, dict[str, object]]:
    return {
        section_id: {
            "authority_mode": profile.authority_mode,
            "direct_vector_proof": profile.direct_vector_proof,
            "inherited_bullet_proof": profile.inherited_bullet_proof,
            "aggregate_section_proof": profile.aggregate_section_proof,
            "positioning_only": profile.positioning_only,
            "upstream_sections": list(profile.upstream_sections),
            "product_hybrid_allowed": profile.product_hybrid_allowed,
        }
        for section_id, profile in sorted(_SECTION_AUTHORITY.items())
    }


__all__ = [
    "AUTHORITY_AGGREGATE_SECTION_PROOF",
    "AUTHORITY_DIRECT_VECTOR_PROOF",
    "AUTHORITY_INHERITED_BULLET_PROOF",
    "AUTHORITY_POSITIONING_ONLY",
    "C0SectionAuthorityProfile",
    "c0_authority_manifest",
    "c0_section_authority_profile",
    "direct_vector_section_ids",
]
