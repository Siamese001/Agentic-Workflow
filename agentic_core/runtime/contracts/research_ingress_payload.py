"""
DS-4: ResearchIngressPayload Contract
Declarative ingress payload for apps_research (company brief generation).
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class ResearchDepth(Enum):
    """Research depth levels."""
    QUICK = "quick"  # ~5 min, high-level
    STANDARD = "standard"  # ~15 min, balanced
    DEEP = "deep"  # ~30 min, comprehensive


class EvidenceSource(Enum):
    """Allowed evidence sources for research."""
    TAVILY = "tavily"
    MANUAL_BRIEF = "manual_brief"
    COMPANY_WEBSITE = "company_website"
    LINKEDIN = "linkedin"
    GLASSDOOR = "glassdoor"


@dataclass(frozen=True)
class ResearchTarget:
    """Target company and role for research."""
    company_name: str
    role_title: str
    
    # Optional context
    industry: Optional[str] = None
    company_size: Optional[str] = None  # startup, mid, enterprise
    location: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "company_name": self.company_name,
            "role_title": self.role_title,
            "industry": self.industry,
            "company_size": self.company_size,
            "location": self.location,
        }


@dataclass(frozen=True)
class ResearchProfilePack:
    """
    Declarative profile pack for research.
    
    These are static YAML files, not runtime configuration.
    """
    profile_digest: str  # sha256 of profile pack
    research_depth: ResearchDepth = ResearchDepth.STANDARD
    evidence_sources: List[EvidenceSource] = field(
        default_factory=lambda: [EvidenceSource.TAVILY, EvidenceSource.MANUAL_BRIEF]
    )
    
    # Output preferences (advisory)
    output_sections: List[str] = field(
        default_factory=lambda: [
            "company_overview",
            "culture_values",
            "technology_stack",
            "leadership_team",
            "recent_news",
            "competitive_position"
        ]
    )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile_digest": self.profile_digest,
            "research_depth": self.research_depth.value,
            "evidence_sources": [s.value for s in self.evidence_sources],
            "output_sections": self.output_sections,
        }


@dataclass(frozen=True)
class ResearchIngressPayload:
    """
    DS-4: Research Ingress Payload
    
    The canonical input format for apps_research.
    apps_reg constructs this from CLI/wizard input and submits
    to AppIngressRunner. No runtime authority in apps_research.
    """
    # Schema version
    schema_version: str = "1.0"
    
    # Target
    target: ResearchTarget = field(default_factory=lambda: ResearchTarget("", ""))
    
    # Research parameters (declarative only)
    profile_pack: ResearchProfilePack = field(
        default_factory=lambda: ResearchProfilePack("default")
    )
    
    # Optional manual brief (user-provided context)
    manual_brief_text: Optional[str] = None
    manual_brief_digest: Optional[str] = None
    
    # Request metadata
    request_id: str = ""
    timestamp_utc: str = ""
    
    # Tracing
    parent_trace_id: Optional[str] = None
    
    def __post_init__(self):
        # Generate request ID if not provided
        if not self.request_id:
            import uuid
            object.__setattr__(self, 'request_id', f"research_{uuid.uuid4().hex[:16]}")
        if not self.timestamp_utc:
            from datetime import datetime
            object.__setattr__(self, 'timestamp_utc', datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "target": self.target.to_dict(),
            "profile_pack": self.profile_pack.to_dict(),
            "manual_brief_digest": self.manual_brief_digest,
            "request_id": self.request_id,
            "timestamp_utc": self.timestamp_utc,
            "parent_trace_id": self.parent_trace_id,
        }


@dataclass(frozen=True)
class ResearchOutputContract:
    """
    DS-4: Research Output Contract
    
    The canonical output format from apps_research.
    Produced by Exit after core runtime processing.
    """
    schema_version: str = "1.0"
    
    # Input reference
    request_id: str = ""
    
    # Output sections
    sections: Dict[str, str] = field(default_factory=dict)
    
    # Evidence attribution
    sources_consulted: List[str] = field(default_factory=list)
    grounding_documents: List[str] = field(default_factory=list)
    
    # Quality metrics
    completeness_score: float = 0.0  # 0.0 - 1.0
    freshness_score: float = 0.0  # Recency of sources
    
    # Tracing
    trace_id: str = ""
    stage_owner_map: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "request_id": self.request_id,
            "sections": self.sections,
            "sources_consulted": self.sources_consulted,
            "grounding_documents": self.grounding_documents,
            "completeness_score": self.completeness_score,
            "freshness_score": self.freshness_score,
            "trace_id": self.trace_id,
            "stage_owner_map": self.stage_owner_map,
        }
