"""Canonical section evidence set SSOT (apps_rg product path)."""

from apps_rg.runtime.evidence.canonical_section_evidence_set import (
    CanonicalSectionEvidenceSet,
    apply_canonical_section_evidence_materialization,
    build_canonical_section_evidence_set,
    canonical_evidence_set_digest,
    classify_lane_proof_bundle_completeness,
    detect_id_namespace_split_without_alias,
    materialize_fec_allowed_from_c04,
)

__all__ = [
    "CanonicalSectionEvidenceSet",
    "apply_canonical_section_evidence_materialization",
    "build_canonical_section_evidence_set",
    "canonical_evidence_set_digest",
    "classify_lane_proof_bundle_completeness",
    "detect_id_namespace_split_without_alias",
    "materialize_fec_allowed_from_c04",
]
