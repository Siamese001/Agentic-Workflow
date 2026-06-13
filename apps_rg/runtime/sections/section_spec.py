"""Section runtime specs for apps_rg section lanes.

The section retrieval profile is the YAML SSOT for per-lane graph routing
configuration. These dataclasses expose the authority defaults used by section
debugging and whole-run orchestration without making graph topology a claim
proof source by default.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml

CANONICAL_SECTION_IDS: tuple[str, ...] = (
    "headline",
    "executive_summary",
    "competencies",
    "unify_bullets",
    "unify_narrative",
    "ibm_bullets",
    "ibm_narrative",
)

SECTION_RETRIEVAL_PROFILE_RELPATH = Path(
    "apps_rg/config/domain_contract/section_retrieval_profile.yaml"
)


@dataclass(frozen=True, slots=True)
class SourceAuthoritySpec:
    """Proof source authority configuration.

    Candidate fact references are lineage/substrate only. GraphDB-backed proof
    remains the claim authority; graph topology supports routing unless a
    section opts into fact-bound graph proof explicitly.
    """

    candidate_facts_as_proof: bool = False
    candidate_fact_lineage_allowed: bool = True
    graph_as_claim_proof: bool = False
    graph_as_routing_support: bool = True
    graph_claim_proof_allowed_only_when_fact_bound: bool = True
    jd_as_proof_allowed: bool = False
    briefing_as_proof_allowed: bool = False
    companion_context_authority: bool = False

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any] | None) -> "SourceAuthoritySpec":
        data = dict(raw or {})
        return cls(
            candidate_facts_as_proof=False,
            candidate_fact_lineage_allowed=bool(
                data.get("candidate_fact_lineage_allowed", True)
            ),
            graph_as_claim_proof=bool(data.get("graph_as_claim_proof", False)),
            graph_as_routing_support=bool(data.get("graph_as_routing_support", True)),
            graph_claim_proof_allowed_only_when_fact_bound=bool(
                data.get("graph_claim_proof_allowed_only_when_fact_bound", True)
            ),
            jd_as_proof_allowed=bool(data.get("jd_as_proof_allowed", False)),
            briefing_as_proof_allowed=bool(data.get("briefing_as_proof_allowed", False)),
            companion_context_authority=bool(data.get("companion_context_authority", False)),
        )

    def candidate_facts_may_prove_claim(self, *, fact_bound: bool = True) -> bool:
        _ = fact_bound
        return False

    def graph_may_prove_claim(self, *, fact_bound: bool = True) -> bool:
        if not self.graph_as_claim_proof:
            return False
        if self.graph_claim_proof_allowed_only_when_fact_bound and not fact_bound:
            return False
        return True

    def effective_claim_proof(self, fact_bound: bool = True) -> bool:
        """True when GraphDB-backed, fact-bound proof can prove a claim."""
        return self.graph_may_prove_claim(fact_bound=fact_bound)


@dataclass(frozen=True, slots=True)
class SectionSpec:
    """Runtime spec for one independently runnable section lane."""

    section_id: str
    retrieval_profile_id: str
    graph_expansion_allowed: bool
    graph_expansion_mode: str
    source_authority: SourceAuthoritySpec

    @classmethod
    def from_mapping(
        cls,
        raw: Mapping[str, Any],
        *,
        source_authority_defaults: Mapping[str, Any] | None = None,
    ) -> "SectionSpec":
        merged_authority = dict(source_authority_defaults or {})
        section_authority = raw.get("source_authority")
        if isinstance(section_authority, Mapping):
            merged_authority.update(section_authority)
        return cls(
            section_id=str(raw.get("section_id") or ""),
            retrieval_profile_id=str(raw.get("retrieval_profile_id") or ""),
            graph_expansion_allowed=bool(raw.get("graph_expansion_allowed", False)),
            graph_expansion_mode=str(raw.get("graph_expansion_mode") or ""),
            source_authority=SourceAuthoritySpec.from_mapping(merged_authority),
        )

    def graph_supports_routing(self) -> bool:
        return bool(
            self.graph_expansion_allowed
            and self.source_authority.graph_as_routing_support
        )


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return here.parents[4]


def load_section_specs(profile_path: Path | None = None) -> dict[str, SectionSpec]:
    path = profile_path or (_repo_root() / SECTION_RETRIEVAL_PROFILE_RELPATH)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"section retrieval profile must be a mapping: {path}")
    defaults = data.get("source_authority_defaults")
    defaults_map = defaults if isinstance(defaults, Mapping) else {}
    specs: dict[str, SectionSpec] = {}
    for row in data.get("sections") or []:
        if not isinstance(row, Mapping):
            continue
        spec = SectionSpec.from_mapping(row, source_authority_defaults=defaults_map)
        if spec.section_id:
            specs[spec.section_id] = spec
    return specs


def get_section_spec(section_id: str, profile_path: Path | None = None) -> SectionSpec:
    specs = load_section_specs(profile_path)
    try:
        return specs[section_id]
    except KeyError as exc:
        raise KeyError(f"unknown apps_rg section_id: {section_id}") from exc


__all__ = [
    "CANONICAL_SECTION_IDS",
    "SECTION_RETRIEVAL_PROFILE_RELPATH",
    "SectionSpec",
    "SourceAuthoritySpec",
    "get_section_spec",
    "load_section_specs",
]
