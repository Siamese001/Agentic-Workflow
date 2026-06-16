"""R1B semantic cache constants — apps_rg only (not C0 fact_vectors)."""

from __future__ import annotations

APP_ID_APPS_RG = "apps_rg"
CACHE_GRAIN_ROLE_TARGET_RUN = "ROLE_TARGET_RUN"
CACHE_SCHEMA_VERSION = "2026-05-18-r1b-w8-v1"
DEFAULT_SIMILARITY_THRESHOLD = 0.88
DEFAULT_CACHE_TTL_SECONDS = 86_400

# R1B output/proof chunk types (child records only; never standalone cache keys).
CHUNK_TYPE_FINAL_RESUME = "final_resume"
CHUNK_TYPE_HEADLINE = "headline_output"
CHUNK_TYPE_EXEC_SUMMARY = "executive_summary_output"
CHUNK_TYPE_COMPETENCIES = "competencies_output"
CHUNK_TYPE_UNIFY_NARRATIVE = "unify_narrative_output"
CHUNK_TYPE_UNIFY_BULLETS = "unify_bullets_output"
CHUNK_TYPE_IBM_NARRATIVE = "ibm_narrative_output"
CHUNK_TYPE_IBM_BULLETS = "ibm_bullets_output"
CHUNK_TYPE_INSURTECH_BULLETS = "insurtech_bullets_output"
CHUNK_TYPE_INSURTECH_NARRATIVE = "insurtech_narrative_output"
CHUNK_TYPE_EY_BULLETS = "ey_bullets_output"
CHUNK_TYPE_EY_NARRATIVE = "ey_narrative_output"
CHUNK_TYPE_AGGREGATION = "aggregation_summary"
CHUNK_TYPE_CLAIM_LEDGER = "claim_ledger_entry"
CHUNK_TYPE_SECTION_PROOF = "section_proof_summary"

SECTION_CHUNK_TYPES: frozenset[str] = frozenset(
    {
        CHUNK_TYPE_HEADLINE,
        CHUNK_TYPE_EXEC_SUMMARY,
        CHUNK_TYPE_COMPETENCIES,
        CHUNK_TYPE_UNIFY_NARRATIVE,
        CHUNK_TYPE_UNIFY_BULLETS,
        CHUNK_TYPE_IBM_NARRATIVE,
        CHUNK_TYPE_IBM_BULLETS,
        CHUNK_TYPE_INSURTECH_BULLETS,
        CHUNK_TYPE_INSURTECH_NARRATIVE,
        CHUNK_TYPE_EY_BULLETS,
        CHUNK_TYPE_EY_NARRATIVE,
    }
)

ALL_CHUNK_TYPES: frozenset[str] = frozenset(
    {
        CHUNK_TYPE_FINAL_RESUME,
        *SECTION_CHUNK_TYPES,
        CHUNK_TYPE_AGGREGATION,
        CHUNK_TYPE_CLAIM_LEDGER,
        CHUNK_TYPE_SECTION_PROOF,
    }
)

# X3 codes that allow finishing a run whose output may be cached for reuse.
X3_FINISH_ALLOWED: frozenset[str] = frozenset(
    {
        "X3_ALLOW",
        "X3C",
        "X3D",
        "EXIT_OK",
        "EXIT_PARTIAL",
    }
)

# Generation paths that must never be marked cache_admissible.
NON_ADMISSIBLE_RUNTIME_STATUSES: frozenset[str] = frozenset(
    {
        "OFFLINE_CONTRACT_STUB",
        "MOCKED",
        "MOCK_ONLY",
        "BLOCKED",
        "BLOCKED_LIVE_PROVIDER",
        "UNKNOWN",
        "PLUMBING_ONLY",
    }
)

# Explicit separation from C0 dense lane (Chroma collection name).
C0_FACT_VECTORS_COLLECTION = "fact_vectors"
R1B_STORAGE_SUBSYSTEM = "apps_rg_r1b_semantic_cache"
R1B_NOT_C0_FACT_VECTORS = (
    "R1B semantic cache stores HistoricalIntentRecord + HistoricalOutputChunk "
    f"under {R1B_STORAGE_SUBSYSTEM}. C0 dense retrieval uses Chroma collection "
    f"'{C0_FACT_VECTORS_COLLECTION}' only on cache miss — never as R1B identity."
)

DURABLE_WRITE_VIA_UWG = "UWG_GATE_REQUIRED"
R1B_UWG_TARGET_SURFACE = "l4.apps_rg.r1b_semantic_cache"
R1B_SCHEMA_REF = "schema:apps_rg.r1b_semantic_cache@2026-05-18-w10-v1"
FILE_BACKED_SSOT_NOTE = (
    "File-backed paths under artifacts/apps_rg/r1b_semantic_cache/ are fixture/proof "
    "mirrors only (storage_tier=fixture_proof_mirror). Durable production truth for R1B "
    "is admitted only via Exit-sourced CommitRequest through DurableWriteGateway to "
    f"{R1B_UWG_TARGET_SURFACE}."
)
STORAGE_TIER_FIXTURE_MIRROR = "fixture_proof_mirror"
STORAGE_TIER_UWG_ADMITTED = "uwg_admitted_durable_projection"

__all__ = [
    "DEFAULT_CACHE_TTL_SECONDS",
    "DEFAULT_SIMILARITY_THRESHOLD",
    "ALL_CHUNK_TYPES",
    "APP_ID_APPS_RG",
    "CACHE_GRAIN_ROLE_TARGET_RUN",
    "CACHE_SCHEMA_VERSION",
    "C0_FACT_VECTORS_COLLECTION",
    "CHUNK_TYPE_AGGREGATION",
    "CHUNK_TYPE_CLAIM_LEDGER",
    "CHUNK_TYPE_COMPETENCIES",
    "CHUNK_TYPE_EXEC_SUMMARY",
    "CHUNK_TYPE_FINAL_RESUME",
    "CHUNK_TYPE_HEADLINE",
    "CHUNK_TYPE_IBM_BULLETS",
    "CHUNK_TYPE_IBM_NARRATIVE",
    "CHUNK_TYPE_INSURTECH_BULLETS",
    "CHUNK_TYPE_INSURTECH_NARRATIVE",
    "CHUNK_TYPE_EY_BULLETS",
    "CHUNK_TYPE_EY_NARRATIVE",
    "CHUNK_TYPE_SECTION_PROOF",
    "CHUNK_TYPE_UNIFY_BULLETS",
    "CHUNK_TYPE_UNIFY_NARRATIVE",
    "DURABLE_WRITE_VIA_UWG",
    "FILE_BACKED_SSOT_NOTE",
    "R1B_SCHEMA_REF",
    "R1B_UWG_TARGET_SURFACE",
    "STORAGE_TIER_FIXTURE_MIRROR",
    "STORAGE_TIER_UWG_ADMITTED",
    "NON_ADMISSIBLE_RUNTIME_STATUSES",
    "R1B_NOT_C0_FACT_VECTORS",
    "R1B_STORAGE_SUBSYSTEM",
    "SECTION_CHUNK_TYPES",
    "X3_FINISH_ALLOWED",
]
