"""C0 evidence room constants and boundary law."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
PRIOR_RESUME_MANIFEST_REL = "artifacts/apps_rg/c0/prior_resume_variant_fact_extraction_manifest.json"
PRIOR_RESUME_STAGING_REL = "artifacts/apps_rg/c0/_prior_resume_extract_staging"

CONFIDENCE_HIGH = "HIGH"
CONFIDENCE_MEDIUM = "MEDIUM"
CONFIDENCE_LOW = "LOW"
CONFIDENCE_PENDING = "PENDING_TRACE"

PROOF_ELIGIBLE = "proof_eligible"
CLAIM_ELIGIBLE = "claim_eligible"
TARGETING_ONLY = "targeting_only"
NOT_PROOF = "not_proof"

STRATUM_MUST_USE = "MUST_USE"
STRATUM_SUPPORTING = "SUPPORTING"
STRATUM_BACKGROUND = "BACKGROUND"
STRATUM_CONTRADICTS = "CONTRADICTS"
STRATUM_EXCLUDED = "EXCLUDED"

REL_DIRECT_SUPPORT = "direct_support"
REL_ADJACENCY_ONLY = "adjacency_only"
REL_CONTRADICTION = "contradiction"
REL_SUPERSEDED = "superseded"
REL_SECTION_FIT = "section_fit"

GRAPH_STRENGTH_DIRECT = "DIRECT"
GRAPH_STRENGTH_ADJACENT_ONLY = "ADJACENT_ONLY"
GRAPH_STRENGTH_CONTRADICTED = "CONTRADICTED"
GRAPH_STRENGTH_NONE = "NONE"

SOURCE_JD = "jd_payload"
SOURCE_BRIEF = "briefing"
SOURCE_PRIOR_VARIANT = "prior_resume_variant"
SOURCE_SRFS = "selected_role_fact_set"
SOURCE_LEDGER = "candidate_fact_ledger"
SOURCE_PROOF_POOL = "proof_pool"

FORBIDDEN_PROOF_SOURCE_TYPES = frozenset(
    {
        SOURCE_JD,
        "app_payload_inline",
        "jd_payload_inline",
        "briefing",
        "generic_best_practice",
        "company_research",
        "rubrics",
        "governance_docs",
    }
)

C0_SECTIONS_ENABLED = frozenset({"competencies", "executive_summary"})

__all__ = [
    "C0_SECTIONS_ENABLED",
    "FORBIDDEN_PROOF_SOURCE_TYPES",
    "PRIOR_RESUME_MANIFEST_REL",
    "PRIOR_RESUME_STAGING_REL",
    "REPO_ROOT",
]
