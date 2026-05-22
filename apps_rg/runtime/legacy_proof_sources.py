"""Non-product proof source labels — offline audit, containment fixtures, and tests only.

Must not appear as authority on ``python -m apps_rg --section <lane>`` receipts.
"""
from __future__ import annotations

PROOF_SOURCE_SRFS = "srfs"
PROOF_SOURCE_BROAD_SKILLS_LEDGER = "broad_skills_ledger"
PROOF_SOURCE_BASE_RESUME_FALLBACK = "base_resume_fallback"

FORBIDDEN_PRODUCT_PROOF_SOURCES: frozenset[str] = frozenset(
    {
        PROOF_SOURCE_SRFS,
        PROOF_SOURCE_BROAD_SKILLS_LEDGER,
        PROOF_SOURCE_BASE_RESUME_FALLBACK,
    }
)

FORBIDDEN_PROOF_POOL_TYPE_LABELS: frozenset[str] = frozenset(
    {
        "selected_role_fact_set",
        "base_resume_fallback",
        "broad_skills_ledger",
        "prompt_pool",
        "proof_pool",
        "legacy_pool",
        "fallback_pool",
        "base_resume",
        "unknown",
    }
)

__all__ = [
    "FORBIDDEN_PRODUCT_PROOF_SOURCES",
    "FORBIDDEN_PROOF_POOL_TYPE_LABELS",
    "PROOF_SOURCE_BASE_RESUME_FALLBACK",
    "PROOF_SOURCE_BROAD_SKILLS_LEDGER",
    "PROOF_SOURCE_SRFS",
]
