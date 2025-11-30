# RG Memory for L4 memory state
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
from enum import Enum
import json

class BulletProvenance(Enum):
    """Bullet point origin tracking"""
    VERBATIM = "verbatim"
    MASTER_RESUME = "master_resume"
    GENERATED = "generated"
    ENRICHED = "enriched"
    HYBRID = "hybrid"

@dataclass
class BulletIndex:
    """Enhanced bullet index with provenance tracking"""
    bullet_id: str
    company: str
    role: str
    bullet_text: str
    keywords: List[str] = field(default_factory=list)
    provenance: BulletProvenance = BulletProvenance.MASTER_RESUME
    relevance_score: float = 0.0
    indexed_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class MemoryResult:
    """Memory operation result with enhanced metadata"""
    success: bool = True
    data: Dict[str, Any] = None
    metadata: Dict[str, Any] = None
    provenance_tracking: Dict[str, BulletProvenance] = field(default_factory=dict)

    def __post_init__(self):
        if self.data is None:
            self.data = {}
        if self.metadata is None:
            self.metadata = {}

class RGMemory:
    """Resume memory for L4 memory state"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.resume_data = {}
        self.bullet_pool = {}
        self.competencies = {}
        self._load_master_resume()

    def _load_master_resume(self) -> None:
        """Load master resume data from production inputs

        NOTE: Path assumes project structure with 'Agentic_Workflow-10_11' directory.
        For different deployments, adjust the path resolution accordingly.
        """

        # Use absolute path resolution - include the missing Agentic_Workflow-10_11 directory
        current_dir = Path(__file__).parent
        resume_path = (
            current_dir.parent.parent.parent.parent.parent /
            "Agentic_Workflow-10_11" / "apps" / "resume_engine" /
            "production_inputs" / "master_resume.json"
        )

        try:
            with open(resume_path, 'r') as f:
                self.resume_data = json.load(f)
                self._index_bullets()
                self._index_competencies()
        except FileNotFoundError:
            # Fallback to mock data if file not found
            self.resume_data = {"mock": True}

    def _index_bullets(self) -> None:
        """Index bullet points by company and role"""
        self.bullet_pool = {}
        for exp in self.resume_data.get("professional_experience", []):
            company = exp.get("company", "")
            title = exp.get("title", "")
            bullets = exp.get("bullet_pool", exp.get("highlights", []))

            key = f"{company}_{title}"
            self.bullet_pool[key] = {
                "company": company,
                "title": title,
                "bullets": bullets,
                "dates": exp.get("dates", {}),
                "location": exp.get("location", "")
            }

    def _index_competencies(self) -> None:
        """Index strategic and technical competencies"""
        self.competencies = {
            "strategic_technical": self.resume_data.get("strategic_and_technical_competencies", []),
            "certifications": self.resume_data.get("certifications_and_credentials", []),
            "education": self.resume_data.get("education", [])
        }

    def process(self, query: Dict[str, Any]) -> MemoryResult:
        """Process memory query for resume data"""
        query_type = query.get("type", "retrieve")

        if query_type == "retrieve_bullets":
            return self._retrieve_bullets(query)
        elif query_type == "get_competencies":
            return self._get_competencies(query)
        elif query_type == "search_experience":
            return self._search_experience(query)
        else:
            return MemoryResult(
                success=False,
                data={},
                metadata={"error": f"Unknown query type: {query_type}"}
            )

    def _retrieve_bullets(self, query: Dict[str, Any]) -> MemoryResult:
        """Retrieve bullets based on criteria"""
        target_role = query.get("target_role", "")
        company_filter = query.get("company", "")

        relevant_bullets = []
        for key, data in self.bullet_pool.items():
            if company_filter and company_filter.lower() not in data["company"].lower():
                continue

            # Filter bullets based on target role keywords
            filtered_bullets = self._filter_bullets_by_role(data["bullets"], target_role)
            relevant_bullets.extend(filtered_bullets)

        return MemoryResult(
            success=True,
            data={"bullets": relevant_bullets, "count": len(relevant_bullets)},
            metadata={"query_role": target_role, "company_filter": company_filter}
        )

    def _filter_bullets_by_role(self, bullets: List[str], target_role: str) -> List[str]:
        """Filter bullets based on target role keywords"""
        role_keywords = {
            "ai_engineer": ["ai", "machine learning", "llm", "models", "algorithms"],
            "technical_lead": ["led", "architected", "built", "designed", "managed"],
            "executive": ["strategic", "leadership", "partnership", "transformation", "revenue"],
            "data_scientist": ["data", "analytics", "models", "statistical", "analysis"]
        }

        keywords = role_keywords.get(target_role.lower(), [])
        if not keywords:
            return bullets[:5]  # Return first 5 if no specific role

        filtered = []
        for bullet in bullets:
            bullet_lower = bullet.lower()
            if any(keyword in bullet_lower for keyword in keywords):
                filtered.append(bullet)

        return filtered[:8]  # Limit to 8 most relevant bullets

    def _get_competencies(self, query: Dict[str, Any]) -> MemoryResult:
        """Get competencies based on type"""
        comp_type = query.get("competency_type", "strategic_technical")

        return MemoryResult(
            success=True,
            data={"competencies": self.competencies.get(comp_type, [])},
            metadata={"competency_type": comp_type}
        )

    def _search_experience(self, query: Dict[str, Any]) -> MemoryResult:
        """Search experience by company or title"""
        search_term = query.get("search_term", "").lower()

        results = []
        for exp in self.resume_data.get("professional_experience", []):
            if (search_term in exp.get("company", "").lower() or
                search_term in exp.get("title", "").lower()):
                results.append(exp)

        return MemoryResult(
            success=True,
            data={"experience": results, "count": len(results)},
            metadata={"search_term": search_term}
        )
