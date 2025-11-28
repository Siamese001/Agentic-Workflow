#!/usr/bin/env python3
"""
Resume Engine Core Models
Shared dataclasses and enums for all L1-L5 components
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class ValidationSeverity(Enum):
    """Validation result severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ResumeSection(Enum):
    """Resume section identifiers"""
    K0_CONTACT = "K0_CONTACT"
    K1_HEADLINE = "K1_HEADLINE"
    K2_SUMMARY = "K2_SUMMARY"
    K3_EXPERIENCE = "K3_EXPERIENCE"
    K4_EDUCATION = "K4_EDUCATION"
    K5_SKILLS = "K5_SKILLS"
    K6_PROJECTS = "K6_PROJECTS"
    K7_CERTIFICATIONS = "K7_CERTIFICATIONS"
    K8_ADDITIONAL = "K8_ADDITIONAL"
    K9_CUSTOM = "K9_CUSTOM"
    K10_AWARDS = "K10_AWARDS"
    K11_PUBLICATIONS = "K11_PUBLICATIONS"


class GateDecision(Enum):
    """Gate decision outcomes"""
    PROCEED = "proceed"
    STOP = "stop"
    RETRY = "retry"
    SKIP = "skip"


class BulletProvenance(Enum):
    """Bullet point origin tracking"""
    VERBATIM = "verbatim"
    MASTER_RESUME = "master_resume"
    GENERATED = "generated"
    ENRICHED = "enriched"
    HYBRID = "hybrid"


@dataclass
class ValidationResult:
    """Individual validation result"""
    rule_id: str
    passed: bool
    severity: ValidationSeverity
    message: str
    details: Dict = field(default_factory=dict)


@dataclass
class ThematicAnalysis:
    """Job description thematic analysis results"""
    themes: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    skills_required: List[str] = field(default_factory=list)
    experience_level: str = "mid"
    industry: Optional[str] = None
    company_intelligence: Dict = field(default_factory=dict)
    competitive_positioning: Dict = field(default_factory=dict)
    narrative_mining: Dict = field(default_factory=dict)
    signal_score: float = 0.0
    analysis_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class RAGEvidence:
    """RAG evidence tracking"""
    phase: str
    evidence: Dict
    confidence: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class RAGCritique:
    """RAG critique results"""
    phase: str
    critique: Dict
    passed: bool
    suggestions: List[str] = field(default_factory=list)


@dataclass
class RAGState:
    """RAG execution state"""
    mission: str
    evidence: List[RAGEvidence] = field(default_factory=list)
    critiques: List[RAGCritique] = field(default_factory=list)
    
    def add_evidence(self, evidence: RAGEvidence) -> None:
        """Add evidence to RAG state"""
        self.evidence.append(evidence)
    
    def add_critique(self, critique: RAGCritique) -> None:
        """Add critique to RAG state"""
        self.critiques.append(critique)
    
    def get_latest_evidence(self) -> Optional[RAGEvidence]:
        """Get most recent evidence"""
        return self.evidence[-1] if self.evidence else None
    
    def get_latest_critique(self) -> Optional[RAGCritique]:
        """Get most recent critique"""
        return self.critiques[-1] if self.critiques else None


@dataclass
class SkillRequirement:
    """Individual skill requirement"""
    skill_name: str
    required_level: str
    evidence: List[str] = field(default_factory=list)


@dataclass
class SkillCluster:
    """Clustered related skills"""
    cluster_name: str
    skills: List[SkillRequirement]
    confidence: float = 0.0


@dataclass
class MasterResumeIndex:
    """Master resume skill and experience index"""
    skills: List[str] = field(default_factory=list)
    experiences: List[str] = field(default_factory=list)
    competencies: List[str] = field(default_factory=list)
    indexed_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class CompetitiveIntelligence:
    """Competitive analysis results"""
    peer_companies: List[str] = field(default_factory=list)
    market_positioning: Dict = field(default_factory=dict)
    differentiation_opportunities: List[str] = field(default_factory=list)


@dataclass
class RetrievalSource:
    """Information retrieval source"""
    source_type: str
    content: str
    relevance_score: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# Configuration dataclasses
@dataclass
class FilePathsConfig:
    """File path configuration"""
    master_resume_path: str
    job_description_path: str
    output_dir: str
    config_dir: str = "config"


@dataclass
class ArtistConfig:
    """Artist generation configuration"""
    temperature: float = 0.9
    max_tokens: int = 2048
    model: str = "gemini-pro"


@dataclass
class ValidatorConfig:
    """Validation configuration"""
    strict_mode: bool = True
    enable_jd_enforcement: bool = True
    min_jd_keywords: int = 5


@dataclass
class WebRagConfig:
    """Web RAG configuration"""
    enabled: bool = True
    max_search_results: int = 10
    confidence_threshold: float = 0.7


@dataclass
class EnricherConfig:
    """Data enrichment configuration"""
    enable_verb_canonicalization: bool = True
    enable_skill_mapping: bool = True
    duplicate_threshold: float = 0.9


@dataclass
class ContentConstraintsConfig:
    """Content constraints configuration"""
    pass


@dataclass
class SignalControlConfig:
    """Signal control configuration"""
    pass


@dataclass
class AppConfig:
    """Application configuration aggregating all sub-configs"""
    file_paths: FilePathsConfig
    artist: ArtistConfig
    validator: ValidatorConfig
    web_rag: WebRagConfig
    enricher: EnricherConfig
    content_constraints: ContentConstraintsConfig
    signal_control: SignalControlConfig
    test_mode: bool = False


# JD Enforcement enums and dataclasses
class JDEnforcementRule:
    """JD enforcement rule definitions"""
    E1_JD_MIN_LENGTH = "JD must be non-empty (min 100 characters)"
    E2_JD_NON_NULL = "JD must be provided to workflow (not None/empty)"
    E3_JD_PARSING_SUCCESS = "JD must parse successfully"
    E4_THEMES_EXTRACTED = "JD-derived themes must be extracted"
    E5_SKILLS_EXTRACTED = "JD-derived skills must be extracted (min 5)"
    E6_JD_TO_THEMATIC = "JD data must flow to ThematicAnalysis"
    E7_THEMATIC_USES_JD = "ThematicAnalysis must use JD data (not mock)"
    E8_ARTIST_RECEIVES_JD = "Artist must receive JD-derived thematic_analysis"
    E9_CONTENT_HAS_JD_KW = "Generated content must contain JD keywords"
    E10_ENRICHMENT_USES_JD = "Enrichment must use JD-derived data"
    E11_VALIDATION_CHECKS_JD = "Validation must check JD keyword presence"
    E12_FILES_CONTAIN_JD = "Output files must contain JD-derived content"
    E13_QA_VERIFIES_JD = "QA report must verify JD usage"
    E14_NO_MOCK_DATA = "No fallback/mock/default data allowed anywhere"
    E15_COMPLETE_AUDIT = "Complete audit trail of JD data flow required"


@dataclass
class JDEnforcementResult:
    """JD enforcement validation result"""
    rule: JDEnforcementRule
    passed: bool
    details: str
    gate_id: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
