"""apps_rg intent payload for R1B semantic cache.

The intent payload captures what the user wants (target role, company,
constraints) — NOT the resume output. Historical cache stores
historical_input_intent_vector → prior_output_chunks.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ResumeGenerationIntent:
    """Normalized intent for apps_rg resume generation."""

    # Source resume metadata
    source_resume_hash: str  # SHA-256 of source resume content
    candidate_identifier: str  # Anonymous candidate id

    # Target job metadata
    target_company: str
    target_role: str
    target_level: str  # junior, mid, senior, staff, principal
    target_function: str  # engineering, product, design, etc.
    target_industry: str

    # Role context
    role_seniority: str  # entry, mid, senior, executive
    role_tech_stack: tuple[str, ...]  # Normalized tech keywords

    # Output constraints
    output_target: str  # markdown, docx, pdf
    max_pages: int
    tone_profile: str  # formal, conversational, executive

    # Blueprint / policy provenance
    policy_hash: str  # SHA-256 of active policy config
    blueprint_hash: str  # SHA-256 of resume blueprint/template
    jd_hash: str  # SHA-256 of job description content
    briefing_hash: str  # SHA-256 of research briefing content

    # Request provenance
    request_id: str
    tenant_id: str

    def to_embedding_text(self) -> str:
        """Flatten to text for embedding model."""
        return (
            f"Resume for {self.target_role} at {self.target_company} "
            f"({self.target_level}, {self.target_function}) "
            f"from candidate {self.candidate_identifier} "
            f"with tone {self.tone_profile}"
        )

    def to_cache_key_dict(self) -> dict:
        """Serializable dict for cache key derivation (14 fields)."""
        return {
            "source_resume_hash": self.source_resume_hash,
            "target_company": self.target_company,
            "target_role": self.target_role,
            "target_level": self.target_level,
            "target_function": self.target_function,
            "target_industry": self.target_industry,
            "role_seniority": self.role_seniority,
            "role_tech_stack": sorted(self.role_tech_stack),
            "output_target": self.output_target,
            "max_pages": self.max_pages,
            "tone_profile": self.tone_profile,
            "policy_hash": self.policy_hash,
            "blueprint_hash": self.blueprint_hash,
            "tenant_id": self.tenant_id,
        }


__all__ = ["ResumeGenerationIntent"]
