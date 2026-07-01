"""W2: Fact vector ingest module for apps_rg.

Handles ingestion of candidate_profile and project_evidence into fact_vectors.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from agentic_core.config.model_catalog import (
    BGE_M3_EMBEDDING_DIMENSION,
    BGE_M3_MODEL_ID,
)

BGE_M3_DIM = BGE_M3_EMBEDDING_DIMENSION


@dataclass(frozen=True)
class FactVectorChunk:
    """A single chunk of fact vector data for fact_vectors collection."""

    chunk_id: str
    content: str
    app: str = "apps_rg"
    source_class: str = "candidate_profile"
    ingestion_timestamp: str = ""
    source_document_id: str = ""
    source_version_hash: str = ""
    skills_mentioned: list[str] = field(default_factory=list)
    section_type: str = ""
    company: str = ""
    role: str = ""
    section_targets: str = ""
    citation_anchor: str = ""
    chunk_digest: str = ""
    authority_class: str = "PRIMARY"
    tier: str = "seed"
    embedding_model_id: str = BGE_M3_MODEL_ID
    embedding_dim: int = BGE_M3_DIM
    freshness_status: str = "FRESH"
    invalid_for_normative_use: str = "false"

    def __post_init__(self) -> None:
        if not self.ingestion_timestamp:
            object.__setattr__(
                self,
                "ingestion_timestamp",
                datetime.now(timezone.utc).isoformat(),
            )
        if not self.chunk_digest:
            object.__setattr__(self, "chunk_digest", _compute_hash(self.content)[:32])
        if not self.citation_anchor:
            object.__setattr__(
                self,
                "citation_anchor",
                f"{self.source_document_id}:{self.chunk_id[:48]}",
            )

    def to_chroma_document(self) -> dict[str, Any]:
        """JSONL row for ``tools.ingestion.chroma_ingest_pipeline`` (uses ``text``)."""
        return {
            "id": self.chunk_id,
            "text": self.content,
            "metadata": {
                "app": self.app,
                "source_class": self.source_class,
                "ingestion_timestamp": self.ingestion_timestamp,
                "source_document_id": self.source_document_id,
                "source_version_hash": self.source_version_hash,
                "skills_mentioned": json.dumps(self.skills_mentioned),
                "section_type": self.section_type,
                "company": self.company or "",
                "role": self.role or "",
                "section_targets": self.section_targets or "",
                "citation_anchor": self.citation_anchor or "",
                "chunk_digest": self.chunk_digest or "",
                "authority_class": self.authority_class or "PRIMARY",
                "tier": self.tier or "seed",
                "embedding_model_id": self.embedding_model_id,
                "embedding_dim": int(self.embedding_dim),
                "freshness_status": self.freshness_status,
                "invalid_for_normative_use": self.invalid_for_normative_use,
            },
        }


class FactVectorSchema:
    """Schema validator for fact_vectors collection."""

    SCHEMA_PATH = Path("apps_rg/config/domain_contract/fact_vectors_schema.yaml")

    def __init__(self):
        self._schema: dict[str, Any] = {}
        self._load_schema()

    def _load_schema(self) -> None:
        """Load schema from YAML file."""
        if self.SCHEMA_PATH.exists():
            try:
                import yaml
            except ModuleNotFoundError:
                self._schema = self._default_schema()
                return

            with open(self.SCHEMA_PATH, encoding="utf-8") as f:
                self._schema = yaml.safe_load(f)
        else:
            self._schema = self._default_schema()

    @staticmethod
    def _default_schema() -> dict[str, Any]:
        return {
            "collection_name": "fact_vectors",
            "allowed_source_classes": ["candidate_profile", "project_evidence"],
            "rejected_source_classes": [
                "rubrics",
                "governance_docs",
                "approved_examples",
                "receipts",
                "company_research",
                "process_docs",
            ],
        }

    @property
    def collection_name(self) -> str:
        return self._schema.get("collection_name", "fact_vectors")

    @property
    def allowed_source_classes(self) -> list[str]:
        return self._schema.get("allowed_source_classes", ["candidate_profile", "project_evidence"])

    @property
    def rejected_source_classes(self) -> list[str]:
        return self._schema.get("rejected_source_classes", [])

    def validate_chunk(self, chunk: FactVectorChunk) -> tuple[bool, list[str]]:
        """Validate a chunk against the schema."""
        errors: list[str] = []

        # Check app
        if not chunk.app:
            errors.append("Missing app metadata")
        elif chunk.app != "apps_rg":
            errors.append(f"Invalid app value: {chunk.app}, expected apps_rg")

        # Check source_class
        if chunk.source_class in self.rejected_source_classes:
            errors.append(
                f"Source class {chunk.source_class} is rejected — belongs in process_docs"
            )
        elif chunk.source_class not in self.allowed_source_classes:
            errors.append(f"Source class {chunk.source_class} not in allowed list")

        tier_schema = (self._schema.get("metadata_schema") or {}).get("tier") or {}
        tier = str(chunk.tier or "").strip()
        if tier_schema.get("required", False) and not tier:
            errors.append("Missing tier metadata")
        allowed_tiers = tier_schema.get("allowed_values") or ["seed", "learned"]
        if tier and tier not in allowed_tiers:
            errors.append(f"Invalid tier value: {tier}, expected one of {allowed_tiers}")

        return len(errors) == 0, errors


def _extract_skills(content: str) -> list[str]:
    """Extract skills mentioned in content."""
    # Common tech skills pattern
    skill_patterns = [
        r"\b(Python|JavaScript|TypeScript|Java|Go|Rust|C\+\+|C#|Ruby|PHP|Swift|Kotlin)\b",
        r"\b(AWS|GCP|Azure|Kubernetes|Docker|Terraform|CloudFormation)\b",
        r"\b(PostgreSQL|MySQL|MongoDB|Redis|Elasticsearch|Cassandra)\b",
        r"\b(TensorFlow|PyTorch|scikit-learn|Pandas|NumPy|Apache Spark)\b",
        r"\b(Machine Learning|AI|Deep Learning|NLP|Computer Vision)\b",
    ]

    skills = set()
    for pattern in skill_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        skills.update(matches)

    return sorted(skills)


def _detect_section_type(content: str) -> str:
    """Detect the section type of content."""
    content_lower = content.lower()

    section_patterns = {
        "experience": ["experience", "work history", "employment", "career"],
        "skills": ["skills", "technologies", "tech stack", "proficiencies"],
        "summary": ["summary", "overview", "profile", "objective"],
        "education": ["education", "degree", "university", "college"],
        "projects": ["projects", "open source", "github"],
        "certifications": ["certifications", "certified", "aws certified"],
    }

    for section_type, keywords in section_patterns.items():
        if any(kw in content_lower for kw in keywords):
            return section_type

    return "general"


def _compute_hash(content: str) -> str:
    """Compute SHA256 hash of content."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def ingest_candidate_profile(
    content: str,
    candidate_name: str,
    source_document_id: str,
    *,
    company: str = "",
    role: str = "",
) -> list[FactVectorChunk]:
    """Ingest candidate profile (resume) into chunks.

    Args:
        content: Raw resume text
        candidate_name: Name of candidate
        source_document_id: Document ID for this resume

    Returns:
        List of FactVectorChunk objects
    """
    chunks: list[FactVectorChunk] = []
    content_hash = _compute_hash(content)
    timestamp = datetime.now(timezone.utc).isoformat()

    # Split content into sections
    sections = re.split(r"\n\n+", content)

    for i, section in enumerate(sections):
        if len(section.strip()) < 50:  # Skip very short sections
            continue

        chunk_id = f"{source_document_id}_section_{i:03d}_{content_hash[:8]}"
        skills = _extract_skills(section)
        section_type = _detect_section_type(section)

        starget = section_type if section_type == "general" else f"{section_type},general"
        chunk = FactVectorChunk(
            chunk_id=chunk_id,
            content=section.strip(),
            app="apps_rg",
            source_class="candidate_profile",
            ingestion_timestamp=timestamp,
            source_document_id=source_document_id,
            source_version_hash=content_hash,
            skills_mentioned=skills,
            section_type=section_type,
            company=company,
            role=role,
            section_targets=starget,
        )
        chunks.append(chunk)

    return chunks


def ingest_project_evidence(
    content: str,
    project_name: str,
    candidate_name: str,
    source_document_id: str,
    employer_or_client: str = "",
    role_or_title: str = "",
) -> list[FactVectorChunk]:
    """Ingest project evidence into chunks.

    Args:
        content: Raw project description text
        project_name: Name of the project
        candidate_name: Name of candidate
        source_document_id: Document ID for this project
        employer_or_client: Optional employer/client name
        role_or_title: Optional role/title

    Returns:
        List of FactVectorChunk objects
    """
    chunks: list[FactVectorChunk] = []
    content_hash = _compute_hash(content)
    timestamp = datetime.now(timezone.utc).isoformat()

    # Split content into paragraphs
    paragraphs = re.split(r"\n\n+", content)

    for i, para in enumerate(paragraphs):
        if len(para.strip()) < 30:  # Skip very short paragraphs
            continue

        chunk_id = f"{source_document_id}_para_{i:03d}_{content_hash[:8]}"
        skills = _extract_skills(para)

        # Build content with metadata
        enriched_content = f"""Project: {project_name}
Candidate: {candidate_name}
Employer/Client: {employer_or_client}
Role: {role_or_title}

{para.strip()}"""

        chunk = FactVectorChunk(
            chunk_id=chunk_id,
            content=enriched_content,
            app="apps_rg",
            source_class="project_evidence",
            ingestion_timestamp=timestamp,
            source_document_id=source_document_id,
            source_version_hash=content_hash,
            skills_mentioned=skills,
            section_type="project",
            company=employer_or_client or "",
            role=role_or_title or "",
            section_targets="outcomes_lane,professional_experience,project",
        )
        chunks.append(chunk)

    return chunks


def export_chunks_jsonl(chunks: Iterable[FactVectorChunk], out_path: Path) -> int:
    """Write ``FactVectorChunk`` rows as JSONL for ``chroma_ingest_pipeline``."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with out_path.open("w", encoding="utf-8") as fh:
        for chunk in chunks:
            fh.write(json.dumps(chunk.to_chroma_document(), ensure_ascii=False) + "\n")
            n += 1
    return n


__all__ = [
    "BGE_M3_DIM",
    "BGE_M3_MODEL_ID",
    "FactVectorChunk",
    "FactVectorSchema",
    "export_chunks_jsonl",
    "ingest_candidate_profile",
    "ingest_project_evidence",
]
