"""
resume_app/adapters – app_resume_memory_adapter.py

Apps layer adapter that wraps agentic_core L4 memory state logic.
Provides clean interface for resume data storage, retrieval, and provenance tracking.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime

# Import from agentic_core L4 memory state layer
from agentic_core.resume_engine.l4_memory_state.memory.rg_memory import (
    RGMemory, MemoryResult, BulletIndex, BulletProvenance
)


@dataclass
class MemoryQueryRequest:
    """Apps layer memory query request"""
    query_type: str  # "bullets", "competencies", "experience", "skills"
    filters: Dict[str, Any] = field(default_factory=dict)
    target_role: Optional[str] = None
    company: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    min_relevance_score: float = 0.0


@dataclass
class MemoryQueryResponse:
    """Apps layer memory query response"""
    success: bool = True
    results: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    provenance_summary: Dict[str, int] = field(default_factory=dict)
    query_stats: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MemoryStoreRequest:
    """Apps layer memory store request"""
    data_type: str  # "bullets", "competencies", "experience"
    data: Dict[str, Any]
    provenance: BulletProvenance = BulletProvenance.GENERATED
    relevance_score: float = 0.0
    tags: List[str] = field(default_factory=list)


class ResumeMemoryAdapter:
    """Apps layer adapter for resume memory operations

    Wraps agentic_core L4 RGMemory to provide clean interface
    for resume data storage, retrieval, and provenance tracking.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        # Initialize agentic core L4 memory
        self.core_memory = RGMemory(config)
        self.cache_enabled = self.config.get("cache_enabled", True)
        self.cache_ttl = self.config.get("cache_ttl", 3600)  # 1 hour default

    def query_memory(self, request: MemoryQueryRequest) -> MemoryQueryResponse:
        """Query resume memory with various filters"""
        response = MemoryQueryResponse()

        try:
            if request.query_type == "bullets":
                response.results = self._query_bullets(request)
            elif request.query_type == "competencies":
                response.results = self._query_competencies(request)
            elif request.query_type == "experience":
                response.results = self._query_experience(request)
            elif request.query_type == "skills":
                response.results = self._query_skills(request)
            else:
                response.success = False
                response.metadata["error"] = f"Unknown query type: {request.query_type}"
                return response

            # Build provenance summary
            response.provenance_summary = self._build_provenance_summary(response.results)

            # Add query statistics
            response.query_stats = {
                "total_results": len(response.results),
                "query_type": request.query_type,
                "filters_applied": len(request.filters),
                "queried_at": datetime.now().isoformat()
            }

            response.metadata["source"] = "agentic_core_l4_memory"

        except Exception as e:
            response.success = False
            response.metadata["error"] = str(e)

        return response

    def store_to_memory(self, request: MemoryStoreRequest) -> MemoryResult:
        """Store data to resume memory with provenance tracking"""
        try:
            if request.data_type == "bullets":
                result = self._store_bullets(request)
            elif request.data_type == "competencies":
                result = self._store_competencies(request)
            elif request.data_type == "experience":
                result = self._store_experience(request)
            else:
                return MemoryResult(
                    success=False,
                    metadata={"error": f"Unknown data type: {request.data_type}"}
                )

            result.metadata["stored_at"] = datetime.now().isoformat()
            result.metadata["adapter"] = "ResumeMemoryAdapter"

            return result

        except Exception as e:
            return MemoryResult(
                success=False,
                metadata={"error": str(e)}
            )

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory usage statistics"""
        return {
            "total_bullets": len(self.core_memory.bullet_pool),
            "total_competencies": len(self.core_memory.competencies),
            "resume_data_loaded": bool(self.core_memory.resume_data),
            "cache_enabled": self.cache_enabled,
            "adapter_version": "1.0.0",
            "last_updated": datetime.now().isoformat()
        }

    def _query_bullets(self, request: MemoryQueryRequest) -> List[Dict[str, Any]]:
        """Query bullet points from memory"""
        bullets = []

        for bullet_id, bullet_data in self.core_memory.bullet_pool.items():
            # Apply filters
            if request.target_role and bullet_data.get("role") != request.target_role:
                continue
            if request.company and bullet_data.get("company") != request.company:
                continue
            if request.min_relevance_score > 0 and bullet_data.get("relevance_score", 0) < request.min_relevance_score:
                continue
            if request.keywords:
                bullet_text = bullet_data.get("bullet_text", "").lower()
                if not any(keyword.lower() in bullet_text for keyword in request.keywords):
                    continue

            bullets.append({
                "bullet_id": bullet_id,
                "bullet_text": bullet_data.get("bullet_text", ""),
                "company": bullet_data.get("company", ""),
                "role": bullet_data.get("role", ""),
                "relevance_score": bullet_data.get("relevance_score", 0.0),
                "provenance": bullet_data.get("provenance", BulletProvenance.MASTER_RESUME),
                "indexed_at": bullet_data.get("indexed_at", "")
            })

        # Sort by relevance score (descending)
        bullets.sort(key=lambda x: x["relevance_score"], reverse=True)
        return bullets

    def _query_competencies(self, request: MemoryQueryRequest) -> List[Dict[str, Any]]:
        """Query competencies from memory"""
        competencies = []

        for comp_id, comp_data in self.core_memory.competencies.items():
            # Apply filters
            if request.target_role and not self._matches_role_filter(comp_data, request.target_role):
                continue
            if request.keywords:
                comp_name = comp_data.get("name", "").lower()
                if not any(keyword.lower() in comp_name for keyword in request.keywords):
                    continue

            competencies.append({
                "competency_id": comp_id,
                "name": comp_data.get("name", ""),
                "category": comp_data.get("category", ""),
                "proficiency_level": comp_data.get("proficiency_level", 0),
                "evidence": comp_data.get("evidence", []),
                "last_used": comp_data.get("last_used", "")
            })

        return competencies

    def _query_experience(self, request: MemoryQueryRequest) -> List[Dict[str, Any]]:
        """Query professional experience from memory"""
        experiences = []

        for exp in self.core_memory.resume_data.get("professional_experience", []):
            # Apply filters
            if request.target_role and exp.get("title", "").lower() != request.target_role.lower():
                continue
            if request.company and exp.get("company", "").lower() != request.company.lower():
                continue

            experiences.append({
                "company": exp.get("company", ""),
                "title": exp.get("title", ""),
                "duration": exp.get("duration", ""),
                "bullet_count": len(exp.get("bullet_pool", exp.get("highlights", []))),
                "start_date": exp.get("start_date", ""),
                "end_date": exp.get("end_date", "")
            })

        return experiences

    def _query_skills(self, request: MemoryQueryRequest) -> List[Dict[str, Any]]:
        """Query skills from memory"""
        skills = []

        # Extract skills from resume data
        all_skills = self.core_memory.resume_data.get("skills", {})

        for skill_category, skill_list in all_skills.items():
            for skill in skill_list:
                # Apply keyword filter
                if request.keywords and not any(keyword.lower() in skill.lower() for keyword in request.keywords):
                    continue

                skills.append({
                    "skill_name": skill,
                    "category": skill_category,
                    "source": "master_resume"
                })

        return skills

    def _store_bullets(self, request: MemoryStoreRequest) -> MemoryResult:
        """Store bullet points to memory"""
        bullets_data = request.data.get("bullets", [])
        stored_count = 0

        for bullet_info in bullets_data:
            bullet_id = f"bullet_{datetime.now().timestamp()}_{stored_count}"

            bullet_index = BulletIndex(
                bullet_id=bullet_id,
                company=bullet_info.get("company", ""),
                role=bullet_info.get("role", ""),
                bullet_text=bullet_info.get("bullet_text", ""),
                keywords=bullet_info.get("keywords", []),
                provenance=request.provenance,
                relevance_score=request.relevance_score
            )

            self.core_memory.bullet_pool[bullet_id] = bullet_index
            stored_count += 1

        return MemoryResult(
            success=True,
            data={"stored_count": stored_count},
            provenance_tracking={"bullets": request.provenance}
        )

    def _store_competencies(self, request: MemoryStoreRequest) -> MemoryResult:
        """Store competencies to memory"""
        competencies_data = request.data.get("competencies", [])
        stored_count = 0

        for comp_info in competencies_data:
            comp_id = f"comp_{datetime.now().timestamp()}_{stored_count}"

            competency = {
                "name": comp_info.get("name", ""),
                "category": comp_info.get("category", ""),
                "proficiency_level": comp_info.get("proficiency_level", 0),
                "evidence": comp_info.get("evidence", []),
                "provenance": request.provenance,
                "stored_at": datetime.now().isoformat()
            }

            self.core_memory.competencies[comp_id] = competency
            stored_count += 1

        return MemoryResult(
            success=True,
            data={"stored_count": stored_count},
            provenance_tracking={"competencies": request.provenance}
        )

    def _store_experience(self, request: MemoryStoreRequest) -> MemoryResult:
        """Store experience to memory"""
        experience_data = request.data.get("experience", {})

        # Add to resume data
        if "professional_experience" not in self.core_memory.resume_data:
            self.core_memory.resume_data["professional_experience"] = []

        self.core_memory.resume_data["professional_experience"].append(experience_data)

        return MemoryResult(
            success=True,
            data={"stored_experience": experience_data.get("company", "")},
            provenance_tracking={"experience": request.provenance}
        )

    def _build_provenance_summary(self, results: List[Dict[str, Any]]) -> Dict[str, int]:
        """Build summary of provenance types in results"""
        summary = {}
        for result in results:
            provenance = result.get("provenance", BulletProvenance.MASTER_RESUME)
            summary[provenance.value] = summary.get(provenance.value, 0) + 1
        return summary

    def _matches_role_filter(self, comp_data: Dict[str, Any], target_role: str) -> bool:
        """Check if competency matches role filter"""
        # Simple implementation - could be more sophisticated
        related_roles = comp_data.get("related_roles", [])
        return target_role.lower() in [role.lower() for role in related_roles]

