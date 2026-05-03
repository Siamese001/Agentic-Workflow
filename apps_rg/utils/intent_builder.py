"""Build normalized ResumeGenerationIntent from CLI args + source resume."""

from __future__ import annotations

import hashlib
import json
import uuid
from pathlib import Path
from typing import Optional

from apps_rg.types.intent_payload import ResumeGenerationIntent


def build_intent_from_request(
    candidate_profile_path: Path,
    target_company: str,
    target_role: str,
    target_level: Optional[str] = None,
    target_function: Optional[str] = None,
    tone_profile: str = "formal",
    output_target: str = "markdown",
    tenant_id: str = "default",
    request_id: Optional[str] = None,
) -> ResumeGenerationIntent:
    """Normalize CLI request into canonical ResumeGenerationIntent.

    Key principle: Same intent → Same embedding vector → Cache hit.
    Variations in whitespace, order, or non-semantic fields don't change intent.
    """
    # Derive source resume hash
    source_hash = _hash_file(candidate_profile_path)

    # Extract tech stack from profile (simplified — real impl uses profile parser)
    tech_stack = _extract_tech_stack(candidate_profile_path)

    # Normalize level
    normalized_level = _normalize_level(target_level or "mid")
    normalized_function = _normalize_function(target_function or "engineering")

    return ResumeGenerationIntent(
        source_resume_hash=source_hash,
        candidate_identifier=_derive_candidate_id(candidate_profile_path),
        target_company=target_company.strip().lower(),
        target_role=target_role.strip().lower(),
        target_level=normalized_level,
        target_function=normalized_function,
        target_industry=_derive_industry(target_company),
        role_seniority=_level_to_seniority(normalized_level),
        role_tech_stack=tuple(sorted(set(tech_stack))),
        output_target=output_target,
        max_pages=_level_to_max_pages(normalized_level),
        tone_profile=tone_profile,
        request_id=request_id or _generate_request_id(),
        tenant_id=tenant_id,
    )


def _hash_file(path: Path) -> str:
    """SHA-256 hash of file content."""
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()[:32]


def _normalize_level(level: str) -> str:
    """Normalize level string to canonical form."""
    level_map = {
        "jr": "junior",
        "junior": "junior",
        "jnr": "junior",
        "mid": "mid",
        "med": "mid",
        "intermediate": "mid",
        "sr": "senior",
        "senior": "senior",
        "snr": "senior",
        "staff": "staff",
        "principal": "principal",
        "lead": "staff",
    }
    return level_map.get(level.lower().strip(), "mid")


def _normalize_function(function: str) -> str:
    """Normalize function string to canonical form."""
    function_map = {
        "eng": "engineering",
        "engineering": "engineering",
        "product": "product",
        "pm": "product",
        "design": "design",
        "ux": "design",
        "research": "research",
        "data": "data",
        "sales": "sales",
        "marketing": "marketing",
    }
    return function_map.get(function.lower().strip(), "engineering")


def _level_to_seniority(level: str) -> str:
    """Map level to seniority class."""
    mapping = {
        "junior": "entry",
        "mid": "mid",
        "senior": "senior",
        "staff": "executive",
        "principal": "executive",
    }
    return mapping.get(level, "mid")


def _level_to_max_pages(level: str) -> int:
    """Max pages based on seniority."""
    return 1 if level == "junior" else 2


def _derive_candidate_id(path: Path) -> str:
    """Derive anonymous candidate id from path."""
    return hashlib.sha256(str(path).encode()).hexdigest()[:16]


def _derive_industry(company: str) -> str:
    """Derive industry from company name (simplified lookup)."""
    # Real implementation would use company database
    tech_keywords = ["tech", "ai", "software", "digital", "data", "cloud", "network"]
    company_lower = company.lower()
    if any(kw in company_lower for kw in tech_keywords):
        return "technology"
    return "general"


def _extract_tech_stack(path: Path) -> list[str]:
    """Extract tech stack from candidate profile."""
    try:
        content = path.read_text(encoding="utf-8")
        # Try to parse as YAML/JSON and extract skills
        try:
            import yaml

            data = yaml.safe_load(content)
        except ImportError:
            data = json.loads(content)

        if isinstance(data, dict):
            skills = data.get("skills", [])
            if isinstance(skills, list):
                return [str(s).lower() for s in skills]
            elif isinstance(skills, str):
                return [s.strip().lower() for s in skills.split(",")]
    except Exception:
        pass
    return ["python"]  # Default fallback


def _generate_request_id() -> str:
    """Generate unique request id."""
    return str(uuid.uuid4())[:16]


def derive_intent_hash(intent: ResumeGenerationIntent) -> str:
    """Derive stable hash from intent for lineage tracking."""
    data = json.dumps(intent.to_cache_key_dict(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(data.encode()).hexdigest()[:32]


__all__ = ["build_intent_from_request", "derive_intent_hash"]
